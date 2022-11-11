"""Enable millisecond precision in MySQL datetime

Revision ID: 46a278193a94
Revises: 4d3c1b59d011
Create Date: 2022-11-01 23:27:44.620893

"""
from alembic import op
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = "46a278193a94"
down_revision = "4d3c1b59d011"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    url = str(bind.engine.url)
    if url.startswith("mysql"):
        get_columns = "SELECT `TABLE_NAME`, `COLUMN_NAME` FROM `information_schema`.`COLUMNS` WHERE `table_schema`=DATABASE() AND `DATA_TYPE`='datetime' AND `COLUMN_TYPE`='datetime';"
        conn = op.get_bind()
        columns = conn.execute(get_columns).fetchall()
        for table_name, column_name in columns:
            op.alter_column(
                table_name=table_name,
                column_name=column_name,
                type_=mysql.DATETIME(fsp=6),
            )


def downgrade():
    bind = op.get_bind()
    url = str(bind.engine.url)
    if url.startswith("mysql"):
        get_columns = "SELECT `TABLE_NAME`, `COLUMN_NAME` FROM `information_schema`.`COLUMNS` WHERE `table_schema`=DATABASE() AND `DATA_TYPE`='datetime' AND `COLUMN_TYPE`='datetime(6)';"
        conn = op.get_bind()
        columns = conn.execute(get_columns).fetchall()
        for table_name, column_name in columns:
            op.alter_column(
                table_name=table_name,
                column_name=column_name,
                type_=mysql.DATETIME(fsp=0),
            )
