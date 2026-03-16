#!/bin/bash
# PEnhance Hook - 文件保存时自动触发上下文保存
# 由 Claude Code PostToolUse hook 调用

set -e

PROJECT_DIR="/Users/kjonekong/OpenClaw-PEnhance"
MEMORY_SCRIPT="$PROJECT_DIR/skills/penhance/scripts/memory-manager.py"
LOG_FILE="$PROJECT_DIR/logs/hook.log"

# 记录日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 检查是否是代码文件
is_code_file() {
    local file="$1"
    [[ "$file" =~ \.(py|js|ts|jsx|tsx|go|rs|java|cpp|c|h|md|json)$ ]]
}

# 主逻辑
main() {
    # 从 stdin 获取 hook 数据
    local hook_data
    hook_data=$(cat)

    # 提取文件路径
    local file_path=$(echo "$hook_data" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))" 2>/dev/null || echo "")

    if [[ -z "$file_path" ]]; then
        log "No file path in hook data"
        exit 0
    fi

    # 只处理代码文件
    if ! is_code_file "$file_path"; then
        log "Skipping non-code file: $file_path"
        exit 0
    fi

    log "Processing: $file_path"

    # 保存上下文
    local context_data=$(cat <<EOF
{
    "currentTask": "File saved: $file_path",
    "codeChanges": [{
        "file_path": "$file_path",
        "change_type": "modify",
        "timestamp": "$(date -Iseconds)"
    }]
}
EOF
)

    python3 "$MEMORY_SCRIPT" save --data "$context_data" >> "$LOG_FILE" 2>&1

    log "Context saved for: $file_path"
}

main
