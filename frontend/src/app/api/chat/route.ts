import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/lib/supabase/server';
import Groq from 'groq-sdk';

const MAX_MESSAGE_LENGTH = 500;

const SYSTEM_PROMPT = `You are Taska AI, a helpful TODO assistant. You help users manage their tasks.
When users want to add, list, complete, or delete tasks, acknowledge their request and provide a helpful response. Be concise and friendly.

Examples of what you can help with:
- Adding new tasks
- Listing existing tasks
- Marking tasks as complete
- Deleting tasks
- Providing task management tips`;

export async function POST(request: NextRequest) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const { message } = await request.json();

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
    const apiKey = process.env.GROQ_API_KEY;
    if (!apiKey) {
      return NextResponse.json(
        { reply: 'AI service is not configured. Please set GROQ_API_KEY.', tool_calls: [] },
        { status: 200 }
      );
    }

    const groq = new Groq({ apiKey });

    const completion = await groq.chat.completions.create({
      model: 'llama-3.1-8b-instant',
      messages: [
        { role: 'system', content: SYSTEM_PROMPT },
        { role: 'user', content: message },
      ],
      temperature: 0.7,
      max_tokens: 1024,
    });

    const reply = completion.choices[0]?.message?.content || "I'm here to help!";

    return NextResponse.json({ reply, tool_calls: [] });
  } catch {
    return NextResponse.json(
      { reply: 'The assistant is currently unavailable. Please try again later.', tool_calls: [] },
      { status: 200 }
    );
  }
}
