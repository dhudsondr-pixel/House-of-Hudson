"""
Schedule a WhatsApp message to a group.

Setup (one time):
  1. pip install -r requirements.txt
  2. On your S26 Ultra: WhatsApp -> Linked Devices -> Link a Device.
     Scan the QR code that opens in your browser the first time the script runs.
  3. In the WhatsApp group on your phone:
        Group info -> Invite via link -> Copy link.
     The GROUP_ID is the part after "https://chat.whatsapp.com/".

Run:
  python schedule_whatsapp.py
The script will wait until the scheduled time, open WhatsApp Web,
type the message, and press send.

Notes:
  - The computer must stay awake and online until the send time.
  - Do not move the mouse or switch windows while it's sending.
"""

from datetime import datetime, timedelta
import sys
import pywhatkit


GROUP_ID = "PUT_YOUR_GROUP_INVITE_SUFFIX_HERE"
MESSAGE = "Good morning everyone!"
SEND_HOUR = 9
SEND_MINUTE = 0
WAIT_BEFORE_SEND_SECONDS = 20
TAB_CLOSE_AFTER_SECONDS = 5


def schedule_for_tomorrow_morning() -> tuple[int, int]:
    target = (datetime.now() + timedelta(days=1)).replace(
        hour=SEND_HOUR, minute=SEND_MINUTE, second=0, microsecond=0
    )
    if target <= datetime.now() + timedelta(minutes=2):
        print("Scheduled time is in the past or too soon. Adjust SEND_HOUR/SEND_MINUTE.")
        sys.exit(1)
    print(f"Scheduled to send at {target.isoformat()} to group {GROUP_ID!r}.")
    return target.hour, target.minute


def main() -> None:
    if GROUP_ID == "PUT_YOUR_GROUP_INVITE_SUFFIX_HERE":
        print("Edit GROUP_ID in schedule_whatsapp.py before running.")
        sys.exit(1)

    hour, minute = schedule_for_tomorrow_morning()
    pywhatkit.sendwhatmsg_to_group(
        group_id=GROUP_ID,
        message=MESSAGE,
        time_hour=hour,
        time_min=minute,
        wait_time=WAIT_BEFORE_SEND_SECONDS,
        tab_close=True,
        close_time=TAB_CLOSE_AFTER_SECONDS,
    )
    print("Message dispatched (or queued for the scheduled time).")


if __name__ == "__main__":
    main()
