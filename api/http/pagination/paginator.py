import sys
from functools import cached_property

from django.core.paginator import Paginator as DjangoPaginator


class Paginator(DjangoPaginator):
    def __init__(self, object_list, per_page, orphans=0, allow_empty_first_page=True):
        super().__init__(object_list, per_page, orphans, allow_empty_first_page)
        self.get_all = False

    def all(self):
        """Return a Page object for all items."""
        self.get_all = True
        return self._get_page(self.object_list, 1, self)

    @cached_property
    def num_pages(self):
        """Return the total number of pages."""
        if self.get_all:
            return 1

        return super().num_pages

    @cached_property
    def count(self):
        return sys.maxsize

    def get_total_items_count(self):
        return super().count
