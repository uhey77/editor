from __future__ import annotations

from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable
from langchain_core.runnables import RunnableLambda

from .parsers import format_instructions
from .parsers import parse_contradiction_result
from .schemas import ContradictionResult

DEFAULT_PROMPT_TEMPLATE = """You are a text consistency checker.
Detect factual contradictions in the input text.
Return only JSON that matches the schema.

{format_instructions}

Text:
{text}
"""


def build_prompt_template(template: str | None = None) -> PromptTemplate:
    prompt = PromptTemplate.from_template(template or DEFAULT_PROMPT_TEMPLATE)
    return prompt.partial(format_instructions=format_instructions())


def build_contradiction_chain(llm: Runnable, template: str | None = None) -> Runnable:
    prompt = build_prompt_template(template)
    return prompt | llm | StrOutputParser() | RunnableLambda(parse_contradiction_result)


def run_contradiction_detection(
    llm: Runnable,
    text: str,
    template: str | None = None,
) -> ContradictionResult:
    chain = build_contradiction_chain(llm, template=template)
    return chain.invoke({"text": text})
