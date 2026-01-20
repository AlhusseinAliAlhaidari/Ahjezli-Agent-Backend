# app/core/execution_context.py
from contextvars import ContextVar

current_execution_context: ContextVar[dict] = ContextVar(
    "current_execution_context", default={}
)


