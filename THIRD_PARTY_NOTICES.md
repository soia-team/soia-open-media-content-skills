# THIRD_PARTY_NOTICES

> Last updated: 2026-07-22
> This file records third-party code adaptations and design references used by skills in this repository.

## Code adaptations

| Upstream | License | Used by | Relationship |
|---|---|---|---|
| [wshuyi/x-article-publisher-skill](https://github.com/wshuyi/x-article-publisher-skill) | MIT (copy: `licenses/wshuyi-x-article-publisher-skill-LICENSE.txt`) | `soia-media-publish-x-article/scripts/parse_x_article.py` | Markdown parsing, `block_index` location, and HTML conversion logic were adapted from upstream `parse_markdown.py`; the adapted file retains provenance. The clipboard automation is an independent implementation. |

## Workflow design references

| Upstream | License snapshot | Used by | Relationship |
|---|---|---|---|
| [mcncarl/yichen-skills — yichen-x-article-draft-uploader](https://github.com/mcncarl/yichen-skills/tree/main/yichen-x-article-draft-uploader) | Personal Learning and Non-Commercial Use License | `soia-media-publish-x-article` | Workflow-only reference for stopping when a cover is missing, mechanical post-upload checks, and saving drafts without publishing. No upstream code was copied. |

## Maintenance

- Recheck upstream licenses before reuse or redistribution.
- Projects without a permissive license may be used only within the reference boundary stated above.
- Any new code adaptation must retain provenance and add the upstream license copy under `licenses/`.
