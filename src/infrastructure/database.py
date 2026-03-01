"""Database setup and connection management.

Uses PostgreSQL via psycopg2.
The database URL is read from the config.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlparse

import psycopg2
import psycopg2.extras

logger = logging.getLogger(__name__)

# Path to init.sql relative to this file
_INIT_SQL = Path(__file__).resolve().parent.parent.parent / "db" / "init.sql"


class Database:
    """PostgreSQL database manager."""

    def __init__(self, database_url: str) -> None:
        self._database_url = database_url
        self._conn_params = self._parse_url(database_url)
        self._verify_connection()

    def _parse_url(self, url: str) -> dict:
        """Parse postgresql:// URL into connection parameters."""
        parsed = urlparse(url)
        return {
            "host": parsed.hostname or "localhost",
            "port": parsed.port or 5432,
            "dbname": parsed.path.lstrip("/"),
            "user": parsed.username or "forecaster",
            "password": parsed.password or "",
        }

    def _verify_connection(self) -> None:
        """Verify database connection works on startup."""
        try:
            with self.connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
            logger.info(
                "Database connected: %s@%s:%s/%s",
                self._conn_params["user"],
                self._conn_params["host"],
                self._conn_params["port"],
                self._conn_params["dbname"],
            )
        except psycopg2.OperationalError as exc:
            logger.error("Database connection failed: %s", exc)
            raise

    @contextmanager
    def connect(self):
        """Get a database connection (context manager).

        Usage:
            with db.connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT ...")
        """
        conn = psycopg2.connect(
            **self._conn_params,
            cursor_factory=psycopg2.extras.RealDictCursor,
        )
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
