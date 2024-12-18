from os import getenv
from typing import List, Tuple
from objects import Feed, Status
import psycopg
from datetime import datetime
from utils import print_log_with_timestamp

DB_CONNSTRING = getenv(
    "DB_CONNSTRING",
    "postgresql://postgres:password@goodreads-github-graph-postgres-1:5432/dev_goodreads_graph",
)


def init_db() -> None:
    with psycopg.connect(DB_CONNSTRING) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS status (
                    id serial primary key,
                    gr_id integer,
                    gr_guid text,
                    gr_date timestamp,
                    gr_title text,
                    gr_link text,
                    gr_description text
                )
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS feeds (
                    id serial primary key,
                    gr_id integer,
                    url_name text,
                    timezone text
                )
                """
            )

        conn.commit()


def get_feeds(gr_id: int = -1, url_name: str = "") -> List[Feed]:
    res: List[Feed] = []
    with psycopg.connect(DB_CONNSTRING) as conn:
        with conn.cursor() as cur:
            if gr_id != -1:
                cur.execute(
                    "SELECT id, gr_id, url_name, timezone FROM feeds WHERE gr_id = %s",
                    (gr_id,),
                )
            elif len(url_name) > 0:
                cur.execute(
                    "SELECT id, gr_id, url_name, timezone FROM feeds WHERE url_name = %s",
                    (url_name,),
                )
            else:
                cur.execute("SELECT id, gr_id, url_name, timezone FROM feeds")
            for obj in cur.fetchall():
                if len(obj) == 4:
                    res.append(
                        Feed(id=obj[0], gr_id=obj[1], url_name=obj[2], timezone=obj[3])
                    )
    return res


def get_statuses(gr_id: int = -1) -> List[Status]:
    res: List[Status] = []
    with psycopg.connect(DB_CONNSTRING) as conn:
        with conn.cursor() as cur:
            if gr_id != -1:
                cur.execute(
                    "SELECT id, gr_id, gr_guid, gr_date, gr_title, gr_link, gr_description FROM status WHERE gr_id = %s",
                    (gr_id,),
                )
            else:
                cur.execute(
                    "SELECT id, gr_id, gr_guid, gr_date, gr_title, gr_link, gr_description FROM status"
                )
            for obj in cur.fetchall():
                if len(obj) == 7:
                    res.append(
                        Status(
                            id=obj[0],
                            gr_id=obj[1],
                            gr_guid=obj[2],
                            gr_date=obj[3],
                            gr_title=obj[4],
                            gr_link=obj[5],
                            gr_description=obj[6],
                        )
                    )
    return res


def add_status(status: Status) -> None:
    with psycopg.connect(DB_CONNSTRING) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT gr_guid, gr_date FROM status WHERE gr_id = %s", (status.gr_id,)
            )
            compare_sql: List[Tuple[str, datetime]] = cur.fetchall()

            sanitized_compare_sql: List[Tuple[str, str]] = []
            for entry in compare_sql:
                sanitized_compare_sql.append(
                    (entry[0], entry[1].strftime("%Y-%m-%dT%H:%M:%S"))
                )

            if (
                status.gr_guid,
                status.gr_date.strftime("%Y-%m-%dT%H:%M:%S"),
            ) not in sanitized_compare_sql:
                print_log_with_timestamp(
                    "Database", f'Adding "{status.gr_title}" to database'
                )
                cur.execute(
                    "INSERT INTO status (gr_id, gr_guid, gr_date, gr_title, gr_link, gr_description) VALUES (%s, %s, %s, %s, %s, %s)",
                    (
                        status.gr_id,
                        status.gr_guid,
                        status.gr_date.strftime("%Y-%m-%dT%H:%M:%S"),
                        status.gr_title,
                        status.gr_link,
                        status.gr_description,
                    ),
                )
        conn.commit()
