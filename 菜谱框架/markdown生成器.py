"""
Markdown菜谱生成器 - 将程序定义的菜谱转换为Markdown格式的菜谱文档
"""

from __future__ import annotations
from typing import Dict, List, Optional
from pathlib import Path

from .处理器 import Markdown输出器, 统计分析器, 组合处理器
from .装饰器 import 菜谱注册表, 执行菜谱
from .核心组件 import 食材组件


# ============================================================================
# Markdown菜谱文档生成器
# ============================================================================

class Markdown菜谱生成器:
    """
    Markdown菜谱文档生成器

    将程序定义的菜谱转换为结构化的Markdown菜谱文档
    """

    def __init__(self):
        self.菜谱信息缓存: Dict[str, Dict] = {}

    def 生成菜谱文档(
        self,
        菜谱名称: str,
        包含统计: bool = True,
        包含营养: bool = False
    ) -> str:
        """
        生成完整的Markdown菜谱文档

        参数:
            菜谱名称: 菜谱名称
            包含统计: 是否包含食材统计
            包含营养: 是否包含营养信息（暂未实现）

        返回:
            Markdown格式的菜谱文档
        """
        # 创建组合处理器
        处理器列表 = [Markdown输出器()]
        if 包含统计:
            处理器列表.append(统计分析器())

        组合 = 组合处理器(处理器列表)

        # 执行菜谱
        菜谱组件 = 执行菜谱(菜谱名称, 组合)

        # 获取操作步骤
        markdown_处理器 = 组合.获取子处理器(0)
        步骤列表 = markdown_处理器.获取操作() if markdown_处理器 else []

        # 获取统计信息
        食材统计 = {}
        if 包含统计 and len(处理器列表) > 1:
            stats_处理器 = 组合.获取子处理器(1)
            if stats_处理器:
                食材统计 = stats_处理器.获取统计()

        # 生成Markdown文档
        文档 = self._格式化菜谱文档(
            菜谱名称,
            步骤列表,
            食材统计 if 包含统计 else None,
            菜谱组件
        )

        return 文档

    def _格式化菜谱文档(
        self,
        菜谱名称: str,
        步骤列表: List[str],
        食材统计: Optional[Dict] = None,
        菜谱组件: Optional[食材组件] = None
    ) -> str:
        """
        格式化为Markdown文档
        """
        行列表 = []

        # 标题
        行列表.append(f"# {菜谱名称}")
        行列表.append("")

        # 食材清单
        if 食材统计:
            行列表.append("## 食材清单")
            行列表.append("")
            for 名称, 数量字典 in 食材统计.items():
                数量字符串 = " + ".join([f"{值}{键}" for 键, 值 in 数量字典.items()])
                行列表.append(f"- **{名称}**: {数量字符串}")
            行列表.append("")

        # 烹饪步骤
        行列表.append("## 烹饪步骤")
        行列表.append("")

        # 编号步骤
        for 索引, 步骤 in enumerate(步骤列表, 1):
            if 步骤.strip():  # 只添加非空步骤
                行列表.append(f"{索引}. {步骤}")

        行列表.append("")

        # 分隔线
        行列表.append("---")
        行列表.append("")

        # 备注
        行列表.append("## 备注")
        行列表.append("")
        行列表.append("- 本菜谱由Pythonic菜谱框架自动生成")
        行列表.append("")

        return "\n".join(行列表)

    def 批量生成菜谱文档(
        self,
        菜谱名称列表: List[str],
        输出目录: str = ".",
        单文件: bool = False
    ) -> None:
        """
        批量生成菜谱文档

        参数:
            菜谱名称列表: 要生成的菜谱名称列表
            输出目录: 输出目录路径
            单文件: 是否合并到单个文件
        """
        if 单文件:
            # 合并到单个文件
            所有内容 = []
            所有内容.append("# 菜谱集合")
            所有内容.append("")
            所有内容.append("本文件包含多个菜谱")
            所有内容.append("")

            for 菜谱名称 in 菜谱名称列表:
                try:
                    文档 = self.生成菜谱文档(菜谱名称)
                    所有内容.append(文档)
                    所有内容.append("")
                except ValueError as e:
                    print(f"警告: {e}")
                    continue

            # 写入文件
            输出路径 = Path(输出目录) / "菜谱集合.md"
            输出路径.write_text("\n".join(所有内容), encoding="utf-8")
            print(f"已生成: {输出路径}")

        else:
            # 每个菜谱单独文件
            输出路径 = Path(输出目录)
            输出路径.mkdir(parents=True, exist_ok=True)

            for 菜谱名称 in 菜谱名称列表:
                try:
                    文档 = self.生成菜谱文档(菜谱名称)

                    # 清理文件名（移除不合法字符）
                    文件名 = "".join(c for c in 菜谱名称 if c.isalnum() or c in (' ', '-', '_'))
                    文件名 = 文件名.strip().replace(' ', '_')
                    文件路径 = 输出路径 / f"{文件名}.md"

                    文件路径.write_text(文档, encoding="utf-8")
                    print(f"已生成: {文件路径}")

                except ValueError as e:
                    print(f"警告: {e}")
                    continue

    def 列出所有菜谱(self) -> List[str]:
        """
        列出所有已注册的菜谱
        """
        return 菜谱注册表.列出()


# ============================================================================
# 便利函数
# ============================================================================

def 生成菜谱文档(
    菜谱名称: str,
    输出文件: Optional[str] = None,
    包含统计: bool = True
) -> str:
    """
    生成单个菜谱的Markdown文档

    参数:
        菜谱名称: 菜谱名称
        输出文件: 输出文件路径（可选）
        包含统计: 是否包含食材统计

    返回:
        Markdown文档内容
    """
    生成器 = Markdown菜谱生成器()
    文档 = 生成器.生成菜谱文档(菜谱名称, 包含统计=包含统计)

    if 输出文件:
        输出路径 = Path(输出文件)
        # 确保目录存在
        输出路径.parent.mkdir(parents=True, exist_ok=True)
        输出路径.write_text(文档, encoding="utf-8")
        print(f"已生成菜谱文档: {输出文件}")

    return 文档


def 生成所有菜谱(
    输出目录: str = "菜谱文档",
    单文件: bool = False
) -> None:
    """
    生成所有已注册菜谱的文档

    参数:
        输出目录: 输出目录
        单文件: 是否合并到单个文件
    """
    生成器 = Markdown菜谱生成器()
    菜谱列表 = 生成器.列出所有菜谱()

    if not 菜谱列表:
        print("没有找到已注册的菜谱")
        return

    print(f"找到 {len(菜谱列表)} 个菜谱:")
    for 菜谱 in 菜谱列表:
        print(f"  - {菜谱}")

    生成器.批量生成菜谱文档(菜谱列表, 输出目录, 单文件)


def 预览菜谱(菜谱名称: str, 包含统计: bool = True) -> None:
    """
    在控制台预览菜谱

    参数:
        菜谱名称: 菜谱名称
        包含统计: 是否包含统计信息
    """
    文档 = 生成菜谱文档(菜谱名称, 包含统计=包含统计)
    print("\n" + "=" * 60)
    print("菜谱预览")
    print("=" * 60 + "\n")
    print(文档)
