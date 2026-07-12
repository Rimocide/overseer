import { NextRequest } from "next/server";

export async function GET() {
  const hasEnv = Boolean(
    process.env.GITHUB_TOKEN &&
    process.env.GEMINI_API_KEY &&
    process.env.PINECONE_API_KEY
  );
  return Response.json({ hasEnv });
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();

    const owner = body.owner || process.env.GITHUB_OWNER;
    const repo = body.repo || process.env.GITHUB_REPO;
    const githubToken = body.githubToken || process.env.GITHUB_TOKEN;
    const geminiKey = body.geminiKey || process.env.GEMINI_API_KEY;
    const pineconeKey = body.pineconeKey || process.env.PINECONE_API_KEY;

    const pydanticPayload = {
      owner: owner,
      repo: repo,
      geminiKey: geminiKey,
      pineconeKey: pineconeKey
    };

    const backendResponse = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/index_repository/`, {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "x-github-token": githubToken || ""
      },
      body: JSON.stringify(pydanticPayload),
    });

    if (!backendResponse.ok) throw new Error("Ingestion pipeline rejected payload");

    return Response.json({ success: true });
  } catch (error) {
    return Response.json({ error: "Ingestion service offline" }, { status: 500 });
  }
}