# SOIA 新媒体内容技能库

覆盖文章写作、封面生成与公众号、X、小红书内容适配和草稿发布的可复用 AI 技能集合。

## 技能目录

| 技能名 | 一句话简介 |
|---|---|
| `soia-media-compose-article-draft` | 将提炼后的用户观点组织成可继续编辑和发布的文章草稿。 |
| `soia-media-cover-image` | 为公众号、X 和小红书文章生成多种比例的封面图。 |
| `soia-media-publish-rednote-card` | 将文章草稿改写为供人工发布的小红书标题、正文、标签与配图建议。 |
| `soia-media-publish-wechat-draft` | 将文章排版为公众号兼容 HTML 并推入草稿箱，不自动群发。 |
| `soia-media-publish-x-article` | 将 Markdown 长文写入 X Articles 草稿箱并完成机械校验，不自动发布。 |
| `soia-media-publish-x-thread` | 将文章改写为符合长度约束的 X thread，默认仅生成文本。 |

## 安装

将 `<技能>` 替换为上表中的技能名：

```bash
npx skills add soia-team/soia-open-media-content-skills -g -a '*' -s <技能> -y
```

例如安装文章起草技能：

```bash
npx skills add soia-team/soia-open-media-content-skills -g -a '*' -s soia-media-compose-article-draft -y
```

## 生态导航

规范真源与全生态目录见 [soia-team/soia-open-skills](https://github.com/soia-team/soia-open-skills)。

## License

MIT License，详见 [LICENSE](./LICENSE)。
