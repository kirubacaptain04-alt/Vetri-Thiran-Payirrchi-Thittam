from ..config import Settings
from ..schemas import DocumentRequest
from ..utils.text import terms_list


SYSTEM_INSTRUCTION = """
You are LegalEase, a legal-document drafting assistant.

Produce a professional first draft based strictly on the user's supplied facts.
Do not invent names, dates, addresses, amounts, obligations, governing law, or
other material facts. If an important fact is missing, use a neutral placeholder
such as [NOT PROVIDED] rather than fabricating it.

Use clear formal language. Structure the document with:
1. A title.
2. Introductory/recital language when appropriate.
3. Clearly numbered sections.
4. Definitions where needed.
5. The user's requested terms.
6. Signature blocks when appropriate.

The result is a draft for user review, not legal advice. Do not claim that the
document is guaranteed to be legally valid or enforceable.
"""


class GeminiDocumentGenerator:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = None

        if settings.gemini_api_key and not settings.demo_mode:
            # Lazy import keeps DEMO_MODE/test environments usable without the SDK.
            from google import genai
            self.client = genai.Client(api_key=settings.gemini_api_key)

    def generate_document(self, request: DocumentRequest) -> str:
        if self.settings.demo_mode or self.client is None:
            return self._demo_document(request)

        prompt = self._build_prompt(request)
        from google.genai import types

        response = self.client.models.generate_content(
            model=self.settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                max_output_tokens=7000,
            ),
        )

        text = getattr(response, "text", None)
        if not text:
            raise RuntimeError("Gemini returned an empty response.")
        return text.strip()

    def _build_prompt(self, request: DocumentRequest) -> str:
        terms = terms_list(request.terms)
        term_lines = "\n".join(f"- {term}" for term in terms)

        return f"""
Draft the following legal document.

DOCUMENT TYPE:
{request.document_type}

PARTIES:
{request.parties}

EFFECTIVE DATE:
{request.effective_date}

JURISDICTION:
{request.jurisdiction or "[NOT PROVIDED]"}

REQUESTED TERMS:
{term_lines}

SPECIAL INSTRUCTIONS:
{request.special_instructions or "[NONE]"}

Return only the draft document. Do not add commentary before or after it.
"""

    @staticmethod
    def _demo_document(request: DocumentRequest) -> str:
        terms = terms_list(request.terms)
        bullets = "\n".join(f"- {term}" for term in terms)

        return f"""{request.document_type.upper()}

Effective Date: {request.effective_date}

PARTIES

{request.parties}

PURPOSE

This document records the agreement described by the parties above and is
prepared from the information supplied to LegalEase.

TERMS AND CONDITIONS

{bullets}

GENERAL PROVISIONS

1. Entire Agreement. The written terms of this document represent the draft
   supplied for review and should be checked against the parties' complete
   understanding.

2. Amendments. Any amendment should be made in writing and agreed by the
   parties.

3. Governing Law. {request.jurisdiction or "[NOT PROVIDED]"}

SIGNATURES

Party 1: ______________________________    Date: ______________

Party 2: ______________________________    Date: ______________

NOTICE

This is an AI-assisted draft generated from user-provided information. It is
not legal advice and should be reviewed by a qualified legal professional.
"""
