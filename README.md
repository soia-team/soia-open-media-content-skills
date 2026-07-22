# SOIA 新媒体内容技能库

新媒体：写作、封面图片、公众号/X/小红书发布（soia-media-*）

## 域说明

本仓负责 `media` 域，技能名称统一使用 `soia-media-*` 前缀。

## 安装

```bash
npx skills add soia-team/soia-open-media-content-skills -g -a '*' -s <skill> -y
```

## 技能清单

| 技能 | 用途 |
|---|---|
| `soia-media-compose-article-draft` | 把提炼出的观点写成可发布的文章草稿 |
| `soia-media-cover-image` | 为公众号、X 和小红书文章生成封面图 |
| `soia-media-publish-wechat-draft` | 排版并推入微信公众号草稿箱，不自动群发 |
| `soia-media-publish-x-thread` | 把文章改写成 X thread，可选存草稿或经确认后发布 |
| `soia-media-publish-x-article` | 把 Markdown 长文写入 X Articles 草稿箱，绝不自动发布 |
| `soia-media-publish-rednote-card` | 把文章改写成供人工发布的小红书笔记文案 |

本仓属于 SOIA 技能生态，规范真源见 [soia-team/soia-open-skills](https://github.com/soia-team/soia-open-skills)。
