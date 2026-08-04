"""Apply the 3-category action plan from the inbox audit:
  - noise     -> label 'SORA/Archived-Noise' + remove from Inbox (archive, NOT delete)
  - billing   -> label 'SORA/Finance-WorkBusiness', kept in Inbox
  - important -> label 'SORA/Needs-Review' + Starred, kept in Inbox

Safe by default: dry-run only (just counts/prints what WOULD happen).
Pass --apply to actually modify the mailbox. Requires gmail.modify scope.
Nothing is ever permanently deleted by this script.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from gmail_client import get_gmail_service, list_message_ids

NOISE_SENDER_DOMAINS = [
    "github.com", "e.atlassian.com", "sinayavarian.atlassian.net",
    "po.atlassian.net", "id.atlassian.com", "vercel.com",
]

BILLING_QUERIES = [
    "from:mail.anthropic.com (invoice OR receipt)",
    "from:google.com (billing OR invoice OR payment)",
    "from:openrouter.ai (billing OR invoice OR payment OR receipt)",
]

IMPORTANT_SENDERS = [
    "hvu0803@gmail.com",
    "andykingcity@gmail.com",
    "truongthuy031994@gmail.com",
]

LABEL_NAMES = {
    "noise": "SORA/Archived-Noise",
    "billing": "SORA/Finance-WorkBusiness",
    "important": "SORA/Needs-Review",
}


def get_or_create_label(service, name):
    labels = service.users().labels().list(userId="me").execute().get("labels", [])
    for l in labels:
        if l["name"] == name:
            return l["id"]
    label = service.users().labels().create(
        userId="me",
        body={"name": name, "labelListVisibility": "labelShow", "messageListVisibility": "show"},
    ).execute()
    return label["id"]


def find_messages(service, query, days, max_results=500):
    return list_message_ids(service, query=f"{query} newer_than:{days}d", max_results=max_results)


def build_plan(service, days):
    noise_query = "(" + " OR ".join(f"from:{d}" for d in NOISE_SENDER_DOMAINS) + ")"
    noise_ids = find_messages(service, noise_query, days)

    billing_ids = set()
    for q in BILLING_QUERIES:
        billing_ids.update(find_messages(service, q, days))

    important_query = "(" + " OR ".join(f"from:{s}" for s in IMPORTANT_SENDERS) + ")"
    important_ids = find_messages(service, important_query, days)

    return {"noise": noise_ids, "billing": list(billing_ids), "important": important_ids}


def apply_plan(service, plan):
    label_ids = {cat: get_or_create_label(service, name) for cat, name in LABEL_NAMES.items()}

    for msg_id in plan["noise"]:
        service.users().messages().modify(
            userId="me", id=msg_id,
            body={"addLabelIds": [label_ids["noise"]], "removeLabelIds": ["INBOX"]},
        ).execute()

    for msg_id in plan["billing"]:
        service.users().messages().modify(
            userId="me", id=msg_id,
            body={"addLabelIds": [label_ids["billing"]]},
        ).execute()

    for msg_id in plan["important"]:
        service.users().messages().modify(
            userId="me", id=msg_id,
            body={"addLabelIds": [label_ids["important"], "STARRED"]},
        ).execute()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=180)
    parser.add_argument("--apply", action="store_true",
                         help="actually modify the mailbox; default is dry-run preview only")
    args = parser.parse_args()

    print("Authenticating with Gmail (modify scope)...")
    service = get_gmail_service()

    print(f"Building plan (last {args.days} days)...")
    plan = build_plan(service, args.days)

    print("\n=== PLAN ===")
    print(f"noise     (label + archive): {len(plan['noise'])} messages")
    print(f"billing   (label, keep in Inbox): {len(plan['billing'])} messages")
    print(f"important (label + star, keep in Inbox): {len(plan['important'])} messages")

    if not args.apply:
        print("\nDry-run only — mailbox NOT modified. Re-run with --apply to execute.")
        return

    print("\nApplying labels/archive to real mailbox...")
    apply_plan(service, plan)
    print("Done. Nothing was permanently deleted — 'noise' messages were archived "
          "(removed from Inbox) but remain searchable under label "
          f"'{LABEL_NAMES['noise']}'.")


if __name__ == "__main__":
    main()
