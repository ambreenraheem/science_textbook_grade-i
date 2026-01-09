"""Initial schema for Grade-1 Science curriculum

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-01-10

Creates:
- chapters table (4 main science topics)
- lessons table (learning concepts within chapters)
- videos table (YouTube videos for lessons)
- Indexes for performance
- CHECK constraints for data validation
- Triggers for updated_at auto-update
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial database schema."""

    # Enable UUID extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # Create chapters table
    op.create_table(
        'chapters',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('chapter_number', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('image_url', sa.Text(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint('chapter_number >= 1 AND chapter_number <= 4', name='ck_chapter_number_range'),
        sa.UniqueConstraint('title', name='uq_chapters_title'),
        sa.UniqueConstraint('chapter_number', name='uq_chapters_chapter_number')
    )

    # Create index on chapter_number for ordered retrieval
    op.create_index('idx_chapters_number', 'chapters', ['chapter_number'])

    # Create lessons table
    op.create_table(
        'lessons',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('chapter_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('lesson_number', sa.Integer(), nullable=False),
        sa.Column('heading', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('image_url', sa.Text(), nullable=False),
        sa.Column('daily_life_examples', postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['chapter_id'], ['chapters.id'], ondelete='CASCADE'),
        sa.CheckConstraint('lesson_number >= 1', name='ck_lesson_number_positive'),
        sa.CheckConstraint('LENGTH(content) <= 500', name='ck_content_length'),
        sa.UniqueConstraint('chapter_id', 'lesson_number', name='uq_chapter_lesson_number')
    )

    # Create indexes on lessons for performance
    op.create_index('idx_lessons_chapter_id', 'lessons', ['chapter_id'])
    op.create_index('idx_lessons_number', 'lessons', ['chapter_id', 'lesson_number'])

    # Create videos table
    op.create_table(
        'videos',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('lesson_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('youtube_video_id', sa.String(length=20), nullable=False),
        sa.Column('thumbnail_url', sa.Text(), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ondelete='CASCADE'),
        sa.CheckConstraint('display_order >= 1 AND display_order <= 2', name='ck_video_order_range'),
        sa.UniqueConstraint('youtube_video_id', name='uq_videos_youtube_video_id'),
        sa.UniqueConstraint('lesson_id', 'display_order', name='uq_lesson_video_order')
    )

    # Create indexes on videos
    op.create_index('idx_videos_lesson_id', 'videos', ['lesson_id'])
    op.create_index('idx_videos_order', 'videos', ['lesson_id', 'display_order'])
    op.create_index('idx_videos_active', 'videos', ['is_active'], postgresql_where=sa.text('is_active = true'))

    # Create trigger function for updated_at auto-update
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create triggers for each table
    op.execute("""
        CREATE TRIGGER update_chapters_updated_at
            BEFORE UPDATE ON chapters
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    """)

    op.execute("""
        CREATE TRIGGER update_lessons_updated_at
            BEFORE UPDATE ON lessons
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    """)

    op.execute("""
        CREATE TRIGGER update_videos_updated_at
            BEFORE UPDATE ON videos
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    """Drop all tables and extensions (rollback)."""

    # Drop triggers
    op.execute('DROP TRIGGER IF EXISTS update_videos_updated_at ON videos')
    op.execute('DROP TRIGGER IF EXISTS update_lessons_updated_at ON lessons')
    op.execute('DROP TRIGGER IF EXISTS update_chapters_updated_at ON chapters')

    # Drop trigger function
    op.execute('DROP FUNCTION IF EXISTS update_updated_at_column()')

    # Drop indexes
    op.drop_index('idx_videos_active', table_name='videos')
    op.drop_index('idx_videos_order', table_name='videos')
    op.drop_index('idx_videos_lesson_id', table_name='videos')
    op.drop_index('idx_lessons_number', table_name='lessons')
    op.drop_index('idx_lessons_chapter_id', table_name='lessons')
    op.drop_index('idx_chapters_number', table_name='chapters')

    # Drop tables (order matters due to foreign keys)
    op.drop_table('videos')
    op.drop_table('lessons')
    op.drop_table('chapters')

    # Drop UUID extension
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
