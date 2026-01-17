> 使用配置式的描述会有大量冗余, 我在这里提议使用面向对象和函数式的结合, 来最大程度的精简菜谱的定义.
>
> 在这种方法下, 基础工作会需要一些劳力, 为了不吓到各位, 首先给出一个简单炒土豆的菜谱定义的最终结果：

我感觉您的写法还是有些许冗余部分，不过写完我的发现我的其实也一样。

单论实现，我建议把所有的菜和中间过程都抽象为 Component 对象，可以免去很多类的定义。

然后把所有的操作方法都封装进一个 Factory 类，这样如果需要扩展性，您只需实现一个满足 Factoryible Trait 的类（请允许我暂用Rust 的称呼方法），它实现了cut，mix等方法，然后做您需要的事情（如统计原料，输出md，甚至让做饭机器人执行操作）

代码有些稍长，我这里贴出来核心部分：

```rust
// 注：这个 'a 是生命周期标注，如果您没有写过 rust，可以忽略。
struct Component<'a> {
    id: i32,
    name: &'a str,
}


trait Factorible {
    fn process<'a>(
        &self,
        _cmps: Vec<Component<'a>>,
        procedure: Procedure,
        name: &'a str,
    ) -> Component<'a>;

    fn require<'a>(&self, name: &'a str, _amount: Amount) -> Component<'a> {
        Component::new(name)
    }
}


fn italian_sauce<'a>(factory: &impl Factorible) -> Component<'a> {
    factory.process(
        vec![
            factory.process(
                vec![factory.require("芹菜", Amount::Other("1根"))],
                Procedure::Cut("段"),
                "芹菜段",
            ),
            factory.process(
                vec![factory.require("猪肉", Amount::Gram(600))],
                Procedure::Cut("碎"),
                "猪肉碎",
            ),
            factory.process(
                vec![factory.require("洋葱", Amount::Number(1))],
                Procedure::Cut("碎"),
                "洋葱丁",
            ),
            factory.require("番茄酱", Amount::Gram(600))
        ],
        Procedure::Other("混合，下锅翻炒一分钟"),
        "意大利肉酱",
    )
}

fn italian_sauce_sandwich<'a>(factory: &impl Factorible) -> Component<'a> {
    factory.process(
        vec![
            factory.require("面包片", Amount::Piece(2)),
            italian_sauce(factory),
        ],
        Procedure::Other("夹在一起"),
        "意大利肉酱三明治",
    )
}

fn main() {
    italian_sauce_sandwich(&Factory);

    // italian_sauce(&Factory);
    // 这个也可以独立调用！
}
// 感谢你看到这里！无论您是否赞成，采纳我的方案，我都希望把这道菜分享给你，真的好吃！
```

输出结果是这样的（四改：不好意思，我忘了加番茄酱）：

```
取出 2片 的 `面包片 #1`
取出 1根 的 `芹菜 #2`
将 `芹菜 #2` 切成段，得到 `芹菜段 #3`
取出 600克 的 `猪肉 #4`
将 `猪肉 #4` 切成碎，得到 `猪肉碎 #5`
取出 1个 的 `洋葱 #6`
取出 100克 的 `番茄酱 #8`
将 `洋葱 #6` 切成碎，得到 `洋葱丁 #7`
将 `芹菜段 #3`, `猪肉碎 #5`, `洋葱丁 #7`, `番茄酱 #8` 混合，下锅翻炒一分钟，得到 `意大利肉酱 #9`
将 `面包片 #1`, `意大利肉酱 #9` 夹在一起，得到 `意大利肉酱三明治 #10`
```

这里我只实现了中间的做饭步骤，如果需要原材料统计，可以实现一个 SourceFactor 类，然后传入参数……
原理是类似的，把最核心的东西展现到就行了。

---

三改：我想了一下，要化简冗余的部分可以使用声明宏，rust的声明宏规则非常强大。

如 [https://docs.rs/serde_json/1.0.145/src/serde_json/macros.rs.html](https://docs.rs/serde_json/1.0.145/src/serde_json/macros.rs.html) 只通过声明宏规则实现了在编译期对 json 的解析。

再如，上面的菜谱可以变成这样：

```rust
fn italian_sauce<'a>(factory: &impl Factorible) -> Component<'a> {
    recipe! { factory,
        [
            {"芹菜": Other("1根") => Cut("段") => "芹菜段"},
            {"猪肉": Gram(600)    => Cut("碎") => "猪肉碎"},
            {"洋葱": Number(1)    => Cut("碎") => "洋葱丁"}
            {"番茄酱": Gram(100)}
        ]
        => Other("混合，下锅翻炒一分钟")
        => "意大利肉酱"
    }
}
```

这样，语言实现就可以和菜谱完全解耦。

所以问题又回到了菜谱格式上面，我们可以放下对解析器的担心而专注菜谱结构了。
