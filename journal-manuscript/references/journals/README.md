# Journal Folders

This directory separates journal template requirements by family at the top level. Child journal folders now live inside their family folder.

## Coverage Snapshot

- 28 family folders
- 87 journal folders
- 115 `official_preview` sets
- 66 verification records
- 65 verified targets plus 1 blocked target

## How To Navigate

- Open `catalog.md` for the full index.
- Open `family-template-sharing-tiers.md` when you need the family-level reuse boundary first.
- Start with a family folder when you only know the publisher or template family.
- Open a specific journal folder under its family directory when the target venue is known.
- Use `custom-journal/` when the target venue does not yet have its own folder.

## Verification Assets

- `profile.md`: narrative profile and editing guidance
- `official_preview.*`: canonical rendered preview asset for every family and journal folder
- `verification.yaml`: structured verification boundary, source, and status
- `layout-checklist.md`: explicit remaining checks for journals that require them
- `slug-paths.json`: lookup table from flat slug to nested family path
- `family-template-sharing-tiers.*`: explicit policy for whether a family template may be shared across sibling journals

## Representative Families

- `aaas/`: AAAS Family
- `acm/`: ACM Family
- `acs/`: ACS Family
- `aip/`: AIP Family
- `bmc/`: BMC Family
- `cambridge/`: Cambridge Family
- `cell-press/`: Cell Press Family
- `copernicus/`: Copernicus Family
- `custom-journal/`: Custom Journal Family
- `de-gruyter/`: De Gruyter Family
- `elsevier/`: Elsevier Family
- `emerald/`: Emerald Family
- `frontiers/`: Frontiers Family
- `hindawi/`: Hindawi Family

## Maintenance Rule

- When a journal becomes important enough for repeated use, give it its own folder and refine `profile.md` with verified template details.
- Keep standard previews conservative and do not present them as official-template evidence by themselves.
- When a journal is upgraded to official-template verification, keep `verification.yaml`, any `layout-checklist.md`, `official_preview.*`, and the downloaded guide-source files in sync.


