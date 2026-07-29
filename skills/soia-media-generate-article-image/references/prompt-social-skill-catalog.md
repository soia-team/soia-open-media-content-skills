# Prompt template: Social skill catalog

## 适用场景

- `image_type: social_card | carousel`
- `preset: social_skill_catalog`
- 开源技能库、插件集合、产品能力清单的朋友圈或小红书宣传图
- 需要同时保证主视觉吸引力、技能数量准确、安装命令可复制和系列一致性

本模板是两阶段工作流：imagegen 只生成无文字主视觉；技能名称、数量、命令、URL、
二维码与品牌标识必须由确定性排版工具合成。不得要求扩散模型渲染这些字段。

## 阶段一：事实清单

先运行：

```bash
python3 scripts/build_social_catalog_facts.py \
  --repo <skill-repo> \
  --repository <owner/repo> \
  --claim-mode <total|featured> \
  --cta-mode <all|featured> \
  --output <output-dir>/facts.yml
```

- `total` 必须展示仓库全部技能，文案使用“当前已提供 N 个技能”。
- `featured` 只展示选中技能，文案使用“精选 N 个技能”，不得暗示是仓库总数。
- `cta_mode=featured` 时必须指定一个真实存在的技能，安装命令由脚本生成。
- 简短展示名优先读取各技能的 `agents/openai.yaml`；需要中文短名时另加 `--label-map <label-map.yml>`，提供“技能名 → 展示名”映射。脚本拒绝不存在的技能或空标签。
- `facts.yml` 是技能数量、名称、版本、命令与仓库地址的唯一真源；图片文案不得另写一份。
- 多仓系列使用 [social-card-batch.example.yml](social-card-batch.example.yml) 明确 `include` / `exclude`，运行 `build_social_catalog_batch.py` 生成 `batch-facts.yml`；发布范围必须与批次清单完全一致。

## 阶段二：主视觉 Prompt

```text
Use case: productivity-visual
Asset type: text-free hero art for a social skill-catalog card

Primary request:
为【技能库主题】生成一个适合 4:5 社交媒体卡片的主视觉插画。只表达【一个核心价值隐喻】，主体可被裁入封面或重点页；不要生成整张海报，不要排版能力网格。

Composition:
- 主体集中在画面一侧或中央，预留稳定的标题与卡片排版空间
- 缩略图下仍有清晰轮廓，不依赖细小细节表达主题
- 同一 series_id 锁定材质、光线、边缘、透视与品牌色
- 同批次允许改变主体隐喻、构图方向和局部强调色，避免每张只是换字

Style:
- 清晰、可信、面向技术与生产力用户
- 使用【品牌色】及一个辅助强调色
- 质感可为克制 3D、编辑式科技插画或经确认的品牌语言

Text and brand safety:
- 不出现任何文字、字母、数字、命令、URL、二维码、Logo 或水印
- 不临摹平台或开源项目 Logo；品牌资产在确定性合成阶段加入

Avoid:
完整信息图、能力网格、安装命令、随机中文、伪二维码、伪 Logo、过量光效、多个主要隐喻、电商促销模板感。
```

## 阶段三：确定性排版

读取 [social-card-contract.yml](social-card-contract.yml)，使用可复现的确定性图形工具完成：

1. 把 `facts.yml` 的 `claim_text`、技能名称、安装命令和仓库 URL 逐字排入版面。
2. 只使用客户提供或来源明确的品牌资产；不得让 imagegen 伪造 Logo。
3. 二维码必须由真实 URL 编码生成；不得使用生图模型生成二维码。
4. `slide_count` 可为 `1`、`2`、`3` 或 `auto`，不是固定四页：
   - 1 张：同页承担 `cover + catalog + cta`，最多 4 项。
   - 2 张：推荐“封面＋能力概览 / 重点能力＋CTA”，每张最多 6 项。
   - 3 张：推荐“封面 / 能力清单 / 重点能力＋CTA”，每张最多 6 项。
   - `auto`：优先选择 2–3 张；技能总数仍放不下时继续增加能力页，不缩小字号硬塞。
5. `cover`、`catalog`、`cta` 是必需语义角色，`highlight` 可选；多个角色允许由同一张图承担，manifest 用 `roles` 数组记录。
6. 朋友圈单图最多展示 4 项能力；更多能力改用多图或标为“精选”。
7. 同一 `series_id` 锁定字体、字号阶梯、圆角、间距、标题区、CTA 区和品牌色；至少改变主体、构图、局部配色中的两项，避免批次缩略图同质化。
8. 最终输出 PNG/JPG；SVG、HTML 或画布文件只能作为可复现的中间源，不冒充最终交付位图。

## 阶段四：验证

1. 在目标平台缩略尺寸检查标题和价值主张；小字只有打开图片后才可读时，不得承担首屏关键信息。
2. 对确定性文字执行 OCR 或逐字段机械提取，并写入 delivery manifest 的 `observed.exact_text`。
3. 用二维码解码器读取终稿二维码，把结果写入 `quality.qr_decoded_target`。
4. 实际 `view_image` 检查主视觉、留白、层级和系列差异。
5. 运行：

```bash
python3 scripts/validate_social_catalog_delivery.py \
  --facts <output-dir>/facts.yml \
  --delivery <output-dir>/manifest.yml
```

只有脚本返回 `PASS`，且位图已实际查看，才能写“比对通过”。
