"""
Authentication models for request/response validation.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserRegistrationRequest(BaseModel):
    """User registration request model"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="User password")
    name: str = Field(..., min_length=1, max_length=100, description="User full name")
    organization: Optional[str] = Field(None, max_length=200, description="User organization")


class UserLoginRequest(BaseModel):
    """User login request model"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    remember_me: bool = Field(False, description="Remember login")


class UserResponse(BaseModel):
    """User response model"""
    id: str = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email address")
    name: str = Field(..., description="User full name")
    role: str = Field(..., description="User role")
    organization: Optional[str] = Field(None, description="User organization")
    isActive: bool = Field(..., description="User active status")
    createdAt: str = Field(..., description="User creation timestamp")


class PasswordChangeRequest(BaseModel):
    """Password change request model"""
    old_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")


class TokenRefreshRequest(BaseModel):
    """Token refresh request model"""
    refresh_token: str = Field(..., description="Refresh token")


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(..., description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")


class ApiKeyCreateRequest(BaseModel):
    """API key creation request model"""
    name: str = Field(..., min_length=1, max_length=100, description="API key name")
    expires_days: int = Field(30, ge=1, le=365, description="Expiration in days")


class ApiKeyResponse(BaseModel):
    """API key response model"""
    id: str = Field(..., description="API key ID")
    name: str = Field(..., description="API key name")
    key: str = Field(..., description="API key value")
    expiresAt: str = Field(..., description="API key expiration timestamp")
    createdAt: str = Field(..., description="API key creation timestamp")