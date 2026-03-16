#!/usr/bin/env python3
"""
Algorithm Analyzer - 算法增强分析器

识别、分析和优化复杂算法
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass


@dataclass
class AlgorithmInfo:
    """算法信息数据类"""
    name: str
    category: str  # sorting, searching, graph, dp, greedy, backtracking, ml
    time_complexity: str
    space_complexity: str
    description: str
    pseudocode: Optional[str] = None
    test_cases: Optional[List[Dict]] = None
    optimizations: Optional[List[str]] = None


# 算法模式库
ALGORITHM_PATTERNS = {
    "sorting": {
        "quicksort": {
            "patterns": ["partition", "pivot", "quick_sort", "quicksort"],
            "time_complexity": "O(n log n) avg, O(n²) worst",
            "space_complexity": "O(log n)",
            "description": "分治排序算法，通过选择基准元素进行分区"
        },
        "mergesort": {
            "patterns": ["merge", "merge_sort", "mergesort", "left", "right"],
            "time_complexity": "O(n log n)",
            "space_complexity": "O(n)",
            "description": "分治排序算法，将数组分成两半分别排序后合并"
        },
        "heapsort": {
            "patterns": ["heapify", "heap", "max_heap", "min_heap", "heap_sort"],
            "time_complexity": "O(n log n)",
            "space_complexity": "O(1)",
            "description": "利用堆数据结构进行排序"
        }
    },
    "searching": {
        "binary_search": {
            "patterns": ["binary_search", "mid", "left", "right", "target"],
            "time_complexity": "O(log n)",
            "space_complexity": "O(1)",
            "description": "在有序数组中查找目标值"
        },
        "dfs": {
            "patterns": ["dfs", "depth_first", "visited", "recursive", "stack"],
            "time_complexity": "O(V + E)",
            "space_complexity": "O(V)",
            "description": "深度优先搜索，优先访问深度节点"
        },
        "bfs": {
            "patterns": ["bfs", "breadth_first", "queue", "level", "enqueue"],
            "time_complexity": "O(V + E)",
            "space_complexity": "O(V)",
            "description": "广度优先搜索，优先访问同一层节点"
        }
    },
    "graph": {
        "dijkstra": {
            "patterns": ["dijkstra", "shortest_path", "priority_queue", "dist", "relax"],
            "time_complexity": "O((V + E) log V)",
            "space_complexity": "O(V)",
            "description": "单源最短路径算法，适用于非负权重图"
        },
        "bellman_ford": {
            "patterns": ["bellman", "ford", "relax", "edge", "negative"],
            "time_complexity": "O(V * E)",
            "space_complexity": "O(V)",
            "description": "单源最短路径算法，可处理负权重"
        },
        "floyd_warshall": {
            "patterns": ["floyd", "warshall", "all_pairs", "distance_matrix"],
            "time_complexity": "O(V³)",
            "space_complexity": "O(V²)",
            "description": "所有节点对的最短路径算法"
        }
    },
    "dynamic_programming": {
        "knapsack": {
            "patterns": ["knapsack", "weight", "value", "dp", "capacity"],
            "time_complexity": "O(n * W)",
            "space_complexity": "O(n * W)",
            "description": "背包问题 - 在容量限制下最大化价值"
        },
        "lcs": {
            "patterns": ["lcs", "longest_common", "subsequence", "dp"],
            "time_complexity": "O(m * n)",
            "space_complexity": "O(m * n)",
            "description": "最长公共子序列问题"
        },
        "edit_distance": {
            "patterns": ["edit_distance", "levenshtein", "insert", "delete", "replace"],
            "time_complexity": "O(m * n)",
            "space_complexity": "O(m * n)",
            "description": "编辑距离 - 最小操作数将一个字符串转换为另一个"
        }
    },
    "greedy": {
        "activity_selection": {
            "patterns": ["activity", "select", "greedy", "finish_time", "interval"],
            "time_complexity": "O(n log n)",
            "space_complexity": "O(1)",
            "description": "活动选择问题 - 选择最大兼容活动集合"
        },
        "huffman": {
            "patterns": ["huffman", "frequency", "encoding", "priority_queue"],
            "time_complexity": "O(n log n)",
            "space_complexity": "O(n)",
            "description": "霍夫曼编码 - 最优前缀编码"
        }
    },
    "backtracking": {
        "n_queens": {
            "patterns": ["queen", "n_queens", "backtrack", "board", "valid"],
            "time_complexity": "O(N!)",
            "space_complexity": "O(N)",
            "description": "N皇后问题 - 在NxN棋盘放置N个皇后"
        },
        "sudoku": {
            "patterns": ["sudoku", "solve", "backtrack", "valid", "cell"],
            "time_complexity": "O(9^(n*n))",
            "space_complexity": "O(n*n)",
            "description": "数独求解器"
        }
    },
    "machine_learning": {
        "gradient_descent": {
            "patterns": ["gradient", "descent", "learning_rate", "loss", "update"],
            "time_complexity": "O(iterations * n)",
            "space_complexity": "O(n)",
            "description": "梯度下降优化算法"
        },
        "kmeans": {
            "patterns": ["kmeans", "centroid", "cluster", "distance", "assign"],
            "time_complexity": "O(n * k * iterations)",
            "space_complexity": "O(k + n)",
            "description": "K-Means 聚类算法"
        }
    }
}


class AlgorithmAnalyzer:
    """算法分析器 - 识别、分析和优化算法"""

    def __init__(self, config_path: str):
        """初始化算法分析器

        Args:
            config_path: 配置文件路径
        """
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.algorithms_path = Path(self.config['algorithmsPath'])
        self.algorithms_path.mkdir(parents=True, exist_ok=True)

    def identify_algorithm(self, code: str) -> Optional[Tuple[str, str, Dict]]:
        """识别代码中的算法

        Args:
            code: 代码字符串

        Returns:
            (算法名, 类别, 信息) 或 None
        """
        code_lower = code.lower()

        best_match = None
        best_score = 0

        for category, algorithms in ALGORITHM_PATTERNS.items():
            for algo_name, algo_info in algorithms.items():
                patterns = algo_info['patterns']
                score = sum(1 for p in patterns if p in code_lower)

                if score > best_score:
                    best_score = score
                    best_match = (algo_name, category, algo_info)

        if best_match and best_score >= 2:  # 至少匹配2个模式
            return best_match

        return None

    def analyze(self, code: str) -> Dict[str, Any]:
        """分析代码中的算法

        Args:
            code: 代码字符串

        Returns:
            分析结果
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "codeLength": len(code),
            "identified": False,
            "algorithm": None,
            "analysis": None
        }

        # 识别算法
        identified = self.identify_algorithm(code)

        if identified:
            algo_name, category, algo_info = identified
            result["identified"] = True
            result["algorithm"] = {
                "name": algo_name,
                "category": category,
                "description": algo_info["description"],
                "timeComplexity": algo_info["time_complexity"],
                "spaceComplexity": algo_info["space_complexity"]
            }

            # 生成详细分析
            result["analysis"] = self._generate_analysis(code, algo_name, category, algo_info)

        else:
            result["analysis"] = self._generate_generic_analysis(code)

        return result

    def _generate_analysis(self, code: str, algo_name: str, category: str, algo_info: Dict) -> Dict[str, Any]:
        """生成算法详细分析

        Args:
            code: 代码
            algo_name: 算法名
            category: 类别
            algo_info: 算法信息

        Returns:
            分析结果
        """
        analysis = {
            "complexityAnalysis": {
                "time": algo_info["time_complexity"],
                "space": algo_info["space_complexity"],
                "explanation": self._explain_complexity(algo_info["time_complexity"])
            },
            "boundaryConditions": self._identify_boundaries(code),
            "optimizations": self._suggest_optimizations(algo_name, category),
            "pseudocode": self._generate_pseudocode(algo_name),
            "testCases": self._generate_test_cases(algo_name, category)
        }

        return analysis

    def _generate_generic_analysis(self, code: str) -> Dict[str, Any]:
        """生成通用分析（未识别算法时）

        Args:
            code: 代码

        Returns:
            分析结果
        """
        return {
            "complexityAnalysis": {
                "time": "需要进一步分析",
                "space": "需要进一步分析",
                "explanation": "未能自动识别算法类型，请手动分析"
            },
            "boundaryConditions": self._identify_boundaries(code),
            "suggestions": [
                "考虑添加算法名称注释",
                "确保代码结构清晰",
                "添加输入验证"
            ]
        }

    def _explain_complexity(self, complexity: str) -> str:
        """解释复杂度含义"""
        explanations = {
            "O(1)": "常数时间 - 无论输入大小，执行时间固定",
            "O(log n)": "对数时间 - 每次操作将问题规模减半",
            "O(n)": "线性时间 - 执行时间与输入大小成正比",
            "O(n log n)": "线性对数时间 - 常见于高效排序算法",
            "O(n²)": "平方时间 - 嵌套循环常见",
            "O(n³)": "立方时间 - 三层嵌套循环",
            "O(2^n)": "指数时间 - 问题规模翻倍，时间翻倍",
            "O(n!)": "阶乘时间 - 组合/排列问题常见"
        }

        for key, explanation in explanations.items():
            if key in complexity:
                return explanation

        return "复杂度取决于具体输入"

    def _identify_boundaries(self, code: str) -> List[Dict[str, str]]:
        """识别边界条件"""
        boundaries = []

        # 检查常见边界条件
        if "len(" in code or ".length" in code:
            boundaries.append({
                "condition": "空输入",
                "check": "检查数组/字符串长度是否为0",
                "handling": "返回默认值或抛出异常"
            })

        if "range(" in code or "for" in code:
            boundaries.append({
                "condition": "单元素",
                "check": "检查输入是否只有一个元素",
                "handling": "直接返回该元素"
            })

        if "[-1]" in code or "[-2]" in code:
            boundaries.append({
                "condition": "索引越界",
                "check": "确保索引在有效范围内",
                "handling": "添加边界检查"
            })

        if "/" in code or "//" in code:
            boundaries.append({
                "condition": "除零错误",
                "check": "检查除数是否为0",
                "handling": "返回特殊值或抛出异常"
            })

        return boundaries

    def _suggest_optimizations(self, algo_name: str, category: str) -> List[str]:
        """建议优化方向"""
        optimizations = {
            "sorting": [
                "考虑使用内置排序函数（通常经过高度优化）",
                "对于小数组，插入排序可能更快",
                "考虑并行化排序过程"
            ],
            "searching": [
                "确保数据已排序（二分查找）",
                "考虑使用哈希表进行O(1)查找",
                "对于频繁查询，考虑建立索引"
            ],
            "graph": [
                "使用优先队列优化Dijkstra",
                "考虑使用邻接表而非邻接矩阵",
                "对于稀疏图，考虑特殊数据结构"
            ],
            "dynamic_programming": [
                "考虑空间优化（滚动数组）",
                "识别重复子问题",
                "考虑自底向上而非递归"
            ],
            "backtracking": [
                "添加剪枝条件减少搜索空间",
                "考虑使用启发式函数",
                "尽早检测无效路径"
            ]
        }

        return optimizations.get(category, [
            "分析热点代码路径",
            "考虑缓存重复计算",
            "使用适当的数据结构"
        ])

    def _generate_pseudocode(self, algo_name: str) -> str:
        """生成伪代码"""
        pseudocodes = {
            "quicksort": """
function quicksort(arr, low, high):
    if low < high:
        pivot = partition(arr, low, high)
        quicksort(arr, low, pivot - 1)
        quicksort(arr, pivot + 1, high)

function partition(arr, low, high):
    pivot = arr[high]
    i = low - 1
    for j = low to high - 1:
        if arr[j] <= pivot:
            i++
            swap(arr[i], arr[j])
    swap(arr[i + 1], arr[high])
    return i + 1
""",
            "binary_search": """
function binary_search(arr, target):
    left = 0
    right = length(arr) - 1

    while left <= right:
        mid = (left + right) / 2
        if arr[mid] == target:
            return mid
        else if arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1  // Not found
""",
            "dfs": """
function dfs(graph, start, visited):
    visited.add(start)
    process(start)

    for neighbor in graph[start]:
        if neighbor not in visited:
            dfs(graph, neighbor, visited)
""",
            "bfs": """
function bfs(graph, start):
    queue = [start]
    visited = {start}

    while queue is not empty:
        node = queue.dequeue()
        process(node)

        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.enqueue(neighbor)
"""
        }

        return pseudocodes.get(algo_name, f"// 伪代码待生成: {algo_name}")

    def _generate_test_cases(self, algo_name: str, category: str) -> List[Dict]:
        """生成测试用例"""
        test_cases = []

        # 基本测试
        test_cases.append({
            "name": "基本输入",
            "input": "正常大小的输入",
            "expected": "预期正确输出"
        })

        # 边界测试
        test_cases.append({
            "name": "空输入",
            "input": "空数组/空字符串",
            "expected": "返回空结果或默认值"
        })

        test_cases.append({
            "name": "最小输入",
            "input": "单元素",
            "expected": "返回该元素"
        })

        # 性能测试
        test_cases.append({
            "name": "大输入",
            "input": "10000+ 元素",
            "expected": "在合理时间内完成"
        })

        return test_cases

    def save_analysis(self, analysis: Dict[str, Any], algo_name: str) -> str:
        """保存分析结果

        Args:
            analysis: 分析结果
            algo_name: 算法名

        Returns:
            保存的文件路径
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{algo_name}_{timestamp}.md"
        filepath = self.algorithms_path / filename

        # 转换为 Markdown
        markdown = self._analysis_to_markdown(analysis, algo_name)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown)

        return str(filepath)

    def _analysis_to_markdown(self, analysis: Dict, algo_name: str) -> str:
        """将分析结果转换为 Markdown"""
        lines = [
            f"# 算法分析: {algo_name}",
            f"\n**分析时间**: {analysis['timestamp']}",
            f"**代码长度**: {analysis['codeLength']} 字符",
            "\n---\n"
        ]

        if analysis['identified']:
            algo = analysis['algorithm']
            lines.extend([
                "## 算法信息",
                f"- **名称**: {algo['name']}",
                f"- **类别**: {algo['category']}",
                f"- **描述**: {algo['description']}",
                f"- **时间复杂度**: {algo['timeComplexity']}",
                f"- **空间复杂度**: {algo['spaceComplexity']}",
                "\n"
            ])

        if analysis['analysis']:
            details = analysis['analysis']

            if 'complexityAnalysis' in details:
                lines.extend([
                    "## 复杂度分析",
                    f"- **时间**: {details['complexityAnalysis']['time']}",
                    f"- **空间**: {details['complexityAnalysis']['space']}",
                    f"- **解释**: {details['complexityAnalysis']['explanation']}",
                    "\n"
                ])

            if 'boundaryConditions' in details:
                lines.append("## 边界条件\n")
                for bc in details['boundaryConditions']:
                    lines.append(f"- **{bc['condition']}**: {bc['handling']}")
                lines.append("\n")

            if 'optimizations' in details:
                lines.append("## 优化建议\n")
                for opt in details['optimizations']:
                    lines.append(f"- {opt}")
                lines.append("\n")

            if 'pseudocode' in details:
                lines.extend([
                    "## 伪代码",
                    "```",
                    details['pseudocode'].strip(),
                    "```\n"
                ])

        return "\n".join(lines)


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description='Algorithm Analyzer for PEnhance')
    parser.add_argument('command', choices=['analyze', 'identify', 'save'])
    parser.add_argument('--code', help='Code to analyze')
    parser.add_argument('--file', help='File containing code to analyze')
    parser.add_argument('--config', default='/Users/kjonekong/OpenClaw-PEnhance/config/algorithm-config.json')

    args = parser.parse_args()

    analyzer = AlgorithmAnalyzer(args.config)

    code = args.code or ""
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            code = f.read()

    if args.command == 'identify':
        result = analyzer.identify_algorithm(code)
        if result:
            print(f"识别到算法: {result[0]} ({result[1]})")
        else:
            print("未能识别算法")

    elif args.command == 'analyze':
        result = analyzer.analyze(code)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == 'save':
        result = analyzer.analyze(code)
        if result['identified']:
            filepath = analyzer.save_analysis(result, result['algorithm']['name'])
            print(f"分析已保存到: {filepath}")
        else:
            print("未能识别算法，无法保存分析")


if __name__ == '__main__':
    main()
