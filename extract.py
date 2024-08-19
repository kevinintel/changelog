import os
import requests
import re
#import opeanai
from datetime import datetime, timedelta


# Constants
REPO_OWNER = "opea-project"
REPO_NAME = "GenAIExamples"
TOKEN = "my_key"
DAYS_AGO = 7


headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

def fetch_recent_merged_prs():
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=DAYS_AGO)
    print ("fetch commits from "+ str(start_date) +"in https://github.com/"+REPO_OWNER+"/"+REPO_NAME )

    response = requests.get(
        f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls?state=closed&since={start_date.isoformat()}Z",
        headers=headers,
    )

    if response.status_code != 200:
        raise Exception("Error fetching PRs from GitHub API!")

    return [pr for pr in response.json() if pr["merged_at"]]

def extract_commit_details_from_prs(prs):
    commit_details = []
    for pr in prs:
        commit_message = pr["title"]
        commit_url = pr["html_url"]
        pr_number = pr["number"]
        merge_commit_sha = pr["merge_commit_sha"]
        branch_name = pr["head"]["ref"]
        issue_numbers = re.findall(r"(www-\d+|web-\d+)", branch_name)

        # If no issue numbers are found, add the PR details without issue numbers and URLs
        if not issue_numbers:
            commit_details.append(
                {
                    "message": commit_message,
                    "pr_number": pr_number,
                    "pr_url": commit_url,
                    "merge_commit_sha": merge_commit_sha,
                }
            )

    return commit_details

def generate_changelog_with_openai(commit_details):
    commit_messages = []
    for details in commit_details:
        first_six_digits = details['merge_commit_sha'][:7]
        commit_url = "https://github.com/"+REPO_OWNER+"/"+REPO_NAME+"/commit/"+first_six_digits
        base_message = f"{details['message']}([{first_six_digits}]({commit_url}))"
        commit_messages.append(base_message)
#        print(base_message)

    commit_list = "\n".join(commit_messages)

#Add ChatQnA instructions for AIPC([26d4ff](https://github.com/opea-project/GenAIExamples/commit/26d4ff11ffd323091d80efdd3f65e4c330b68840))
    prompt = """
Generate a changelog for the web version of the OPEA Project, which offers Enterprise AI Solution.
The changelog should:
1. Classification into 3 categories: Features, Deployment, CI/UT. If commit messages contains "UT", "test", please classified as CI/UT. If commit messages contains "k8s", "Kubernenets", please classified as Deployment.
2. Formatting: using Markdown formatting

Here's a good example to follow:
- Features
    - Add ChatQnA instructions for AIPC([26d4ff1](https://github.com/opea-project/GenAIExamples/commit/26d4ff11ffd323091d80efdd3f65e4c330b68840))
- Deployment
    - Add ChatQnA instructions for AIPC([26d4ff1](https://github.com/opea-project/GenAIExamples/commit/26d4ff11ffd323091d80efdd3f65e4c330b68840))
- CI/UT
    - Add ChatQnA instructions for AIPC([26d4ff1](https://github.com/opea-project/GenAIExamples/commit/26d4ff11ffd323091d80efdd3f65e4c330b68840))

And here are the commits:
{}
    """.format(
        commit_list
    )


    print (prompt)
#    openai.api_key = OPENAI_API_KEY
#    messages = [{"role": "user", "content": prompt}]
#    response = openai.ChatCompletion.create(model="gpt-4", messages=messages)

#    if "error" in response.choices[0].message:
#        raise Exception("Error generating changelog with OpenAI!")

#    return response.choices[0].message["content"].strip()



if __name__ == "__main__":
    try:
        print("⏳ Generating changelog, it can take a few minutes...")
        prs = fetch_recent_merged_prs()
        commit_details = extract_commit_details_from_prs(prs)
        changelog = generate_changelog_with_openai(commit_details)
        print(" Generated prompt !")
    except Exception as e:
        print(str(e))
