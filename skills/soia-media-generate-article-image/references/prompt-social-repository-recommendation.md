# Prompt deck: repository recommendation

## source_grounding

- 读取 `facts.yml`、`content-facts.yml`、仓库 `README.md` 与重点技能 `SKILL.md`。
- 仅使用可回指来源的仓库规模、能力分组、重点技能、交付形态、安装命令和 URL；未知信息删除，不猜测。
- 共享视觉参数只引用 `00-series-bible.md`；本文件必须单独写完本页画面与逐字文字。

## primary_task

做一张“值得收藏并立即试用”的仓库推荐页。缩略图先读结果/痛点钩子，打开后依次读规模、能力结构、重点技能判断、交付形态与安装入口。

## composition_and_layout

1. 顶部品牌条：逐字写 `【repository_display_name】`。
2. 核心价值区：单一主题隐喻 + 眉题 `【category_label】` + 主标题 `【headline】` + 副标题 `【subtitle】`。
3. 能力结构区：数量徽章 `【claim_text】`；2×2 或 3×2 展示 3–6 个可追溯能力组，每组写标题和一句用途。
4. 重点推荐区：橙色标题 `★ 重点推荐：【highlight_name】 ★`，放 3–4 条真实要点与一个真实效果/交付形态。
5. 底部 CTA：安装命令 `【install_command】`、项目地址 `【repository_url】`、真实二维码 `【qr_target】`。

## visual_style_and_materials

完全遵循 `00-series-bible.md` 的颜色角色、字体阶梯、组件比例、光线与移动端安全区。主视觉只表达仓库主题，不使用通用科技物体堆。

## exact_text

- 仓库名：`【repository_display_name】`
- 主标题：`【headline】`
- 副标题：`【subtitle】`
- 能力组：`【capability_groups】`
- 数量声明：`【claim_text】`
- 重点技能与要点：`【highlight_name】` / `【highlight_bullets】`
- 安装命令：`【install_command】`
- 项目地址：`【repository_url】`

## aspect_and_output

4:5 竖版社交卡；输出 PNG 位图与本 Prompt。正式文件名 `01-repository-recommendation.png`，候选用 `v1/v2`，不得覆盖旧版本。

## constraints_and_avoid

不把总数写成精选数，不把能力组写成未经来源支持的承诺；不伪造截图、二维码、Logo、版本号、测试数或用户评价。文字空间不足时缩短说明，不缩小高风险字段。
