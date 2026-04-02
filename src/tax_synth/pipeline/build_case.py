from __future__ import annotations

import random

from tax_synth.generators.income_generator import IncomeGenerator
from tax_synth.generators.profile_generator import ProfileGenerator
from tax_synth.models.case import Dependent, FilingInfo, IncomeDocuments, TaxCase
from tax_synth.models.enums import FilingStatus, Relationship
from tax_synth.rules.california_rules import build_california_return
from tax_synth.rules.federal_rules import build_federal_return


def build_one_case(case_id: str, seed: int = 42) -> TaxCase:
    profile_gen = ProfileGenerator(seed=seed)
    income_gen = IncomeGenerator(seed=seed)

    taxpayer = profile_gen.build_person(
        min_age=30,
        max_age=55,
        occupation="Graphic Designer",
        employer=None,
    )
    spouse = profile_gen.build_person(
        min_age=25,
        max_age=50,
        occupation="Nurse",
        employer="Pacific Health System Inc.",
    )

    dependent_count = random.choice([0, 1, 2, 3])
    dependents: list[Dependent] = []

    for _ in range(dependent_count):
        relationship = random.choice([Relationship.SON, Relationship.DAUGHTER])
        qualifies_credit = random.choice([True, False])

        dependents.append(
            Dependent(
                first_name=profile_gen.fake.first_name(),
                last_name=taxpayer.last_name,
                ssn=profile_gen.fake_ssn(),
                relationship=relationship,
                qualifies_child_tax_credit=qualifies_credit,
            )
        )

    income_docs = IncomeDocuments(
        w2=income_gen.build_w2("Pacific Health System Inc."),
        interest_1099_int=income_gen.build_interest(),
        dividend_1099_div=income_gen.build_dividends(),
        schedule_c=income_gen.build_schedule_c(),
    )

    case = TaxCase(
        case_id=case_id,
        tax_year=2024,
        taxpayer=taxpayer,
        spouse=spouse,
        address=profile_gen.build_address(),
        filing=FilingInfo(
            federal_status=FilingStatus.MFJ,
            state_status=FilingStatus.MFJ,
            residency_state="CA",
            full_year_resident=True,
        ),
        dependents=dependents,
        income_documents=income_docs,
    )

    case.federal_return = build_federal_return(case)
    case.california_return = build_california_return(case)
    return case