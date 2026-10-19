from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas import IssueCreate, IssueOut, IssueUpdate, IssueStatus
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Issue

router = APIRouter(prefix="/api/v1/issues", tags=["issues"])


@router.get("/", response_model=list[IssueOut])
def get_issues(session: Session = Depends(get_session)):
    """Retrieve all issues."""
    statement = select(Issue)
    issues = session.scalars(statement).all()
    return issues


@router.get("/{issue_id}", response_model=IssueOut)
def get_issue(issue_id: str, session: Session = Depends(get_session)):
    """Retrieve a specific issue by ID"""
    statement = select(Issue).where(Issue.id == issue_id)
    issue = session.scalars(statement).one_or_none()

    if issue is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found"
        )

    return issue


@router.post("/", response_model=IssueOut, status_code=status.HTTP_201_CREATED)
def create_issue(payload: IssueCreate, session: Session = Depends(get_session)):
    """Create a new issue"""
    issue = Issue(**payload.model_dump())

    session.add(issue)
    session.commit()
    session.refresh(issue)

    return issue


@router.put("/{issue_id}", response_model=IssueOut)
def update_issue(
    issue_id: str, payload: IssueUpdate, session: Session = Depends(get_session)
):
    """Update an existing issue"""
    statement = select(Issue).where(Issue.id == issue_id)
    issue = session.scalars(statement).one_or_none()

    if issue is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found",
        )

    if payload.title is not None:
        issue.title = payload.title
    if payload.description is not None:
        issue.description = payload.description
    if payload.priority is not None:
        issue.priority = payload.priority
    if payload.status is not None:
        issue.status = payload.status

    session.commit()
    session.refresh(issue)

    return issue


@router.delete("/{issue_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_issue(issue_id: str, session: Session = Depends(get_session)):
    """Delete an issue by ID"""
    statement = select(Issue).where(Issue.id == issue_id)
    issue = session.scalars(statement).one_or_none()

    if issue is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found",
        )

    session.delete(issue)
    session.commit()

    return
