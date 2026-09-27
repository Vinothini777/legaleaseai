import os
import time
from typing import Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


class GeminiDocumentGenerator:
    """Generate legal-document drafts using Google Gemini."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = (
            api_key
            or os.getenv("GEMINI_API_KEY", "").strip()
        )

        self.model = (
            model
            or os.getenv(
                "GEMINI_MODEL",
                "gemini-2.5-flash",
            ).strip()
        )

        self.mode = "gemini" if self.api_key else "demo"

        self.client = (
            genai.Client(api_key=self.api_key)
            if self.api_key
            else None
        )

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
        jurisdiction: str = "India",
        additional_instructions: str = "",
    ) -> str:

        # -------------------------------------------------
        # DEMO MODE
        # -------------------------------------------------
        if not self.api_key:
            self.mode = "demo"

            return self._demo_document(
                document_type=document_type,
                parties=parties,
                terms=terms,
                effective_date=effective_date,
                jurisdiction=jurisdiction,
            )

        # -------------------------------------------------
        # GEMINI PROMPT
        # -------------------------------------------------
        prompt = f"""
You are LegalEase, an AI-powered legal document drafting assistant.

Generate a professional legal document based ONLY on the
information provided by the user.

Document type:
{document_type}

Parties:
{parties}

Terms and conditions:
{terms}

Effective date:
{effective_date}

Jurisdiction:
{jurisdiction}

Additional instructions:
{additional_instructions}

Requirements:

1. Create a clear and professional legal document.
2. Include an appropriate title.
3. Include the relevant parties and effective date.
4. Include obligations, rights, payment terms, confidentiality,
   termination, dispute resolution, governing law, and other
   clauses appropriate to the selected document type.
5. Do NOT invent names, addresses, amounts, dates, legal facts,
   or other information.
6. If required information is missing, use:
   [INSERT INFORMATION]
7. Organize the document using numbered sections.
8. Use formal but understandable legal language.
9. Keep the document specific to the selected document type.
10. Consider the specified jurisdiction.
11. Do not provide explanations before the document.
12. Do not provide explanations after the document.
13. Return ONLY the completed legal document.

At the end of the document include:

LEGAL NOTICE:

This document is an AI-generated draft for informational
purposes only and does not constitute legal advice. The
document should be reviewed by a qualified legal professional
before signing or relying upon it.
"""

        # -------------------------------------------------
        # CALL GEMINI WITH RETRIES
        # -------------------------------------------------
        last_error = None

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

                generated_text = (
                    response.text or ""
                ).strip()

                if generated_text:
                    self.mode = "gemini"
                    return generated_text

                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            except Exception as exc:

                last_error = exc

                if attempt < 2:
                    time.sleep(
                        2 * (attempt + 1)
                    )

        # -------------------------------------------------
        # FALLBACK TO DEMO MODE
        # -------------------------------------------------
                print(f"GEMINI ERROR: {last_error}")
raise RuntimeError(f"Gemini API error: {last_error}") from last_error
            document_type=document_type,
            parties=parties,
            terms=terms,
            effective_date=effective_date,
            jurisdiction=jurisdiction,
            fallback_reason=str(last_error),
        )

    # =====================================================
    # DEMO DOCUMENT
    # =====================================================

    @staticmethod
    def _demo_document(
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
        jurisdiction: str,
        fallback_reason: str = "",
    ) -> str:

        if fallback_reason:
            demo_notice = (
                "\n\n"
                "[DEMO MODE: Gemini was temporarily unavailable. "
                "This sample draft was generated locally.]\n"
            )
        else:
            demo_notice = (
                "\n\n"
                "[DEMO MODE: Add GEMINI_API_KEY to enable "
                "AI generation.]\n"
            )

        return f"""
{document_type.upper()}

Effective Date: {effective_date}

Jurisdiction: {jurisdiction}


PARTIES

{parties}


1. PURPOSE AND SCOPE

This document records the terms described by the parties
for the selected document type.


2. TERMS AND CONDITIONS

{terms}


3. REPRESENTATIONS

Each party represents that it has the authority to enter
into this arrangement, subject to applicable law.


4. CONFIDENTIALITY

Where confidential information is exchanged, the parties
shall use reasonable care to protect such information,
subject to applicable law and the specific terms provided.


5. TERMINATION

Termination shall occur according to the terms supplied
by the parties and applicable law.

Where a notice period or other termination requirement
has not been provided, use:

[INSERT INFORMATION]


6. DISPUTE RESOLUTION

Any dispute arising from this document shall be addressed
according to the dispute-resolution terms supplied by
the parties and applicable law.


7. GOVERNING LAW

This document shall be interpreted subject to the laws
of {jurisdiction}, to the extent applicable.


8. ENTIRE AGREEMENT

This document records the information supplied for this
draft and does not replace any mandatory legal requirements.


SIGNATURES


Party 1:

Signature: ______________________________

Name: [INSERT INFORMATION]

Date: _________________________________


Party 2:

Signature: ______________________________

Name: [INSERT INFORMATION]

Date: _________________________________


LEGAL NOTICE:

This document is an AI-generated draft for informational
purposes only and does not constitute legal advice. The
document should be reviewed by a qualified legal professional
before signing or relying upon it.

{demo_notice}
""".strip()