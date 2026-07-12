from fastapi import BackgroundTasks
from modules.load_vectorstore import UniversalCodeRAGPipeline
from logger import logger
import os

class RepoIndexService:
    def trigger_sync_index(
        self, 
        owner: str, 
        repo: str, 
        github_token: str, 
        pinecone_key: str | None,
        gemini_key: str | None,
        background_tasks: BackgroundTasks
    ):
        resolved_pinecone = pinecone_key or os.getenv("PINECONE_API_KEY")
        resolved_gemini = gemini_key or os.getenv("GEMINI_API_KEY")

        pipeline = UniversalCodeRAGPipeline(
            github_token=github_token,
            pinecone_index_name="github-ai-index",
            pinecone_api_key=resolved_pinecone,
            gemini_api_key=resolved_gemini
        )

        background_tasks.add_task(self._run_pipeline_worker, pipeline, owner, repo)

    def _run_pipeline_worker(self, pipeline: UniversalCodeRAGPipeline, owner: str, repo: str):
        try:
            for status_update in pipeline.process_repository(owner, repo):
                logger.info(f"[Pipeline Worker]: {status_update}")
        except Exception as e:
            logger.error(f"Background worker failed processing {owner}/{repo}: {str(e)}")
            raise