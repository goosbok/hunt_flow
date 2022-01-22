import typing as t

import aiohttp

import const


class ApiHttpRequestResponse:
    def __init__(
        self,
        status=100,
        text='',
        json=None,
    ):
        if not json:
            json = {}
        self._status = status
        self._text = text
        self._json = json

    def json(self):
        return self._json

    def text(self):
        return self._text

    @property
    def status(self):
        return self._status


class ApiHttpRequest:
    _session: aiohttp.ClientSession

    def __init__(self):
        self._session = aiohttp.ClientSession()

    async def close_session(self):
        await self._session.close()

    async def get(
            self,
            url: str,
            headers: dict = None,
    ):
        if not headers:
            headers = const.BASE_HEADERS

        async with self._session.get(
            url=url,
            headers=headers,
        ) as response:
            response = ApiHttpRequestResponse(
                status=response.status,
                text=await response.text(),
                json=await response.json(),
            )

            return response

    async def post(
            self,
            url: str,
            data: dict = None,
            json: t.Union[dict, str] = None,
            headers: dict = None,
    ):
        if not headers:
            headers = const.BASE_HEADERS

        async with self._session.post(
                url=url,
                headers=headers,
                json=json,
                data=data,
        ) as response:
            response = ApiHttpRequestResponse(
                status=response.status,
                text=await response.text(),
                json=await response.json(),
            )
            return response


class BaseApi(ApiHttpRequest):
    async def get_me(self, headers=None):
        url = const.BASE_URL + '/me'
        return await self.get(url=url, headers=headers)

    async def get_accounts(self, headers=None):
        url = const.BASE_URL + '/accounts'
        return await self.get(url=url, headers=headers)


class CandidateAPI(ApiHttpRequest):
    async def create_candidate(
            self,
            account_id: int,
            data: dict,
            headers: dict = None
    ):
        url = const.BASE_URL + f'/account/{account_id}/applicants'

        return await self.post(url=url, json=data, headers=headers)

    async def add_to_vacancy(
            self,
            account_id: int,
            applicant_id: int,
            data: dict = None,
            headers: dict = None
    ):
        url = const.BASE_URL + f'/account/{account_id}/applicants/{applicant_id}/vacancy'
        return await self.post(url=url, json=data, headers=headers)


class VacancyApi(ApiHttpRequest):
    async def get_vacancies(self, account_id: int, headers=None):
        url = const.BASE_URL + f'/account/{account_id}/vacancies'
        return await self.get(url=url, headers=headers)

    async def get_statuses(self, account_id: int, headers=None):
        url = const.BASE_URL + f'/account/{account_id}/vacancy/statuses'
        return await self.get(url=url, headers=headers)


class UploadApi(ApiHttpRequest):
    async def upload_resume(self, files: dict, account_id: int, headers=None):
        url = const.BASE_URL + f'/account/{account_id}/upload'
        headers = {
            **headers,
            'X-File-Parse': 'true',
        }

        return await self.post(url=url, headers=headers, data=files)


class Client:
    _candidate: CandidateAPI
    _vacancy: VacancyApi
    _upload: UploadApi
    _base: BaseApi

    def __init__(self):
        self._candidate = CandidateAPI()
        self._vacancy = VacancyApi()
        self._upload = UploadApi()
        self._base = BaseApi()

    async def close_session(self):
        await self._base.close_session()
        await self._upload.close_session()
        await self._vacancy.close_session()
        await self._candidate.close_session()

    @property
    def candidate(self):
        return self._candidate

    @property
    def vacancy(self):
        return self._vacancy

    @property
    def upload(self):
        return self._upload

    @property
    def base(self):
        return self._base


client = Client()
