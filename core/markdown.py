from __future__ import annotations

import html
from typing import List, Tuple


def parse_markdown_blocks(text: str) -> List[Tuple[str, str]]:
    """
    Split message content into blocks of (type, content).
    type: "code" or "text".
    """
    lines = text.splitlines()
    blocks: List[Tuple[str, str]] = []
    buffer: List[str] = []
    in_code = False
    for line in lines:
        if line.strip().startswith("```"):
            if in_code:
                blocks.append(("code", "\n".join(buffer)))
                buffer = []
                in_code = False
            else:
                if buffer:
                    blocks.append(("text", "\n".join(buffer)))
                    buffer = []
                in_code = True
        else:
            buffer.append(line)
    if buffer:
        blocks.append(("code" if in_code else "text", "\n".join(buffer)))
    return blocks


def render_text_as_html(text: str) -> str:
    escaped = html.escape(text)
    return escaped.replace("\n", "<br>")
