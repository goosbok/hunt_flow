import asyncio
import os
import unicodedata
import typing as t
import traceback

import aiohttp

import const
from client import client
import schemas
from logger import logger
from validators import (
    base_path_validator,
    token_validator,
)
from base import Base


def get_requisites() -> tuple:
    token = input('Enter access token:\n')
    headers = token_validator(token=token)

    excel_base_path = input('Enter ABSOLUTE path to directory with base in format *.xlsx:\n')
    excel_base_path = base_path_validator(path=excel_base_path)

    return headers, excel_base_path


async def get_account_id(headers: dict) -> int:
    accounts_data = await client.base.get_accounts(headers=headers)
    account_id = accounts_data.json().get('items', [{}]).pop().get('id', None)
    if not account_id:
        raise ValueError('Can`t received account.')

    return account_id


async def get_uses_items(
        candidates: t.List[schemas.Candidate],
        headers: dict,
        account_id: int,
        field: str,
        match_by: str,
        method,
) -> dict:
    statuses_data = await method(headers=headers, account_id=account_id)
    items = statuses_data.json().get('items', [{}])

    candidates_items_names = {
        candidate.dict().get(field)
        for candidate in candidates
    }

    uses_items = {
        item.get(match_by): item.get('id')
        for item in items
        if item.get(match_by) in candidates_items_names
    }

    return uses_items


def get_candidate_create_data(
        candidate: schemas.Candidate,
        candidate_resume: dict,
) -> schemas.CandidateCreate:
    fields = candidate_resume.get('fields', {})
    photo = candidate_resume.get('photo', {})
    name = fields.get('name', {})
    birthdate = fields.get('birthdate', {})
    phones = fields.get('phones', [])
    email = fields.get('email')
    salary = fields.get('salary')
    experience = fields.get('experience', [])
    position = experience[0].get('position') if experience else None
    company = experience[0].get('company') if experience else None
    text = candidate_resume.get('text')
    resume_id = candidate_resume.get('id')
    if not birthdate:
        birthdate = {}
    data = {
        'last_name': name.get('last'),
        'first_name': name.get('first'),
        'middle_name': name.get('middle'),
        'phone': phones.pop() if phones else None,
        'email': email,
        'position': position,
        'company': company,
        'money': str(salary) if salary else candidate.waiting_for_salary,
        'birthday_day': birthdate.get('day'),
        'birthday_month': birthdate.get('month'),
        'birthday_year': birthdate.get('year'),
        'photo': photo.get('id'),
        'externals': [
            {
                'data': {'body': text.replace('"', "'").replace('\xa0', ' ')} if text else None,
                'auth_type': "NATIVE",
                'files': [{'id': resume_id}] if resume_id else None,
                'account_source': None,
            }
        ],
    }
    candidate_create_data = schemas.CandidateCreate(**data)

    return candidate_create_data


def get_vacancy_data(
    candidate: schemas.Candidate,
    uses_statuses: dict,
    uses_vacancies: dict,
    candidate_resume: dict,
) -> schemas.VacancyData:
    files = [{'id': candidate_resume.get('id')}]

    vacancy_data = schemas.VacancyData(
        vacancy=uses_vacancies.get(candidate.position),
        status=uses_statuses.get(candidate.status),
        files=files,
        comment=candidate.comment,
    )

    return vacancy_data


def get_content_type(file_name: str) -> str:
    extend = file_name.split('.')[-1]
    return const.CONTENT_TYPES.get(extend)


async def get_candidate_resume(
        headers: dict,
        account_id: int,
        candidate_resume_path: str,
) -> dict:
    headers = {
        **headers,
        'X-File-Parse': 'true'
    }
    file_name = candidate_resume_path.split('/')[-1]
    content_type = get_content_type(file_name=file_name)
    if not content_type:
        raise ValueError(
            f'Haven`t content type for this resume: {candidate_resume_path}.'
        )

    data = aiohttp.FormData()
    data.add_field(
        'file',
        open(candidate_resume_path, 'rb'),
        filename=candidate_resume_path.split('/')[-1],
        content_type=content_type
    )

    resume_data = await client.upload.upload_resume(
        headers=headers,
        account_id=account_id,
        files=data,
    )

    if resume_data.status not in const.GOOD_STATUSES:
        raise ValueError('Failed to upload resume.')

    resume = resume_data.json()

    return resume


async def push_candidate(
        candidate: schemas.Candidate,
        base: Base,
        uses_statuses: dict,
        uses_vacancies: dict,
        headers: dict,
        account_id: int,
) -> dict:
    data = {
        'row': int,
        'pushed': bool,
        'exception': t.Union[Exception, None],
    }
    candidate_resume = dict()
    try:
        resumes_path = os.path.join(os.path.dirname(base.base_path), candidate.position)
        resumes = os.listdir(resumes_path)

        candidate_resumes = [
            r
            for r in resumes
            if candidate.name in unicodedata.normalize('NFKC', r)
        ]

        if candidate_resumes:
            candidate_resume = candidate_resumes.pop()
            candidate_resume_path = os.path.join(resumes_path, candidate_resume)
            candidate_resume = await get_candidate_resume(
                headers=headers,
                candidate_resume_path=candidate_resume_path,
                account_id=account_id,
            )
        candidate_data = get_candidate_create_data(
            candidate=candidate,
            candidate_resume=candidate_resume,
        )
        vacancy_data = get_vacancy_data(
            uses_statuses=uses_statuses,
            uses_vacancies=uses_vacancies,
            candidate=candidate,
            candidate_resume=candidate_resume,
        )

        candidate_created_date = await client.candidate.create_candidate(
            account_id=account_id,
            headers=headers,
            data=candidate_data.dict(exclude_none=True),
        )

        candidate_id = candidate_created_date.json().get('id')

        candidate_added_data = await client.candidate.add_to_vacancy(
            account_id=account_id,
            applicant_id=candidate_id,
            data=vacancy_data.dict(),
            headers=headers,
        )

        if candidate_added_data.status not in const.GOOD_STATUSES:
            raise ValueError(
                f'The candidate is not added to the vacancy. Detail: {candidate_added_data.json()}'
            )

        base.write_candidate(index=candidate.index_row)

        data['row'] = candidate.index_row
        data['pushed'] = True
        data['exception'] = None

    except Exception:
        data['row'] = candidate.index_row
        data['pushed'] = False
        data['exception'] = traceback.format_exc()

    return data


async def push_data(
        base: Base,
        headers: dict
) -> list:
    candidates = base.get_not_recorded()
    account_id = await get_account_id(headers=headers)

    uses_statuses = await get_uses_items(
        candidates=candidates,
        headers=headers,
        account_id=account_id,
        field='status',
        match_by='name',
        method=client.vacancy.get_statuses
    )
    uses_vacancies = await get_uses_items(
        candidates=candidates,
        headers=headers,
        account_id=account_id,
        field='position',
        match_by='position',
        method=client.vacancy.get_vacancies
    )

    coroutines = list()
    for candidate in candidates:
        coroutine = push_candidate(
            candidate=candidate,
            uses_vacancies=uses_vacancies,
            uses_statuses=uses_statuses,
            base=base,
            headers=headers,
            account_id=account_id,
        )
        coroutines.append(coroutine)

    exceptions = list()
    offset = 0
    its_all = False
    while not its_all and coroutines:
        cap = offset + const.STEP
        if cap >= len(coroutines):
            cap = None
            its_all = True

        candidates = await asyncio.gather(*coroutines[offset: cap])
        exceptions.extend(
            [
                c
                for c in candidates
                if c.get('pushed') is False
            ]
        )

        offset += const.STEP
        percents = int((len(coroutines) - offset) / len(coroutines) * 100)
        if its_all:
            percents = 100
        logger.debug(
            f'Выполнено {percents}%'
        )

    await client.close_session()

    logger.warning(f'Exceptions: {exceptions}')

    return exceptions


def run() -> bool:
    headers, excel_base_path = get_requisites()
    logger.info('Start process')
    base = Base(base_path=excel_base_path)
    exceptions = const.LOOP.run_until_complete(
        push_data(base=base, headers=headers)
    )
    logger.info(f'End process. Status: {not bool(exceptions)}\n')
    return exceptions
