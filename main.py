from agent.utils import load_team_config
from agent.jira_client import get_user_issues, get_days_remaining_in_sprint
from agent.summary_generator import generate_sprint_summary
from dotenv import load_dotenv
from agent.teams_notifier import send_to_teams
from agent.llm_agent import summarize_issues_with_llm

def main():
    load_dotenv()
    config = load_team_config()
    all_summaries = []
    print(f"\n🏁 Sprint Summary for Team: {config['team']['name']}\n")

    for member in config["members"]:
        name = member["name"]
        board_id = member["jira_board_id"]
        project_id = member["jira_project_id"]
        account_id = member["account_id"]

        print(f"▶ Fetching issues for {name}")
        sprint_ends_in = get_days_remaining_in_sprint(board_id)
        print(f"⏳ Days left in sprint: {sprint_ends_in}")

        issues = get_user_issues(project_id, account_id)
        #summary = generate_sprint_summary(name, issues, sprint_ends_in)

        if config.get("use_llm", False):
            summary = summarize_issues_with_llm(name, issues, sprint_ends_in)
        else:
            summary = generate_sprint_summary(name, issues, sprint_ends_in)

        print(summary)
        print("-" * 60)
        all_summaries.append(summary)

    full_summary = "\n\n".join(all_summaries)
    send_to_teams(full_summary)

if __name__ == "__main__":
    main()




# ... your loop logic ...
