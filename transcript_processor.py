
import re


def clean_transcript(transcript):

    if not isinstance(transcript, str):
        raise TypeError("Transcript must be text.")

    if not transcript.strip():
        return ""

    # Normalize Windows and Unix line endings
    transcript = transcript.replace("\r\n", "\n")
    transcript = transcript.replace("\r", "\n")

    # Remove unwanted control characters
    transcript = re.sub(
        r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]",
        "",
        transcript
    )

    # Remove leading and trailing spaces from each line
    lines = [
        line.strip()
        for line in transcript.split("\n")
    ]

    # Remove repeated blank lines
    cleaned_lines = []
    previous_blank = False

    for line in lines:

        if not line:
            if not previous_blank:
                cleaned_lines.append("")

            previous_blank = True

        else:
            cleaned_lines.append(line)
            previous_blank = False

    transcript = "\n".join(cleaned_lines)

    # Normalize repeated spaces and tabs
    transcript = re.sub(r"[ \t]+", " ", transcript)

    return transcript.strip()


def get_transcript_statistics(transcript):

    words = transcript.split()

    return {
        "character_count": len(transcript),
        "word_count": len(words),
        "line_count": len(transcript.splitlines())
    }
