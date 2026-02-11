import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    status: "ok",
    service: "todo-frontend",
    timestamp: new Date().toISOString(),
  });
}
