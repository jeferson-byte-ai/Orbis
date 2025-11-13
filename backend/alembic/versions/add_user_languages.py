"""Add speaks_languages and understands_languages to users

Revision ID: add_user_languages
Revises: 
Create Date: 2025-10-31

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_user_languages'
down_revision = None  # Update this to your latest migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new language columns to users table
    op.add_column('users', sa.Column('speaks_languages', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('users', sa.Column('understands_languages', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    
    # Set default values for existing users
    op.execute("UPDATE users SET speaks_languages = '[\"en\"]'::json WHERE speaks_languages IS NULL")
    op.execute("UPDATE users SET understands_languages = '[\"en\"]'::json WHERE understands_languages IS NULL")


def downgrade() -> None:
    # Remove language columns
    op.drop_column('users', 'understands_languages')
    op.drop_column('users', 'speaks_languages')
