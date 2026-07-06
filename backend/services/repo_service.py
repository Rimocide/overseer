from fastapi import BackgroundTasks
from modules.load_vectorstore import UniversalCodeRAGPipeline
from logger import logger

class RepoIndexService:
    def trigger_sync_index(self, owner: str, repo: str, github_token: str, background_tasks: BackgroundTasks):
        pipeline = UniversalCodeRAGPipeline(
            github_token=github_token,
            pinecone_index_name="githubAiIndex"
        )

        background_tasks.add_task(self._run_pipeline_worker, pipeline, owner, repo)

    def _run_pipeline_worker(self, pipeline: UniversalCodeRAGPipeline, owner: str, repo: str):
        try: 
            for status_update in pipeline.process_repository(owner, repo):
                logger.info(f"[Pipeline Worker]: {status_update}")
        except Exception as e:
            logger.error(f"Background worker failed processing {owner}/{repo}: {str(e)}")
            raise