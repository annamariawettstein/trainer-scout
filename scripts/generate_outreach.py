#!/usr/bin/env python
"""
Generate personalized outreach emails for top improving trainers.
"""

import json
from pathlib import Path
from datetime import datetime


def extract_first_name(email):
    """Extract first name from email address."""
    # Get part before @
    username = email.split('@')[0]
    # Get first part before dot or underscore
    first_part = username.split('.')[0].split('_')[0]
    # Capitalize
    return first_part.capitalize()


def generate_email(trainer_data):
    """Generate a warm, personalized outreach email."""
    first_name = extract_first_name(trainer_data['trainer_name'])
    email = trainer_data['trainer_name']

    # Pick the first quote as evidence
    evidence_quote = trainer_data['quotes'][0]['quote']
    evidence_row_id = trainer_data['quotes'][0]['row_id']

    # Create subject line
    subject = f"Your training impact is showing up in the feedback, {first_name}!"

    # Create email body
    body = f"""Hi {first_name},

I wanted to reach out personally because I've been reviewing our trainer feedback data and your name kept coming up in a really positive way.

Over the past few months, we've seen strong improvement in your training scores and the feedback from learners has been genuinely impressive. Here's one that really stood out to me:

"{evidence_quote}"

That kind of feedback tells us you're doing something right, and we'd love to capture and share what's working for you.

Would you be up for helping us with two quick things?

1. A short testimonial quote from you (just a sentence or two about your experience as a trainer with us)
2. Either a 15-20 min chat or a quick written Q&A where we can learn more about your approach to training

We're building out some case studies and best practices to help other trainers, and your insights would be really valuable.

Just reply to this email and let me know if you're interested. No pressure if you're swamped — I totally get it.

Thanks for being such a great part of the team!

Best,
[Your name]"""

    return {
        'trainer_name': first_name,
        'trainer_email': email,
        'email_subject': subject,
        'email_body': body,
        'evidence_quote': evidence_quote,
        'evidence_row_id': evidence_row_id,
        'generated_at': datetime.now().isoformat()
    }


def main():
    # Load results
    results_file = Path('outputs/results.json')
    print(f"Loading trainer analysis from: {results_file}\n")

    with open(results_file, 'r', encoding='utf-8') as f:
        trainers = json.load(f)

    print(f"Found {len(trainers)} top trainer(s)\n")
    print("="*80)

    # Generate outreach for each trainer
    outreach_emails = []

    for trainer in trainers:
        email_data = generate_email(trainer)
        outreach_emails.append(email_data)

        # Print to console
        print(f"\nTRAINER #{trainer['rank']}: {email_data['trainer_name']}")
        print("-"*80)
        print(f"TO: {email_data['trainer_email']}")
        print(f"SUBJECT: {email_data['email_subject']}")
        print(f"\nBODY:\n{email_data['email_body']}")
        print(f"\nEVIDENCE: Quote from {email_data['evidence_row_id']}")
        print("="*80)

    # Save to JSON
    output_file = Path('outputs/outreach_ready.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(outreach_emails, f, indent=2, ensure_ascii=False)

    print(f"\n✓ {len(outreach_emails)} outreach email(s) saved to: {output_file}")
    print(f"\nReady to send! Just personalize with your name and hit send.\n")


if __name__ == '__main__':
    main()
