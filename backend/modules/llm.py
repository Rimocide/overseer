from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts.chat import HumanMessagePromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()

system_instruction_string = """You are an expert software engineering assistant. Your task is to answer the user's questions about a codebase by analyzing the provided repository files.

Here is the context from the repository:
<codebase_context>
{context}
</codebase_context>

Strict Guidelines:
1. Ground your answers deeply in the provided code files. Refer to specific filenames, class names, functions, or variables where applicable.
2. If the provided context does not contain enough information to answer the question, state clearly: "I cannot find the answer based on the provided repository files." Do not make up or assume functionality.
3. If writing code examples or fixes, follow the patterns, style, and programming languages found in the codebase.
4. Keep explanations technically accurate and concise."""

human_query_string= "Question about the codebase: {question}"

GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY")

def get_llm_chain():
    llm=ChatGoogleGenerativeAI(
        api_key=GOOGLE_API_KEY,
        model="gemini-3.5-flash"
    )

    chat_prompt_template=ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_instruction_string),
        HumanMessagePromptTemplate.from_template(human_query_string)

    ])

    output_parser = StrOutputParser()

    chain = chat_prompt_template | llm | output_parser

    return chain
