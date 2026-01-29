-- ==================== ANALYSES TABLE ====================
-- Stores all CSV analysis results

CREATE TABLE IF NOT EXISTS public.analyses (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    health_score DECIMAL(5,2) NOT NULL CHECK (health_score >= 0 AND health_score <= 100),
    total_rows INTEGER NOT NULL,
    total_columns INTEGER NOT NULL,
    issues_high INTEGER DEFAULT 0,
    issues_medium INTEGER DEFAULT 0,
    issues_low INTEGER DEFAULT 0,
    analysis_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==================== INDEXES ====================
-- Speed up queries

CREATE INDEX IF NOT EXISTS idx_analyses_user_id ON public.analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON public.analyses(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analyses_health_score ON public.analyses(health_score);

-- ==================== ROW LEVEL SECURITY (RLS) ====================
-- Users can only see their own analyses

ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view their own analyses
CREATE POLICY "Users can view own analyses" 
    ON public.analyses 
    FOR SELECT 
    USING (auth.uid() = user_id);

-- Policy: Users can insert their own analyses
CREATE POLICY "Users can insert own analyses" 
    ON public.analyses 
    FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

-- Policy: Users can update their own analyses
CREATE POLICY "Users can update own analyses" 
    ON public.analyses 
    FOR UPDATE 
    USING (auth.uid() = user_id);

-- Policy: Users can delete their own analyses
CREATE POLICY "Users can delete own analyses" 
    ON public.analyses 
    FOR DELETE 
    USING (auth.uid() = user_id);

-- ==================== UPDATED_AT TRIGGER ====================
-- Automatically update updated_at timestamp

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_analyses_updated_at 
    BEFORE UPDATE ON public.analyses 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();