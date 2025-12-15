import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8065';

export async function GET(request: NextRequest) {
  try {
    // Forward the request to the FastAPI backend
    const response = await fetch(`${BACKEND_URL}/api/v1/engines/status`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`);
    }

    const data = await response.json();
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching engines data from backend:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to fetch engines data' },
      { status: 500 }
    );
  }
}