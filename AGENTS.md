# AGENTS.md - soia-open-media-content-skills

Rules for all AI agents editing this repository.

## Repository Purpose

`soia-open-media-content-skills` publishes reusable `soia-media-*` skills for the media domain. Every committed skill must be safe for users who do not share the maintainer's machine, accounts, private data, or internal workspace.

## Safety Rules

- No real API keys, tokens, cookies, session strings, passwords, account ids,
  private `config.yml`, or `.env` files.
- No maintainer-specific absolute paths such as `/Users/<name>/...`.
- No private family, home, health, finance, or learner profile context.
- Put user-specific behavior behind CLI args, env vars, or skill-specific
  user-owned config files outside this repo:
  `~/.config/soia-skills/<skill-name>/config.yml`.
- Repository examples must use placeholders such as `<path>`, `<repo>`, and
  `<YOUR_KEY>`.

## Validation

Before committing skill changes, run:

```bash
python3 -m pip install -r requirements-dev.txt  # once per machine; the audit uses PyYAML
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/generate_skill_catalog.py --check
python3 scripts/audit_skills.py
git diff --check
```

For changed skills, also run a skill validator when one is available. On Codex
machines, this helper is commonly available:

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/<skill-name>
```

Final installation acceptance must use the pushed remote repo, not a local
checkout copied into an agent target:

```bash
npx skills add soia-team/soia-open-media-content-skills -l --full-depth
npx skills add soia-team/soia-open-media-content-skills -g --all
```

## 维护本仓技能

技能契约、调试安装、新增/改名/拆分/删除的完整流程，以及插件市场发布步骤，统一见
元仓的 [CONTRIBUTING.md](https://github.com/soia-team/soia-open-skills/blob/main/CONTRIBUTING.md)。
本文件只保留本仓特有的用途、边界与验证命令。

## Git Workflow

### Protected branches — ABSOLUTE prohibition on direct push

`dev` and `main` are protected. **Direct push to either branch is FORBIDDEN,
even if the remote does not technically block it.** Both branches enforce a
required `audit` status check; bypassing it corrupts governance history and
must never happen.

**If you are an AI agent**, follow these steps exactly — no shortcuts:

1. Create a feature branch from `dev`:
   ```bash
   git checkout dev && git pull
   git checkout -b feat/<short-description>
   ```
2. Make your commits on the feature branch.
3. Push the feature branch to origin:
   ```bash
   git push origin feat/<short-description>
   ```
4. Open a PR targeting `dev` using `gh pr create --base dev`.
5. Wait for `audit` CI to pass; do **not** merge yourself.

**Never run `git push origin dev` or `git push origin main` from a feature or
working branch.** If you find yourself about to do this, stop and open a PR
instead. Bypassing branch protection — even accidentally — must be reported to
the maintainer.

### Branch purpose

- `dev` is the default integration branch: all feature PRs merge here after
  `audit` passes.
- `main` always equals the latest formal release and only accepts release PRs
  from `dev`, driven by `soia-meta-skill-release`. Never open feature PRs
  against `main`.
- Plugin manifests on `dev` carry a `-SNAPSHOT` version naming the next release
  target. Do not change manifest versions in feature PRs; versions move only in
  release PRs.
