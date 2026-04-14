# Family Template Sharing Tiers

Use this note to decide whether a publisher-family template can be reused across multiple journals in the same family.

## Core Rule

- A family template may usually be reused as the drafting and preview baseline for sibling journals.
- A family template should not be treated as the final submission contract for every sibling journal without checking the live journal-specific author guide.
- When a journal-specific rule conflicts with the family baseline, the journal wins.

## Tiers

### Tier 1: Reusable Local Template Package

These families have a real local package or class root in `assets/official-templates/` and can be reused across sibling journals as the baseline manuscript source.

| Family | Local Asset Root | Share As Baseline? | Boundary |
|---|---|---|---|
| `ieee` | `assets/official-templates/ieee/template-package` | yes | Keep `IEEEtran` as the baseline, then tighten title-specific author-page rules. |
| `acm` | `assets/official-templates/acm/template-package` | yes | Keep `acmart` as the baseline, then adjust journal code, metadata, and review/submission mode. |
| `acs` | `assets/official-templates/acs/template-package` | yes | Keep `achemso` as the baseline, then adjust article mode and chemistry-specific front matter. |
| `aip` | `assets/official-templates/aip/template-package` | yes | Keep `revtex4-2` as the baseline, then adjust journal option and article constraints. |
| `copernicus` | `assets/official-templates/copernicus/template-package` | yes | Keep the Copernicus package as the baseline, then confirm journal-specific article metadata and bibliography rules. |
| `elsevier` | `assets/official-templates/elsevier/template-package` | yes | Keep `elsarticle` or CAS as the baseline, then match the target journal's citation mode and front matter. |
| `siam` | `assets/official-templates/siam/template-package` | yes | Keep the SIAM package as the baseline, then confirm the target title's current author instructions. |
| `springer` | `assets/official-templates/springer/template-package` | yes | Keep `sn-jnl` as the baseline, then match the target title's style option and author guide. |
| `frontiers` | `assets/official-templates/frontiers/template-package` | yes | Keep the Frontiers package as the baseline, then confirm specialty and declaration rules for the target title. |
| `plos` | `assets/official-templates/plos/template-package` | yes | Keep the PLOS manuscript package as the baseline, then confirm title-specific reporting rules. |
| `wiley` | `assets/official-templates/wiley/template-package` | yes, with caution | Local assets exist, but this family is not yet wired into the verified rendering flow. |
| `iop` | `assets/official-templates/iop/template-package` | yes, with caution | IOP exposes a basic official journal article template package, but some titles do not require authors to submit in that exact class format. |

### Tier 2: Reusable Official Family Class Without A Local Package Root

These families are suitable for family-level reuse because the official class path is stable, but the repository has not yet materialized a publisher-side package root under `assets/official-templates/`.

| Family | Share As Baseline? | Boundary |
|---|---|---|
| _none currently_ | | |

### Tier 3: Guide-Only Or Blocked

These families are not yet ready to be treated as reusable local template-package baselines in this repository.

| Family | Current State | Boundary |
|---|---|---|
| `mdpi` | blocked / partial | Journal guidance exists, but this repository does not yet have a reusable local MDPI package path suitable for honest family-wide verification. |

## Practical Use

1. If the exact journal exists and has `verification.yaml`, use that journal first.
2. If the exact journal does not exist, start from the family tier listed here.
3. If the family is Tier 1 or Tier 2, reuse the family template as the draft baseline.
4. Before calling anything submission-ready, re-check the target journal's live author page for journal-specific differences.
