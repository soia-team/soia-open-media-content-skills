# SOIA New Media Content Skills

Reusable AI skills for article writing, cover generation, content adaptation, and draft delivery across WeChat, X, and Rednote.

## Skills

| Skill | Summary |
|---|---|
| `soia-media-compose-article-draft` | Turn distilled user ideas into an editable article draft ready for downstream publishing. |
| `soia-media-cover-image` | Generate cover images in multiple aspect ratios for WeChat, X, and Rednote articles. |
| `soia-media-publish-rednote-card` | Rewrite an article as Rednote titles, body copy, tags, and image suggestions for manual publishing. |
| `soia-media-publish-wechat-draft` | Format an article as WeChat-compatible HTML and upload it as a draft without broadcasting. |
| `soia-media-publish-x-article` | Fill and mechanically verify an X Articles draft from Markdown without publishing it. |
| `soia-media-publish-x-thread` | Rewrite an article as a length-compliant X thread, producing text by default. |

## Installation

Replace `<skill>` with a skill name from the table above:

```bash
npx skills add soia-team/soia-open-media-content-skills -g -a '*' -s <skill> -y
```

For example, install the article drafting skill:

```bash
npx skills add soia-team/soia-open-media-content-skills -g -a '*' -s soia-media-compose-article-draft -y
```

## Ecosystem

See [soia-team/soia-open-skills](https://github.com/soia-team/soia-open-skills) for the canonical specifications and complete ecosystem catalog.

## License

MIT License. See [LICENSE](./LICENSE).
