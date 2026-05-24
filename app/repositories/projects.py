from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.db.models import Project
from app.schemas.project import ProjectCreate


class ProjectRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: ProjectCreate) -> Project:
        project = Project(
            name=payload.name,
            brand_name=payload.brand_name,
            domain=payload.domain,
            target_language=payload.target_language,
            target_region=payload.target_region,
            competitors=[item.model_dump() for item in payload.competitors],
            project_metadata=payload.project_metadata,
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def get(self, project_id: int) -> Optional[Project]:
        return self.db.get(Project, project_id)

    def find_by_domain(self, domain: str) -> Optional[Project]:
        return self.db.query(Project).filter(Project.domain == domain).first()

    def list(self, limit: int = 50) -> List[Project]:
        return (
            self.db.query(Project)
            .order_by(Project.created_at.desc())
            .limit(limit)
            .all()
        )
