# Prompt template: Brand logo system

## 适用场景

- `image_type: logo`
- `preset: brand_logo`
- 新品牌的图形标、字标、组合锁定和应用变体

它与 `plugin_icon` 的区别是：`plugin_icon` 解决一个方形市场图标；`brand_logo`
解决可以跨网页、文档、社交头像、深浅背景和小尺寸使用的品牌识别系统。

## 两阶段交付

### 阶段 1：imagegen 方向稿

imagegen 只负责探索 2–4 个图形概念、负空间、几何比例、色彩关系和横竖组合方向。
不得把模型生成的字标、商标、二维码、网址或“已注册品牌”当成事实。

### 阶段 2：确定性矢量终稿

选定方向后，用确定性矢量脚本或设计工具重绘并输出：

- `mark-only`：图形标单独使用
- `wordmark-only`：字标单独使用
- `horizontal-lockup`：横向组合
- `stacked-lockup`：上下组合
- `app-icon`：需要时再派生 App 图标
- `color`、`monochrome`、`reversed`：至少三套颜色变体

终稿必须保留 SVG 母版，并按客户要求导出 PNG。字标应使用批准字体或字形路径；
不能把一次扩散模型的乱码直接当作 Logo 字标。
如果方向稿包含强调节点，阶段 2 应把它作为 `mark_accent_path` 与
`secondary_color` 一起确定性重绘，不能在矢量终稿中静默丢失。

## 输入字段

```yaml
brand_logo:
  brand_name: <品牌名称>
  mark_concept: <一个核心概念；不要叠加无关隐喻>
  mark_accent_path: <可选；与 mark_viewbox 同坐标系的强调节点路径>
  mark_stroke_width: <可选；中心线图形的确定性描边宽度>
  wordmark: <逐字字标，可选>
  tagline: <逐字副标题，可选>
  lockups: [mark-only, wordmark-only, horizontal-lockup, stacked-lockup, app-icon]
  variants: [color, monochrome, reversed]
  primary_color: <hex>
  secondary_color: <hex，可选>
  approved_font: <字体名或字体文件路径，可选>
  clear_space_ratio: <例如 0.25>
  min_size_px: <例如 24>
  reference_images: <style-reference | composition-reference | edit-target>
```

## 组合轴编译

- `family=brand_identity`
- `information_structure=logo_system`
- `visual_mechanism=geometric_mark`
- `aesthetic_system=brand_system`
- `text_strategy=logo_wordmark`
- `render_mode=vector_two_stage`

## 质量门

1. 图形标在 16–24px 缩略尺寸下仍可辨认。
2. 字标逐字正确；字体、字距、大小写和中英文混排有明确来源。
3. 横向、上下、单标和深浅背景变体共享同一几何底座。
4. 记录安全空间、最小尺寸、颜色值和实际画布尺寸。
5. SVG 不嵌入位图；PNG 只是导出物，不替代 SVG 母版。
6. `view_image` 检查每个变体，并检查透明背景与深浅背景对比。

## Prompt 母本

```text
创建一个全新的品牌 Logo 方向稿，不复制任何现有品牌或第三方 Logo。
品牌名称：<brand_name>
核心概念：<mark_concept>
字标：<wordmark 或“阶段 1 只留字标位置”>

图形任务：用一个可在小尺寸识别的几何图形表达核心概念，优先使用轮廓、负空间和单一主隐喻。
组合任务：同时考虑 mark-only、horizontal-lockup 和 stacked-lockup 的比例关系。
视觉系统：<primary_color> 为主色，<secondary_color> 为辅助色；提供浅底、深底和单色方向。
如果有强调节点，保持节点位置、比例和负空间关系在所有组合中一致。
阶段边界：这是方向稿，不是最终矢量 Logo；不要生成二维码、网址、随机英文、伪商标或注册声明。
验收重点：轮廓清晰、构图可缩小、字标位置明确、变体之间几何一致。
```
