# 常用算法模式参考

## 一、排序算法

### 1.1 快速排序

```python
def quicksort(arr):
    if len(arr) <= 1:
        return arr

    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]

    return quicksort(left) + middle + quicksort(right)
```

**复杂度**: 时间 O(n log n) 平均, 空间 O(log n)

---

### 1.2 归并排序

```python
def mergesort(arr):
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
```

**复杂度**: 时间 O(n log n), 空间 O(n)

---

## 二、搜索算法

### 2.1 二分查找

```python
def binary_search(arr, target):
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = (left + right) // 2

        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1  # 未找到
```

**复杂度**: 时间 O(log n), 空间 O(1)

---

### 2.2 深度优先搜索 (DFS)

```python
def dfs(graph, start, visited=None):
    if visited is None:
        visited = set()

    visited.add(start)
    print(start)

    for neighbor in graph[start]:
        if neighbor not in visited:
            dfs(graph, neighbor, visited)

    return visited
```

**复杂度**: 时间 O(V + E), 空间 O(V)

---

### 2.3 广度优先搜索 (BFS)

```python
from collections import deque

def bfs(graph, start):
    visited = set()
    queue = deque([start])
    visited.add(start)

    while queue:
        vertex = queue.popleft()
        print(vertex)

        for neighbor in graph[vertex]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return visited
```

**复杂度**: 时间 O(V + E), 空间 O(V)

---

## 三、图算法

### 3.1 Dijkstra 最短路径

```python
import heapq

def dijkstra(graph, start):
    distances = {vertex: float('infinity') for vertex in graph}
    distances[start] = 0
    pq = [(0, start)]

    while pq:
        current_distance, current_vertex = heapq.heappop(pq)

        if current_distance > distances[current_vertex]:
            continue

        for neighbor, weight in graph[current_vertex].items():
            distance = current_distance + weight

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(pq, (distance, neighbor))

    return distances
```

**复杂度**: 时间 O((V + E) log V), 空间 O(V)

---

## 四、动态规划

### 4.1 背包问题

```python
def knapsack(weights, values, capacity):
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(capacity + 1):
            if weights[i-1] <= w:
                dp[i][w] = max(
                    dp[i-1][w],
                    dp[i-1][w - weights[i-1]] + values[i-1]
                )
            else:
                dp[i][w] = dp[i-1][w]

    return dp[n][capacity]
```

**复杂度**: 时间 O(n * W), 空间 O(n * W)

---

### 4.2 最长公共子序列 (LCS)

```python
def lcs(text1, text2):
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i-1] == text2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])

    return dp[m][n]
```

**复杂度**: 时间 O(m * n), 空间 O(m * n)

---

## 五、贪心算法

### 5.1 活动选择

```python
def activity_selection(start, finish):
    activities = sorted(zip(start, finish), key=lambda x: x[1])
    selected = [activities[0]]

    for i in range(1, len(activities)):
        if activities[i][0] >= selected[-1][1]:
            selected.append(activities[i])

    return selected
```

**复杂度**: 时间 O(n log n), 空间 O(1)

---

## 六、算法选择指南

| 问题类型 | 推荐算法 | 时间复杂度 |
|----------|----------|------------|
| 小数组排序 | 插入排序 | O(n²) |
| 通用排序 | 快速/归并排序 | O(n log n) |
| 有序查找 | 二分查找 | O(log n) |
| 最短路径 | Dijkstra/BFS | O((V+E) log V) |
| 最优子结构 | 动态规划 | 视问题而定 |
| 局部最优 | 贪心 | 通常 O(n log n) |
