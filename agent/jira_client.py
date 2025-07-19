import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from datetime import datetime, timedelta
from datetime import timezone

# Load environment variables from .env for local dev
load_dotenv()

# Jira credentials from .env or GitHub Secrets
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

# Validate config
if not all([JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN]):
    raise ValueError("Missing Jira credentials. Check .env or GitHub Secrets.")

# Common auth + headers
auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}


def get_days_remaining_in_sprint(board_id):
    """
    Fetch the current sprint's start date for the board,
    assume a 2-week sprint duration, and return days left.
    """
    url = f"{JIRA_BASE_URL}/rest/agile/1.0/board/{board_id}/sprint"
    params = {"state": "active"}

    try:
        response = requests.get(url, headers=headers, auth=auth, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to fetch sprint info: {e}")
        return 0

    sprints = response.json().get("values", [])
    if not sprints:
        return 0

    # Use the first active sprint
    sprint = sprints[0]
    start_date_str = sprint.get("startDate")

    if not start_date_str:
        return 0

    # Parse startDate (ISO format) and calculate remaining days
    start_date = datetime.fromisoformat(start_date_str.replace("Z", "+00:00"))
    sprint_end_date = start_date + timedelta(days=14)
    # today = datetime.utcnow()


    today = datetime.now(timezone.utc)

    days_left = (sprint_end_date - today).days
    return max(0, days_left)



def get_user_issues(board_id, username):
    
    jql = f"project={board_id} AND assignee={username} AND sprint in openSprints()"
    url = f"{JIRA_BASE_URL}/rest/api/3/search"
    params = {
        "jql": jql,
        "fields": "summary,status,comment",
        "maxResults": 20
    }

    try:
        response = requests.get(url, headers=headers, auth=auth, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Jira API failed: {e}")
        return []

    data = response.json()
    issues = []

    for issue in data.get("issues", []):
        key = issue.get("key")
        fields = issue.get("fields", {})
        summary = fields.get("summary", "")
        status = fields.get("status", {}).get("name", "Unknown")

        # Extract plain text comments
        comments = []
        for comment in fields.get("comment", {}).get("comments", []):
            try:
                # Text may be nested in content layers (Atlassian JSON format)
                content_blocks = comment.get("body", {}).get("content", [])
                for block in content_blocks:
                    if block["type"] == "paragraph":
                        text_chunks = block.get("content", [])
                        for chunk in text_chunks:
                            if chunk["type"] == "text":
                                comments.append(chunk["text"])
            except Exception:
                pass  # Safely ignore parsing errors

        # Check for MR link if completed
        mr_url = None
        if status.lower() in {"done", "closed", "resolved","completed"}:
            mr_url = get_merge_request_url(key)

        issues.append({
            "key": key,
            "summary": summary,
            "status": status,
            "comments": comments,
            "mr_url": mr_url
        })

    return issues

def get_merge_request_url(issue_key):
    url = f"{JIRA_BASE_URL}/rest/dev-status/1.0/issue/detail"
    params = {
        "issueIdOrKey": issue_key,
        "applicationType": "github",         # or "bitbucket", "gitlab" if applicable
        "dataType": "pullrequest"
    }

    try:
        response = requests.get(url, headers=headers, auth=auth, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[WARN] Could not fetch MR for {issue_key}: {e}")
        return None

    data = response.json()
    details = data.get("detail", [])
    if not details:
        return None

    prs = details[0].get("pullRequests", [])
    if prs:
        return prs[0].get("url")
    return None