import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const filePath = searchParams.get('filePath');

  if (!filePath) {
    return NextResponse.json({ error: 'filePath is required' }, { status: 400 });
  }

  try {
    const fullPath = path.join(process.cwd(), 'public', 'app', filePath);
    const fileContents = fs.readFileSync(fullPath, 'utf8');
    return NextResponse.json({ content: fileContents }, { status: 200 });
  } catch {
    return NextResponse.json({ error: 'Failed to read the file' }, { status: 500 });
  }
}
