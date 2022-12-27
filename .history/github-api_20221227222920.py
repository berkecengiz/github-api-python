import datetime

import requests

BASE_URL = "https://api.github.com/repos/"


class GitHubAPI:
    def __init__(self, token: str):
        self.token = token
        self.headers = {"Authorization": f"token {self.token}"}

    def get_issues(self, owner: str, repo: str) -> list:
        url = self.base_url + f"{owner}/{repo}/issues"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise ValueError(response.json()["message"])

    def create_issue(self, owner: str, repo: str, title: str, body: str = "") -> dict:
        data = {"title": title, "body": body}
        url = self.base_url + f"{owner}/{repo}/issues"
        response = requests.post(url, json=data, headers=self.headers)

        if response.status_code == 201:
            return response.json()
        else:
            raise ValueError(response.json()["message"])

    def update_issue(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        title: str = "",
        body: str = "",
    ) -> dict:
        data = {}
        if title:
            data["title"] = title
        if body:
            data["body"] = body
        url = self.base_url + f"{owner}/{repo}/issues/{issue_number}"
        response = requests.patch(url, json=data, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise ValueError(response.json()["message"])

    def delete_issue(self, owner: str, repo: str, issue_number: int):
        url = self.base_url + f"{owner}/{repo}/issues/{issue_number}"
        response = requests.delete(url, headers=self.headers)
        if response.status_code == 204:
            return
        else:
            raise ValueError(response.json()["message"])

    def save_to_file(self, issues: list, filename: str):
        with open(filename, "w") as fs:
            for issue in issues:
                fs.write(f"{issue['number']} - {issue['title']}\n")

    def check_issue_update_time(issue: dict, delta: int) -> bool:
        last_update = datetime.datetime.strptime(
            issue["updated_at"], "%Y-%m-%dT%H:%M:%SZ"
        )
        return last_update < datetime.datetime.now() - datetime.timedelta(days=delta)

    def close_issue_if_old(api: GitHubAPI, issue: dict, delta: int):
        if check_issue_update_time(issue, delta):
            api.update_issue("OWNER", "REPO", issue["number"], state="closed")
            print(f"Closed issue {issue['number']}: {issue['title']}")
        else:
            print(f"Issue {issue['number']}: {issue['title']} - {issue['state']}")


def main():
    # Create an instance of the GitHubAPI class
    api = GitHubAPI("YOUR_TOKEN")
    # Retrieve the list of issues
    issues = api.get_issues("OWNER", "REPO")
    # Iterate through the list of issues
    for issue in issues:
        # Check the last update time of the issue
        last_update = datetime.datetime.strptime(
            issue["updated_at"], "%Y-%m-%dT%H:%M:%SZ"
        )
        if last_update < datetime.datetime.now() - datetime.timedelta(days=365):
            # If the last update time is greater than 1 year, close the issue
            api.update_issue("OWNER", "REPO", issue["number"], state="closed")
            print(f"Closed issue {issue['number']}: {issue['title']}")
        else:
            print(f"Issue {issue['number']}: {issue['title']} - {issue['state']}")
