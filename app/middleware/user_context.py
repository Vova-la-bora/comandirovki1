# app/middleware/user_context.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt

from app.core.security import SECRET_KEY, ALGORITHM
from app.core.context import set_current_user_id


class UserContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        user_id = None  # По умолчанию None, НЕ 1!
        
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                user_id = payload.get("id")
            except Exception:
                pass
        
        # Устанавливаем только если есть пользователь
        if user_id:
            set_current_user_id(user_id)
        
        response = await call_next(request)
        return response