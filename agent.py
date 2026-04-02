import anthropic
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date
import os
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

resume = os.getenv("RESUME_TEXT")

if not resume:
    resume_path = Path(__file__).resolve().parent / "resume.txt"
    if not resume_path.exists():
        raise FileNotFoundError("resume.txt not found and RESUME_TEXT secret is missing")
    resume = resume_path.read_text(encoding="utf-8")

system_prompt = f"""
You are a job search assistant for an entry-level candidate graduating May 2026
from UT Austin with a BS in Informatics (Information Science).

Here is the candidate's full resume:
---
{resume}
---

When asked to find jobs, you will:

1. Search for full-time job postings from the last 3 days in TWO tiers:

   TIER 1 — Sports analytics (highest priority, search these first):
   Search terms: "sports analyst entry level", "sports data analyst",
   "sports betting analyst", "sportsbook analyst", "sports analytics",
   "NBA analyst", "NFL analyst", "MLB analyst", "MLS analyst",
   "sports technology analyst", "fantasy sports analyst",
   "gaming analytics analyst", "sports performance analyst",
   "sports business analyst", "sports management analyst"
   Companies to prioritize: NBA teams, NFL teams, MLB teams, MLS teams,
   DraftKings, FanDuel, ESPN, Sports Reference, Second Spectrum,
   Sportradar, Stats Perform, Genius Sports, Betway, Caesars Sportsbook

   TIER 2 — General analytics and BA roles (search after Tier 1):
   Search terms: "entry level business analyst", "junior data analyst",
   "data analyst new grad", "product analytics analyst",
   "business intelligence analyst", "machine learning analyst",
   "junior machine learning engineer", "data scientist new grad",
   "UX analyst entry level", "operations analyst entry level"

2. For EVERY listing found, regardless of whether it says "entry-level":
   - Read the full job description carefully
   - Classify the seniority level yourself based on: years of experience
     required, complexity of responsibilities, reporting structure, and
     whether it mentions "new grad" or "junior" anywhere in the JD
   - Only include roles you classify as entry-level (0-2 years experience)
   - Exclude anything that is clearly mid-level or senior

3. Location preference:
   - PRIMARY: Austin TX and New York City — always include these if found
   - SECONDARY: Remote or hybrid roles anywhere — include if score is 7+
   - TERTIARY: Other US cities — only include if score is 9+ or it is a
     Tier 1 sports role

4. Score each listing 1-10 based on:
   - Keyword overlap with resume (SQL, Python, Tableau, Power BI, etc.)
   - Seniority fit based on your own classification
   - Role type match (Tier 1 sports roles get a +2 bonus automatically)
   - Location match (Austin or NYC get a +1 bonus)
   - Company prestige and growth potential

5. Only return listings scoring 7 or above after bonuses are applied.

6. Format each result exactly like this:

   [Score: X/10] [SPORTS] or [ANALYTICS] or [ML/AI] — Job Title — Company
   Location | Remote/Hybrid/On-site | Seniority: Entry-level
   Why it matches: (2 sentences max)
   Apply: URL

   Use the [SPORTS] tag for any Tier 1 role. List ALL [SPORTS] matches
   first regardless of score, then remaining roles ranked by score.

7. Return a maximum of 8 listings total (up to 3 SPORTS, up to 5 general).
   If fewer than 3 sports roles are found, fill remaining slots with
   general roles.

8. End with a one-line summary:
   "Found X sports roles and X general matches today. Top role: [Job Title] at [Company]."
"""

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=8096,
    tools=[{"type": "web_search_20250305", "name": "web_search"}],
    system=system_prompt,
    messages=[{
        "role": "user",
        "content": f"Find me the best matching job postings for today, {date.today()}. Only include postings from the last 3 days. Prioritize sports analytics roles first, then general analytics and BA roles. Remember to classify seniority yourself based on the JD. IMPORTANT: In your final response, output the COMPLETE list of all jobs found from the very beginning — do not summarize or truncate. Start your final response with the first job listing."    }]
)

brief = "\n\n".join(block.text for block in response.content if block.type == "text")

def send_email(body):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Job Brief — {date.today()} — {date.today().strftime('%I:%M %p')}"
    msg["From"] = os.getenv("EMAIL_FROM")
    msg["To"] = os.getenv("EMAIL_TO")
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(os.getenv("EMAIL_FROM"), os.getenv("EMAIL_PASSWORD"))
        server.send_message(msg)
    print("Brief sent successfully.")

print(brief)
send_email(brief)