"""empty message

Revision ID: c62f703cf027
Revises: a3b6c8065a7d
Create Date: 2021-02-23 15:12:22.894862

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c62f703cf027'
down_revision = 'a3b6c8065a7d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artist', sa.Column('website_link', sa.String(length=500), nullable=True))
    op.add_column('venue', sa.Column('website_link', sa.String(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venue', 'website_link')
    op.drop_column('artist', 'website_link')
    # ### end Alembic commands ###