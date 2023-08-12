import time
from ..utils import find_object


class BaseGeneratorClass(dict):

    def _get_cursor(self, response):
        cursor = find_object(response, lambda x: x.get("cursorType") == "Bottom")

        if not cursor:
            return False

        newCursor = cursor.get('value', self.cursor)

        if newCursor == self.cursor:
            return False

        self.cursor = newCursor
        return True

    def generator(self):
        for page in range(1, int(self.pages) + 1):
            results = self.get_next_page()

            yield self, results

            if not self.is_next_page:
                break

            if page != self.pages:
                time.sleep(self.wait_time)

        return self

    def __repr__(self):
        class_name = self.__class__.__name__
        return "{}(user_id={}, count={})".format(
            class_name, self.user_id, self.__len__()
        )