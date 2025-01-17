import time
from . import User, Tweet
from ..utils import find_objects, parse_wait_time


class BaseGeneratorClass(dict):

    @staticmethod
    def _get_cursor_(response, cursor_key="Bottom"):
        cursor = find_objects(response, "cursorType", cursor_key, recursive=False, none_value={})
        return cursor.get("value", None)

    def _has_next_page(self, new_cursor):
        if new_cursor == self.cursor:
            return False

        self.cursor = new_cursor
        return True

    @staticmethod
    def _get_entries(response, key_value="TimelineAddEntries"):
        entry = find_objects(response, "type", key_value)

        if not entry:
            return []

        return entry.get('entries', [])

    def get_next_page(self, cursor=0):
        if cursor == 0 and not self.is_next_page:
            return []

        cursor = cursor if cursor != 0 else self.cursor

        results, cursor, cursor_top = self.get_page(cursor)
        self.is_next_page = self._has_next_page(cursor)
        self.cursor, self.cursor_top = cursor, cursor_top
        _result_attr = self._RESULT_ATTR
        getattr(self, _result_attr).extend(results)
        self[_result_attr] = getattr(self, _result_attr)
        self['cursor'], self['cursor_top'], self['is_next_page'] = self.cursor, self.cursor_top, self.is_next_page

        for result in results:
            if isinstance(result, User):
                self.client._cached_users[result.username.lower()] = result.id
            elif isinstance(result, Tweet):
                self.client._cached_users[result.author.username.lower()] = result.author.id

        return results

    def generator(self):
        for page in range(1, int(self.pages) + 1):
            results = self.get_next_page()

            if len(results) == 0:
                break

            yield self, results

            if not self.is_next_page:
                break

            if page != self.pages:
                time.sleep(parse_wait_time(self.wait_time))

        return self

    def __repr__(self):
        class_name = self.__class__.__name__
        return "{}(user_id={}, count={})".format(
            class_name, self.user_id, self.__len__()
        )

    def __getitem__(self, index):
        if isinstance(index, str):
            return getattr(self, index)

        return getattr(self, self._RESULT_ATTR)[index]

    def __iter__(self):
        for i in getattr(self, self._RESULT_ATTR):
            yield i

    def __len__(self):
        return len(getattr(self, self._RESULT_ATTR))