"""empty message

Revision ID: f1c8ac32509c
Revises: d2d94c048178
Create Date: 2018-09-18 10:14:53.602865

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f1c8ac32509c'
down_revision = 'd2d94c048178'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('actions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('label', sa.String(length=55), nullable=False),
    sa.Column('question_id', sa.Integer(), nullable=True),
    sa.Column('completed', sa.Boolean(), nullable=True),
    sa.Column('completed_on', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('actions')
    # ### end Alembic commands ###
