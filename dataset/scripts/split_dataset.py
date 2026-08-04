"""Combine all synthetic records under raw/synthetic/, stratify by domain into
train/val/test (70/15/15), write dataset/splits/*.jsonl, and update labels.csv
with the assigned split per record id. Per Requirements.md NFR-03.
"""
import csv
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "raw" / "synthetic"
SPLITS_DIR = ROOT / "splits"
LABELS_CSV = ROOT / "labels.csv"

SEED = 42
RATIOS = {"train": 0.70, "val": 0.15, "test": 0.15}


def load_records():
    records = []
    for path in sorted(RAW_DIR.glob("*/*.json")):
        records.append(json.loads(path.read_text(encoding="utf-8")))
    for path in sorted(RAW_DIR.glob("*/*.jsonl")):
        with path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
    return records


def stratified_split(records):
    rng = random.Random(SEED)
    by_domain = {}
    for r in records:
        by_domain.setdefault(r["domain"], []).append(r)

    splits = {"train": [], "val": [], "test": []}
    for domain, items in by_domain.items():
        items = items[:]
        rng.shuffle(items)
        n = len(items)
        n_train = round(n * RATIOS["train"])
        n_val = round(n * RATIOS["val"])
        # remainder goes to test to keep counts exact
        n_test = n - n_train - n_val
        cursor = 0
        for split_name, count in (("train", n_train), ("val", n_val), ("test", n_test)):
            for r in items[cursor: cursor + count]:
                r["split"] = split_name
                splits[split_name].append(r)
            cursor += count
    return splits


def write_splits(splits):
    SPLITS_DIR.mkdir(parents=True, exist_ok=True)
    for name, items in splits.items():
        out_path = SPLITS_DIR / f"{name}.jsonl"
        with out_path.open("w", encoding="utf-8") as f:
            for r in items:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")


def update_labels_csv(all_records):
    by_id = {r["id"]: r for r in all_records}
    fieldnames = ["id", "domain", "sub_domain", "event_type", "source_type",
                  "based_on_template", "split", "created_date"]
    rows = []
    for r in by_id.values():
        rows.append({
            "id": r["id"],
            "domain": r["domain"],
            "sub_domain": r["sub_domain"],
            "event_type": r["event_type"],
            "source_type": r["source_type"],
            "based_on_template": r.get("based_on_template") or "",
            "split": r.get("split") or "",
            "created_date": r["created_date"],
        })
    rows.sort(key=lambda r: r["id"])
    with LABELS_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    records = load_records()
    splits = stratified_split(records)
    write_splits(splits)
    all_records = splits["train"] + splits["val"] + splits["test"]
    update_labels_csv(all_records)

    print(f"Total records: {len(all_records)}")
    for name in ("train", "val", "test"):
        print(f"  {name}: {len(splits[name])}")
    print("\nPer-domain breakdown:")
    domains = sorted({r["domain"] for r in all_records})
    for d in domains:
        counts = {name: sum(1 for r in splits[name] if r["domain"] == d) for name in splits}
        print(f"  {d}: train={counts['train']} val={counts['val']} test={counts['test']}")


if __name__ == "__main__":
    main()
