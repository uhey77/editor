from __future__ import annotations

from langchain.output_parsers import PydanticOutputParser

from .schemas import ContradictionResult


def build_contradiction_parser() -> PydanticOutputParser:
    return PydanticOutputParser(pydantic_object=ContradictionResult)


def format_instructions() -> str:
    return build_contradiction_parser().get_format_instructions()


def parse_contradiction_result(text: str) -> ContradictionResult:
    parser = build_contradiction_parser()
    return parser.parse(_strip_code_fences(text))


def _strip_code_fences(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```") and stripped.endswith("```"):
        lines = stripped.splitlines()
        if len(lines) >= 2:
            return "\n".join(lines[1:-1]).strip()
    return stripped
