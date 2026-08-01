# 可组合 Prompt 家族目录

这是从公开主页中抽象出的“方法家族”目录，不是第三方账号的原始 Prompt 备份。
目录回答两个问题：一是用户说了一组关键词时应该加载哪些 Prompt 块；二是哪些变量
属于事实/主题，哪些变量属于可复用的视觉系统。

## 家族总览

| family_id | 适用任务 | 信息结构 | 主视觉机制 | 常用美学系统 | 批量策略 |
|---|---|---|---|---|---|
| morning_city | 城市早安、问候、城市系列 | 每页 1 个城市 + 3–5 个知识点 | `typographic_mask` 或 `travel_editorial_narrative` | `editorial_aesthetic` / `travel_publication` | 10 页，城市/色相/裁切变化 |
| poster_type_stage | 金句、活动宣言、人物/主题海报 | 单一钩子 + 少量署名信息 | `oversized_type` + `color_field_stage` | `bright_modern` | 单张或 4 张创意候选 |
| presentation_grid | PPT、课程、招商手册、知识卡 | 每页 3–5 个知识点，页间角色变化 | `modular_grid` + `controlled_crop` | `bright_modern` / `editorial_aesthetic` | 10 页，固定网格、页面角色变化 |
| travel_publication | 城市、旅行、带叙事的早安海报 | 主体 + 环境 + 边注 + 日期/栏目 | `travel_editorial_narrative` | `travel_publication` | 10 页，地点/色相/主体变化 |
| portrait_identity | 人像写真、家庭照、宠物、百岁照 | 主体身份 + 姿态 + 光线 + 画面用途 | `identity_lock` + `cinematic_lighting` | `portrait_editorial` / `ceremonial_soft` | 单张或 4 张姿态/场景变化 |
| event_people | 会议、展会、活动、邀请函 | 活动事实 + 人物/主体 + CTA | `poster_type_stage` 或 `modular_grid` | `bright_modern` / `ceremonial_soft` | 4 张物料或单张主海报 |
| celebration_ceremony | 生日、婚礼、婚纱、纪念 | 对象 + 日期 + 仪式情绪 + 祝福语 | `mirror_reflection`、`portrait_identity` | `ceremonial_soft` | 4 张或 10 张，角色/构图变化 |
| hospitality_food | 酒店、餐饮、饮料、菜单 | 产品/场景 + 卖点 + 价格/入口（若有事实） | `material_closeup` + `commercial_stage` | `hospitality_premium` | 单张、4 张物料或 300 套提示词批量 |
| archival_print | 古籍、票据、拓印、书法金句、历史课件 | 金句/史实 + 来源 + 注释 | `archival_collage` + `oversized_type` | `archival_historical` | 单张或 10 页课件 |
| pixel_play | 食物、产品或主题的像素解体实验 | 单一主体 + 视觉变化说明 | `pixel_dissolution` | `playful_pixel` | 4 张候选 |

## 组合规则

### 早安不是一个风格

`早安`只是 `use_case`。它可以组合成：

```text
morning_city × typographic_mask × editorial_aesthetic × series
morning_city × travel_editorial_narrative × travel_publication × series
morning_city × oversized_type × bright_modern × single
```

### PPT 不是一个风格

`presentation` 是信息任务；它至少需要选择页面结构和视觉机制：

```text
presentation × presentation_grid × bright_modern × 10-page-deck
presentation × archival_print × archival_historical × 10-page-deck
presentation × poster_type_stage × editorial_aesthetic × title-page
```

### “美学提示词”不是一个固定模板

它是美学系统的入口词。先确定色彩角色、材质、字体对比和光线，再决定是否加载
`editorial_aesthetic`、`travel_publication`、`portrait_editorial`、
`hospitality_premium` 等系统；禁止把“高级、质感、电影感”直接当作可执行规则。

## 主题佐料与固定底座

批量系列必须区分：

- **固定底座**：网格、标题尺度、边距、字体角色、光线逻辑、色彩角色和阅读顺序。
- **主题佐料**：城市、人物、产品、日期、金句、知识点、活动事实和 CTA。
- **系列变量**：主体、主色相、裁切、页面角色或局部扰动；每页最多改变 2–4 个。
- **事实边界**：来源没有给出的地标、人物身份、价格、活动信息和“今日宜忌”不得补写。

## 模型适配边界

目录中的家族和机制是模型无关的语义层。`model_adapter` 只负责把它们翻译成实际后端
可执行的 Prompt，并声明文字、参考图、批量一致性和验收能力。文本代理可以完成检索
与编译，但没有 imagegen + view_image 时，状态必须是 `BLOCKED`，不能交付“生成成功”。
