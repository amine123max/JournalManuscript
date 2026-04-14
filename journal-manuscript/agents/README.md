# Agents Folder

This folder now has two layers:

- `openai.yaml`: the only file in this folder that is natively defined by the current Codex skill schema
- provider portability files: optional cross-AI configuration notes for other model ecosystems
- `shared-journal-loading.yaml`: one provider-neutral journal profile loader contract reused by all portability configs

## Important Limitation

The current local skill schema explicitly defines `agents/openai.yaml`, but it does not define a universal multi-provider runtime format for Claude, Gemini, OpenRouter, or local LLMs.

That means:

- Codex/OpenAI can read `openai.yaml` directly
- the additional provider files in this folder are portability configs for humans, wrappers, gateways, or future tooling
- these extra files do not become active automatically unless the consuming system is taught to read them

## Portability Files

- `shared-journal-loading.yaml`: shared journal resolution order and invocation contract
- `provider-portability.yaml`: shared cross-provider loading rules
- `anthropic.yaml`: Claude-oriented portability mapping
- `gemini.yaml`: Gemini-oriented portability mapping
- `openrouter.yaml`: OpenRouter-oriented portability mapping
- `local-llm.yaml`: self-hosted or gateway-based LLM portability mapping

## Common Loading Order

When porting this skill to another AI system, use the same invocation contract:

- `skill=journal-manuscript`
- `journal=<journal-slug>`
- `task=<what to do>`

Then resolve files in this order:

1. `references/journals/slug-paths.json`
2. `references/journals/<family>/<journal-slug>/verification.yaml`
3. `references/journals/<family>/<journal-slug>/official_preview.tex`
4. `references/journals/<family>/<journal-slug>/profile.md`
5. `references/journals/catalog.md`
6. `references/journals/ieee/verification.yaml`
7. `references/journals/ieee/profile.md`
8. `references/journal-profiles.md`
9. `references/house-style.md`
10. `SKILL.md`

## Safe Rule

Do not claim native multi-AI support from these files alone. They make the skill portable, but each target runtime still needs its own adapter or prompt wrapper. The shared loader unifies the loading logic; it does not create automatic provider integration by itself.
