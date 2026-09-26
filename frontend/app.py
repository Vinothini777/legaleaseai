import sys
from pathlib import Path

# ---------------------------------------------------------
# Make the project root available for imports
# ---------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import os
import requests
import streamlit as st

from dotenv import load_dotenv

from services.document_formatter import (
    format_docx,
    format_pdf,
    format_txt,
)

load_dotenv(PROJECT_ROOT / ".env")


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------
BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
).rstrip("/")


DOCUMENT_TYPES = [
    "Employment Contract",
    "NDA",
    "Lease Agreement",
    "Freelance Work Contract",
    "Employment Offer Letter",
    "Service Agreement",
    "General Agreement",
    "Custom Contract",
]


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------
st.markdown(
    """
    <style>
    .main-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 20px;
        color: #667085;
        margin-top: 0;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 24px;
        font-weight: 700;
        margin-top: 25px;
        margin-bottom: 10px;
    }

    .notice {
        padding: 15px;
        border-radius: 10px;
        background-color: #fff7ed;
        border: 1px solid #fed7aa;
        color: #7c2d12;
        margin-top: 20px;
    }

    .success-box {
        padding: 15px;
        border-radius: 10px;
        background-color: #ecfdf3;
        border: 1px solid #a7f3d0;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Session state
# ---------------------------------------------------------
if "document" not in st.session_state:
    st.session_state.document = ""

if "document_type" not in st.session_state:
    st.session_state.document_type = ""

if "generation_mode" not in st.session_state:
    st.session_state.generation_mode = ""

if "generated" not in st.session_state:
    st.session_state.generated = False


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------
st.markdown(
    '<div class="main-title">⚖️ LegalEase</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">AI-Powered Legal Document Generator</div>',
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Backend status
# ---------------------------------------------------------
try:
    health_response = requests.get(
        f"{BACKEND_URL}/health",
        timeout=5,
    )

    if health_response.ok:
        st.success("Backend connected successfully.")
    else:
        st.warning(
            f"Backend returned HTTP {health_response.status_code}."
        )

except requests.RequestException:
    st.error(
        f"Backend is not reachable at {BACKEND_URL}. "
        "Make sure FastAPI is running."
    )


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------
with st.sidebar:

    st.header("Document Details")

    document_type = st.selectbox(
        "Document Type",
        DOCUMENT_TYPES,
        index=0,
    )

    jurisdiction = st.text_input(
        "Jurisdiction",
        value="India",
    )

    effective_date = st.text_input(
        "Effective Date",
        value="1 October 2026",
    )

    parties = st.text_area(
        "Parties",
        placeholder=(
            "Example:\n"
            "Company ABC\n"
            "John Doe"
        ),
        height=120,
    )

    terms = st.text_area(
        "Terms & Conditions",
        placeholder=(
            "Enter the important terms of the agreement.\n\n"
            "You can separate individual terms using semicolons."
        ),
        height=180,
    )

    additional_instructions = st.text_area(
        "Additional Instructions",
        placeholder=(
            "Optional instructions for the AI document generator."
        ),
        height=120,
    )

    logo_file = st.file_uploader(
        "Optional Company Logo",
        type=["png", "jpg", "jpeg"],
    )

    st.divider()

    generate_button = st.button(
        "⚖️ Generate Document",
        type="primary",
        use_container_width=True,
    )


# ---------------------------------------------------------
# Generate document
# ---------------------------------------------------------
if generate_button:

    if not parties.strip():
        st.error("Please enter the parties.")

    elif not terms.strip():
        st.error("Please enter the terms and conditions.")

    elif not effective_date.strip():
        st.error("Please enter the effective date.")

    else:

        payload = {
            "document_type": document_type,
            "parties": parties,
            "terms": terms,
            "effective_date": effective_date,
            "jurisdiction": jurisdiction,
            "additional_instructions": additional_instructions,
        }

        with st.spinner("Generating your legal document..."):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/generate",
                    json=payload,
                    timeout=120,
                )

                if response.ok:

                    data = response.json()

                    generated_document = data.get(
                        "content",
                        "",
                    )

                    if not generated_document.strip():
                        st.error(
                            "The backend returned an empty document."
                        )

                    else:

                        st.session_state.document = (
                            generated_document
                        )

                        st.session_state.document_type = (
                            document_type
                        )

                        st.session_state.generation_mode = (
                            data.get("mode", "unknown")
                        )

                        st.session_state.generated = True

                        st.success(
                            "Document generated successfully!"
                        )

                else:

                    try:
                        error_detail = response.json().get(
                            "detail",
                            response.text,
                        )
                    except Exception:
                        error_detail = response.text

                    st.error(
                        f"Backend error "
                        f"({response.status_code}): "
                        f"{error_detail}"
                    )

            except requests.RequestException as exc:

                st.error(
                    "Could not connect to the LegalEase backend."
                )

                st.code(str(exc))


# ---------------------------------------------------------
# Generated document
# ---------------------------------------------------------
if st.session_state.generated:

    st.markdown(
        '<div class="section-title">Generated Document</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.generation_mode == "demo":

        st.info(
            "The document was generated in demo mode. "
            "Add a valid Gemini API key to your .env file "
            "to enable AI generation."
        )

    elif st.session_state.generation_mode == "gemini":

        st.success(
            "Document generated using Gemini AI."
        )

    # -----------------------------------------------------
    # Editable document
    # -----------------------------------------------------
    edited_document = st.text_area(
        "Review and edit your document",
        value=st.session_state.document,
        height=650,
        key="editable_document",
    )

    # Keep session state synchronized
    st.session_state.document = edited_document

    st.divider()

    # -----------------------------------------------------
    # Download section
    # -----------------------------------------------------
    st.markdown(
        '<div class="section-title">Download Document</div>',
        unsafe_allow_html=True,
    )

    st.write(
        "Choose a format to download your completed document:"
    )

    # Generate files
    try:

        txt_bytes = format_txt(
            edited_document
        )

        docx_bytes = format_docx(
            edited_document,
            st.session_state.document_type,
            terms=terms,
        )

        pdf_bytes = format_pdf(
            edited_document,
            st.session_state.document_type,
            terms=terms,
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.download_button(
                label="📄 Download TXT",
                data=txt_bytes,
                file_name=(
                    f"{st.session_state.document_type}"
                    ".txt"
                ),
                mime="text/plain",
                use_container_width=True,
            )

        with col2:

            st.download_button(
                label="📝 Download DOCX",
                data=docx_bytes,
                file_name=(
                    f"{st.session_state.document_type}"
                    ".docx"
                ),
                mime=(
                    "application/vnd.openxmlformats-"
                    "officedocument.wordprocessingml.document"
                ),
                use_container_width=True,
            )

        with col3:

            st.download_button(
                label="📕 Download PDF",
                data=pdf_bytes,
                file_name=(
                    f"{st.session_state.document_type}"
                    ".pdf"
                ),
                mime="application/pdf",
                use_container_width=True,
            )

    except Exception as exc:

        st.error(
            "The document was generated, but the "
            "download files could not be prepared."
        )

        st.exception(exc)


# ---------------------------------------------------------
# Legal notice
# ---------------------------------------------------------
st.markdown(
    """
    <div class="notice">
        <strong>Legal notice:</strong><br>
        LegalEase generates draft documents and does not
        provide legal advice. Review the document with a
        qualified legal professional and check the applicable
        requirements of the relevant jurisdiction before
        signing.
    </div>
    """,
    unsafe_allow_html=True,
)