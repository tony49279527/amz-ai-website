-- Create the blog_posts table
CREATE TABLE blog_posts (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
  published_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
  title TEXT NOT NULL,
  slug TEXT NOT NULL UNIQUE,
  summary TEXT,
  content TEXT, -- HTML content
  cover_image TEXT,
  author TEXT DEFAULT 'Amz AI Agent',
  tags TEXT[], -- Array of strings
  source_url TEXT,
  status TEXT DEFAULT 'published' CHECK (status IN ('draft', 'published', 'archived'))
);

-- Enable Row Level Security (RLS)
ALTER TABLE blog_posts ENABLE ROW LEVEL SECURITY;

-- Create Policy: Everyone can read published posts
CREATE POLICY "Allow public read access" ON blog_posts
  FOR SELECT USING (status = 'published');

-- Create Policy: Service role (AI Bot) can insert
-- Note: Service role bypasses RLS by default so this might be optional depending on config
-- but good practice if using authenticated user.
CREATE POLICY "Allow service role insert" ON blog_posts
  FOR INSERT WITH CHECK (true);
