"""Added unique id generator

Revision ID: c09ec300e436
Revises: c247870a29ea
Create Date: 2024-11-20 01:09:11.164978

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c09ec300e436'
down_revision = 'c247870a29ea'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('id',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=16),
               existing_nullable=False)
        batch_op.create_unique_constraint(None, ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.alter_column('id',
               existing_type=sa.String(length=16),
               type_=sa.INTEGER(),
               existing_nullable=False)

    # ### end Alembic commands ###
