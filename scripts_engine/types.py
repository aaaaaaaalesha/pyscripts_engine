from typing import Any, Protocol, Literal

ModeLiteral = Literal["eval", "exec"]


class Object(Protocol):
    """Объект (нечто, поддерживающие протокол `__getattr__`)."""

    def __getattr__(self, attr: str) -> Any: ...
