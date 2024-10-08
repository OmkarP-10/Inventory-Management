"""Add cascade delete to foreign keys

Revision ID: 2fe9c42ff6ef
Revises: 0845bf5c6e73
Create Date: 2024-06-12 11:11:16.419326

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '2fe9c42ff6ef'
down_revision = '0845bf5c6e73'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product_movement', schema=None) as batch_op:
        batch_op.alter_column('timestamp',
               existing_type=mysql.DATETIME(),
               nullable=False)
        batch_op.alter_column('from_location',
               existing_type=mysql.VARCHAR(length=50),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('to_location',
               existing_type=mysql.VARCHAR(length=50),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('product_id',
               existing_type=mysql.VARCHAR(length=50),
               type_=sa.Integer(),
               existing_nullable=False)
        batch_op.drop_constraint('product_movement_ibfk_1', type_='foreignkey')
        batch_op.drop_constraint('product_movement_ibfk_3', type_='foreignkey')
        batch_op.drop_constraint('product_movement_ibfk_2', type_='foreignkey')
        batch_op.create_foreign_key(None, 'location', ['from_location'], ['location_id'], ondelete='CASCADE')
        batch_op.create_foreign_key(None, 'product', ['product_id'], ['product_id'], ondelete='CASCADE')
        batch_op.create_foreign_key(None, 'location', ['to_location'], ['location_id'], ondelete='CASCADE')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product_movement', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('product_movement_ibfk_2', 'location', ['to_location'], ['location_id'])
        batch_op.create_foreign_key('product_movement_ibfk_3', 'product', ['product_id'], ['product_id'])
        batch_op.create_foreign_key('product_movement_ibfk_1', 'location', ['from_location'], ['location_id'])
        batch_op.alter_column('product_id',
               existing_type=sa.Integer(),
               type_=mysql.VARCHAR(length=50),
               existing_nullable=False)
        batch_op.alter_column('to_location',
               existing_type=sa.Integer(),
               type_=mysql.VARCHAR(length=50),
               existing_nullable=True)
        batch_op.alter_column('from_location',
               existing_type=sa.Integer(),
               type_=mysql.VARCHAR(length=50),
               existing_nullable=True)
        batch_op.alter_column('timestamp',
               existing_type=mysql.DATETIME(),
               nullable=True)

    # ### end Alembic commands ###

