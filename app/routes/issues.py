import uuid
from fastapi import APIRouter, HTTPException, status
from app.schemas import IssueCreate, IssueOut, IssueUpdate, IssueStatus
from app.storage import load_data, save_data

router = APIRouter(prefix="/api/v1/issues", tags=["issues"])


@router.get("/", response_model= list[IssueOut])
async def get_issues():
    """Retrieve all issues"""
    issues = load_data()
    return issues

@router.get("/{issue_id}", response_model= IssueOut)
async def get_issue(issue_id: str):
    """Retrieve a specific issue by ID"""
    issues = load_data()
    for i in issues:
        if i["id"] == issue_id:
            return i
    raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Issue not found")

@router.post("/", response_model= IssueOut, status_code= status.HTTP_201_CREATED)
def create_issue(payload: IssueCreate):
    """Create a new issue"""
    issues = load_data()
    new_issue = {
        "id": str(uuid.uuid4()),
        "title": payload.title,
        "description": payload.description,
        "priority": payload.priority,
        "status": IssueStatus.open
    }
    issues.append(new_issue)
    save_data(issues)
    return new_issue

@router.put("/{issue_id}", response_model= IssueOut)
def update_issue(issue_id: str, payload: IssueUpdate):
    """Update an existing issue"""
    issues = load_data()
    for i in issues:
        if i["id"] == issue_id:
            if payload.title is not None:
                i["title"] = payload.title
            if payload.description is not None:
                i["description"] = payload.description
            if payload.priority is not None:
                i["priority"] = payload.priority
            if payload.status is not None:
                i["status"] = payload.status
            save_data(issues)
            return i
    raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Issue not found")

@router.delete("/{issue_id}", status_code= status.HTTP_204_NO_CONTENT)
def delete_issue(issue_id: str):
    """Delete an issue by ID"""
    issues = load_data()
    for i in issues:
        if i["id"] == issue_id:
            issues.remove(i)
            save_data(issues)
            return
    raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Issue not found")