from alembic import op
import sqlalchemy as sa

# Set the revision identifier
revision = 'b7ec098dd868'

down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user_exercise', sa.Column('day', sa.String(length=50), nullable=True))


def downgrade():
    op.drop_column('user_exercise', 'day')