"""Layer 0 (Ingest) + Layer 1 (Spam/Trash Gate) + Layer 2 (Mailbox-Wide
Statistical Audit) — run once against a real Gmail inbox to produce a ranked
sender importance report, per Requirements.md pipeline design.

Usage:
    python src/inbox_audit.py [--days 180] [--max 1000] [--top 30]

Requires credentials.json in the project root (see README instructions).
Writes results to inbox_audit_output/ (gitignored, never committed).
"""
import argparse
import csv
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

sys.path.insert(0, os.path.dirname(__file__))
from gmail_client import get_gmail_service, list_message_ids, get_message_summary

OUTPUT_DIR = "inbox_audit_output"


def layer1_is_junk(label_ids):
    """Spam/Trash gate — reuse Gmail's own classification, no model."""
    return "SPAM" in label_ids or "TRASH" in label_ids


def parse_date_safe(date_str):
    try:
        return parsedate_to_datetime(date_str)
    except Exception:
        return None


def layer2_statistical_audit(messages, top_n_for_reciprocity, service):
    """Compute per-sender frequency/recency stats, then reciprocity for the
    top N senders by volume only (keeps API calls bounded)."""
    by_sender = defaultdict(list)
    for m in messages:
        by_sender[m["sender_email"]].append(m)

    rows = []
    for sender, msgs in by_sender.items():
        dates = [parse_date_safe(m["date"]) for m in msgs]
        dates = [d for d in dates if d is not None]
        rows.append({
            "sender_email": sender,
            "sender_domain": msgs[0]["sender_domain"],
            "sender_name": msgs[0]["sender_name"],
            "count": len(msgs),
            "first_seen": min(dates).isoformat() if dates else "",
            "last_seen": max(dates).isoformat() if dates else "",
            "sample_subject": msgs[0]["subject"],
        })

    rows.sort(key=lambda r: r["count"], reverse=True)
    total = sum(r["count"] for r in rows)

    # Reciprocity: only check the top-N by volume (keeps this fast)
    for r in rows[:top_n_for_reciprocity]:
        query = f'in:sent to:{r["sender_domain"]}'
        try:
            sent_ids = list_message_ids(service, query=query, max_results=1)
            r["ever_replied"] = bool(sent_ids)
        except Exception:
            r["ever_replied"] = "unknown"
    for r in rows[top_n_for_reciprocity:]:
        r["ever_replied"] = "not_checked"

    for r in rows:
        r["pct_of_inbox"] = round(100 * r["count"] / total, 2) if total else 0.0

    return rows, total


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=180, help="how far back to scan")
    parser.add_argument("--max", type=int, default=1000, help="max messages to fetch")
    parser.add_argument("--top", type=int, default=30, help="top N senders to check reciprocity for")
    args = parser.parse_args()

    print("Authenticating with Gmail...")
    service = get_gmail_service()

    query = f"newer_than:{args.days}d"
    print(f"Listing message ids ({query}, max {args.max})...")
    ids = list_message_ids(service, query=query, max_results=args.max)
    print(f"Found {len(ids)} messages. Fetching metadata (Layer 0)...")

    kept, junk_count = [], 0
    for i, msg_id in enumerate(ids, 1):
        summary = get_message_summary(service, msg_id)
        if layer1_is_junk(summary["label_ids"]):
            junk_count += 1
            continue
        kept.append(summary)
        if i % 50 == 0:
            print(f"  ...{i}/{len(ids)} processed")

    print(f"Layer 1 (spam/trash gate): kept {len(kept)}, discarded {junk_count} junk")
    print(f"Layer 2 (statistical audit): computing sender stats "
          f"(reciprocity checked for top {args.top} senders)...")
    rows, total = layer2_statistical_audit(kept, args.top, service)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, "sender_stats.csv")
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "sender_email", "sender_domain", "sender_name", "count",
            "pct_of_inbox", "ever_replied", "first_seen", "last_seen", "sample_subject",
        ])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSaved full report: {out_path}")
    print(f"\n=== Top {min(20, len(rows))} senders by volume (of {total} kept emails) ===")
    print(f"{'sender':40} {'count':>6} {'%':>6} {'replied?':>10}")
    for r in rows[:20]:
        print(f"{r['sender_email'][:40]:40} {r['count']:>6} {r['pct_of_inbox']:>5.1f}% {str(r['ever_replied']):>10}")


if __name__ == "__main__":
    main()
