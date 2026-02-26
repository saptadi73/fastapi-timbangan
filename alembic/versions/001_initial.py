"""Create timbangan table

Revision ID: 001_initial
Revises: 
Create Date: 2026-02-25

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create timbangan table
    op.create_table(
        'timbangan',
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('no_urut', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('nopol', sa.String(20), nullable=False),
        sa.Column('sopir', sa.String(100), nullable=False),
        sa.Column('gross', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('rate', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('nett', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('tanggalwaktu', sa.DateTime(), nullable=False),
        sa.Column('petugas', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('catatan', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('uuid')
    )
    
    # Create index untuk no_urut (unique)
    op.create_index('ix_timbangan_no_urut', 'timbangan', ['no_urut'], unique=True)
    
    # Create index untuk nopol (untuk fast query)
    op.create_index('ix_timbangan_nopol', 'timbangan', ['nopol'])
    
    # Create index untuk tanggalwaktu (untuk time range query)
    op.create_index('ix_timbangan_tanggalwaktu', 'timbangan', ['tanggalwaktu'])
    
    # Create index untuk created_at (untuk audit trail)
    op.create_index('ix_timbangan_created_at', 'timbangan', ['created_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_timbangan_created_at', table_name='timbangan')
    op.drop_index('ix_timbangan_tanggalwaktu', table_name='timbangan')
    op.drop_index('ix_timbangan_nopol', table_name='timbangan')
    op.drop_index('ix_timbangan_no_urut', table_name='timbangan')
    
    # Drop table
    op.drop_table('timbangan')
