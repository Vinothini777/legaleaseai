import os
import time
from typing import Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


class GeminiDocumentGenerator:
    """
    Gemini-powered legal document generator.

    This version does NOT silently fall back to Demo mode.
    If Gemini fails, the actual API error is raised so it can be fixed.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = (
            api_key
            or os.getenv("GEMINI_API_KEY", "")
        ).strip()

        self.model = (
            model
            or os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
        ).strip()

        self.mode = "gemini"

        if not self.api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is missing. "
                "Add your Gemini API key to .env locally "
                "or Streamlit Secrets when deployed."
            )

        self.client = genai.Client(api_key=self.api_key)

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
        jurisdiction: str = "India",
        additional_instructions: str = "",
    ) -> str:

        prompt = f"""
You are LegalEase, an AI-powered legal document drafting assistant.

Create a professional legal document based strictly on the information
provided below.

DOCUMENT TYPE:
{document_type}

JURISDICTION:
{jurisdiction}

PARTIES:
{parties}

TERMS AND CONDITIONS:
{terms}

EFFECTIVE DATE:
{effective_date}

ADDITIONAL INSTRUCTIONS:
{additional_instructions}

DOCUMENT REQUIREMENTS:

1. Create a complete professional legal document.
2. Give the document an appropriate title.
3. Use formal and clear legal language.
4. Organize the document using numbered sections and clauses.
5. Include all important facts and requirements supplied by the user.
6. Do not invent names, addresses, dates, amounts, obligations,
   identification numbers, or other facts.
7. If important information is missing, use:
   [INSERT INFORMATION]
8. Include appropriate clauses relevant to the document type.
9. Where appropriate, consider clauses covering:
   - Definitions
   - Scope and purpose
   - Rights and obligations
   - Payment and financial terms
   - Confidentiality
   - Term and renewal
   - Termination
   - Liability
   - Dispute resolution
   - Governing law
   - Notices
   - Signatures
10. Adapt the document to the specified jurisdiction.
11. Use numbered clauses consistently.
12. Include signature blocks for all relevant parties.
13. Do not provide explanations before the document.
14. Return only the completed legal document.

At the end of the document, include:

LEGAL NOTICE:
This document is an AI-generated draft for informational purposes only.
It does not constitute legal advice and should be reviewed by a qualified
legal professional before signing or relying upon it.
"""

        last_error = None

        # Try Gemini up to 3 times in case of a temporary API failure.
        for attempt in range(3):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.2,
                        max_output_tokens=6000,
                    ),
                )

                generated_text = (response.text or "").strip()

                if generated_text:
                    self.mode = "gemini"
                    return generated_text

                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            except Exception as exc:
                last_error = exc

                if attempt < 2:
                    time.sleep(2 * (attempt + 1))

        # IMPORTANT:
        # Do NOT silently switch to Demo mode.
        # Show the real Gemini error instead.
        self.mode = "gemini"

        raise RuntimeError(
            f"Gemini API error using model '{self.model}': {last_error}"
        ) from last_error