"""
Context Compressor for PEnhance
Intelligently compresses long contexts while preserving key information
"""

import re
from typing import List, Dict, Any


# Patterns for identifying important content
IMPORTANT_PATTERNS = [
    r"def\s+\w+\s*\(",  # Function definitions
    r"class\s+\w+",  # Class definitions
    r"import\s+",  # Imports
    r"TODO|FIXME|XXX",  # Task markers
    r"error|exception|bug",  # Error-related
    r"API|endpoint|route",  # API-related
]

# Patterns for identifying compressible content
COMPRESSIBLE_PATTERNS = [
    (r"[\s\n]{3,}", "\n\n"),  # Multiple blank lines
    (r"#.*$", ""),  # Simple comments (keep docstrings)
    (r"print\(.*\)", "..."),  # Print statements
]


def estimate_tokens(text: str) -> int:
    """Estimate token count for text (rough approximation)."""
    # Rough approximation: ~4 chars per token for English/code
    return len(text) // 4


def extract_code_blocks(text: str) -> List[Dict[str, str]]:
    """Extract code blocks from text."""
    pattern = r"```(\w+)?\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    return [{"language": lang or "text", "code": code} for lang, code in matches]


def extract_imports(code: str) -> str:
    """Extract import statements from code."""
    import_lines = []
    for line in code.split("\n"):
        if line.strip().startswith(("import ", "from ")):
            import_lines.append(line)
    return "\n".join(import_lines)


def extract_function_signatures(code: str) -> str:
    """Extract function signatures from code."""
    signatures = []
    pattern = r"(def\s+\w+\s*\([^)]*\)(?:\s*->\s*\w+)?)"
    for match in re.finditer(pattern, code):
        signatures.append(match.group(1))
    return "\n".join(signatures)


def is_important_content(text: str) -> bool:
    """Check if content contains important patterns."""
    for pattern in IMPORTANT_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def compress_code_block(code: str, max_length: int = 500) -> str:
    """Compress a code block while preserving structure."""
    if len(code) <= max_length:
        return code

    parts = []

    # Keep imports
    imports = extract_imports(code)
    if imports:
        parts.append(imports)
        parts.append("# ... (other code compressed)")

    # Keep function signatures
    signatures = extract_function_signatures(code)
    if signatures:
        parts.append("\n# Function signatures:")
        parts.append(signatures.replace("def ", "def ").replace(":", ": ..."))

    # Keep important lines
    important_lines = []
    for line in code.split("\n"):
        if is_important_content(line) and line not in imports and "def " not in line:
            important_lines.append(line)

    if important_lines:
        parts.append("\n# Key content:")
        parts.extend(important_lines[:10])  # Limit to 10 important lines

    compressed = "\n".join(parts)
    return compressed[:max_length] + "\n# ... (truncated)"


def compress_text(text: str, max_length: int = 1000) -> str:
    """Compress general text while preserving key information."""
    if len(text) <= max_length:
        return text

    # Split into paragraphs
    paragraphs = text.split("\n\n")

    # Score each paragraph by importance
    scored = []
    for para in paragraphs:
        score = 0
        if is_important_content(para):
            score += 10
        if "?" in para:  # Questions are important
            score += 5
        if len(para) < 50:  # Short paragraphs might be summaries
            score += 3
        scored.append((score, para))

    # Sort by score and take top paragraphs
    scored.sort(reverse=True, key=lambda x: x[0])

    result = []
    current_length = 0

    for score, para in scored:
        if current_length + len(para) <= max_length:
            result.append(para)
            current_length += len(para)

    return "\n\n".join(result) + "\n\n[... content compressed ...]"


def compress_message(message: Dict[str, Any], max_tokens: int = 2000) -> Dict[str, Any]:
    """Compress a single message if needed."""
    content = message.get("content", "")

    if isinstance(content, str):
        current_tokens = estimate_tokens(content)

        if current_tokens > max_tokens:
            # Check if it contains code
            code_blocks = extract_code_blocks(content)

            if code_blocks:
                # Compress code blocks
                compressed_content = content
                for block in code_blocks:
                    compressed_code = compress_code_block(
                        block["code"], max_length=max_tokens * 2
                    )
                    original = f"```{block['language']}\n{block['code']}```"
                    compressed = f"```{block['language']}\n{compressed_code}```"
                    compressed_content = compressed_content.replace(original, compressed)
                message = {**message, "content": compressed_content}
            else:
                # Compress general text
                compressed_content = compress_text(content, max_length=max_tokens * 4)
                message = {**message, "content": compressed_content}

    elif isinstance(content, list):
        # Handle multi-part content (e.g., with images)
        compressed_parts = []
        for part in content:
            if part.get("type") == "text":
                text = part.get("text", "")
                if estimate_tokens(text) > max_tokens:
                    text = compress_text(text, max_length=max_tokens * 4)
                compressed_parts.append({**part, "text": text})
            else:
                compressed_parts.append(part)  # Keep non-text parts as-is
        message = {**message, "content": compressed_parts}

    return message


def compress_messages(
    messages: List[Dict[str, Any]],
    max_total_tokens: int = 100000,
    preserve_recent: int = 3,
) -> List[Dict[str, Any]]:
    """
    Compress a list of messages to fit within token limit.

    Args:
        messages: List of message dictionaries
        max_total_tokens: Maximum total tokens allowed
        preserve_recent: Number of recent messages to preserve fully

    Returns:
        Compressed list of messages
    """
    if not messages:
        return messages

    # Calculate total tokens
    total_tokens = sum(
        estimate_tokens(str(m.get("content", ""))) for m in messages
    )

    if total_tokens <= max_total_tokens:
        return messages

    # Preserve recent messages
    preserved = messages[-preserve_recent:] if preserve_recent > 0 else []
    to_compress = messages[:-preserve_recent] if preserve_recent > 0 else messages

    # Calculate how much we need to compress
    preserved_tokens = sum(
        estimate_tokens(str(m.get("content", ""))) for m in preserved
    )
    available_tokens = max_total_tokens - preserved_tokens
    per_message_tokens = available_tokens // max(len(to_compress), 1)

    # Compress older messages
    compressed = []
    for msg in to_compress:
        compressed_msg = compress_message(msg, max_tokens=per_message_tokens)
        compressed.append(compressed_msg)

    return compressed + preserved


def summarize_conversation(messages: List[Dict[str, Any]]) -> str:
    """Create a brief summary of the conversation so far."""
    summary_parts = []

    for i, msg in enumerate(messages):
        role = msg.get("role", "unknown")
        content = msg.get("content", "")

        if isinstance(content, list):
            content = " ".join(
                p.get("text", "") for p in content if p.get("type") == "text"
            )

        # Extract first sentence or first 100 chars
        first_sentence = content.split(".")[0][:100]
        if first_sentence:
            summary_parts.append(f"[{role}]: {first_sentence}...")

    return "\n".join(summary_parts[-10:])  # Last 10 exchanges
