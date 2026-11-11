
import streamlit as st
from decision_extractor import extract_decisions
from action_extractor import extract_action_items
from deadline_tracker import extract_deadlines
from meeting_storage import save_meeting_history
from meeting_report import (
    generate_pdf_report,
    generate_excel_report
)

from config import APP_TITLE

from transcript_processor import (
    clean_transcript,
    get_transcript_statistics
)

from meeting_ai import summarize_meeting
from speaker_analyzer import analyze_speakers

from meeting_interface import (
    initialize_meeting_history,
    display_meeting_input
)


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🎙️",
    layout="wide"
)

st.title("🎙️ AI Meeting Assistant")

st.write(
    "Upload meeting transcripts and let AI generate "
    "summaries, decisions, and action items."
)

# INITIALIZE MEETING HISTORY
initialize_meeting_history()

st.divider()

# MEETING INPUT
meeting_data = display_meeting_input()


# PROCESS SUBMITTED MEETING
if meeting_data:

    # STEP 1: TRANSCRIPT PREPROCESSING
    st.subheader("🧹 Transcript Preprocessing")

    try:

        cleaned_transcript = clean_transcript(
            meeting_data["transcript"]
        )

        if not cleaned_transcript:

            st.error("The transcript contains no usable text.")

        else:

            meeting_data["transcript"] = cleaned_transcript

            st.session_state["meeting_history"][-1]["transcript"] = (
                cleaned_transcript
            )

            statistics = get_transcript_statistics(
                cleaned_transcript
            )

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Characters",
                statistics["character_count"]
            )

            col2.metric(
                "Words",
                statistics["word_count"]
            )

            col3.metric(
                "Lines",
                statistics["line_count"]
            )

            st.success("Transcript cleaned successfully!")

            st.subheader("📄 Cleaned Meeting Transcript")

            st.text_area(
                "Meeting Content",
                value=cleaned_transcript,
                height=250,
                disabled=True
            )

            # STEP 2: AI MEETING SUMMARIZATION
            st.divider()

            st.subheader("🤖 AI Meeting Summary")

            try:

                with st.spinner("AI is analyzing your meeting..."):

                    summary = summarize_meeting(meeting_data)

                    meeting_data["summary"] = summary

                    st.session_state["meeting_history"][-1]["summary"] = (
                        summary
                    )

                st.success("Meeting summary generated successfully!")

                st.markdown(summary)

            except Exception as error:

                st.error(
                    f"Meeting summarization failed: {error}"
                )

            # STEP 3: SPEAKER IDENTIFICATION AND ANALYSIS
            st.divider()

            st.subheader("👥 Speaker Identification")

            try:

                with st.spinner("Analyzing meeting speakers..."):

                    speaker_analysis = analyze_speakers(meeting_data)

                    meeting_data["speaker_analysis"] = speaker_analysis

                    st.session_state["meeting_history"][-1][
                        "speaker_analysis"
                    ] = speaker_analysis

                st.success("Speaker analysis completed!")

                for speaker in speaker_analysis.get("speakers", []):

                    with st.expander(
                        f"👤 {speaker.get('name', 'Unknown')}"
                    ):

                        st.write("**Topics Discussed:**")

                        for topic in speaker.get("topics_discussed", []):
                            st.write(f"- {topic}")

                        st.write("**Contributions:**")

                        for contribution in speaker.get("contributions", []):
                            st.write(f"- {contribution}")

                        st.write("**Questions or Concerns:**")

                        for concern in speaker.get("questions_or_concerns", []):
                            st.write(f"- {concern}")

                st.subheader("📝 Overall Discussion")

                st.write(
                    speaker_analysis.get(
                        "discussion_overview",
                        "No overview available."
                    )
                )

            except Exception as error:

                st.error(f"Speaker analysis failed: {error}")

    except Exception as error:

        st.error(
            f"Transcript preprocessing failed: {error}"
        )


            
            # STEP 4: MEETING DECISION EXTRACTION

        st.divider()

        st.subheader("⚖️ Meeting Decisions")

        try:

            with st.spinner("Extracting meeting decisions..."):

                decision_result = extract_decisions(meeting_data)

                meeting_data["decision_analysis"] = decision_result

                st.session_state["meeting_history"][-1][
                        "decision_analysis"
                    ] = decision_result

                st.success("Decision extraction completed!")

                decisions = decision_result.get("decisions", [])

            if decisions:

                for index, decision in enumerate(decisions, start=1):

                    with st.expander(
                        f"Decision {index}: {decision.get('decision', 'Untitled')}"
                        ):

                        st.write("**Decision:**")
                        st.write(decision.get("decision", "Not provided"))

                        st.write("**Participants:**")
                        st.write(
                            ", ".join(decision.get("participants", []))
                            or "Not identified"
                            )

                        st.write("**Reason:**")
                        st.write(decision.get("reason", "Not provided"))

                        st.write("**Status:**")
                        st.write(decision.get("status", "Unclear"))

                else:

                    st.info("No explicit decisions were identified.")

                st.subheader("📝 Decision Summary")

                st.write(
                    decision_result.get(
                        "decision_summary",
                        "No decision summary available."
                    )
                )

        except Exception as error:

            st.error(f"Decision extraction failed: {error}")


            # STEP 5: ACTION ITEM EXTRACTION

            st.divider()

            st.subheader("📋 Action Items and Tasks")

            try:

                with st.spinner("Extracting meeting action items..."):

                    action_result = extract_action_items(meeting_data)

                    meeting_data["action_analysis"] = action_result

                    st.session_state["meeting_history"][-1][
                        "action_analysis"
                    ] = action_result

                st.success("Action items extracted successfully!")

                action_items = action_result.get("action_items", [])

                if action_items:

                    for index, item in enumerate(action_items, start=1):

                        with st.expander(
                            f"Task {index}: {item.get('task', 'Untitled task')}"
                        ):

                            st.write("**Task Description:**")
                            st.write(item.get("task", "Not provided"))

                            st.write("**Assigned To:**")
                            st.write(item.get("assigned_to", "Unassigned"))

                            st.write("**Deadline:**")
                            st.write(item.get("deadline", "Not specified"))

                            st.write("**Status:**")
                            st.write(item.get("status", "Unknown"))

                else:

                    st.info("No action items were identified.")

                st.subheader("📝 Action Item Summary")

                st.write(
                    action_result.get(
                        "action_summary",
                        "No action summary available."
                    )
                )

            except Exception as error:

                st.error(f"Action item extraction failed: {error}")


            # STEP 6: DEADLINE AND RESPONSIBLE-PERSON EXTRACTION

            st.divider()

            st.subheader("📅 Deadline and Task Tracker")

            try:

                with st.spinner("Analyzing task deadlines and owners..."):

                    deadline_result = extract_deadlines(meeting_data)

                    meeting_data["deadline_analysis"] = deadline_result

                    st.session_state["meeting_history"][-1][
                        "deadline_analysis"
                    ] = deadline_result

                st.success("Deadline analysis completed!")

                tasks = deadline_result.get("tasks", [])

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Total Tasks",
                    deadline_result.get("total_tasks", len(tasks))
                )

                col2.metric(
                    "Tasks With Deadlines",
                    deadline_result.get("tasks_with_deadlines", 0)
                )

                col3.metric(
                    "Tasks Without Deadlines",
                    deadline_result.get("tasks_without_deadlines", 0)
                )

                if tasks:

                    st.subheader("📋 Task Details")

                    for index, task in enumerate(tasks, start=1):

                        with st.expander(
                            f"Task {index}: {task.get('task', 'Untitled')}"
                        ):

                            st.write(
                                "**Responsible Person:**",
                                task.get("responsible_person", "Unassigned")
                            )

                            st.write(
                                "**Deadline:**",
                                task.get("deadline", "Not specified")
                            )

                            st.write(
                                "**Deadline Status:**",
                                task.get("deadline_status", "Unknown")
                            )

                            st.write(
                                "**Task Status:**",
                                task.get("task_status", "Unknown")
                            )

                else:

                    st.info("No tasks were identified.")

            except Exception as error:

                st.error(f"Deadline extraction failed: {error}")

# MEETING HISTORY
st.divider()

st.header("📂 Meeting History")

if st.session_state["meeting_history"]:

    for index, meeting in enumerate(
        st.session_state["meeting_history"]
    ):

        with st.expander(
            f"Meeting {index + 1}: {meeting['title']}"
        ):

            st.write("**Meeting Transcript:**")

            st.write(meeting["transcript"])
            if meeting.get("decision_analysis"):

                st.divider()

                st.subheader("⚖️ Meeting Decisions")

                st.json(meeting["decision_analysis"])
            
            if meeting.get("action_analysis"):

                st.divider()

                st.subheader("📋 Action Items")

                st.json(meeting["action_analysis"])

            if meeting.get("deadline_analysis"):

                st.divider()

                st.subheader("📅 Deadline and Task Tracker")

                st.json(meeting["deadline_analysis"])
                
            if meeting.get("summary"):

                st.divider()

                st.subheader("🤖 AI Meeting Summary")

                st.markdown(meeting["summary"])

            if meeting.get("speaker_analysis"):

                st.divider()

                st.subheader("👥 Speaker Analysis")

                st.json(meeting["speaker_analysis"])

else:

    st.info("No meetings submitted yet.")

# SAVE MEETING HISTORY

try:

    save_meeting_history(
        st.session_state["meeting_history"]
    )

except Exception as error:

    st.error(f"Meeting history could not be saved: {error}")


# MEETING REPORT DOWNLOADS

st.divider()

st.header("📥 Download Meeting Reports")

meeting_history = st.session_state.get(
    "meeting_history", []
)

if meeting_history:

    selected_meeting_index = st.selectbox(
        "Select Meeting",
        range(len(meeting_history)),
        format_func=lambda index: (
            meeting_history[index].get(
                "title",
                "Untitled Meeting"
            )
        )
    )

    selected_meeting = meeting_history[
        selected_meeting_index
    ]

    col1, col2 = st.columns(2)

    try:

        pdf_report = generate_pdf_report(selected_meeting)

        col1.download_button(
            label="📄 Download PDF Report",
            data=pdf_report,
            file_name="meeting_report.pdf",
            mime="application/pdf"
        )

        excel_report = generate_excel_report(selected_meeting)

        col2.download_button(
            label="📊 Download Excel Report",
            data=excel_report,
            file_name="meeting_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as error:

        st.error(f"Report generation failed: {error}")

else:

    st.info("Submit a meeting before generating reports.")

