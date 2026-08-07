# Image 输入契约

L0 选定用途和家族后，再读取本文件。首层 `SKILL.md` 只保留路由；本文件保存可复现输入字段和来源边界。

## 通用字段

```yaml
source: <article-path | full-text | topic | x-profile-export>
image_type: <cover | summary_card | learning_note | poster | social_card | carousel | icon | logo | auto>
preset: <godot_pixel_metaphor | editorial_summary_card | editorial_research_minimal | cornell_notes | social_skill_catalog | plugin_icon | brand_logo | auto>
family: <auto | morning_city | poster_type_stage | presentation_grid | travel_publication | portrait_identity | event_people | celebration_ceremony | hospitality_food | archival_print | pixel_play | brand_identity>
use_case: <auto | good_morning | presentation | repository_recommendation | featured_skill | event_poster | birthday_poster | hospitality_poster | brand_identity>
information_structure: <auto | single_hook | knowledge_card | deck_page | deck_series | carousel_sequence | portrait_brief | campaign_pack | logo_system>
asset_role: <auto | none | reference_subject | identity_reference | brand_asset | proof_screenshot | foreground_subject>
visual_mechanism: <auto | typographic_mask | oversized_type | oversized_type_whitespace | color_field_stage | modular_grid | travel_editorial_narrative | pixel_dissolution | geometric_mark>
aesthetic_system: <auto | editorial_aesthetic | bright_modern | archival_historical | travel_publication | portrait_editorial | ceremonial_soft | hospitality_premium | playful_pixel | brand_system>
text_strategy: <auto | exact_text | cjk_exact_text | hero_typography | quote_led | latin_hero_type | logo_wordmark>
model_adapter: <auto | builtin_imagegen | external_gpt_image_label | text_orchestrator_only | text_orchestrator_or_provider_dependent>
batch_strategy: <single | series | auto>
output_mode: <poster | slide | carousel | campaign_pack | logo | auto>
logo_variant: <color | monochrome | reversed | all_variants | auto>
purpose: <wechat-cover | x-cover | rednote | wechat-moments | article-inline | poster | plugin-icon | brand-logo>
platform: <rednote | wechat-moments | general>
layout_mode: <single | carousel | auto>
slide_count: <1 | 2 | 3 | auto>
aspect: <2.35:1 | 16:9 | 3:2 | 3:4 | 4:5 | 9:16 | 1:1 | A4-portrait | custom>
render_mode: <direct_poster | hybrid_exact_text | vector_two_stage | auto>
output_dir: <optional-directory>
quick: false
```

可选字段包括 `series_id`、`facts_source`、`batch_spec`、`claim_mode`、`featured_skills`、`cta_mode`、`qr_target`、`exact_text`、`brand_assets` 和 `reference_images`。参考图必须声明 `style-reference`、`composition-reference`、`style_density_reference` 或 `edit-target`；标记 `style_density_reference` 时只继承版式、密度、材质和颜色角色，不继承参考图事实。

Logo 请求还必须提供：

```yaml
brand_logo:
  brand_name: <品牌名称>
  mark_concept: <一个核心图形概念>
  wordmark: <逐字字标，可选>
  wordmark_viewbox: <有 wordmark_path 时必填，例如 0 0 500 110>
  wordmark_path: <可选；确定性字标轮廓路径，必须与 wordmark_viewbox 同坐标系>
  tagline: <逐字副标题，可选>
  mark_viewbox: <有 mark_path 时必填，例如 0 0 800 800>
  mark_path: <确定性主图形路径>
  mark_accent_path: <可选；强调节点/辅助图形路径，与 mark_viewbox 同坐标系>
  mark_stroke_width: <可选；主图形为描边路径时的描边宽度>
  lockups: [mark-only, wordmark-only, horizontal-lockup, stacked-lockup, app-icon]
  variants: [color, monochrome, reversed]
  primary_color: <hex>
  secondary_color: <hex，可选>
  approved_font: <字体名或字体文件路径，可选>
  clear_space_ratio: <例如 0.25>
  min_size_px: <例如 24>
```

## 交付路由

- `cover + godot_pixel_metaphor`：像素视觉隐喻封面。
- `cover|summary_card + editorial_research_minimal`：研究编辑极简风。
- `summary_card + editorial_summary_card`：正文小结卡。
- `learning_note + cornell_notes`：康奈尔笔记。
- `social_card|carousel + social_skill_catalog`：可核验的技能库宣传卡。
- `icon + plugin_icon`：插件/应用图标字形方向后确定性矢量重绘。
- `logo + brand_logo`：品牌 Logo 方向稿后确定性矢量重绘，必须输出 SVG 母版与颜色/组合变体。

`family` 是 Prompt 检索家族，`preset` 是交付契约；组合轴优先于新增 preset。`GPT2` 只记录来源模型标签，不限制可用 imagegen provider。

## 比例选择

`aspect` 按投放平台定，不要一律套 4:5：

| 平台 / 用途 | 比例 | 依据 |
|---|---|---|
| `rednote`（小红书） | **3:4** | 小红书信息流允许的最高竖版比例，占屏最多；4:5 会白白让出高度。2026-08-06 实发验证 2160×2880 正常展示 |
| `wechat-moments`（朋友圈） | 4:5 | 朋友圈按方形裁切预览，4:5 更耐裁 |
| `article-inline`（正文内嵌） | 3:2 或 16:9 | 随正文宽度排版，过高会打断阅读 |
| `x-cover` | 16:9 | |

## 层级 A：Prompt 文件的七个内容块

下面七个是 **Prompt 文件的章节名**（前面还有一个 `composition_axes` 头，不计入七块）。
它们与 [组合块执行契约](prompt-block-contract.yml) 里的 `per_block_required_fields` **不是同一层**——
那组字段名（`role_in_frame`、`composition_parameters`、`acceptance_checks` 等）只在每个组合块内部使用，
不要拿来当章节名。层级关系见 `SKILL.md`「两个层级，别混」。

## 必须保留的证据

X profile 导入必须同时存在 `manifest.yml`、`source_profile`、`source_status_id`、`source_url`、`selection.filters`、`source_prompt`、`composition_axes` 头和七个内容块：

```text
source_grounding
primary_task
composition_and_layout
visual_style_and_materials
exact_text
aspect_and_output
constraints_and_avoid
```

缺少来源 URL、正文/ALT、状态 ID 或 canonical block 时标记 `BLOCKED`，不以模型常识补写。
