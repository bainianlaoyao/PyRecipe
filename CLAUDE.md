# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Pythonic Recipe Framework** (菜谱框架) - a highly extensible, Python-based framework for defining cooking recipes programmatically and generating Markdown documentation. The framework uses a unique approach combining Python's dataclasses, Protocol-based interfaces, and Chinese naming conventions to create a clean, expressive DSL for recipe definitions.

**Key Design Philosophy**: All ingredients, intermediate products, and final dishes are abstracted as `食材组件` (Ingredient Component) objects. This unified abstraction enables recipe composition, nesting, and multiple output formats through pluggable processors.

**Architecture Inspiration**: Based on design1.md (Component + Factory pattern) and design2.md (Pythonic Meal class), using Python's Protocol system instead of Rust traits.

## Common Commands

### Running Examples
```bash
# Basic framework examples
python 示例/基础示例.py

# Complete recipe with Markdown generation
python 示例/完整菜谱.py

# Markdown recipe generation examples
python 示例/生成markdown菜谱.py

# Simple test scripts
python 简单测试.py
python 测试markdown生成.py
```

### Generating Recipe Documentation
```python
from 菜谱框架 import 预览菜谱, 生成菜谱文档, 生成所有菜谱

# Preview a recipe in console
预览菜谱("番茄炒蛋")

# Generate single recipe to file
生成菜谱文档("番茄炒蛋", "输出菜谱/番茄炒蛋.md")

# Generate all registered recipes
生成所有菜谱(输出目录="菜谱文档")
```

### Testing
```bash
# No pytest configuration exists - tests are run as standalone scripts
python 示例/基础示例.py  # This serves as the main test/demo
```

## High-Level Architecture

### Core Abstraction: 食材组件 (Ingredient Component)

Everything is a `食材组件` - ingredients, intermediate products, and final dishes all share the same structure:

```python
@dataclass(slots=True)
class 食材组件:
    name: str
    id: int  # Auto-incremented
    数量: Optional[数量类型] = None
    子组件: List[食材组件]
    元数据: Dict[str, Any]
    操作: Optional[烹饪操作] = None
    是否基础食材: bool = False
```

**Key Implication**: This unified abstraction enables:
- **Composition**: Recipes can contain other recipes as sub-components
- **Metadata extension**: Nutrition info, calories, etc. can be attached to any component
- **Operator overloading**: `+` for mixing, `>>` for processing, `&` for combining

### Protocol-Based Processor System

The framework uses Python's `Protocol` to define the processor interface (菜谱处理器), enabling duck-typing and multiple output formats:

**Required Methods**:
- `取食材(名称, 数量) -> 食材组件` - Declare ingredients
- `处理(组件列表, 操作, 名称, **元数据) -> 食材组件` - Process ingredients

**Built-in Processors**:
- `Markdown输出器` - Generates cooking steps (optimized for human-readability, no technical artifacts)
- `统计分析器` - Aggregates ingredient quantities
- `组合处理器` - Delegates to multiple processors simultaneously

### Framework Structure

```
菜谱框架/
├── 核心组件.py          # 食材组件, 数量类型 (克/个/片/根/毫升), 烹饪操作
├── 处理器.py            # Protocol definition + processor implementations
├── 构建器.py            # 菜谱构建器 - fluent API with operator overloading
├── 装饰器.py            # @定义菜谱 decorator, recipe registry, context manager
└── markdown生成器.py    # Markdown recipe document generator
```

### Recipe Definition Patterns

**1. Decorator Style (Recommended)**:
```python
@定义菜谱("番茄炒蛋")
def 番茄炒蛋(菜: 菜谱构建器):
    番茄 = 菜.切(菜.取食材("番茄", 个(2)), "块")
    鸡蛋 = 菜.取食材("鸡蛋", 个(3))
    炒蛋 = 菜.炒([鸡蛋], 时间_秒=30, 描述="炒", 用油=10, 名称="炒鸡蛋")
    炒番茄 = 菜.炒([番茄], 时间_秒=20, 描述="炒", 用油=5, 名称="炒番茄")
    混合 = 菜.混合([炒蛋, 炒番茄], "翻炒均匀")
    最终 = 菜.调味([混合], ["葱", "盐"], "加入盐和葱花")
    return 最终
```

**2. Context Manager Style**:
```python
with 菜谱上下文(Markdown输出器()) as 菜:
    芹菜段 = 菜.切(菜.取食材("芹菜", 根(1)), "段")
    猪肉碎 = 菜.切(菜.取食材("猪肉", 克(600)), "碎")
    肉酱 = 菜.混合([芹菜段, 猪肉碎, ...], "混合，下锅翻炒一分钟")
```

**3. Operator Overloading Style**:
```python
芹菜段 = 菜.取食材("芹菜", 根(1)) >> 切("段")
肉酱 = (芹菜段 + 猪肉碎 + 洋葱丁) >> 混合("混合")
```

### Recipe Registry and Reuse

The `@定义菜谱` decorator automatically registers recipes, enabling **recipe composition**:

```python
@定义菜谱("意大利肉酱")
def 意大利肉酱(菜: 菜谱构建器):
    # ... define sauce
    return 肉酱

@定义菜谱("意大利肉酱三明治")
def 意大利肉酱三明治(菜: 菜谱构建器):
    面包片 = 菜.取食材("面包片", 片(2))
    肉酱 = 菜.引用("意大利肉酱")  # Reuse registered recipe!
    return 菜.组合([面包片, 肉酱], "夹在一起", "意大利肉酱三明治")
```

### Markdown Output Optimization

The `Markdown输出器` has been optimized through 3 iterations to produce clean, human-readable output:

- **No component IDs**: Intermediate products don't show technical `#3` markers
- **No backticks**: Ingredient names aren't wrapped in code markers
- **Merged preparation**: "Taking ingredient" + "cutting" → single step
- **Clean intermediate names**: `番茄_切块` displays as `番茄`

Example output:
```markdown
1. 将 2个 的 番茄 切成块
2. 将 3个 的 鸡蛋 炒30秒，用10克油，炒
3. 将 炒鸡蛋, 番茄 翻炒均匀
```

## Python Features Used

- **`@dataclass(frozen=True, slots=True)`**: Immutable, memory-efficient components
- **`Protocol`**: Type-safe duck-typing for processor interface
- **Operator overloading**: `__add__` (+), `__rshift__` (>>), `__and__` (&) for intuitive syntax
- **Chinese identifiers**: All class/method names use Chinese for domain relevance
- **Decorators**: `@定义菜谱` for automatic registration and wrapped execution
- **Context managers**: `with 菜谱上下文` for scoped recipe building
- **Type annotations**: Full typing with `Optional`, `List`, `Dict`, `Protocol`

## Key Implementation Details

### Component ID Generation
Uses `itertools.count()` for auto-incrementing IDs. Call `组件ID生成器.重置()` in tests to reset state.

### Processor Delegation in 组合处理器
The first processor in the list creates the actual `食材组件` objects, ensuring consistent IDs across all processors. Other processors are notified of operations but don't create components.

### Immutable Data Pattern
Since `食材组件` is frozen, methods like `设置元数据()` and `添加子组件()` return new objects rather than modifying in place. This is intentional for safety.

### Chinese Naming Convention
The framework embraces Chinese naming for domain relevance:
- Classes: `食材组件`, `菜谱构建器`, `Markdown输出器`
- Methods: `取食材`, `切`, `混合`, `炒`, `炖`, `调味`
- Amounts: `克(500)`, `个(2)`, `片(3)`, `根(1)`, `毫升(100)`

## Extending the Framework

### Custom Processor
Implement the `菜谱处理器` Protocol:
```python
class RobotProcessor:
    def 取食材(self, 名称: str, 数量: 数量类型) -> 食材组件:
        # Generate robot command for getting ingredient
        ...
    def 处理(self, 组件: List[食材组件], 操作: 烹饪操作, 名称: str, **元数据) -> 食材组件:
        # Generate robot command for processing
        ...
```

### Custom Amount Type
```python
@dataclass(frozen=True, slots=True)
class 杯(数量类型):
    def __post_init__(self):
        object.__setattr__(self, 'unit', '杯')
```

### Custom Cooking Operation
Add new operation type to `操作类型` enum and create subclass of `烹饪操作`.

## File Reference

| File | Purpose |
|------|---------|
| [菜谱框架/核心组件.py](菜谱框架/核心组件.py) | Core abstractions: 食材组件, 数量类型, 烹饪操作 |
| [菜谱框架/处理器.py](菜谱框架/处理器.py) | Protocol definition + processor implementations |
| [菜谱框架/构建器.py](菜谱框架/构建器.py) | 菜谱构建器 fluent API |
| [菜谱框架/装饰器.py](菜谱框架/装饰器.py) | Recipe registration system, decorators |
| [菜谱框架/markdown生成器.py](菜谱框架/markdown生成器.py) | Markdown document generation |
| [示例/基础示例.py](示例/基础示例.py) | Main demo/test file showing all patterns |
| [README_框架.md](README_框架.md) | User-facing documentation |
| [python_recipe_architecture.md](python_recipe_architecture.md) | Detailed architecture explanation |
| [项目总结.md](项目总结.md) | Project completion summary |
| [design1.md](design1.md) | Original Rust-based design inspiration |
| [design2.md](design2.md) | Alternative Python design reference |
