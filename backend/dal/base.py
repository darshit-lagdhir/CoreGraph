from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Foundational Declarative Base for the CoreGraph Data Access Layer.
    Ensures all models inherit the centralized metadata registry for the 3.88M node ingestion.
    """

    pass
