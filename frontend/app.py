import os
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# ---------------------------------------------------------
# PROJECT PATH
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")

try:
    gemini_key = st.secrets.get("GEMINI_API_KEY", "")
    if gemini_key:
        os.environ["GEMINI_API_KEY"] = gemini_key
except Exception:
    pass
# ---------------------------------------------------------
# LEGAL EASE IMPORTS
# ---------------------------------------------------------

from ai_core.gemini_generator import GeminiDocumentGenerator

from services.document_formatter import (
    format_docx,
    format_pdf,
    format_txt,
)

from services.text_utils import safe_filename


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
)


# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    .main-title {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        color: #64748b;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }

    .section-title {
        font-size: 1.4rem;
        font-weight: 700;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

if "generated" not in st.session_state:
    st.session_state.generated = False

if "document" not in st.session_state:
    st.session_state.document = ""

if "document_type" not in st.session_state:
    st.session_state.document_type = ""

if "generation_mode" not in st.session_state:
    st.session_state.generation_mode = ""


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.markdown(
    '<div class="main-title">⚖️ LegalEase</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "AI-powered legal document drafting assistant"
    "</div>",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

with st.sidebar:

    st.header("Document Setup")

    document_type = st.selectbox(
        "Document type",
        [
            "Employment Agreement",
            "Non-Disclosure Agreement",
            "Service Agreement",
            "Rental Agreement",
            "Freelance Agreement",
            "Business Partnership Agreement",
            "Offer Letter",
            "Custom Legal Document",
        ],
    )

    jurisdiction = st.text_input(
        "Jurisdiction",
        value="India",
    )

    st.markdown("---")

    st.caption(
        "LegalEase creates AI-generated drafts for "
        "informational purposes. Important documents "
        "should be reviewed by a qualified legal "
        "professional."
    )


# ---------------------------------------------------------
# MAIN INPUT AREA
# ---------------------------------------------------------

left_column, right_column = st.columns(2)


# ---------------------------------------------------------
# LEFT COLUMN
# ---------------------------------------------------------

with left_column:

    st.markdown(
        '<div class="section-title">1. Parties</div>',
        unsafe_allow_html=True,
    )

    parties = st.text_area(
        "Enter the parties involved",
        height=140,
        placeholder=(
            "Example:\n"
            "Employer: ABC Technologies Pvt. Ltd.\n"
            "Employee: John Doe"
        ),
    )

    st.markdown(
        '<div class="section-title">2. Terms</div>',
        unsafe_allow_html=True,
    )

    terms = st.text_area(
        "Enter the terms and conditions",
        height=300,
        placeholder=(
            "Describe salary, duties, payment terms, "
            "confidentiality, termination, etc."
        ),
    )


# ---------------------------------------------------------
# RIGHT COLUMN
# ---------------------------------------------------------

with right_column:

    st.markdown(
        '<div class="section-title">3. Effective Date</div>',
        unsafe_allow_html=True,
    )

    effective_date = st.text_input(
        "Effective date",
        value="1 October 2026",
    )

    st.markdown(
        '<div class="section-title">'
        "4. Additional Instructions"
        "</div>",
        unsafe_allow_html=True,
    )

    additional_instructions = st.text_area(
        "Optional instructions",
        height=140,
        placeholder=(
            "Example: Use formal language and "
            "numbered clauses."
        ),
    )

    st.info(
        "Tip: Give specific facts and use "
        "[INSERT INFORMATION] for anything you do not know."
    )


# ---------------------------------------------------------
# GENERATE BUTTON
# ---------------------------------------------------------

generate_button = st.button(
    "⚖️ Generate Legal Document",
    type="primary",
    use_container_width=True,
)


# ---------------------------------------------------------
# DOCUMENT GENERATION
# ---------------------------------------------------------

if generate_button:

    if not parties.strip():

        st.error(
            "Please enter the parties."
        )

    elif not terms.strip():

        st.error(
            "Please enter the terms and conditions."
        )

    elif not effective_date.strip():

        st.error(
            "Please enter an effective date."
        )

    else:

        with st.spinner(
            "Generating your legal document..."
        ):

            try:

                generator = GeminiDocumentGenerator(
    api_key=st.secrets.get("GEMINI_API_KEY", "")
        )
                st.write("Gemini key loaded:", bool(generator.api_key))
                st.write("Gemini model:", generator.model)
                generated_document = (
                    generator.generate_document(
                        document_type=document_type,
                        parties=parties,
                        terms=terms,
                        effective_date=effective_date,
                        jurisdiction=jurisdiction,
                        additional_instructions=(
                            additional_instructions
                        ),
                    )
                )

                if not generated_document.strip():

                    st.error(
                        "The generated document is empty."
                    )

                else:

                    st.session_state.document = (
                        generated_document
                    )

                    st.session_state.document_type = (
                        document_type
                    )

                    st.session_state.generation_mode = (
                        generator.mode
                    )

                    st.session_state.generated = True

                    st.success(
                        "Document generated successfully!"
                    )

            except Exception as exc:

                st.error(
                    f"Document generation failed: {exc}"
                )


# ---------------------------------------------------------
# GENERATED DOCUMENT
# ---------------------------------------------------------

if st.session_state.generated:

    st.markdown("---")

    st.markdown(
        '<div class="section-title">'
        "Generated Document"
        "</div>",
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------
    # GENERATION MODE MESSAGE
    # -----------------------------------------------------

    mode = st.session_state.generation_mode

    if mode == "demo":

        st.warning(
            "Demo mode is active. Gemini AI was not used."
        )

    elif mode == "gemini":

        st.success(
            "Document generated using Gemini AI."
        )


    # -----------------------------------------------------
    # EDITABLE DOCUMENT
    # -----------------------------------------------------

    edited_document = st.text_area(
        "Edit your document before downloading",
        value=st.session_state.document,
        height=600,
        key="editable_document",
    )


    # -----------------------------------------------------
    # FILE NAME
    # -----------------------------------------------------

    filename_base = safe_filename(
        st.session_state.document_type
        or "legal_document"
    )


    # -----------------------------------------------------
    # DOWNLOAD SECTION
    # -----------------------------------------------------

    st.markdown("### Download")

    col1, col2, col3 = st.columns(3)


    # -----------------------------------------------------
    # TXT
    # -----------------------------------------------------

    with col1:

        st.download_button(
            "📄 Download TXT",
            data=format_txt(
                edited_document
            ),
            file_name=f"{filename_base}.txt",
            mime="text/plain",
            use_container_width=True,
        )


    # -----------------------------------------------------
    # DOCX
    # -----------------------------------------------------

    with col2:

        st.download_button(
            "📝 Download DOCX",
            data=format_docx(
                edited_document
            ),
            file_name=f"{filename_base}.docx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            use_container_width=True,
        )


    # -----------------------------------------------------
    # PDF
    # -----------------------------------------------------

    with col3:

        st.download_button(
            "📕 Download PDF",
            data=format_pdf(
                edited_document
            ),
            file_name=f"{filename_base}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )


    # -----------------------------------------------------
    # LEGAL DISCLAIMER
    # -----------------------------------------------------

    st.caption(
        "Review the generated document carefully and "
        "obtain professional legal advice before signing "
        "or relying upon it."
    )