"""High-stakes keyword override — scans the FULL mailbox (not just noise/
billing buckets) for rare-but-critical content that frequency/reciprocity
stats can never catch (by definition: rare events have low frequency).

Any match gets SORA/Needs-Review + Starred, regardless of sender history,
frequency, or which bucket it already landed in. Cost of a false positive
here (user glances at an unimportant email) is near zero; cost of a false
negative (missed work permit deadline) is severe — so this deliberately
runs wide, not precise.

Safe by default: dry-run only unless --apply is passed.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from gmail_client import get_gmail_service, list_message_ids, get_message_summary
from organize_inbox import get_or_create_label

# Keep this list editable — Andy should extend it over time as new
# high-stakes categories come up (legal, health emergencies, etc.)
CRITICAL_TERMS = {
    "Administration/immigration": [
        "work permit", "permanent resident", "pr card", "deportation",
        "biometric", "citizenship", "ircc", "oinp", "pnp", "study permit",
        "cbsa", "immigration", "visa application", "expression of interest",
    ],
    "Administration/legal": [
        "court date", "lawsuit", "subpoena", "eviction notice", "legal notice",
    ],
}

REVIEW_LABEL_NAME = "SORA/Needs-Review"


def build_query(days):
    all_terms = [t for terms in CRITICAL_TERMS.values() for t in terms]
    quoted = [f'"{t}"' if " " in t else t for t in all_terms]
    return "(" + " OR ".join(quoted) + f") newer_than:{days}d"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=365)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    print("Authenticating with Gmail...")
    service = get_gmail_service()

    query = build_query(args.days)
    print(f"Scanning full mailbox (last {args.days}d) for high-stakes keywords...")
    ids = list_message_ids(service, query=query, max_results=200)

    print(f"\nFound {len(ids)} messages matching critical-term list:")
    for i in ids:
        s = get_message_summary(service, i)
        print(f"  {s['sender_email']:35} | {s['subject'][:70]} | labels={s['label_ids']}")

    if not args.apply:
        print("\nDry-run only. Re-run with --apply to label these as Needs-Review + Star.")
        return

    if not ids:
        print("\nNothing to apply.")
        return

    review_id = get_or_create_label(service, REVIEW_LABEL_NAME)
    for msg_id in ids:
        service.users().messages().modify(
            userId="me", id=msg_id,
            body={"addLabelIds": [review_id, "STARRED", "INBOX"]},
        ).execute()
    print(f"\nApplied Needs-Review + Star to {len(ids)} messages.")


if __name__ == "__main__":
    main()
