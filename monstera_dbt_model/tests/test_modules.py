#!/usr/bin/env python3
"""
Test for data generation modules.
This module contains unit tests for the refactored data generation functions.
"""

import os
import sys
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

# Add scripts directory to path - this must be done before imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.data_generators import (  # noqa: E402
    create_user_session_events,
    generate_account_data,
    generate_project_data,
    generate_user_data,
    generate_video_data,
)
from scripts.db_utils import create_database_connection, get_db_config  # noqa: E402
from scripts.setup_sample_data import (  # noqa: E402
    create_entity_tables,
    create_events_table,
    create_schemas,
)


class TestDatabaseUtils:
    """Test database utility functions."""

    def test_get_db_config(self):
        """Test database configuration retrieval."""
        config = get_db_config()
        required_fields = ["host", "port", "user", "password", "database"]

        for field in required_fields:
            assert field in config
            assert config[field] is not None

    @patch("scripts.db_utils.psycopg2.connect")
    def test_create_database_connection_success(self, mock_connect):
        """Test successful database connection."""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        result = create_database_connection()

        assert result == mock_conn
        mock_connect.assert_called_once()

    @patch("scripts.db_utils.psycopg2.connect")
    def test_create_database_connection_failure(self, mock_connect):
        """Test database connection failure handling."""
        mock_connect.side_effect = Exception("Connection failed")

        result = create_database_connection()

        assert result is None


class TestDataGenerators:
    """Test data generation functions."""

    def test_generate_account_data(self):
        """Test account data generation."""
        accounts = generate_account_data(5)

        assert len(accounts) == 5
        for account in accounts:
            assert "account_id" in account
            assert "account_name" in account
            assert "account_type" in account
            assert "created_at" in account

    def test_generate_user_data(self):
        """Test user data generation."""
        accounts = [
            {"account_id": f"acc_{i}", "created_at": datetime(2024, 1, 1)}
            for i in range(3)
        ]
        users = generate_user_data(accounts, 10)

        assert len(users) == 10
        for user in users:
            assert "user_id" in user
            assert "email" in user
            assert "first_name" in user
            assert "last_name" in user
            assert "account_id" in user

    def test_generate_project_data(self):
        """Test project data generation."""
        users = [
            {
                "user_id": f"user_{i}",
                "account_id": f"acc_{i//3}",
                "created_at": datetime(2024, 1, 1),
            }
            for i in range(6)
        ]
        projects = generate_project_data(users, 8)

        assert len(projects) == 8
        for project in projects:
            assert "project_id" in project
            assert "project_name" in project
            assert "account_id" in project

    def test_generate_video_data(self):
        """Test video data generation."""
        projects = [
            {
                "project_id": f"proj_{i}",
                "account_id": f"acc_{i % 3}",
                "created_at": datetime(2024, 1, 1),
                "created_by_user_id": f"user_{i % 3}",
            }
            for i in range(5)
        ]
        videos = generate_video_data(projects, 15)

        assert len(videos) == 15
        for video in videos:
            assert "video_id" in video
            assert "video_title" in video
            assert "project_id" in video

    def test_create_user_session_events(self):
        """Test event data generation."""
        users = [
            {"user_id": f"user_{i}", "account_id": f"acc_{i % 3}"} for i in range(5)
        ]
        projects = [
            {
                "project_id": f"proj_{i}",
                "account_id": f"acc_{i % 3}",
                "created_by_user_id": f"user_{i % 5}",
            }
            for i in range(3)
        ]
        videos = [
            {
                "video_id": f"vid_{i}",
                "project_id": f"proj_{i % 3}",
                "created_by_user_id": f"user_{i % 5}",
            }
            for i in range(3)
        ]

        # Test single user session event generation
        user = users[0]
        session_date = datetime.now()
        events = create_user_session_events(user, session_date, projects, videos)

        assert len(events) > 0
        for event in events:
            assert "entity_id" in event
            assert "entity_type" in event
            assert "event_type" in event
            assert "timestamp" in event
            assert "location" in event


class TestTableCreation:
    """Test table creation functions."""

    @patch("scripts.setup_sample_data.create_schema_if_not_exists")
    def test_create_schemas(self, mock_create_schema):
        """Test schema creation."""
        mock_conn = Mock()
        mock_create_schema.return_value = True

        result = create_schemas(mock_conn)

        assert result is True
        # Should call create_schema_if_not_exists for each schema (bronze, silver)
        assert mock_create_schema.call_count == 2

    @patch("scripts.setup_sample_data.execute_sql_file")
    def test_create_entity_tables(self, mock_execute):
        """Test entity table creation."""
        mock_conn = Mock()
        mock_execute.return_value = True

        result = create_entity_tables(mock_conn)

        assert result is True
        # Should be called once with table definitions
        mock_execute.assert_called_once()

    @patch("scripts.setup_sample_data.execute_sql_file")
    def test_create_events_table(self, mock_execute):
        """Test events table creation."""
        mock_conn = Mock()
        mock_execute.return_value = True

        result = create_events_table(mock_conn)

        assert result is True
        # Should be called twice: once for table creation, once for index creation
        assert mock_execute.call_count == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
