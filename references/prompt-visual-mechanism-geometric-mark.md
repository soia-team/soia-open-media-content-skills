# Visual mechanism: Geometric mark

用轮廓、网格、负空间和单一几何隐喻建立可缩小的 Logo 图形。

## Compile fields

- `mark_concept`
- `primitive_set`
- `grid_or_ratio`
- `negative_space_rule`
- `stroke_or_fill_rule`
- `small_size_simplification`

## Rules

- 一个 Logo 只保留一个主隐喻，避免把多个图标拼成说明书。
- 先定义外轮廓和负空间，再添加最少的辅助切口或节点。
- 线宽、圆角和端点在所有 lockup 变体中保持一致。
- 不依赖渐变、阴影或复杂纹理来维持识别度。

## Acceptance

- 轮廓在小尺寸仍然清楚。
- mark-only 和 app-icon 裁切不丢失主识别特征。
- SVG 使用确定性路径，不嵌入截图或扩散模型位图。
