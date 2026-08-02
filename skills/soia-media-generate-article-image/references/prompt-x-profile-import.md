# X profile Prompt 导入契约

`soia-pkm-clip-x-profile` 负责有限窗口采集、时间/关键词/主题筛选、研究摘要和来源证据整理；本技能只在客户明确选择 image 路由时，把已编译 Prompt 重新拆成可复用的 image 视觉系统，再变成位图并完成视觉验收。两者之间的交付物是 run bundle 中的 `image-prompts.yml` 与 `prompts/*.md`，二次编译产物由 `scripts/import_x_profile_prompt_deck.py` 生成。

## 输入

输入索引至少包含：

- `source_profile`、`source_status_id`、`source_url`；
- `selection.filters`：时间、关键词、分类、媒体/ALT 和模型条件；
- `source_prompt` 原文（优先图片 ALT，缺失时为帖子正文）；
- `composition_axes`：`family`、`use_case`、`information_structure`、`visual_mechanism`、`aesthetic_system`、`text_strategy`、`model_adapter`、`aspect`；
- 每条 Prompt 的七个 blocks：`source_grounding`、`primary_task`、`composition_and_layout`、`visual_style_and_materials`、`exact_text`、`aspect_and_output`、`constraints_and_avoid`。

## 导入规则

1. 先核对 `manifest.yml` 的窗口、时间/关键词条件和 `selected` 数量；“最新 100 条”不是账号全量。
2. 只读取当前筛选集里 `prompt_file` 存在的记录；若上游明确要求 GPT2，再额外要求 `is_gpt2=true`。没有来源 Prompt 或 ALT 证据时标记 `BLOCKED`，不自行补写。
3. `GPT2` 只映射为 `model_adapter=external_gpt_image_label`；非 GPT2 来源可以保持 `auto`。它描述作者的模型线索，不限制本技能可用的 imagegen provider，也不默认画在图片里。
4. 组合轴是可复用查询结果，不是新增 preset。若客户说“换成字体蒙版/巨字留白/模块网格”，只替换对应轴并保留来源事实。
5. X source route 可以在不同 family 上统一使用 `hybrid_exact_text`，但这只是执行策略，不是新 preset；生成后必须执行 `view_image`、比例检查和需要时的 OCR。失败重生要使用新版本文件名，不覆盖原始来源证据。

## 二次编译（必须）

不要把上游 `prompts/*.md` 当成 image 技能最终 Prompt，也不要只把它们复制到交付目录。运行：

```bash
python3 scripts/import_x_profile_prompt_deck.py \
  --input <x-profile-run>/image-prompts.yml \
  --output <image-output>/x-profile-evolution
```

编译器按 [X 提示词进化契约](x-profile-prompt-evolution.yml) 输出：

- `base_visual_system`：稳定的字体、网格、色彩、材质、光线和阅读顺序；
- `topic_seasoning`：本条来源的主题、对象、事实和用途；
- `series_variables`：系列中可变化的 2–4 个轴；
- `render_plan`：位图后端、比例、文字策略和验收门。

缺少来源证据或七个 canonical blocks 时必须 `BLOCKED`；编译通过仍不等于位图通过。

## 最小导入示例

```text
source=x-profile-export
input=<run-dir>/image-prompts.yml
item=prompts/001-morning_city-<status-id>.md
family=morning_city
visual_mechanism=typographic_mask
model_adapter=external_gpt_image_label
```

本契约不允许 image 技能直接抓取账号、调用登录态或绕过 X provider；采集失败应回到 `soia-pkm-clip-x-profile`，而不是在生图阶段隐式补抓。
