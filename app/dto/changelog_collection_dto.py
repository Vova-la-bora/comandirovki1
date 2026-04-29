from pydantic import BaseModel
from typing import List
from app.dto.changelog_dto import ChangeLogDTO


class ChangeLogCollectionDTO(BaseModel):
    items: List[ChangeLogDTO]
    total: int
    entity_type: str      # Добавить
    entity_id: int        # Добавить