# MedXpert 标准检索连接器

本地只读的医疗器械 / 骨科标准检索 MCP 连接器。把一份结构化「标准索引知识库」封装成 MCP Server，
供 WorkBuddy / Agent 直接调用，检索标准号、名称、适用区域、归口方、主题领域、官方链接与关联法规。

> **形态说明**：本连接器是**标准检索索引**，不复制受版权保护的标准正文（ISO 等标准文本受版权保护）。
> 每条标准记录指向官方公开信息与购买/查阅链接，合规安全、体积可控。

## 特性

- 本地只读，零网络外发，零凭据
- 4 个工具：`list_standards` / `search_standards` / `get_standard` / `standards_by_region`
- 中文友好 BM25 近似检索（无第三方依赖，仅 `fastmcp`）
- 知识库随包分发（见 `references/`），开箱即用

## 覆盖范围（标准族）

| 主题 | 代表标准 |
|---|---|
| 质量管理体系 | ISO 13485、ISO 9001、GB/T 42061、21 CFR 820 (QMSR)、PIC/S PE 009 |
| 风险管理 | ISO 14971、GB/T 42062、MDCG 2021-9 |
| 生物相容性 | ISO 10993 系列、GB/T 16886 系列、FDA 10993-1 指南 |
| 软件与网络安全 | IEC 62304、IEC 62366-1、IMDRF SaMD、MDCG 2019-16 |
| 灭菌与无菌屏障 | ISO 11135、ISO 11137、ISO 11607、YY 0033 |
| 洁净室与环境 | ISO 14644 系列、GB 50073、GB/T 16292 |
| 标签与 UDI | ISO 15223-1、ISO 20417、YY/T 1752、MDCG 2019-15 |
| 植入物材料 | ASTM F138/F139/F2063、GB/T 13810、GB 4234、ISO 5832、ISO 7153-1 |
| 电气安全 | IEC 60601 系列、GB 9706 系列 |
| 设计开发 | ISO 13485 7.3、21 CFR 820.30、IEC 62366 |

## 安装

```bash
pip install -r requirements.txt
python standards_mcp_server.py        # stdio 模式自测
```

## 接入 WorkBuddy

将本目录配置进 WorkBuddy 的 `mcp.json`（与包内 `mcp.json` 一致）：

```json
{
  "mcpServers": {
    "medxpert-standards-connector": {
      "command": "python",
      "args": ["<包目录>/standards_mcp_server.py"],
      "env": { "STD_REFS": "references" }
    }
  }
}
```

可选：设置环境变量 `STD_REFS` 指向自定义标准知识库目录（默认使用包内 `references/`）。

## 安全

- `network: none` — 不发起任何网络请求
- `credentials: none` — 不读取任何凭据
- `readOnly: true` — 只读加载本地 Markdown
- `dataEgress: false` — 无数据出域

## 目录结构

```
medxpert-standards-connector/
├── standards_mcp_server.py     # MCP Server 主程序
├── connector-meta.json        # 开放平台元数据
├── mcp.json                   # MCP 启动配置
├── icon.svg                   # 头像
├── LICENSE                  # Apache-2.0
├── requirements.txt           # 依赖：fastmcp
├── README.md
└── references/                # 标准索引知识库（随包分发）
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

## 许可说明 · License Notice

- **代码许可**：本仓库源代码以 **Apache-2.0** 许可发布（见根目录 [LICENSE](LICENSE)），版权归「赵兴华 / Steven Zhao·China（ORCID 0009-0001-0512-1237）」。
- **知识库 / 方法论**：随仓库分发的知识库、references/、合成法规知识、检索方法论、分类体系与编排结构 **保留所有权利（All Rights Reserved）**；可在注明出处的前提下引用与学术、公共讨论，但未经书面许可不得复制、改编、再分发、转售或用于模型训练。
- **品牌状态限定**：MedXpert、SynomosAI、LGD 等为相关项目标识，**均未申请实体注册、未申请商标注册**；出现仅作来源标识，不构成对法人实体或商标权的任何主张。
- **免责**：本仓库内容不构成法规意见、法律意见或注册代理服务；关键数据以监管机构最新发布为准。
- **联系**：zhaoxinghua09@gmail.com ｜ ORCID 0009-0001-0512-1237

标准正文版权归各标准组织所有；本连接器仅索引公开信息与官方链接，不复制标准正文。
`mcp-name: io.github.zhaoxinghua09-cell/medxpert-standards-connector`
