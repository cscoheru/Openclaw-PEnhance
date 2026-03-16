# 编程最佳实践参考

## 一、代码质量

### 1.1 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 变量 | 小写+下划线 | `user_name`, `item_count` |
| 常量 | 大写+下划线 | `MAX_SIZE`, `DEFAULT_TIMEOUT` |
| 函数 | 动词+名词 | `get_user_by_id()`, `calculate_total()` |
| 类 | 大驼峰 | `UserManager`, `OrderProcessor` |

### 1.2 函数设计

```python
# 好的函数设计
def calculate_discount(price: float, discount_rate: float) -> float:
    """
    计算折扣后价格

    Args:
        price: 原价
        discount_rate: 折扣率 (0-1)

    Returns:
        折扣后价格
    """
    if not 0 <= discount_rate <= 1:
        raise ValueError("折扣率必须在 0-1 之间")
    return price * (1 - discount_rate)
```

### 1.3 错误处理

```python
# 好的错误处理
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"操作失败: {e}")
    raise  # 或返回默认值
```

---

## 二、安全实践

### 2.1 输入验证

```python
# 始终验证外部输入
def process_user_input(data: dict) -> None:
    if not isinstance(data, dict):
        raise TypeError("输入必须是字典")

    required_fields = ['name', 'email']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"缺少必需字段: {field}")
```

### 2.2 避免常见漏洞

| 漏洞 | 防护 |
|------|------|
| SQL注入 | 使用参数化查询 |
| XSS | 输出编码 |
| CSRF | CSRF Token |
| 命令注入 | 避免shell=True |

---

## 三、性能优化

### 3.1 时间复杂度优化

| 场景 | 优化方法 |
|------|----------|
| 频繁查找 | 使用哈希表 |
| 大数据排序 | 考虑外部排序 |
| 重复计算 | 添加缓存 |
| 深度递归 | 改用迭代 |

### 3.2 空间优化

```python
# 使用生成器节省内存
def read_large_file(file_path):
    with open(file_path) as f:
        for line in f:
            yield line.strip()
```

---

## 四、测试原则

### 4.1 测试覆盖

- 单元测试: 测试单个函数/方法
- 集成测试: 测试模块间交互
- 端到端测试: 测试完整流程

### 4.2 测试命名

```python
def test_should_return_discounted_price_when_valid_input():
    # AAA 模式
    # Arrange
    price = 100.0
    discount_rate = 0.2

    # Act
    result = calculate_discount(price, discount_rate)

    # Assert
    assert result == 80.0
```

---

## 五、文档规范

### 5.1 代码注释

```python
# 好的注释：解释为什么，而不是做什么
# 使用二分查找而非线性查找，因为列表已排序且很大
index = binary_search(sorted_list, target)
```

### 5.2 函数文档

```python
def complex_function(x: int, y: int) -> dict:
    """
    执行复杂计算

    详细描述...

    Args:
        x: 第一个参数
        y: 第二个参数

    Returns:
        包含结果的字典

    Raises:
        ValueError: 当x为负数时

    Example:
        >>> complex_function(10, 20)
        {'result': 30}
    """
    pass
```
