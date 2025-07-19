import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def summarize_issues_with_llm(name, issues, sprint_ends_in):
    # Construct a prompt with all issue details
    prompt = f"""You are a helpful AI assistant that prepares sprint standup summaries for software engineers.

Team Member: {name}
Sprint ends in: {sprint_ends_in} days

Here are their Jira issues:
"""

    for issue in issues:
        prompt += f"\n- [{issue['status']}] {issue['key']}: {issue['summary']}\n"
        for comment in issue["comments"]:
            prompt += f"    - Comment: {comment}\n"

    prompt += """
Please:
1. Identify blockers based on comments or status
2. Count stories completed vs total
3. Estimate % completion and sprint risk level
4. Format a clean Teams-friendly summary

Use hyperlinks for each ticket like [SCRUM-123](https://example.atlassian.net/browse/SCRUM-123)
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            temperature=0.4,
            messages=[
                {"role": "system", "content": "You are an expert Jira assistant for agile standups."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"[LLM ERROR] {e}")
        return "⚠️ Could not generate summary."
