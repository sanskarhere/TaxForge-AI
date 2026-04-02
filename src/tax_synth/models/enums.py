from enum import Enum


class FilingStatus(str, Enum):
    SINGLE = "single"
    MFJ = "married_filing_jointly"
    MFS = "married_filing_separately"
    HOH = "head_of_household"
    QSS = "qualifying_surviving_spouse"


class Relationship(str, Enum):
    SON = "son"
    DAUGHTER = "daughter"
    SPOUSE = "spouse"
    OTHER = "other"