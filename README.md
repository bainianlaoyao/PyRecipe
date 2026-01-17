# 菜谱架构设计

基于Python的菜谱架构,结合design1的Component抽象和design2的Pythonic风格,提供了一个灵活、可扩展的菜谱定义框架。

## 设计理念

### 1. 核心抽象 - Component

所有食材、中间产物、最终菜品都抽象为`Component`对象,这是整个架构的核心概念。

```python
@dataclass
class Component:
    name: str                          # 名称
    id: int                            # 唯一标识符
    amount: Optional[Amount] = None   # 数量
    ingredients: List[Component]       # 包含的子Component
    metadata: Dict[str, Any]           # 元数据(营养成分等)
    procedure: Optional[Procedure]     # 操作过程
    is_ingredient: bool                # 是否为原始食材
```

**优势**:
- 统一的抽象,简化了菜谱定义
- 支持嵌套和组合
- 可以携带任意元数据(营养成分、热量等)

### 2. 工厂模式 - RecipeProcessor

参考design1的Factorible trait,使用Python的Protocol定义处理器接口:

```python
class RecipeProcessor(Protocol):
    def require(self, name: str, amount: Amount) -> Component:
        """声明需要的食材"""
        ...

    def process(
        self,
        components: List[Component],
        procedure: Procedure,
        name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Component:
        """处理食材"""
        ...
```

**优势**:
- 通过Protocol实现鸭子类型
- 可以轻松实现不同的处理器
- 支持多种输出格式(Markdown、统计、机器人指令等)

### 3. Pythonic特性

充分利用Python的特性:

- **dataclass**: 简化类定义
- **Protocol**: 实现接口约束
- **typing**: 完整的类型注解
- **Enum**: 枚举操作类型
- **链式调用**: 优雅的API设计
- **类型安全**: 编译期类型检查

## 核心组件

### Amount - 数量表示

```python
# 支持多种单位
Gram(600)      # 600克
Number(1)      # 1个
Piece(2)       # 2片
Root(1)        # 1根
Other("1根")   # 其他描述
```

### Procedure - 操作过程

```python
# 内置操作
Procedure.cut("段")          # 切成段
Procedure.cut("碎")          # 切成碎
Procedure.mix("混合")        # 混合
Procedure.fry(60, "中火")    # 炒60秒
Procedure.stew(120)          # 炖120秒

# 自定义操作
Procedure.other("夹在一起")
```

### 处理器实现

#### MarkdownProcessor - Markdown输出

```python
processor = MarkdownProcessor()
result = italian_sauce_sandwich(processor)

for op in processor.get_operations():
    print(op)
```

**输出示例**:
```
取出 2片 的 `面包片 #1`
取出 1根 的 `芹菜 #2`
将 `芹菜 #2` 切成段，得到 `芹菜段 #3`
...
将 `面包片 #1`, `意大利肉酱 #9` 夹在一起，得到 `意大利肉酱三明治 #10`
```

#### StatisticsProcessor - 统计信息

```python
processor = StatisticsProcessor()
italian_sauce_sandwich(processor)
processor.print_statistics()
```

**输出示例**:
```
=== 食材统计 ===
- 面包片: 2片
- 芹菜:
- 猪肉: 600克
- 洋葱: 1个
- 番茄酱: 100克
```

#### CompositeProcessor - 组合处理器

同时使用多个处理器:

```python
markdown_proc = MarkdownProcessor()
stats_proc = StatisticsProcessor()
composite = CompositeProcessor([markdown_proc, stats_proc])
italian_sauce_sandwich(composite)
```

## 使用示例

### 1. 函数式定义风格

参考design1的简洁风格:

```python
def italian_sauce(factory: RecipeProcessor) -> Component:
    return factory.process(
        [
            factory.process(
                [factory.require("芹菜", Other("1根"))],
                Procedure.cut("段"),
                "芹菜段"
            ),
            factory.process(
                [factory.require("猪肉", Gram(600))],
                Procedure.cut("碎"),
                "猪肉碎"
            ),
            factory.process(
                [factory.require("洋葱", Number(1))],
                Procedure.cut("碎"),
                "洋葱丁"
            ),
            factory.require("番茄酱", Gram(100))
        ],
        Procedure.mix("混合，下锅翻炒一分钟"),
        "意大利肉酱"
    )

def italian_sauce_sandwich(factory: RecipeProcessor) -> Component:
    return factory.process(
        [
            factory.require("面包片", Piece(2)),
            italian_sauce(factory),  # 复用子菜谱!
        ],
        Procedure.other("夹在一起"),
        "意大利肉酱三明治"
    )
```

### 2. 链式调用风格

使用RecipeBuilder提供更简洁的API:

```python
builder = RecipeBuilder(MarkdownProcessor())

# 准备食材
bread = builder.require("面包片", Piece(2))
celery = builder.require("芹菜", Other("1根"))
pork = builder.require("猪肉", Gram(600))
onion = builder.require("洋葱", Number(1))
sauce = builder.require("番茄酱", Gram(100))

# 处理食材
celery_cut = builder.cut(celery, "段", "芹菜段")
pork_cut = builder.cut(pork, "碎", "猪肉碎")
onion_cut = builder.cut(onion, "碎", "洋葱丁")

# 混合
meat_sauce = builder.mix(
    [celery_cut, pork_cut, onion_cut, sauce],
    "混合，下锅翻炒一分钟",
    "意大利肉酱"
)

# 最终菜品
sandwich = builder.custom(
    [bread, meat_sauce],
    "夹在一起",
    "意大利肉酱三明治"
)
```

## 扩展性

### 自定义处理器

实现RecipeProcessor接口即可:

```python
class RobotProcessor:
    """机器人执行处理器"""
    def __init__(self):
        self.commands = []

    def require(self, name: str, amount: Amount) -> Component:
        self.commands.append(f"ARM_GET({name}, {amount})")
        return Component(name=name, amount=amount)

    def process(
        self,
        components: List[Component],
        procedure: Procedure,
        name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Component:
        cmd = f"ARM_PROCESS({procedure.type}, {[c.name for c in components]})"
        self.commands.append(cmd)
        return Component(name=name, ingredients=components, procedure=procedure)
```

### 自定义Amount类型

```python
@dataclass(frozen=True)
class Cup(Amount):
    """杯"""
    def __post_init__(self):
        object.__setattr__(self, 'unit', '杯')
```

### 自定义Procedure

```python
@classmethod
def bake(cls, temperature: int, time: int) -> "Procedure":
    desc = f"在{temperature}°C下烤{time}分钟"
    return cls("bake", desc, {"temperature": temperature, "time": time})
```

## 架构优势

### 1. 与design1对比

| 特性 | design1 (Rust) | 本架构 (Python) |
|------|---------------|-----------------|
| 抽象 | Component + Trait | Component + Protocol |
| 类型系统 | 严格静态 | 动态 + 类型注解 |
| 元编程 | 宏 | 内省 + dataclass |
| 学习曲线 | 较高 | 较低 |

### 2. 与design2对比

| 特性 | design2 | 本架构 |
|------|---------|---------|
| 抽象 | Food + Meal | 统一的Component |
| 扩展性 | 继承 | Protocol + 组合 |
| 复用性 | 子Meal | 函数式组件 |
| 输出格式 | Markdown | 可扩展(多种处理器) |

### 3. 核心优势

- **统一抽象**: 一切皆Component
- **高度可扩展**: 通过Protocol实现处理器
- **强类型**: 完整的类型注解,支持IDE智能提示
- **简洁**: 函数式风格,最小化冗余
- **复用性**: 菜谱可以作为组件被其他菜谱引用
- **Pythonic**: 充分利用Python特性

## 运行示例

```bash
python recipe_architecture.py
```

输出包括:
- Markdown格式的烹饪步骤
- 食材统计信息
- 链式调用示例

## 未来扩展

1. **营养成分计算**: 在metadata中存储营养成分,自动计算
2. **菜谱验证**: 检查食材是否可用,操作是否合理
3. **可视化**: 生成菜谱流程图
4. **时间优化**: 并行执行可独立的操作
5. **数据库持久化**: 保存和加载菜谱

## 总结

本架构融合了design1的Component抽象和函数式风格,以及design2的Pythonic特性,提供了一个:
- **简洁**: 菜谱定义清晰,无冗余
- **灵活**: 支持多种处理器和输出格式
- **可扩展**: 易于添加新功能和自定义
- **类型安全**: 完整的类型注解
- **Pythonic**: 充分利用Python特性

的菜谱定义框架。
