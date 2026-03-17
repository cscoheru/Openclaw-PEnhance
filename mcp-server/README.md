# PEnhance MCP Server

Programming Enhancement Tools for Claude Code via MCP (Model Context Protocol).

## Installation

```bash
# Install dependencies
pip3 install mcp
```

## Configuration

Add to `~/.claude.json`:

```json
{
  "mcpServers": {
    "penhance": {
      "command": "python3",
      "args": ["/Users/kjonekong/OpenClaw-PEnhance/mcp-server/penhance_mcp.py"],
      "description": "PEnhance - Programming Enhancement Tools"
    }
  }
}
```

## Available Tools

### Memory Tools

| Tool | Description |
|------|-------------|
| `penhance_memory_save` | Save current context/session to memory |
| `penhance_memory_load` | Load a saved session by ID |
| `penhance_memory_list` | List all saved sessions |
| `penhance_memory_compress` | Compress old memories |

### Plan Tools

| Tool | Description |
|------|-------------|
| `penhance_plan_create` | Create a new development plan |
| `penhance_plan_track` | Start tracking a plan |
| `penhance_plan_status` | Get plan completion status |
| `penhance_plan_check` | Check if code change matches plan |
| `penhance_plan_list` | List all plans |

### Algorithm Tools

| Tool | Description |
|------|-------------|
| `penhance_algo_analyze` | Analyze code for algorithms |
| `penhance_algo_suggest` | Get algorithm suggestions |
| `penhance_algo_generate` | Generate algorithm implementation |
| `penhance_algo_compare` | Compare two algorithms |

### Status

| Tool | Description |
|------|-------------|
| `penhance_status` | Get overall PEnhance status |

## Usage Examples

### Save Memory
```json
{
  "task": "Implementing user authentication",
  "context": {
    "files_modified": ["auth.py", "models.py"],
    "decisions": ["Using JWT tokens", "bcrypt for passwords"]
  }
}
```

### Create Plan
```json
{
  "name": "User Auth Feature",
  "tasks": [
    "Create User model",
    "Implement login endpoint",
    "Add JWT middleware",
    "Write tests"
  ]
}
```

### Analyze Algorithm
```json
{
  "code": "def quicksort(arr): ...",
  "language": "python"
}
```

## Architecture

```
penhance_mcp.py
├── Memory Tools (save/load/list/compress)
├── Plan Tools (create/track/status/check/list)
├── Algorithm Tools (analyze/suggest/generate/compare)
└── Status Tool

Data Storage:
├── memory/sessions/    # Saved contexts
├── memory/plans/       # Development plans
└── memory/compressed/  # Compressed old memories
```

## Related

- Main Skill: `~/OpenClaw-PEnhance/skills/penhance/SKILL.md`
- Hook Script: `~/OpenClaw-PEnhance/scripts/penhance-hook.sh`
- Original Scripts: `~/OpenClaw-PEnhance/skills/penhance/scripts/`
