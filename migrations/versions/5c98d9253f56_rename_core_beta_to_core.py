"""Rename core-beta to core

Revision ID: 5c98d9253f56
Revises: 364b4efa1686
Create Date: 2025-08-24 16:23:18.795064

"""
from alembic import op
from sqlalchemy.sql import column, table

from CTFd.models import db


# revision identifiers, used by Alembic.
revision = "5c98d9253f56"
down_revision = "364b4efa1686"
branch_labels = None
depends_on = None

configs_table = table(
    "config", column("id", db.Integer), column("key", db.Text), column("value", db.Text)
)

pages_table = table("pages", column("id", db.Integer), column("content", db.Text))


def upgrade():
    connection = op.get_bind()

    # Define theme transformations: old_theme -> new_theme
    theme_transformations = {
        "core-beta": "core",
        "hacker-beta-theme": "hacker-theme",
        "learning-beta-theme": "learning-theme",
        "learning": "learning-theme",
    }

    # Find the ctf_theme config entry
    theme_config = connection.execute(
        configs_table.select().where(configs_table.c.key == "ctf_theme")
    ).fetchone()

    # Update ctf_theme config
    if (
        theme_config
        and theme_config.value
        and theme_config.value in theme_transformations
    ):
        new_value = theme_transformations[theme_config.value]
        connection.execute(
            configs_table.update()
            .where(configs_table.c.id == theme_config.id)
            .values(value=new_value)
        )

    # Update pages content for all theme transformations
    for old_theme, new_theme in theme_transformations.items():
        old_path = f"themes/{old_theme}/static"
        new_path = f"themes/{new_theme}/static"

        pages_with_old_theme = connection.execute(
            pages_table.select().where(pages_table.c.content.like(f"%{old_path}%"))
        ).fetchall()

        for page in pages_with_old_theme:
            if page.content:
                new_content = page.content.replace(old_path, new_path)
                connection.execute(
                    pages_table.update()
                    .where(pages_table.c.id == page.id)
                    .values(content=new_content)
                )


def downgrade():
    connection = op.get_bind()

    # Define reverse theme transformations: new_theme -> old_theme
    reverse_theme_transformations = {
        "core": "core-beta",
        "hacker-theme": "hacker-beta-theme",
        "learning-theme": "learning-beta-theme",
    }

    # Find the ctf_theme config entry
    theme_config = connection.execute(
        configs_table.select().where(configs_table.c.key == "ctf_theme")
    ).fetchone()

    # Restore ctf_theme config
    if (
        theme_config
        and theme_config.value
        and theme_config.value in reverse_theme_transformations
    ):
        new_value = reverse_theme_transformations[theme_config.value]
        connection.execute(
            configs_table.update()
            .where(configs_table.c.id == theme_config.id)
            .values(value=new_value)
        )

    # Restore pages content for all theme transformations
    for new_theme, old_theme in reverse_theme_transformations.items():
        new_path = f"themes/{new_theme}/static"
        old_path = f"themes/{old_theme}/static"

        pages_with_new_theme = connection.execute(
            pages_table.select().where(pages_table.c.content.like(f"%{new_path}%"))
        ).fetchall()

        for page in pages_with_new_theme:
            if page.content and old_path not in page.content:
                new_content = page.content.replace(new_path, old_path)
                connection.execute(
                    pages_table.update()
                    .where(pages_table.c.id == page.id)
                    .values(content=new_content)
                )
