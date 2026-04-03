from infra.database import db_manager

# Legacy compatibility mapping for CoreGraph Modules 1-9
engine = db_manager.engine
AsyncSessionLocal = db_manager.session_factory
