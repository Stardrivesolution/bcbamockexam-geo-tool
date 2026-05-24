from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.projects import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectRead

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectRead)
async def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
) -> ProjectRead:
    repo = ProjectRepository(db)
    if payload.domain and repo.find_by_domain(payload.domain):
        raise HTTPException(status_code=409, detail="A project with this domain already exists")
    return repo.create(payload)


@router.get("", response_model=list[ProjectRead])
async def list_projects(
    limit: int = 50,
    db: Session = Depends(get_db),
) -> list[ProjectRead]:
    return ProjectRepository(db).list(limit=min(limit, 100))


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db),
) -> ProjectRead:
    project = ProjectRepository(db).get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
