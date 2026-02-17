import requests
import os

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

if load_dotenv:
    load_dotenv()



def fetch_github_graphql(username, token=None):
    if not token:
        token = os.getenv("GITHUB_TOKEN")
    if not token:
        return None

    query = """
    query ($login: String!) {
      user(login: $login) {
        contributionsCollection {
          totalCommitContributions
          contributionCalendar {
            weeks {
              contributionDays {
                date
                contributionCount
              }
            }
          }
        }
      }
    }
    """

    headers = {
        "Authorization": f"Bearer {token}"
    }

    resp = requests.post(
        GITHUB_GRAPHQL_URL,
        json={"query": query, "variables": {"login": username}},
        headers=headers,
        timeout=10
    )

    if resp.status_code != 200:
        return None
    

    return resp.json()

def parse_graphql_contributions(graphql_json):
    weeks = (
        graphql_json["data"]["user"]
        ["contributionsCollection"]
        ["contributionCalendar"]
        ["weeks"]
    )

    contributions = []
    contribution_weeks = []
    for week in weeks:
        week_days = []
        for day in week["contributionDays"]:
            day_entry = {
                "date": day["date"],
                "count": day["contributionCount"]
            }
            contributions.append(day_entry)
            week_days.append(day_entry)
        contribution_weeks.append(week_days)

    total_commits = (
        graphql_json["data"]["user"]
        ["contributionsCollection"]
        ["totalCommitContributions"]
    )

    return contributions, total_commits, contribution_weeks


def get_github_headers(token=None):
    """
    Build headers for GitHub REST API requests.
    Uses Authorization header if GITHUB_TOKEN is set.
    """
    headers = {
        "Accept": "application/vnd.github+json"
    }

    if not token:
        token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    return headers

def get_live_github_data(username, token=None):
    """
    Fetches real data from GitHub API. 
    Notes: 
    - Unauthenticated requests are rate-limited (60/hr).
    - For a real production app, we need a token or use GraphQL.
    - For this MVP, we scrape or use public endpoints where possible to avoid token complexity for the user usage.
    """
    try:
        # User details
        user_url = f"https://api.github.com/users/{username}"
        headers = get_github_headers(token)
        user_resp = requests.get(user_url, headers=headers)

        if user_resp.status_code != 200:
            return None
        user_data = user_resp.json()
        
        # Repos for stars count (limited to first 100 public repos for basic sum without pagination for MVP speed)
        repos_url = f"https://api.github.com/users/{username}/repos?per_page=100&type=owner"
        repos_resp = requests.get(repos_url, headers=headers)
        repos_data = repos_resp.json() if repos_resp.status_code == 200 else []
        
        total_stars = sum(repo.get("stargazers_count", 0) for repo in repos_data)
        
        # Languages (Approximation from top repos)
        languages = {}
        for repo in repos_data[:10]: # Check top 10 repos
            lang = repo.get("language")
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
        
        top_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
        

        # Ensure total_commits is always an integer
        total_commits = 0 

        try:
            contrib_url = f"https://github-contributions-api.jogruber.de/v4/{username}"
            contrib_resp = requests.get(contrib_url)
            if contrib_resp.status_code == 200:
                c_data = contrib_resp.json()
<<<<<<< HEAD
                # Sum up all contributions in the returned calendar year(s)
                all_days = []
                if 'contributions' in c_data:
                    for year_group in c_data['contributions']:
                        all_days.extend(year_group.get('days', []))
            print(f"Contrib API Error: {ex}")
            total_commits = 0 # Safety fallback

        data = {
            "total_stars": total_stars,
            "total_commits": total_commits,
            "public_repos": user_data.get("public_repos", 0),
            "followers": user_data.get("followers", 0),
            "top_languages": top_langs,
<<<<<<< HEAD
            "streak_data": streak_data
        }

=======
        }

        # --- Optional GraphQL enrichment ---
        graphql_data = fetch_github_graphql(username, token)
        if graphql_data:
            try:
                contributions, gql_total_commits, contribution_weeks = parse_graphql_contributions(graphql_data)
                data["contributions"] = contributions
                data["total_commits"] = gql_total_commits
                data["contribution_weeks"] = contribution_weeks
            except Exception:
                pass  # Never break REST fallback

        if "contributions" not in data:
            # Fallback to empty list; UI should handle missing contribution data gracefully.
            data["contributions"] = []

        return data

>>>>>>> cbb812d0c91d6b7aeb9b0eaee07897344e999074
            
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_mock_data(username):
    """Returns dummy data for layout testing/building without hitting API limits"""
    return {
        "username": username,
        "total_stars": 120,
        "total_commits": 450,
        "public_repos": 25,
        "followers": 85,
        "top_languages": [("Python", 10), ("JavaScript", 5), ("Rust", 2)],
<<<<<<< HEAD
        "streak_data": {
            "current_streak": 15,
            "longest_streak": 45,
            "total_contributions": 450
        }
=======
        "contributions":[ 
            {"date": f"2025-01-{i+1:02d}", "count": (i * 3) % 10}
            for i in range(80)
        ]

>>>>>>> cbb812d0c91d6b7aeb9b0eaee07897344e999074
    }
