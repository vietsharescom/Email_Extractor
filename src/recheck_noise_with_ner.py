"""Cross-check every email already labeled SORA/Archived-Noise for a real
monetary amount — anything matching gets pulled OUT of noise into
SORA/Needs-Review, since sender-domain rules alone can miss real financial
content buried in a 'noisy' sender.

NOTE: an earlier version used spaCy's en_core_web_sm for this (generic
pretrained NER). Tested against real email bodies from this mailbox, it
produced ~60% false positives (e.g. tagging "2 annotations" as MONEY) and
also MISSED the real currency format used here ("CA$31.64" — no space).
A targeted regex is more reliable for this narrow, well-defined pattern
than a small generic NER model — see dataset.md session log for the
before/after comparison.

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

NOISE_LABEL_QUERY = "label:sora-archived-noise"
REVIEW_LABEL_NAME = "SORA/Needs-Review"
NOISE_LABEL_NAME = "SORA/Archived-Noise"


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
    parser.add_argument("--apply", action="store_true",
                         help="actually move flagged messages from noise to Needs-Review")
    parser.add_argument("--max", type=int, default=1000)
    args = parser.parse_args()

    print("Authenticating with Gmail...")
    service = get_gmail_service()

    ids = list_message_ids(service, query=NOISE_LABEL_QUERY, max_results=args.max)
    print(f"Re-checking {len(ids)} archived-noise emails for real currency amounts...")

    flagged = []
    for i, msg_id in enumerate(ids, 1):
        body = get_body(service, msg_id)[:1500]
        money_matches = MONEY_PATTERN.findall(body)
        if money_matches:
            flagged.append((msg_id, money_matches))
        if i % 50 == 0:
            print(f"  ...{i}/{len(ids)} checked, {len(flagged)} flagged so far")

    print(f"\n=== RESULT ===")
    print(f"Total archived-noise re-checked: {len(ids)}")
    print(f"Flagged (contains MONEY entity, likely mis-archived): {len(flagged)}")
    print(f"Confirmed noise (no MONEY entity): {len(ids) - len(flagged)}")

    if flagged:
        print("\nSample flagged messages:")
        for msg_id, ents in flagged[:15]:
            print(f"  {msg_id} -> MONEY entities: {ents}")

    if not args.apply:
        print("\nDry-run only — no labels changed. Re-run with --apply to move "
              "flagged messages: Archived-Noise -> Needs-Review (+ restore to Inbox).")
        return

    if not flagged:
        print("\nNothing to move.")
        return

    noise_id = get_or_create_label(service, NOISE_LABEL_NAME)
    review_id = get_or_create_label(service, REVIEW_LABEL_NAME)
    for msg_id, _ in flagged:
        service.users().messages().modify(
            userId="me", id=msg_id,
            body={
                "addLabelIds": [review_id, "INBOX", "STARRED"],
                "removeLabelIds": [noise_id],
            },
        ).execute()
    print(f"\nMoved {len(flagged)} messages: Archived-Noise -> Needs-Review (restored to Inbox, starred).")


if __name__ == "__main__":
    main()
