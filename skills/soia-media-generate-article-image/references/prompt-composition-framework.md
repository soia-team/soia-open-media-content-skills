# 组合式图片 Prompt 框架

本文件定义“怎么找和怎么拼 Prompt”，不是一个成品风格模板。外部帖子常用
`模型标签 x 场景 x 视觉机制 x 美学提示词` 作为检索标题；本技能把它规范化成
可复用的组合轴：

```text
交付家族 / preset
  × Prompt 家族 / family
  × 使用场景 / use_case
  × 信息结构 / information_structure
  × 参考资产角色 / asset_role
  × 视觉机制 / visual_mechanism
  × 美学系统 / aesthetic_system
  × 文字策略 / text_strategy
  × 系列策略 / batch_strategy
  × 输出形态 / output_mode
  × 模型适配 / model_adapter
  × 来源事实与逐字文字 / facts + exact_text
```

## “GPT2 x 早安 x 字体蒙版 x 美学提示词”应该怎么读

它应被解析为：

| 片段 | 在技能中的角色 | 作用 |
|---|---|---|
| GPT2 | `model_adapter` 的外部标签别名 | 表示作者以某个 GPT-image 能力测试；不是本技能依赖，也不是品牌 |
| 早安 | `use_case=good_morning`，通常落入 `family=morning_city` | 提供日期、地点、问候语、今日宜忌等事实任务 |
| 字体蒙版 | `visual_mechanism=typographic_mask` | 规定巨型字形、字腔图像、裁切和系列一致性 |
| 美学提示词 | `aesthetic_system=editorial_aesthetic` | 规定色彩角色、材质、字体角色、留白和阅读层级 |

同一个词可能只决定一个轴：例如“婚礼”是场景，“镜面”是机制，“唯美”要继续拆成
柔光、低饱和、主体高光等可执行美学角色；不能把整句话当成一个新模板名。

如果改用内置 imagegen、其他能真正出图的模型或未来 provider，核心 Prompt 仍然相同；
只替换 `model_adapter` 的可执行能力和验收规则。Claude Code、DeepCode 这类文本
代理可以编译 Prompt，但没有 imagegen + view_image 时不能冒充图片生成器。

## 编译顺序

1. **事实层**：从文章、仓库 README、重点技能 SKILL.md 或用户给出的素材提取允许使用的事实。
2. **Prompt 家族**：从家族目录选择“早安城市、演示文稿、人物写真、活动物料”等检索入口。
3. **使用场景与信息结构**：明确这张图帮助谁做什么判断，以及是单钩子、知识卡、PPT 页还是物料包。
4. **资产角色**：声明垫图、人脸/主体参考、品牌素材、截图或前景对象分别负责什么。
5. **视觉机制**：选一个主机制，例如字体蒙版、巨字留白、模块网格、旅行叙事、身份锁定或档案拼贴。
6. **美学系统**：选颜色角色、材质、字体对比、光线与空间秩序；不写空泛的“高级感”。
7. **文字策略**：决定主标题、金句、中文逐字字段和高风险文字是否需要 `hybrid_exact_text`。
8. **系列策略**：批量时锁定底座，每页只改变 2–4 个主题佐料；不要每页更换全部风格。
9. **模型适配与验收**：根据实际后端声明参考图、尺寸、文字和批量能力；生成后必须 `view_image`。

## 检索规则

- 用户说“GPT2 x …”时，先从 `prompt-composition-index.yml` 解析别名，再加载对应机制和美学词条。
- 用户说“GPT2 x 婚礼 x 请柬 x 婚纱”时，解析为 `celebration_ceremony × wedding × campaign_pack`，不是新增 wedding preset。
- 用户说“GPT2 x 票据 x 拓印 x 古籍气质”时，解析为 `archival_print × archival_collage × archival_historical`，把票据/史实事实与材质机制分开。
- 用户说“GPT2 x 人像 x 锁定五官 x 写真”时，解析为 `portrait_identity × identity_lock × portrait_editorial`，只有用户提供授权参考图时才启用 identity asset。
- 用户只说“做一张早安海报”时，不自动假定字体蒙版；根据内容和参考图推荐组合并说明假设。
- 用户说“仓库推荐、重点技能宣传卡”时，交付家族仍是 `social_skill_catalog`，再选择机制/美学层；不得用单张封面模板替代事实、工作流和 CTA。
- 用户给出多个相邻词时，合并同义词，不新增 preset；只有交付结构、事实契约或验收方式真正不同，才注册新模板。
- 找不到视觉机制或美学词条时，回退 `auto` 并写明“待补词条”，不得复制第三方原始 Prompt。

## 复用边界

可以复用：构图关系、色彩角色、信息层级、材质描述、系列变量和验收清单。

不能复用：第三方账号的原始长 Prompt、专属品牌、不可授权字体、个人素材、伪造的
事实或“某模型一定能做到”的承诺。参考帖子只用于抽象方法，不作为事实来源。
