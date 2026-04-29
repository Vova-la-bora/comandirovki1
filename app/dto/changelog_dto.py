# from pydantic import BaseModel
# from datetime import datetime
# from typing import Dict
# from typing import Any


# class ChangeLogDTO(BaseModel):

#     id: int

#     entity_type: str

#     entity_id: int

#     changed_fields: Dict[str, Dict[str, Any]]

#     created_at: datetime

#     created_by: int


# app/dto/changelog_dto.py
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime


class ChangeLogDTO(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    changed_fields: Dict[str, Dict[str, Any]]  # {"field": {"old": x, "new": y}}
    created_at: datetime
    created_by: int

    class Config:
        from_attributes = True