from fastapi import APIRouter, BackgroundTasks, status
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
async def index_repository(request: RepoIndexRequest, background_tasks: BackgroundTasks):
    try:
        logger.info(f"Received indexing request for: {request.owner}/{request.repo}")

        github_token="Will Add Logic Later"

        repo_service.trigger_sync_index(
            owner=request.owner,
            repo=request.repo,
            github_token=github_token,
            background_tasks=background_tasks
        )

        return {
            "status": "Accepted",
            "message": f"Repository ingestion for {request.owner}/{request.repo} initialized"
        }
    except Exception as e:
        logger.exception("failed to initialize repository indexing lifecycle")
        return JSONResponse(status_code=500, content={"error": "internal server error"})
    