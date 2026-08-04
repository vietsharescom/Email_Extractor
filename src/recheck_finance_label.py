"""Symmetric check to recheck_noise_with_ner.py: verify every email labeled
SORA/Finance-WorkBusiness actually contains a real currency amount. Keyword
matching ("billing" OR "payment" OR "invoice") also catches marketing copy
that merely mentions those words in passing — this removes the label from
false positives (confirmed no real $ amount found).

Safe by default: dry-run only unless --apply is passed.
"""
import argparse
import base64
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from gmail_client import get_gmail_service, list_message_ids
from organize_inbox import get_or_create_label

MONEY_PATTERN = re.compile(r"(CA\$|US\$|\$|CAD|USD)\s?[\d,]+\.\d{2}")
FINANCE_LABEL_QUERY = "label:sora-finance-workbusiness"
FINANCE_LABEL_NAME = "SORA/Finance-WorkBusiness"


def get_body(service, msg_id):
    msg = service.users().messages().get(userId="me", id=msg_id, format="full").execute()

    def walk(part):
        if part.get("mimeType") == "text/plain" and "data" in part.get("body", {}):
            return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
        for p in part.get("parts", []) or []:
            r = walk(p)
            if r:
                return r
        return None

    return walk(msg["payload"]) or ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    print("Authenticating with Gmail...")
    service = get_gmail_service()

    ids = list_message_ids(service, query=FINANCE_LABEL_QUERY, max_results=500)
    print(f"Re-checking {len(ids)} Finance-WorkBusiness emails for a real $ amount...")

    confirmed, false_positive = [], []
    for msg_id in ids:
        body = get_body(service, msg_id)
        if MONEY_PATTERN.search(body):
            confirmed.append(msg_id)
        else:
            false_positive.append(msg_id)

    print(f"\nConfirmed real bills (has $ amount): {len(confirmed)}")
    print(f"False positives (label matched keyword only, no real $ amount): {len(false_positive)}")

    if not args.apply:
        print("\nDry-run only. Re-run with --apply to remove the Finance-WorkBusiness "
              "label from the false positives (message stays in Inbox, unlabeled).")
        return

    if false_positive:
        finance_id = get_or_create_label(service, FINANCE_LABEL_NAME)
        for msg_id in false_positive:
            service.users().messages().modify(
                userId="me", id=msg_id, body={"removeLabelIds": [finance_id]}
            ).execute()
        print(f"Removed Finance-WorkBusiness label from {len(false_positive)} false positives.")


if __name__ == "__main__":
    main()
