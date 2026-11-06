"""add courses, course_files and content_chunks

Revision ID: 2fff283568e3
Revises: 9e2e67a881cf
Create Date: 2026-11-03 16:26:20.889360

"""
from typing import Sequence, Union

from alembic import op
import pgvector.sqlalchemy
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2fff283568e3'
down_revision: Union[str, Sequence[str], None] = '9e2e67a881cf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table('courses',
    sa.Column('course_id', sa.UUID(), nullable=False),
    sa.Column('org_id', sa.UUID(), nullable=True),
    sa.Column('teacher_id', sa.UUID(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('subject', sa.String(length=80), nullable=True),
    sa.Column('status', sa.Enum('draft', 'published', name='course_status'), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['org_id'], ['organisations.org_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['teacher_id'], ['users.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('course_id')
    )
    op.create_index(op.f('ix_courses_org_id'), 'courses', ['org_id'], unique=False)
    op.create_index(op.f('ix_courses_teacher_id'), 'courses', ['teacher_id'], unique=False)
    op.create_table('course_files',
    sa.Column('file_id', sa.UUID(), nullable=False),
    sa.Column('course_id', sa.UUID(), nullable=False),
    sa.Column('file_name', sa.String(length=255), nullable=False),
    sa.Column('file_type', sa.String(length=20), nullable=False),
    sa.Column('file_url', sa.Text(), nullable=True),
    sa.Column('status', sa.Enum('uploaded', 'processing', 'ready', 'failed', name='file_status'), nullable=False),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['course_id'], ['courses.course_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('file_id')
    )
    op.create_index(op.f('ix_course_files_course_id'), 'course_files', ['course_id'], unique=False)
    op.create_table('content_chunks',
    sa.Column('chunk_id', sa.UUID(), nullable=False),
    sa.Column('file_id', sa.UUID(), nullable=False),
    sa.Column('chunk_text', sa.Text(), nullable=False),
    sa.Column('source_ref', sa.String(length=20), nullable=True),
    sa.Column('embedding', pgvector.sqlalchemy.vector.VECTOR(dim=384), nullable=True),
    sa.ForeignKeyConstraint(['file_id'], ['course_files.file_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('chunk_id')
    )
    op.create_index('ix_content_chunks_embedding', 'content_chunks', ['embedding'], unique=False, postgresql_using='hnsw', postgresql_ops={'embedding': 'vector_cosine_ops'})
    op.create_index(op.f('ix_content_chunks_file_id'), 'content_chunks', ['file_id'], unique=False)
    op.create_index(op.f('ix_classes_course_id'), 'classes', ['course_id'], unique=False)
    op.create_foreign_key('fk_classes_course_id_courses', 'classes', 'courses', ['course_id'], ['course_id'], ondelete='SET NULL')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_classes_course_id_courses', 'classes', type_='foreignkey')
    op.drop_index(op.f('ix_classes_course_id'), table_name='classes')
    op.drop_index(op.f('ix_content_chunks_file_id'), table_name='content_chunks')
    op.drop_index('ix_content_chunks_embedding', table_name='content_chunks', postgresql_using='hnsw', postgresql_ops={'embedding': 'vector_cosine_ops'})
    op.drop_table('content_chunks')
    op.drop_index(op.f('ix_course_files_course_id'), table_name='course_files')
    op.drop_table('course_files')
    op.drop_index(op.f('ix_courses_teacher_id'), table_name='courses')
    op.drop_index(op.f('ix_courses_org_id'), table_name='courses')
    op.drop_table('courses')
    op.execute("DROP TYPE IF EXISTS file_status")
    op.execute("DROP TYPE IF EXISTS course_status")
