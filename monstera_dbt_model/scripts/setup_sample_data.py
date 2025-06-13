#!/usr/bin/env python3
"""
Setup script for Monstera demo database following software engineering best practices.

This script is broken into small, testable functions that follow
the single responsibility principle.
"""

import json
from datetime import datetime
from typing import Any, Dict, List

from scripts.data_generators import (
    create_user_session_events,
    fake,
    generate_account_data,
    generate_project_data,
    generate_user_data,
    generate_video_data,
)
from scripts.db_utils import (
    create_database_connection,
    create_schema_if_not_exists,
    execute_sql_file,
)


def create_schemas(conn) -> bool:
    """Create bronze and silver schemas."""
    schemas = ["bronze", "silver"]
    for schema in schemas:
        if not create_schema_if_not_exists(conn, schema):
            return False
    return True


def get_entity_table_definitions() -> List[str]:
    """Get SQL definitions for entity tables."""
    return [
        """
        CREATE TABLE IF NOT EXISTS bronze.users (
            user_id VARCHAR(50) PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            country VARCHAR(50),
            created_at TIMESTAMP WITH TIME ZONE,
            account_id VARCHAR(50),
            is_active BOOLEAN DEFAULT TRUE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS bronze.accounts (
            account_id VARCHAR(50) PRIMARY KEY,
            account_name VARCHAR(255),
            account_type VARCHAR(50),
            industry VARCHAR(100),
            created_at TIMESTAMP WITH TIME ZONE,
            is_active BOOLEAN DEFAULT TRUE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS bronze.projects (
            project_id VARCHAR(50) PRIMARY KEY,
            project_name VARCHAR(255),
            account_id VARCHAR(50),
            created_by_user_id VARCHAR(50),
            status VARCHAR(50),
            created_at TIMESTAMP WITH TIME ZONE,
            updated_at TIMESTAMP WITH TIME ZONE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS bronze.videos (
            video_id VARCHAR(50) PRIMARY KEY,
            video_title VARCHAR(255),
            project_id VARCHAR(50),
            created_by_user_id VARCHAR(50),
            duration_seconds INTEGER,
            status VARCHAR(50),
            created_at TIMESTAMP WITH TIME ZONE,
            published_at TIMESTAMP WITH TIME ZONE
        )
        """,
    ]


def get_events_table_definition() -> str:
    """Get SQL definition for events table."""
    return """
        CREATE TABLE IF NOT EXISTS bronze.events (
            event_id SERIAL PRIMARY KEY,
            entity_id VARCHAR(50) NOT NULL,
            entity_type VARCHAR(50) NOT NULL,
            event_type VARCHAR(100) NOT NULL,
            timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
            location VARCHAR(100) NOT NULL,
            session_id VARCHAR(100),
            metadata JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
    """


def create_entity_tables(conn) -> bool:
    """Create all entity tables."""
    table_definitions = get_entity_table_definitions()
    return execute_sql_file(conn, table_definitions)


def create_events_table(conn) -> bool:
    """Create events table with indexes."""
    events_sql = get_events_table_definition()
    if not execute_sql_file(conn, [events_sql]):
        return False

    # Create indexes
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_events_entity_id ON bronze.events(entity_id)",
        "CREATE INDEX IF NOT EXISTS idx_events_event_type ON bronze.events(event_type)",
        "CREATE INDEX IF NOT EXISTS idx_events_timestamp ON bronze.events(timestamp)",
    ]

    return execute_sql_file(conn, indexes)


def insert_entity_data(conn, entities: Dict[str, List[Dict[str, Any]]]) -> bool:
    """Insert all entity data into database."""
    try:
        with conn.cursor() as cursor:
            # Insert accounts
            for account in entities["accounts"]:
                cursor.execute(
                    """
                    INSERT INTO bronze.accounts
                    (account_id, account_name, account_type, industry, created_at)
                    VALUES (%(account_id)s, %(account_name)s, %(account_type)s,
                            %(industry)s, %(created_at)s)
                    ON CONFLICT (account_id) DO NOTHING
                """,
                    account,
                )

            # Insert users
            for user in entities["users"]:
                cursor.execute(
                    """
                    INSERT INTO bronze.users
                    (user_id, email, first_name, last_name, country,
                     account_id, created_at)
                    VALUES (%(user_id)s, %(email)s, %(first_name)s, %(last_name)s,
                            %(country)s, %(account_id)s, %(created_at)s)
                    ON CONFLICT (user_id) DO NOTHING
                """,
                    user,
                )

            # Insert projects
            for project in entities["projects"]:
                cursor.execute(
                    """
                    INSERT INTO bronze.projects
                    (project_id, project_name, account_id, created_by_user_id,
                     status, created_at, updated_at)
                    VALUES (%(project_id)s, %(project_name)s, %(account_id)s,
                            %(created_by_user_id)s, %(status)s, %(created_at)s,
                            %(updated_at)s)
                    ON CONFLICT (project_id) DO NOTHING
                """,
                    project,
                )

            # Insert videos
            for video in entities["videos"]:
                cursor.execute(
                    """
                    INSERT INTO bronze.videos
                    (video_id, video_title, project_id, created_by_user_id,
                     duration_seconds, status, created_at, published_at)
                    VALUES (%(video_id)s, %(video_title)s, %(project_id)s,
                            %(created_by_user_id)s, %(duration_seconds)s, %(status)s,
                            %(created_at)s, %(published_at)s)
                    ON CONFLICT (video_id) DO NOTHING
                """,
                    video,
                )

            conn.commit()
        return True
    except Exception as e:
        print(f"Error inserting entity data: {e}")
        conn.rollback()
        return False


def generate_user_signup_event(user: Dict[str, Any]) -> Dict[str, Any]:
    """Generate signup event for a user."""
    return {
        "entity_id": user["user_id"],
        "entity_type": "user",
        "event_type": "user_signup",
        "timestamp": user["created_at"],
        "location": fake.random_element(["web_app", "mobile_app"]),
        "session_id": fake.uuid4(),
        "metadata": json.dumps(
            {
                "account_id": user["account_id"],
                "country": user["country"],
                "signup_source": fake.random_element(
                    ["organic", "referral", "paid_ad", "social"]
                ),
            }
        ),
    }


def insert_events_batch(
    conn, events: List[Dict[str, Any]], batch_size: int = 1000
) -> bool:
    """Insert events in batches for better performance."""
    try:
        with conn.cursor() as cursor:
            for i in range(0, len(events), batch_size):
                batch = events[i : i + batch_size]
                for event in batch:
                    cursor.execute(
                        """
                        INSERT INTO bronze.events
                        (entity_id, entity_type, event_type, timestamp,
                         location, session_id, metadata)
                        VALUES (%(entity_id)s, %(entity_type)s, %(event_type)s,
                                %(timestamp)s, %(location)s, %(session_id)s,
                                %(metadata)s)
                    """,
                        event,
                    )
                conn.commit()
                print(f"Inserted {len(batch)} events " f"(batch {i//batch_size + 1})")
        return True
    except Exception as e:
        print(f"Error inserting events: {e}")
        conn.rollback()
        return False


def main() -> None:
    """Main function to set up the Monstera demo database."""
    print("Setting up Monstera demo database...")

    # Connect to database
    conn = create_database_connection()
    if not conn:
        print(
            "Failed to connect to database. Please ensure PostgreSQL is running "
            "and database 'monstera_demo' exists."
        )
        return

    try:
        # Create schemas
        print("Creating schemas...")
        if not create_schemas(conn):
            raise Exception("Failed to create schemas")

        # Create tables
        print("Creating entity tables...")
        if not create_entity_tables(conn):
            raise Exception("Failed to create entity tables")

        print("Creating events table...")
        if not create_events_table(conn):
            raise Exception("Failed to create events table")

        # Generate data
        print("Generating entity data...")
        accounts = generate_account_data(50)
        users = generate_user_data(accounts, 200)
        projects = generate_project_data(users, 100)
        videos = generate_video_data(projects, 300)

        entities = {
            "accounts": accounts,
            "users": users,
            "projects": projects,
            "videos": videos,
        }

        # Insert entity data
        if not insert_entity_data(conn, entities):
            raise Exception("Failed to insert entity data")

        # Generate and insert events
        print("Generating events data...")
        all_events = []

        # Generate signup events
        for user in users:
            signup_event = generate_user_signup_event(user)
            all_events.append(signup_event)

        # Generate session events
        for user in users:
            current_date = user["created_at"]
            end_date = datetime.now()

            while current_date < end_date:
                if fake.random.random() < 0.7:  # 70% chance of daily activity
                    session_events = create_user_session_events(
                        user, current_date, projects, videos
                    )
                    all_events.extend(session_events)
                current_date += fake.timedelta(days=1)

        # Insert events
        if not insert_events_batch(conn, all_events):
            raise Exception("Failed to insert events")

        print("Setup completed successfully!")
        print(
            f"Created {len(accounts)} accounts, {len(users)} users, "
            f"{len(projects)} projects, {len(videos)} videos"
        )
        print(f"Generated {len(all_events)} total events")

    except Exception as e:
        print(f"Error during setup: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
