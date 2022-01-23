import pandas
from pydantic import ValidationError

from const import RECORDED
from logger import logger
from schemas import Candidate


class Base:
    def __init__(self, base_path: str):
        self.base_path = base_path
        self._base = pandas.read_excel(self.base_path)
        if RECORDED not in self._base.columns:
            self._base.insert(len(self._base.columns), RECORDED, int(False))

        self._not_recorded = self._set_not_recorded_in_base()

    def _set_not_recorded_in_base(self) -> list:
        not_recorded_candidates = list()

        not_recorded_rows_indexes = list(self._base.recorded[self._base.recorded == int(False)].index)
        rows = self._base.loc[not_recorded_rows_indexes]

        for row in rows.iterrows():
            position, name, waiting_for_salary, comment, status, recorded = row[1].values
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

            not_recorded_candidates.append(candidate)

        return not_recorded_candidates

    def get_not_recorded(self):
        return self._not_recorded

    def write_candidate(self, index: int):
        self._base.at[index, RECORDED] = int(True)
        self._base.to_excel(self.base_path, index=False)
        return True
