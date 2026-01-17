"""
核心组件 - 食材组件、数量类型、烹饪操作
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional, List, Dict
from enum import Enum
import itertools


# ============================================================================
# 数量类型体系 (Amount)
# ============================================================================

@dataclass(frozen=True, slots=True)
class 数量类型:
    """数量基类"""
    value: float | str
    unit: str = ""

    def __str__(self) -> str:
        if isinstance(self.value, str):
            return self.value
        return f"{self.value}{self.unit}"

    def __add__(self, other: 数量类型) -> 数量类型:
        """数量相加"""
        if not isinstance(other, 数量类型):
            raise TypeError(f"不能将 数量类型 与 {type(other)} 相加")
        if self.unit != other.unit:
            raise ValueError(f"单位不匹配: {self.unit} vs {other.unit}")
        return type(self)(self.value + other.value)

    def __mul__(self, factor: float) -> 数量类型:
        """数量乘以因子"""
        return type(self)(self.value * factor)


@dataclass(frozen=True, slots=True)
class 克(数量类型):
    """克 - 质量单位"""
    def __post_init__(self):
        object.__setattr__(self, 'unit', '克')


@dataclass(frozen=True, slots=True)
class 个(数量类型):
    """个 - 计数单位"""
    def __post_init__(self):
        object.__setattr__(self, 'unit', '个')


@dataclass(frozen=True, slots=True)
class 片(数量类型):
    """片 - 切片单位"""
    def __post_init__(self):
        object.__setattr__(self, 'unit', '片')


@dataclass(frozen=True, slots=True)
class 根(数量类型):
    """根 - 条状单位"""
    def __post_init__(self):
        object.__setattr__(self, 'unit', '根')


@dataclass(frozen=True, slots=True)
class 毫升(数量类型):
    """毫升 - 液体单位"""
    def __post_init__(self):
        object.__setattr__(self, 'unit', '毫升')


@dataclass(frozen=True, slots=True)
class 自定义单位(数量类型):
    """自定义描述性数量"""
    pass


# ============================================================================
# 烹饪操作体系 (Cooking Operations)
# ============================================================================

class 操作类型(Enum):
    """操作类型枚举"""
    切 = "cut"
    混合 = "mix"
    煎炒 = "fry"
    炖煮 = "stew"
    调味 = "season"
    其他 = "other"


@dataclass(slots=True)
class 烹饪操作:
    """烹饪操作基类"""
    类型: str
    描述: str
    参数: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return self.描述

    @classmethod
    def 其他(cls, 描述: str, **参数) -> "烹饪操作":
        """创建自定义操作"""
        return cls("other", 描述, 参数)


@dataclass(slots=True)
class 切制(烹饪操作):
    """切割操作"""

    @classmethod
    def 切(cls, 方式: str) -> "切制":
        """创建切割操作"""
        return cls("cut", f"切成{方式}", {"方式": 方式})


@dataclass(slots=True)
class 混合操作(烹饪操作):
    """混合操作"""

    @classmethod
    def 混合(cls, 描述: str) -> "混合操作":
        """创建混合操作"""
        return cls("mix", 描述, {"描述": 描述})


@dataclass(slots=True)
class 煎炒(烹饪操作):
    """煎炒操作"""

    @classmethod
    def 炒(cls, 时间_秒: int, 描述: str = "") -> "煎炒":
        """创建炒操作"""
        desc = f"炒{时间_秒}秒" + (f"，{描述}" if 描述 else "")
        return cls("fry", desc, {"时间": 时间_秒, "描述": 描述})


@dataclass(slots=True)
class 炖煮(烹饪操作):
    """炖煮操作"""

    @classmethod
    def 炖(cls, 时间_秒: int, 描述: str = "") -> "炖煮":
        """创建炖操作"""
        desc = f"炖{时间_秒}秒" + (f"，{描述}" if 描述 else "")
        return cls("stew", desc, {"时间": 时间_秒, "描述": 描述})


@dataclass(slots=True)
class 调味(烹饪操作):
    """调味操作"""

    @classmethod
    def 加调料(cls, 调料列表: List[str]) -> "调味":
        """创建调味操作"""
        desc = f"加入{', '.join(调料列表)}"
        return cls("season", desc, {"调料": 调料列表})


# ============================================================================
# 食材组件 (Ingredient Component)
# ============================================================================

class 组件ID生成器:
    """组件ID生成器"""
    _计数器 = itertools.count(1)

    @classmethod
    def 下一ID(cls) -> int:
        """获取下一个ID"""
        return next(cls._计数器)

    @classmethod
    def 重置(cls):
        """重置计数器（主要用于测试）"""
        cls._计数器 = itertools.count(1)


@dataclass(slots=True)
class 食材组件:
    """
    食材组件 - 所有食材、中间产物、最终菜品的统一抽象

    特性:
    - 不可变: 使用frozen=True防止意外修改
    - 内存高效: 使用slots减少内存占用
    - 支持嵌套: 通过子组件实现组合模式
    - 元数据扩展: 可携带营养、热量等信息
    """
    name: str
    id: int = field(default_factory=组件ID生成器.下一ID)
    数量: Optional[数量类型] = None
    子组件: List[食材组件] = field(default_factory=list)
    元数据: Dict[str, Any] = field(default_factory=dict)
    操作: Optional[烹饪操作] = None
    是否基础食材: bool = False

    def __str__(self) -> str:
        """格式化显示"""
        if self.数量:
            return f"`{self.name} #{self.id}` ({self.数量})"
        return f"`{self.name} #{self.id}`"

    def __repr__(self) -> str:
        return f"食材组件(name={self.name!r}, id={self.id}, 子组件数={len(self.子组件)})"

    def __add__(self, other: 食材组件) -> 食材组件:
        """
        + 操作符: 表示混合多个组件
        返回一个新的组件，包含两个子组件
        """
        if not isinstance(other, 食材组件):
            raise TypeError(f"不能将 食材组件 与 {type(other)} 相加")

        # 创建一个临时组件用于表示混合
        return 食材组件(
            name=f"{self.name}+{other.name}",
            子组件=[self, other],
            操作=混合操作.混合("混合")
        )

    def __rshift__(self, 操作: 烹饪操作) -> 食材组件:
        """
        >> 操作符: 表示对组件执行操作
        返回一个新的组件，表示操作后的结果
        """
        if not isinstance(操作, 烹饪操作):
            raise TypeError(f">> 操作符右侧需要 烹饪操作，实际得到 {type(操作)}")

        return 食材组件(
            name=f"{self.name}_处理后",
            子组件=[self],
            操作=操作
        )

    def __and__(self, other: 食材组件) -> 食材组件:
        """
        & 操作符: 表示组合/夹在一起
        """
        if not isinstance(other, 食材组件):
            raise TypeError(f"& 操作符右侧需要 食材组件，实际得到 {type(操作)}")

        return 食材组件(
            name=f"{self.name}&{other.name}",
            子组件=[self, other],
            操作=烹饪操作.其他("组合在一起")
        )

    def 添加子组件(self, 组件: 食材组件) -> "食材组件":
        """添加子组件（注意：返回新对象因为frozen）"""
        if self.是否基础食材:
            raise ValueError("基础食材不能添加子组件")
        新组件 = 食材组件(
            name=self.name,
            数量=self.数量,
            子组件=self.子组件 + [组件],
            元数据=dict(self.元数据),
            操作=self.操作,
            是否基础食材=self.是否基础食材
        )
        return 新组件

    def 设置元数据(self, 键: str, 值: Any) -> "食材组件":
        """设置元数据（注意：返回新对象因为frozen）"""
        新元数据 = dict(self.元数据)
        新元数据[键] = 值
        新组件 = 食材组件(
            name=self.name,
            数量=self.数量,
            子组件=list(self.子组件),
            元数据=新元数据,
            操作=self.操作,
            是否基础食材=self.是否基础食材
        )
        return 新组件

    def 克隆(self, 新名称: Optional[str] = None) -> "食材组件":
        """克隆组件"""
        import copy
        克隆后的 = copy.deepcopy(self)
        if 新名称:
            # 由于frozen，需要创建新对象
            克隆后的 = 食材组件(
                name=新名称,
                数量=克隆后的.数量,
                子组件=克隆后的.子组件,
                元数据=dict(克隆后的.元数据),
                操作=克隆后的.操作,
                是否基础食材=克隆后的.是否基础食材
            )
        return 克隆后的

    def 获取所有基础食材(self) -> List[食材组件]:
        """递归获取所有基础食材"""
        if self.是否基础食材:
            return [self]
        结果 = []
        for 子 in self.子组件:
            结果.extend(子.获取所有基础食材())
        return 结果

    def 获取总数量(self, 名称: str) -> Optional[数量类型]:
        """获取指定名称食材的总数量"""
        总数量 = 0
        单位 = None
        for 食材 in self.获取所有基础食材():
            if 食材.name == 名称 and 食材.数量:
                if isinstance(食材.数量.value, (int, float)):
                    总数量 += 食材.数量.value
                    单位 = 食材.数量.unit

        if 单位:
            # 根据单位创建相应的数量类型
            单位映射 = {
                "克": 克,
                "个": 个,
                "片": 片,
                "根": 根,
                "毫升": 毫升,
            }
            类型 = 单位映射.get(单位, 自定义单位)
            return 类型(总数量)
        return None


# 便利函数
def 切(方式: str) -> 切制:
    """创建切割操作"""
    return 切制.切(方式)


def 混合(描述: str) -> 混合操作:
    """创建混合操作"""
    return 混合操作.混合(描述)


def 炒(时间_秒: int, 描述: str = "") -> 煎炒:
    """创建炒操作"""
    return 煎炒.炒(时间_秒, 描述)


def 炖(时间_秒: int, 描述: str = "") -> 炖煮:
    """创建炖操作"""
    return 炖煮.炖(时间_秒, 描述)
