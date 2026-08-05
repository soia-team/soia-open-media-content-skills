---
name: soia-media-generate-article-image
description: 将文章、开源项目、品牌 Logo 或公开 X Prompt Deck 编译为可验收的图片与矢量资产，按组合轴生成 Prompt 并完成事实、文字和视觉验收。
version: 3.16.1
created_at: 2026-07-09 20:56:44
updated_at: 2026-08-05 13:00:00
created_by: claude opus 4.6
updated_by: claude-opus-5
---

# soia-media-generate-article-image

生成真实 PNG/JPG，并为每次生成保存可复用 Prompt、来源边界、manifest 和验收结果。本技能不负责文章排版、平台发布、账号登录或凭空补写事实。

## 客户可读说明

### 这个技能可以做什么

支持六类交付：文章封面/小结卡、康奈尔笔记、视觉隐喻海报、技能库宣传单图/轮播、插件图标、品牌 Logo 系统。客户只需提供来源、用途、平台、比例和必须逐字出现的文字；有参考图时说明它是风格参考、构图参考还是编辑目标。

### 客户如何使用

1. 先明确 `image_type`、用途和输出形态；省略的组合轴由 Agent 给出假设。
2. 请求含糊时先展示 L0 支持目录，让客户选择 `preset` 或 `family`；不得静默套用早安、字体蒙版或某个美学 preset。
3. 选定后只加载命中的 references，编译完整 Prompt，调用 imagegen，执行 `view_image` 和对应质量门。

### 需求不明确时：先反问，不生成

当客户只说“做张好看的图”“帮我配个海报”或没有给出用途/输出形态时，先运行 L0 目录命令，再用下面的最小问题澄清；不要猜 preset，也不要先生成样图：

```text
我先确认一下需求。我们目前支持：
1. 文章封面 / 研究小结卡
2. 康奈尔笔记信息图
3. 视觉隐喻海报
4. 技能库宣传单图 / 小红书轮播
5. 插件或应用图标
6. 品牌 Logo 系统（图形标、字标、组合和变体）
7. 公开 X Prompt Deck → image 技能进化导入

请回复：
- 用途：封面、小结、笔记、海报、宣传卡、轮播、插件图标还是品牌 Logo？
- 来源：文章/仓库/X Prompt Deck，还是只给一个主题？
- 风格：从支持目录选一个 family，或描述你想要的视觉感觉？
- 版式：比例、平台、张数；有没有必须逐字出现的标题、数字、URL、字标或 Logo？
```

客户只回答部分问题时，只追问缺失且会改变路由的字段；比例、文字策略等次级轴由 Agent 给出一个可确认的默认值。客户明确说“直接生成”且用途、来源和输出形态已经足够确定时，才可跳过这段反问。

### 依赖与安装

`imagegen` 路径需要可调用的 imagegen 和 `view_image`；`html_render` 路径只需 Node.js + puppeteer，不依赖 imagegen。插件安装、配置文件和 provider 登录态按宿主文档处理，本技能不保存 API key、cookie 或 token。

## 渐进式选择与加载（必须遵守）

装整个域：`claude plugin install soia-media-content@soia`（先 `claude plugin marketplace add soia-team/soia-open-skills`）；只装本技能：`npx skills add soia-team/soia-open-media-content-skills -g -a '*' -s soia-media-generate-article-image -y`。**WorkBuddy** 是角色化专家，`npx -a '*'` 覆盖不到，见 [docs/install/workbuddy.md](https://github.com/soia-team/soia-open-skills/blob/main/docs/install/workbuddy.md)。

### L0：支持目录

首次请求只读取 `template-registry.yml` 与 `prompt-composition-index.yml` 的 `support_catalog`。当前目录包含 7 个交付模板、11 个 Prompt 家族、4 个 Logo 变体和 1 条外部提示词进化导入路线。

```bash
python3 scripts/resolve_prompt_composition.py --list-supported
```

向客户展示数量、模板、家族摘要和外部路线；客户没有选定用途/输出形态/家族前，不加载全部长 Prompt。

### L1：选择家族

确认 `family`、用途、信息结构和输出形态。例如 `presentation_grid + deck_series + 16:9`、`celebration_ceremony + campaign_pack`，或 `brand_identity + logo_system + 1:1`。

### L2：组合轴

只加载一个 `family`、`information_structure`、`visual_mechanism`、`aesthetic_system`、`text_strategy` 和 `model_adapter` 的对应词条，以及 [家族目录](references/prompt-family-catalog.md)；再读取 [组合块执行契约](references/prompt-block-contract.yml)。缺失轴给出一个可确认的默认值，不把形容词当成已编译 Prompt。

### L3：生成与验收

读取所选模板、来源事实和质量门，落盘七个 canonical blocks 后调用 imagegen；实际打开位图、核对文字/比例/事实，失败则用新版本重生。

### 康奈尔多页决策

- 选择 `cornell_notes` 后默认运行 `scripts/resolve_cornell_pagination.py`，锁定 `density_profile=dense_cornell_v1`；客户给了已认可成品时标记 `style_density_reference`，只替换事实与页变量。
- `page_count` 只能是 1–6；≤10 个完整模块默认保持一张高密度母版，系列页目标 6–10 个问题—笔记模块，内容不足就合并，不用虚构信息填页。
- 生成前在 Prompt/manifest 记录 `density_audit`（cue/module 数、页角色、页码）；多页写入统一 `series_id`，左上角安全区使用统一的紧凑页码徽章显示 `NN/TT`。参考图中的红圈、红框或手写数字只当用户批注，不得复制进成品。
- 按知识单元拆分，不机械截断；所有页共享康奈尔视觉底座，最后一页承担总结/一句话记忆。
- manifest 必须记录系列和逐页状态；每页都要 `view_image`，密度、页码、文字、来源或比例任一失败，系列不能通过。

## 路由索引

- 普通文章图：读取 [输入契约](references/input-contract.md)、[模板注册表](references/template-registry.yml) 和 [组合索引](references/prompt-composition-index.yml)。
- 研究封面/小结：`editorial_research_minimal`；正文小结：`editorial_summary_card`；康奈尔笔记：`cornell_notes`（长文使用 `adaptive_series`，最多 6 页）。
- 交付选择支持 `social_card | carousel | icon | logo`；社交图使用 `social_skill_catalog`，插件图标使用 `plugin_icon`，品牌 Logo 使用 `brand_logo`。朋友圈单图或小红书轮播的事实和两阶段规则见 [社交卡契约](references/social-card-contract.yml)。
- 研究封面使用 `editorial_research_minimal`；插件图标和品牌 Logo 的 imagegen 只给方向稿，终稿必须确定性矢量重绘。品牌 Logo 额外读取 [Logo 系统 Prompt](references/prompt-brand-logo.md)。
- X profile 导入：`source=x-profile-export` 时，先读取 [X 导入契约](references/prompt-x-profile-import.md) 和 [X 提示词进化契约](references/x-profile-prompt-evolution.yml)，运行：

```bash
python3 scripts/import_x_profile_prompt_deck.py \
  --input <x-profile-run>/image-prompts.yml \
  --output <image-output>/x-profile-evolution
```

需要盘点与当前能力的差距时，再运行：

```bash
python3 scripts/audit_x_profile_prompt_deck.py \
  --input <x-profile-run>/image-prompts.yml \
  --output <image-output>/gap-report.md
```

该步骤不是复制 Prompt：它会核对 run `manifest.yml`、窗口/筛选条件、状态 ID、来源证据和 canonical blocks，再拆出 `base_visual_system`、`topic_seasoning`、`series_variables`、`render_plan`。GPT2 只保留为来源模型标签，不成为 image 技能依赖。

## 输入与 Prompt 编译

完整字段见 [输入契约](references/input-contract.md)。最小输入必须包括 `source`、`image_type`、`preset/family`、用途、比例、输出目录和逐字文字；Logo 还必须提供品牌名称、图形概念、字标策略、颜色变体和矢量终稿要求；X 导入还必须保留 source URL、status ID、selection filters、source_prompt 和七个 blocks。

每次生成按以下顺序落盘，不从案例库整段复制：

1. `composition_axes`：记录交付模板、家族、信息结构、视觉机制、美学系统、文字策略、模型适配、批次策略及系列页字段。
2. `source_grounding`：允许进入图片的事实、禁止补写的字段和缺失信息。
3. `primary_task`：一个主要视觉任务，不把封面、小结和信息图混成一张。
4. `composition_and_layout`、`visual_style_and_materials`：主体、空间、阅读顺序、材质、光线和颜色角色。
5. `exact_text`、`aspect_and_output`、`constraints_and_avoid`：逐字文字、比例/格式和可验证禁项。

封面和社交卡要区分基础视觉系统、主题佐料、系列变量和事实层；同一系列每张只改变 2–4 个变量。`GPT2 x 早安 x 字体蒙版`是组合查询，不是新 preset。

## 执行闭环

1. **确认**：解析 L0–L2，并记录未指定轴的假设。
2. **取证**：仅 `social_skill_catalog` 运行 `build_social_catalog_facts.py`；仓库推荐/重点技能还要读取仓库 README 与重点技能 SKILL.md。
3. **编译**：创建 `prompts/NN-*.md`（系列页使用 `pNN-of-TT`），写全七个 blocks、页码字段和来源证据；未落盘不得生图。
4. **生成**：按 `render_engine` 路由（manifest 须记录该字段）：`imagegen`（默认，视觉海报/隐喻图/social 封面/logo 方向稿）→ Agent 内置 imagegen；`html_render`（`cornell_notes`/`editorial_summary_card`/`editorial_research_minimal` 文字密度高）→ html 模板 + puppeteer 截图 → PNG（正式产物，view_image 验收）；`svg_deterministic`（`plugin_icon`/`brand_logo` 终稿）→ 矢量重绘。禁止 Pillow/canvas 冒充终稿。
5. **验收**：按 [质量门](references/quality-gates.md) 实际 `view_image`（系列逐页执行）；社交卡再运行 `validate_social_catalog_delivery.py`，检查事实、OCR、二维码、缩略图和语义密度。
6. **重生**：只改一个主要问题，使用新 Prompt 和新文件名，最多连续重生两次；不要覆盖已通过版本。

## 交付目录与数据边界

未指定 `output_dir` 时，必须先运行：

```bash
python3 scripts/resolve_output_dir.py --source <source> --json
```

采用解析结果并在 manifest 记录 `output_dir_origin`。禁止把 cwd、技能仓、vault 根或 `<topic>-delivery-<date>` 当默认交付根；不要在交付目录保存缓存或未选候选。完整目录、配置、临时数据和回执见 [交付契约](references/delivery-contract.md)。

普通交付至少包含 `prompts/`、最终 PNG/JPG 和 `manifest.yml`；Cornell 多页另需系列级 `page_count`/`series_id` 和逐页页码、状态；两阶段模板另含事实清单和可复现合成源。X 进化交付另含 `evolution.yml`、`series-index.yml`、`bibles/` 和重编译 `prompts/`。

### 私密信息与中间数据

配置只放私有 skill-specific 根；中间候选放 OS 临时 run 目录并在结束后清理。provider 缓存、cookie、token、无关私人文件和绝对临时路径不进入公开交付。完整规则见 [交付契约](references/delivery-contract.md)。

## 硬性边界

- 不伪造二维码、安装命令、项目 URL、已有品牌 Logo、数字或人物身份；`brand_logo` 只用于客户明确要求的新品牌识别，不能冒充第三方或已存在品牌。
- 不把脚本返回 0 当作图片通过；Prompt 编译通过也不等于位图通过。
- 不读取无关私人目录，不把 provider 缓存、cookie、token 或临时路径写入公开交付。
- `imagegen` 路径缺少 imagegen 时停止并明确说明；`html_render` 路径不依赖 imagegen，可继续执行；所有路径缺少 `view_image` 时停止。Logo 第二阶段只有在已有批准路径、矢量规格和可视验收条件齐全时才能执行确定性 SVG，不得用代码输出冒充方向稿。

## 验证

```bash
python3 scripts/generate_skill_catalog.py --check
python3 scripts/generate_expert_manifest.py --check
python3 scripts/audit_skills.py
python3 -m unittest discover -s tests -p 'test_*.py'
```

前向测试必须逐张查看真实位图；X 进化测试还要检查 `base_visual_system`、`topic_seasoning`、`series_variables` 和 `render_plan`，不能只检查 YAML 是否存在。

## 完成后回执

```markdown
完成：<一句话结果>

路由：image_type=<值> preset=<值> family=<值> aspect=<值>
产出：Prompt=<路径> 图片=<路径/尺寸> manifest=<路径>
验证：事实=<通过/不适用> 文字=<通过/失败> 比例=<通过/失败> view_image=<通过/失败>
问题与下一步：<无；或列出未通过项>
```
