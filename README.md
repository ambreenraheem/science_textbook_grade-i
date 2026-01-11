# Grade-1 Science Learning Web Application

A child-safe, interactive science learning platform for 6-7 year old students (Grade-1) featuring engaging curriculum content, multimedia resources, and an AI-powered learning assistant.

## Overview

This application provides an age-appropriate learning experience for young students exploring fundamental science concepts through:

- **Interactive Curriculum Browser**: Four main chapters (Living and Non-Living Things, Plants, Animals, Food)
- **Lesson-Based Learning**: One concept per screen with simple explanations, colorful illustrations, and daily life examples
- **Educational Videos**: Child-safe YouTube videos embedded with restricted mode
- **AI Learning Assistant** (Future): Friendly chatbot to answer questions and provide encouragement

## Features

### Current (Feature 001: Curriculum Browser)
- Browse 4 science chapters with colorful cards
- View lessons with Grade-1 appropriate vocabulary (Lexile 190L-530L)
- Watch 1-2 educational videos per lesson
- Navigate easily with "Next Lesson" and "Back" buttons
- Child-friendly error messages and graceful fallbacks

### Planned
- User authentication with BetterAuth
- AI chatbot learning assistant (OpenAI SDK)
- Parent/teacher dashboard for progress tracking
- Progress tracking and completion status

## Technology Stack

- **Language**: Python 3.11+
- **Framework**: Streamlit 1.30+ (rapid UI development)
- **Database**: Neon (PostgreSQL 15+, managed service)
- **ORM**: SQLAlchemy 2.0 with Alembic migrations
- **Testing**: pytest 7.0+ with coverage
- **Deployment**: Vercel / Streamlit Cloud

## Quick Start

Get the application running locally in ~20 minutes:

**[→ See Quickstart Guide](./specs/001-curriculum-browser/quickstart.md)**

### Prerequisites
- Python 3.11+
- Neon account (free tier)
- Git

### Installation (Quick Version)

```bash
# Clone repository
git clone https://github.com/ambreenraheem/science_textbook_grade-i.git
cd science_textbook_grade-i

# Checkout feature branch
git checkout 001-curriculum-browser

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Neon DATABASE_URL

# Run migrations
alembic upgrade head

# Start application
streamlit run src/app.py
```

Open browser to `http://localhost:8501`

## Project Structure

```
├── src/                      # Application source code
│   ├── lib/                  # Framework-agnostic business logic
│   ├── components/           # Streamlit UI components
│   ├── pages/                # Multi-page Streamlit app
│   └── utils/                # Utilities (database, logging, config)
├── tests/                    # Test suite
│   ├── contract/             # Database contract tests (TDD)
│   ├── integration/          # User journey tests
│   └── unit/                 # Library unit tests
├── database/                 # Database artifacts
│   ├── migrations/           # Alembic migrations
│   └── seeds/                # Sample data
├── static/                   # Static assets
│   ├── images/               # Illustrations and icons
│   └── styles/               # Custom CSS
└── specs/                    # Design documentation
    └── 001-curriculum-browser/
        ├── spec.md           # Feature requirements
        ├── plan.md           # Implementation plan
        ├── tasks.md          # Task breakdown
        └── quickstart.md     # Setup guide
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test suites
pytest tests/contract/         # Database tests
pytest tests/integration/      # User journey tests
pytest tests/unit/             # Library tests

# Run with coverage
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

### Performance Targets

Per constitution requirements:
- Page load: <2 seconds
- Database queries: <500ms p95
- Image loading: <1 second
- Support: 30-100 concurrent users

## Child Safety & Design Principles

This application follows strict child-safety guidelines:

- **Age-Appropriate Content**: Grade-1 vocabulary (Lexile 190L-530L)
- **No External Links**: YouTube embeds only, no external navigation
- **No PII Collection**: COPPA compliant, minimal data collection
- **Child-Friendly UX**: Large touch targets (48x48px), bright soft colors, one concept per screen
- **Graceful Degradation**: Fallback messages when content unavailable

See [Constitution](./specs/memory/constitution.md) for full design principles.

## Documentation

- **[Quickstart Guide](./specs/001-curriculum-browser/quickstart.md)** - Get started in 20 minutes
- **[Feature Specification](./specs/001-curriculum-browser/spec.md)** - User stories and requirements
- **[Implementation Plan](./specs/001-curriculum-browser/plan.md)** - Technical architecture
- **[Task Breakdown](./specs/001-curriculum-browser/tasks.md)** - 58 implementation tasks
- **[Constitution](./specs/memory/constitution.md)** - Design principles and governance

## Contributing

This project follows a Discovery-First development workflow:

1. **Specify**: Create feature specification (`/sp.specify`)
2. **Plan**: Design implementation approach (`/sp.plan`)
3. **Tasks**: Generate task breakdown (`/sp.tasks`)
4. **Implement**: Execute tasks with TDD
5. **Review**: Code review and QA testing
6. **Deploy**: Merge to main and deploy

All database operations require TDD (tests written first).

## License

[Add your license here]

## Contact

- **Repository**: [https://github.com/ambreenraheem/science_textbook_grade-i](https://github.com/ambreenraheem/science_textbook_grade-i)
- **Issues**: Report bugs or request features via GitHub Issues

---

**Built with ❤️ for young learners**
