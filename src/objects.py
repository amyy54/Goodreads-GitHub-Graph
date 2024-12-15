from dataclasses import dataclass
from time import struct_time


@dataclass
class Feed:
    id: int
    gr_id: int
    url_name: str


@dataclass
class Status:
    id: int
    gr_id: int
    gr_guid: str
    gr_date: struct_time
    gr_title: str
    gr_link: str
    gr_description: str
