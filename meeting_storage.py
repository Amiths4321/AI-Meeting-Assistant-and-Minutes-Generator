
import json
import os
from datetime import datetime


STORAGE_FOLDER = "meeting_data"
STORAGE_FILE = os.path.join(
    STORAGE_FOLDER,
    "meeting_history.json"
)


def save_meeting_history(meeting_history):

    os.makedirs(STORAGE_FOLDER, exist_ok=True)

    with open(
        STORAGE_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            meeting_history,
            file,
            indent=4,
            ensure_ascii=False
        )


def load_meeting_history():

    if not os.path.exists(STORAGE_FILE):
        return []

    try:

        with open(
            STORAGE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if isinstance(data, list):
            return data

        return []

    except (json.JSONDecodeError, OSError):

        return []


def add_meeting_timestamp(meeting_data):

    meeting_data["submitted_at"] = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    return meeting_data
