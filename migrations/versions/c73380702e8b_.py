"""empty message

Revision ID: c73380702e8b
Revises: a82fba2acba2
Create Date: 2018-09-11 15:29:00.361806

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c73380702e8b'
down_revision = 'a82fba2acba2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('roles', 'label')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('roles', sa.Column('label', sa.VARCHAR(length=255), server_default=sa.text(u"''::character varying"), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
