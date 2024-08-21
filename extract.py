import os
import requests
import re
#import opeanai
from datetime import datetime, timedelta


# Constants
REPO_OWNER = "opea-project"
REPO_NAME = "GenAIEval"
TOKEN = "my_key"
# DAYS_AGO = 2

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

def fetch_recent_merged_prs():
#    end_date = datetime.utcnow()
#    start_date = end_date - timedelta(days=DAYS_AGO)
#    specific_time = datetime(2024, 8, 20, 15, 30, 45)  # Year, Month, Day, Hour, Minute, Second
    end_date = datetime(2024,8,21,23,59,59)
    start_date = datetime(2024,7,27,0,0,0)

    print ("fetch commits from "+ str(start_date)+" to "+str(end_date) +" in https://github.com/"+REPO_OWNER+"/"+REPO_NAME )

    params = {
        "per_page": 100,  # Number of commits per page (max 100)
        "page": 1,         # Page number to retrieve
#        "since": "2024-08-19T00:00:00Z",  # Start date
#        "until": "2024-08-20T23:59:59Z",  # End date
    }



    all_merged_prs = []
    page = 1
    while True :
        params['page'] = page
        print("Page:", params['page'])
        response = requests.get(
            f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls?state=closedZ",
#            f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls?state=closed&since={start_date.isoformat()}&until={end_date.isoformat()}Z",
            headers=headers,
            params=params
        )

        if response.status_code != 200:
            raise Exception("Error fetching PRs from GitHub API!")

        json_file = response.json()
        if not json_file:
            break

        if len(json_file) == 0:
            break

        print(page)

        prs= [pr for pr in json_file if pr["merged_at"]]
        print("merged prs: "+str(len(prs)))
        correct_prs=[]

        time_correct_pr = 0
        for pr in json_file: 
            if pr["merged_at"]:
                merged_time_str = pr["merged_at"]
                merged_time = datetime.fromisoformat(merged_time_str[:-1])
                if start_date <= merged_time and end_date >= merged_time:
                    time_correct_pr= time_correct_pr+1
                    correct_prs.append(pr)
                    print(f"PR #{pr['number']} was merged at: {merged_time}")
                    
#                print(f"PR #{pr['number']} was merged at: {merged_time}")

        print("prs between start and end date: "+str(time_correct_pr))

        if time_correct_pr==0:
            break

        page= page+1
        all_merged_prs.extend(correct_prs)
             
    print("====================extract json done=====================")
    return all_merged_prs

def extract_commit_details_from_prs(prs):
    commit_details = []
    for pr in prs:
        commit_message = pr["title"]
        commit_url = pr["html_url"]
        pr_number = pr["number"]
        merge_commit_sha = pr["merge_commit_sha"]
        branch_name = pr["head"]["ref"]
        issue_numbers = re.findall(r"(www-\d+|web-\d+)", branch_name)

#        print(commit_message)
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
        print(base_message)

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

    print("==================prompt========================")
#    print (prompt)
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
