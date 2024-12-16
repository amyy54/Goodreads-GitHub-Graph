from dataclasses import dataclass
from datetime import datetime


@dataclass
class Feed:
    id: int
    gr_id: int
    url_name: str
    timezone: str


@dataclass
class Status:
    id: int
    gr_id: int
    gr_guid: str
    gr_date: datetime
    gr_title: str
    gr_link: str
    gr_description: str
