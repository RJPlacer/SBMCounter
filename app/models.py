from dataclasses import dataclass


@dataclass
class SchoolResult:

    school: str

    always: int = 0

    frequent: int = 0

    rare: int = 0

    notyet: int = 0

    na: int = 0

    total: int = 42