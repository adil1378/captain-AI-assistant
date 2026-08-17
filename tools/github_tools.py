"""
Captain AI OS — GitHub Integration Tools.
Provides utility functions to interact with GitHub REST API and git operations.
"""

import os
import subprocess
from typing import Dict, Any, Optional
import requests
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

_GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
_API_BASE = "https://api.github.com"


def _get_headers() -> Dict[str, str]:
    """Build GitHub API authorization headers if token is present."""
    headers = {"Accept": "application/vnd.github.v3+json"}
    if _GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {_GITHUB_TOKEN}"
    return headers


def get_authenticated_user() -> Dict[str, Any]:
    """Retrieve details of the authenticated GitHub user."""
    if not _GITHUB_TOKEN:
        return {"status": "error", "error": "GITHUB_TOKEN not configured in .env file."}
    try:
        resp = requests.get(f"{_API_BASE}/user", headers=_get_headers(), timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "status": "success",
                "username": data.get("login"),
                "name": data.get("name"),
                "html_url": data.get("html_url")
            }
        return {"status": "error", "error": f"API HTTP {resp.status_code}: {resp.text}"}
    except Exception as e:
        logger.error(f"GitHub get_authenticated_user error: {e}")
        return {"status": "error", "error": str(e)}


def create_github_repo(repo_name: str, description: str = "", private: bool = False) -> Dict[str, Any]:
    """
    Create a new repository on GitHub for the authenticated user.

    Args:
        repo_name: Name of the repository to create.
        description: Short description of the project.
        private: Whether the repo should be private (default False).
    """
    if not _GITHUB_TOKEN:
        return {
            "status": "error",
            "error": "GITHUB_TOKEN is missing. Please add GITHUB_TOKEN to your .env file."
        }
    try:
        payload = {
            "name": repo_name,
            "description": description or "Captain AI OS Repository",
            "private": private,
            "auto_init": False
        }
        resp = requests.post(f"{_API_BASE}/user/repos", json=payload, headers=_get_headers(), timeout=10)
        if resp.status_code in [200, 201]:
            data = resp.json()
            return {
                "status": "success",
                "repo_name": data.get("name"),
                "full_name": data.get("full_name"),
                "clone_url": data.get("clone_url"),
                "ssh_url": data.get("ssh_url"),
                "html_url": data.get("html_url")
            }
        return {"status": "error", "error": f"API HTTP {resp.status_code}: {resp.text}"}
    except Exception as e:
        logger.error(f"GitHub create_github_repo error: {e}")
        return {"status": "error", "error": str(e)}


def list_user_repos(limit: int = 10) -> Dict[str, Any]:
    """List recent repositories for the authenticated user."""
    if not _GITHUB_TOKEN:
        return {"status": "error", "error": "GITHUB_TOKEN is missing."}
    try:
        resp = requests.get(
            f"{_API_BASE}/user/repos?sort=updated&per_page={limit}",
            headers=_get_headers(),
            timeout=10
        )
        if resp.status_code == 200:
            repos = [
                {
                    "name": r.get("name"),
                    "full_name": r.get("full_name"),
                    "url": r.get("html_url"),
                    "private": r.get("private")
                }
                for r in resp.json()
            ]
            return {"status": "success", "count": len(repos), "repos": repos}
        return {"status": "error", "error": f"API HTTP {resp.status_code}: {resp.text}"}
    except Exception as e:
        logger.error(f"GitHub list_user_repos error: {e}")
        return {"status": "error", "error": str(e)}


def git_commit_and_push(commit_message: str = "Update Captain AI OS", remote_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Stage all changes, commit, and optionally push to a remote git repository.
    """
    try:
        # git add .
        subprocess.run(["git", "add", "."], check=True, capture_output=True, text=True)

        # git commit -m
        commit_res = subprocess.run(
            ["git", "commit", "-m", commit_message],
            capture_output=True,
            text=True
        )
        commit_out = commit_res.stdout or commit_res.stderr

        # Set remote if provided
        if remote_url:
            subprocess.run(["git", "remote", "remove", "origin"], capture_output=True)
            subprocess.run(["git", "remote", "add", "origin", remote_url], check=True, capture_output=True)

        return {
            "status": "success",
            "commit_message": commit_message,
            "detail": commit_out.strip()
        }
    except Exception as e:
        logger.error(f"Git commit error: {e}")
        return {"status": "error", "error": str(e)}
