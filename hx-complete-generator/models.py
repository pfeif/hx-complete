from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Value:
    name: str
    description: str | None = field(default=None)


@dataclass
class ValueSet:
    name: str
    values: list[Value] = field(default_factory=list)


@dataclass
class Reference:
    name: str
    url: str


@dataclass
class Attribute:
    name: str
    description: str
    value_set: str | None = field(default=None)
    references: list[Reference] = field(default_factory=list)


@dataclass
class HtmlData:
    version: float = field(default=1.1, init=False)
    tags: list[None] = field(default_factory=list, init=False)
    global_attributes: list[Attribute] = field(default_factory=list)
    value_sets: list[ValueSet] = field(default_factory=list)

    @staticmethod
    def __camel_case(key: str):
        parts = key.split('_')
        return parts[0].lower() + ''.join(part.title() for part in parts[1:])

    def as_dict(self) -> dict[str, Any]:
        return asdict(
            self,
            dict_factory=lambda fields: {self.__camel_case(key): value for (key, value) in fields if value is not None},
        )
