from fastapi import APIRouter, BackgroundTasks, status, Header, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from services.repo_service import RepoIndexService
from logger import logger

router = APIRouter()
repo_service = RepoIndexService()

class RepoIndexRequest(BaseModel):
    owner: str
    repo: str

@router.post("/index_repository/", status_code=status.HTTP_202_ACCEPTED)
async def index_repository(request: RepoIndexRequest, background_tasks: BackgroundTasks, x_github_token: str = Header(None)):
    try:
        if not x_github_token:
            raise HTTPException(status_code=401, detail="Missing GitHub Authorization Token.")
        logger.info(f"Received indexing request for: {request.owner}/{request.repo}")

        repo_service.trigger_sync_index(
            owner=request.owner,
            repo=request.repo,
            github_token=x_github_token,
            background_tasks=background_tasks
        )

        return {
            "status": "Accepted",
            "message": f"Repository ingestion for {request.owner}/{request.repo} initialized"
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception("failed to initialize repository indexing lifecycle")
        return JSONResponse(status_code=500, content={"error": "internal server error"})
    