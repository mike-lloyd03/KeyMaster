"""empty message

Revision ID: c2580134a462
Revises: 12032516e94b
Create Date: 2021-10-05 21:57:57.757967

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c2580134a462'
down_revision = '12032516e94b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('keys', sa.Column('status', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('keys', 'status')
    # ### end Alembic commands ###