#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MedXpert 标准检索连接器 · MCP Server
=====================================
把 medxpert 标准索引知识库（医疗器械 / 骨科常用标准：ISO / YY-T / GB-T / ASTM /
IEC / EN / 21 CFR / MDCG 等）封装成本地只读 MCP Server，
供 WorkBuddy / Agent 直接调用检索标准信息（标准号、名称、适用区域、归口方、
主题领域、官方链接、关联法规）。

特性：
- 本地只读，零网络外发，零凭据
- 4 个工具：list_standards / search_standards / get_standard / standards_by_region
- 检索返回标准条目 + 官方链接 + 关联法规标注

运行：python standards_mcp_server.py   （stdio 模式，供 MCP 客户端调用）
用法：FastMCP stdio 协议，直接作为 MCP server 配置进 WorkBuddy mcp.json
"""

import json
import os
import re
import sys
from pathlib import Path

from fastmcp import FastMCP

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------
# 知识库源目录定位（三级回退，确保开箱即用）：
#   1. 包内 references/（本连接器自带知识库，发布形态）
#   2. STD_REFS 环境变量（用户自定义指向其他知识库目录）
#   3. 脚本所在目录的 ../references 或 ./references（源码形态/相对安装）
_BUNDLED = Path(__file__).resolve().parent / "references"
_SIBLING = Path(__file__).resolve().parent.parent / "references"


def _resolve_refs_dir() -> Path:
    env_dir = os.environ.get("STD_REFS")
    if env_dir:
        p = Path(env_dir)
        if p.is_dir():
            return p.resolve()
    for cand in (_BUNDLED, _SIBLING, Path(__file__).resolve().parent):
        if (cand / "README.md").is_file() or any(cand.glob("*.md")):
            return cand.resolve()
    return _BUNDLED.resolve()


REFS_DIR = _resolve_refs_dir()

SERVER_NAME = "medxpert-standards-connector"
SERVER_VERSION = "1.0.0"
SERVER_DESC = (
    "MedXpert 标准检索连接器：本地只读检索医疗器械 / 骨科常用标准索引库 "
    "(ISO/YY-T/GB-T/ASTM/IEC/EN/21 CFR/MDCG 等)，返回标准号、名称、适用区域、"
    "归口方、主题领域、官方链接与关联法规。零网络、零凭据、纯本地。"
)

mcp = FastMCP(SERVER_NAME, version=SERVER_VERSION, instructions=SERVER_DESC)

# ---------------------------------------------------------------------------
# 知识库加载
# ---------------------------------------------------------------------------
STD_FILES = {}  # std_key -> {"title": str, "path": Path, "content": str, "sections": {section_title: text}, "links": [str]}


def _extract_title(content: str, filename: str) -> str:
    """从 # 标题或文件名提取主题名"""
    m = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return filename.replace(".md", "")


def _split_sections(content: str) -> list:
    """按 ## / ### 标题切分为小节，返回 [(title, body)]"""
    sections = []
    lines = content.splitlines()
    cur_title = "(前言)"
    cur_body = []
    for ln in lines:
        if re.match(r"^#{2,4}\s+", ln):
            if cur_body or cur_title != "(前言)":
                sections.append((cur_title, "\n".join(cur_body).strip()))
            cur_title = re.sub(r"^#{2,4}\s+", "", ln).strip()
            cur_body = []
        else:
            cur_body.append(ln)
    if cur_body or cur_title != "(前言)":
        sections.append((cur_title, "\n".join(cur_body).strip()))
    return [s for s in sections if s[1]]


def _extract_links(content: str) -> list:
    """提取 md 中的 http(s) 链接"""
    return re.findall(r"https?://[^\s\)\]\>\"']+", content)


def load_standards() -> None:
    if not REFS_DIR.is_dir():
        raise RuntimeError(f"知识库目录不存在: {REFS_DIR}，请设置 STD_REFS 指向含 .md 的知识库目录")
    for p in sorted(REFS_DIR.glob("*.md")):
        if p.name == "README.md":
            continue
        try:
            content = p.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            content = p.read_text(encoding="gb18030", errors="replace")
        STD_FILES[p.stem] = {
            "title": _extract_title(content, p.name),
            "path": p,
            "content": content,
            "sections": _split_sections(content),
            "links": list(dict.fromkeys(_extract_links(content))),  # 去重保序
        }


# ---------------------------------------------------------------------------
# 检索核心：中文友好 BM25 近似（无第三方依赖）
# ---------------------------------------------------------------------------
STOPWORDS = {
    "的", "了", "和", "与", "或", "及", "在", "是", "为", "对", "于", "以",
    "这", "那", "个", "中", "上", "下", "等", "之", "也", "而", "并", "其",
    "a", "an", "the", "to", "of", "and", "or", "in", "on", "for", "with",
}


def _tokenize(text: str) -> list:
    """分词：英文按单词，中文按 2-gram 滑动窗口 + 单字回退"""
    text = text.lower()
    tokens = []
    # 英文/数字单词
    for w in re.findall(r"[a-z0-9][a-z0-9\-\.\']{1,}", text):
        tokens.append(w)
    # 中文连续片段
    for seg in re.findall(r"[\u4e00-\u9fff]{2,}", text):
        if len(seg) <= 4:
            tokens.append(seg)
        else:
            for i in range(len(seg) - 1):
                tokens.append(seg[i : i + 2])
    return [t for t in tokens if t and t not in STOPWORDS and len(t) > 1]


def _build_index():
    """为所有标准主题文件建立 词->[(std_key, tf, sec_idx)] 索引"""
    index = {}
    for key, std in STD_FILES.items():
        for si, (stitle, sbody) in enumerate(std["sections"]):
            text = stitle + "\n" + sbody
            for tok in set(_tokenize(text)):
                tf = text.lower().count(tok)
                index.setdefault(tok, []).append((key, si, tf))
    return index


_INDEX = {}


def _ensure_index():
    global _INDEX
    if not _INDEX:
        _INDEX = _build_index()
    return _INDEX


def search(query: str, top_k: int = 5, topic_filter: str = None) -> list:
    """
    返回 [{std_key, title, section, snippet, score, links}]
    score: 词频加权 + 标题命中加权
    """
    q_tokens = _tokenize(query)
    if not q_tokens:
        return []
    index = _ensure_index()
    scores = {}  # (std_key, sec_idx) -> score
    for tok in q_tokens:
        for key, si, tf in index.get(tok, []):
            if topic_filter and key != topic_filter:
                continue
            scores[(key, si)] = scores.get((key, si), 0) + (1.0 + 0.5 * tf)
    if not scores:
        return []
    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:top_k]
    results = []
    for (key, si), score in ranked:
        std = STD_FILES[key]
        stitle, sbody = std["sections"][si]
        # 摘要：截取 400 字
        snippet = re.sub(r"\s+", " ", sbody).strip()
        if len(snippet) > 400:
            snippet = snippet[:400] + "…"
        results.append(
            {
                "std_key": key,
                "std_title": std["title"],
                "section": stitle,
                "snippet": snippet,
                "score": round(score, 2),
                "links": std["links"][:8],
            }
        )
    return results


# ---------------------------------------------------------------------------
# MCP 工具
# ---------------------------------------------------------------------------
@mcp.tool()
def list_standards() -> str:
    """列出标准索引库全部主题文件（枢纽）及覆盖的标准族，返回 JSON 数组。"""
    files = []
    for key in sorted(STD_FILES.keys()):
        std = STD_FILES[key]
        files.append(
            {
                "std_key": key,
                "title": std["title"],
                "sections": len(std["sections"]),
                "official_links": len(std["links"]),
                "topic": _topic_of(std["content"]),
            }
        )
    return json.dumps(files, ensure_ascii=False, indent=2)


@mcp.tool()
def search_standards(query: str, top_k: int = 5, topic_filter: str = None) -> str:
    """
    在标准索引库中检索关键词（支持中文/英文/标准号，如 'ISO 13485'、'无菌屏障'、
    '生物相容性'、'ASTM F138'、'UDI'）。返回命中的主题、小节、摘要片段、官方链接与相关度得分。
    """
    if not query or not query.strip():
        return json.dumps({"error": "query 不能为空"}, ensure_ascii=False)
    results = search(query, top_k=top_k, topic_filter=topic_filter)
    if not results:
        return json.dumps(
            {"query": query, "count": 0, "hint": "未命中，可尝试更短关键词或标准缩写（ISO/YY-T/GB-T/ASTM/IEC/EN）"},
            ensure_ascii=False,
            indent=2,
        )
    return json.dumps({"query": query, "count": len(results), "results": results}, ensure_ascii=False, indent=2)


@mcp.tool()
def get_standard(std_key: str) -> str:
    """按 std_key 取某一标准主题文件的完整整理内容（含全部小节与官方链接）。先调用 list_standards 查看可用 std_key。"""
    std = STD_FILES.get(std_key)
    if not std:
        keys = list(STD_FILES.keys())
        return json.dumps(
            {"error": f"未找到主题 {std_key}，可用: {keys[:10]} ...（共 {len(keys)} 个）"},
            ensure_ascii=False,
        )
    return json.dumps(
        {
            "std_key": std_key,
            "title": std["title"],
            "content": std["content"],
            "official_links": std["links"],
        },
        ensure_ascii=False,
        indent=2,
    )


@mcp.tool()
def standards_by_region(region: str) -> str:
    """
    按适用区域筛选标准：输入区域简称（如 '中国' / '国际' / '美国' / '欧盟' / '日本' /
    'ISO' / 'ASTM'），返回相关主题文件与官方链接。
    """
    if not region or not region.strip():
        return json.dumps({"error": "region 不能为空"}, ensure_ascii=False)
    region = region.strip()
    matched = []
    for key in sorted(STD_FILES.keys()):
        std = STD_FILES[key]
        if region in std["content"] or region in std["title"]:
            matched.append(
                {
                    "std_key": key,
                    "title": std["title"],
                    "official_links": std["links"][:5],
                }
            )
    if not matched:
        return json.dumps(
            {"region": region, "count": 0, "hint": "未命中区域，可用：中国 / 国际 / 美国 / 欧盟 / 日本 / ISO / ASTM / IEC"},
            ensure_ascii=False,
            indent=2,
        )
    return json.dumps({"region": region, "count": len(matched), "results": matched}, ensure_ascii=False, indent=2)


def _topic_of(content: str) -> str:
    """粗判主题文件归属的标准领域（用于列表展示）"""
    topic_map = [
        ("质量管理体系", "质量体系"),
        ("风险管理", "风险管理"),
        ("生物相容", "生物相容性"),
        ("软件", "软件与网络安全"),
        ("灭菌", "灭菌与无菌屏障"),
        ("洁净", "洁净室与环境"),
        ("标签", "标签与 UDI"),
        ("植入", "植入物材料"),
        ("电气", "电气安全与性能"),
        ("设计", "设计开发"),
    ]
    for kw, topic in topic_map:
        if kw in content[:600]:
            return topic
    return "综合"


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------
def main() -> None:
    try:
        load_standards()
    except RuntimeError as e:
        print(f"[standards-connector] FATAL: {e}", file=sys.stderr)
        sys.exit(1)
    n = len(STD_FILES)
    print(f"[standards-connector] v{SERVER_VERSION} 已加载 {n} 份标准主题资料 from {REFS_DIR}", file=sys.stderr)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
