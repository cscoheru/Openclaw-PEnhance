#!/usr/bin/env python3
"""
Plan Enforcer - 计划与代码匹配强制器

监控代码变更与开发计划的匹配程度，防止任务漂移
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass


@dataclass
class Task:
    """任务数据类"""
    id: str
    description: str
    status: str  # pending, in_progress, completed
    phase: str
    estimated_hours: float = 0.0
    actual_hours: float = 0.0
    code_references: List[str] = None

    def __post_init__(self):
        if self.code_references is None:
            self.code_references = []


@dataclass
class CodeChange:
    """代码变更数据类"""
    file_path: str
    change_type: str  # add, modify, delete
    description: str
    timestamp: str
    matched_task: Optional[str] = None
    match_score: float = 0.0


class PlanEnforcer:
    """计划强制器 - 监控代码与计划的匹配"""

    def __init__(self, config_path: str):
        """初始化计划强制器

        Args:
            config_path: 配置文件路径
        """
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.plans_path = Path(self.config['plansPath'])
        self.plans_path.mkdir(parents=True, exist_ok=True)

        self.current_plan: Optional[Dict[str, Any]] = None
        self.tasks: List[Task] = []
        self.changes: List[CodeChange] = []

    def load_plan(self, plan_path: str) -> bool:
        """加载开发计划

        Args:
            plan_path: 计划文件路径

        Returns:
            是否加载成功
        """
        try:
            with open(plan_path, 'r', encoding='utf-8') as f:
                content = f.read()

            self.current_plan = {
                "path": plan_path,
                "content": content,
                "loadedAt": datetime.now().isoformat()
            }

            # 解析任务
            self.tasks = self._parse_tasks(content)

            return True
        except Exception as e:
            print(f"Error loading plan: {e}")
            return False

    def _parse_tasks(self, content: str) -> List[Task]:
        """从计划内容解析任务

        Args:
            content: 计划文件内容

        Returns:
            任务列表
        """
        tasks = []
        task_pattern = r'- \[([ x])\] (Task \d+\.\d+): (.+?) - 预计: (\d+\.?\d*)h - 状态: (\w+)'

        for match in re.finditer(task_pattern, content):
            checked, task_id, description, hours, status = match.groups()
            tasks.append(Task(
                id=task_id,
                description=description,
                status=status,
                phase=task_id.split('.')[0],
                estimated_hours=float(hours)
            ))

        return tasks

    def analyze_change(self, change: CodeChange) -> Tuple[float, Optional[str]]:
        """分析代码变更与计划的匹配度

        Args:
            change: 代码变更

        Returns:
            (匹配分数, 匹配的任务ID)
        """
        if not self.tasks:
            return 0.0, None

        best_match = None
        best_score = 0.0

        # 计算与每个任务的相似度
        for task in self.tasks:
            score = self._calculate_similarity(change.description, task.description)
            if score > best_score:
                best_score = score
                best_match = task.id

        change.matched_task = best_match
        change.match_score = best_score

        self.changes.append(change)

        return best_score, best_match

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度

        Args:
            text1: 文本1
            text2: 文本2

        Returns:
            相似度分数 (0-1)
        """
        # 简单的关键词匹配实现
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union)

    def check_deviation(self) -> Dict[str, Any]:
        """检查计划偏离情况

        Returns:
            偏离分析报告
        """
        if not self.changes:
            return {"status": "no_changes", "deviation": 0.0}

        # 计算总体偏离度
        total_score = sum(c.match_score for c in self.changes)
        avg_score = total_score / len(self.changes)
        deviation = 1.0 - avg_score

        # 检查未匹配的变更
        unmatched_changes = [c for c in self.changes if c.match_score < 0.3]

        # 检查未完成的任务
        pending_tasks = [t for t in self.tasks if t.status == 'pending']
        completed_tasks = [t for t in self.tasks if t.status == 'completed']

        return {
            "status": "analyzed",
            "deviation": round(deviation, 2),
            "averageMatchScore": round(avg_score, 2),
            "totalChanges": len(self.changes),
            "unmatchedChanges": len(unmatched_changes),
            "pendingTasks": len(pending_tasks),
            "completedTasks": len(completed_tasks),
            "unmatchedDetails": [
                {
                    "file": c.file_path,
                    "description": c.description,
                    "score": c.match_score
                }
                for c in unmatched_changes[:5]  # 只显示前5个
            ]
        }

    def suggest_actions(self, deviation_report: Dict[str, Any]) -> List[str]:
        """根据偏离报告建议行动

        Args:
            deviation_report: 偏离报告

        Returns:
            建议的行动列表
        """
        suggestions = []
        deviation = deviation_report.get('deviation', 0)

        if deviation > self.config['enforcement']['blockThreshold']:
            suggestions.append("⚠️ 严重偏离计划！建议：")
            suggestions.append("  1. 回滚最近的代码变更")
            suggestions.append("  2. 重新审视开发计划")
            suggestions.append("  3. 与团队讨论优先级")

        elif deviation > self.config['enforcement']['warnThreshold']:
            suggestions.append("⚡ 检测到任务漂移，建议：")
            suggestions.append("  1. 更新计划以包含新任务")
            suggestions.append("  2. 标记为技术债务")

        else:
            suggestions.append("✅ 代码变更与计划匹配良好")

        # 添加具体建议
        if deviation_report.get('unmatchedChanges', 0) > 0:
            suggestions.append(f"\n未匹配的变更 ({deviation_report['unmatchedChanges']} 项):")
            for detail in deviation_report.get('unmatchedDetails', []):
                suggestions.append(f"  - {detail['file']}: {detail['description']}")

        return suggestions

    def update_task_status(self, task_id: str, new_status: str) -> bool:
        """更新任务状态

        Args:
            task_id: 任务ID
            new_status: 新状态

        Returns:
            是否更新成功
        """
        for task in self.tasks:
            if task.id == task_id:
                task.status = new_status
                return True
        return False

    def get_status_report(self) -> Dict[str, Any]:
        """获取状态报告

        Returns:
            状态报告
        """
        if not self.current_plan:
            return {"error": "No plan loaded"}

        return {
            "planPath": self.current_plan['path'],
            "loadedAt": self.current_plan['loadedAt'],
            "totalTasks": len(self.tasks),
            "pendingTasks": len([t for t in self.tasks if t.status == 'pending']),
            "completedTasks": len([t for t in self.tasks if t.status == 'completed']),
            "inProgressTasks": len([t for t in self.tasks if t.status == 'in_progress']),
            "totalChanges": len(self.changes),
            "tasks": [
                {
                    "id": t.id,
                    "description": t.description,
                    "status": t.status,
                    "phase": t.phase
                }
                for t in self.tasks
            ]
        }


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description='Plan Enforcer for PEnhance')
    parser.add_argument('command', choices=['load', 'analyze', 'status', 'deviation', 'suggest'])
    parser.add_argument('--plan', help='Plan file path')
    parser.add_argument('--config', default='/Users/kjonekong/OpenClaw-PEnhance/config/plan-config.json')
    parser.add_argument('--change', help='Code change description')
    parser.add_argument('--file', help='Changed file path')

    args = parser.parse_args()

    enforcer = PlanEnforcer(args.config)

    if args.command == 'load':
        if not args.plan:
            print("Error: --plan required for load command")
            return
        success = enforcer.load_plan(args.plan)
        print(f"Plan loaded: {success}")

    elif args.command == 'status':
        report = enforcer.get_status_report()
        print(json.dumps(report, indent=2, ensure_ascii=False))

    elif args.command == 'analyze':
        if not args.change:
            print("Error: --change required for analyze command")
            return
        change = CodeChange(
            file_path=args.file or 'unknown',
            change_type='modify',
            description=args.change,
            timestamp=datetime.now().isoformat()
        )
        score, task = enforcer.analyze_change(change)
        print(f"Match score: {score:.2f}, Task: {task}")

    elif args.command == 'deviation':
        report = enforcer.check_deviation()
        print(json.dumps(report, indent=2, ensure_ascii=False))

    elif args.command == 'suggest':
        report = enforcer.check_deviation()
        suggestions = enforcer.suggest_actions(report)
        for suggestion in suggestions:
            print(suggestion)


if __name__ == '__main__':
    main()
