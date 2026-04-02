from datetime import date

from pydantic import BaseModel, Field, computed_field


class Person(BaseModel):
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    ssn: str = Field(min_length=11, max_length=11)
    dob: date
    occupation: str | None = None
    employer: str | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"