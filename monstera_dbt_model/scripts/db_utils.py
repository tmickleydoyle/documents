#!/usr/bin/env python3
"""
Database utility functions for the Monstera dbt project.

This module contains reusable database functions that are
used across the sample data generation scripts.
"""

import os
from typing import Any, Dict, Optional

import psycopg2
import psycopg2.extensions


def get_db_config() -> Dict[str, Any]:
    """
    Get database configuration from environment variables.

    Returns:
        Dict containing database connection parameters.
    """
    return {
        "host": os.environ.get("POSTGRES_HOST", "localhost"),
        "database": os.environ.get("POSTGRES_DATABASE", "monstera_demo"),
        "user": os.environ.get("POSTGRES_USER", "tmickleydoyle"),
        "password": os.environ.get("POSTGRES_PASSWORD", ""),
        "port": int(os.environ.get("POSTGRES_PORT", "5432")),
    }


def create_database_connection() -> Optional[psycopg2.extensions.connection]:
    """
    Create a database connection using configuration.

    Returns:
        Database connection object or None if connection fails.
    """
    try:
        config = get_db_config()
        return psycopg2.connect(**config)
    except Exception as e:
        print(f"Database connection error: {e}")
        return None


def execute_sql_file(
    conn: psycopg2.extensions.connection, sql_statements: list
) -> bool:
    """
    Execute a list of SQL statements safely.

    Args:
        conn: Database connection
        sql_statements: List of SQL statements to execute

    Returns:
        True if all statements executed successfully, False otherwise.
    """
    try:
        with conn.cursor() as cursor:
            for statement in sql_statements:
                cursor.execute(statement)
            conn.commit()
        return True
    except psycopg2.Error as e:
        print(f"SQL execution error: {e}")
        conn.rollback()
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        conn.rollback()
        return False


def create_schema_if_not_exists(
    conn: psycopg2.extensions.connection, schema_name: str
) -> bool:
    """
    Create a schema if it doesn't exist.

    Args:
        conn: Database connection
        schema_name: Name of schema to create

    Returns:
        True if schema was created or already exists, False otherwise.
    """
    sql = f"CREATE SCHEMA IF NOT EXISTS {schema_name}"
    return execute_sql_file(conn, [sql])


def table_exists(
    conn: psycopg2.extensions.connection, table_name: str, schema_name: str = "public"
) -> bool:
    """
    Check if a table exists in the specified schema.

    Args:
        conn: Database connection
        table_name: Name of table to check
        schema_name: Schema to check in (default: 'public')

    Returns:
        True if table exists, False otherwise.
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = %s
                    AND table_name = %s
                )
            """,
                (schema_name, table_name),
            )

            return cursor.fetchone()[0]
    except Exception as e:
        print(f"Error checking table existence: {e}")
        return False


def get_table_row_count(
    conn: psycopg2.extensions.connection, table_name: str, schema_name: str = "public"
) -> int:
    """
    Get the number of rows in a table.

    Args:
        conn: Database connection
        table_name: Name of table
        schema_name: Schema name (default: 'public')

    Returns:
        Number of rows in the table, -1 if error.
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM {schema_name}.{table_name}")
            return cursor.fetchone()[0]
    except Exception as e:
        print(f"Error getting row count: {e}")
        return -1
