# SOIA 新媒体内容技能库

[English](README.en.md) · 中文

从观点到多平台发布：成文、配图、按各平台规矩排版——只进草稿箱，绝不替你按发送。

## 这是什么

`soia-open-media-content-skills` 负责内容生产的最后一公里：

```text
你的观点 / 素材
    ↓
成文草稿（compose）
    ↓
配图（封面 / 小结卡 / 视觉隐喻海报）
    ↓
分平台改写（公众号 HTML · X thread · X Article · 小红书笔记）
    ↓
草稿箱（等你人工确认后发布）
```

**发布权始终在你手里**：公众号只建草稿绝不群发，X 只存草稿不点发布，小红书只产出文本由你手动贴。

### 适合什么场景

- 「把这些观点写成一篇文章。」
- 「给这篇文章配张封面。」
- 「排版成公众号，推到草稿箱。」
- 「拆成 X thread，每条别超字数。」
- 「改写成小红书笔记，带话题标签。」

### 不负责什么

- 不自动发布。所有发布类技能止步于草稿箱，最后一步必须由你在平台上确认。
- 不替你编造事实。配图与成文都要求先给出事实清单，不确定的信息会标注「未核实」而不是猜。
- 不做选题与观点提炼。那在 [soia-open-pkm-vault-skills](https://github.com/soia-team/soia-open-pkm-vault-skills) 的 distill 系列。
- 不接管你的账号。各平台登录态由官方流程持有，不进仓库、不进日志。

## 从哪里开始

典型流程是「成文 → 配图 → 分平台发布」：

| 你要做的 | 用这个 | 完成标准 |
|---|---|---|
| 把观点写成文章 | `soia-media-compose-article-draft` | 可继续交给发布技能的成文草稿 |
| 生成配图 | `soia-media-generate-article-image` | Prompt 落盘、位图验收通过 |
| 发公众号 | `soia-media-publish-wechat-draft` | 内联样式 HTML 进草稿箱，未群发 |
| 发 X | `soia-media-publish-x-thread` 或 `-x-article` | 草稿已存，未点发布 |
| 发小红书 | `soia-media-publish-rednote-card` | 标题、正文、标签、配图建议齐全 |

带 🟡 的技能需要对应平台的登录态或生图能力，技能会在执行前检查。

## 技能清单

> **开箱可用**：✅ 装完即可使用 · 🟡 还需申请 API key 或完成第三方登录

| 技能 | 一句话职责 | 开箱可用 |
|---|---|---|
| `soia-media-compose-article-draft` | 把 distill 提炼出的观点写成成文草稿。 | ✅ |
| `soia-media-generate-article-image` | 为文章生成封面、小结卡、笔记图或技能库宣传卡，含事实清单与位图验收。 | 🟡 |
| `soia-media-publish-rednote-card` | 改写成小红书笔记：吸睛标题、短段落、话题标签与配图建议。 | ✅ |
| `soia-media-publish-wechat-draft` | 排版成公众号内联样式 HTML 并推入草稿箱，只建草稿绝不群发。 | 🟡 |
| `soia-media-publish-x-article` | 将 Markdown 成文上传到 X Articles 草稿箱并校验格式，只保存草稿。 | 🟡 |
| `soia-media-publish-x-thread` | 拆成带编号、符合字数限制的 X thread，授权后才存草稿。 | 🟡 |

## 触发词映射

装完直接用自然语言说话即可，Agent 按下表触发对应技能（完整触发词见各技能 `SKILL.md` 的 `description`）：

| 你说 | 触发技能 |
|---|---|
| `把这些观点写成一篇` / `把 X 主题写成文章` / `compose 这篇` / `写成草稿` | `soia-media-compose-article-draft` |
| `生成文章图片` / `正文小结图` / `康奈尔笔记图` / `技能库宣传图` | `soia-media-generate-article-image` |
| `发成小红书` / `小红书笔记` / `改成 rednote` / `rednote 这篇` | `soia-media-publish-rednote-card` |
| `把这篇发成公众号` / `排版这篇公众号` / `推到公众号草稿箱` / `公众号 draft` | `soia-media-publish-wechat-draft` |
| `发成 X Article` / `推到 X 文章草稿箱` | `soia-media-publish-x-article` |
| `发成 X thread` / `拆成推文串` / `thread 这篇` | `soia-media-publish-x-thread` |

## 安装

推荐装整个领域插件，一次装好本仓全部技能：

```bash
claude plugin marketplace add soia-team/soia-open-skills
```

```bash
claude plugin install soia-media-content@soia
```

Codex 用户：

```bash
codex plugin marketplace add soia-team/soia-open-skills
codex plugin add soia-media-content@soia
```

只要单个技能时可用 npx 路线。注意技能会落进共享真源 `~/.agents/skills`；
若同时装了插件，同一技能会出现两份索引且各自漂移，建议二选一：

```bash
npx skills add soia-team/soia-open-media-content-skills -g -a '*' -s <技能名> -y
```

## 验证与贡献

改动技能后，提交前跑：

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/generate_skill_catalog.py --check
python3 scripts/audit_skills.py --strict
```

贡献流程、技能契约与发布步骤见元仓
[CONTRIBUTING.md](https://github.com/soia-team/soia-open-skills/blob/main/CONTRIBUTING.md)。

## 生态导航

规范真源、全生态技能目录与安装指南见 [soia-team/soia-open-skills](https://github.com/soia-team/soia-open-skills)。
维护本仓技能的完整流程见 [CONTRIBUTING.md](https://github.com/soia-team/soia-open-skills/blob/main/CONTRIBUTING.md)。

## License

MIT License — see [LICENSE](./LICENSE).
