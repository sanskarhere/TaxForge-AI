from pydantic import BaseModel, Field, computed_field

from tax_synth.models.address import Address
from tax_synth.models.california import StateReturn
from tax_synth.models.enums import FilingStatus, Relationship
from tax_synth.models.federal import FederalReturn
from tax_synth.models.income import DividendIncome, InterestIncome, ScheduleCIncome, W2Income
from tax_synth.models.person import Person


class Dependent(BaseModel):
    first_name: str
    last_name: str
    ssn: str
    relationship: Relationship
    qualifies_child_tax_credit: bool = False

    @computed_field  # type: ignore[prop-decorator]
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class FilingInfo(BaseModel):
    federal_status: FilingStatus
    state_status: FilingStatus
    residency_state: str = "CA"
    full_year_resident: bool = True


class IncomeDocuments(BaseModel):
    w2: W2Income | None = None
    interest_1099_int: InterestIncome | None = None
    dividend_1099_div: DividendIncome | None = None
    schedule_c: ScheduleCIncome | None = None


class TaxCase(BaseModel):
    case_id: str = Field(min_length=1)
    tax_year: int = 2024

    taxpayer: Person
    spouse: Person | None = None
    address: Address
    filing: FilingInfo
    dependents: list[Dependent] = Field(default_factory=list)

    income_documents: IncomeDocuments

    federal_return: FederalReturn | None = None
    state_return: StateReturn| None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def dependent_count(self) -> int:
        return len(self.dependents)