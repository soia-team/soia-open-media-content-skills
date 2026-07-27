---
name: soia-media-generate-article-image
description: 为文章生成封面、正文小结卡、康奈尔笔记或视觉隐喻海报，并完成 Prompt 落盘和位图验收。触发：「生成文章图片」「正文小结图」「康奈尔笔记图」「Godot 像素海报」
version: 3.1.0
created_at: 2026-07-09 20:56:44
updated_at: 2026-07-27 11:44:45
created_by: claude opus 4.6
updated_by: gpt-5.6-sol
---

# soia-media-generate-article-image

为文章生成真实位图：既覆盖原 `cover` 封面流程，也覆盖正文小结卡、康奈尔笔记信息图和视觉隐喻海报。所有工作流共享模板路由、可配置输出目录、Prompt 落盘、`view_image` 视觉验收与版本化重生；不排版文章、不发布内容、不碰账号凭据。

## 客户可读说明

### 这个技能可以做什么

| 客户想要 | `image_type` / `preset` | 客户能看到 |
|---|---|---|
| 公众号、X、小红书文章封面 | `cover` / `godot_pixel_metaphor` 或 `auto` | 完整 Prompt、PNG/JPG 封面、视觉验收回执 |
| 正文段落或章节小结图 | `summary_card` / `editorial_summary_card` | 可嵌入正文的编辑式小结卡 |
| 把文章总结成康奈尔笔记 | `learning_note` / `cornell_notes` | A4 竖版康奈尔笔记信息图 |
| 后续新增文章图片模板 | 注册到 `references/template-registry.yml` | 同一技能内按 preset 路由，不复制新技能 |

### 客户如何使用

1. 提供文章路径、完整正文或明确主题；给出用途、比例、图片上必须逐字出现的文字。
2. 如有参考图，明确每张图是“风格参考”“构图参考”还是“编辑目标”。
3. 指定 `image_type`、`preset` 和 `output_dir`；省略时由 Agent 依据文章与用途推荐，并在生成前说明假设。客户说“直接生成”时可跳过确认。
4. Agent 读取 [模板注册表](references/template-registry.yml) 和所选模板，按注册表的原子字段编译本次 Prompt，落盘后再调用 imagegen。
5. 生成后必须用 `view_image` 检查文字、比例、构图和参考图相似性。失败只能修改 Prompt 后生成新版本，禁止在位图上覆盖文字。

安装单个技能：

```bash
npx skills add soia-team/soia-open-media-content-skills -g -a '*' -s soia-media-generate-article-image -y
```

### 依赖与安装

| 依赖 | 类型 | 缺失时怎么处理 |
|---|---|---|
| 支持 imagegen 的 Agent / Codex 内置 `image_gen` | 强能力依赖 | 停止生成并说明缺失；不得切换为 HTML、SVG、canvas 或 Pillow 绘图 |
| `view_image` 或等价位图查看能力 | 强验收依赖 | 不得声称视觉验收通过；明确交给客户人工复核 |
| `soia-media-publish-wechat-draft` | 下游衔接，非安装依赖 | 仅在客户要推公众号草稿时，把已验收封面/正文图交给它 |

配置路径：

```text
~/.config/soia-skills/soia-open-media-content-skills/soia-media/soia-media-generate-article-image/config.yml
SOIA_MEDIA_ARTICLE_IMAGE_CONFIG_FILE=<custom-config-path>
SOIA_MEDIA_ARTICLE_IMAGE_OUTPUT_DIR=<custom-output-directory>
```

- 本技能不需要 API key、cookie 或 token。Provider 登录态归 provider 自己管理。
- 配置样例见 `config.example.yml`。
- 输出目录解析脚本：`python3 scripts/resolve_output_dir.py --source <article.md> --json`。

### 私密信息与中间数据：文件放在哪里

| 类型 | 默认位置 | 内容与保留策略 |
|---|---|---|
| 非秘密配置 | `~/.config/soia-skills/soia-open-media-content-skills/soia-media/soia-media-generate-article-image/` | 只放 `config.yml`；可用 `SOIA_SKILLS_CONFIG_HOME` 改根目录 |
| 中间候选 | OS 临时目录下 `soia-skills/soia-open-media-content-skills/soia-media/soia-media-generate-article-image/<run-id>/` | 只放本次候选图和临时回执；成功、失败都清理 |
| Provider 缓存 | 由 imagegen provider 管理 | 本技能不移动、不复制、不把缓存路径写入交付 manifest |
| 可选运行回执 | `~/.local/state/soia-skills/soia-open-media-content-skills/soia-media/soia-media-generate-article-image/` | 默认关闭；仅 `runtime.keep_run_receipts: true` 时持久保留 |
| 最终交付 | 客户明确目录；未指定时为 Downloads 下的技能目录 | 只放最终 Prompt、选中位图和 manifest |

- 只读取客户提供的文章、参考图和当前任务目录；不扫描无关私人目录。
- 默认不持久保留任何中间状态。`runtime.keep_failed_candidates: true` 仅用于客户明确要求排查失败生图时。
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
- 文字逐字核对：<通过/失败>
- 尺寸与比例：<通过/失败>
- view_image 视觉检查：<通过/失败及问题>
- 参考图一致性：<通过/不适用/差异>

问题与下一步：<无；或说明新版本文件名与重生原因>
```

## 输入契约

```yaml
source: <article-path | full-text | topic>
image_type: <cover | summary_card | learning_note | poster | auto>
preset: <godot_pixel_metaphor | editorial_summary_card | cornell_notes | auto>
purpose: <wechat-cover | x-cover | rednote | article-inline | poster>
aspect: <2.35:1 | 16:9 | 3:2 | 4:5 | 9:16 | 1:1 | A4-portrait | custom>
exact_text:
  title: <verbatim-title>
  subtitle: <optional-verbatim-subtitle>
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

## 模板路由

1. 读取 [template-registry.yml](references/template-registry.yml)。
2. 客户指定 preset 时严格使用；未指定时根据 `image_type`、用途和文章结构选最匹配模板。
3. 只加载所选模板：
   - [Godot 像素视觉隐喻](references/prompt-godot-pixel-metaphor.md)
   - [编辑式正文小结卡](references/prompt-editorial-summary-card.md)
   - [康奈尔笔记信息图](references/prompt-cornell-notes-infographic.md)
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

重生使用 `02-...md` 与 `...-v2.png`，不覆盖旧版本。未选中的候选图不进入最终交付目录，除非客户明确要求保留对比版本。**正式产物不包含 HTML。**

## 执行流程

### 1. 提炼单一图片任务

- `cover`：抓一个最强视觉隐喻，标题必须逐字使用客户/原文标题。
- `summary_card`：抓一句主命题、1–3 个关键词和必要补充解释，不把整篇文章塞进图。
- `learning_note`：先生成问题—答案覆盖表，再组织为左侧线索、右侧笔记、底部回顾。
- 不代写客户观点；输入缺少结论时标注缺失，不凭空补事实。

### 2. 编译并落盘最终 Prompt

生成前创建 `prompts/NN-<preset>-<slug>.md`，按注册表 required blocks 写全：来源边界、主要任务、构图、视觉语言、逐字文字、目标比例/用途和禁止项；有参考图时再写逐张角色。未落盘不得调用生图。

### 3. 只调用真实生图后端

- 默认使用 Agent 内置 imagegen / `image_gen`。
- 参考图是风格或构图参考时，按索引逐张写明角色；不要把它们误当成编辑目标。
- 生图工具不可用时停止，绝不使用 HTML/CSS、SVG、canvas、Pillow、ImageMagick 或截图方式冒充。
- 不要求位图后端把 Markdown、wikilink、文件路径或内部说明画进图片。
- 每次调用创建唯一 `<run-id>` 临时目录；将选中位图复制到最终交付目录后，无论成功或失败都清理临时目录。
- Provider 自有缓存不属于技能产物，不写入 manifest，也不把 provider 缓存目录当交付目录。

### 4. 真实验收

按 [quality-gates.md](references/quality-gates.md) 检查：文件类型、尺寸、逐字文字、布局、视觉质量、参考图相似性和来源保真。必须实际 `view_image`；只看命令退出码不算通过。

### 5. 失败重生

- 中文错误、布局偏离、风格不符：只改一个主要问题，写新 Prompt，生成新位图。
- 禁止在原图上描字、补字、遮盖、拼接或局部代码修图。
- 最多连续重生两次；仍失败时交付最佳版本并准确列出未通过项。

## 私有配置样例

以 `config.example.yml` 为 schema 真源；脚本与说明不得维护另一套字段。运行时配置优先级为当前请求/CLI > 环境变量 > 私有配置 > 安全默认。

## 边界

- 本技能生成图片，不负责文章排版、平台上传或发布。
- `soia-media-publish-wechat-draft --cover` 可消费本技能的封面；正文图由发布技能按文章中的图片引用处理。
- 不承诺生图模型第一次就能正确渲染所有密集中文；必须以视觉验收和版本化重生结果为准。

## 验证

- 路径：`python3 scripts/resolve_output_dir.py --source <article.md> --output-dir <dir> --json`，确认 config/state/cache/temp 与 deliverable 相互分离。
- Skill 结构：`python3 <skill-creator>/scripts/quick_validate.py skills/soia-media-generate-article-image`
- 仓库：`python3 -m unittest discover -s tests -p 'test_*.py'`
- 目录：最终输出存在 Prompt + 位图 + manifest，且不存在本次新生成的 HTML。
- 视觉：实际打开最终位图逐项核对，不把“已生成”写成“已通过”。
