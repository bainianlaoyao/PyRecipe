使用配置式的描述会有大量冗余, 我在这里提议使用面向对象和函数式的结合, 来最大程度的精简菜谱的定义.

在这种方法下, 基础工作会需要一些劳力, 为了不吓到各位, 首先给出一个简单炒土豆的菜谱定义的最终结果

本方法下, 所有代码都可以实际运行, 并已经基本实现生成markdown功能. 我会在文末放出完整代码, 原生实现, 无外部依赖

class 炒土豆(Meal):
    def __init__(self,weight=100):
        super().__init__('炒土豆', weight)
        self.potato = 土豆(weight)
        self.require = [self.potato]
        # self.extend_submeal([self.potato])
        self.steps = [
            切块(self.potato),
            炒(蒜(3),10,5),
            炒_调料(self.potato,30,20,[盐(5),盐(3)],[10,20]) # 先炒蒜，再加入土豆和盐,
        ]
        self.auto_req()
并能根据此生成结果:

菜名: 炒土豆
工具要求
刀
锅
调料要求
油 (5g)
油 (20g)
盐 (5g)
盐 (3g)
食材要求 (每份)
土豆 (500g)
最终营养成分
淀粉: 100.0
水分: 400.0
脂肪: 25
钠: 8
合并重量
土豆: 500g
油: 25g
盐: 8g
步骤
拿出食材 土豆
将土豆切成块
将5克油放入锅中, 炒 蒜 10 秒
将20克油放入锅中, 炒 切块土豆 30 秒
在10秒时加入盐 5g
在20秒时加入盐 3g
可以看到, 我们定义了一个土豆作为原材料,. 并使用了两个步骤, 切快和炒.

实际上我做的, 就是借助python当我的AST分析器, 如果我们试图标准化的定义菜谱, 那么就一定能够将菜谱解析为AST. 因此, 借助编程语言解析AST并无不妥.
同时, 这种方法还实现了极好的封装性, 请看我自创的暗黑炖土豆:

class 黑暗炖土豆(Meal):
    def __init__(self, weight=0):
        super().__init__("黑暗炖土豆", weight)
        self.is_show_submeal = True
        self.potato = 炒土豆(weight)
        self.extend_submeal([self.potato])
        self.submeal.append(self.potato)
        self.steps = [
            # 切块([self.potato]),
            炖(self.potato,120)
        ]
        self.auto_req()
可以看到, 我使用了炒土豆作为一个前置菜品, 这非常符合菜谱中需要的各种复杂准备, 并且无须重复定义! 而且参数可调.
生成结果:

菜名: 黑暗炖土豆
工具要求
刀
锅
调料要求
油 (5g)
油 (20g)
盐 (5g)
盐 (3g)
食材要求 (每份)
土豆 (500g)
最终营养成分
淀粉: 100.0
水分: 400.0
脂肪: 25
钠: 8
合并重量
土豆: 500g
油: 25g
盐: 8g
步骤
拿出食材 土豆
将土豆切成块
将5克油放入锅中, 炒 蒜 10 秒
将20克油放入锅中, 炒 切块土豆 30 秒
在10秒时加入盐 5g
在20秒时加入盐 3g
将炒土豆放入煮开水的锅中，炖 120 秒
完整代码:

from copy import deepcopy
from functools import reduce

class Food:
    def __init__(self, name='', weight=0):
        self.require : list[Food]= [self]
        self.tool_require : list[Tool] = []
        self.spice_require : list[Food]= []
        self.name = name
        self.weight = weight
        self.method = None
        self.营养成分 = {}
    def clone(self):
        return deepcopy(self)
    def info(self):
        return f"{self.name} ({self.weight}g)"
    def generate(self) -> str:
        return f"拿出食材 {self.name}"
class 油(Food):
    def __init__(self, weight=0):
        super().__init__('油', weight)
        self.营养成分={'脂肪' : weight}
class 盐(Food):
    def __init__(self, weight=0):
        super().__init__('盐', weight)
        self.营养成分 = {'钠': weight}
class 蒜(Food):
    def __init__(self, weight=0):
        super().__init__('蒜', weight)

class Tool:
    def __init__(self):
        self.name = ''
        pass
class 刀(Tool):
    def __init__(self,name = '刀'):
        super().__init__()
        self.name = name
    pass
class 锅(Tool):
    def__init__(self,name = '锅'):
        super().__init__()
        self.name = name
        pass
class Method:
    def __init__(self):
        self.require = []
        self.spice_require = []
        self.tool_require = []
        pass
    def process(self) -> Food:
        return '无事发生'
class 切块(Method):
    def __init__(self,food : Food):
        super().__init__()
        self.tool_require = [刀()]

    self.food = food
        pass
    def process(self) -> Food:
        description= self.food.generate()
        description += f"\n将{self.food.name}切成块"
        self.food.name = f"切块{self.food.name}"
        self.food.method = self
        return description
class 炒(Method):
    def__init__(self, food : Food,time = 30,oil=2):
        super().__init__()
        self.spice_require = [油(oil)]
        self.tool_require = [锅()]
        self.time = time

    self.food = food
    def process(self) -> Food:
        description = f"将{self.spice_require[0].weight}克油放入锅中, 炒 {self.food.name} {self.time} 秒"
        self.food.name = f"炒{self.food.name}"
        self.food.method = self
        return description
class 炒_调料(炒):
    def__init__(self, food : Food,time = 30,oil=1,spice_require = [], add_time = []):
        super().__init__(food,time,oil)
        if len(spice_require) != len(add_time):
            assert "调料和时间数量不匹配"
        self.spice_require.extend(spice_require)
        self.add_time = add_time
    def process(self) -> Food:
        description = f"将{self.spice_require[0].weight}克油放入锅中, 炒 {self.food.name} {self.time} 秒"
        for i in range(len(self.add_time)):
            description = description + f'\n在{self.add_time[i]}秒时加入{self.spice_require[i+1].name} {self.spice_require[i+1].weight}g'
        self.food.name = f"炒{self.food.name}"
        self.food.method = self
        return description

class 加调料(Method):
    def __init__(self, spice : Food):
        super().__init__()
        self.spice_require = [spice]
        self.spice = spice
    def process(self) -> Food:
        description = f"加入{self.spice.name}"
        return description
class 炖(Method):
    def __init__(self, food: Food, time=30, end_result = ''):
        super().__init__()
        self.tool_require = [锅()]
        self.time = time
        self.end_result = end_result
        self.food = food
    def process(self):
        description = f"将{self.food.name}放入煮开水的锅中，炖 {self.time} 秒 "
        self.food.name = f"炖{self.food.name if not self.end_result else self.end_result}"
        return description

class 土豆(Food):
    def __init__(self, weight=0):
        super().__init__('土豆', weight)
        self.营养成分 = {
            '淀粉': 0.2 * weight,
            '水分': 0.8 * weight
        }
class Meal(Food):
    def __init__(self, name='', weight=0):
        super().__init__(name, weight)
        self.require : list[Food] = []
        self.steps : list[Method] = []
        self.submeal : list[Meal] = []
        self.is_show_submeal = True
    def generate(self,level=0) -> str:
        md = []
        # 标题
        md.append(f"#{'#'*level} 菜名: {self.name}")
        md.append(f"##{'#'*level} 工具要求")
        # 列出唯一工具
        unique_tools = []
        for tool in self.tool_require:
            if tool.name not in unique_tools:
                unique_tools.append(tool.name)
        md.append("\n".join([f"- {name}" for name in unique_tools]))
        # 调料要求
        md.append(f"##{'#'*level} 调料要求")
        md.append("\n".join([f"- {food.name} ({food.weight}g)" for food in self.spice_require]))
        # 食材要求 (每份)
        md.append(f"##{'#'*level} 食材要求 (每份)")
        md.append("\n".join([f"- {food.name} ({food.weight}g)" for food in self.require]))
        # 计算总营养成分
        total_nutrition = {}
        for item in self.require + self.spice_require:
            for key, val in item.营养成分.items():
                total_nutrition[key] = total_nutrition.get(key, 0) + val
        md.append(f"##{'#'*level} 最终营养成分")
        md.append("\n".join([f"- {k}: {v}" for k, v in total_nutrition.items()]))
        # 合并重量
        weight_summary = {}
        for item in self.require + self.spice_require:
            weight_summary[item.name] = weight_summary.get(item.name, 0) + item.weight
        md.append(f"##{'#'*level} 合并重量")
        md.append("\n".join([f"- {name}: {weight}g" for name, weight in weight_summary.items()]))
        # 步骤
        md.append(f"##{'#'*level} 步骤")
        steps_md = []

    if self.is_show_submeal:
            for meal in self.submeal:
                for step in meal.steps:
                    steps_md.append(f"- {step.process()}")

    # 各个处理步骤
        for step in self.steps:
            steps_md.append(f"- {step.process()}")
        md.append("\n".join(steps_md))
        return "\n\n".join(md)
    def auto_req(self):
        for step in self.steps:
            self.tool_require.extend(step.tool_require)
            self.spice_require.extend(step.spice_require)
    def extend_submeal(self, food_lsit: list[Food]):
        for food in food_lsit:
            self.require.extend(food.require)
            self.tool_require.extend(food.tool_require)
            self.spice_require.extend(food.spice_require)
            self.营养成分 = reduce(lambda x, y: {k: x.get(k, 0) + y.get(k, 0) for k in set(x) | set(y)}, [self.营养成分] + [food.营养成分 for food in food_lsit])

class 炒土豆(Meal):
    def __init__(self,weight=100):
        super().__init__('炒土豆', weight)
        self.potato = 土豆(weight)
        self.require = [self.potato]
        # self.extend_submeal([self.potato])
        self.steps = [
            切块(self.potato),
            炒(蒜(3),10,5),
            炒_调料(self.potato,30,20,[盐(5),盐(3)],[10,20]) # 先炒蒜，再加入土豆和盐,
        ]
        self.auto_req()

class 黑暗炖土豆(Meal):
    def __init__(self, weight=0):
        super().__init__("黑暗炖土豆", weight)
        self.is_show_submeal = True
        self.potato = 炒土豆(weight)
        self.extend_submeal([self.potato])
        self.submeal.append(self.potato)
        self.steps = [
            # 切块([self.potato]),
            炖(self.potato,120)
        ]
        self.auto_req()
if __name__ == '__main__':
    # meal = 炒土豆( 500)
    meal = 黑暗炖土豆( 500)
    print(meal.generate())
    # print(meal.potato.export())
    # print(meal.potato.营养成分)  # 输出营养成分
