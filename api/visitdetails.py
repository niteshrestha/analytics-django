import json
from typing import List


class Details(object):
    def __init__(self, page: str, count: int):
        self.page = page
        self.count = count
