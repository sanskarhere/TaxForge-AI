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
        # Synthetic only; format match for downstream docs
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

    def build_address(self) -> Address:
        return Address(
            street=self.fake.street_address(),
            city="Sacramento",
            state="CA",
            zip_code=self.fake.postcode(),
            county="Sacramento",
        )