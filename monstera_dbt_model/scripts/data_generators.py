#!/usr/bin/env python3
"""
Data generation utilities for the Monstera dbt project.

This module contains functions for generating realistic sample data
that follows the Monstera event schema standards.
"""

import json
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List

from faker import Faker

# Initialize Faker
fake = Faker()


def generate_account_data(count: int = 50) -> List[Dict[str, Any]]:
    """
    Generate sample account data.

    Args:
        count: Number of accounts to generate

    Returns:
        List of account dictionaries
    """
    account_types = ["enterprise", "small_business", "individual"]
    industries = ["technology", "healthcare", "finance", "education", "media", "retail"]

    accounts = []
    for i in range(count):
        account = {
            "account_id": f"acc_{i+1: 03d}",
            "account_name": fake.company(),
            "account_type": random.choice(account_types),
            "industry": random.choice(industries),
            "created_at": fake.date_time_between(start_date="-2y", end_date="-30d"),
        }
        accounts.append(account)

    return accounts


def generate_user_data(
    accounts: List[Dict[str, Any]], count: int = 200
) -> List[Dict[str, Any]]:
    """
    Generate sample user data linked to accounts.

    Args:
        accounts: List of account dictionaries
        count: Number of users to generate

    Returns:
        List of user dictionaries
    """
    countries = [
        "US",
        "Canada",
        "UK",
        "Germany",
        "France",
        "Australia",
        "Japan",
        "Brazil",
    ]

    users = []
    for i in range(count):
        account = random.choice(accounts)
        user = {
            "user_id": f"user_{i+1: 03d}",
            "email": fake.email(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "country": random.choice(countries),
            "account_id": account["account_id"],
            "created_at": fake.date_time_between(
                start_date=account["created_at"], end_date="now"
            ),
        }
        users.append(user)

    return users


def generate_project_data(
    users: List[Dict[str, Any]], count: int = 100
) -> List[Dict[str, Any]]:
    """
    Generate sample project data linked to users.

    Args:
        users: List of user dictionaries
        count: Number of projects to generate

    Returns:
        List of project dictionaries
    """
    project_statuses = ["active", "completed", "archived", "draft"]

    projects = []
    for i in range(count):
        user = random.choice(users)
        created_at = fake.date_time_between(
            start_date=user["created_at"], end_date="now"
        )

        project = {
            "project_id": f"proj_{i+1: 03d}",
            "project_name": f"Project {fake.catch_phrase()}",
            "account_id": user["account_id"],
            "created_by_user_id": user["user_id"],
            "status": random.choice(project_statuses),
            "created_at": created_at,
            "updated_at": fake.date_time_between(start_date=created_at, end_date="now"),
        }
        projects.append(project)

    return projects


def generate_video_data(
    projects: List[Dict[str, Any]], count: int = 300
) -> List[Dict[str, Any]]:
    """
    Generate sample video data linked to projects.

    Args:
        projects: List of project dictionaries
        count: Number of videos to generate

    Returns:
        List of video dictionaries
    """
    video_statuses = ["draft", "published", "archived"]

    videos = []
    for i in range(count):
        project = random.choice(projects)
        created_at = fake.date_time_between(
            start_date=project["created_at"], end_date="now"
        )
        status = random.choice(video_statuses)
        published_at = (
            created_at + timedelta(hours=random.randint(1, 48))
            if status == "published"
            else None
        )

        video = {
            "video_id": f"vid_{i+1: 03d}",
            "video_title": f"Video: {fake.sentence(nb_words=4)}",
            "project_id": project["project_id"],
            "created_by_user_id": project["created_by_user_id"],
            "duration_seconds": random.randint(30, 1800),
            "status": status,
            "created_at": created_at,
            "published_at": published_at,
        }
        videos.append(video)

    return videos


def generate_event_metadata(
    event_type: str,
    user: Dict[str, Any],
    projects: List[Dict[str, Any]],
    videos: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Generate appropriate metadata for an event.

    Args:
        event_type: Type of event
        user: User dictionary
        projects: List of available projects
        videos: List of available videos

    Returns:
        Metadata dictionary for the event
    """
    metadata = {"account_id": user["account_id"]}

    if event_type.startswith("project_"):
        user_projects = [
            p for p in projects if p["created_by_user_id"] == user["user_id"]
        ]
        if user_projects:
            metadata["project_id"] = random.choice(user_projects)["project_id"]

    elif event_type.startswith("video_"):
        user_videos = [v for v in videos if v["created_by_user_id"] == user["user_id"]]
        if user_videos:
            video = random.choice(user_videos)
            metadata["video_id"] = video["video_id"]
            metadata["project_id"] = video["project_id"]

    return metadata


def create_user_session_events(
    user: Dict[str, Any],
    session_date: datetime,
    projects: List[Dict[str, Any]],
    videos: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Generate events for a single user session.

    Args:
        user: User dictionary
        session_date: Date of the session
        projects: List of available projects
        videos: List of available videos

    Returns:
        List of event dictionaries for the session
    """
    events = []
    session_id = fake.uuid4()
    locations = ["web_app", "mobile_app", "api", "desktop_app"]
    location = random.choice(locations)

    # Login event
    login_time = session_date.replace(
        hour=random.randint(8, 18), minute=random.randint(0, 59)
    )
    login_event = {
        "entity_id": user["user_id"],
        "entity_type": "user",
        "event_type": "user_login",
        "timestamp": login_time,
        "location": location,
        "session_id": session_id,
        "metadata": json.dumps(
            {
                "account_id": user["account_id"],
                "device_type": random.choice(["desktop", "mobile", "tablet"]),
            }
        ),
    }
    events.append(login_event)

    # Session activities
    session_duration = random.randint(5, 120)  # 5 minutes to 2 hours
    session_end = login_time + timedelta(minutes=session_duration)

    activity_count = random.randint(1, 10)
    activity_types = [
        "project_create",
        "project_update",
        "video_create",
        "video_upload",
        "comment_add",
    ]

    for _ in range(activity_count):
        activity_time = login_time + timedelta(
            minutes=random.randint(1, session_duration - 1)
        )
        activity_type = random.choice(activity_types)

        metadata = generate_event_metadata(activity_type, user, projects, videos)

        activity_event = {
            "entity_id": user["user_id"],
            "entity_type": "user",
            "event_type": activity_type,
            "timestamp": activity_time,
            "location": location,
            "session_id": session_id,
            "metadata": json.dumps(metadata),
        }
        events.append(activity_event)

    # Logout event
    logout_event = {
        "entity_id": user["user_id"],
        "entity_type": "user",
        "event_type": "user_logout",
        "timestamp": session_end,
        "location": location,
        "session_id": session_id,
        "metadata": json.dumps(
            {
                "account_id": user["account_id"],
                "session_duration_minutes": session_duration,
            }
        ),
    }
    events.append(logout_event)

    return events
