# Image 交付契约

在 L3 生成与验收阶段读取。本文件承接输出目录、临时数据、交付结构和完成回执细则。

## 输出目录解析

优先级：客户明确的 `output_dir` → CLI `--output-dir` → `SOIA_MEDIA_ARTICLE_IMAGE_OUTPUT_DIR` → 私有 `config.yml` → `SOIA_DERIVED_OUTPUT_DIR` → Downloads 默认目录。

未指定目录时必须运行：

```bash
python3 scripts/resolve_output_dir.py --source <source-id> --json
```

manifest 必须记录 `output_dir_origin`。禁止使用 cwd、技能仓、vault 根、`outputs/` 或 `<topic>-delivery-<date>` 作为默认交付根。

### source-id 统一约定（所有 agent 必须一致）

不同 agent 对 `<source-id>` 的不同解读会导致输出目录分叉。按下表规则推导，不得使用随机目录名或调用时的 cwd：

| 输入类型 | source-id 规则 | 示例 |
|---------|---------------|------|
| X 推文 / Article URL | `x-{handle}-{status_id}` | `x-guansheng_ai-2083576296639283456` |
| 本地 Markdown 文件 | 文件 stem（不含扩展名） | `2026-08-01-AI-Agent` |
| 网页 URL | URL 最后路径段 slug | `ai-agent-engineering` |
| 任意主题字符串 | 小写 + 只保留 `[a-z0-9\-]` | `ai-agent-engineering` |

同一篇文章无论哪个 agent 执行，source-id 必须相同，输出目录唯一确定：`~/Downloads/soia-media-generate-article-image/<source-id>/`

## 目录结构

普通模板（`imagegen` 路径）：

```text
<output-dir>/
├── prompts/01-<preset>-<mechanism>-<topic>.md
├── <preset>-<topic>.png
└── manifest.yml
```

`html_render` 路径（`cornell_notes`、`editorial_summary_card`、`editorial_research_minimal`）：

```text
<output-dir>/
├── html/01-<preset>-<topic>.html      ← HTML 模板源文件
├── prompts/01-<preset>-<mechanism>-<topic>.md
├── <preset>-<topic>.png               ← puppeteer 截图产物
└── manifest.yml                       ← render_engine: html_render
```

品牌 Logo 两阶段交付：

```text
<output-dir>/
├── prompts/01-brand-logo-direction.md
├── vector/logo-master.svg
├── vector/mark-only.svg
├── vector/horizontal-lockup.svg
├── vector/stacked-lockup.svg
├── vector/monochrome.svg
├── vector/reversed.svg
├── exports/logo-color.png
├── exports/logo-monochrome.png
├── exports/logo-reversed.png
└── manifest.yml
```

Logo 的 SVG 是母版，PNG 是导出预览；manifest 必须记录字标是否已转路径、颜色值、
安全空间、最小尺寸、实际画布和每个变体的验收状态。没有确定性矢量终稿时只能交付方向稿，
不能写“Logo 终稿完成”。

技能库宣传卡还需要 `facts.yml`、`assets/`、`sources/`、`slides/` 和机器验收证据。仓库推荐/重点技能默认保留 `00-series-bible.md`、`01-repository-recommendation.md`、`02-featured-skill-deep-dive.md`。

X profile 进化导入：

```text
<output-dir>/x-profile-evolution/
├── evolution.yml
├── series-index.yml
├── bibles/<family>.md
├── prompts/001-<family>-<status-id>.md
└── manifest.yml
```

Prompt Deck 或 Prompt 编译通过不等于位图通过；最终交付必须有 PNG/JPG 和视觉验收记录。

## 私密数据

- 非秘密配置：`~/.config/soia-skills/soia-media-generate-article-image/`。
- 中间候选：OS 临时目录下的 skill-specific run 目录，成功或失败后清理。
- provider 缓存：由 provider 管理，不复制进 manifest 或交付目录。
- 运行回执：默认不持久化；需要保留时使用私有 state 根。
- 不把 cookie、token、登录态、无关私人文件或绝对临时路径写入公开技能仓。

插件安装和私有配置以 `config.example.yml` 及宿主插件文档为准；本技能不要求在仓库保存 API key、cookie 或 token。

## 质量门

必须实际 `view_image`，并按模板执行：

- 普通图：文件类型、尺寸、比例、层次、参考图角色和逐字文字。
- 社交卡：事实清单、OCR、二维码解码、移动端缩略图、语义密度和伪证据扫描。
- X 进化：窗口/筛选条件、来源证据、底座稳定性、每张 2–4 个系列变量和 `render_plan`。
- 品牌 Logo：图形标可缩小性、字标逐字、SVG 路径、颜色/黑白/反白变体、安全空间和最小尺寸。

失败时新建 Prompt 和版本化位图；最多连续重生两次，不覆盖已通过版本。

## 完成回执

```markdown
完成：<一句话结果>
路由：image_type=<值> preset=<值> family=<值> aspect=<值>
产出：Prompt=<路径> 图片=<路径/尺寸> manifest=<路径>
验证：事实=<通过/不适用> 文字=<通过/失败> 比例=<通过/失败> view_image=<通过/失败>
问题与下一步：<无；或列出未通过项>
```
