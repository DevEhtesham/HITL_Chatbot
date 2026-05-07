from langchain_core.tools import tool
import requests
from github import Github
import os

@tool
def github_repo_crawl(repo_name: str) -> str:
    """
    Crawls a GitHub repository to get basic information such as description, stars, languages, and a snippet of the README.md file.
    Requires a valid GitHub repository name (e.g., 'langchain-ai/langgraph').
    """
    # Validate input — reject placeholders or obviously fake values
    PLACEHOLDER_PATTERNS = ["your-repo", "example", "user/repo", "owner/repo", "username", "<", ">", "repo-name", "langchain-ai/langgraph"]
    if not repo_name or not "/" in repo_name or any(p in repo_name.lower() for p in PLACEHOLDER_PATTERNS):
        return "ERROR: No valid GitHub repository name was provided. You MUST ask the user for the exact repository name in 'owner/repo' format before calling this tool."

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        return f"Error: GITHUB_TOKEN environment variable not set. Please set it to access real GitHub API."
    
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        
        try:
            readme = repo.get_readme()
            readme_content = readme.decoded_content.decode('utf-8')
            readme_snippet = readme_content[:1500] + ("..." if len(readme_content) > 1500 else "")
        except Exception:
            readme_snippet = "No README found or error fetching README."

        info = {
            "name": repo.full_name,
            "description": repo.description,
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "language": repo.language,
            "open_issues": repo.open_issues_count,
            "readme_snippet": readme_snippet
        }
        print(f"DEBUG - Crawling response: {info}")
        return f"Successfully crawled GitHub repo '{repo_name}'. Details: {info}"
    except Exception as e:
        return f"Error crawling GitHub repo '{repo_name}': {str(e)}"

@tool
def linkedin_profile_crawl(profile_url: str) -> str:
    """
    Crawls a LinkedIn profile to get user details using the Reverse Contact API.
    Requires a valid LinkedIn profile URL.
    """
    # Validate input — reject placeholders or obviously fake values
    PLACEHOLDER_PATTERNS = ["your-profile", "your-url", "example", "username", "profile-url", "<", ">", "janedoe", "linkedin.com/in/your"]
    if not profile_url or not "linkedin.com/in/" in profile_url.lower() or any(p in profile_url.lower() for p in PLACEHOLDER_PATTERNS):
        return "ERROR: No valid LinkedIn profile URL was provided. You MUST ask the user for the exact LinkedIn profile URL before calling this tool."

    api_key = os.environ.get("API_KEY_LINKEDIN_CRAWLER")
    if not api_key:
        return "Error: API_KEY_LINKEDIN_CRAWLER environment variable not set."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {"url": profile_url}
    
    try:
        response = requests.post("https://api.reversecontact.com/v2/fetch/persons", headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        
        if not result.get("success"):
            return f"Error crawling LinkedIn profile: {result.get('error')}"
        
        person = result.get("data")
        if not person:
            return "Error: No data found for this LinkedIn profile."
        
        # Build a highly detailed, field-by-field response to guide the AI
        firstName = person.get("firstName", "N/A")
        lastName = person.get("lastName", "N/A")
        headline = person.get("headline", "N/A")
        photoUrl = person.get("photoUrl", "N/A")
        isOpenToWork = person.get("isOpenToWork", False)
        
        loc = person.get("location", {})
        location = f"{loc.get('city', 'Unknown')}, {loc.get('country', 'Unknown')}"
        
        cur = person.get("currentPosition", {})
        currentPosition = f"{cur.get('title', 'N/A')} at {cur.get('companyName', 'N/A')}"
        
        experience = []
        for exp in person.get("experience", []):
            dates = exp.get("startEndDate", {})
            experience.append(f"- {exp.get('title')} at {exp.get('companyName')} (Started: {dates.get('start')}, Ended: {dates.get('end') or 'Present'})")
        experience_str = "\n".join(experience) if experience else "None listed"
        
        skills = ", ".join(person.get("skills", [])) if person.get("skills") else "None listed"
        
        output = (
            f"LINKEDIN DATA FOUND:\n"
            f"Public ID: {person.get('publicId', 'N/A')}\n"
            f"First Name: {firstName}\n"
            f"Last Name: {lastName}\n"
            f"Headline: {headline}\n"
            f"Photo URL: {photoUrl}\n"
            f"Open To Work: {isOpenToWork}\n"
            f"Location: {location}\n"
            f"Current Position: {currentPosition}\n"
            f"Experience History:\n{experience_str}\n"
            f"Skills: {skills}"
        )
        
        print(f"DEBUG - Tool Output Prepared:\n{output}")
        return output
    except Exception as e:
        return f"Error crawling LinkedIn profile '{profile_url}': {str(e)}"

tools_list = [github_repo_crawl, linkedin_profile_crawl]
