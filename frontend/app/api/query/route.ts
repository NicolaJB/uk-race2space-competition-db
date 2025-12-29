import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const { query } = await request.json();

    // Call your FastAPI backend
    const res = await fetch('http://127.0.0.1:8000/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });

    const data = await res.json();

    return NextResponse.json(data);
  } catch (err) {
    console.error('Error in API route:', err);
    return NextResponse.json({ results: [] });
  }
}
