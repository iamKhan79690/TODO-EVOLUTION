import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/lib/supabase/server';

const AGENT_URL = process.env.AGENT_URL || 'http://localhost:8001';
const MAX_MESSAGE_LENGTH = 500;

export async function POST(request: NextRequest) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const { message, session_id } = await request.json();

  if (!message || typeof message !== 'string') {
    return NextResponse.json({ error: 'Message is required' }, { status: 400 });
  }

  if (message.length > MAX_MESSAGE_LENGTH) {
    return NextResponse.json(
      { reply: 'Please keep your message under 500 characters.', tool_calls: [] },
      { status: 200 }
    );
  }

  try {
    const response = await fetch(`${AGENT_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        user_id: user.id,
        session_id: session_id || user.id,
      }),
    });

    if (!response.ok) {
      const err = await response.text();
      return NextResponse.json({ error: 'Agent error', details: err }, { status: 502 });
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch {
    return NextResponse.json(
      { reply: 'The assistant is currently unavailable. Please try again later.', tool_calls: [] },
      { status: 200 }
    );
  }
}
