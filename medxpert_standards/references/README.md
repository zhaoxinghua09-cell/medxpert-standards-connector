# 标准索引知识库

MedXpert 标准检索连接器的本地知识库（随包分发）。收录医疗器械 / 骨科常用标准族：
**ISO / YY-T / GB-T / ASTM / IEC / EN / 21 CFR / MDCG** 等。

> 本库为**标准检索索引**，不复制受版权保护的标准正文，仅记录标准号、名称、适用区域、
> 归口方、主题领域、官方链接与关联法规。标准正文版权归各标准组织所有。

## 主题枢纽（10 个）

| 文件 | 覆盖标准族 |
|---|---|
| 标准索引总览.md | 主索引 + 按主题/区域导航 |
| 质量管理与体系标准枢纽.md | ISO 13485、ISO 9001、GB/T 42061、21 CFR 820、PIC/S |
| 风险管理标准枢纽.md | ISO 14971、GB/T 42062、MDCG 2021-9 |
| 生物相容性标准枢纽.md | ISO 10993 系列、GB/T 16886 系列、FDA 10993-1 |
| 软件与网络安全标准枢纽.md | IEC 62304、IEC 62366、IMDRF SaMD、MDCG 2019-16 |
| 灭菌与无菌屏障标准枢纽.md | ISO 11135、ISO 11137、ISO 11607、YY 0033 |
| 洁净室与环境控制标准枢纽.md | ISO 14644 系列、GB 50073、GB/T 16292 |
| 标签与UDI标准枢纽.md | ISO 15223-1、ISO 20417、YY/T 1752、MDCG 2019-15 |
| 植入物材料标准枢纽.md | ASTM F138/F139/F2063、GB/T 13810、GB 4234、ISO 5832 |
| 电气安全与性能标准枢纽.md | IEC 60601 系列、GB 9706 系列 |

## 检索

由 `standards_mcp_server.py` 加载，提供 `list_standards / search_standards / get_standard / standards_by_region` 四个工具。
