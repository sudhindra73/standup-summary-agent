import os

JIRA_BASE_URL = os.getenv("JIRA_BASE_URL", "").rstrip("/")


def make_link(key):
    return f"[{key}]({JIRA_BASE_URL}/browse/{key})"


def generate_sprint_summary(name, issues, sprint_ends_in):
    total_stories = len(issues)

    completed_keys = []
    in_progress_keys = []
    to_do_keys = []
    blocker_keys = []

    blocker_keywords = ["blocked", "waiting", "qa", "dependency", "approval", "review", "pending", "not working"]

    for issue in issues:
        key = issue["key"]
        status = issue["status"].lower()
        comments_text = " ".join(issue["comments"]).lower()
        link = make_link(key)

        if status in {"done", "closed", "resolved","completed"}:
            if issue.get("mr_url"):
                link = f"[{key}]({issue['mr_url']})"
            else:
                link = make_link(key)
            completed_keys.append(link)

        elif status in {"in progress", "qa", "testing"}:
            in_progress_keys.append(link)
        elif status in {"to do", "open", "backlog"}:
            to_do_keys.append(link)

        if status in {"blocked", "waiting", "in qa", "qa", "on hold"}:
            blocker_keys.append(link)
        elif any(keyword in comments_text for keyword in blocker_keywords):
            blocker_keys.append(link)

    # Prediction score
    if total_stories == 0:
        prediction_score = 100
    else:
        completion_ratio = len(completed_keys) / total_stories
        days_left_factor = min(1, sprint_ends_in / 7)
        prediction_score = int(completion_ratio * 100 * days_left_factor)

    # Risk level
    if prediction_score >= 80:
        risk = "LOW"
    elif prediction_score >= 50:
        risk = "MEDIUM"
    else:
        risk = "HIGH"

    # Burndown trend
    sprint_length_days = 14
    days_elapsed = sprint_length_days - sprint_ends_in
    expected_ratio = days_elapsed / sprint_length_days
    actual_ratio = len(completed_keys) / total_stories if total_stories else 1

    if actual_ratio >= expected_ratio:
        burndown_trend = "🟢 On Track"
    elif actual_ratio >= expected_ratio * 0.7:
        burndown_trend = "🟡 Slightly Behind"
    else:
        burndown_trend = "🔴 Lagging Behind"

    summary_lines = [
        f"**Sprint Summary – {name}**",
        f"• Stories Completed: {len(completed_keys)}/{total_stories}",
        f"  → {', '.join(completed_keys) if completed_keys else 'None'}",
        f"• In Progress: {', '.join(in_progress_keys) if in_progress_keys else 'None'}",
        f"• To Do: {', '.join(to_do_keys) if to_do_keys else 'None'}",
        f"• Blockers: {', '.join(blocker_keys) if blocker_keys else 'None'}",
        f"• Prediction Score: {prediction_score}%",
        f"• Sprint Completion Risk: {risk}",
        f"• Burndown Trend: {burndown_trend}"
    ]

    return "\n".join(summary_lines)
