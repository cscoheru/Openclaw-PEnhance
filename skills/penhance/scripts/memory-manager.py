#!/usr/bin/env python3
"""
Memory Manager - 记忆增强模块

负责上下文的保存、加载、压缩和管理
"""

import json
import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List


class MemoryManager:
    """记忆管理器 - 管理上下文的持久化和检索"""

    def __init__(self, config_path: str):
        """初始化记忆管理器

        Args:
            config_path: 配置文件路径
        """
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.storage_path = Path(self.config['storagePath'])
        self.sessions_path = self.storage_path / 'sessions'
        self.context_path = self.storage_path / 'context'

        # 确保目录存在
        self.sessions_path.mkdir(parents=True, exist_ok=True)
        self.context_path.mkdir(parents=True, exist_ok=True)

        self.current_session: Optional[Dict[str, Any]] = None

    def create_session(self, working_directory: str, project_name: str = "Unknown") -> str:
        """创建新的会话

        Args:
            working_directory: 工作目录
            project_name: 项目名称

        Returns:
            会话ID
        """
        session_id = self._generate_session_id()
        timestamp = datetime.now().isoformat()

        self.current_session = {
            "sessionId": session_id,
            "createdAt": timestamp,
            "updatedAt": timestamp,
            "workingDirectory": working_directory,
            "project": {
                "name": project_name,
                "type": "unknown",
                "language": "unknown"
            },
            "context": {
                "currentTask": "",
                "taskDescription": "",
                "completedWork": [],
                "pendingTasks": [],
                "keyDecisions": [],
                "codeChanges": []
            },
            "memory": {
                "shortTerm": {
                    "recentFiles": [],
                    "recentCommands": [],
                    "activeVariables": {}
                },
                "longTerm": {
                    "patterns": [],
                    "learnings": [],
                    "preferences": {}
                }
            },
            "metadata": {
                "tokenCount": 0,
                "fileCount": 0,
                "commitCount": 0,
                "sessionDuration": 0
            }
        }

        return session_id

    def save_context(self, context_data: Dict[str, Any]) -> str:
        """保存当前上下文

        Args:
            context_data: 上下文数据

        Returns:
            保存的文件路径
        """
        if not self.current_session:
            self.create_session(os.getcwd())

        # 更新会话数据
        self.current_session['updatedAt'] = datetime.now().isoformat()
        self.current_session['context'].update(context_data)

        # 保存到文件
        filename = self._get_session_filename()
        filepath = self.sessions_path / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.current_session, f, indent=2, ensure_ascii=False)

        return str(filepath)

    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """加载指定会话

        Args:
            session_id: 会话ID

        Returns:
            会话数据，如果不存在返回None
        """
        # 查找会话文件
        for file in self.sessions_path.glob('*.json'):
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data.get('sessionId') == session_id:
                    self.current_session = data
                    return data

        return None

    def list_sessions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """列出所有会话

        Args:
            limit: 最大返回数量

        Returns:
            会话列表
        """
        sessions = []

        for file in sorted(self.sessions_path.glob('*.json'), reverse=True)[:limit]:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                sessions.append({
                    "sessionId": data.get('sessionId'),
                    "createdAt": data.get('createdAt'),
                    "workingDirectory": data.get('workingDirectory'),
                    "projectName": data.get('project', {}).get('name', 'Unknown'),
                    "taskCount": len(data.get('context', {}).get('completedWork', []))
                })

        return sessions

    def compress_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """压缩上下文，保留关键信息

        Args:
            context: 原始上下文

        Returns:
            压缩后的上下文
        """
        if not self.config.get('compressionEnabled', False):
            return context

        compression_ratio = self.config.get('compressionRatio', 0.3)

        # 提取关键信息
        compressed = {
            "summary": self._extract_summary(context),
            "keyDecisions": context.get('keyDecisions', [])[-5:],  # 保留最近5个决策
            "activePatterns": self._extract_patterns(context),
            "timestamp": datetime.now().isoformat()
        }

        return compressed

    def save_snapshot(self, snapshot_data: Dict[str, Any]) -> str:
        """保存上下文快照

        Args:
            snapshot_data: 快照数据

        Returns:
            快照文件路径
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"snapshot_{timestamp}.md"
        filepath = self.context_path / filename

        # 转换为 Markdown 格式
        markdown = self._to_markdown(snapshot_data)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown)

        return str(filepath)

    def _generate_session_id(self) -> str:
        """生成唯一会话ID"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_suffix = hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:6]
        return f"{timestamp}_{random_suffix}"

    def _get_session_filename(self) -> str:
        """获取会话文件名"""
        date = datetime.now().strftime('%Y-%m-%d')
        index = len(list(self.sessions_path.glob(f'{date}_session_*.json'))) + 1
        return f"{date}_session_{index:03d}.json"

    def _extract_summary(self, context: Dict[str, Any]) -> str:
        """提取上下文摘要"""
        # 简单实现：提取任务描述和最近完成的工作
        parts = []

        if context.get('currentTask'):
            parts.append(f"当前任务: {context['currentTask']}")

        completed = context.get('completedWork', [])
        if completed:
            parts.append(f"已完成工作: {len(completed)} 项")

        return " | ".join(parts)

    def _extract_patterns(self, context: Dict[str, Any]) -> List[str]:
        """提取代码模式"""
        # 简单实现：从代码变更中提取模式
        patterns = []
        for change in context.get('codeChanges', []):
            if change.get('type') == 'pattern':
                patterns.append(change.get('description', ''))
        return patterns[:10]  # 保留最近10个模式

    def _to_markdown(self, data: Dict[str, Any]) -> str:
        """将数据转换为 Markdown 格式"""
        lines = [
            "# 上下文快照",
            f"\n**时间**: {datetime.now().isoformat()}",
            f"**工作目录**: {data.get('workingDirectory', 'N/A')}",
            "\n---\n",
            "## 当前任务",
            data.get('currentTask', '无'),
            "\n## 已完成工作",
        ]

        for work in data.get('completedWork', []):
            lines.append(f"- {work}")

        lines.extend([
            "\n## 待办事项",
        ])

        for task in data.get('pendingTasks', []):
            lines.append(f"- [ ] {task}")

        return "\n".join(lines)


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description='Memory Manager for PEnhance')
    parser.add_argument('command', choices=['save', 'load', 'list', 'compress', 'snapshot'])
    parser.add_argument('--session-id', help='Session ID for load command')
    parser.add_argument('--config', default='/Users/kjonekong/OpenClaw-PEnhance/config/memory-config.json')
    parser.add_argument('--data', help='JSON data for save command')

    args = parser.parse_args()

    manager = MemoryManager(args.config)

    if args.command == 'list':
        sessions = manager.list_sessions()
        print(json.dumps(sessions, indent=2))

    elif args.command == 'load':
        if not args.session_id:
            print("Error: --session-id required for load command")
            return
        data = manager.load_session(args.session_id)
        if data:
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"Session not found: {args.session_id}")

    elif args.command == 'save':
        if not args.data:
            print("Error: --data required for save command")
            return
        context = json.loads(args.data)
        filepath = manager.save_context(context)
        print(f"Session saved to: {filepath}")

    elif args.command == 'compress':
        if not args.data:
            print("Error: --data required for compress command")
            return
        context = json.loads(args.data)
        compressed = manager.compress_context(context)
        print(json.dumps(compressed, indent=2, ensure_ascii=False))

    elif args.command == 'snapshot':
        if not args.data:
            print("Error: --data required for snapshot command")
            return
        data = json.loads(args.data)
        filepath = manager.save_snapshot(data)
        print(f"Snapshot saved to: {filepath}")


if __name__ == '__main__':
    main()
