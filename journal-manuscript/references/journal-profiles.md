# Journal Template Profiles

Use this reference as the routing guide for the per-journal folder structure.

## Coverage Snapshot

- 28 family-level profiles
- 87 journal-level profiles
- 115 profile folders with `official_preview.*`
- 66 journals with `verification.yaml`
- 65 verified targets and 1 blocked target

## Folder Layout

Journal-specific formats now live under `references/journals/` and are separated by family at the first level, with child journals nested underneath their family folder:

- `references/journals/catalog.md`: full catalog of the current library
- `references/journals/family-template-sharing-tiers.md`: human-readable family-template reuse policy
- `references/journals/family-template-sharing-tiers.yaml`: machine-readable family-template reuse policy
- `references/journals/README.md`: quick navigation notes
- `references/journals/<family>/profile.md`: publisher or template-family baseline
- `references/journals/<family>/<journal>/profile.md`: concrete journal profile
- `references/journals/<family>/<journal>/verification.yaml`: structured verification status, official source, and remaining manual checks
- `references/journals/<family>/<journal>/layout-checklist.md`: journal-facing checklist for verified journals that still need manual validation steps
- `references/journals/<family-or-journal>/official_preview.*`: canonical rendered preview assets used by the library
- `references/journals/slug-paths.json`: slug-to-relative-path lookup for nested journal folders

This structure is meant to grow. Add one new subfolder per journal family or target journal whenever another template becomes important enough to maintain explicitly.

## Verification Tiers

1. Standard profile tier: use `profile.md` and `official_preview.*` as the default visual asset even when the folder has no verification record.
2. Official-template tier: use `verification.yaml` as the source of truth for what has been audited; when the status is `verified`, the folder is backed by an official family template or official template package.
3. Blocked tier: if the verification record says `blocked`, keep the folder as a documented gap and do not claim official-template compliance.

## How To Use The Profiles

1. Start with `references/journals/ieee/verification.yaml`, `references/journals/ieee/profile.md`, and `house-style.md` if the manuscript is still IEEE-based or the venue is not yet fixed.
2. Open `references/journals/catalog.md` to find the matching family or journal folder.
3. If the target does not match an existing folder, use `custom-journal/` as the staging profile and replace it later with a journal-specific folder.
4. When the actual template files are available, update the relevant profile using the real class file, author guide, or manuscript sample.
5. When a journal has a verification record, treat `verification.yaml` as the boundary of what may be called official and what still remains manual.

## Family Template Reuse

- Use `references/journals/family-template-sharing-tiers.md` when you need to know whether a publisher-family template may be reused across multiple sibling journals.
- Tier 1 families have a local template-package root under `assets/official-templates/` and are the best fallback when the exact journal slug does not exist yet.
- Tier 2 families can still share an official family class baseline, but the repository has not yet materialized a family package root under `assets/official-templates/`.
- Tier 3 families should not yet be treated as reusable local template-package baselines in this repository.

## Minimum Profile Checklist

Every journal profile should capture at least these items:

1. Document class and options
2. Front matter structure
3. Abstract and keyword format
4. Section and heading hierarchy
5. Figure placement and caption position
6. Table environment, font size, and width rules
7. Equation numbering and notation conventions
8. Citation and bibliography style
9. Appendix, acknowledgments, and data-availability requirements
10. Compile toolchain and required packages

## Safe Defaults

- If no new journal template is provided, stay with the official IEEE baseline described in `house-style.md` and the verified IEEE family profile under `references/journals/ieee/`.
- If a journal name is given without template files, treat the journal folder as a conservative starter profile and verify the concrete rules before making high-risk layout changes.
- Preserve manuscript content logic where possible and update only the formatting and structure that the target journal requires.
- Treat the expanded library as a broad working catalog, not as a blanket claim that every journal rule has already been officially audited.


