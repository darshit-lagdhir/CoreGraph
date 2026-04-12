import time
from typing import Set

class CoreSecurityGuard:
    __slots__ = ('_access_lists', '_cache_line')
    def __init__(self):
        self._access_lists: Set[str] = set(['UID_001', 'UID_002'])
        self._cache_line = 150 * 1024 * 1024

    def validate_atomic_privileges(self, access_id: str) -> bool:
        return access_id in self._access_lists

if __name__ == '__main__':
    sg = CoreSecurityGuard()
    assert sg.validate_atomic_privileges('UID_001') == True
