# SOIA Social Content Skills

[中文](README.md) · English

From a point of view to multi-platform publishing: draft, illustrate, reformat per platform — drafts only, never auto-send.

## What this is

`soia-open-media-content-skills` covers the last mile of content production:

```text
Your point of view / material
    ↓
Article draft (compose)
    ↓
Imagery (cover / summary card / metaphor poster)
    ↓
Per-platform rewrite (WeChat HTML · X thread · X Article · Rednote note)
    ↓
Draft box (you confirm and publish)
```

**Publishing stays in your hands**: WeChat only creates drafts and never mass-sends, X only saves drafts and never clicks publish, Rednote produces text you paste yourself.

### When to use it

- "Write these points up as an article."
- "Generate a cover image for this piece."
- "Format it for WeChat and push it to the draft box."
- "Split it into an X thread, respect the character limit."
- "Rewrite it as a Rednote note with hashtags."

### What it does not do

- Does not publish. Every publishing skill stops at the draft box; the final step is yours on the platform.
- Does not invent facts. Both imagery and prose require a fact list first; anything uncertain is marked "unverified" rather than guessed.
- Does not pick topics or distill opinions — that is the distill family in [soia-open-pkm-vault-skills](https://github.com/soia-team/soia-open-pkm-vault-skills).
- Does not take over your accounts. Platform sessions stay in their official flows — never in the repo or logs.

## Where to start

The typical flow is compose → illustrate → publish per platform:

| Your task | Use | Done when |
|---|---|---|
| Write points up as an article | `soia-media-compose-article-draft` | A draft ready for the publishing skills |
| Generate imagery | `soia-media-generate-article-image` | Prompt persisted, bitmap acceptance passed |
| Publish to WeChat | `soia-media-publish-wechat-draft` | Inline-styled HTML in the draft box, not sent |
| Publish to X | `soia-media-publish-x-thread` or `-x-article` | Draft saved, publish not clicked |
| Publish to Rednote | `soia-media-publish-rednote-card` | Title, body, tags, and image suggestions complete |

Skills marked 🟡 need a platform session or image-generation capability; each checks before running.

## Skill catalog

> **Ready to use**: ✅ works right after install · 🟡 needs an API key or a third-party login first

| Skill | Responsibility | Ready to use |
|---|---|---|
| `soia-media-compose-article-draft` | Turn distilled opinions into a finished article draft ready for the publishing skills. | ✅ |
| `soia-media-generate-article-image` | Generate covers, summary cards, note graphics, or semantically dense catalog promo cards, with deep source grounding, a two-slide recommendation narrative, and bitmap acceptance. | 🟡 |
| `soia-media-publish-rednote-card` | Rewrite a draft as a Rednote note: catchy title, short paragraphs, hashtags, and image suggestions. | ✅ |
| `soia-media-publish-wechat-draft` | Format as inline-styled WeChat HTML and push to the draft box — drafts only, never mass-sent. | 🟡 |
| `soia-media-publish-x-article` | Upload a Markdown draft to X Articles, validate formatting, and save as a draft only. | 🟡 |
| `soia-media-publish-x-thread` | Split a draft into a numbered, length-compliant X thread; saves a draft only when authorized. | 🟡 |

## Trigger phrases

Once installed, just speak naturally — the agent routes to a skill by these phrases (the full trigger list lives in each skill's `SKILL.md` `description`).

> Trigger phrases are listed in the language the skill actually matches on. Most are Chinese because that is what these skills were written to recognize; describing the same intent in English works too — the agent matches on meaning, not on the literal string.

| You say | Skill |
|---|---|
| `把这些观点写成一篇` / `把 X 主题写成文章` / `compose 这篇` / `写成草稿` | `soia-media-compose-article-draft` |
| `生成文章图片` / `正文小结图` / `康奈尔笔记图` / `技能库宣传图` | `soia-media-generate-article-image` |
| `发成小红书` / `小红书笔记` / `改成 rednote` / `rednote 这篇` | `soia-media-publish-rednote-card` |
| `把这篇发成公众号` / `排版这篇公众号` / `推到公众号草稿箱` / `公众号 draft` | `soia-media-publish-wechat-draft` |
| `发成 X Article` / `推到 X 文章草稿箱` | `soia-media-publish-x-article` |
| `发成 X thread` / `拆成推文串` / `thread 这篇` | `soia-media-publish-x-thread` |

## Install

Installing the whole domain plugin is recommended — it brings every skill in this repo:

```bash
claude plugin marketplace add soia-team/soia-open-skills
```

```bash
claude plugin install soia-media-content@soia
```

For Codex:

```bash
codex plugin marketplace add soia-team/soia-open-skills
codex plugin add soia-media-content@soia
```

For a single skill you can use the npx route. Note the skill lands in the shared
source `~/.agents/skills`; if the plugin is installed too, the same skill shows up
twice and the two copies drift apart — pick one:

```bash
npx skills add soia-team/soia-open-media-content-skills -g -a '*' -s <skill-name> -y
```

## Validate & contribute

After changing a skill, run before committing:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/generate_skill_catalog.py --check
python3 scripts/audit_skills.py --strict
```

Contribution flow, the skill contract, and release steps are in the portal's
[CONTRIBUTING.md](https://github.com/soia-team/soia-open-skills/blob/main/CONTRIBUTING.md).

## Ecosystem

Specifications, the full ecosystem catalog, and install guides live in [soia-team/soia-open-skills](https://github.com/soia-team/soia-open-skills).
The full maintenance workflow is in [CONTRIBUTING.md](https://github.com/soia-team/soia-open-skills/blob/main/CONTRIBUTING.md).

## License

MIT License — see [LICENSE](./LICENSE).
