from __future__ import annotations

import random
from datetime import date

from faker import Faker

from tax_synth.models.address import Address
from tax_synth.models.person import Person


class ProfileGenerator:
    def __init__(self, seed: int = 42, locale: str = "en_US") -> None:
        self.fake = Faker(locale)
        Faker.seed(seed)
        random.seed(seed)

    def fake_ssn(self) -> str:
        return f"{random.randint(100, 899):03d}-{random.randint(10, 99):02d}-{random.randint(1000, 9999):04d}"

    def build_person(
        self,
        *,
        min_age: int,
        max_age: int,
        occupation: str | None = None,
        employer: str | None = None,
    ) -> Person:
        first_name = self.fake.first_name()
        last_name = self.fake.last_name()
        dob: date = self.fake.date_of_birth(minimum_age=min_age, maximum_age=max_age)

        return Person(
            first_name=first_name,
            last_name=last_name,
            ssn=self.fake_ssn(),
            dob=dob,
            occupation=occupation,
            employer=employer,
        )

    def build_address(self, state: str = "CA") -> Address:
        city_map = {
            "CA": "Sacramento",
            "TX": "Austin",
            "NY": "New York",
            "FL": "Miami",
            "WA": "Seattle",
        }

        county_map = {
            "CA": "Sacramento",
            "TX": "Travis",
            "NY": "New York",
            "FL": "Miami-Dade",
            "WA": "King",
        }

        zip_map = {
            "CA": ["95814", "95821", "95825", "95833"],
            "TX": ["73301", "78701", "78702", "78704"],
            "NY": ["10001", "10011", "11201", "11354"],
            "FL": ["33101", "33130", "33131", "33132"],
            "WA": ["98101", "98104", "98109", "98004"],
        }

        return Address(
            street=self.fake.street_address(),
            city=city_map[state],
            state=state,
            zip_code=random.choice(zip_map[state]),
            county=county_map[state],
        )