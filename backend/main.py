from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from middlewares.exception_handlers import catch_exception_middleware
from routes.upload_repo import router as upload_router
from routes.query_router import router as query_router

app=FastAPI(title="Github AI Assistant API", description="API for RAG on Github Repos")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=["*"],
    allow_methods=["*"],
   allow_headers=["*"]
)

app.middleware("http")(catch_exception_middleware)

app.include_router(upload_router)
app.include_router(query_router)
