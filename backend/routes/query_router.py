from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.query_service import CodeQueryService
from logger import logger

router = APIRouter()
query_service = CodeQueryService()

class AskRequest(BaseModel):
    question:str

@router.post('/ask/')
async def ask_question(request: AskRequest):
    try:
        logger.info(f"Received query for code: {request.question}")
        result = query_service.ask_codebase(request.question)

        return result

    except Exception as e:
        logger.error(f"failed to process question: {str(e)}")
        raise HTTPException(status_code=500, detail="internal server error during query processing")
