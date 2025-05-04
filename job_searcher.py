import requests
from bs4 import BeautifulSoup
import time
import schedule
import subprocess
import json
import os

# Constants
SEARCH_URL = 'https://jobs.apple.com/en-us/search?team=SFTWR&location=united-states-USA'
KEYWORDS = ['software engineer', 'java']
SEEN_JOBS_FILE = 'seen_jobs.json'

# Load seen job IDs
def load_seen_jobs():
    if os.path.exists(SEEN_JOBS_FILE):
        with open(SEEN_JOBS_FILE, 'r') as f:
            return set(json.load(f))
    return set()

# Save seen job IDs
def save_seen_jobs(seen_jobs):
    with open(SEEN_JOBS_FILE, 'w') as f:
        json.dump(list(seen_jobs), f)

# macOS desktop notification
def send_notification(title, message, url):
    subprocess.run(['osascript', '-e', 
        f'display notification "{message}" with title "{title}" subtitle "{url}"'])

# Determine if a job is relevant
def is_relevant_job(title, url):
    if 'en-us' not in url.lower():
        return False
    title_lower = title.lower()
    if not all(kw in title_lower for kw in KEYWORDS):
        return False
    return True

# Main job checker
def check_jobs():
    print("Checking Apple jobs site...")
    seen_jobs = load_seen_jobs()
    try:
        response = requests.get(SEARCH_URL)
        soup = BeautifulSoup(response.text, 'html.parser')
        job_links = soup.find_all('a', class_='table--advanced-search__title')
    except Exception as e:
        print(f"Error fetching or parsing job data: {e}")
        return

    new_jobs_found = False

    for job in job_links:
        title = job.get_text(strip=True)
        url = 'https://jobs.apple.com' + job['href']
        job_id = url.split('/')[-1]

        if job_id in seen_jobs:
            continue

        if is_relevant_job(title, url):
            send_notification("New Apple Job Alert!", title, url)
            print(f"✔ New job matched: {title}\n🔗 {url}")
            seen_jobs.add(job_id)
            new_jobs_found = True

    if new_jobs_found:
        save_seen_jobs(seen_jobs)
    else:
        print("No new matching jobs found.")

# Schedule check every 5 minutes
schedule.every(5).minutes.do(check_jobs)

print("📡 Apple job monitor running. Press Ctrl+C to stop.")
check_jobs()

while True:
    schedule.run_pending()
    time.sleep(1)
