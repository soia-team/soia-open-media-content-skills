# Prompt deck: featured skill deep dive

## source_grounding

- 读取重点技能完整 `SKILL.md`、仓库 `README.md`、`facts.yml` 与 `content-facts.yml`。
- 所有输入、能力、优势、工作流、交付物、验证方式、安全边界、命令和 URL 必须记录来源路径；没有来源的卖点不进入图片。
- 共享视觉参数只引用 `00-series-bible.md`；本文件必须单独写完本页画面与逐字文字。

## primary_task

做一张回答“它具体怎么工作、为什么值得用、如何验收”的重点技能深挖页。避免重复第一页能力目录，用真实工作流和交付物形成结果闭环。

## composition_and_layout

1. 顶部品牌条与反差/结果标题：仓库名 `【repository_display_name】`，主标题 `【headline】`。
2. 输入区：用 3–6 个图标列出支持输入 `【inputs】`，不扩写未声明格式。
3. 核心能力与真正优势：并列展示 `【capabilities】`、`【advantages】`，每条说明一个判断点。
4. 工作流区：4–7 步编号流程 `【workflow_steps】`，箭头方向明确，不把步骤合并成抽象“闭环”。
5. 交付/验收/边界区：分别写 `【deliverables】`、`【validation】`、`【guardrails】`。
6. 底部 CTA：安装命令 `【install_command】`、项目地址 `【repository_url】`；二维码只使用真实目标。

## visual_style_and_materials

完全遵循 `00-series-bible.md` 的颜色角色、字体阶梯、组件比例、光线与移动端安全区。步骤图标、箭头和效果证据保持同一视觉语言；真实截图原样使用，不重绘界面文字。

## exact_text

- 仓库名：`【repository_display_name】`
- 主标题：`【headline】`
- 输入：`【inputs】`
- 核心能力：`【capabilities】`
- 优势：`【advantages】`
- 工作流：`【workflow_steps】`
- 交付物：`【deliverables】`
- 验收：`【validation】`
- 边界：`【guardrails】`
- 安装命令 / URL：`【install_command】` / `【repository_url】`

## aspect_and_output

4:5 竖版社交卡；输出 PNG 位图与本 Prompt。正式文件名 `02-featured-skill-deep-dive.png`，候选用 `v1/v2`，不得覆盖旧版本。

## constraints_and_avoid

不得复述第一页全部能力卡，不生成未经来源支持的效果、版本、数量、测试结果或客户评价；不得用“沿用上一张，其余不变”代替本页 Prompt；文字空间不足时优先保留输入、工作流、交付物、验收和 CTA。
