import os
import time
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


class GeminiDocumentGenerator:
    def __init__(self, model: Optional[str] = None):
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()

        self.model = (
            model
            or os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
        )

        self.client = None

        if self.api_key:
            try:
                from google import genai

                self.client = genai.Client(
                    api_key=self.api_key
                )

                self.mode = "gemini"

            except Exception:
                self.client = None
                self.mode = "demo"

        else:
            self.mode = "demo"

    def build_prompt(
        self,
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
        jurisdiction: str,
        additional_instructions: str = "",
    ) -> str:

        return f"""
You are LegalEase, an AI-assisted legal document drafting system.

Create a professional draft of the following legal document.

DOCUMENT TYPE:
{document_type}

PARTIES:
{parties}

EFFECTIVE DATE:
{effective_date}

JURISDICTION:
{jurisdiction}

TERMS AND CONDITIONS:
{terms}

ADDITIONAL INSTRUCTIONS:
{additional_instructions}

IMPORTANT RULES:

1. Do not invent facts that were not provided.
2. If important information is missing, use:
   [INSERT INFORMATION]
3. Create a professional legal-document structure.
4. Include an appropriate title.
5. Include an introduction/recitals where appropriate.
6. Use numbered clauses and sections.
7. Clearly reflect the supplied terms.
8. Include appropriate obligations and responsibilities based
   only on the supplied information.
9. Include termination provisions where appropriate.
10. Include governing law/jurisdiction where appropriate.
11. Include signature blocks.
12. Include names, titles and dates as placeholders where needed.
13. Use professional and readable legal language.
14. Do not claim that the document has been reviewed by a lawyer.
15. Do not provide explanations outside the document.
16. Do not use Markdown code fences.

At the end include:

REVIEW NOTE:
This document has been prepared for drafting purposes and should
be reviewed by a qualified legal professional before signing.

Return only the completed legal document.
"""

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
        jurisdiction: str,
        additional_instructions: str = "",
    ):

        prompt = self.build_prompt(
            document_type=document_type,
            parties=parties,
            terms=terms,
            effective_date=effective_date,
            jurisdiction=jurisdiction,
            additional_instructions=additional_instructions,
        )

        # Gemini available
        if self.client is not None:

            last_error = None

            # Retry temporary 503/availability errors
            for attempt in range(3):

                try:

                    response = self.client.models.generate_content(
                        model=self.model,
                        contents=prompt,
                    )

                    text = getattr(response, "text", None)

                    if text and text.strip():
                        return text.strip()

                    raise RuntimeError(
                        "Gemini returned an empty response."
                    )

                except Exception as exc:

                    last_error = exc

                    error_text = str(exc).lower()

                    temporary_error = any(
                        phrase in error_text
                        for phrase in [
                            "503",
                            "unavailable",
                            "high demand",
                            "temporarily",
                            "overloaded",
                            "deadline exceeded",
                        ]
                    )

                    if temporary_error and attempt < 2:
                        time.sleep(3 * (attempt + 1))
                        continue

                    break

            # If Gemini is temporarily unavailable,
            # return a usable draft instead of crashing.
            return self._demo_document(
                document_type=document_type,
                parties=parties,
                terms=terms,
                effective_date=effective_date,
                jurisdiction=jurisdiction,
                additional_instructions=additional_instructions,
                ai_error=str(last_error),
            )

        # No API key / Gemini unavailable
        return self._demo_document(
            document_type=document_type,
            parties=parties,
            terms=terms,
            effective_date=effective_date,
            jurisdiction=jurisdiction,
            additional_instructions=additional_instructions,
        )

    @staticmethod
    def _demo_document(
        document_type,
        parties,
        terms,
        effective_date,
        jurisdiction,
        additional_instructions="",
        ai_error=None,
    ):

        term_items = [
            item.strip()
            for item in terms.split(";")
            if item.strip()
        ]

        sections = []

        for index, term in enumerate(term_items, start=1):
            sections.append(
                f"{index}. {term}"
            )

        terms_text = "\n\n".join(sections)

        return f"""
{document_type.upper()}

THIS {document_type.upper()} ("Agreement") is made effective as of
{effective_date}.

PARTIES

This Agreement is entered into between:

{parties}

JURISDICTION

This Agreement shall be governed by the applicable laws of
{jurisdiction}, subject to applicable law.

TERMS AND CONDITIONS

{terms_text}

ADDITIONAL PROVISIONS

{additional_instructions}

GENERAL

The Parties acknowledge that the terms stated above represent
the information supplied for preparation of this draft.

SIGNATURES

For the First Party:

____________________________________
Name: [INSERT INFORMATION]
Title: [INSERT INFORMATION]
Date: [INSERT INFORMATION]


For the Second Party:

____________________________________
Name: [INSERT INFORMATION]
Title: [INSERT INFORMATION]
Date: [INSERT INFORMATION]


REVIEW NOTE:

This document has been prepared for drafting purposes and should
be reviewed by a qualified legal professional before signing.
""".strip()