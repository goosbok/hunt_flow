import unicodedata
from typing import Optional, List, Dict

import pydantic


class Candidate(pydantic.BaseModel):
    position: str
    name: str
    waiting_for_salary: str
    comment: str
    status: str
    index_row: int

    @pydantic.validator('waiting_for_salary', allow_reuse=True)
    def waiting_for_salary_is_numeric(cls, v):
        if not v.isnumeric():
            v = ''.join(
                [sing for sing in v.strip() if sing.isnumeric()]
            )
        return v

    @pydantic.validator('position', 'name', 'comment', 'status', allow_reuse=True)
    def strip_str_fields(cls, v):
        return v.strip()


class Externals(pydantic.BaseModel):
    data: Optional[Dict[str, str]]
    auth_type: Optional[str]
    files: Optional[List[Dict[str, int]]]
    account_source: Optional[int]


class CandidateCreate(pydantic.BaseModel):
    last_name: str
    first_name: str
    middle_name: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    position: Optional[str]
    company: Optional[str]
    money: Optional[str]
    birthday_day: Optional[int]
    birthday_month: Optional[int]
    birthday_year: Optional[int]
    photo: Optional[int]
    externals: List[Externals]

    @pydantic.validator(
        'last_name', 'first_name', 'middle_name',
        'phone', 'email', 'position', 'company',
        'money',
    )
    def encode_to_utf8(cls, v: str):
        if v:
            return unicodedata.normalize('NFKC', v)

    @pydantic.validator('money')
    def add_currency(cls, v):
        return v + ' руб'


class VacancyData(pydantic.BaseModel):
    vacancy: int
    status: int
    comment: Optional[str]
    files: Optional[List[Dict[str, int]]]
    rejection_reason_id: Optional[int]

    @pydantic.validator('comment')
    def encode_to_utf8(cls, v: str):
        return unicodedata.normalize('NFKC', v)
