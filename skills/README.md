# SOIA Open Skills Catalog

> Generated from `skills/*/SKILL.md` and optional `agents/openai.yaml`.
> Do not edit by hand. Run `python3 scripts/generate_skill_catalog.py`.
> Discoverable by `npx skills add soia-team/soia-open-media-content-skills -l`: 6 skills.

## Source Fields

- `SKILL.md` is the canonical cross-agent instruction file. Capabilities, dependencies, setup, workflow steps, logs, and completion summaries must live there.
- `agents/openai.yaml` is optional UI/catalog metadata for OpenAI/Codex-style surfaces and SOIA registry display: `display_name`, `short_description`, and `default_prompt`.
- Claude Code and generic skills.sh-compatible agents must be assumed to consume `SKILL.md`; do not put required workflow steps only in `agents/openai.yaml`.
- Legacy `metadata.json` files are not used to generate this catalog.

## Media

| Skill | Description | Default Prompt |
|---|---|---|
| [`soia-media-compose-article-draft`](./soia-media-compose-article-draft/) | 把 distill 提炼出的观点写成成文草稿，生成可继续交给 publish-* 家族的文章。可指定公众号/知乎/随笔风格 | Use soia-media-compose-article-draft: 把 distill 提炼出的观点写成成文草稿，后续按目标平台交给 publish-* 家族。 |
| [`soia-media-cover-image`](./soia-media-cover-image/) | 为公众号/X/小红书文章生成封面图。五维参数（type/palette/rendering/text/mood），公众号产出接 soia-media-publish-wechat-draft --cover。后端仅用 codex CLI 内置生图，探测不到就询问客户，绝不静默降级、绝不用代码渲染冒充位图 | Use soia-media-cover-image: 为公众号/X/小红书文章生成封面图；公众号产出接 soia-media-publish-wechat-draft --cover。 |
| [`soia-media-publish-rednote-card`](./soia-media-publish-rednote-card/) | 把文章改写成小红书 rednote 笔记：标题、3–5 段短文、标签和配图建议。 | Use soia-media-publish-rednote-card: 把这篇文章改成小红书笔记，给我标题、短文、话题标签和配图建议。 |
| [`soia-media-publish-wechat-draft`](./soia-media-publish-wechat-draft/) | 把文章排版成符合微信公众号限制的 HTML，校验后推入草稿箱；只建草稿，绝不自动群发。 | Use soia-media-publish-wechat-draft: 把这篇文章排版成公众号文章，校验后推到草稿箱。 |
| [`soia-media-publish-x-article`](./soia-media-publish-x-article/) | 把 Markdown 成文直传 X Articles 草稿箱：富文本粘贴、封面与正文图按原位插入，只存草稿绝不发布。 | Use soia-media-publish-x-article: 把这篇 Markdown 长文上传到 X Articles 草稿箱，封面用文首第一张图，校验通过后给我草稿 URL。 |
| [`soia-media-publish-x-thread`](./soia-media-publish-x-thread/) | 把成文草稿拆成 ≤280 字符的 X thread；可选宿主无关 Playwright 脚本直填存草稿，明确授权才发布，不接 X API。 | Use soia-media-publish-x-thread: 把这篇文章拆成带 (1/N) 编号的 X 推文串，保留链接和代码完整性。 |

## Registry Export

Generate v7 SOIA registry manifests from the same sources when needed:

```bash
python3 scripts/generate_skill_catalog.py --registry-out <soia-repo>/runtime/registry/skills
```
