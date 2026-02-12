# Quick Start Guide

## Running the Analysis

From the project root directory (`/Users/admin/be:impact`):

### Step 1: Analyze Feedback Data
```bash
python scripts/analyze_trainer_feedback.py
```

This generates:
- `outputs/results.json` - Structured data
- `outputs/results.csv` - Spreadsheet format
- `outputs/results.html` - Professional report (opens in browser)

### Step 2: Generate Outreach Emails
```bash
python scripts/generate_outreach.py
```

This generates:
- `outputs/outreach_ready.json` - Ready-to-send email templates

### Alternative: Use the convenience script
```bash
./scripts/run_analysis.sh
```

---

## File Locations

- **Input Data:** `data/export_Learner-Feedback-for-Trainers_*.csv`
- **Scripts:** `scripts/`
- **Outputs:** `outputs/`
- **Assets:** `assets/` (images, etc.)

---

## Important Notes

✓ Always run scripts from the project root
✓ Python environment: Use `python` (conda) not `python3`
✓ All outputs auto-regenerate with latest data
✓ Email templates need [Your name] personalization

---

Need more details? See `README.md`
