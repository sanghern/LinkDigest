-- Enable required extensions first
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Drop existing tables if they exist
DROP TABLE IF EXISTS logs CASCADE;
DROP TABLE IF EXISTS bookmarks CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS sessions CASCADE;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false
);

-- Create bookmarks table
CREATE TABLE IF NOT EXISTS bookmarks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    url TEXT NOT NULL,
    content TEXT,
    summary TEXT,
    source_name VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    is_deleted BOOLEAN DEFAULT FALSE,
    tags TEXT[],
    read_count INTEGER DEFAULT 0,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create logs table for system logging
CREATE TABLE IF NOT EXISTS logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    level VARCHAR(10) NOT NULL,
    message TEXT NOT NULL,
    source VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    trace TEXT,
    request_path TEXT,
    request_method VARCHAR(10),
    response_status INTEGER,
    execution_time FLOAT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    meta_data JSONB,
    trace_id UUID DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Create sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active BOOLEAN DEFAULT true,
    user_agent TEXT,
    ip_address VARCHAR(45)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_bookmarks_user_id ON bookmarks(user_id);
CREATE INDEX IF NOT EXISTS idx_bookmarks_created_at ON bookmarks(created_at);
CREATE INDEX IF NOT EXISTS idx_bookmarks_url ON bookmarks(url);
CREATE INDEX IF NOT EXISTS idx_bookmarks_title ON bookmarks(title);
CREATE INDEX IF NOT EXISTS idx_bookmarks_tags ON bookmarks USING gin (tags);
CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_logs_level ON logs(level);
CREATE INDEX IF NOT EXISTS idx_logs_source ON logs(source);
CREATE INDEX IF NOT EXISTS idx_logs_trace_id ON logs(trace_id);
CREATE INDEX IF NOT EXISTS idx_logs_meta_data ON logs USING gin (meta_data);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for bookmarks table
DROP TRIGGER IF EXISTS update_bookmarks_updated_at ON bookmarks;
CREATE TRIGGER update_bookmarks_updated_at
    BEFORE UPDATE ON bookmarks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create views for easy querying
CREATE OR REPLACE VIEW active_bookmarks AS
SELECT 
    b.*,
    u.username as owner_username
FROM bookmarks b
JOIN users u ON b.user_id = u.id
WHERE NOT b.is_deleted;

-- Add comments to tables and columns
COMMENT ON TABLE users IS '사용자 정보를 저장하는 테이블';
COMMENT ON TABLE bookmarks IS '북마크 정보를 저장하는 테이블';
COMMENT ON TABLE logs IS '시스템 로그를 저장하는 테이블';
COMMENT ON TABLE sessions IS '사용자 세션 정보를 저장하는 테이블'; 