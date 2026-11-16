"""MedXpert Standards — read-only MCP index of medical-device standards.

The PyPI distribution ships the same code the repository runs: a FastMCP stdio
server over a bundled, structured index of ISO / YY-T / GB-T / ASTM / IEC / EN /
21 CFR / MDCG entries. It returns standard numbers, titles, regions, owners,
topics, official links and related regulations — never copyrighted standard
text.
"""

__version__ = "1.0.2"

__all__ = ["__version__"]
