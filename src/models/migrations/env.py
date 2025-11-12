from alembic import context
from sqlalchemy import engine_from_config, pool
from ..base import Base

config = context.config
target_metadata = Base.metadata