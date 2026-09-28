# Radiology AI Triage API

A backend for prioritizing AI-flagged imaging findings for radiologist review, and for tracking how often the AI is right.

> **Note:** This project uses synthetic data only. No real patient information is stored.

## Why this exists

Hospitals run AI models over X-rays, CT scans, and MRIs to catch findings a radiologist might not get to right away, such as a possible **pneumothorax** (collapsed lung).

The AI doesn't diagnose anything. It flags a possible finding with a confidence score, for example: *"92% confident there's a pneumothorax here."*

### Getting urgent cases seen first

Studies wait in a **worklist** for a radiologist to read them. Without help, that queue is first come, first served, so a collapsed lung or a brain bleed can sit behind a stack of routine scans.

The AI's real value is **reordering that queue** so the most urgent cases come first. It doesn't replace the radiologist: every flag is still reviewed by a human, who either **confirms** it or **rejects** it as a false alarm.

### Knowing whether to trust the AI

Those reviews answer an important question: **how good is the AI, really?**

An AI whose flags radiologists confirm 40% of the time is a very different tool from one with an 85% confirmation rate. Tracking that rate gives a rough, real-world measure of the model's precision, and shows whether its flags deserve to move cases up the queue.

## What it does

1. **Stores** imaging studies and the AI's findings on them.
2. **Serves a prioritized worklist**, so urgent, high-confidence findings appear first.
3. **Records radiologist feedback** and tracks the AI's accuracy over time.

## Setup

```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data --count 20
python manage.py runserver
```

## Models

- **Study** — one imaging exam (`accession_id`, `modality`: XR/CT/MR, `body_part`, `received_at`).
- **AIFinding** — one AI-flagged observation on a study (`label`, `confidence` 0–1, `critical`,
  `review_status`: pending/confirmed/rejected). Linked to `Study` via `ForeignKey(related_name="findings")`.

## Endpoints

| Method | URL | Description |
|---|---|---|
| `GET` | `/findings/worklist/` | Pending findings, ordered critical-first then by highest confidence. |
| `POST` | `/findings/<id>/review/` | Submit a verdict: `{"status": "confirmed"}` or `{"status": "rejected"}`. 400 if already reviewed or status is invalid, 404 if the ID doesn't exist. |
| `GET` | `/findings/stats/` | AI performance summary: reviewed count, confirmed count, confirmation rate. Optional `?modality=XR` filter. |

## Testing

```cmd
python manage.py test
```

Covers double-review (400), missing ID (404), and successful review (200) on `/findings/<id>/review/`.

## Management commands

- `python manage.py seed_data --count N` — generates N fake studies, each with one AI finding.
