from __future__ import annotations
import random
from tax_synth.generators.income_generator import IncomeGenerator
from tax_synth.generators.profile_generator import ProfileGenerator
from tax_synth.models.case import Dependent, FilingInfo, IncomeDocuments, TaxCase
from tax_synth.models.enums import FilingStatus, Relationship
from tax_synth.rules.california_rules import build_california_return
from tax_synth.rules.federal_rules import build_federal_return


def build_one_case(case_id: str, seed: int = 42) -> TaxCase:
    random.seed(seed)

    profile_gen = ProfileGenerator(seed=seed)
    income_gen = IncomeGenerator(seed=seed)

    states = ["CA", "TX", "NY", "FL", "WA"]
    years = [2019, 2020, 2021, 2022, 2023, 2024]
    filings = [FilingStatus.SINGLE, FilingStatus.MFJ, FilingStatus.HOH]

    taxpayer_occupations = [
        "Graphic Designer",
        "Software Engineer",
        "Data Analyst",
        "Marketing Manager",
        "Teacher",
        "Accountant",
    ]
    spouse_occupations = [
        "Nurse",
        "Business Analyst",
        "HR Specialist",
        "Teacher",
        "Project Coordinator",
        "Pharmacist",
    ]
    spouse_employers = [
        "Pacific Health System Inc.",
        "NorthStar Solutions LLC",
        "Sunrise Community Hospital",
        "BluePeak Analytics",
        "Evergreen Retail Group",
        "City Public School District",
    ]

    state = random.choice(states)
    year = random.choice(years)
    filing_status = random.choice(filings)

    taxpayer_occupation = random.choice(taxpayer_occupations)
    spouse_occupation = random.choice(spouse_occupations)
    spouse_employer = random.choice(spouse_employers)

    taxpayer = profile_gen.build_person(
        min_age=30,
        max_age=55,
        occupation=taxpayer_occupation,
        employer=None,
    )

    spouse = profile_gen.build_person(
        min_age=25,
        max_age=50,
        occupation=spouse_occupation,
        employer=spouse_employer,
    )

    dependent_count = random.choice([0, 1, 2, 3])
    dependents: list[Dependent] = []

    for _ in range(dependent_count):
        gender = random.choice(["male", "female"])
        qualifies_credit = random.choice([True, False])

        if gender == "male":
            first_name = profile_gen.fake.first_name_male()
            relationship = Relationship.SON
        else:
            first_name = profile_gen.fake.first_name_female()
            relationship = Relationship.DAUGHTER

        dependents.append(
            Dependent(
                first_name=first_name,
                last_name=taxpayer.last_name,
                ssn=profile_gen.fake_ssn(),
                relationship=relationship,
                qualifies_child_tax_credit=qualifies_credit,
            )
        )

    income_docs = IncomeDocuments(
        w2=income_gen.build_w2(spouse_employer),
        interest_1099_int=income_gen.build_interest(),
        dividend_1099_div=income_gen.build_dividends(),
        schedule_c=income_gen.build_schedule_c(),
    )

    address = profile_gen.build_address(state=state)

    case = TaxCase(
        case_id=case_id,
        tax_year=year,
        taxpayer=taxpayer,
        spouse=spouse,
        address=address,
        filing=FilingInfo(
            federal_status=filing_status,
            state_status=filing_status,
            residency_state=state,
            full_year_resident=True,
        ),
        dependents=dependents,
        income_documents=income_docs,
    )

    case.federal_return = build_federal_return(case)
    case.state_return = build_california_return(case)
    return case