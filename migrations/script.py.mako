   from alembic import op
   import sqlalchemy as sa


   def upgrade():
       op.add_column('user_exercise', sa.Column('day', sa.String(length=50), nullable=True))


   def downgrade():
       op.drop_column('user_exercise', 'day')