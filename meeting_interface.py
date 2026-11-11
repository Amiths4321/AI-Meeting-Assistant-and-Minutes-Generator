
import streamlit as st
import fitz
from meeting_storage import add_meeting_timestamp
from meeting_storage import (
    add_meeting_timestamp,
    load_meeting_history
)

def initialize_meeting_history():

    if "meeting_history" not in st.session_state:
        st.session_state["meeting_history"] = (
            load_meeting_history()
        )


def extract_pdf_text(uploaded_file):

    text = ""

    pdf_bytes = uploaded_file.read()

    pdf_document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    for page_number, page in enumerate(pdf_document, start=1):

        page_text = page.get_text("text")

        if page_text.strip():
            text += (
                f"\n\n--- Page {page_number} ---\n"
                + page_text
            )

    pdf_document.close()

    return text


def display_meeting_input():

    st.header("📥 Meeting Transcript Input")

    meeting_title = st.text_input(
        "Meeting Title",
        placeholder="Example: Weekly Project Review"
    )

    uploaded_file = st.file_uploader(
        "Upload Meeting Transcript",
        type=["txt", "pdf"]
    )

    pasted_text = st.text_area(
        "Or Paste Meeting Transcript",
        height=250,
        placeholder="Paste your meeting transcript here..."
    )

    if st.button("Submit Meeting", type="primary"):

        transcript = ""

        if uploaded_file is not None:

            if uploaded_file.name.lower().endswith(".pdf"):
                transcript = extract_pdf_text(uploaded_file)

            else:
                transcript = uploaded_file.getvalue().decode(
                    "utf-8-sig",
                    errors="replace"
                )

        elif pasted_text.strip():
            transcript = pasted_text.strip()

        if not transcript.strip():
            st.warning(
                "Please upload a transcript or paste meeting text."
            )
            return None

        meeting_data = {
            "title": meeting_title.strip() or "Untitled Meeting",
            "transcript": transcript
        }

        meeting_data = add_meeting_timestamp(meeting_data)

        st.session_state["meeting_history"].append(meeting_data)

        st.success("Meeting transcript submitted successfully!")

        return meeting_data

    return None
