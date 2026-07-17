from dataclasses import dataclass, field

@dataclass
class SBMAssessment:

    school_name: str = ""

    school_id: str = ""

    responses: list[str] = field(default_factory=list)