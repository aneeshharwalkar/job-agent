# Job Agent

An automated AI-powered job search agent that finds recent entry-level job postings matching a candidate’s background and emails a curated job brief on a recurring schedule using GitHub Actions.

## Overview

This project uses Anthropic Claude with web search to look for recent job postings that fit a candidate’s resume, preferred locations, and target role types. It can run locally or through GitHub Actions and sends a job brief directly to email.

The current version is configured around my own profile and preferences, but it can be easily customized for other users by editing the resume input, search preferences, scoring criteria, and location priorities in `agent.py`.

## Features

- Uses Claude to search and evaluate recent job postings
- Prioritizes target job categories based on user preferences
- Filters for entry-level positions based on job description content
- Scores job postings based on resume fit, seniority, location, and role type
- Sends curated job matches by email
- Supports automated scheduled runs with GitHub Actions
- Keeps `resume.txt` private by using GitHub Secrets in production
- Can be customized for different job seekers by editing the prompt and preferences in `agent.py`

## How It Works

The script:

1. Loads environment variables
2. Loads resume data from either:
   - the `RESUME_TEXT` environment variable, or
   - a local `resume.txt` file as a fallback
3. Sends a structured job-search prompt to Claude
4. Uses web search to find relevant roles posted in the last few days
5. Filters and ranks the results
6. Emails the final job brief

## Customization

The current agent is tailored to my own background and job search goals, including sports analytics, analytics, and business analyst roles. However, users can adapt it to their own profile by editing `agent.py`.

Things you can customize in `agent.py` include:

- target role categories
- preferred industries
- preferred companies
- location preferences
- seniority rules
- scoring logic
- number of job results returned
- wording of the final email brief

For example, a user could change:
- sports analytics preferences to software engineering, marketing, finance, UX research, or product roles
- Austin and New York preferences to any cities they want
- entry-level filtering criteria to match their own experience level
- scoring priorities to emphasize remote roles, specific skills, or certain companies

## Job Search Logic

The current version searches in two tiers:

### Tier 1: Sports Analytics
Highest-priority roles such as:
- sports analyst
- sports data analyst
- sports betting analyst
- sportsbook analyst
- sports business analyst
- sports technology analyst

It also prioritizes companies and organizations in sports, media, gaming, and betting.

### Tier 2: General Analytics and BA Roles
Examples include:
- entry-level business analyst
- junior data analyst
- data analyst new grad
- product analytics analyst
- business intelligence analyst
- junior ML/AI analyst roles

These defaults are fully editable in `agent.py`.

### Filtering Rules
The agent only includes roles it classifies as entry-level based on:
- years of experience required
- job responsibilities
- whether the role appears junior or new grad friendly

### Location Preference
The current default priority order is:
1. Austin, TX
2. New York City
3. Remote or hybrid roles
4. Other US cities only if they score very highly or are strong sports roles

Users can change these location preferences directly in `agent.py` to match their own profile.

## Project Structure

```text
.
├── .github/
│   └── workflows/
│       └── daily.yml
├── agent.py
├── requirements.txt
├── .gitignore
├── .env                # local only, not committed
└── resume.txt          # local only, gitignored
```

## Setup

### 1. Clone the repo

~~~bash
git clone https://github.com/your-username/job-agent.git
cd job-agent
~~~

### 2. Create and activate a virtual environment

~~~bash
python3 -m venv venv
source venv/bin/activate
~~~

### 3. Install dependencies

~~~bash
pip install -r requirements.txt
~~~

### 4. Create a local `.env` file

Create a `.env` file in the project root with:

~~~env
ANTHROPIC_API_KEY=your_anthropic_key
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=your_target_email@example.com
EMAIL_PASSWORD=your_gmail_app_password
~~~

### 5. Add your local `resume.txt`

Create a `resume.txt` file in the project root containing your resume text.

This file is intended for local use only and should remain in `.gitignore`.

### 6. Add GitHub Actions secrets

In your GitHub repository, go to:

**Settings → Secrets and variables → Actions**

Add the following repository secrets:

- `ANTHROPIC_API_KEY`
- `EMAIL_FROM`
- `EMAIL_TO`
- `EMAIL_PASSWORD`
- `RESUME_TEXT`

`RESUME_TEXT` should contain the full text of your resume. This allows GitHub Actions to run without exposing `resume.txt` in the public repository.

### 7. Update your workflow file

Make sure your workflow passes the secrets into the environment:

~~~yaml
name: Daily Job Brief

on:
  schedule:
    - cron: '0 14 */2 * *'
  workflow_dispatch:

jobs:
  run-agent:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run job agent
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          EMAIL_FROM: ${{ secrets.EMAIL_FROM }}
          EMAIL_TO: ${{ secrets.EMAIL_TO }}
          EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
          RESUME_TEXT: ${{ secrets.RESUME_TEXT }}
        run: python agent.py
~~~

### 8. Update `agent.py` to support both local and GitHub runs

Use this logic so the script reads from `RESUME_TEXT` in GitHub Actions and falls back to local `resume.txt` on your machine:

~~~python
from pathlib import Path
import os

resume = os.getenv("RESUME_TEXT")

if not resume:
    resume_path = Path(__file__).resolve().parent / "resume.txt"
    if not resume_path.exists():
        raise FileNotFoundError("resume.txt not found and RESUME_TEXT secret is missing")
    resume = resume_path.read_text(encoding="utf-8")
~~~

### 9. Run locally

~~~bash
python agent.py
~~~

If configured correctly, the script will generate a job brief and send it to your email.

### 10. Customize preferences

The current version of the agent is tailored to my own profile, role preferences, and locations. To adapt it for your own use, edit the search terms, preferred industries, preferred locations, scoring logic, and output preferences directly in `agent.py`.

For example, you can change:

- sports analytics roles to software engineering, finance, UX, or marketing roles
- Austin and New York preferences to your own target cities
- the entry-level filter to match your experience level
- the scoring logic to prioritize remote roles, certain companies, or specific skills
