import base64
import html
import os
from datetime import date

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
)

st.markdown(
    """
    <style>
    .hero {
        padding: 1.2rem 1.4rem;
        border-radius: 18px;
        background: linear-gradient(135deg, #151922, #232a3a);
        color: white;
        margin-bottom: 1rem;
    }
    .hero h1 { margin: 0; }
    .hero p { margin: .35rem 0 0; color: #d7dbe5; }
    .preview {
        max-height: 680px;
        overflow-y: auto;
        padding: 1.4rem;
        border-radius: 14px;
        background: #10131a;
        color: #e9edf5;
        border: 1px solid #303747;
    }
    .preview h3 { margin-top: 1rem; color: #ffffff; }
    .preview p { line-height: 1.65; white-space: pre-wrap; }
    .spacer { height: 8px; }
    .small-note { color: #737b8c; font-size: .88rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <h1>⚖️ LegalEase</h1>
      <p>AI-assisted legal document drafting, editing and export.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "generated_text" not in st.session_state:
    st.session_state.generated_text = ""
if "generated_model" not in st.session_state:
    st.session_state.generated_model = ""

with st.sidebar:
    st.header("Document settings")
    document_type = st.selectbox(
        "Document type",
        [
            "Employment Contract",
            "Non-Disclosure Agreement (NDA)",
            "Residential Lease Agreement",
            "Freelance Work Contract",
            "Employment Offer Letter",
            "Service Agreement",
            "Custom Agreement",
        ],
    )
    if document_type == "Custom Agreement":
        document_type = st.text_input(
            "Custom document type",
            placeholder="e.g. Software Licensing Agreement",
        ) or "Custom Agreement"

    jurisdiction = st.text_input(
        "Jurisdiction (optional)",
        placeholder="e.g. Tamil Nadu, India",
    )
    effective_date = st.date_input(
        "Effective date",
        value=date.today(),
    )

    st.subheader("Branding")
    company_name = st.text_input("Company / brand name", value="LegalEase")
    footer_text = st.text_input(
        "Footer",
        value="Generated with LegalEase — review with a qualified legal professional.",
    )
    logo = st.file_uploader(
        "Optional logo",
        type=["png", "jpg", "jpeg"],
    )

    st.caption("Keep confidential information out of external AI services unless authorized.")

left, right = st.columns([1, 1])

with left:
    st.subheader("Document inputs")
    parties = st.text_area(
        "Parties involved",
        placeholder=(
            "Jane Doe (Service Provider), TechNova Inc. (Client)"
        ),
        height=120,
    )
    terms = st.text_area(
        "Terms & conditions",
        placeholder=(
            "Payment to be made within 30 days of invoice; "
            "Provider will deliver work by the agreed deadline; "
            "Confidentiality must be maintained; "
            "Either party may terminate with 15 days notice"
        ),
        height=180,
    )
    special_instructions = st.text_area(
        "Special instructions (optional)",
        placeholder="Add clauses, tone, structure or formatting requirements.",
        height=120,
    )

    generate = st.button(
        "✨ Generate Document",
        type="primary",
        use_container_width=True,
    )

    if generate:
        if not parties.strip() or not terms.strip():
            st.error("Please enter parties and at least one term.")
        else:
            payload = {
                "document_type": document_type,
                "parties": parties,
                "terms": terms,
                "effective_date": effective_date.isoformat(),
                "jurisdiction": jurisdiction,
                "special_instructions": special_instructions,
                "company_name": company_name,
                "footer_text": footer_text,
            }
            try:
                with st.spinner("Generating your draft..."):
                    response = requests.post(
                        f"{BACKEND_URL}/api/v1/generate",
                        json=payload,
                        timeout=120,
                    )
                if response.ok:
                    data = response.json()
                    st.session_state.generated_text = data["text"]
                    st.session_state.generated_model = data["model"]
                    if data.get("demo_mode"):
                        st.info("Demo mode is active. Add a Gemini API key for real AI generation.")
                    else:
                        st.success(f"Generated with {data['model']}.")
                else:
                    st.error(f"Backend error: {response.text}")
            except requests.RequestException as exc:
                st.error(
                    "Could not reach FastAPI. Start the backend on "
                    f"{BACKEND_URL}. Details: {exc}"
                )

with right:
    st.subheader("Preview / edit")

    if st.session_state.generated_text:
        edited = st.text_area(
            "Editable document",
            value=st.session_state.generated_text,
            height=530,
            key="document_editor",
        )
        st.session_state.generated_text = edited

        preview = html.escape(edited).replace("\n", "<br>")
        st.markdown(
            f'<div class="preview">{preview}</div>',
            unsafe_allow_html=True,
        )

        st.markdown("### Download")

        logo_data_url = None
        if logo is not None:
            mime = logo.type or "image/png"
            encoded = base64.b64encode(logo.getvalue()).decode("ascii")
            logo_data_url = f"data:{mime};base64,{encoded}"

        export_payload = {
            "document_type": document_type,
            "text": st.session_state.generated_text,
            "terms": terms,
            "company_name": company_name,
            "footer_text": footer_text,
            "logo_data_url": logo_data_url,
        }

        col1, col2, col3 = st.columns(3)

        def export_button(label, endpoint, mime, filename):
            try:
                result = requests.post(
                    f"{BACKEND_URL}/api/v1/export/{endpoint}",
                    json=export_payload,
                    timeout=60,
                )
                if result.ok:
                    st.download_button(
                        label,
                        data=result.content,
                        file_name=filename,
                        mime=mime,
                        use_container_width=True,
                    )
                else:
                    st.error(f"Export failed: {result.text}")
            except requests.RequestException as exc:
                st.error(f"Export request failed: {exc}")

        with col1:
            export_button(
                "Download TXT",
                "txt",
                "text/plain",
                "legalease_document.txt",
            )
        with col2:
            export_button(
                "Download DOCX",
                "docx",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "legalease_document.docx",
            )
        with col3:
            export_button(
                "Download PDF",
                "pdf",
                "application/pdf",
                "legalease_document.pdf",
            )

        st.caption(
            f"Model: {st.session_state.generated_model or 'configured backend model'}"
        )
    else:
        st.info("Your generated document will appear here.")
        st.markdown(
            """
            **Workflow**

            1. Enter parties and terms.
            2. Click **Generate Document**.
            3. Edit the draft.
            4. Download TXT, DOCX or PDF.
            """
        )

st.divider()
st.markdown(
    '<div class="small-note">LegalEase produces AI-assisted drafts and general legal information. '
    'Have a qualified legal professional review documents before relying on them.</div>',
    unsafe_allow_html=True,
)
