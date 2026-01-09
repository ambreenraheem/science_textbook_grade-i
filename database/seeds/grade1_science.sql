-- ============================================================================
-- Seed Data: Grade-1 Science Curriculum
-- ============================================================================
-- Sample data for development and testing
-- Includes: 4 chapters, 5+ lessons, 3+ videos
-- ============================================================================

-- ============================================================================
-- Chapters (4 main topics)
-- ============================================================================

INSERT INTO chapters (title, chapter_number, description, image_url) VALUES
    (
        'Living and Non-Living Things',
        1,
        'Learn about things that are alive and things that are not.',
        'https://via.placeholder.com/400x300/87CEEB/333333?text=Living+%26+Non-Living'
    ),
    (
        'Plants',
        2,
        'Discover different types of plants and how they grow.',
        'https://via.placeholder.com/400x300/90EE90/333333?text=Plants'
    ),
    (
        'Animals',
        3,
        'Explore the animal kingdom and their habitats.',
        'https://via.placeholder.com/400x300/FFB6C1/333333?text=Animals'
    ),
    (
        'Food',
        4,
        'Understand where our food comes from and why it is important.',
        'https://via.placeholder.com/400x300/FFD700/333333?text=Food'
    );

-- ============================================================================
-- Lessons for Chapter 1: Living and Non-Living Things
-- ============================================================================

INSERT INTO lessons (chapter_id, title, lesson_number, heading, content, image_url, daily_life_examples)
SELECT
    id as chapter_id,
    'What is Living?',
    1,
    'Living Things',
    'Living things can grow, eat, and move. Plants and animals are living. They need water and food to stay alive.',
    'https://via.placeholder.com/600x400/87CEEB/333333?text=Living+Things',
    '["Your pet dog is living because it eats and plays.", "The tree in your yard grows bigger every year."]'::jsonb
FROM chapters WHERE chapter_number = 1;

INSERT INTO lessons (chapter_id, title, lesson_number, heading, content, image_url, daily_life_examples)
SELECT
    id as chapter_id,
    'What is Non-Living?',
    2,
    'Non-Living Things',
    'Non-living things do not grow or eat. Rocks, toys, and chairs are non-living. They stay the same size.',
    'https://via.placeholder.com/600x400/87CEEB/333333?text=Non-Living+Things',
    '["Your toy car does not need food or water.", "A rock does not grow bigger like you do."]'::jsonb
FROM chapters WHERE chapter_number = 1;

INSERT INTO lessons (chapter_id, title, lesson_number, heading, content, image_url, daily_life_examples)
SELECT
    id as chapter_id,
    'How Are They Different?',
    3,
    'Living vs Non-Living',
    'Living things need food, water, and air. Non-living things do not need these. Look around your room!',
    'https://via.placeholder.com/600x400/87CEEB/333333?text=Differences',
    '["Your stuffed animal is non-living, but your pet fish is living.", "The flower on the table is living, but the table is not."]'::jsonb
FROM chapters WHERE chapter_number = 1;

-- ============================================================================
-- Lessons for Chapter 2: Plants
-- ============================================================================

INSERT INTO lessons (chapter_id, title, lesson_number, heading, content, image_url, daily_life_examples)
SELECT
    id as chapter_id,
    'Parts of a Plant',
    1,
    'What Are Plant Parts?',
    'Plants have roots, stems, and leaves. Roots take in water. Stems hold the plant up. Leaves make food.',
    'https://via.placeholder.com/600x400/90EE90/333333?text=Plant+Parts',
    '["Look at a flower in your garden. Can you see its stem and leaves?", "Carrots are roots that we eat!"]'::jsonb
FROM chapters WHERE chapter_number = 2;

INSERT INTO lessons (chapter_id, title, lesson_number, heading, content, image_url, daily_life_examples)
SELECT
    id as chapter_id,
    'How Plants Grow',
    2,
    'Growing Plants',
    'Plants grow from seeds. They need sun, water, and soil. First, a tiny shoot comes out of the seed.',
    'https://via.placeholder.com/600x400/90EE90/333333?text=Plant+Growth',
    '["You can plant a bean seed and watch it grow in a cup.", "The plants in your home need water to grow."]'::jsonb
FROM chapters WHERE chapter_number = 2;

-- ============================================================================
-- Lessons for Chapter 3: Animals
-- ============================================================================

INSERT INTO lessons (chapter_id, title, lesson_number, heading, content, image_url, daily_life_examples)
SELECT
    id as chapter_id,
    'What Are Animals?',
    1,
    'Animals All Around',
    'Animals are living things that can move and eat. Some animals have fur, some have feathers, and some have scales.',
    'https://via.placeholder.com/600x400/FFB6C1/333333?text=Animals',
    '["Your dog has fur and can run fast.", "Birds have feathers and can fly in the sky."]'::jsonb
FROM chapters WHERE chapter_number = 3;

-- ============================================================================
-- Videos for Lessons
-- ============================================================================
-- Note: Replace these with actual educational YouTube video IDs

-- Videos for "What is Living?" lesson
INSERT INTO videos (lesson_id, title, youtube_video_id, display_order, duration_seconds)
SELECT
    l.id as lesson_id,
    'Living Things for Kids',
    'ABC1234WXYZ',  -- Replace with real YouTube ID
    1,
    180
FROM lessons l
JOIN chapters c ON l.chapter_id = c.id
WHERE c.chapter_number = 1 AND l.lesson_number = 1;

INSERT INTO videos (lesson_id, title, youtube_video_id, display_order, duration_seconds)
SELECT
    l.id as lesson_id,
    'Examples of Living Things',
    'DEF5678UVWX',  -- Replace with real YouTube ID
    2,
    120
FROM lessons l
JOIN chapters c ON l.chapter_id = c.id
WHERE c.chapter_number = 1 AND l.lesson_number = 1;

-- Videos for "What is Non-Living?" lesson
INSERT INTO videos (lesson_id, title, youtube_video_id, display_order, duration_seconds)
SELECT
    l.id as lesson_id,
    'Non-Living Things Explained',
    'GHI9012STUV',  -- Replace with real YouTube ID
    1,
    150
FROM lessons l
JOIN chapters c ON l.chapter_id = c.id
WHERE c.chapter_number = 1 AND l.lesson_number = 2;

-- Video for "Parts of a Plant" lesson
INSERT INTO videos (lesson_id, title, youtube_video_id, display_order, duration_seconds)
SELECT
    l.id as lesson_id,
    'Plant Parts for Children',
    'JKL3456PQRS',  -- Replace with real YouTube ID
    1,
    200
FROM lessons l
JOIN chapters c ON l.chapter_id = c.id
WHERE c.chapter_number = 2 AND l.lesson_number = 1;

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Verify chapters
-- SELECT chapter_number, title FROM chapters ORDER BY chapter_number;

-- Verify lessons count per chapter
-- SELECT c.title, COUNT(l.id) as lesson_count
-- FROM chapters c
-- LEFT JOIN lessons l ON c.id = l.chapter_id
-- GROUP BY c.id, c.title
-- ORDER BY c.chapter_number;

-- Verify videos count per lesson
-- SELECT c.title as chapter, l.title as lesson, COUNT(v.id) as video_count
-- FROM chapters c
-- JOIN lessons l ON c.id = l.chapter_id
-- LEFT JOIN videos v ON l.id = v.lesson_id
-- GROUP BY c.id, c.title, l.id, l.title
-- ORDER BY c.chapter_number, l.lesson_number;

-- ============================================================================
-- End of Seed Data
-- ============================================================================
