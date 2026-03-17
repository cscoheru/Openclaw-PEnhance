"""
PEnhance Prompt Enhancer
Enhances prompts before sending to GLM for better code generation
"""

import re
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    ENABLE_CODE_TEMPLATES,
    ENABLE_BEST_PRACTICES,
    ENABLE_CONTEXT_COMPRESSION,
    CONTEXT_COMPRESSION_THRESHOLD,
    ENABLE_OPENCLAW,
    OPENCLAW_URL,
    OPENCLAW_TOKEN,
    OPENCLAW_TIMEOUT,
    FALLBACK_ON_ERROR,
)
from enhancement.templates import (
    get_quality_prompt,
    get_algorithm_prompt,
    get_best_practices,
    REVIEW_CHECKLIST,
)
from enhancement.context_compressor import (
    estimate_tokens,
    compress_messages,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Keywords for detecting request types
CODE_KEYWORDS = [
    "write", "implement", "create", "build", "code", "function", "class",
    "method", "module", "script", "program", "algorithm", "refactor",
    "debug", "fix", "optimize", "编写", "实现", "创建", "代码", "函数",
]

ALGORITHM_KEYWORDS = [
    "sort", "search", "find", "path", "tree", "graph", "dp", "dynamic",
    "recursion", "iterate", "complexity", "排序", "搜索", "算法", "路径",
]

DEBUG_KEYWORDS = [
    "error", "bug", "fix", "debug", "issue", "problem", "not working",
    "crash", "exception", "traceback", "错误", "调试", "修复", "问题",
]


def detect_request_type(messages: List[Dict]) -> str:
    """Detect the type of request based on message content."""
    content = " ".join(
        str(m.get("content", ""))
        for m in messages
        if m.get("role") == "user"
    ).lower()

    # Check for debug requests
    if any(kw in content for kw in DEBUG_KEYWORDS):
        return "debug"

    # Check for algorithm requests
    if any(kw in content for kw in ALGORITHM_KEYWORDS):
        return "algorithm"

    # Check for code generation requests
    if any(kw in content for kw in CODE_KEYWORDS):
        return "code"

    return "general"


def detect_language(messages: List[Dict]) -> str:
    """Detect the programming language from context."""
    content = " ".join(str(m.get("content", "")) for m in messages)

    language_hints = {
        "python": ["python", "py", "def ", "import ", "self.", "__init__"],
        "javascript": ["javascript", "js", "function ", "const ", "let ", "=>"],
        "typescript": ["typescript", "ts", ": string", ": number", "interface "],
        "go": ["golang", "go ", "func ", "package ", "fmt."],
        "rust": ["rust", "fn ", "let mut", "impl ", "pub fn"],
    }

    for lang, hints in language_hints.items():
        for hint in hints:
            if hint.lower() in content.lower():
                return lang

    return "python"  # Default


def create_system_enhancement(request_type: str, language: str) -> str:
    """Create enhancement content to add to system message."""
    enhancements = []

    if request_type == "code":
        if ENABLE_CODE_TEMPLATES:
            enhancements.append(get_quality_prompt("type_hints"))
            enhancements.append(get_quality_prompt("error_handling"))
            enhancements.append(get_quality_prompt("documentation"))

        if ENABLE_BEST_PRACTICES:
            practices = get_best_practices(language)
            if practices:
                enhancements.append(
                    f"\n[BEST PRACTICES for {language.upper()}]\n" +
                    "\n".join(f"- {p}" for p in practices[:5])
                )

    elif request_type == "algorithm":
        enhancements.append(get_quality_prompt("type_hints"))
        # Detect algorithm type from content
        enhancements.append(get_algorithm_prompt("sorting"))
        enhancements.append(get_algorithm_prompt("search"))

    elif request_type == "debug":
        enhancements.append(get_quality_prompt("error_handling"))
        enhancements.append("""
[DEBUG ASSISTANCE]
When helping debug:
1. Identify the root cause first
2. Explain why the error occurs
3. Provide a minimal fix
4. Suggest how to prevent similar issues
5. Add appropriate error handling if missing
""")

    return "\n".join(enhancements)


def enhance_system_message(
    messages: List[Dict],
    request_type: str,
    language: str
) -> List[Dict]:
    """Enhance the first user message with additional context (GLM doesn't support system role)."""
    enhancement = create_system_enhancement(request_type, language)

    if not enhancement:
        return messages

    enhanced_messages = []

    # Find and enhance the first user message (GLM only supports user/assistant roles)
    first_user_enhanced = False

    for msg in messages:
        if msg.get("role") == "user" and not first_user_enhanced:
            # Prepend enhancement to first user message
            content = msg.get("content", "")
            if isinstance(content, str):
                enhanced_content = f"[Enhanced Context]\n{enhancement}\n\n[User Request]\n{content}"
                enhanced_messages.append({**msg, "content": enhanced_content})
                first_user_enhanced = True
            else:
                enhanced_messages.append(msg)
                first_user_enhanced = True
        else:
            # Filter out system messages (GLM doesn't support them)
            if msg.get("role") != "system":
                enhanced_messages.append(msg)

    return enhanced_messages


async def enhance_with_openclaw(messages: List[Dict]) -> List[Dict]:
    """Use OpenClaw for advanced enhancement (optional)."""
    if not ENABLE_OPENCLAW:
        return messages

    try:
        import httpx

        async with httpx.AsyncClient(timeout=OPENCLAW_TIMEOUT) as client:
            # Call OpenClaw enhancement endpoint
            response = await client.post(
                f"{OPENCLAW_URL}/enhance",
                headers={"Authorization": f"Bearer {OPENCLAW_TOKEN}"},
                json={"messages": messages}
            )

            if response.status_code == 200:
                logger.info("OpenClaw enhancement successful")
                return response.json().get("messages", messages)
            else:
                logger.warning(f"OpenClaw returned {response.status_code}")
                return messages

    except Exception as e:
        logger.warning(f"OpenClaw enhancement failed: {e}")
        if FALLBACK_ON_ERROR:
            return messages
        raise


def add_review_reminder(messages: List[Dict], request_type: str) -> List[Dict]:
    """Add a reminder to the last user message for code review."""
    if request_type != "code":
        return messages

    enhanced_messages = messages.copy()

    # Find the last user message
    for i in range(len(enhanced_messages) - 1, -1, -1):
        if enhanced_messages[i].get("role") == "user":
            content = enhanced_messages[i].get("content", "")

            # Add review reminder if generating code
            if isinstance(content, str) and any(
                kw in content.lower() for kw in ["write", "implement", "create", "编写"]
            ):
                review_note = "\n\n[After generating code, briefly verify against common issues.]"
                enhanced_messages[i] = {
                    **enhanced_messages[i],
                    "content": content + review_note
                }
            break

    return enhanced_messages


async def enhance(request_body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main enhancement function.

    Args:
        request_body: The original request body from Claude Code

    Returns:
        Enhanced request body
    """
    messages = request_body.get("messages", [])

    if not messages:
        return request_body

    # Step 1: Detect request type
    request_type = detect_request_type(messages)
    language = detect_language(messages)
    logger.info(f"Detected request type: {request_type}, language: {language}")

    # Step 2: Compress context if needed
    if ENABLE_CONTEXT_COMPRESSION:
        total_tokens = sum(
            estimate_tokens(str(m.get("content", ""))) for m in messages
        )
        if total_tokens > CONTEXT_COMPRESSION_THRESHOLD:
            logger.info(f"Compressing context ({total_tokens} tokens)")
            messages = compress_messages(messages)

    # Step 3: Enhance system message
    messages = enhance_system_message(messages, request_type, language)

    # Step 4: Add review reminder
    messages = add_review_reminder(messages, request_type)

    # Step 5: Optional OpenClaw enhancement
    if ENABLE_OPENCLAW:
        messages = await enhance_with_openclaw(messages)

    # Return enhanced request
    return {**request_body, "messages": messages}


class Enhancer:
    """Enhancer class for stateful enhancement operations."""

    def __init__(self):
        self.stats = {
            "total_requests": 0,
            "code_requests": 0,
            "algorithm_requests": 0,
            "debug_requests": 0,
            "compressions": 0,
        }

    async def enhance(self, request_body: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance request with statistics tracking."""
        self.stats["total_requests"] += 1

        request_type = detect_request_type(request_body.get("messages", []))

        if request_type == "code":
            self.stats["code_requests"] += 1
        elif request_type == "algorithm":
            self.stats["algorithm_requests"] += 1
        elif request_type == "debug":
            self.stats["debug_requests"] += 1

        return await enhance(request_body)

    def get_stats(self) -> Dict:
        """Get enhancement statistics."""
        return self.stats.copy()
