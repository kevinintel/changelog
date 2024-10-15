import os
import requests
import re
import time
from collections import Counter
#import opeanai
from datetime import datetime, timedelta
from requests.exceptions import SSLError


# Constants
REPO_OWNER = "opea-project"
REPO_NAME = "GenAIExamples"
TOKEN = "your_token"
BRANCH = "v1.0rc"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


params = {
    "per_page": 100,  # Number of commits per page (max 100)
    "page": 1,         # Page number to retrieve
# time params not working
#        "since": "2024-08-19T00:00:00Z",  # Start date
#        "until": "2024-08-20T23:59:59Z",  # End date
}

end_date = datetime(2024,9,20,23,59,59)
start_date = datetime(2024,9,10,0,0,0)

changelog =""
page = 1

while True :
    print("page"+str(page))
    params['page'] = page
    request_str=f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/commits?sha={BRANCH}"
    response = requests.get(request_str, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception("Error fetching PRs from GitHub API!")

    json_file = response.json()
    if not json_file:
       break

    if len(json_file) == 0:
        break

    correct_num = 0
    for commit in json_file:    
        time_str = commit["commit"]["author"]["date"]
        merged_time = datetime.fromisoformat(time_str[:-1])
        sha = commit["sha"]
        first_seven_digits = sha[:7]
        commit_url = "https://github.com/"+REPO_OWNER+"/"+REPO_NAME+"/commit/"+first_seven_digits

        if start_date <= merged_time and end_date >= merged_time:
            title = commit["commit"]["message"].splitlines()[0]
            author = commit["commit"]["author"]["name"]
            base_message = f"{title}([{first_seven_digits}]({commit_url}))"
            #print(base_message)
            changelog = changelog+ base_message+"\n"
            correct_num = correct_num+1
        else:
             print(f"commit {commit_url} not in time: {merged_time}")   

    if correct_num ==0:
        break
    page= page+1
    

print("================================")
print(changelog)

