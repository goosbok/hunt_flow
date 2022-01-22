import os

import const
from client import client
from const import (
    BASE_HEADERS,
    XLSX_FILE_EXTEND,
    GOOD_STATUSES, LOOP,
)


def token_validator(token: str) -> str:
    headers = BASE_HEADERS
    headers['Authorization'] += token

    response = LOOP.run_until_complete(client.base.get_me(headers=headers))
    if response.status not in GOOD_STATUSES:
        const.LOOP.run_until_complete(client.close_session())
        raise ValueError('Token is not valid.')

    return headers


def base_path_validator(path: str) -> str:
    if not os.path.exists(path=path):
        const.LOOP.run_until_complete(client.close_session())
        raise ValueError('Path not found. Maybe not an absolute path.')
    elif not os.path.isdir(path):
        const.LOOP.run_until_complete(client.close_session())
        raise ValueError('Enter path to DIRECTORY, not file.')

    files_names_in_dir = os.listdir(path=path)
    xlsx_files = [
        file_name
        for file_name in files_names_in_dir
        if file_name[-(len(XLSX_FILE_EXTEND)):] == XLSX_FILE_EXTEND
    ]

    if not xlsx_files:
        const.LOOP.run_until_complete(client.close_session())
        raise ValueError(f'The dir haven`t {XLSX_FILE_EXTEND} files.')
    elif len(xlsx_files) == 1:
        return os.path.join(path, xlsx_files.pop())
    else:
        xlsx_files_names = [f'{i}) {xlsx_files[i]}\n' for i in range(len(xlsx_files))]

        not_received_xlsx_file_index = True

        while not_received_xlsx_file_index:
            xlsx_file_index = input(
                f'Chose one in {XLSX_FILE_EXTEND} files:\n{"".join(xlsx_files_names)}\nEnter file index:\n'
            )
            if not xlsx_file_index.isdigit() or int(xlsx_file_index) >= len(xlsx_files_names):
                print('Enter not valid index.')
                continue

            return os.path.join(
                path,
                xlsx_files.pop(int(xlsx_file_index)),
            )
