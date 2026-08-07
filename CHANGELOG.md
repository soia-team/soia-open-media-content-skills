# Changelog

本文件由 soia-meta-skill-release 在每次正式发版时自动更新，与 GitHub Release 同源；
更早的版本演进见 git 提交历史与 GitHub Releases。

## v1.12.0 — 2026-08-07

generate-article-image 3.17.1：imagegen 默认路由（codex gpt-image-2 派发）、rednote 3:4、封面角色约束、两层契约澄清、prompt 排版说明分离规则；rednote-card 2.1.0：网页端发布实操

## 新增
- feat(generate-article-image): imagegen provider 路由、rednote 3:4、封面角色约束与两层契约澄清 (#64)
- feat(rednote): 补齐网页端发布实操——由文案技能扩展为可代客户发布 (#63)

## 修复
- fix(generate-article-image): imagegen prompt 排版说明与逐字文字分离规则 (#65)

## 维护
- chore(release): feat 在列,版本列车提为 next-minor
- chore(release): open next train after release

## v1.11.0 — 2026-08-06

安装章节三宿主覆盖、config 归位 assets

## 新增
- feat(generate-article-image): add html_render path and source-id convention (v3.16.0) (#48)

## 修复
- fix(generate-article-image): clarify Cornell page marker style (#54)

## 维护
- chore(release): feat 在列,版本列车提为 next-minor
- chore(skills): config.example.yml 归位到 assets/ (#60)
- docs(skills): 安装章节补齐三个一等宿主 (#59)
- docs(agents): branch off main; releases fast-forward dev onto main (#58)
- chore(release): switch dev train to patch level (#56)
- chore(release): reopen version train (missed after last release) (#55)

## v1.10.0 — 2026-08-03

康奈尔笔记图支持多页路由

## 新增
- feat(generate-article-image): 康奈尔笔记图支持多页路由 (#50)
- feat(generate-article-image): add html_render path and source-id convention (v3.16.0)
- feat(image): X-profile prompt deck contracts and audit tooling (#39)
- feat(image): X-profile prompt deck contracts and audit tooling
- feat(image): compile X prompt decks into reusable skill layers

## 修复
- fix(media): preserve brand logo accent and lockups (#47)
- fix(tests): restore brand-logo assertions lost in sync resolution (#45)
- fix(image): keep logo prompt references inside skill

## 维护
- docs(changelog): seed with current release baseline (#49)
- docs(agents): dev-branch integration workflow (#46)
- chore(release): open next train after v1.9.0 (#44)
- release: finalize v1.9.0 (drop -SNAPSHOT) (#41)
- chore(release): open dev branch — audit on dev, version train 1.9.0-SNAPSHOT

## 其他
- Revert "feat(generate-article-image): add html_render path and source-id convention (v3.16.0)"

## v1.9.0 — 2026-08-02

X-profile prompt deck：可执行 prompt 块、前向矩阵与审计工具落地。
