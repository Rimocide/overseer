<div align="center">

<!-- DEMO GIF PLACEHOLDER: Insert your interactive UI demonstration GIF here -->
<img src="https://readme-typing-svg.demolab.com/?font=Press+Start+2P&size=30&duration=4000&color=22C55E&center=true&vCenter=true&width=1200&height=100&lines=OVERSEER;AST-DRIVEN+CODE+ANALYSIS" alt="Overseer Banner" width="100%" style="border-radius: 12px;" />

# Overseer
### A High-Performance AST-Driven Code RAG & AI Assistant for GitHub Repositories

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js-000000.svg?style=flat&logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![Pinecone](https://img.shields.io/badge/Vector%20DB-Pinecone-000000.svg?style=flat&logo=pinecone&logoColor=white)](https://pinecone.io/)
[![Gemini](https://img.shields.io/badge/LLM-Gemini%202.5%20Flash-4A90E2.svg?style=flat&logo=google&logoColor=white)](https://deepmind.google/technologies/gemini/)

<p align="center">
  <a href="#overview">Overview</a> •
  <a href="#features">Features</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#getting-started">Getting Started</a>
</p>

<img width="640" height="360" alt="output" src="https://github.com/user-attachments/assets/fc10bf47-687e-4227-8e89-640efe7759b5" />

<div align="center"><sub>Here's me generating the readme for this very repo using this project!</sub></div>
</div>

---

## Overview

**Overseer** is a full-stack, intelligence-driven repository analysis engine. Unlike generic RAG models that read code as raw chunks of unstructured text, **Overseer** uses **Abstract Syntax Tree (AST)** parsing via Tree-Sitter to surgically extract modular structural constructs (such as functions, classes, and method declarations) across Python, JavaScript, TypeScript, and Go. 

It generates deterministic contextual embeddings using Google's `gemini-embedding-001`, synthesizes high-level file architecture summaries via `gemini-2.5-flash`, and indexes them within isolated namespaces inside a serverless **Pinecone** database to drive precise, context-aware interactions.

---

## Features

- **AST-Based Semantic Ingestion**: Leverages Tree-sitter parsers (`tspython`, `tsjavascript`, `tstypescript`, `tsgo`) to target specific semantic blocks:
  - `.py` -> Classes and functions.
  - `.js` / `.jsx` -> Class declarations, functions, methods, and arrow functions.
  - `.ts` / `.tsx` -> Functions, methods, and interface/class implementations.
  - `.go` -> Struct declarations, interfaces, methods, and functions.
- **Architectural Summarization**: Automatically processes valid files through `gemini-2.5-flash` to construct concise architectural briefs.
- **Streaming UI**: Modern dark-mode interface styled with Tailwind CSS, leveraging custom markdown renderers, syntax highlighting, streaming message states, and robust error handling.
- **Configurable Vector Namespaces**: Data is partitioned into two optimized Pinecone namespaces:
  - `code-chunks`: Stores micro-level AST functional code blocks.
  - `repo-summaries`: Stores high-level, file-by-file context summaries.
- **Gitignore Compliance**: Uses `pathspec` to read and respect repository `.gitignore` patterns dynamically during repository ingestion.

---

## Architecture

                  [GitHub Tarball API]
                           │
                   (Reads .gitignore)
                           ▼
                [Targeted File Extractor]
                 (Python, JS, TS, Go)
                 /                  \
                /                    \
               ▼                      ▼
      [Tree-sitter Parser]    [Gemini 2.5 Flash]
    (AST Functional Blocks) (Architectural Summaries)
               │                      │
    [Gemini-Embedding-001]  [Gemini-Embedding-001]
               │                      │
               ▼                      ▼
      Pinecone Namespace:    Pinecone Namespace:
         "code-chunks"         "repo-summaries"

---

## Getting Started

### Prerequisites

You will need the following API keys ready. Create a `.env` file in your backend directory to configure them (or set them up directly in the UI if prompted):

- `GEMINI_API_KEY`
- `PINECONE_API_KEY`
- `GITHUB_TOKEN` (Personal Access Token)

### 1. Backend Setup

Fast, deterministic dependency installation is powered by `uv`.

```bash
# Clone the repository
git clone [https://github.com/Rimocide/overseer.git](https://github.com/Rimocide/overseer.git)
cd overseer

# Install backend dependencies via uv pip
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
cd backend
uv pip install -r requirements.txt
```
### 2. Frontend Setup
The frontend is built with Next.js. Ensure you have Node.js installed before running the commands below.

```bash
# From the project root, navigate to the frontend directory
cd frontend

# Install base dependencies
npm install

# Install required UI components and utilities
npm install sonner next

# Start the development server
npm run dev
