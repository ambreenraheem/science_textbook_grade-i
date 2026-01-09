# Research: Science Curriculum Browser

**Phase**: 0 (Outline & Research)
**Date**: 2026-01-10
**Purpose**: Investigate technical approaches, resolve unknowns, and validate technology choices for curriculum browser implementation

## Research Questions

1. **Streamlit vs FastAPI**: Which framework best supports child-friendly UI with rapid development?
2. **YouTube Embedding**: How to embed YouTube videos with child-safety restrictions enabled?
3. **Neon Database Patterns**: Best practices for PostgreSQL connection pooling and query optimization
4. **Grade-1 UX/UI Design**: What design patterns work best for 6-7 year old children?
5. **Performance Optimization**: How to achieve <2s page load with external content (images, videos)?

---

## R1: Streamlit vs FastAPI for Educational Apps

### Decision: **Streamlit 1.30+**

### Rationale:

**Streamlit Advantages:**
- **Built-in Components**: `st.columns()` for chapter cards, `st.image()` for illustrations, `st.button()` for navigation - all with minimal code
- **State Management**: `st.session_state` handles chapter/lesson selection without complex routing
- **Rapid Prototyping**: Declarative Python code generates UI (no HTML/CSS/JS needed for MVP)
- **Child-Friendly Defaults**: Large buttons, clear typography, responsive layouts out-of-the-box
- **Deployment**: One-click Vercel/Streamlit Cloud deployment

**FastAPI Disadvantages for This Feature:**
- Requires separate frontend framework (React/Vue) - increases complexity
- More boilerplate for UI rendering (Jinja templates or API + SPA)
- Better suited for API-heavy applications (not needed for content browsing)

**FastAPI Use Case**: Will be reconsidered for future features requiring RESTful APIs (e.g., parent dashboard, progress tracking)

### Alternatives Considered:

| Framework | Pros | Cons | Verdict |
|-----------|------|------|---------|
| **Streamlit** | Rapid dev, built-in components, Python-only | Limited customization, full page reloads | ✅ **SELECTED** for MVP |
| **FastAPI + React** | Full control, modern SPA | High complexity, separate codebases | ❌ Overkill for browsing |
| **Flask + Jinja** | Lightweight, flexible | Manual UI construction, outdated patterns | ❌ Slower than Streamlit |
| **Django** | Admin panel, ORM included | Heavy framework, long learning curve | ❌ Too complex for MVP |

### Implementation Notes:

- Use Streamlit's multi-page app structure (`src/pages/`) for chapter → lesson navigation
- Customize with `static/styles/child_friendly.css` via `st.markdown()` injection
- Test page load performance with `st.cache_data()` for database queries
- Future migration path: Extract `src/lib/` logic to FastAPI if API endpoints needed

---

## R2: YouTube Embedding with Child-Safety Restrictions

### Decision: **YouTube Embed API with `rel=0&modestbranding=1&disablekb=1` parameters**

### Rationale:

YouTube IFrame Player API allows embedding videos with safety controls:

**Required Parameters:**
- `rel=0`: Disable related videos after playback (prevents inappropriate suggestions)
- `modestbranding=1`: Hide YouTube logo (reduces distractions)
- `disablekb=1`: Disable keyboard controls (prevents accidental navigation)
- `fs=0`: Disable fullscreen (keeps child in app context)
- `iv_load_policy=3`: Hide video annotations

**Embed URL Format:**
```
https://www.youtube-nocookie.com/embed/{VIDEO_ID}?rel=0&modestbranding=1&disablekb=1&fs=0&iv_load_policy=3
```

**Why `youtube-nocookie.com`?**
- Privacy-enhanced mode (COPPA compliance)
- No tracking cookies unless video is played
- Reduces third-party data collection

### Alternatives Considered:

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **YouTube Embed API** | Official, reliable, parameter controls | Can't filter 100% of recommendations | ✅ **SELECTED** |
| **Download + Self-Host** | Full control, no external dependency | Copyright issues, storage costs | ❌ Legal/practical issues |
| **Vimeo** | Better privacy controls | Limited educational content | ❌ Content availability |
| **Direct `<iframe>` embed** | Simple | No safety parameters | ❌ Unsafe for children |

### Implementation Notes:

- Store YouTube video IDs (not full URLs) in database for flexibility
- Generate embed URLs in `src/lib/youtube_embedder.py` with safety parameters
- Use Streamlit's `st.components.v1.iframe()` for embedding
- Fallback message if video fails to load: "Video is resting now! Let's read the lesson together." (spec FR-016)
- Test with restricted YouTube accounts to verify controls work

**Sample Code:**
```python
def get_safe_youtube_embed_url(video_id: str) -> str:
    base_url = "https://www.youtube-nocookie.com/embed/"
    params = "?rel=0&modestbranding=1&disablekb=1&fs=0&iv_load_policy=3"
    return f"{base_url}{video_id}{params}"
```

---

## R3: Neon Database Connection Patterns

### Decision: **SQLAlchemy 2.0 with Connection Pooling**

### Rationale:

**Neon-Specific Considerations:**
- Neon is serverless PostgreSQL (connection pooling managed by Neon)
- Supports standard `postgresql://` connection strings
- Built-in connection pooling (no need for PgBouncer)
- Query performance: <10ms latency for simple SELECTs (per Neon docs)

**SQLAlchemy Advantages:**
- ORM for domain models (`Chapter`, `Lesson`, `Video`)
- Query builder for type-safe queries
- Alembic integration for migrations (Constitution VI)
- Connection pooling via `create_engine(pool_size=5, max_overflow=10)`

**Connection String Format:**
```
postgresql://[user]:[password]@[endpoint]/[database]?sslmode=require
```

### Alternatives Considered:

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **SQLAlchemy ORM** | Type-safe, migration support, connection pooling | Learning curve | ✅ **SELECTED** |
| **psycopg2 (raw SQL)** | Lightweight, fast | Manual query building, no migrations | ❌ No ORM benefits |
| **asyncpg** | Async performance | Requires async/await throughout | ❌ Unnecessary for this scale |

### Implementation Notes:

- Use `sqlalchemy.ext.asyncio` for non-blocking queries (optional, evaluate performance)
- Cache query results with `@st.cache_data(ttl=300)` (5-minute TTL for lesson content)
- Implement retry logic for transient connection errors (Constitution VIII: graceful degradation)
- Monitor query performance with logging (Constitution V: observability)

**Performance Targets:**
- Chapter list query: <50ms (4 chapters, simple SELECT)
- Lesson list query: <100ms (5-8 lessons per chapter with JOINs)
- Lesson detail query: <150ms (lesson + videos + examples)

**Schema Optimization:**
- Index on `chapters.chapter_number` and `lessons.lesson_number` for ordering
- Index on `lessons.chapter_id` for foreign key lookups
- Use `TEXT` for content (flexible length), `JSONB` for daily_life_examples array

---

## R4: Grade-1 UX/UI Design Principles

### Decision: **Child-Centered Design with Large Touch Targets and Visual Hierarchy**

### Rationale:

**Research Sources:**
- "Designing for Kids: Cognitive Considerations" (Nielsen Norman Group)
- "Children's Technology Review" guidelines
- "COPPA Design Principles" (FTC guidelines)

**Key Findings for Ages 6-7:**

1. **Reading Level**:
   - Max 10-12 words per sentence
   - Lexile 190L-530L (short words, simple sentence structure)
   - Large fonts: 18-24pt body text, 28-36pt headings

2. **Touch Targets**:
   - Minimum 44x44 pixels (Apple HIG), 48x48 pixels ideal (Google Material)
   - Children have less precise motor control than adults
   - Spacing between interactive elements: 8-16 pixels minimum

3. **Visual Processing**:
   - One concept per screen (cognitive load management)
   - High contrast: 4.5:1 minimum (WCAG AA standard)
   - Use illustrations over photographs (easier for children to parse)
   - Limit color palette: 4-6 colors maximum (reduces decision paralysis)

4. **Navigation**:
   - Clear "Back" button on every screen (error recovery)
   - Visible progress indicators (e.g., "Lesson 3 of 7")
   - No breadcrumbs (too complex for Grade-1)
   - Use icons + text labels (redundancy helps comprehension)

5. **Feedback**:
   - Immediate visual feedback on interactions (button press animations)
   - Encouraging language ("Great! Let's learn more!")
   - Avoid negative framing ("Wrong!" → "Let's try again!")

### Color Palette (Child-Friendly):

| Color | Hex | Usage |
|-------|-----|-------|
| Sky Blue | `#87CEEB` | Primary (chapter cards, buttons) |
| Grass Green | `#90EE90` | Success states, positive feedback |
| Sunshine Yellow | `#FFD700` | Highlights, interactive elements |
| Soft Pink | `#FFB6C1` | Secondary actions, decorative |
| Warm Orange | `#FFA500` | Alerts (not errors), important info |
| White | `#FFFFFF` | Background, text on dark |
| Dark Gray | `#333333` | Body text (high contrast on white) |

**Contrast Ratios:**
- Dark Gray (#333333) on White (#FFFFFF): 12.6:1 ✅ (exceeds 4.5:1)
- Sky Blue (#87CEEB) on White: Use for backgrounds only, not text

### Implementation Notes:

- Use Streamlit's `st.columns([1, 1, 1, 1])` for chapter card grid (4 columns on desktop, 2 on tablet)
- Custom CSS via `st.markdown()` for button sizes, spacing, fonts
- Test with real Grade-1 students (usability testing per spec SC-009)
- Implement loading skeletons for images/videos (visual feedback during load)

---

## R5: Performance Optimization Strategies

### Decision: **Multi-Layer Caching + Lazy Loading + CDN for Static Assets**

### Rationale:

**Performance Budget Breakdown (2-second page load):**
- Database query: 150ms (lesson + videos + examples)
- HTML rendering: 100ms (Streamlit component generation)
- Image loading: 800ms (lesson illustration, lazy-loaded)
- Video embed loading: 500ms (YouTube iframe, below fold)
- Network overhead: 450ms (DNS, TLS, request/response)
- **Total**: 2000ms ✅

**Optimization Strategies:**

1. **Database Query Caching**:
   - Use `@st.cache_data(ttl=300)` for chapter/lesson queries (content changes infrequently)
   - Cache key: `(chapter_id, lesson_id)` tuple
   - Invalidate cache on content updates (manual trigger or version number)

2. **Lazy Loading Images**:
   - Use `loading="lazy"` attribute for lesson illustrations
   - Load chapter card images eagerly (above fold), lesson images lazily (below fold)
   - Serve images from CDN (Vercel CDN or Cloudflare)
   - Optimize images: WebP format, 800px width max, <200KB file size

3. **YouTube Embed Optimization**:
   - Use `loading="lazy"` for iframes (below fold)
   - Show thumbnail + play button initially, load iframe on click (saves bandwidth)
   - YouTube nocookie domain reduces cookie overhead

4. **Streamlit-Specific Optimizations**:
   - Minimize `st.rerun()` calls (full page reload)
   - Use `st.session_state` to avoid re-fetching data on navigation
   - Enable Streamlit's built-in caching with `@st.cache_resource` for DB connections

5. **Connection Pooling**:
   - SQLAlchemy pool: `pool_size=5, max_overflow=10` (handles 30-100 concurrent users)
   - Neon connection pooling (serverless, auto-scales)
   - Reuse connections across requests (Constitution IX: performance budgets)

### Alternatives Considered:

| Strategy | Pros | Cons | Verdict |
|----------|------|------|---------|
| **Caching + Lazy Loading** | Proven, easy to implement | Requires cache invalidation logic | ✅ **SELECTED** |
| **Static Site Generation** | Fastest possible, no DB queries | Can't handle dynamic content (progress tracking later) | ❌ Not scalable |
| **Redis Caching** | Distributed, fast | Adds infrastructure complexity | ❌ Overkill for MVP |
| **GraphQL** | Fetch only needed data | Requires API layer, learning curve | ❌ Unnecessary |

### Implementation Notes:

- Monitor performance with Streamlit's built-in profiler
- Log query times with structured logging (Constitution V)
- Test with slow network conditions (throttled Chrome DevTools)
- Set up performance monitoring (Vercel Analytics or simple logging)

**Performance Testing Plan:**
1. Measure baseline: fresh page load with empty cache
2. Measure cached: page load with warm cache
3. Test edge cases: slow network (3G), concurrent users (30+)
4. Validate: SC-002 (<2s page load) and SC-007 (graceful degradation)

---

## Summary of Decisions

| Research Area | Decision | Key Rationale |
|---------------|----------|---------------|
| **Framework** | Streamlit 1.30+ | Rapid UI development, built-in components, Python-only |
| **YouTube Embedding** | YouTube Embed API with safety params | Privacy-enhanced mode, disable related videos, COPPA compliant |
| **Database** | SQLAlchemy 2.0 + Neon PostgreSQL | ORM for type safety, Alembic migrations, connection pooling |
| **UX/UI Design** | Child-centered with large touch targets | One concept per screen, 18-24pt fonts, high contrast colors |
| **Performance** | Multi-layer caching + lazy loading | <2s page load via DB caching, lazy images, CDN for static assets |

---

## Next Steps (Phase 1)

Based on research findings, Phase 1 will create:

1. **data-model.md**: SQLAlchemy ORM models for `Chapter`, `Lesson`, `Video` entities
2. **contracts/database-schema.sql**: PostgreSQL schema with indexes, constraints, sample data
3. **quickstart.md**: Step-by-step setup guide (Python env, Neon DB, Streamlit run)

All research questions resolved. Ready to proceed to Phase 1 design artifacts.
