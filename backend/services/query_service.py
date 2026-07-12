import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from modules.llm import get_llm_chain
from logger import logger

def _format_docs(docs):
    logged_sources = [doc.metadata.get("path", "unknown_file") for doc in docs]
    logger.info(f"chunks successfully retrieved from: {logged_sources}")
    return "\n\n".join(doc.page_content for doc in docs)

class CodeQueryService:
    def __init__(self):
        self.index_name="github-ai-index"
        self.embeddings=GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", output_dimensionality=768)

    def ask_codebase(self, question: str) -> dict:
        try:
            logger.debug(f"Building Rag pipeline for {question}")

            vectorstore = PineconeVectorStore.from_existing_index(
                index_name=self.index_name,
                namespace="code-chunks",
                embedding=self.embeddings
            )
            retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
            base_llm_chain = get_llm_chain()

            rag_chain = (
                        {"context": retriever | _format_docs, "question": RunnablePassthrough()}
                        | base_llm_chain
                        )

            ai_response = rag_chain.invoke(question)

            return {
                    "response": ai_response
                    }

        except Exception as e:
            logger.exception("query execution failed in service layer")
            raise
