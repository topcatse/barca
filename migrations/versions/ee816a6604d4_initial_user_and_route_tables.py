"""Initial User and Route tables

Revision ID: ee816a6604d4
Revises: 
Create Date: 2019-10-21 00:06:36.149211

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ee816a6604d4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('route',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('start', sa.String(length=100), nullable=False),
    sa.Column('stop', sa.String(length=100), nullable=False),
    sa.Column('date_created', sa.DateTime(), nullable=True),
    sa.Column('date_finished', sa.DateTime(), nullable=True),
    sa.Column('route', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('coords', sa.PickleType(), nullable=True),
    sa.Column('distances', sa.PickleType(), nullable=True),
    sa.Column('prev_coord', sa.PickleType(), nullable=True),
    sa.Column('prev_distance', sa.Integer(), nullable=True),
    sa.Column('current', sa.PickleType(), nullable=True),
    sa.Column('done', sa.Boolean(), nullable=True),
    sa.Column('achieved', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('route')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###
