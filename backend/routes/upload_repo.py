from fastapi import APIRouter, BackgroundTasks, status, Header, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from services.repo_service import RepoIndexService
from logger import logger
import os

router = APIRouter()
repo_service = RepoIndexService()

class RepoIndexRequest(BaseModel):
    owner: str | None = None
    repo: str | None = None
    geminiKey: str | None = None
    pineconeKey: str | None = None

@router.post("/index_repository/", status_code=status.HTTP_202_ACCEPTED)
async def index_repository(request: RepoIndexRequest, background_tasks: BackgroundTasks, x_github_token: str = Header(None)):
    try:
        token = x_github_token or os.getenv("GITHUB_TOKEN")
        if not token:
            raise HTTPException(status_code=401, detail="Missing GitHub Authorization Token.")
            
        owner = request.owner or os.getenv("GITHUB_OWNER")
        repo = request.repo or os.getenv("GITHUB_REPO")
            
        if not owner or not repo:
            raise HTTPException(status_code=400, detail="Missing Repository Owner or Name.")

        logger.info(f"Received indexing request for: {owner}/{repo}")

        repo_service.trigger_sync_index(
            owner=owner,
            repo=repo,
            github_token=token,
            pinecone_key=request.pineconeKey,
            gemini_key=request.geminiKey,
            background_tasks=background_tasks
        )

        return {
            "status": "Accepted",
            "message": f"Repository ingestion for {owner}/{repo} initialized"
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception("failed to initialize repository indexing lifecycle")
        return JSONResponse(status_code=500, content={"error": "internal server error"})