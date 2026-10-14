from dataclasses import dataclass
from threading import Lock
from uuid import uuid4


@dataclass(frozen=True)
class Photo:
    id: str
    content: bytes


class PhotoStack:
    """Pila de fotografías en memoria, con capacidad limitada."""

    def __init__(self, capacity: int = 30) -> None:
        if capacity < 1:
            raise ValueError("La capacidad debe ser mayor que cero.")

        self._items: list[Photo] = []
        self._capacity = capacity
        self._lock = Lock()

    def push(self, content: bytes) -> Photo:
        with self._lock:
            if len(self._items) >= self._capacity:
                raise OverflowError("La pila está llena. Desapila una foto.")

            photo = Photo(id=uuid4().hex, content=content)
            self._items.append(photo)
            return photo

    def pop(self) -> Photo:
        with self._lock:
            if not self._items:
                raise IndexError("La pila está vacía.")

            return self._items.pop()

    def snapshot(self) -> list[Photo]:
        """Devuelve una copia ordenada desde la cima hasta la base."""
        with self._lock:
            return list(reversed(self._items))

    def find(self, photo_id: str) -> Photo | None:
        with self._lock:
            return next(
                (photo for photo in self._items if photo.id == photo_id),
                None,
            )