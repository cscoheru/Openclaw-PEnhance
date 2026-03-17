#!/usr/bin/env python3
"""
PEnhance MCP Server - Programming Enhancement Tools for Claude Code
Exposes memory, plan, and algorithm enhancement as MCP tools
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Import PEnhance modules
SCRIPTS_DIR = Path(__file__).parent.parent / "skills" / "penhance" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

# Try to import the modules, fallback to direct execution if needed
try:
    from memory_manager import MemoryManager
    from plan_enforcer import PlanEnforcer
    from algorithm_analyzer import AlgorithmAnalyzer
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False

# Configuration
PROJECT_DIR = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_DIR / "config"
MEMORY_DIR = PROJECT_DIR / "memory"

# Create MCP server instance
server = Server("penhance-mcp")


# ============================================================================
# Memory Tools
# ============================================================================

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available PEnhance tools"""
    return [
        # Memory Tools
        Tool(
            name="penhance_memory_save",
            description="Save current context/session to memory. Captures task state, code changes, and decisions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "Current task description"
                    },
                    "context": {
                        "type": "object",
                        "description": "Context data to save (code changes, decisions, etc.)"
                    },
                    "session_id": {
                        "type": "string",
                        "description": "Optional session ID. Auto-generated if not provided."
                    }
                },
                "required": ["task"]
            }
        ),
        Tool(
            name="penhance_memory_load",
            description="Load a saved session/context from memory by session ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session ID to load"
                    }
                },
                "required": ["session_id"]
            }
        ),
        Tool(
            name="penhance_memory_list",
            description="List all saved memory sessions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of sessions to return (default: 10)"
                    }
                }
            }
        ),
        Tool(
            name="penhance_memory_compress",
            description="Compress old memories to save space while preserving key information.",
            inputSchema={
                "type": "object",
                "properties": {
                    "older_than_days": {
                        "type": "integer",
                        "description": "Compress memories older than N days (default: 7)"
                    }
                }
            }
        ),

        # Plan Tools
        Tool(
            name="penhance_plan_create",
            description="Create a new development plan for tracking code changes.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Plan name"
                    },
                    "tasks": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of planned tasks"
                    },
                    "description": {
                        "type": "string",
                        "description": "Plan description"
                    }
                },
                "required": ["name", "tasks"]
            }
        ),
        Tool(
            name="penhance_plan_track",
            description="Start tracking a plan for code-change matching.",
            inputSchema={
                "type": "object",
                "properties": {
                    "plan_id": {
                        "type": "string",
                        "description": "Plan ID to track"
                    }
                },
                "required": ["plan_id"]
            }
        ),
        Tool(
            name="penhance_plan_status",
            description="Get current plan status, completion percentage, and deviation score.",
            inputSchema={
                "type": "object",
                "properties": {
                    "plan_id": {
                        "type": "string",
                        "description": "Plan ID (optional, uses active plan if not provided)"
                    }
                }
            }
        ),
        Tool(
            name="penhance_plan_check",
            description="Check if a code change matches the current plan. Returns deviation analysis.",
            inputSchema={
                "type": "object",
                "properties": {
                    "change_description": {
                        "type": "string",
                        "description": "Description of the code change"
                    },
                    "file_path": {
                        "type": "string",
                        "description": "File being modified"
                    }
                },
                "required": ["change_description"]
            }
        ),
        Tool(
            name="penhance_plan_list",
            description="List all development plans.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),

        # Algorithm Tools
        Tool(
            name="penhance_algo_analyze",
            description="Analyze code to identify algorithms, complexity, and optimization opportunities.",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Code snippet to analyze"
                    },
                    "language": {
                        "type": "string",
                        "description": "Programming language (python, javascript, etc.)"
                    }
                },
                "required": ["code"]
            }
        ),
        Tool(
            name="penhance_algo_suggest",
            description="Get algorithm suggestions for a problem description.",
            inputSchema={
                "type": "object",
                "properties": {
                    "problem": {
                        "type": "string",
                        "description": "Problem description"
                    },
                    "constraints": {
                        "type": "string",
                        "description": "Time/space constraints (optional)"
                    }
                },
                "required": ["problem"]
            }
        ),
        Tool(
            name="penhance_algo_generate",
            description="Generate code implementation for a specific algorithm.",
            inputSchema={
                "type": "object",
                "properties": {
                    "algorithm": {
                        "type": "string",
                        "description": "Algorithm name (e.g., 'quicksort', 'dijkstra')"
                    },
                    "language": {
                        "type": "string",
                        "description": "Target language (default: python)"
                    },
                    "include_tests": {
                        "type": "boolean",
                        "description": "Include test cases (default: true)"
                    }
                },
                "required": ["algorithm"]
            }
        ),
        Tool(
            name="penhance_algo_compare",
            description="Compare two algorithms and their trade-offs.",
            inputSchema={
                "type": "object",
                "properties": {
                    "algo1": {
                        "type": "string",
                        "description": "First algorithm name"
                    },
                    "algo2": {
                        "type": "string",
                        "description": "Second algorithm name"
                    },
                    "context": {
                        "type": "string",
                        "description": "Problem context for comparison (optional)"
                    }
                },
                "required": ["algo1", "algo2"]
            }
        ),

        # Status Tool
        Tool(
            name="penhance_status",
            description="Get overall PEnhance status including memory usage, active plans, and health.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls"""

    try:
        # ====================================================================
        # Memory Tools
        # ====================================================================

        if name == "penhance_memory_save":
            return await handle_memory_save(arguments)

        elif name == "penhance_memory_load":
            return await handle_memory_load(arguments)

        elif name == "penhance_memory_list":
            return await handle_memory_list(arguments)

        elif name == "penhance_memory_compress":
            return await handle_memory_compress(arguments)

        # ====================================================================
        # Plan Tools
        # ====================================================================

        elif name == "penhance_plan_create":
            return await handle_plan_create(arguments)

        elif name == "penhance_plan_track":
            return await handle_plan_track(arguments)

        elif name == "penhance_plan_status":
            return await handle_plan_status(arguments)

        elif name == "penhance_plan_check":
            return await handle_plan_check(arguments)

        elif name == "penhance_plan_list":
            return await handle_plan_list(arguments)

        # ====================================================================
        # Algorithm Tools
        # ====================================================================

        elif name == "penhance_algo_analyze":
            return await handle_algo_analyze(arguments)

        elif name == "penhance_algo_suggest":
            return await handle_algo_suggest(arguments)

        elif name == "penhance_algo_generate":
            return await handle_algo_generate(arguments)

        elif name == "penhance_algo_compare":
            return await handle_algo_compare(arguments)

        # ====================================================================
        # Status Tool
        # ====================================================================

        elif name == "penhance_status":
            return await handle_status(arguments)

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        return [TextContent(type="text", text=f"Error executing {name}: {str(e)}")]


# ============================================================================
# Memory Tool Handlers
# ============================================================================

async def handle_memory_save(args: dict) -> list[TextContent]:
    """Save context to memory"""
    task = args.get("task", "")
    context = args.get("context", {})
    session_id = args.get("session_id")

    # Ensure memory directory exists
    sessions_dir = MEMORY_DIR / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)

    # Generate session ID if not provided
    if not session_id:
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create memory entry
    memory_data = {
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "task": task,
        "context": context,
        "status": "active"
    }

    # Save to file
    memory_file = sessions_dir / f"{session_id}.json"
    with open(memory_file, "w", encoding="utf-8") as f:
        json.dump(memory_data, f, indent=2, ensure_ascii=False)

    return [TextContent(
        type="text",
        text=f"✅ Memory saved successfully\n\n"
             f"Session ID: {session_id}\n"
             f"Task: {task}\n"
             f"Context items: {len(context)}\n"
             f"File: {memory_file}"
    )]


async def handle_memory_load(args: dict) -> list[TextContent]:
    """Load a saved session"""
    session_id = args.get("session_id")

    memory_file = MEMORY_DIR / "sessions" / f"{session_id}.json"

    if not memory_file.exists():
        return [TextContent(type="text", text=f"❌ Session not found: {session_id}")]

    with open(memory_file, "r", encoding="utf-8") as f:
        memory_data = json.load(f)

    # Format output
    output = f"📂 Loaded Session: {session_id}\n\n"
    output += f"**Timestamp**: {memory_data.get('timestamp', 'N/A')}\n"
    output += f"**Task**: {memory_data.get('task', 'N/A')}\n\n"

    context = memory_data.get("context", {})
    if context:
        output += "**Context**:\n"
        output += f"```json\n{json.dumps(context, indent=2, ensure_ascii=False)}\n```\n"

    return [TextContent(type="text", text=output)]


async def handle_memory_list(args: dict) -> list[TextContent]:
    """List saved sessions"""
    limit = args.get("limit", 10)
    sessions_dir = MEMORY_DIR / "sessions"

    if not sessions_dir.exists():
        return [TextContent(type="text", text="No saved sessions found.")]

    sessions = sorted(
        sessions_dir.glob("*.json"),
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )[:limit]

    if not sessions:
        return [TextContent(type="text", text="No saved sessions found.")]

    output = f"📋 Saved Sessions ({len(sessions)} of {len(list(sessions_dir.glob('*.json')))}):\n\n"

    for session_file in sessions:
        with open(session_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        output += f"- **{data.get('session_id', session_file.stem)}**: {data.get('task', 'N/A')[:50]}...\n"

    return [TextContent(type="text", text=output)]


async def handle_memory_compress(args: dict) -> list[TextContent]:
    """Compress old memories"""
    older_than_days = args.get("older_than_days", 7)
    sessions_dir = MEMORY_DIR / "sessions"
    compressed_dir = MEMORY_DIR / "compressed"
    compressed_dir.mkdir(parents=True, exist_ok=True)

    if not sessions_dir.exists():
        return [TextContent(type="text", text="No sessions to compress.")]

    cutoff = datetime.now().timestamp() - (older_than_days * 86400)
    compressed_count = 0

    for session_file in sessions_dir.glob("*.json"):
        if session_file.stat().st_mtime < cutoff:
            # Read and compress
            with open(session_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Create compressed summary
            compressed = {
                "session_id": data.get("session_id"),
                "task": data.get("task"),
                "timestamp": data.get("timestamp"),
                "compressed_at": datetime.now().isoformat(),
                "summary": f"Task: {data.get('task', 'N/A')[:100]}"
            }

            # Save compressed version
            compressed_file = compressed_dir / f"{session_file.stem}_compressed.json"
            with open(compressed_file, "w", encoding="utf-8") as f:
                json.dump(compressed, f, indent=2, ensure_ascii=False)

            # Remove original
            session_file.unlink()
            compressed_count += 1

    return [TextContent(
        type="text",
        text=f"✅ Compressed {compressed_count} sessions older than {older_than_days} days.\n"
             f"Compressed files saved to: {compressed_dir}"
    )]


# ============================================================================
# Plan Tool Handlers
# ============================================================================

async def handle_plan_create(args: dict) -> list[TextContent]:
    """Create a new development plan"""
    name = args.get("name", "")
    tasks = args.get("tasks", [])
    description = args.get("description", "")

    # Ensure plans directory exists
    plans_dir = MEMORY_DIR / "plans"
    plans_dir.mkdir(parents=True, exist_ok=True)

    # Generate plan ID
    plan_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + name.lower().replace(" ", "_")[:20]

    # Create plan
    plan_data = {
        "plan_id": plan_id,
        "name": name,
        "description": description,
        "tasks": [{"id": i, "description": t, "status": "pending", "completed_at": None}
                  for i, t in enumerate(tasks)],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "status": "active",
        "deviation_score": 0.0
    }

    # Save plan
    plan_file = plans_dir / f"{plan_id}.json"
    with open(plan_file, "w", encoding="utf-8") as f:
        json.dump(plan_data, f, indent=2, ensure_ascii=False)

    # Set as active plan
    active_file = plans_dir / "active_plan.txt"
    with open(active_file, "w") as f:
        f.write(plan_id)

    return [TextContent(
        type="text",
        text=f"✅ Plan created and set as active\n\n"
             f"**Plan ID**: {plan_id}\n"
             f"**Name**: {name}\n"
             f"**Tasks**: {len(tasks)}\n"
             f"**File**: {plan_file}"
    )]


async def handle_plan_track(args: dict) -> list[TextContent]:
    """Start tracking a plan"""
    plan_id = args.get("plan_id")

    plans_dir = MEMORY_DIR / "plans"
    plan_file = plans_dir / f"{plan_id}.json"

    if not plan_file.exists():
        return [TextContent(type="text", text=f"❌ Plan not found: {plan_id}")]

    # Set as active
    active_file = plans_dir / "active_plan.txt"
    with open(active_file, "w") as f:
        f.write(plan_id)

    return [TextContent(
        type="text",
        text=f"✅ Now tracking plan: {plan_id}\n"
             f"All code changes will be checked against this plan."
    )]


async def handle_plan_status(args: dict) -> list[TextContent]:
    """Get plan status"""
    plans_dir = MEMORY_DIR / "plans"

    # Get plan ID
    plan_id = args.get("plan_id")
    if not plan_id:
        active_file = plans_dir / "active_plan.txt"
        if active_file.exists():
            with open(active_file, "r") as f:
                plan_id = f.read().strip()
        else:
            return [TextContent(type="text", text="❌ No active plan. Create one first with penhance_plan_create.")]

    plan_file = plans_dir / f"{plan_id}.json"
    if not plan_file.exists():
        return [TextContent(type="text", text=f"❌ Plan not found: {plan_id}")]

    with open(plan_file, "r", encoding="utf-8") as f:
        plan = json.load(f)

    # Calculate status
    tasks = plan.get("tasks", [])
    completed = sum(1 for t in tasks if t.get("status") == "completed")
    total = len(tasks)
    percentage = (completed / total * 100) if total > 0 else 0

    output = f"📊 Plan Status: {plan.get('name', plan_id)}\n\n"
    output += f"**Progress**: {completed}/{total} tasks ({percentage:.1f}%)\n"
    output += f"**Deviation Score**: {plan.get('deviation_score', 0):.1f}%\n"
    output += f"**Status**: {plan.get('status', 'active')}\n\n"

    output += "**Tasks**:\n"
    for task in tasks:
        status_icon = "✅" if task.get("status") == "completed" else "⬜"
        output += f"- {status_icon} [{task.get('id')}] {task.get('description')}\n"

    return [TextContent(type="text", text=output)]


async def handle_plan_check(args: dict) -> list[TextContent]:
    """Check if a change matches the plan"""
    change_description = args.get("change_description", "")
    file_path = args.get("file_path", "")

    plans_dir = MEMORY_DIR / "plans"
    active_file = plans_dir / "active_plan.txt"

    if not active_file.exists():
        return [TextContent(type="text", text="❌ No active plan. Create one first.")]

    with open(active_file, "r") as f:
        plan_id = f.read().strip()

    plan_file = plans_dir / f"{plan_id}.json"
    with open(plan_file, "r", encoding="utf-8") as f:
        plan = json.load(f)

    # Simple keyword matching for deviation detection
    tasks = plan.get("tasks", [])
    pending_tasks = [t for t in tasks if t.get("status") == "pending"]

    # Check for matches
    matches = []
    change_words = set(change_description.lower().split())

    for task in pending_tasks:
        task_words = set(task.get("description", "").lower().split())
        overlap = len(change_words & task_words)
        if overlap > 0:
            matches.append({
                "task_id": task.get("id"),
                "description": task.get("description"),
                "match_score": overlap
            })

    # Calculate deviation
    if matches:
        deviation = 0
        matched_task = matches[0]
        output = f"✅ Change matches plan task\n\n"
        output += f"**Matched Task**: [{matched_task['task_id']}] {matched_task['description']}\n"
        output += f"**Match Score**: {matched_task['match_score']} keywords\n"
    else:
        deviation = 30  # No match found
        output = f"⚠️ Change may deviate from plan\n\n"
        output += f"**Deviation Score**: {deviation}%\n"
        output += f"**Change**: {change_description}\n"
        output += f"**File**: {file_path or 'N/A'}\n\n"
        output += "**Pending Tasks**:\n"
        for task in pending_tasks[:5]:
            output += f"- [{task.get('id')}] {task.get('description')}\n"

    return [TextContent(type="text", text=output)]


async def handle_plan_list(args: dict) -> list[TextContent]:
    """List all plans"""
    plans_dir = MEMORY_DIR / "plans"

    if not plans_dir.exists():
        return [TextContent(type="text", text="No plans found.")]

    # Get active plan
    active_file = plans_dir / "active_plan.txt"
    active_plan_id = ""
    if active_file.exists():
        with open(active_file, "r") as f:
            active_plan_id = f.read().strip()

    plans = sorted(
        [f for f in plans_dir.glob("*.json")],
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )

    if not plans:
        return [TextContent(type="text", text="No plans found.")]

    output = f"📋 Development Plans ({len(plans)}):\n\n"

    for plan_file in plans:
        with open(plan_file, "r", encoding="utf-8") as f:
            plan = json.load(f)

        is_active = "🟢 " if plan.get("plan_id") == active_plan_id else "   "
        tasks = plan.get("tasks", [])
        completed = sum(1 for t in tasks if t.get("status") == "completed")

        output += f"{is_active}**{plan.get('name', plan_file.stem)}**\n"
        output += f"    ID: {plan.get('plan_id')}\n"
        output += f"    Progress: {completed}/{len(tasks)} tasks\n\n"

    return [TextContent(type="text", text=output)]


# ============================================================================
# Algorithm Tool Handlers
# ============================================================================

# Algorithm knowledge base
ALGORITHMS = {
    "sorting": {
        "quicksort": {
            "time_complexity": "O(n log n) average, O(n²) worst",
            "space_complexity": "O(log n)",
            "description": "Divide-and-conquer sorting algorithm",
            "best_for": "General purpose sorting, good cache performance",
            "stable": False
        },
        "mergesort": {
            "time_complexity": "O(n log n)",
            "space_complexity": "O(n)",
            "description": "Divide-and-conquer, stable sorting",
            "best_for": "Linked lists, external sorting, when stability needed",
            "stable": True
        },
        "heapsort": {
            "time_complexity": "O(n log n)",
            "space_complexity": "O(1)",
            "description": "In-place sorting using heap data structure",
            "best_for": "When O(1) space is required",
            "stable": False
        }
    },
    "search": {
        "binary_search": {
            "time_complexity": "O(log n)",
            "space_complexity": "O(1)",
            "description": "Search in sorted array",
            "best_for": "Sorted arrays, random access",
            "requires_sorted": True
        },
        "dfs": {
            "time_complexity": "O(V + E)",
            "space_complexity": "O(V)",
            "description": "Depth-first graph traversal",
            "best_for": "Topological sort, cycle detection, path finding",
            "uses_stack": True
        },
        "bfs": {
            "time_complexity": "O(V + E)",
            "space_complexity": "O(V)",
            "description": "Breadth-first graph traversal",
            "best_for": "Shortest path in unweighted graphs, level-order",
            "uses_queue": True
        }
    },
    "graph": {
        "dijkstra": {
            "time_complexity": "O((V + E) log V)",
            "space_complexity": "O(V)",
            "description": "Shortest path in weighted graphs (non-negative)",
            "best_for": "GPS navigation, network routing",
            "requires_non_negative_weights": True
        },
        "bellman_ford": {
            "time_complexity": "O(V * E)",
            "space_complexity": "O(V)",
            "description": "Shortest path with negative weights",
            "best_for": "Detecting negative cycles, currency arbitrage",
            "handles_negative_weights": True
        },
        "a_star": {
            "time_complexity": "O(E)",
            "space_complexity": "O(V)",
            "description": "Heuristic-guided pathfinding",
            "best_for": "Game AI, robotics, GPS with heuristics",
            "uses_heuristic": True
        }
    },
    "dynamic_programming": {
        "knapsack": {
            "time_complexity": "O(n * W)",
            "space_complexity": "O(n * W) or O(W) optimized",
            "description": "Optimal subset selection with weight constraint",
            "best_for": "Resource allocation, investment decisions"
        },
        "lcs": {
            "time_complexity": "O(m * n)",
            "space_complexity": "O(m * n)",
            "description": "Longest Common Subsequence",
            "best_for": "Diff algorithms, DNA sequence alignment"
        },
        "edit_distance": {
            "time_complexity": "O(m * n)",
            "space_complexity": "O(m * n)",
            "description": "Minimum edits to transform strings",
            "best_for": "Spell checking, fuzzy matching"
        }
    }
}


async def handle_algo_analyze(args: dict) -> list[TextContent]:
    """Analyze code for algorithms"""
    code = args.get("code", "")
    language = args.get("language", "python")

    # Simple pattern detection
    detected = []

    code_lower = code.lower()

    # Check for sorting patterns
    if any(kw in code_lower for kw in ["partition", "pivot", "quicksort"]):
        detected.append(("quicksort", "sorting"))
    if any(kw in code_lower for kw in ["merge", "mergesort"]):
        detected.append(("mergesort", "sorting"))
    if any(kw in code_lower for kw in ["heapify", "heapsort"]):
        detected.append(("heapsort", "sorting"))

    # Check for search patterns
    if any(kw in code_lower for kw in ["binary_search", "mid", "left", "right"]):
        detected.append(("binary_search", "search"))
    if any(kw in code_lower for kw in ["dfs", "stack", "visited", "recursive"]):
        detected.append(("dfs", "search"))
    if any(kw in code_lower for kw in ["bfs", "queue", "level"]):
        detected.append(("bfs", "search"))

    # Check for graph patterns
    if any(kw in code_lower for kw in ["dijkstra", "shortest_path", "priority_queue"]):
        detected.append(("dijkstra", "graph"))
    if any(kw in code_lower for kw in ["bellman", "relax"]):
        detected.append(("bellman_ford", "graph"))
    if any(kw in code_lower for kw in ["a_star", "astar", "heuristic", "f_score"]):
        detected.append(("a_star", "graph"))

    # Check for DP patterns
    if any(kw in code_lower for kw in ["dp", "memo", "knapsack", "weight"]):
        detected.append(("dynamic_programming", "dp"))
    if any(kw in code_lower for kw in ["lcs", "subsequence"]):
        detected.append(("lcs", "dp"))

    # Build output
    output = f"🔍 Algorithm Analysis\n\n"
    output += f"**Language**: {language}\n"
    output += f"**Code Length**: {len(code)} characters\n\n"

    if detected:
        output += f"**Detected Algorithms** ({len(detected)}):\n\n"
        for algo_name, category in detected:
            output += f"### {algo_name}\n"
            if category in ALGORITHMS and algo_name in ALGORITHMS[category]:
                info = ALGORITHMS[category][algo_name]
                output += f"- **Category**: {category}\n"
                output += f"- **Time Complexity**: {info.get('time_complexity', 'N/A')}\n"
                output += f"- **Space Complexity**: {info.get('space_complexity', 'N/A')}\n"
                output += f"- **Description**: {info.get('description', 'N/A')}\n"
                output += f"- **Best For**: {info.get('best_for', 'N/A')}\n\n"
            else:
                output += f"- **Category**: {category}\n\n"
    else:
        output += "No standard algorithms detected.\n\n"
        output += "**Suggestions**:\n"
        output += "- Check for loops that might indicate O(n) or O(n²) complexity\n"
        output += "- Look for recursive patterns\n"
        output += "- Identify data structures used (arrays, hash maps, trees)\n"

    return [TextContent(type="text", text=output)]


async def handle_algo_suggest(args: dict) -> list[TextContent]:
    """Suggest algorithms for a problem"""
    problem = args.get("problem", "")
    constraints = args.get("constraints", "")

    problem_lower = problem.lower()

    suggestions = []

    # Keyword-based suggestions
    if any(kw in problem_lower for kw in ["sort", "order", "arrange"]):
        suggestions.append(("quicksort", "Fast general-purpose sorting"))
        suggestions.append(("mergesort", "Stable sorting, good for linked structures"))

    if any(kw in problem_lower for kw in ["search", "find", "locate"]):
        suggestions.append(("binary_search", "Fast search in sorted data"))
        suggestions.append(("hash_table", "O(1) lookup"))

    if any(kw in problem_lower for kw in ["shortest", "path", "route", "distance"]):
        suggestions.append(("dijkstra", "Shortest path with non-negative weights"))
        suggestions.append(("bfs", "Shortest path in unweighted graphs"))
        suggestions.append(("a_star", "Pathfinding with heuristics"))

    if any(kw in problem_lower for kw in ["traverse", "visit", "explore", "graph", "tree"]):
        suggestions.append(("dfs", "Deep exploration, cycle detection"))
        suggestions.append(("bfs", "Level-by-level exploration"))

    if any(kw in problem_lower for kw in ["optimize", "maximize", "minimize", "best"]):
        suggestions.append(("dynamic_programming", "Optimal substructure problems"))
        suggestions.append(("greedy", "Local optimal choices"))

    if any(kw in problem_lower for kw in ["match", "compare", "similar", "diff"]):
        suggestions.append(("lcs", "Find common subsequences"))
        suggestions.append(("edit_distance", "String similarity"))

    # Build output
    output = f"💡 Algorithm Suggestions\n\n"
    output += f"**Problem**: {problem[:200]}...\n\n"

    if constraints:
        output += f"**Constraints**: {constraints}\n\n"

    if suggestions:
        output += f"**Suggested Algorithms**:\n\n"
        for i, (algo, reason) in enumerate(suggestions[:5], 1):
            output += f"{i}. **{algo}**\n"
            output += f"   - {reason}\n"

            # Add complexity info if available
            for category in ALGORITHMS.values():
                if algo in category:
                    info = category[algo]
                    output += f"   - Time: {info.get('time_complexity', 'N/A')}\n"
                    output += f"   - Space: {info.get('space_complexity', 'N/A')}\n"
                    break
            output += "\n"
    else:
        output += "No specific suggestions found. Consider:\n"
        output += "- Breaking down the problem into subproblems\n"
        output += "- Identifying the input size and constraints\n"
        output += "- Determining if the problem has optimal substructure\n"

    return [TextContent(type="text", text=output)]


async def handle_algo_generate(args: dict) -> list[TextContent]:
    """Generate algorithm implementation"""
    algorithm = args.get("algorithm", "quicksort").lower()
    language = args.get("language", "python")
    include_tests = args.get("include_tests", True)

    # Algorithm implementations
    implementations = {
        "quicksort": {
            "python": '''def quicksort(arr):
    """Quicksort implementation - O(n log n) average"""
    if len(arr) <= 1:
        return arr

    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]

    return quicksort(left) + middle + quicksort(right)

# In-place version
def quicksort_inplace(arr, low=0, high=None):
    if high is None:
        high = len(arr) - 1

    if low < high:
        pivot_idx = partition(arr, low, high)
        quicksort_inplace(arr, low, pivot_idx - 1)
        quicksort_inplace(arr, pivot_idx + 1, high)

    return arr

def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1
''',
            "test": '''
def test_quicksort():
    assert quicksort([3, 1, 4, 1, 5, 9, 2, 6]) == [1, 1, 2, 3, 4, 5, 6, 9]
    assert quicksort([]) == []
    assert quicksort([1]) == [1]
    assert quicksort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]
    print("All tests passed!")
'''
        },
        "mergesort": {
            "python": '''def mergesort(arr):
    """Mergesort implementation - O(n log n)"""
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = mergesort(arr[:mid])
    right = mergesort(arr[mid:])

    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result
''',
            "test": '''
def test_mergesort():
    assert mergesort([3, 1, 4, 1, 5, 9, 2, 6]) == [1, 1, 2, 3, 4, 5, 6, 9]
    assert mergesort([]) == []
    assert mergesort([1]) == [1]
    print("All tests passed!")
'''
        },
        "binary_search": {
            "python": '''def binary_search(arr, target):
    """Binary search - O(log n)"""
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = (left + right) // 2

        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1  # Not found

def binary_search_recursive(arr, target, left=0, right=None):
    if right is None:
        right = len(arr) - 1

    if left > right:
        return -1

    mid = (left + right) // 2

    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return binary_search_recursive(arr, target, mid + 1, right)
    else:
        return binary_search_recursive(arr, target, left, mid - 1)
''',
            "test": '''
def test_binary_search():
    arr = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert binary_search(arr, 5) == 4
    assert binary_search(arr, 1) == 0
    assert binary_search(arr, 9) == 8
    assert binary_search(arr, 10) == -1
    print("All tests passed!")
'''
        },
        "dijkstra": {
            "python": '''import heapq
from collections import defaultdict

def dijkstra(graph, start):
    """Dijkstra's shortest path algorithm - O((V + E) log V)"""
    distances = {node: float('infinity') for node in graph}
    distances[start] = 0
    pq = [(0, start)]
    visited = set()

    while pq:
        current_dist, current = heapq.heappop(pq)

        if current in visited:
            continue
        visited.add(current)

        for neighbor, weight in graph[current].items():
            distance = current_dist + weight

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(pq, (distance, neighbor))

    return distances

# Example usage:
# graph = {
#     'A': {'B': 4, 'C': 2},
#     'B': {'A': 4, 'C': 1, 'D': 5},
#     'C': {'A': 2, 'B': 1, 'D': 8},
#     'D': {'B': 5, 'C': 8}
# }
# dijkstra(graph, 'A')  # {'A': 0, 'B': 3, 'C': 2, 'D': 8}
''',
            "test": '''
def test_dijkstra():
    graph = {
        'A': {'B': 4, 'C': 2},
        'B': {'A': 4, 'C': 1, 'D': 5},
        'C': {'A': 2, 'B': 1, 'D': 8},
        'D': {'B': 5, 'C': 8}
    }
    result = dijkstra(graph, 'A')
    assert result['A'] == 0
    assert result['B'] == 3
    assert result['C'] == 2
    assert result['D'] == 8
    print("All tests passed!")
'''
        },
        "bfs": {
            "python": '''from collections import deque

def bfs(graph, start):
    """Breadth-first search - O(V + E)"""
    visited = set([start])
    queue = deque([start])
    result = []

    while queue:
        node = queue.popleft()
        result.append(node)

        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return result

def bfs_shortest_path(graph, start, end):
    """Find shortest path using BFS"""
    if start == end:
        return [start]

    visited = set([start])
    queue = deque([(start, [start])])

    while queue:
        node, path = queue.popleft()

        for neighbor in graph[node]:
            if neighbor == end:
                return path + [neighbor]

            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return None  # No path found
''',
            "test": '''
def test_bfs():
    graph = {
        'A': ['B', 'C'],
        'B': ['A', 'D', 'E'],
        'C': ['A', 'F'],
        'D': ['B'],
        'E': ['B', 'F'],
        'F': ['C', 'E']
    }
    result = bfs(graph, 'A')
    assert result[0] == 'A'
    assert len(result) == 6
    print("All tests passed!")
'''
        },
        "dfs": {
            "python": '''def dfs(graph, start, visited=None):
    """Depth-first search - O(V + E)"""
    if visited is None:
        visited = set()

    visited.add(start)
    result = [start]

    for neighbor in graph[start]:
        if neighbor not in visited:
            result.extend(dfs(graph, neighbor, visited))

    return result

def dfs_iterative(graph, start):
    """Iterative DFS using stack"""
    visited = set()
    stack = [start]
    result = []

    while stack:
        node = stack.pop()

        if node not in visited:
            visited.add(node)
            result.append(node)

            # Add neighbors in reverse order for correct traversal
            for neighbor in reversed(graph[node]):
                if neighbor not in visited:
                    stack.append(neighbor)

    return result
''',
            "test": '''
def test_dfs():
    graph = {
        'A': ['B', 'C'],
        'B': ['A', 'D', 'E'],
        'C': ['A', 'F'],
        'D': ['B'],
        'E': ['B', 'F'],
        'F': ['C', 'E']
    }
    result = dfs(graph, 'A')
    assert result[0] == 'A'
    assert len(result) == 6
    print("All tests passed!")
'''
        }
    }

    # Get implementation
    algo_data = implementations.get(algorithm)

    if not algo_data:
        return [TextContent(
            type="text",
            text=f"❌ Algorithm '{algorithm}' not found in library.\n\n"
                 f"Available: {', '.join(implementations.keys())}"
        )]

    code = algo_data.get(language, algo_data.get("python", ""))
    test = algo_data.get("test", "") if include_tests else ""

    output = f"📝 {algorithm.upper()} Implementation ({language})\n\n"
    output += f"```{language}\n{code}\n```\n"

    if test:
        output += f"\n**Test Cases**:\n```{language}\n{test}\n```\n"

    # Add complexity info
    for category in ALGORITHMS.values():
        if algorithm in category:
            info = category[algorithm]
            output += f"\n**Complexity**:\n"
            output += f"- Time: {info.get('time_complexity', 'N/A')}\n"
            output += f"- Space: {info.get('space_complexity', 'N/A')}\n"
            break

    return [TextContent(type="text", text=output)]


async def handle_algo_compare(args: dict) -> list[TextContent]:
    """Compare two algorithms"""
    algo1 = args.get("algo1", "").lower()
    algo2 = args.get("algo2", "").lower()
    context = args.get("context", "")

    # Find algorithm info
    info1 = None
    info2 = None
    cat1 = cat2 = None

    for category, algos in ALGORITHMS.items():
        if algo1 in algos:
            info1 = algos[algo1]
            cat1 = category
        if algo2 in algos:
            info2 = algos[algo2]
            cat2 = category

    if not info1 or not info2:
        missing = []
        if not info1:
            missing.append(algo1)
        if not info2:
            missing.append(algo2)
        return [TextContent(
            type="text",
            text=f"❌ Algorithm(s) not found: {', '.join(missing)}"
        )]

    # Build comparison
    output = f"⚖️ Algorithm Comparison: {algo1} vs {algo2}\n\n"

    if context:
        output += f"**Context**: {context}\n\n"

    output += f"| Aspect | {algo1} | {algo2} |\n"
    output += f"|--------|--------|--------|\n"
    output += f"| Category | {cat1} | {cat2} |\n"
    output += f"| Time Complexity | {info1.get('time_complexity', 'N/A')} | {info2.get('time_complexity', 'N/A')} |\n"
    output += f"| Space Complexity | {info1.get('space_complexity', 'N/A')} | {info2.get('space_complexity', 'N/A')} |\n"
    output += f"| Best For | {info1.get('best_for', 'N/A')[:30]} | {info2.get('best_for', 'N/A')[:30]} |\n"

    output += f"\n**{algo1}**: {info1.get('description', 'N/A')}\n"
    output += f"**{algo2}**: {info2.get('description', 'N/A')}\n"

    # Recommendation
    output += f"\n**Recommendation**:\n"

    if "log n" in info1.get("time_complexity", "") and "n²" in info2.get("time_complexity", ""):
        output += f"- {algo1} is generally faster for large inputs\n"
    elif "n²" in info1.get("time_complexity", "") and "log n" in info2.get("time_complexity", ""):
        output += f"- {algo2} is generally faster for large inputs\n"
    else:
        output += f"- Choice depends on specific use case and constraints\n"

    if "O(1)" in info1.get("space_complexity", "") and "O(n)" in info2.get("space_complexity", ""):
        output += f"- {algo1} uses less memory\n"
    elif "O(n)" in info1.get("space_complexity", "") and "O(1)" in info2.get("space_complexity", ""):
        output += f"- {algo2} uses less memory\n"

    return [TextContent(type="text", text=output)]


# ============================================================================
# Status Handler
# ============================================================================

async def handle_status(args: dict) -> list[TextContent]:
    """Get overall PEnhance status"""
    output = "🧠 PEnhance Status\n\n"

    # Memory status
    sessions_dir = MEMORY_DIR / "sessions"
    session_count = len(list(sessions_dir.glob("*.json"))) if sessions_dir.exists() else 0
    compressed_dir = MEMORY_DIR / "compressed"
    compressed_count = len(list(compressed_dir.glob("*.json"))) if compressed_dir.exists() else 0

    output += "### Memory\n"
    output += f"- Active Sessions: {session_count}\n"
    output += f"- Compressed Sessions: {compressed_count}\n"
    output += f"- Memory Directory: {MEMORY_DIR}\n\n"

    # Plan status
    plans_dir = MEMORY_DIR / "plans"
    plan_count = len([f for f in plans_dir.glob("*.json")]) if plans_dir.exists() else 0

    active_file = plans_dir / "active_plan.txt"
    active_plan = ""
    if active_file.exists():
        with open(active_file, "r") as f:
            active_plan = f.read().strip()

    output += "### Plans\n"
    output += f"- Total Plans: {plan_count}\n"
    output += f"- Active Plan: {active_plan or 'None'}\n\n"

    # Algorithm library
    algo_count = sum(len(algos) for algos in ALGORITHMS.values())
    output += "### Algorithm Library\n"
    output += f"- Known Algorithms: {algo_count}\n"
    output += f"- Categories: {', '.join(ALGORITHMS.keys())}\n\n"

    # Config
    output += "### Configuration\n"
    output += f"- Project Directory: {PROJECT_DIR}\n"
    output += f"- Scripts Directory: {SCRIPTS_DIR}\n"
    output += f"- Modules Available: {MODULES_AVAILABLE}\n"

    return [TextContent(type="text", text=output)]


# ============================================================================
# Main Entry Point
# ============================================================================

async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
