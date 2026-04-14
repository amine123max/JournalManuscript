# Journal Manuscript

[English](README.md) | [中文](README.zh-CN.md)

![openai](https://img.shields.io/badge/openai-0A0A0A?style=flat-square&logo=openai&logoColor=white) ![journal](https://img.shields.io/badge/journal-manuscript-1D4ED8?style=flat-square) ![latex](https://img.shields.io/badge/latex-layout-166534?style=flat-square) ![template](https://img.shields.io/badge/template-profiles-7C3AED?style=flat-square) ![paper-writing](https://img.shields.io/badge/paper-writing-92400E?style=flat-square)

Journal Manuscript 是一套面向期刊论文起草、模板保真修订与投稿 venue 迁移的 Codex skill 包。整个仓库围绕“出版社 family 基线、具体期刊 overlay，以及显式核验记录”来组织。在使用者工作区中，默认起稿基线是官方 IEEE 期刊 family LaTeX 模板（`IEEEtran`）；只有当某项约束已经写入 profile 或已被本地官方模板资产核验时，才会继续叠加目标期刊的额外要求。

## 分发模式

- 完整库：适合维护者、研究团队或需要跨多个出版社 family / 多个期刊反复切换的用户。
- Family 精简包：面向最终用户的最小下载单元，包含可安装的 `journal-manuscript/` skill 包、所选 family 库、该 family 所需的模板/guide 资产，以及继承该 family 的子期刊 profile。

## 覆盖快照

- 28 个家族级模板基线
- 87 个具体期刊 profile
- 115 组标准化 `official_preview.tex/.pdf/.png` 资产
- 66 份模板核验记录（`verification.yaml`）
- 65 个已核验 official-template 目标
- 1 个仍缺少官方模板资产的 blocked 目标

主入口索引位于 `journal-manuscript/references/journals/catalog.md`。现在所有 profile 目录统一使用 `official_preview.*` 作为渲染资产名，核验级别则由 `verification.yaml` 决定。

## 核验分层

- 标准 profile 层：没有核验记录的目录也会提供 `profile.md` 和 `official_preview.*`，用于保守查看版式方向。
- 官方模板层：带有 `verification.yaml` 的目录会明确说明“哪些部分已经核验、哪些仍需人工确认”，并统一使用 `official_preview.*` 作为渲染产物。
- 阻塞层：如果本地缺少官方模板资产，则显式标记为 `blocked`，而不是把未核验内容包装成“已官方化”。

## Family 级基线复用

- 某些出版社 family 可以在起稿和预览阶段，把同一个 family 级模板基线复用到多个兄弟期刊。
- 这种 family 级基线复用并不等于这些期刊的投稿规则完全相同；最终仍然要以具体 journal 的 author guide 为准。
- 当前 family 级基线复用策略请看 `journal-manuscript/references/journals/family-template-sharing-tiers.md` 和 `journal-manuscript/references/journals/family-template-sharing-tiers.yaml`。

这套库是“广覆盖、谨慎声明”的设计，不会把所有期刊都宣称为已经完全官方核验。

## 核心使用场景

- 在保持论文语气与结构稳定的前提下补写或重写章节
- 接入图、表、公式与 caption，同时尽量不破坏现有排版节奏
- 保持引用样式、交叉引用与尾部声明和目标期刊要求一致
- 在 IEEE 基线之上向其他期刊模板迁移，并只应用已核验的差异

## 包结构

```text
Journal-manuscript/
├── README.md
├── README.zh-CN.md
├── .gitignore
└── journal-manuscript/
    ├── SKILL.md
    ├── agents/
    │   ├── openai.yaml
    │   ├── shared-journal-loading.yaml
    │   ├── provider-portability.yaml
    │   ├── anthropic.yaml
    │   ├── gemini.yaml
    │   ├── openrouter.yaml
    │   ├── local-llm.yaml
    │   └── README.md
    ├── references/
    │   ├── house-style.md
    │   ├── journal-profiles.md
    │   └── journals/
    │       ├── catalog.md
    │       ├── official-template-verified-targets.md
    │       ├── README.md
    │       ├── ieee/
    │       ├── elsevier/
    │       ├── springer/
    │       ├── mdpi/
    │       └── ...
    └── scripts/
        ├── README.md
        ├── export_selective_skill_bundle.py
        ├── render_profile_preview_assets.py
        └── render_official_template_preview_assets.py
```

## 使用者论文工作区约定

当这套 skill 真正在论文仓库中工作时，默认期待论文侧路径大致为：

- `paper/main.tex`
- `paper/references.bib`
- `paper/CAPTION_BANK.md`
- `paper/tables/`
- `paper/figures/`

这些路径是“使用者论文工作区”的约定，不是当前 skill 仓库里自带的文件。如果你的论文目录结构不同，先找到等价文件，再保持同样的功能角色即可。

## 官方预览示例

下面这组示例现在统一展示 family 级 official preview 资产，让 README 反映“可复用的出版社基线模板”，而不是具体子期刊示例。

<table>
  <tr>
    <td align="center" valign="top">
      <strong>IEEE Family</strong><br/>
      <img src="journal-manuscript/references/journals/ieee/official_preview.png" alt="IEEE family official preview" width="280"/><br/>
      基于已导入的 IEEEtran 模板路径生成的已核验 family 基线预览；具体子期刊差异仍由各自 profile 继续收紧。
    </td>
    <td align="center" valign="top">
      <strong>Elsevier Family</strong><br/>
      <img src="journal-manuscript/references/journals/elsevier/official_preview.png" alt="Elsevier family official preview" width="280"/><br/>
      展示 Elsevier family 可复用的作者稿基线版式，后续再叠加具体期刊对引用样式或声明区的要求。
    </td>
  </tr>
  <tr>
    <td align="center" valign="top">
      <strong>Frontiers Family</strong><br/>
      <img src="journal-manuscript/references/journals/frontiers/official_preview.png" alt="Frontiers family official preview" width="280"/><br/>
      保留 Frontiers family 层面的 specialty 元数据、通讯作者信息和声明区结构，更接近开放科学投稿流。
    </td>
    <td align="center" valign="top">
      <strong>PLOS Family</strong><br/>
      <img src="journal-manuscript/references/journals/plos/official_preview.png" alt="PLOS family official preview" width="280"/><br/>
      展示 PLOS family 复用的作者稿报告结构，具体 title 的额外投稿要求再在子 profile 中补充。
    </td>
  </tr>
</table>

如果你要看完整库，直接进入 `journal-manuscript/references/journals/`。现在每个 family 目录和 journal 目录都带有 `profile.md` 与 `official_preview.*`。带核验记录的目录额外包含 `verification.yaml`；真正的核验级别由该文件决定，可能是官方 family 模板、官方模板包，或者 blocked 占位状态。只要涉及跨期刊复用 family 级模板基线，就先看 `family-template-sharing-tiers.*`。

## 维护脚本

- `journal-manuscript/scripts/export_selective_skill_bundle.py`：导出一个可分发的最小精简包，包含选定 family 或 journal 库及其所需模板资产。
- `journal-manuscript/scripts/render_profile_preview_assets.py`：为未 `verified` 的目录生成标准化 `official_preview.*` 资产。
- `journal-manuscript/scripts/render_official_template_preview_assets.py`：刷新已核验目录的 `official_preview.*` 与核验记录。
- `journal-manuscript/scripts/README.md`：说明脚本命名规则、输出约定和典型命令。

## 安装方式

如果你需要完整目录库，可以直接克隆本仓库，或下载完整 ZIP 压缩包。然后将内部的 `journal-manuscript/` 文件夹复制到你的 Codex skill 目录：

- Windows：`C:\Users\<你的用户名>\.codex\skills\journal-manuscript`
- macOS/Linux：`~/.codex/skills/journal-manuscript`

这个 skill 包并不只支持单一模型。当前安装内容同时包含原生 Codex/OpenAI 配置，以及放在 `journal-manuscript/agents/` 下的 Claude、Gemini、OpenRouter 和本地 LLM 包装层兼容配置。

安装完成后，在 Codex 配置中启用并按需要重启客户端即可。如果你使用的是非 Codex 的包装层，也应让它指向同一个已安装的 `journal-manuscript/` skill 目录，这样它就能复用同一套期刊加载规则和 profile 元数据。

如果你希望最终用户只下载某一个出版社 family，对外分发时应优先使用下面的 family 精简包流程，而不是整个完整库。

## Family 精简包

Family 精简包是面向最终用户的推荐下载格式。每个精简包都会包含：

- 可直接安装的 `journal-manuscript/` skill 包
- 所选 family 在 `references/journals/<family>/` 下的目录库
- 该 family 引用到的 family 级 guide 与模板资产
- 继承该 family 的子期刊 profile
- 用于说明分发范围的包内 README 和 `bundle-manifest.json`

也就是说，用户下载一个 family 精简包，就能同时拿到“对应的 family 库、family 模板资产，以及可安装的 skill 包”。

下面这些链接可以直接点击下载对应的 family 最小安装 ZIP：

| Family | 下载 |
| --- | --- |
| `aaas` | [下载 AAAS Family](https://github.com/amine123max/JournalManuscript/releases/latest/download/journal-manuscript-family-aaas.zip) |
| `acm` | [下载 ACM Family](https://github.com/amine123max/JournalManuscript/releases/latest/download/journal-manuscript-family-acm.zip) |
| `acs` | [下载 ACS Family](https://github.com/amine123max/JournalManuscript/releases/latest/download/journal-manuscript-family-acs.zip) |
| `aip` | [下载 AIP Family](https://github.com/amine123max/JournalManuscript/releases/latest/download/journal-manuscript-family-aip.zip) |
| `bmc` | [下载 BMC Family](https://github.com/amine123max/JournalManuscript/releases/latest/download/journal-manuscript-family-bmc.zip) |
| `cambridge` | [下载 Cambridge Family](https://github.com/amine123max/JournalManuscript/releases/latest/download/journal-manuscript-family-cambridge.zip) |
| `cell-press` | [下载 Cell Press Family](https://github.com/amine123max/JournalManuscript/releases/latest/download/journal-manuscript-family-cell-press.zip) |
| `copernicus` | [下载 Copernicus Family](https://github.com/amine123max/JournalManuscript/releases/latest/download/journal-manuscript-family-copernicus.zip) |
| `custom-journal` | [下载 Custom Journal Family](https://github.com/amine123max/JournalManuscript/releases/latest/download/journal-manuscript-family-custom-journal.zip) |
| `de-gruyter` | [下载 De Gruyter Family](https://github.com/amine123max/JournalManuscript/releases/latest/download/journal-manuscript-family-de-gruyter.zip) |
| `elsevier` | [下载 Elsevier Family](https://github.com/amine123max/JournalManuscript/releases/latest/download/journal-manuscript-family-elsevier.zip) |
| `emerald` | [下载 Emerald Family](https://github.com/amine123max/JournalManuscript/releases/latest/download/journal-manuscript-family-emerald.zip) |
| `frontiers` | [下载 Frontiers Family](https://github.com/amine123max/JournalManuscript/releases/latest/download/journal-manuscript-family-frontiers.zip) |
| `hindawi` | [下载 Hindawi Family](https://github.com/amine123max/JournalManuscript/releases/latest/download/journal-manuscript-family-hindawi.zip) |
| `ieee` | [下载 IEEE Family](https://github.com/amine123max/JournalManuscript/releases/latest/download/journal-manuscript-family-ieee.zip) |
| `iop` | [下载 IOP Family](https://github.com/amine123max/JournalManuscript/releases/latest/download/journal-manuscript-family-iop.zip) |
| `mdpi` | [下载 MDPI Family](https://github.com/amine123max/JournalManuscript/releases/latest/download/journal-manuscript-family-mdpi.zip) |
| `nas` | [下载 NAS Family](https://github.com/amine123max/JournalManuscript/releases/latest/download/journal-manuscript-family-nas.zip) |
| `nature-portfolio` | [下载 Nature Portfolio Family](https://github.com/amine123max/JournalManuscript/releases/latest/download/journal-manuscript-family-nature-portfolio.zip) |
| `optica-publishing` | [下载 Optica Publishing Group Family](https://github.com/amine123max/JournalManuscript/releases/latest/download/journal-manuscript-family-optica-publishing.zip) |
| `oxford` | [下载 Oxford Family](https://github.com/amine123max/JournalManuscript/releases/latest/download/journal-manuscript-family-oxford.zip) |
| `plos` | [下载 PLOS Family](https://github.com/amine123max/JournalManuscript/releases/latest/download/journal-manuscript-family-plos.zip) |
| `royal-society` | [下载 Royal Society Family](https://github.com/amine123max/JournalManuscript/releases/latest/download/journal-manuscript-family-royal-society.zip) |
| `sage` | [下载 SAGE Family](https://github.com/amine123max/JournalManuscript/releases/latest/download/journal-manuscript-family-sage.zip) |
| `siam` | [下载 SIAM Family](https://github.com/amine123max/JournalManuscript/releases/latest/download/journal-manuscript-family-siam.zip) |
| `springer` | [下载 Springer Family](https://github.com/amine123max/JournalManuscript/releases/latest/download/journal-manuscript-family-springer.zip) |
| `taylor-francis` | [下载 Taylor and Francis Family](https://github.com/amine123max/JournalManuscript/releases/latest/download/journal-manuscript-family-taylor-francis.zip) |
| `wiley` | [下载 Wiley Family](https://github.com/amine123max/JournalManuscript/releases/latest/download/journal-manuscript-family-wiley.zip) |

如果你要在本地重新生成或刷新某个精简包，可使用：

```powershell
python journal-manuscript/scripts/export_selective_skill_bundle.py --family ieee --archive
```

常见示例：

```powershell
python journal-manuscript/scripts/export_selective_skill_bundle.py --family ieee --archive
python journal-manuscript/scripts/export_selective_skill_bundle.py --family elsevier --archive
python journal-manuscript/scripts/export_selective_skill_bundle.py --family frontiers --archive
```

最终用户的安装步骤很直接：点击 ZIP 链接，必要时先解压，然后把内部的 `journal-manuscript/` 文件夹复制到 Codex skills 目录。如果你在本地重复生成同名包，可追加 `--force` 覆盖旧输出。

## Family 脚手架生成功能

现在仓库也支持直接从 family 模板基线创建一个新的 `paper/` 写作工作区。

常见示例：

```powershell
python journal-manuscript/scripts/scaffold_family_manuscript.py --family ieee --output-dir C:\work\ieee-paper
python journal-manuscript/scripts/scaffold_family_manuscript.py --family frontiers --output-dir C:\work\frontiers-paper
```

脚手架会创建这些内容：

- `paper/main.tex`
- `paper/references.bib`
- `paper/CAPTION_BANK.md`
- `paper/README_PAPER.md`
- `paper/figures/`
- `paper/tables/`
- `paper/tables/generated/`

当前脚本已支持的 scaffold family：

- `ieee`
- `elsevier`
- `springer`
- `frontiers`
- `plos`
- `wiley`
- `acs`
- `aip`

推荐用法：

1. 先生成 family 脚手架。
2. 用 `$journal-manuscript` 配合 `journal=<family-slug>`，把 family 示例模板收敛成你的第一版草稿。
3. 当你需要进一步贴近具体期刊时，再切换到 `journal=<journal-slug>` 做定向收紧。

## 按目标论文选择并下载使用

对外分发发生在 family 精简包这一层；真正运行时的行为选择，仍然发生在 journal profile 这一层。

推荐流程：

1. 先确认你的论文目标期刊，或者至少确认所属出版社 / 模板家族。
2. 先安装包含该期刊的 family 精简包；如果需要更广的覆盖范围，再使用完整库。
3. 打开 `journal-manuscript/references/journals/catalog.md`，找到对应的 journal slug。
4. 调用时传入 `journal=<journal-slug>`，这样 skill 就会加载对应期刊的 profile、预览资产和核验元数据。
5. 如果暂时没有完全对应的期刊目录，就先使用最接近的家族目录，或者使用 `custom-journal/`。

典型示例：

- 机器人方向论文准备投 IEEE Transactions on Robotics：使用 `journal=ieee-tro`
- 海洋工程方向论文准备投 Ocean Engineering：使用 `journal=ocean-engineering`
- 跨学科开放获取论文准备投 PLOS ONE：使用 `journal=plos-one`

也就是说，用户实际下载的是 family 精简包，而“对应哪篇论文 / 哪个期刊”的差异，仍然是通过运行时选择的 journal profile 来完成的。

## 快速开始

如果你已经有目标论文或目标期刊，可以直接走下面这条最短路径：

1. 先从论文 PDF 首页、期刊官网或投稿系统里确认期刊名。
2. 在 `journal-manuscript/references/journals/catalog.md` 中搜索这个期刊名。
3. 复制匹配到的 slug，并用 `journal=<journal-slug>` 调用 skill。

注意：不要把论文标题直接当成 slug。真正要找的是论文所属的期刊 / venue 名称。

反查 slug 示例：

- `IEEE Transactions on Robotics` -> `ieee-tro`
- `IEEE Journal of Oceanic Engineering` -> `ieee-joe`
- `Ocean Engineering` -> `ocean-engineering`
- `Frontiers in Neurorobotics` -> `frontiers-in-neurorobotics`
- `PLOS ONE` -> `plos-one`

如果你现在只知道出版社或模板家族，也可以先从对应家族 profile 开始，例如 `ieee`、`elsevier`、`springer`、`wiley`、`frontiers`、`plos`。如果暂时没有完全匹配的具体期刊目录，就使用最接近的家族 profile，或者使用 `custom-journal/`。

如果你是要给别人打包一个最小可分发 skill，也可以把对应的 family slug 或 journal slug 直接传给 `export_selective_skill_bundle.py`，让它只导出当前需要的期刊模板样式和依赖资产。

可直接照抄的调用示例：

```text
Use $journal-manuscript with journal=ieee-tro task="Revise the related work section in the style of the current manuscript."
Use $journal-manuscript with journal=ocean-engineering task="Reformat the paper toward the target journal submission style."
Use $journal-manuscript with journal=plos-one task="Check whether the manuscript structure matches the target journal flow."
```

## 使用方式

现在建议所有 provider 共用同一套调用契约：

```text
skill=journal-manuscript journal=<journal-slug> task="<what to do>"
```

示例：

- OpenAI / Codex：`Use $journal-manuscript with journal=ieee-tro task="Rewrite the Introduction in the same style as the current paper."`
- Claude 包装层：`skill=journal-manuscript journal=ocean-engineering task="Reformat the manuscript toward Elsevier submission style."`
- Gemini 包装层：`skill=journal-manuscript journal=frontiers-in-neurorobotics task="Adapt the abstract and end sections to the target journal."`
- 本地 LLM 网关：`skill=journal-manuscript journal=plos-one task="Check whether the manuscript structure matches the official template flow."`

共享加载逻辑：

- 所有 provider 都应通过 `journal-manuscript/agents/shared-journal-loading.yaml` 来解析目标期刊。
- 这样在切换 OpenAI、Claude、Gemini、本地 LLM 时，会共用同一套 journal profile、verification metadata 和 fallback 规则。

## 说明

- 对外展示名是 `Journal Manuscript`。
- 内部合法 skill 触发名是 `journal-manuscript`。
- 这套包默认继承“使用者工作区中的官方 IEEE 期刊家族 LaTeX 基线（`IEEEtran`）”，并在需要时叠加目标期刊的额外要求。
- 现在扩展出来的大目录库强调“广覆盖但谨慎声明”；只有带核验记录的目录，才应被当作进入官方模板路径的依据。
- 在 Codex 里真正原生生效的仍然是 `agents/openai.yaml`；新增的其他 `agents/*.yaml` 是为了 Claude、Gemini、OpenRouter 和本地 LLM 包装层做 portability 配置，不是当前 Codex schema 的原生字段。



