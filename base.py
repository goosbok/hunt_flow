import pandas
from pydantic import ValidationError

from const import WRITE
from logger import logger
from schemas import Candidate


class Base:
    def __init__(self, base_path: str):
        self.base_path = base_path
        self._base = pandas.read_excel(self.base_path)
        if WRITE not in self._base.columns:
            self._base.insert(len(self._base.columns), WRITE, int(False))

        self._not_write = self._get_not_write_in_base()

    def _get_not_write_in_base(self) -> list:
        not_write_candidates = list()

        not_write_rows_indexes = list(self._base.write[self._base.write == int(False)].index)
        rows = self._base.loc[not_write_rows_indexes]

        for row in rows.iterrows():
            position, name, waiting_for_salary, comment, status, write = row[1].values
            try:
                candidate = Candidate(
                    position=position,
                    name=name,
                    waiting_for_salary=waiting_for_salary,
                    comment=comment,
                    status=status,
                    index_row=row[0],
                )
            except ValidationError:
                logger.warning(f'Candidate {name}, string {row[0] + 1} not valid.')
                continue

            not_write_candidates.append(candidate)

        return not_write_candidates

    def get_not_write(self):
        return self._not_write

    def write_candidate(self, index: int):
        self._base.at[index, WRITE] = int(True)
        self._base.to_excel(self.base_path, index=False)
        return True
