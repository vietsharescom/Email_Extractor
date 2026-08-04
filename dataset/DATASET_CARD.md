# DATASET_CARD.md — Email Extractor AI Dataset

Following the "Datasheets for Datasets" framework (Gebru et al.). This card is a
living document — updated as generation batches are added. See `Requirements.md`
(project root) for full system context.

**Status:** Scaffold only — no data rows generated yet.

---

## Motivation

This dataset trains two components of the Email Extractor AI pipeline
(Requirements.md §3): the Stage 3 domain classifier and the Stage 5 NER model
(amount / due date / sender extraction). It exists because no public dataset
matches this task's schema natively (Requirements.md §2.5) — training data is
therefore predominantly synthetic, generated to reflect the structure of real
household/business correspondence (tax notices, credit reports, mortgage
statements, insurance renewals, school correspondence, invoices) without
reproducing any real personal data.

## Composition

- **Rows:** TBD (target: ~100–300 for first batch)
- **Domains covered:** Finance, Administration, Education, Work & Business,
  Home & Family, Health, Personal Growth, Notes (fallback) — see
  Requirements.md §5.3 for coverage priority.
- **Schema:** see `schema/extraction_schema.json`.
- **Splits:** train/val/test, target ratio 70/15/15, stratified by domain
  (Requirements.md NFR-03).

## Collection & Generation Process

| Source type | Description | Status |
|---|---|---|
| `synthetic_llm` | Generated directly by Claude, no external API | Not started |
| `real_redacted_template` | Structure-only reference from fully text-layer-redacted real documents (no real content ever copied) | Not used yet |
| `public_dataset` | `invoice-extraction-dataset-v2` (format reference only), CommonForms (Administration structure), Enron `emails.csv` (negative-class filtering) | Evaluated, not yet incorporated |

For synthetic rows, each record carries `generated_by`, `prompt_version`, and
`created_date` for traceability.

## Preprocessing / Labeling

Each row is labeled with `domain` and `sub_domain` at generation time (not
inferred afterward). `event_type` is **not** independently labeled — it is
derived downstream from NER output (has amount + due_date → `finance_obligation`;
has date only → `schedule`; neither → `note`), per Requirements.md FR-06.

## Known Limitations

- Synthetic data reflects document types the author has personally observed —
  not a statistically representative sample of real-world email.
- No reliable public dataset exists for Insurance/Immigration sub-domains;
  these rely almost entirely on synthetic generation (coverage gap, flagged
  in Requirements.md §9).
- Synthetic text will not reproduce real-world noise: OCR errors, handwriting,
  inconsistent formatting.

## Intended Use / Not Intended Use

- **Intended:** training/evaluation for the AASD 4016/4017 course prototype.
- **Not intended:** production use without further validation; not a
  substitute for a representative real-world email corpus.

## Privacy Statement

No row in this dataset contains real personal, family, or business PII (SIN,
account numbers, real names/addresses, real credit data). Where real documents
were used for structural reference, only layout/pattern was observed — no
real content was copied into any generated row (Requirements.md §5.5).
