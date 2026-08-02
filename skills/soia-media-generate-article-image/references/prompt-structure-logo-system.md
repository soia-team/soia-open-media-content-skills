# Information structure: Logo system

## 任务

把一个品牌识别需求拆为可复用的图形标、字标、组合锁定和应用变体，而不是只生成一张装饰性图片。

## 必须编译的字段

- `brand_name`
- `mark_concept`
- `wordmark` / `tagline` 的逐字字段
- `lockup_variants`
- `color_variants`
- `clear_space_ratio`
- `min_size_px`
- `approved_font_or_path`

## 页面/画板角色

1. 概念方向板：最多 2–4 个候选，说明每个候选的核心隐喻。
2. 选定标志：记录几何底座、比例和负空间规则。
3. 组合锁定：mark-only、wordmark-only、horizontal-lockup、stacked-lockup。
4. 应用变体：color、monochrome、reversed、app-icon（按需求选择）。

## 验收

- 每个变体都能回指同一几何底座。
- 文字和颜色没有随机补写。
- 终稿含 SVG；PNG 只作为导出预览。
