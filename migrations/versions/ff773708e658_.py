"""empty message

Revision ID: ff773708e658
Revises: 64b56f2dc11f
Create Date: 2022-08-13 01:53:20.010207

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ff773708e658'
down_revision = '64b56f2dc11f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('areas',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('city', sa.String(), nullable=False),
    sa.Column('state', sa.String(length=2), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('city')
    )
    op.create_table('artist_area',
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.Column('area_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['area_id'], ['areas.id'], ),
    sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], ),
    sa.PrimaryKeyConstraint('artist_id', 'area_id')
    )
    op.create_table('venues_area',
    sa.Column('venue_id', sa.Integer(), nullable=False),
    sa.Column('area_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['area_id'], ['areas.id'], ),
    sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], ),
    sa.PrimaryKeyConstraint('venue_id', 'area_id')
    )
    op.create_unique_constraint(None, 'Artist', ['name'])
    op.drop_column('Artist', 'state')
    op.drop_column('Artist', 'city')
    op.create_unique_constraint(None, 'Venue', ['name'])
    op.drop_column('Venue', 'state')
    op.drop_column('Venue', 'city')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('city', sa.VARCHAR(length=120), autoincrement=False, nullable=False))
    op.add_column('Venue', sa.Column('state', sa.VARCHAR(length=120), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'Venue', type_='unique')
    op.add_column('Artist', sa.Column('city', sa.VARCHAR(length=120), autoincrement=False, nullable=False))
    op.add_column('Artist', sa.Column('state', sa.VARCHAR(length=120), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'Artist', type_='unique')
    op.drop_table('venues_area')
    op.drop_table('artist_area')
    op.drop_table('areas')
    # ### end Alembic commands ###
