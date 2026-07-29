---
name: soia-media-generate-article-image
description: 为文章生成封面、小结卡、学习笔记、视觉隐喻海报或技能库宣传卡/轮播，并完成事实清单、Prompt、确定性文字与位图验收。触发：「生成文章图片」「正文小结图」「康奈尔笔记图」「技能库宣传图」「朋友圈配图」「小红书轮播」
version: 3.4.0
created_at: 2026-07-09 20:56:44
updated_at: 2026-07-29 14:59:08
created_by: claude opus 4.6
updated_by: gpt-5.6-sol
---

# soia-media-generate-article-image

为文章和开源项目生成真实位图：覆盖封面、正文小结卡、康奈尔笔记、视觉隐喻海报，以及技能库宣传单图/轮播。所有工作流共享模板路由、可配置输出目录、Prompt 落盘、`view_image` 视觉验收与版本化重生；高密度宣传卡额外使用来源事实清单和确定性排版，避免技能数量、命令、URL 与二维码被生图模型写错。不发布内容，不碰账号凭据。

## 客户可读说明

### 这个技能可以做什么

| 客户想要 | `image_type` / `preset` | 客户能看到 |
|---|---|---|
| 公众号、X、小红书文章封面 | `cover` / `godot_pixel_metaphor` 或 `auto` | 完整 Prompt、PNG/JPG 封面、视觉验收回执 |
| 正文段落或章节小结图 | `summary_card` / `editorial_summary_card` | 可嵌入正文的编辑式小结卡 |
| 把文章总结成康奈尔笔记 | `learning_note` / `cornell_notes` | A4 竖版康奈尔笔记信息图 |
| 技能库、插件集合宣传图 | `social_card` 或 `carousel` / `social_skill_catalog` | 事实清单、朋友圈单图或小红书轮播、机器验收回执 |
| 插件市场图标、应用图标 | `icon` / `plugin_icon` | 字形设计稿；终稿须矢量重绘，规格见模板 |
| 后续新增文章图片模板 | 注册到 `references/template-registry.yml` | 同一技能内按 preset 路由，不复制新技能 |

### 客户如何使用

1. 提供文章路径、完整正文、明确主题或技能仓路径；给出用途、平台、比例和必须逐字出现的文字。
2. 如有参考图，明确每张图是“风格参考”“构图参考”还是“编辑目标”。
3. 指定 `image_type`、`preset` 和 `output_dir`；省略时由 Agent 依据文章与用途推荐，并在生成前说明假设。客户说“直接生成”时可跳过确认。
4. Agent 读取 [模板注册表](references/template-registry.yml) 和所选模板；宣传卡先从实际仓库生成 `facts.yml`，再生成无文字主视觉和确定性排版终稿。
5. 多仓系列先用 [批次清单样例](references/social-card-batch.example.yml) 明确纳入与排除范围；脚本拒绝同一仓同时出现在两边。
6. 生成后必须用 `view_image` 检查比例、构图和参考图；密集宣传卡还要核对 OCR、CTA、二维码、移动端缩略图和事实指纹。失败时重生主视觉或重跑确定性合成源，不直接涂改位图。

插件市场安装：

```bash
claude plugin marketplace add soia-team/soia-open-skills
```

```bash
claude plugin install soia-media-content@soia
```

只要这一个技能时，可用 npx 路线。注意技能会落进共享真源 `~/.agents/skills`；若同时装了插件，同一技能会出现两份索引且各自漂移，建议二选一：

```bash
npx skills add soia-team/soia-open-media-content-skills -g -a '*' -s soia-media-generate-article-image -y
```

### 依赖与安装

| 依赖 | 类型 | 缺失时怎么处理 |
|---|---|---|
| 支持 imagegen 的 Agent / Codex 内置 `image_gen` | 强能力依赖 | 停止生成并说明缺失；不得切换为 HTML、SVG、canvas 或 Pillow 绘图 |
| `view_image` 或等价位图查看能力 | 强验收依赖 | 不得声称视觉验收通过；明确交给客户人工复核 |
| 确定性图形合成器与 OCR/二维码解码器 | `social_skill_catalog`、`plugin_icon` 条件强依赖 | 其他模板不受影响；两阶段模板停止终稿交付并说明缺失，不让 imagegen 代画确定性字段 |
| `soia-media-publish-wechat-draft` | 下游衔接，非安装依赖 | 仅在客户要推公众号草稿时，把已验收封面/正文图交给它 |

配置路径：

```text
~/.config/soia-skills/soia-media-generate-article-image/config.yml
SOIA_MEDIA_ARTICLE_IMAGE_CONFIG_FILE=<custom-config-path>
SOIA_MEDIA_ARTICLE_IMAGE_OUTPUT_DIR=<custom-output-directory>
```

- 本技能不需要 API key、cookie 或 token。Provider 登录态归 provider 自己管理。
- 配置样例见 `config.example.yml`。
- 输出目录解析脚本：`python3 scripts/resolve_output_dir.py --source <article.md> --json`。

### 私密信息与中间数据：文件放在哪里

| 类型 | 默认位置 | 内容与保留策略 |
|---|---|---|
| 非秘密配置 | `~/.config/soia-skills/soia-media-generate-article-image/` | 只放 `config.yml`；可用 `SOIA_SKILLS_CONFIG_HOME` 改根目录 |
| 中间候选 | OS 临时目录下 `soia-skills/soia-media-generate-article-image/<run-id>/` | 只放本次候选图和临时回执；成功、失败都清理 |
| Provider 缓存 | 由 imagegen provider 管理 | 本技能不移动、不复制、不把缓存路径写入交付 manifest |
| 可选运行回执 | `~/.local/state/soia-skills/soia-media-generate-article-image/` | 默认关闭；仅 `runtime.keep_run_receipts: true` 时持久保留 |
| 最终交付 | 客户明确目录；未指定时为 Downloads 下的技能目录 | 普通模板放 Prompt、位图和 manifest；两阶段模板另放 facts 与可复现合成源 |

- 只读取客户提供的文章、参考图和当前任务目录；不扫描无关私人目录。
- 默认不持久保留任何中间状态。`runtime.keep_failed_candidates: true` 仅用于客户明确要求排查失败生图时。
- 旧三层配置路径仅作只读兼容回退；新配置和所有新状态一律写入扁平的 skill-specific 路径。
- 不在技能仓、cwd、vault 根或最终交付目录中创建缓存与运行状态。
- 完整存储规范见仓库根 `DATA_STORAGE_SPEC.md`；脚本可用 `--json` 输出实际解析到的四类运行根与最终交付根。

### 日志与完成回执

```markdown
完成：已用 <preset> 为 <文章/主题> 生成 <image_type>。

日志摘要：
- 输入：<来源类型与标题，不打印私人绝对路径>
- 路由：image_type=<值> preset=<值> aspect=<值>
- 后端：<built-in imagegen 或客户指定后端>
- 输出目录来源：<user / cli / env / config / product / downloads-default>

产出：
- Prompt：<相对路径>
- 图片：<相对路径与像素尺寸>
- manifest：<相对路径>

验证：
- 来源事实与版本：<通过/失败/不适用>
- 文字逐字核对：<通过/失败>
- OCR 机械比对：<通过/失败/不适用>
- CTA 与二维码解码：<通过/失败/不适用>
- 尺寸与比例：<通过/失败>
- 移动端缩略预览：<通过/失败/不适用>
- view_image 视觉检查：<通过/失败及问题>
- 参考图一致性：<通过/不适用/差异>

问题与下一步：<无；或说明新版本文件名与重生原因>
```

## 输入契约

```yaml
source: <article-path | full-text | topic>
image_type: <cover | summary_card | learning_note | poster | social_card | carousel | icon | auto>
preset: <godot_pixel_metaphor | editorial_summary_card | cornell_notes | social_skill_catalog | plugin_icon | auto>
purpose: <wechat-cover | x-cover | rednote | wechat-moments | article-inline | poster | plugin-icon>
platform: <rednote | wechat-moments | general>
layout_mode: <single | carousel | auto>
slide_count: <1 | 2 | 3 | auto>
aspect: <2.35:1 | 16:9 | 3:2 | 4:5 | 9:16 | 1:1 | A4-portrait | custom>
series_id: <optional-batch-id>
facts_source:
  repo: <skill-repository-path>
  repository: <owner/repo>
  as_of_version: <optional-package-version>
  label_map: <optional-skill-name-to-display-label-yaml>
batch_spec: <optional-multi-repository-series-yaml>
claim_mode: <total | featured>
featured_skills: [<skill-name>]
cta_mode: <all | featured>
cta_featured_skill: <optional-skill-name>
qr_target: <optional-verbatim-url>
exact_text:
  title: <verbatim-title>
  subtitle: <optional-verbatim-subtitle>
brand_assets:
  - path: <approved-asset-path>
    role: <logo | platform-mark | screenshot>
reference_images:
  - path: <image-path>
    role: <style-reference | composition-reference | edit-target>
output_dir: <optional-directory>
quick: false
```

`image_type` 决定交付用途，`preset` 决定视觉与提示词模板。常见映射：

- `cover + godot_pixel_metaphor`：像素风视觉隐喻封面。
- `summary_card + editorial_summary_card`：正文小结卡。
- `learning_note + cornell_notes`：康奈尔笔记学习信息图。
- `social_card|carousel + social_skill_catalog`：来源可核验的技能库宣传卡；朋友圈单图默认最多 4 项，小红书轮播优先 2–3 张并可自动分页。
- `icon + plugin_icon`：imagegen 只产出字形设计方向，终稿确定性矢量重绘。

## 模板路由

1. 读取 [template-registry.yml](references/template-registry.yml)。
2. 客户指定 preset 时严格使用；未指定时根据 `image_type`、用途和文章结构选最匹配模板。
3. 只加载所选模板：
   - [Godot 像素视觉隐喻](references/prompt-godot-pixel-metaphor.md)
   - [编辑式正文小结卡](references/prompt-editorial-summary-card.md)
   - [康奈尔笔记信息图](references/prompt-cornell-notes-infographic.md)
   - [技能库社交宣传卡](references/prompt-social-skill-catalog.md)，并同时读取 [社交卡机器契约](references/social-card-contract.yml)
   - [插件/应用图标](references/prompt-plugin-icon.md)
4. 模板是母本，不是最终 Prompt。把文章事实、逐字标题、比例和参考图角色填入后，写出本次完整 Prompt。
5. 新增模板时：新增一个直接引用的 `references/prompt-*.md`，在注册表增加一项，并补一个真实前向测试；不要把长模板堆进本文件。

## 结构化 Prompt 编译

按注册表 `prompt_blocks.required` 的顺序编译最终 Prompt，不从案例库整段复制成品 Prompt：

1. `source_grounding`：列出允许使用的文章事实、禁止代写的观点和缺失信息。
2. `primary_task`：只写一个主要视觉任务，避免把封面、小结图、信息图混成一张。
3. `composition_and_layout`：写清主体、焦点、空间关系、留白与移动端阅读顺序。
4. `visual_style_and_materials`：用媒介、材质、光线、边缘和色彩描述视觉，不依赖艺术家姓名或含糊的“高级感”。
5. `exact_text`：把逐字文字单独列出；密集中文先保证标题、数字、专有名词和层级，再压缩解释。
6. `aspect_and_output`：写明目标比例、用途和位图格式；生成后记录实际像素与比例，不用 Prompt 中的目标值冒充结果。
7. `constraints_and_avoid`：只保留会改变结果的约束，删除互相重复、不可验证或与当前模板无关的规则。

`social_skill_catalog` 先运行 `build_social_catalog_facts.py`，把 `facts.yml` 的事实指纹写入 manifest；Prompt 的 `source_facts` 只引用该文件，不手写第二份技能列表。注册表标记为 `deterministic_fields` 的字段不得进入 imagegen Prompt，只进入确定性合成源。

需要多个概念时，保持同一 preset，每版只改变主体、构图、配色、场景中的 2–4 项，并分别落盘；不要同时更换模板和全部风格轴，导致版本无法比较。

## 输出目录（C 类交付物）

按以下优先级解析，第一项命中即停止：

1. 客户当前请求明确给出的 `output_dir`。
2. CLI `--output-dir`。
3. 环境变量 `SOIA_MEDIA_ARTICLE_IMAGE_OUTPUT_DIR`。
4. 私有 `config.yml` 的 `paths.output_dir`。
5. 调用方明确提供的产品派生目录 `SOIA_DERIVED_OUTPUT_DIR`。
6. 跨平台默认：用户 Downloads 下的 `soia-media-generate-article-image/<source-stem>/`。

禁止把 cwd、技能仓或 vault 根 `outputs/` 当默认目录。Obsidian 等产品已有派生产物规范时，由调用方通过 `output_dir` 或 `SOIA_DERIVED_OUTPUT_DIR` 传入，本技能不硬编码任何 vault 目录名。

最终交付目录保持以下结构：

```text
<output-dir>/
├── prompts/
│   └── 01-<preset>-<topic-slug>.md
├── <preset>-<topic-slug>.png
└── manifest.yml
```

`social_skill_catalog` 使用扩展结构：

```text
<output-dir>/
├── facts.yml
├── prompts/
│   └── 01-social-skill-catalog-hero.md
├── assets/
│   └── hero-art.png
├── sources/
│   └── <deterministic-layout-source>
├── slides/
│   ├── 01-cover.png
│   ├── 02-catalog.png
│   ├── 03-highlight.png
│   └── 04-cta.png
└── manifest.yml
```

上图是四角色展开示例，不是固定页数。可按内容生成 1、2、3 张或更多：多个角色允许合并到同一张，manifest 用 `roles` 数组记录；单图必须同时承担 `cover`、`catalog`、`cta`。`auto` 优先选择 2–3 张，技能总数仍超出每页上限时继续增加能力页。确定性源可以保留以便复现，最终对外图片必须是位图。

重生使用 `02-...md` 与 `...-v2.png`，不覆盖旧版本。未选中的候选图不进入最终交付目录，除非客户明确要求保留对比版本。普通模板的正式产物不包含 HTML；两阶段模板可保留确定性合成源，但终稿必须是位图。

## 执行流程

### 1. 提炼单一图片任务

- `cover`：抓一个最强视觉隐喻，标题必须逐字使用客户/原文标题。
- `summary_card`：抓一句主命题、1–3 个关键词和必要补充解释，不把整篇文章塞进图。
- `learning_note`：先生成问题—答案覆盖表，再组织为左侧线索、右侧笔记、底部回顾。
- `social_card` / `carousel`：先锁定平台、`slide_count`、`claim_mode` 和 `cta_mode`；允许 1、2、3 张或自动分页，全量能力超过每页密度上限时继续拆页，不缩小文字硬塞。
- `icon`：只提炼一个字形隐喻；图标家族参数与终稿规格见模板。
- 不代写客户观点；输入缺少结论时标注缺失，不凭空补事实。

### 2. 生成来源事实

仅 `social_skill_catalog` 执行：

```bash
python3 scripts/build_social_catalog_facts.py \
  --repo <skill-repo> \
  --repository <owner/repo> \
  --claim-mode <total|featured> \
  --cta-mode <all|featured> \
  --output <output-dir>/facts.yml
```

核对 `displayed_skill_count`、技能名/展示标签、版本、CTA 和仓库 URL。展示标签默认来自 `agents/openai.yaml`；需要中文短名时另加 `--label-map <label-map.yml>`，不在版面阶段临时改名。客户提供的数字与仓库不一致时，以事实清单为准并明确提示；不得继续把旧数字画进图。

多仓系列先复制 [social-card-batch.example.yml](references/social-card-batch.example.yml)，逐项写明 `include` 与 `exclude`，再运行：

```bash
python3 scripts/build_social_catalog_batch.py \
  --spec <batch-spec.yml> \
  --output <output-dir>/batch-facts.yml
```

把 `batch_fingerprint` 写入系列 manifest。实际产出仓、文案声明范围与 batch facts 不一致时停止，不生成或发布该批次。

### 3. 编译并落盘最终 Prompt

生成前创建 `prompts/NN-<preset>-<slug>.md`，按注册表 required blocks 写全：来源边界、主要任务、构图、视觉语言、逐字文字、目标比例/用途和禁止项；有参考图时再写逐张角色。未落盘不得调用生图。

### 4. 生成主视觉与两阶段终稿

- 默认使用 Agent 内置 imagegen / `image_gen`。
- 参考图是风格或构图参考时，按索引逐张写明角色；不要把它们误当成编辑目标。
- 生图工具不可用时停止；不得使用 HTML/CSS、SVG、canvas、Pillow、ImageMagick 或截图方式冒充主视觉。
- `two_stage: true` 的模板是唯一例外：imagegen 产出无文字设计稿/主视觉后，使用确定性图形工具排版注册表声明的字段。代码渲染不能代替主视觉生成，也不能修改非确定性插画内容。
- `social_skill_catalog` 的文字、命令、URL、二维码和批准 Logo 全部在第二阶段加入；二维码必须由目标 URL 编码生成，禁止扩散模型生成伪二维码。
- 不要求位图后端把 Markdown、wikilink、文件路径或内部说明画进图片。
- 每次调用创建唯一 `<run-id>` 临时目录；将选中位图复制到最终交付目录后，无论成功或失败都清理临时目录。
- Provider 自有缓存不属于技能产物，不写入 manifest，也不把 provider 缓存目录当交付目录。

### 5. 真实验收

按 [quality-gates.md](references/quality-gates.md) 检查：文件类型、尺寸、逐字文字、布局、视觉质量、参考图相似性和来源保真。必须实际 `view_image`；只看命令退出码不算通过。社交宣传卡还必须运行 `validate_social_catalog_delivery.py`，并保留 OCR、二维码解码和移动端缩略预览证据。

### 6. 失败重生

- 主视觉偏离或风格不符：只改一个主要问题，写新 Prompt，生成新位图。
- 非两阶段模板出现中文错误时重生，不在位图上描字、补字、遮盖或局部代码修图。
- 两阶段模板出现确定性字段错误时，修正事实/合成源并整体重跑；不得直接涂改最终位图。
- 最多连续重生两次；仍失败时交付最佳版本并准确列出未通过项。

## 私有配置样例

以 `config.example.yml` 为 schema 真源；脚本与说明不得维护另一套字段。运行时配置优先级为当前请求/CLI > 环境变量 > 私有配置 > 安全默认。

## 边界

- 本技能生成图片，不负责文章排版、平台上传或发布。
- `soia-media-publish-wechat-draft --cover` 可消费本技能的封面；正文图由发布技能按文章中的图片引用处理。
- 不承诺生图模型第一次就能正确渲染所有密集中文；必须以视觉验收和版本化重生结果为准。
- 不让 imagegen 伪造二维码、安装命令、项目 URL 或品牌 Logo；两阶段模板用事实清单与确定性合成解决这些字段。
- 不把“脚本返回 0”当作视觉验收；社交卡必须同时具备机器比对结果和实际位图检查。

## 验证

- 路径：`python3 scripts/resolve_output_dir.py --source <article.md> --output-dir <dir> --json`，确认 config/state/cache/temp 与 deliverable 相互分离。
- 事实：`python3 scripts/build_social_catalog_facts.py --repo <repo> --repository <owner/repo> --output <dir>/facts.yml`，核对数量、技能名、版本、CTA 与仓库地址。
- 批次：`python3 scripts/build_social_catalog_batch.py --spec <batch-spec.yml> --output <dir>/batch-facts.yml`，核对纳入/排除仓、总技能数和批次指纹。
- 社交卡：`python3 scripts/validate_social_catalog_delivery.py --facts <dir>/facts.yml --delivery <dir>/manifest.yml`，必须输出 `PASS`。
- Skill 结构：`python3 <skill-creator>/scripts/quick_validate.py skills/soia-media-generate-article-image`
- 仓库：`python3 -m unittest discover -s tests -p 'test_*.py'`
- 目录：普通模板存在 Prompt + 位图 + manifest；两阶段模板还存在 facts、可复现合成源和机器验收证据。最终交付必须包含位图。
- 视觉：实际打开最终位图逐项核对，不把“已生成”写成“已通过”。
