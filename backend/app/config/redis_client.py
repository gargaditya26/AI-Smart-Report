import json
import threading
import time
from typing import Any, Optional


class InMemoryClient:
    """
    Temporary in-memory replacement for Redis.

    This is suitable for Vercel testing/demo use only. Data is not persistent
    and may disappear when the serverless instance restarts or changes.
    """

    def __init__(self):
        self._data = {}
        self._lock = threading.Lock()

    def _purge_expired(self, key: str) -> None:
        item = self._data.get(key)
        if item and item["expires_at"] is not None and time.time() >= item["expires_at"]:
            self._data.pop(key, None)

    def set(self, key: str, value: Any) -> bool:
        with self._lock:
            self._data[key] = {"value": value, "expires_at": None}
        return True

    def setex(self, key: str, ttl: int, value: Any) -> bool:
        with self._lock:
            self._data[key] = {
                "value": value,
                "expires_at": time.time() + int(ttl),
            }
        return True

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            self._purge_expired(key)
            item = self._data.get(key)
            return None if item is None else item["value"]

    def delete(self, key: str) -> int:
        with self._lock:
            return 1 if self._data.pop(key, None) is not None else 0

    def exists(self, key: str) -> int:
        with self._lock:
            self._purge_expired(key)
            return 1 if key in self._data else 0

    def expire(self, key: str, ttl: int) -> bool:
        with self._lock:
            self._purge_expired(key)
            if key not in self._data:
                return False
            self._data[key]["expires_at"] = time.time() + int(ttl)
            return True

    def ping(self) -> bool:
        return True


class RedisClient:
    """
    Compatibility wrapper so the rest of the application can continue using
    redis_client.set_json/get_json/set_bytes/get_bytes/etc. without changes.
    """

    def __init__(self):
        self.client = InMemoryClient()

    @staticmethod
    def _decode(data: Any) -> Optional[str]:
        if data is None:
            return None
        if isinstance(data, bytes):
            return data.decode("utf-8")
        return str(data)

    def set_json(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        try:
            json_data = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
            if ttl and ttl > 0:
                return bool(self.client.setex(key, int(ttl), json_data.encode("utf-8")))
            return bool(self.client.set(key, json_data.encode("utf-8")))
        except Exception as e:
            print(f"In-memory set_json error for '{key}': {e}")
            return False

    def get_json(self, key: str) -> Optional[Any]:
        try:
            data = self.client.get(key)
            if data is None:
                return None
            decoded = self._decode(data)
            if not decoded:
                return None
            return json.loads(decoded)
        except Exception as e:
            print(f"In-memory get_json error for '{key}': {e}")
            return None

    def set_bytes(self, key: str, value: bytes, ttl: Optional[int] = None) -> bool:
        try:
            if ttl and ttl > 0:
                return bool(self.client.setex(key, int(ttl), value))
            return bool(self.client.set(key, value))
        except Exception as e:
            print(f"In-memory set_bytes error for '{key}': {e}")
            return False

    def get_bytes(self, key: str) -> Optional[bytes]:
        try:
            data = self.client.get(key)
            if data is None:
                return None
            if isinstance(data, bytes):
                return data
            return str(data).encode("utf-8")
        except Exception as e:
            print(f"In-memory get_bytes error for '{key}': {e}")
            return None

    def delete(self, key: str) -> bool:
        try:
            return self.client.delete(key) > 0
        except Exception as e:
            print(f"In-memory delete error: {e}")
            return False

    def exists(self, key: str) -> bool:
        try:
            return self.client.exists(key) > 0
        except Exception as e:
            print(f"In-memory exists error: {e}")
            return False

    def set_ttl(self, key: str, ttl: int) -> bool:
        try:
            return bool(self.client.expire(key, int(ttl)))
        except Exception as e:
            print(f"In-memory TTL error: {e}")
            return False

    def ping(self) -> bool:
        try:
            return bool(self.client.ping())
        except Exception as e:
            print(f"In-memory ping error: {e}")
            return False


redis_client = RedisClient()
