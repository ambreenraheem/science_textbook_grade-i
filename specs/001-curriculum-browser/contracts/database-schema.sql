-- ============================================================================
-- Database Schema: Science Curriculum Browser
-- ============================================================================
-- Purpose: PostgreSQL schema for Grade-1 science curriculum content
-- Database: Neon (PostgreSQL 15+)
-- Migration Tool: Alembic
-- Created: 2026-01-10
-- ============================================================================

-- Enable UUID extension (required for uuid_generate_v4())
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- Table: chapters
-- ============================================================================
-- Stores the four main Grade-1 science topics
-- ============================================================================

CREATE TABLE chapters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(100) NOT NULL UNIQUE,
    chapter_number INTEGER NOT NULL UNIQUE,
    description TEXT,
    image_url TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT ck_chapter_number_range CHECK (chapter_number >= 1 AND chapter_number <= 4)
);

-- Indexes for chapters
CREATE INDEX idx_chapters_number ON chapters(chapter_number);

-- Comments for documentation
COMMENT ON TABLE chapters IS 'Main Grade-1 science topics (4 chapters total)';
COMMENT ON COLUMN chapters.chapter_number IS 'Display order (1-4)';
COMMENT ON COLUMN chapters.image_url IS 'Illustration URL for chapter card';

-- ============================================================================
-- Table: lessons
-- ============================================================================
-- Stores individual learning concepts within chapters
-- ============================================================================

CREATE TABLE lessons (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chapter_id UUID NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    lesson_number INTEGER NOT NULL,
    heading VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    image_url TEXT NOT NULL,
    daily_life_examples JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT ck_lesson_number_positive CHECK (lesson_number >= 1),
    CONSTRAINT ck_content_length CHECK (LENGTH(content) <= 500),
    CONSTRAINT uq_chapter_lesson_number UNIQUE (chapter_id, lesson_number)
);

-- Indexes for lessons
CREATE INDEX idx_lessons_chapter_id ON lessons(chapter_id);
CREATE INDEX idx_lessons_number ON lessons(chapter_id, lesson_number);

-- Comments for documentation
COMMENT ON TABLE lessons IS 'Individual learning concepts (one concept per screen)';
COMMENT ON COLUMN lessons.content IS 'Lesson explanation (max 500 chars for 2-4 lines)';
COMMENT ON COLUMN lessons.daily_life_examples IS 'JSON array of 1-2 relatable examples';

-- ============================================================================
-- Table: videos
-- ============================================================================
-- Stores YouTube video references for lessons (1-2 per lesson)
-- ============================================================================

CREATE TABLE videos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lesson_id UUID NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    youtube_video_id VARCHAR(20) NOT NULL UNIQUE,
    thumbnail_url TEXT,
    display_order INTEGER NOT NULL,
    duration_seconds INTEGER,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT ck_video_order_range CHECK (display_order >= 1 AND display_order <= 2),
    CONSTRAINT uq_lesson_video_order UNIQUE (lesson_id, display_order)
);

-- Indexes for videos
CREATE INDEX idx_videos_lesson_id ON videos(lesson_id);
CREATE INDEX idx_videos_order ON videos(lesson_id, display_order);
CREATE INDEX idx_videos_active ON videos(is_active) WHERE is_active = TRUE;

-- Comments for documentation
COMMENT ON TABLE videos IS 'YouTube video references (max 2 per lesson)';
COMMENT ON COLUMN videos.youtube_video_id IS 'YouTube video ID (11 chars, e.g., dQw4w9WgXcQ)';
COMMENT ON COLUMN videos.display_order IS 'Order within lesson (1 = first, 2 = second)';
COMMENT ON COLUMN videos.is_active IS 'Soft delete flag (FALSE hides video without deletion)';

-- ============================================================================
-- Trigger: updated_at auto-update
-- ============================================================================
-- Automatically updates the updated_at timestamp on row modification
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_chapters_updated_at
    BEFORE UPDATE ON chapters
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_lessons_updated_at
    BEFORE UPDATE ON lessons
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_videos_updated_at
    BEFORE UPDATE ON videos
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Sample Data: Chapters
-- ============================================================================

INSERT INTO chapters (title, chapter_number, description, image_url) VALUES
    (
        'Living and Non-Living Things',
        1,
        'Learn about things that are alive and things that are not.',
        'https://placeholder.example.com/chapters/living-nonliving.png'
    ),
    (
        'Plants',
        2,
        'Discover different types of plants and how they grow.',
        'https://placeholder.example.com/chapters/plants.png'
    ),
    (
        'Animals',
        3,
        'Explore the animal kingdom and their habitats.',
        'https://placeholder.example.com/chapters/animals.png'
    ),
    (
        'Food',
        4,
        'Understand where our food comes from and why it is important.',
        'https://placeholder.example.com/chapters/food.png'
    );

-- ============================================================================
-- Sample Data: Lessons (Chapter 1: Living and Non-Living Things)
-- ============================================================================

INSERT INTO lessons (chapter_id, title, lesson_number, heading, content, image_url, daily_life_examples) VALUES
    (
        (SELECT id FROM chapters WHERE chapter_number = 1),
        'What is Living?',
        1,
        'Living Things',
        'Living things can grow, eat, and move. Plants and animals are living. They need water and food to stay alive.',
        'https://placeholder.example.com/lessons/living-things.png',
        '["Your pet dog is living because it eats and plays.", "The tree in your yard grows bigger every year."]'::jsonb
    ),
    (
        (SELECT id FROM chapters WHERE chapter_number = 1),
        'What is Non-Living?',
        2,
        'Non-Living Things',
        'Non-living things do not grow or eat. Rocks, toys, and chairs are non-living. They stay the same size.',
        'https://placeholder.example.com/lessons/nonliving-things.png',
        '["Your toy car does not need food or water.", "A rock does not grow bigger like you do."]'::jsonb
    ),
    (
        (SELECT id FROM chapters WHERE chapter_number = 1),
        'Differences',
        3,
        'How Are They Different?',
        'Living things need food, water, and air. Non-living things do not need these. Look around your room!',
        'https://placeholder.example.com/lessons/differences.png',
        '["Your stuffed animal is non-living, but your pet fish is living.", "The flower on the table is living, but the table is not."]'::jsonb
    );

-- ============================================================================
-- Sample Data: Lessons (Chapter 2: Plants)
-- ============================================================================

INSERT INTO lessons (chapter_id, title, lesson_number, heading, content, image_url, daily_life_examples) VALUES
    (
        (SELECT id FROM chapters WHERE chapter_number = 2),
        'Parts of a Plant',
        1,
        'What Are Plant Parts?',
        'Plants have roots, stems, and leaves. Roots take in water. Stems hold the plant up. Leaves make food.',
        'https://placeholder.example.com/lessons/plant-parts.png',
        '["Look at a flower in your garden. Can you see its stem and leaves?", "Carrots are roots that we eat!"]'::jsonb
    ),
    (
        (SELECT id FROM chapters WHERE chapter_number = 2),
        'How Plants Grow',
        2,
        'Growing Plants',
        'Plants grow from seeds. They need sun, water, and soil. First, a tiny shoot comes out of the seed.',
        'https://placeholder.example.com/lessons/plant-growth.png',
        '["You can plant a bean seed and watch it grow in a cup.", "The plants in your home need water to grow."]'::jsonb
    );

-- ============================================================================
-- Sample Data: Videos (for lessons in Chapter 1)
-- ============================================================================

-- Note: Replace these placeholder YouTube IDs with actual educational video IDs
-- Format: 11-character alphanumeric strings (e.g., "dQw4w9WgXcQ")

INSERT INTO videos (lesson_id, title, youtube_video_id, display_order, duration_seconds) VALUES
    (
        (SELECT id FROM lessons WHERE chapter_id = (SELECT id FROM chapters WHERE chapter_number = 1) AND lesson_number = 1),
        'Living vs Non-Living Things for Kids',
        'PLACEHOLDER1',
        1,
        180
    ),
    (
        (SELECT id FROM lessons WHERE chapter_id = (SELECT id FROM chapters WHERE chapter_number = 1) AND lesson_number = 1),
        'Examples of Living Things',
        'PLACEHOLDER2',
        2,
        120
    ),
    (
        (SELECT id FROM lessons WHERE chapter_id = (SELECT id FROM chapters WHERE chapter_number = 1) AND lesson_number = 2),
        'What Are Non-Living Things?',
        'PLACEHOLDER3',
        1,
        150
    );

-- ============================================================================
-- Performance Validation Queries
-- ============================================================================
-- Use these queries to test performance against constitution budgets
-- ============================================================================

-- Q1: Get all chapters (expected: <50ms)
-- EXPLAIN ANALYZE
SELECT id, title, chapter_number, image_url
FROM chapters
ORDER BY chapter_number;

-- Q2: Get lessons for a chapter (expected: <100ms)
-- EXPLAIN ANALYZE
SELECT id, title, lesson_number, heading, content, image_url, daily_life_examples
FROM lessons
WHERE chapter_id = (SELECT id FROM chapters WHERE chapter_number = 1)
ORDER BY lesson_number;

-- Q3: Get lesson with videos (expected: <150ms)
-- EXPLAIN ANALYZE
SELECT
    l.id AS lesson_id,
    l.title AS lesson_title,
    l.heading,
    l.content,
    l.image_url,
    l.daily_life_examples,
    v.id AS video_id,
    v.title AS video_title,
    v.youtube_video_id,
    v.display_order
FROM lessons l
LEFT JOIN videos v ON v.lesson_id = l.id AND v.is_active = TRUE
WHERE l.id = (SELECT id FROM lessons LIMIT 1)
ORDER BY v.display_order;

-- ============================================================================
-- Cleanup Script (for development/testing)
-- ============================================================================
-- Use this to reset the database during development
-- WARNING: This will delete ALL data
-- ============================================================================

/*
DROP TABLE IF EXISTS videos CASCADE;
DROP TABLE IF EXISTS lessons CASCADE;
DROP TABLE IF EXISTS chapters CASCADE;
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;
DROP EXTENSION IF EXISTS "uuid-ossp";
*/

-- ============================================================================
-- End of Schema
-- ============================================================================
