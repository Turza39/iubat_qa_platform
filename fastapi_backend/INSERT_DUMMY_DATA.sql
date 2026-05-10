-- ============================================================================
-- IUBAT Q&A Platform - PostgreSQL Dummy Data (100k users, 10k questions)
-- ============================================================================

-- =========================
-- USERS (100,000)
-- =========================
INSERT INTO users (
    username, email, password, verification_status,
    is_active, is_staff, is_superuser,
    date_joined, last_login
)
SELECT
    'user_' || gs,
    'user' || gs || '@iubat.edu.bd',
    '$2b$12$abcdefghijklmnopqrstuvwxyz123456789012345678901234567890',
    CASE
        WHEN gs % 3 = 0 THEN 'verified'
        WHEN gs % 3 = 1 THEN 'pending'
        ELSE 'unverified'
    END,
    TRUE, FALSE, FALSE,
    CURRENT_TIMESTAMP - (gs || ' days')::interval,
    NULL
FROM generate_series(1, 100000) AS gs;


-- =========================
-- QUESTIONS (10,000)
-- =========================
INSERT INTO questions (title, body, author_id, created_at, updated_at)
SELECT
    'Question #' || gs || ': ' ||
    CASE gs % 5
        WHEN 0 THEN 'How to use FastAPI for building APIs?'
        WHEN 1 THEN 'Best practices for Python development'
        WHEN 2 THEN 'How to optimize database queries?'
        WHEN 3 THEN 'React app structure best practices?'
        WHEN 4 THEN 'Authentication in modern web apps?'
    END,
    'This is a dummy question. Question number: ' || gs,
    ((gs - 1) % 100000) + 1,
    CURRENT_TIMESTAMP - (gs || ' days')::interval,
    CURRENT_TIMESTAMP - (gs || ' days')::interval
FROM generate_series(1, 10000) AS gs;


-- =========================
-- TAGS
-- =========================
INSERT INTO tags (name, slug) VALUES
('python', 'python'),
('javascript', 'javascript'),
('fastapi', 'fastapi'),
('react', 'react'),
('database', 'database'),
('api', 'api'),
('authentication', 'authentication'),
('frontend', 'frontend'),
('backend', 'backend'),
('web-development', 'web-development')
ON CONFLICT (slug) DO NOTHING;


-- =========================
-- QUESTION TAGS
-- =========================
INSERT INTO question_tags (question_id, tag_id)
SELECT
    ((gs - 1) % 10000) + 1,
    (gs % 10) + 1
FROM generate_series(1, 10000) AS gs
ON CONFLICT DO NOTHING;


-- =========================
-- ANSWERS (10,000)
-- =========================
INSERT INTO answers (body, question_id, author_id, created_at, updated_at)
SELECT
    'Answer for question #' || ((gs % 10000) + 1),
    (gs % 10000) + 1,
    ((gs + 500) % 100000) + 1,
    CURRENT_TIMESTAMP - (gs || ' days')::interval,
    CURRENT_TIMESTAMP - (gs || ' days')::interval
FROM generate_series(1, 10000) AS gs;


-- =========================
-- VOTES (~50,000)
-- =========================
INSERT INTO votes (user_id, question_id, answer_id, created_at)
SELECT
    ((gs + 200) % 100000) + 1,
    CASE WHEN gs % 2 = 0 THEN (gs % 10000) + 1 ELSE NULL END,
    CASE WHEN gs % 2 = 1 THEN (gs % 10000) + 1 ELSE NULL END,
    CURRENT_TIMESTAMP - ((gs % 500) || ' days')::interval
FROM generate_series(1, 50000) AS gs
ON CONFLICT DO NOTHING;


-- =========================
-- VERIFY COUNTS
-- =========================
SELECT COUNT(*) AS user_count FROM users;
SELECT COUNT(*) AS question_count FROM questions;
SELECT COUNT(*) AS answer_count FROM answers;
SELECT COUNT(*) AS tag_count FROM tags;
SELECT COUNT(*) AS vote_count FROM votes;