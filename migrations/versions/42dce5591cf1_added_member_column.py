"""added member column

Revision ID: 42dce5591cf1
Revises: 07d67100fa4b
Create Date: 2020-06-30 21:31:01.506076

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '42dce5591cf1'
down_revision = '07d67100fa4b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('boardusers',
    sa.Column('board_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['board_id'], ['board.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('boardusers')
    # ### end Alembic commands ###
