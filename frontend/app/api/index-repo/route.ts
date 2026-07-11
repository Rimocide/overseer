import { NextRequest } from "next/server";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();

    console.log("Next.js received configuration:", body);

    const owner = body.owner;
    const repo = body.repo;
    const githubToken = body.githubToken;
    const geminiKey = body.geminiKey;
    const pineconeKey = body.pineconeKey;

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

