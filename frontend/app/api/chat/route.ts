import { NextRequest } from "next/server";

export async function POST(req: NextRequest) {
  const { messages } = await req.json();
  const latestMessage = messages?.[messages.length - 1]?.content ?? "";

  const backendResponse = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/ask/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question: latestMessage }),
  });

  if (!backendResponse.ok || !backendResponse.body) {
    return new Response("Backend connection error", { status: 502 });
  }

  return new Response(backendResponse.body, {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "no-cache, no-transform",
    },
  });
}