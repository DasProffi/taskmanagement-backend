from datetime import datetime
from typing import Any, Dict

from sqlalchemy import Column, String, Integer, DateTime


class DBEntity:
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    last_updated_by = Column(String(256), nullable=False, )

    def __init__(self, created_by):
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.last_updated_by = created_by

    @staticmethod
    def delete_attributes_from_dict(entity_dict: Dict[str, Any]) -> Dict[str, Any]:
        del entity_dict['created_at']
        del entity_dict['updated_at']
        del entity_dict['last_updated_by']
        return entity_dict
