# Quickstart Guide: Science Curriculum Browser

**Feature**: Science Curriculum Browser
**Branch**: `001-curriculum-browser`
**Last Updated**: 2026-01-10

## Purpose

This guide helps developers set up a local development environment and run the Science Curriculum Browser feature. Follow these steps to get from zero to a working Grade-1 science learning application.

---

## Prerequisites

Before starting, ensure you have:

- **Python 3.11+** installed ([python.org](https://python.org))
- **Git** installed ([git-scm.com](https://git-scm.com))
- **Neon Account** (free tier available at [neon.tech](https://neon.tech))
- **Code Editor** (VS Code, PyCharm, or similar)
- **Web Browser** (Chrome, Firefox, Safari, or Edge)

**Time to Complete**: ~20 minutes

---

## Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/ambreenraheem/science_textbook_grade-i.git

# Navigate to the project directory
cd science_textbook_grade-i

# Checkout the feature branch
git checkout 001-curriculum-browser
```

---

## Step 2: Set Up Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# On Windows (Command Prompt):
.\venv\Scripts\activate.bat

# On macOS/Linux:
source venv/bin/activate

# Verify Python version (should be 3.11+)
python --version
```

---

## Step 3: Install Dependencies

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

**Expected Dependencies**:
- `streamlit >= 1.30.0` - Web UI framework
- `sqlalchemy >= 2.0.0` - Database ORM
- `psycopg2-binary >= 2.9.0` - PostgreSQL driver
- `python-dotenv >= 1.0.0` - Environment variable loader
- `alembic >= 1.13.0` - Database migration tool
- `pytest >= 7.0.0` - Testing framework
- `pillow >= 10.0.0` - Image processing

---

## Step 4: Set Up Neon Database

### 4.1: Create Neon Project

1. Go to [neon.tech](https://neon.tech) and sign up (free tier)
2. Click **"New Project"**
3. Choose:
   - **Name**: `science-textbook-grade1`
   - **Region**: Closest to your location
   - **PostgreSQL Version**: 15 or 16
4. Click **"Create Project"**

### 4.2: Get Connection String

1. In your Neon dashboard, click **"Connection Details"**
2. Copy the connection string (looks like this):
   ```
   postgresql://user:password@ep-example-123.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
3. Save this for the next step

### 4.3: Initialize Database Schema

```bash
# Navigate to database directory
cd database

# Run the schema creation script
# (You'll need psql CLI or use Neon SQL Editor in the dashboard)

# Option 1: Using psql CLI
psql "YOUR_NEON_CONNECTION_STRING" -f migrations/versions/001_initial_schema.sql

# Option 2: Using Neon SQL Editor (web)
# - Go to Neon dashboard → "SQL Editor"
# - Copy contents of contracts/database-schema.sql
# - Paste and click "Run"
```

**Verify**: You should see tables created: `chapters`, `lessons`, `videos`

---

## Step 5: Configure Environment Variables

```bash
# Navigate back to project root
cd ..

# Create .env file (copy from template)
cp .env.example .env

# Open .env in your editor and fill in:
```

**`.env` File Contents**:
```env
# Neon Database Connection
DATABASE_URL=postgresql://user:password@ep-example-123.us-east-2.aws.neon.tech/neondb?sslmode=require

# Application Settings
APP_ENV=development
LOG_LEVEL=INFO

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ENABLE_CORS=false

# Feature Flags (future use)
ENABLE_ANALYTICS=false
```

**Important**: Never commit `.env` to Git! It's already in `.gitignore`.

---

## Step 6: Run Database Migrations (Alembic)

```bash
# Initialize Alembic (first time only)
alembic init database/migrations

# Apply migrations to create tables
alembic upgrade head

# Verify migration
alembic current
```

**Expected Output**: `001_initial_schema (head)`

---

## Step 7: Seed Sample Data (Optional but Recommended)

```bash
# Run seed script
psql "YOUR_NEON_CONNECTION_STRING" -f database/seeds/grade1_science.sql

# Or use Neon SQL Editor to run the sample data inserts
```

**What This Does**:
- Inserts 4 chapters (Living/Non-Living, Plants, Animals, Food)
- Adds 5 sample lessons with content
- Includes 3 placeholder videos (you'll need to update with real YouTube IDs)

---

## Step 8: Run the Application

```bash
# Start Streamlit server
streamlit run src/app.py

# You should see output like:
#   You can now view your Streamlit app in your browser.
#   Local URL: http://localhost:8501
```

**Open in Browser**: Navigate to `http://localhost:8501`

---

## Step 9: Verify the Application

### 9.1: Chapter Selection Screen

- **Expected**: 4 colorful chapter cards displayed
- **Test**: Click on "Living and Non-Living Things"

### 9.2: Lesson List Screen

- **Expected**: List of lessons for the selected chapter
- **Test**: Click on "What is Living?"

### 9.3: Lesson Viewer Screen

- **Expected**:
  - Lesson heading at top
  - 2-4 lines of explanation
  - Colorful illustration
  - 1-2 daily life examples
  - 1-2 embedded YouTube videos (if sample data loaded)
  - "Next Lesson" button
  - "Back" button

### 9.4: Performance Check

- **Test**: Measure page load time (should be <2 seconds)
- **Tool**: Chrome DevTools → Network tab → Reload page
- **Target**: Total load time under 2000ms (per constitution)

---

## Step 10: Run Tests (Optional)

```bash
# Run all tests
pytest

# Run specific test suites
pytest tests/contract/         # Database contract tests
pytest tests/integration/      # User journey tests
pytest tests/unit/             # Library unit tests

# Run with coverage report
pytest --cov=src --cov-report=html

# View coverage
open htmlcov/index.html  # macOS/Linux
start htmlcov/index.html # Windows
```

**Expected**: All tests pass (green) with >80% code coverage

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'streamlit'"

**Solution**:
```bash
# Ensure virtual environment is activated
# On Windows:
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

---

### Issue: "Could not connect to database"

**Solution**:
1. Verify `.env` file has correct `DATABASE_URL`
2. Check Neon project is active (not suspended)
3. Test connection:
   ```bash
   psql "YOUR_NEON_CONNECTION_STRING"
   ```
4. If connection fails, regenerate connection string in Neon dashboard

---

### Issue: "No chapters displayed"

**Solution**:
```bash
# Verify data exists in database
psql "YOUR_NEON_CONNECTION_STRING" -c "SELECT * FROM chapters;"

# If empty, run seed script
psql "YOUR_NEON_CONNECTION_STRING" -f database/seeds/grade1_science.sql
```

---

### Issue: "YouTube videos not showing"

**Solution**:
1. Check `videos` table has valid YouTube IDs:
   ```sql
   SELECT title, youtube_video_id FROM videos;
   ```
2. Replace placeholder IDs with real YouTube video IDs:
   ```sql
   UPDATE videos SET youtube_video_id = 'REAL_VIDEO_ID' WHERE youtube_video_id = 'PLACEHOLDER1';
   ```
3. Ensure video IDs are 11 characters (e.g., `dQw4w9WgXcQ`)

---

### Issue: "Page load is slow (>2 seconds)"

**Solution**:
1. Check database query performance:
   ```sql
   EXPLAIN ANALYZE SELECT * FROM chapters;
   ```
2. Verify indexes exist:
   ```sql
   SELECT * FROM pg_indexes WHERE tablename IN ('chapters', 'lessons', 'videos');
   ```
3. Enable Streamlit caching in `src/lib/content_loader.py`:
   ```python
   @st.cache_data(ttl=300)
   def get_all_chapters():
       # ...
   ```

---

## Next Steps

Once the application is running successfully:

1. **Replace Placeholder Data**:
   - Update chapter images with real illustrations
   - Add more lessons for each chapter (aim for 5-8 per chapter)
   - Replace placeholder YouTube IDs with curated educational videos

2. **Customize UI**:
   - Edit `static/styles/child_friendly.css` for custom colors
   - Update fonts in Streamlit components
   - Add loading animations

3. **Run Tests**:
   - Write contract tests for database queries (TDD per constitution)
   - Create integration tests for user journeys
   - Test on tablets (9+ inch screens)

4. **Deploy to Staging**:
   - Push branch to GitHub
   - Connect Vercel to repository
   - Deploy to preview URL for QA testing

5. **Move to Next Feature**:
   - After curriculum browser is complete, proceed to user authentication (`/sp.specify` for auth feature)

---

## Useful Commands Reference

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
.\venv\Scripts\Activate.ps1  # Windows

# Run application
streamlit run src/app.py

# Run tests
pytest
pytest tests/contract/  # TDD for database
pytest --cov=src        # With coverage

# Database migrations
alembic revision -m "description"  # Create migration
alembic upgrade head               # Apply migrations
alembic downgrade -1               # Rollback one migration

# Database queries (via psql)
psql "$DATABASE_URL" -c "SELECT * FROM chapters;"
psql "$DATABASE_URL" -f database/seeds/grade1_science.sql

# Code formatting (if using)
black src/
isort src/
```

---

## Support

- **Documentation**: See `/specs/001-curriculum-browser/` directory
- **Issues**: Report bugs on GitHub repository
- **Questions**: Check constitution for development principles (`.specify/memory/constitution.md`)

---

**Congratulations!** 🎉 You now have a working Grade-1 Science Curriculum Browser running locally. Happy coding!
