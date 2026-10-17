# MedXpert Standards Connector

## License Notice

- **Code**: The source code of this repository is released under **Apache-2.0** (see [LICENSE](LICENSE)), copyright by 赵兴华 / Steven Zhao·China (ORCID 0009-0001-0512-1237).
- **Knowledge base / methodology**: The bundled knowledge base, `references/`, synthesized regulatory knowledge, retrieval methodology, classification system and editorial structure are **All Rights Reserved** (see [CONTENT-LICENSE](CONTENT-LICENSE)); they may be quoted with attribution for academic or public discussion, but may not be copied, adapted, redistributed, resold, or used to train models without prior written permission.
- **Brand status**: MedXpert, SynomosAI, LGD and similar names are project identifiers only; none is a registered legal entity or registered trademark. Their use is for source identification and does not assert any legal-entity or trademark rights.
- **Disclaimer**: This repository does not constitute regulatory, legal, or registration-agent advice. For critical decisions, always refer to the latest official publications of the competent authority.
- **Contact**: zhaoxinghua09@gmail.com ｜ ORCID 0009-0001-0512-1237

---

A local, read-only MCP connector for medical-device / orthopedic **standards retrieval**. It packages a structured "standards index knowledge base" as an MCP Server that WorkBuddy / agents can call directly to look up standard numbers, names, applicable regions, owning committees, topic areas, official links, and related regulations.

> **Form note**: this connector is a **standards search index**. It does not copy copyright-protected standard texts (e.g., ISO documents); each record points to official public information and purchase/consult links — compliant, safe, and small.

## Features

- Local-only, read-only: zero network egress, zero credentials
- 4 tools: `list_standards` / `search_standards` / `get_standard` / `standards_by_region`
- Chinese-friendly BM25 approximate retrieval (no third-party dependency, only `fastmcp`)
- Knowledge base ships with the package (see `references/`), clone-and-run

## Coverage (standard families)

| Topic | Representative standards |
|---|---|
| Quality management systems | ISO 13485, ISO 9001, GB/T 42061, 21 CFR 820 (QMSR), PIC/S PE 009 |
| Risk management | ISO 14971, GB/T 42062, MDCG 2021-9 |
| Biocompatibility | ISO 10993 series, GB/T 16886 series, FDA 10993-1 guidance |
| Software & cybersecurity | IEC 62304, IEC 62366-1, IMDRF SaMD, MDCG 2019-16 |
| Sterilization & barrier | ISO 11135, ISO 11137, ISO 11607, YY 0033 |
| Cleanrooms & environment | ISO 14644 series, GB 50073, GB/T 16292 |
| Labeling & UDI | ISO 15223-1, ISO 20417, YY/T 1752, MDCG 2019-15 |
| Implant materials | ASTM F138/F139/F2063, GB/T 13810, GB 4234, ISO 5832, ISO 7153-1 |
| Electrical safety | IEC 60601 series, GB 9706 series |
| Design & development | ISO 13485 7.3, 21 CFR 820.30, IEC 62366 |

## Install

```bash
pip install -r requirements.txt
python standards_mcp_server.py        # stdio self-test
```

## Connect to WorkBuddy / any MCP host

Add this directory to your host's `mcp.json` (matches the bundled `mcp.json`):

```json
{
  "mcpServers": {
    "medxpert-standards-connector": {
      "command": "python",
      "args": ["<package dir>/standards_mcp_server.py"],
      "env": { "STD_REFS": "references" }
    }
  }
}
```

Optional: set the `STD_REFS` environment variable to point at a custom standards knowledge base (default: the bundled `references/`).

## Security

- `network: none` — no outbound network requests
- `credentials: none` — no credential access
- `readOnly: true` — loads local Markdown read-only
- `dataEgress: false` — no data leaves the machine

## Directory layout

```
medxpert-standards-connector/
├── standards_mcp_server.py     # MCP server entry
├── connector-meta.json        # platform metadata
├── mcp.json                   # MCP bootstrap config
├── icon.svg                   # icon
├── LICENSE                  # Apache-2.0
├── CONTENT-LICENSE          # knowledge content: All Rights Reserved
├── requirements.txt           # deps: fastmcp
├── README.md
└── references/                # standards index knowledge base (bundled)
    ├── 标准索引总览.md
    ├── 质量管理与体系标准枢纽.md
    ├── 风险管理标准枢纽.md
    ├── 生物相容性标准枢纽.md
    ├── 软件与网络安全标准枢纽.md
    ├── 灭菌与无菌屏障标准枢纽.md
    ├── 洁净室与环境控制标准枢纽.md
    ├── 标签与UDI标准枢纽.md
    ├── 植入物材料标准枢纽.md
    └── 电气安全与性能标准枢纽.md
```

## License & Attribution

Source code: **Apache-2.0** (see [LICENSE](LICENSE)), copyright by 赵兴华 / Steven Zhao·China (ORCID 0009-0001-0512-1237). The bundled knowledge base / `references/` / synthesized regulatory knowledge / retrieval methodology / classification system are **All Rights Reserved** (see [CONTENT-LICENSE](CONTENT-LICENSE)); they may be quoted with attribution, but not copied, resold, or used for model training.

Standard texts remain the property of their respective standards organizations; this connector only indexes public information and official links and does not copy standard texts.

`mcp-name: io.github.zhaoxinghua09-cell/medxpert-standards-connector`

## Why AI-Friendly

This connector is designed for both humans and AI agents:

- **Discoverable**: `agent.json` exposes tool/keyword metadata so MCP hosts (Claude Desktop, Cursor, etc.) can index and recommend it.
- **Zero-dependency**: pure Python standard library + `fastmcp`. `mcp.json` ships ready-to-paste — no extra install steps.
- **Read-only by design**: zero credentials, zero network egress, zero side effects. Safe for AI to invoke without human pre-approval.
- **Honest scope**: standards-index only — it returns records with official links, never reproduced standard texts. Out-of-scope queries return explicit codes, not hallucinations.
- **Examples included**: `references/` documents real query → answer patterns an AI can learn from.

## Keywords (to help AI match when to call)

`medical device standards`, `ISO 13485`, `ISO 14971`, `IEC 60601`, `IEC 62304`, `GB 9706`, `GB/T 42061`, `ASTM`, `sterilization ISO 11135`, `biocompatibility ISO 10993`, `standards lookup`, `regulatory standards`, `标准检索`, `医疗器械标准`, `UDI standards`, `MDR Annex VIII`, `IMDRF`, `MDCG`

## When to Invoke This Connector

Call any tool here when the user's question matches one of these intents:

- Look up a standard number, title, region, or owning committee for medical devices / orthopedics
- Find official links and related regulations for a standard family
- Compare standards across regions (ISO / GB / YY / ASTM / IEC)
- Prepare standards lists for regulatory submissions or design dossiers

Do NOT invoke for: medical advice, patient diagnosis, drug prescription, or any clinical decision-making.
