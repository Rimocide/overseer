from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from services.query_service import CodeQueryService
from logger import logger

router = APIRouter()
query_service = CodeQueryService()

class AskRequest(BaseModel):
    question: str

@router.post('/ask/')
async def ask_question(request: AskRequest):
    try:
        logger.info(f"Received query: {request.question}")
        result = query_service.ask_codebase(request.question)

        if isinstance(result, dict):
            answer_text = result.get("response") or result.get("answer")
            if not answer_text:
                logger.error(f"Unexpected result shape: {result}")
                answer_text = "Sorry, I could not generate a response."
        else:
            answer_text = str(result)

        async def generate():
            for char in answer_text:
                yield char

        return StreamingResponse(
            generate(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache, no-transform",
                "X-Accel-Buffering": "no",
            },
        )
    except Exception as e:
        logger.error(f"Pipeline failure: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")