#!/usr/bin/env python
"""
Analyze trainer feedback CSV to identify top improving trainers.
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path


def clean_numeric(val):
    """Convert value to float, handling nan and non-numeric values."""
    try:
        if pd.isna(val) or val == '' or val == 'nan':
            return np.nan
        return float(val)
    except (ValueError, TypeError):
        return np.nan


def extract_positive_quotes(df, text_cols):
    """Extract positive quotes from text columns."""
    quotes = []

    for col in text_cols:
        if col in df.columns:
            for idx, row in df.iterrows():
                text = row[col]
                row_id = row['row_id']

                # Skip empty/nan values
                if pd.isna(text) or text == '' or text == 'nan' or text == '-':
                    continue

                # Skip short responses
                text_str = str(text).strip()
                if len(text_str) < 20:
                    continue

                # Look for positive indicators
                positive_keywords = ['excellent', 'great', 'love', 'helpful', 'enjoyed',
                                   'beneficial', 'best', 'appreciated', 'wonderful',
                                   'positive', 'fun', 'engaging', 'motivated', 'patient',
                                   'clear', 'friendly', 'approachable', 'flexible']

                text_lower = text_str.lower()
                has_positive = any(keyword in text_lower for keyword in positive_keywords)

                if has_positive:
                    # Limit quote length for readability
                    if len(text_str) > 200:
                        text_str = text_str[:200] + "..."

                    quotes.append({
                        'row_id': row_id,
                        'quote': text_str,
                        'source_column': col
                    })

    return quotes


def generate_html_report(results):
    """Generate an HTML report from the results."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trainer Improvement Analysis</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
            color: #1a1a1a;
            padding: 0;
            min-height: 100vh;
        }
        .header {
            background: linear-gradient(135deg, #001f5c 0%, #002d7a 100%);
            color: white;
            padding: 60px 40px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0, 31, 92, 0.15);
        }
        .header h1 {
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: 15px;
            letter-spacing: -0.5px;
        }
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
            max-width: 700px;
            margin: 0 auto;
            font-weight: 300;
        }
        .container {
            max-width: 1200px;
            margin: -30px auto 60px;
            padding: 0 40px;
        }
        .trainer-card {
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
            margin-bottom: 30px;
            overflow: hidden;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .trainer-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        .card-header {
            padding: 35px 40px 25px;
            border-bottom: 1px solid #f0f0f0;
        }
        .rank-badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            font-weight: 700;
            font-size: 1.1em;
            margin-bottom: 15px;
            color: white;
        }
        .rank-1 {
            background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
            box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);
        }
        .rank-2 {
            background: linear-gradient(135deg, #C0C0C0 0%, #A8A8A8 100%);
            box-shadow: 0 4px 12px rgba(192, 192, 192, 0.3);
        }
        .trainer-name {
            font-size: 1.6em;
            font-weight: 600;
            color: #001f5c;
            margin: 10px 0;
        }
        .card-body {
            padding: 30px 40px;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 20px;
            margin-bottom: 35px;
        }
        .metric {
            background: #f8f9fb;
            padding: 24px 20px;
            border-radius: 12px;
            text-align: center;
            border: 1px solid #e8ecf1;
            transition: all 0.2s ease;
        }
        .metric:hover {
            background: #f0f2f5;
            transform: translateY(-2px);
        }
        .metric-label {
            font-size: 0.75em;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
            font-weight: 600;
        }
        .metric-value {
            font-size: 2em;
            font-weight: 700;
            color: #001f5c;
            line-height: 1;
        }
        .improvement-positive {
            color: #10b981;
        }
        .case-study {
            background: linear-gradient(135deg, #e6f7ed 0%, #d1f0dd 100%);
            border-radius: 12px;
            padding: 24px 28px;
            margin-bottom: 35px;
            border-left: 5px solid #10b981;
            position: relative;
        }
        .case-study::before {
            content: "💡";
            font-size: 1.5em;
            position: absolute;
            top: 20px;
            right: 24px;
            opacity: 0.3;
        }
        .case-study-label {
            font-size: 0.75em;
            text-transform: uppercase;
            color: #059669;
            font-weight: 700;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }
        .case-study-text {
            color: #064e3b;
            font-size: 1.05em;
            line-height: 1.6;
            font-weight: 500;
        }
        .section-title {
            font-size: 1.3em;
            font-weight: 600;
            color: #001f5c;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
        }
        .section-title::before {
            content: "";
            display: inline-block;
            width: 4px;
            height: 24px;
            background: linear-gradient(135deg, #e91e63 0%, #ff1493 100%);
            border-radius: 2px;
            margin-right: 12px;
        }
        .quote {
            background: white;
            border: 2px solid #f0f0f0;
            border-radius: 12px;
            padding: 24px 28px;
            margin-bottom: 20px;
            position: relative;
            transition: all 0.2s ease;
        }
        .quote:hover {
            border-color: #e91e63;
            box-shadow: 0 4px 16px rgba(233, 30, 99, 0.1);
        }
        .quote::before {
            content: "\\201C";
            font-size: 4em;
            color: #f0f0f0;
            position: absolute;
            top: 10px;
            left: 20px;
            font-family: Georgia, serif;
            line-height: 1;
        }
        .quote-text {
            color: #374151;
            line-height: 1.7;
            font-size: 1.05em;
            padding-left: 40px;
            position: relative;
        }
        .quote-meta {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-top: 16px;
            padding-left: 40px;
            font-size: 0.85em;
        }
        .row-id {
            background: linear-gradient(135deg, #e91e63 0%, #ff1493 100%);
            color: white;
            padding: 4px 12px;
            border-radius: 6px;
            font-family: 'SF Mono', 'Monaco', 'Menlo', monospace;
            font-size: 0.9em;
            font-weight: 600;
            letter-spacing: 0.5px;
        }
        .source-label {
            color: #9ca3af;
            font-size: 0.95em;
        }
        footer {
            text-align: center;
            padding: 40px 20px;
            color: #6b7280;
            font-size: 0.9em;
        }
        footer .logo {
            font-weight: 700;
            color: #001f5c;
            font-size: 1.2em;
            margin-bottom: 8px;
        }
        @media (max-width: 768px) {
            .header {
                padding: 40px 20px;
            }
            .header h1 {
                font-size: 1.8em;
            }
            .container {
                padding: 0 20px;
            }
            .card-header, .card-body {
                padding: 25px 20px;
            }
            .metrics-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Trainer Improvement Analysis</h1>
        <p>Top performing trainers showing the greatest improvement in participant feedback scores over time</p>
    </div>

    <div class="container">
"""

    for result in results:
        rank_class = f"rank-{result['rank']}"
        improvement_sign = "+" if result['improvement_score'] >= 0 else ""

        html += f"""
        <div class="trainer-card">
            <div class="card-header">
                <div class="rank-badge {rank_class}">#{result['rank']}</div>
                <div class="trainer-name">{result['trainer_name']}</div>
            </div>

            <div class="card-body">
                <div class="metrics-grid">
                    <div class="metric">
                        <div class="metric-label">Responses</div>
                        <div class="metric-value">{result['n_responses']}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Early Score</div>
                        <div class="metric-value">{result['mean_early_score']:.2f}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Late Score</div>
                        <div class="metric-value">{result['mean_late_score']:.2f}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Improvement</div>
                        <div class="metric-value improvement-positive">{improvement_sign}{result['improvement_score']:.3f}</div>
                    </div>
                </div>

                <div class="case-study">
                    <div class="case-study-label">Case Study Angle</div>
                    <div class="case-study-text">{result['case_study_angle']}</div>
                </div>

                <div class="section-title">Positive Feedback</div>
"""

        for i, quote in enumerate(result['quotes'], 1):
            source_clean = quote['source'].split('_', 1)[1] if '_' in quote['source'] else quote['source']
            source_clean = source_clean.replace('*', '').strip()
            html += f"""
                <div class="quote">
                    <div class="quote-text">{quote['quote']}</div>
                    <div class="quote-meta">
                        <span class="row-id">{quote['row_id']}</span>
                        <span class="source-label">{source_clean}</span>
                    </div>
                </div>
"""

        html += """
            </div>
        </div>
"""

    html += """
    </div>

    <footer>
        <div class="logo">be/impact</div>
        <p>Trainer Feedback Analysis System</p>
    </footer>
</body>
</html>
"""
    return html


def main():
    # Load CSV
    csv_path = Path('data/export_Learner-Feedback-for-Trainers_2026-01-30_15-55-17_anonymised.csv')
    print(f"Loading CSV: {csv_path}")

    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} records")

    # Assign stable row_id
    df['row_id'] = [f"R{i:04d}" for i in range(1, len(df) + 1)]

    # Parse Creation Date
    df['creation_datetime'] = pd.to_datetime(df['Creation Date'], format='%b %d, %Y %I:%M %p', errors='coerce')

    # Define numeric score columns
    score_cols = ['1.3', '1.4', '2.8', '2.9', 'v1_1.2', 'v2_1.1', 'v2_1.2']

    # Get actual column names (they have full text descriptions)
    actual_score_cols = []
    for score_col in score_cols:
        matching_cols = [col for col in df.columns if col.startswith(score_col)]
        if matching_cols:
            actual_score_cols.append(matching_cols[0])

    print(f"\nScore columns found: {actual_score_cols}")

    # Clean and convert score columns to numeric
    for col in actual_score_cols:
        df[col] = df[col].apply(clean_numeric)

    # Compute composite score (average of available scores per row)
    df['composite_score'] = df[actual_score_cols].mean(axis=1, skipna=True)

    # Filter out rows with no trainer or no valid creation date
    df = df[df['Trainer'].notna() & df['creation_datetime'].notna()].copy()

    print(f"\nRecords with valid trainer and date: {len(df)}")

    # Group by trainer
    trainer_stats = []

    for trainer, group in df.groupby('Trainer'):
        n_responses = len(group)

        # Only process trainers with >= 3 responses
        if n_responses < 3:
            continue

        # Sort by date
        group = group.sort_values('creation_datetime')

        # Split into early and late halves
        mid_point = len(group) // 2
        early_half = group.iloc[:mid_point]
        late_half = group.iloc[mid_point:]

        # Calculate mean scores for each half
        early_scores = early_half['composite_score'].dropna()
        late_scores = late_half['composite_score'].dropna()

        if len(early_scores) > 0 and len(late_scores) > 0:
            mean_early = early_scores.mean()
            mean_late = late_scores.mean()
            improvement = mean_late - mean_early

            trainer_stats.append({
                'trainer': trainer,
                'n_responses': n_responses,
                'mean_early': mean_early,
                'mean_late': mean_late,
                'improvement': improvement,
                'group_df': group
            })

    # Sort by improvement (descending)
    trainer_stats.sort(key=lambda x: x['improvement'], reverse=True)

    print(f"\nTrainers with >= 3 responses: {len(trainer_stats)}")

    # Select top 2
    top_2 = trainer_stats[:2]

    # Text columns for quotes
    text_cols = [col for col in df.columns if '3.12' in col or '3.13' in col]

    print(f"\nText columns for quotes: {text_cols}")

    # Build results
    results = []

    for idx, trainer_data in enumerate(top_2, 1):
        trainer = trainer_data['trainer']
        n_responses = trainer_data['n_responses']
        improvement = trainer_data['improvement']
        group_df = trainer_data['group_df']

        print(f"\n{'='*60}")
        print(f"Top {idx}: {trainer}")
        print(f"  Responses: {n_responses}")
        print(f"  Improvement: {improvement:+.2f}")

        # Extract positive quotes
        all_quotes = extract_positive_quotes(group_df, text_cols)

        # Select best 2 quotes (prefer longer, more detailed ones)
        all_quotes.sort(key=lambda q: len(q['quote']), reverse=True)
        selected_quotes = all_quotes[:2]

        # Generate case study angle based on improvement and quotes
        if improvement > 1.0:
            case_study = "Demonstrated exceptional growth in participant satisfaction scores"
        elif improvement > 0.5:
            case_study = "Showed strong improvement in training effectiveness and learner engagement"
        elif improvement > 0:
            case_study = "Steady upward trajectory in teaching quality and participant feedback"
        else:
            case_study = "Maintained consistently high training standards with positive learner outcomes"

        results.append({
            'rank': idx,
            'trainer_name': trainer,
            'n_responses': n_responses,
            'improvement_score': round(improvement, 3),
            'mean_early_score': round(trainer_data['mean_early'], 2),
            'mean_late_score': round(trainer_data['mean_late'], 2),
            'quotes': [
                {
                    'row_id': q['row_id'],
                    'quote': q['quote'],
                    'source': q['source_column']
                } for q in selected_quotes
            ],
            'case_study_angle': case_study
        })

    # Save results to JSON
    output_file = Path('outputs/results.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"Results saved to: {output_file}")

    # Save results to CSV
    csv_rows = []
    for result in results:
        # Flatten quotes into separate columns
        quote_1 = result['quotes'][0] if len(result['quotes']) > 0 else {}
        quote_2 = result['quotes'][1] if len(result['quotes']) > 1 else {}

        csv_rows.append({
            'Rank': result['rank'],
            'Trainer Name': result['trainer_name'],
            'Total Responses': result['n_responses'],
            'Early Period Score': result['mean_early_score'],
            'Late Period Score': result['mean_late_score'],
            'Improvement Score': result['improvement_score'],
            'Quote 1 (Row ID)': quote_1.get('row_id', ''),
            'Quote 1': quote_1.get('quote', ''),
            'Quote 2 (Row ID)': quote_2.get('row_id', ''),
            'Quote 2': quote_2.get('quote', ''),
            'Case Study Angle': result['case_study_angle']
        })

    csv_df = pd.DataFrame(csv_rows)
    csv_output = Path('outputs/results.csv')
    csv_df.to_csv(csv_output, index=False, encoding='utf-8')
    print(f"Results saved to: {csv_output}")

    # Generate HTML report
    html_output = Path('outputs/results.html')
    html_content = generate_html_report(results)
    with open(html_output, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"HTML report saved to: {html_output}")

    # Print nice console table
    print(f"\n{'='*80}")
    print("TOP 2 TRAINERS BY IMPROVEMENT")
    print(f"{'='*80}")

    for result in results:
        print(f"\n#{result['rank']}: {result['trainer_name']}")
        print(f"{'-'*80}")
        print(f"  Total Responses:     {result['n_responses']}")
        print(f"  Early Period Score:  {result['mean_early_score']:.2f}")
        print(f"  Late Period Score:   {result['mean_late_score']:.2f}")
        print(f"  Improvement:         {result['improvement_score']:+.3f}")
        print(f"\n  Case Study Angle:")
        print(f"  → {result['case_study_angle']}")
        print(f"\n  Positive Quotes:")
        for i, quote in enumerate(result['quotes'], 1):
            print(f"\n  Quote {i} [{quote['row_id']}]:")
            # Word wrap for readability
            words = quote['quote'].split()
            lines = []
            current_line = []
            current_length = 0

            for word in words:
                if current_length + len(word) + 1 <= 70:
                    current_line.append(word)
                    current_length += len(word) + 1
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                    current_length = len(word)

            if current_line:
                lines.append(' '.join(current_line))

            for line in lines:
                print(f"    {line}")

    print(f"\n{'='*80}")
    print(f"✓ Analysis complete!")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    main()
