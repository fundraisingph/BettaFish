"""
Authentication service for user management and JWT tokens.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import bcrypt
import jwt
from jose import JWTError
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from core.database import get_db_connection
from core.config import JWT_CONFIG
from core.exceptions import AuthenticationException, AuthorizationException
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"

class AuthService:
    """Authentication service for user management"""
    
    def __init__(self):
        self.db = None
    
    async def _get_db(self):
        """Get database connection lazily"""
        if self.db is None:
            self.db = await get_db_connection()
        return self.db
    
    async def register_user(
        self,
        email: str,
        password: str,
        name: str,
        organization: Optional[str] = None
    ) -> Dict[str, Any]:
        """Register a new user"""
        db = await self._get_db()
        
        # Check if user already exists
        existing_user = await db.fetchrow(
            "SELECT id FROM users WHERE email = $1", email
        )
        
        if existing_user:
            raise AuthenticationException("User with this email already exists")
        
        # Hash password
        password_hash = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
        # Create user
        user = await db.fetchrow(
            """
            INSERT INTO users (email, password_hash, name, organization, role)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id, email, name, role, organization, is_active, created_at
            """,
            email, password_hash, name, organization, UserRole.USER
        )
        
        return {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
            "organization": user["organization"],
            "isActive": user["is_active"],
            "createdAt": user["created_at"]
        }
    
    async def authenticate_user(
        self,
        email: str,
        password: str,
        remember_me: bool = False
    ) -> Dict[str, str]:
        """Authenticate user and return tokens"""
        db = await self._get_db()
        
        # Find user by email
        user = await db.fetchrow(
            "SELECT id, email, password_hash, name, role, organization, is_active, created_at FROM users WHERE email = $1",
            email
        )
        
        if not user:
            raise AuthenticationException("Invalid email or password")
        
        if not user["is_active"]:
            raise AuthenticationException("User account is inactive")
        
        # Verify password
        if not bcrypt.checkpw(
            password.encode('utf-8'),
            user["password_hash"].encode('utf-8')
        ):
            raise AuthenticationException("Invalid email or password")
        
        # Generate tokens
        access_token_expires = timedelta(
            minutes=JWT_CONFIG["access_token_expire_minutes"]
        )
        refresh_token_expires = timedelta(
            days=JWT_CONFIG["refresh_token_expire_days"]
        )
        
        access_token = await self.create_access_token(
            user["id"],
            expires_delta=access_token_expires
        )
        
        refresh_token = await self.create_refresh_token(
            user["id"],
            expires_delta=refresh_token_expires
        )
        
        # Update last login
        await db.execute(
            "UPDATE users SET updated_at = $1 WHERE id = $2",
            datetime.utcnow(), user["id"]
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": JWT_CONFIG["access_token_expire_minutes"] * 60
        }
    
    async def create_access_token_with_key(
        self,
        user_id: str,
        secret_key: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token with custom secret key"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=JWT_CONFIG["access_token_expire_minutes"]
            )
        
        to_encode = {
            "sub": user_id,
            "exp": expire,
            "type": "access"
        }
        
        return jwt.encode(
            to_encode,
            secret_key,
            algorithm=JWT_CONFIG["algorithm"]
        )
    
    async def create_refresh_token_with_key(
        self,
        user_id: str,
        secret_key: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT refresh token with custom secret key"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                days=JWT_CONFIG["refresh_token_expire_days"]
            )
        
        to_encode = {
            "sub": user_id,
            "exp": expire,
            "type": "refresh"
        }
        
        token = jwt.encode(
            to_encode,
            secret_key,
            algorithm=JWT_CONFIG["algorithm"]
        )
        
        # Store refresh token in database
        db = await self._get_db()
        import uuid
        session_id = str(uuid.uuid4())
        await db.execute(
            """
            INSERT INTO sessions (id, user_id, refresh_token, expires_at, is_active, created_at)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            session_id, user_id, token, expire, True, datetime.utcnow()
        )
        
        return token
    
    async def create_access_token(
        self,
        user_id: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=JWT_CONFIG["access_token_expire_minutes"]
            )
        
        to_encode = {
            "sub": user_id,
            "exp": expire,
            "type": "access"
        }
        
        return jwt.encode(
            to_encode,
            JWT_CONFIG["secret_key"],
            algorithm=JWT_CONFIG["algorithm"]
        )
    
    async def create_refresh_token(
        self,
        user_id: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT refresh token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                days=JWT_CONFIG["refresh_token_expire_days"]
            )
        
        to_encode = {
            "sub": user_id,
            "exp": expire,
            "type": "refresh"
        }
        
        token = jwt.encode(
            to_encode,
            JWT_CONFIG["secret_key"],
            algorithm=JWT_CONFIG["algorithm"]
        )
        
        # Store refresh token in database
        db = await self._get_db()
        import uuid
        session_id = str(uuid.uuid4())
        await db.execute(
            """
            INSERT INTO sessions (id, user_id, refresh_token, expires_at, is_active, created_at)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            session_id, user_id, token, expire, True, datetime.utcnow()
        )
        
        return token
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        """Refresh access token using refresh token"""
        db = await self._get_db()
        
        # Validate refresh token
        try:
            payload = jwt.decode(
                refresh_token,
                JWT_CONFIG["secret_key"],
                algorithms=[JWT_CONFIG["algorithm"]]
            )
            
            if payload.get("type") != "refresh":
                raise AuthenticationException("Invalid refresh token")
            
            user_id = payload["sub"]
            
        except JWTError:
            raise AuthenticationException("Invalid refresh token")
        
        # Check if refresh token exists and is active
        session = await db.fetchrow(
            "SELECT id, user_id, expires_at, is_active FROM sessions WHERE refresh_token = $1",
            refresh_token
        )
        
        if not session or not session["is_active"]:
            raise AuthenticationException("Invalid or expired refresh token")
        
        # Check if refresh token is expired
        if session["expires_at"] < datetime.utcnow():
            raise AuthenticationException("Refresh token expired")
        
        # Generate new access token
        access_token = await self.create_access_token(user_id)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": JWT_CONFIG["access_token_expire_minutes"] * 60
        }
    
    async def logout_user(self, refresh_token: str) -> bool:
        """Logout user and invalidate refresh token"""
        db = await self._get_db()
        
        # Find and invalidate refresh token
        session = await db.fetchrow(
            "SELECT id FROM sessions WHERE refresh_token = $1",
            refresh_token
        )
        
        if session:
            await db.execute(
                "UPDATE sessions SET is_active = $1 WHERE id = $2",
                False, session["id"]
            )
            return True
        
        return False
    
    async def get_current_user(self, token: str) -> Dict[str, Any]:
        """Get current user from JWT token"""
        try:
            payload = jwt.decode(
                token,
                JWT_CONFIG["secret_key"],
                algorithms=[JWT_CONFIG["algorithm"]]
            )
            
            if payload.get("type") != "access":
                raise AuthenticationException("Invalid access token")
            
            user_id = payload["sub"]
            
        except JWTError:
            raise AuthenticationException("Invalid token")
        
        # Get user from database
        db = await self._get_db()
        user = await db.fetchrow(
            "SELECT id, email, name, role, organization, is_active, created_at FROM users WHERE id = $1",
            user_id
        )
        
        if not user or not user["is_active"]:
            raise AuthenticationException("User not found or inactive")
        
        return {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
            "organization": user["organization"],
            "isActive": user["is_active"],
            "createdAt": user["created_at"].isoformat() if user["created_at"] else None
        }
    
    async def change_password(
        self,
        token: str,
        old_password: str,
        new_password: str
    ) -> bool:
        """Change user password"""
        db = await self._get_db()
        
        # Get user from token
        user_data = await self.get_current_user(token)
        user = await db.fetchrow(
            "SELECT id, password_hash FROM users WHERE id = $1",
            user_data["id"]
        )
        
        # Verify old password
        if not bcrypt.checkpw(
            old_password.encode('utf-8'),
            user["password_hash"].encode('utf-8')
        ):
            raise AuthenticationException("Invalid current password")
        
        # Hash new password
        new_password_hash = bcrypt.hashpw(
            new_password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
        # Update password
        await db.execute(
            "UPDATE users SET password_hash = $1, updated_at = $2 WHERE id = $3",
            new_password_hash, datetime.utcnow(), user["id"]
        )
        
        return True


# Dependency injection function
async def get_auth_service() -> AuthService:
    """Get auth service instance"""
    return AuthService()


# Helper function for WebSocket authentication
async def get_current_user_ws(token: str) -> Dict[str, Any]:
    """Get current user from JWT token for WebSocket"""
    if not token:
        raise AuthenticationException("No token provided")
    
    auth_service = await get_auth_service()
    return await auth_service.get_current_user(token)


# FastAPI dependency function for authentication
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
) -> Dict[str, Any]:
    """Get current user from JWT token for FastAPI dependencies"""
    if not credentials:
        raise AuthenticationException("No token provided")
    
    auth_service = await get_auth_service()
    return await auth_service.get_current_user(credentials.credentials)