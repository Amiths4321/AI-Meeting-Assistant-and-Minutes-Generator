
from io import BytesIO
import pandas as pd

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.units import inch


def generate_pdf_report(meeting):

    output = BytesIO()

    document = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    content = []

    def add_section(title, text):
        content.append(Paragraph(title, styles["Heading2"]))
        content.append(Paragraph(str(text), styles["BodyText"]))
        content.append(Spacer(1, 12))

    title = meeting.get("title", "Untitled Meeting")

    content.append(
        Paragraph("AI Meeting Report", styles["Title"])
    )

    content.append(Spacer(1, 15))

    add_section("Meeting Title", title)

    add_section(
        "Submission Date",
        meeting.get("submitted_at", "Not available")
    )

    add_section(
        "Meeting Transcript",
        meeting.get("transcript", "Not available").replace(
            "\n", "<br/>"
        )
    )

    add_section(
        "AI Meeting Summary",
        meeting.get("summary", "No summary available").replace(
            "\n", "<br/>"
        )
    )

    speaker_analysis = meeting.get("speaker_analysis", {})

    content.append(
        Paragraph("Speaker Analysis", styles["Heading2"])
    )

    for speaker in speaker_analysis.get("speakers", []):

        speaker_text = (
            f"<b>{speaker.get('name', 'Unknown')}</b><br/>"
            f"Topics: {', '.join(speaker.get('topics_discussed', []))}<br/>"
            f"Contributions: "
            f"{'; '.join(speaker.get('contributions', []))}<br/>"
            f"Questions: "
            f"{'; '.join(speaker.get('questions_or_concerns', []))}"
        )

        content.append(
            Paragraph(speaker_text, styles["BodyText"])
        )

        content.append(Spacer(1, 8))

    decision_analysis = meeting.get("decision_analysis", {})

    content.append(
        Paragraph("Meeting Decisions", styles["Heading2"])
    )

    for decision in decision_analysis.get("decisions", []):

        decision_text = (
            f"<b>Decision:</b> {decision.get('decision', '')}<br/>"
            f"<b>Participants:</b> "
            f"{', '.join(decision.get('participants', []))}<br/>"
            f"<b>Status:</b> {decision.get('status', 'Unclear')}"
        )

        content.append(
            Paragraph(decision_text, styles["BodyText"])
        )

        content.append(Spacer(1, 8))

    action_analysis = meeting.get("action_analysis", {})
    deadline_analysis = meeting.get("deadline_analysis", {})

    content.append(
        Paragraph("Action Items and Deadlines", styles["Heading2"])
    )

    tasks = deadline_analysis.get("tasks", [])

    if tasks:
        task_data = [
            ["Task", "Responsible Person", "Deadline", "Status"]
        ]

        for task in tasks:
            task_data.append([
                task.get("task", ""),
                task.get("responsible_person", ""),
                task.get("deadline", ""),
                task.get("task_status", "")
            ])

        task_table = Table(
            task_data,
            colWidths=[2.2 * inch, 1.3 * inch, 1 * inch, 1 * inch],
            repeatRows=1
        )

        task_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("PADDING", (0, 0), (-1, -1), 6)
        ]))

        content.append(task_table)

    else:
        for item in action_analysis.get("action_items", []):
            content.append(
                Paragraph(
                    str(item.get("task", "")),
                    styles["BodyText"]
                )
            )

    document.build(content)

    output.seek(0)

    return output.getvalue()


def generate_excel_report(meeting):

    output = BytesIO()

    speakers = meeting.get("speaker_analysis", {}).get(
        "speakers", []
    )

    decisions = meeting.get("decision_analysis", {}).get(
        "decisions", []
    )

    actions = meeting.get("deadline_analysis", {}).get(
        "tasks", []
    )

    if not actions:
        actions = meeting.get("action_analysis", {}).get(
            "action_items", []
        )

    with pd.ExcelWriter(output, engine="openpyxl") as writer:

        overview = pd.DataFrame([{
            "Meeting Title": meeting.get("title", ""),
            "Submitted At": meeting.get("submitted_at", ""),
            "Transcript": meeting.get("transcript", ""),
            "Summary": meeting.get("summary", "")
        }])

        overview.to_excel(
            writer,
            sheet_name="Overview",
            index=False
        )

        speaker_data = []

        for speaker in speakers:
            speaker_data.append({
                "Speaker": speaker.get("name", ""),
                "Topics": "; ".join(
                    speaker.get("topics_discussed", [])
                ),
                "Contributions": "; ".join(
                    speaker.get("contributions", [])
                ),
                "Questions": "; ".join(
                    speaker.get("questions_or_concerns", [])
                )
            })

        pd.DataFrame(speaker_data).to_excel(
            writer,
            sheet_name="Speakers",
            index=False
        )

        decision_data = []

        for decision in decisions:
            decision_data.append({
                "Decision": decision.get("decision", ""),
                "Participants": "; ".join(
                    decision.get("participants", [])
                ),
                "Reason": decision.get("reason", ""),
                "Status": decision.get("status", "")
            })

        pd.DataFrame(decision_data).to_excel(
            writer,
            sheet_name="Decisions",
            index=False
        )

        task_data = []

        for task in actions:
            task_data.append({
                "Task": task.get("task", ""),
                "Responsible Person": task.get(
                    "responsible_person",
                    task.get("assigned_to", "Unassigned")
                ),
                "Deadline": task.get("deadline", "Not specified"),
                "Status": task.get(
                    "task_status",
                    task.get("status", "Unknown")
                )
            })

        pd.DataFrame(task_data).to_excel(
            writer,
            sheet_name="Action Items",
            index=False
        )

        # Format worksheets
        for worksheet in writer.sheets.values():

            worksheet.freeze_panes = "A2"
            worksheet.auto_filter.ref = worksheet.dimensions

            for column in worksheet.columns:

                column_letter = column[0].column_letter

                max_length = max(
                    len(str(cell.value or ""))
                    for cell in column
                )

                worksheet.column_dimensions[
                    column_letter
                ].width = min(max(max_length + 2, 12), 45)

    output.seek(0)

    return output.getvalue()
