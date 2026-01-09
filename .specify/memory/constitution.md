<!--
Sync Impact Report:
Version Change: Initial → 1.0.0
Added Sections:
  - Core Principles (9 principles)
  - Security & Privacy Requirements (child-safety focused)
  - Development Workflow
  - Governance
Modified Principles: N/A (initial creation)
Templates Status:
  ✅ plan-template.md - Compatible (Constitution Check section)
  ✅ spec-template.md - Compatible (Requirements alignment)
  ✅ tasks-template.md - Compatible (Task categorization matches principles)
Follow-up TODOs: None
-->

# Grade-1 Science Learning Web Application Constitution

## Core Principles

### I. Child-Safety First (NON-NEGOTIABLE)

All features, content, and interactions MUST be designed for children aged 6-7 years.

**Rules:**
- NO external links without parental approval mechanisms
- NO collection of personally identifiable information (PII) beyond necessary session data
- NO advertisements or third-party tracking
- ALL AI-generated content MUST be filtered for age-appropriateness before display
- ALL text MUST use vocabulary appropriate for Grade-1 reading levels (Lexile 190L-530L)
- Content filtering MUST block inappropriate topics, language, and imagery

**Rationale:** Children's safety and age-appropriate learning experiences are the foundational requirement. This principle overrides all other considerations including features, performance, and convenience.

### II. Discovery-First Development

Implementation MUST NOT begin until design artifacts (spec, plan, research) are complete and approved.

**Rules:**
- EVERY feature starts with `/sp.specify` → `/sp.plan` → `/sp.tasks` workflow
- Research phase MUST answer: "What exists? What patterns apply? What are the constraints?"
- Design phase MUST produce: data models, API contracts, quickstart guides
- Implementation phase MUST reference approved design artifacts
- NO speculative coding or "figure it out as we go" approaches

**Rationale:** Prevents rework, ensures architectural consistency, and allows stakeholder review before investment in code. Discovery surfaces risks and dependencies early when they're cheapest to address.

### III. Test-Driven Development for Critical Paths (CONDITIONAL)

Tests MUST be written first for features involving data persistence, AI interactions, or user state.

**Rules:**
- TDD MANDATORY for: database operations, AI/LLM calls, authentication, user progress tracking
- TDD OPTIONAL for: UI components, static content, presentation logic
- Red-Green-Refactor cycle: Write failing test → User approval → Implement → Pass → Refactor
- Tests MUST verify both success and error paths (network failures, API timeouts, invalid inputs)
- Integration tests REQUIRED for AI chatbot interactions (mocked LLM responses)

**Rationale:** Grade-1 users cannot report bugs effectively. Critical functionality must be proven correct before deployment. TDD focuses effort where failures have highest impact.

### IV. Python-First, Library-Driven Architecture

Core logic MUST be implemented as standalone Python libraries independent of web framework.

**Rules:**
- Business logic in `src/lib/` or `backend/src/lib/` as importable modules
- Web framework (Streamlit/FastAPI) is delivery mechanism only, not business logic container
- Libraries MUST have clear single responsibilities: `content_filter.py`, `progress_tracker.py`, `chatbot_service.py`
- Each library MUST be independently testable with mocked dependencies
- NO framework-specific code in library modules (no Streamlit session state, no FastAPI Request objects)

**Rationale:** Enables CLI tooling for content management, supports future deployment targets (mobile app, desktop), simplifies testing, and prevents framework lock-in.

### V. Observability & Child-Friendly Logging

System MUST log all AI interactions and errors for parent/teacher review without exposing technical jargon.

**Rules:**
- EVERY AI chatbot interaction logged: prompt (sanitized), response, timestamp, session ID
- Structured logging in JSON format for parsing: `{"timestamp": "...", "event": "...", "data": {...}}`
- Parent dashboard MUST show: questions asked, topics explored, time spent per session
- Error messages MUST have dual layers: child-friendly ("Oops, something went wrong!") + technical (logged for admins)
- NO sensitive data in logs (passwords, API keys, full conversations without consent)

**Rationale:** Enables parents/teachers to monitor learning, helps developers debug safely, builds trust through transparency, and meets educational accountability requirements.

### VI. Database Schema Versioning & Migration Safety

ALL database changes MUST use versioned migrations with rollback plans.

**Rules:**
- Use migration tool (e.g., Alembic for SQLAlchemy, or Neon's migration features)
- EVERY schema change requires: forward migration + backward migration (rollback)
- Breaking changes MUST go through deprecation cycle: add new column → migrate data → remove old column (3 phases)
- Test migrations on staging environment with production-like data volumes BEFORE production
- Document migration dependencies in plan.md (e.g., "Requires Python 3.11+ for new JSON operators")

**Rationale:** Preserves user progress data during updates, enables zero-downtime deployments, reduces risk of data loss, and supports rapid rollback if issues arise.

### VII. AI Content Filtering Pipeline (MANDATORY)

ALL OpenAI API responses MUST pass through content filter before display to children.

**Rules:**
- Multi-layer filtering: OpenAI moderation API + custom Grade-1 vocabulary validator + blocked-topics list
- Filter MUST reject: profanity, violence, mature themes, complex language (above Grade-2 level)
- Blocked content handling: generic safe response ("Let's talk about something else!") + log for review
- Filter configuration MUST be externalized (YAML/JSON) to allow updates without code changes
- Performance budget: filtering MUST complete within 200ms to avoid disrupting conversation flow

**Rationale:** OpenAI models can produce inappropriate content despite safety training. Defense-in-depth protects children and reduces liability.

### VIII. Offline Resilience & Graceful Degradation

Application MUST function with reduced features when external services (OpenAI, Neon DB) are unavailable.

**Rules:**
- Core content (science facts, images, static lessons) MUST be bundled with application (no external dependencies)
- Chatbot unavailable → display curated Q&A from cache + "AI friend is sleeping, try again soon" message
- Database unavailable → allow read-only mode for content browsing + warn "Progress won't be saved"
- API timeouts MUST be aggressive (5s max) to fail fast and switch to fallback
- Dependency health checks on startup with user-visible status (green/yellow/red indicators)

**Rationale:** Children's learning sessions shouldn't be blocked by infrastructure issues. Graceful degradation maintains engagement and builds trust.

### IX. Performance Budgets for Child Engagement

Interactive elements MUST respond within child attention span limits.

**Rules:**
- Page load: <2 seconds for initial content
- AI response: <5 seconds for chatbot reply (including filtering)
- Database queries: <500ms p95 latency
- Image loading: lazy-load with placeholders, <1 second for hero images
- Animation frame rate: 30+ fps for interactive elements (no janky scrolling)

**Rationale:** Grade-1 children have limited attention spans (5-10 minutes). Slow interfaces cause frustration and disengagement. Performance is a usability requirement.

## Security & Privacy Requirements

**Child Safety Compliance:**
- COPPA compliance: NO personal data collection without verifiable parental consent
- Data minimization: collect ONLY what's necessary (session IDs, progress state, not names/emails)
- Secure storage: ALL data encrypted at rest (Neon database encryption) and in transit (HTTPS/TLS 1.3)
- API key management: OpenAI keys in environment variables (`.env`), NEVER committed to Git
- Rate limiting: prevent abuse via IP-based throttling (max 100 AI requests/hour per session)

**Parent/Teacher Access Control:**
- Admin dashboard MUST require authentication (password + optional 2FA)
- Role-based access: parent (view own child), teacher (view class), admin (view all)
- Audit log: track who viewed which child's data and when

**Third-Party Dependencies:**
- Vetted libraries only (PyPI packages with >1M downloads, active maintenance, security advisories)
- Pin exact versions in `requirements.txt` to prevent supply-chain attacks
- Monthly dependency updates with security patch reviews

## Development Workflow

**Branch Strategy:**
- `master` branch: production-ready code (protected, requires PR + approval)
- Feature branches: `###-feature-name` format (e.g., `001-chatbot-integration`)
- Hotfix branches: `hotfix-###-description` (e.g., `hotfix-001-filter-bypass`)

**Code Review Requirements:**
- ALL code changes require pull request with:
  - Constitution compliance check (which principles apply?)
  - Functionality demonstration (screenshots/video for UI, test output for backend)
  - Security review for AI interactions, data access, authentication changes
- Approval required from: (1) peer developer, (2) project lead for breaking changes

**Deployment Pipeline:**
1. Local testing: run `pytest` + manual smoke tests
2. Staging deployment (Vercel preview): automated on PR creation
3. QA validation: manual testing by parent/teacher representatives
4. Production deployment: merge to `master` triggers Vercel production deploy
5. Post-deployment monitoring: check error logs for 24 hours, rollback if error rate >1%

**Documentation Requirements:**
- User-facing: `docs/parent-guide.md` (how to use dashboard), `docs/teacher-guide.md` (classroom integration)
- Developer-facing: `docs/setup.md` (local development), `docs/architecture.md` (system design)
- ADRs (Architecture Decision Records) for: AI provider choice, database selection, framework selection

## Governance

**Constitution Authority:**
This constitution supersedes all other development practices, coding conventions, and individual preferences. When in conflict, constitution principles win.

**Amendment Process:**
1. Proposal: document WHY amendment needed (new requirement, principle conflict, technical constraint)
2. Impact analysis: which existing features/code affected? What's migration path?
3. Approval: requires consensus from project lead + 1 parent representative + 1 developer
4. Migration: update constitution → update templates → update code → update docs
5. Version bump according to semantic versioning:
   - MAJOR: backward-incompatible principle removals/redefinitions
   - MINOR: new principle additions or material expansions
   - PATCH: clarifications, typo fixes, non-semantic refinements

**Compliance Verification:**
- ALL PRs MUST pass constitution check in plan.md Constitution Check section
- Quarterly constitution review meetings: are principles still relevant? Any violations detected?
- Violation consequences: minor violations (documentation gaps) → fix in follow-up PR; major violations (child safety breaches) → immediate rollback + incident review

**Complexity Justification:**
Any feature violating simplicity principles (e.g., adding 4th project, introducing complex patterns) MUST document in plan.md Complexity Tracking table:
- What principle does it violate?
- Why is added complexity necessary?
- What simpler alternatives were considered and why rejected?

**References:**
- Runtime development guidance: See `CLAUDE.md` for agent-specific workflows
- Template compliance: `.specify/templates/` directory contains plan, spec, tasks templates aligned with these principles
- PHR (Prompt History Records): `history/prompts/` directory tracks all architectural decisions and implementation work

**Version**: 1.0.0 | **Ratified**: 2026-01-10 | **Last Amended**: 2026-01-10
