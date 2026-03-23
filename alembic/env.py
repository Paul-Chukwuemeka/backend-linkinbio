from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from lib.database import Base, get_database_url
import models.CollectionModel  # noqa: F401
import models.LinkModel  # noqa: F401
import models.cardModel  # noqa: F401
import models.userModel  # noqa: F401


def get_alembic_database_url() -> str:
    return get_database_url().replace("%", "%%")


config = context.config
config.set_main_option("sqlalchemy.url", get_alembic_database_url())

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_required_main_option(name: str) -> str:
    value = config.get_main_option(name)
    if value is None:
        raise RuntimeError(f"Alembic option '{name}' is not set")
    return value


def run_migrations_offline() -> None:
    url = get_required_main_option("sqlalchemy.url")
    render_as_batch = url.startswith("sqlite")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        render_as_batch=render_as_batch,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        render_as_batch = connection.dialect.name == "sqlite"
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            render_as_batch=render_as_batch,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
