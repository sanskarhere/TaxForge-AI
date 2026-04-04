from __future__ import annotations

import random

from tax_synth.generators.income_generator import IncomeGenerator
from tax_synth.generators.profile_generator import ProfileGenerator
from tax_synth.models.case import Dependent, FilingInfo, IncomeDocuments, TaxCase
from tax_synth.models.enums import FilingStatus, Relationship
from tax_synth.rules.california_rules import build_california_return
from tax_synth.rules.federal_rules import build_federal_return


def _pick_state(rng: random.Random) -> str:
    # Required states only
    return rng.choice(["CA", "NY", "TX", "FL", "IL"])


def _pick_filing_status(rng: random.Random) -> FilingStatus:
    roll = rng.random()
    if roll < 0.45:
        return FilingStatus.SINGLE
    if roll < 0.75:
        return FilingStatus.MFJ
    return FilingStatus.HOH


def _build_dependents(
    profile_gen: ProfileGenerator,
    rng: random.Random,
    filing_status: FilingStatus,
) -> list[Dependent]:
    dependents: list[Dependent] = []

    if filing_status not in {FilingStatus.MFJ, FilingStatus.HOH}:
        return dependents

    count = rng.randint(1, 2) if rng.random() < 0.7 else 0

    for _ in range(count):
        child = profile_gen.build_person(min_age=3, max_age=16)
        dependents.append(
            Dependent(
                first_name=child.first_name,
                last_name=child.last_name,
                ssn=child.ssn,
                relationship=rng.choice([Relationship.SON, Relationship.DAUGHTER]),
                qualifies_child_tax_credit=True,
            )
        )

    return dependents


def build_one_case(case_id: str, seed: int) -> TaxCase:
    rng = random.Random(seed)
    profile_gen = ProfileGenerator(seed=seed)
    income_gen = IncomeGenerator(seed=seed)

    tax_year = rng.choice([2020, 2021, 2022, 2023, 2024])
    state = _pick_state(rng)
    filing_status = _pick_filing_status(rng)

    taxpayer = profile_gen.build_person(
        min_age=24,
        max_age=58,
        occupation=rng.choice(
            [
                "Software Analyst",
                "Teacher",
                "Nurse",
                "Project Coordinator",
                "Sales Executive",
                "Operations Associate",
            ]
        ),
        employer=rng.choice(
            [
                "Acme Corp",
                "Northwind LLC",
                "BrightPath Systems",
                "Vertex Solutions",
                "BlueWave Inc",
            ]
        ),
    )

    spouse = None
    if filing_status == FilingStatus.MFJ:
        spouse = profile_gen.build_person(
            min_age=24,
            max_age=58,
            occupation=rng.choice(
                [
                    "Teacher",
                    "HR Specialist",
                    "Accountant",
                    "Designer",
                    "Operations Executive",
                ]
            ),
            employer=rng.choice(
                [
                    "Public School District",
                    "Brooks Consulting",
                    "CarePoint Health",
                    "Nexa Services",
                ]
            ),
        )

    address = profile_gen.build_address(state=state)
    dependents = _build_dependents(profile_gen, rng, filing_status)

    w2 = income_gen.build_w2(taxpayer.employer or "Acme Corp")
    interest = income_gen.build_interest()
    dividend = income_gen.build_dividends()
    schedule_c = income_gen.build_schedule_c()

    # No-income-tax states should not carry fake state withholding
    if w2 and state in {"TX", "FL"}:
        w2.state_withholding = 0

    filing = FilingInfo(
        federal_status=filing_status,
        state_status=filing_status,
        residency_state=state,
        full_year_resident=True,
    )

    income_documents = IncomeDocuments(
        w2=w2,
        interest_1099_int=interest,
        dividend_1099_div=dividend,
        schedule_c=schedule_c,
    )

    case = TaxCase(
        case_id=case_id,
        tax_year=tax_year,
        taxpayer=taxpayer,
        spouse=spouse,
        address=address,
        filing=filing,
        dependents=dependents,
        income_documents=income_documents,
    )

    case.federal_return = build_federal_return(case)
    case.state_return = build_california_return(case)

    return case