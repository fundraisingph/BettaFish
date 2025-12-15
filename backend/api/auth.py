"""
Authentication API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta

from core.database import get_db_connection
from core.exceptions import AuthenticationException, AuthorizationException
from services.auth_service import AuthService
from models.auth import UserLoginRequest, UserRegistrationRequest, UserResponse

router = APIRouter()
security = HTTPBearer()
auth_service = AuthService()


@router.post("/register", response_model=UserResponse)
async def register_user(
    request: UserRegistrationRequest,
    db = Depends(get_db_connection)
):
    """Register a new user"""
    try:
        user = await auth_service.register_user(
            email=request.email,
            password=request.password,
            name=request.name,
            organization=request.organization
        )
        return UserResponse(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            role=user["role"],
            organization=user.get("organization"),
            isActive=user["isActive"],
            createdAt=user["createdAt"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=dict)
async def login_user(
    request: UserLoginRequest,
    db = Depends(get_db_connection)
):
    """Authenticate user and return tokens"""
    try:
        tokens = await auth_service.authenticate_user(
            email=request.email,
            password=request.password,
            remember_me=request.remember_me
        )
        return tokens
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message
        )


@router.post("/refresh", response_model=dict)
async def refresh_token(
    refresh_token: str,
    db = Depends(get_db_connection)
):
    """Refresh access token"""
    try:
        tokens = await auth_service.refresh_token(refresh_token)
        return tokens
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message
        )


@router.post("/logout")
async def logout_user(
    refresh_token: str,
    db = Depends(get_db_connection)
):
    """Logout user and invalidate refresh token"""
    try:
        await auth_service.logout_user(refresh_token)
        return {"message": "Logged out successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = Depends(get_db_connection)
):
    """Get current user information"""
    try:
        user = await auth_service.get_current_user(credentials.credentials)
        return UserResponse(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            role=user["role"],
            organization=user.get("organization"),
            isActive=user["isActive"],
            createdAt=user["createdAt"]
        )
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/bypass-login", response_model=dict)
async def bypass_login(
    request: dict,
    db = Depends(get_db_connection)
):
    """Bypass login for admin access - development only"""
    try:
        # For development purposes, create an admin user if not exists
        admin_email = "admin@bettafish.local"
        admin_password = "admin123"
        
        # Check if admin user exists
        existing_admin = await db.fetchval(
            "SELECT id FROM users WHERE email = $1",
            admin_email
        )
        
        if not existing_admin:
            # Create admin user
            from datetime import datetime
            import bcrypt
            now = datetime.utcnow()
            password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            import uuid
            user_id = str(uuid.uuid4())
            
            await db.execute(
                "INSERT INTO users (id, email, password_hash, name, role, is_active, monthly_quota, created_at, updated_at) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)",
                user_id, admin_email, password_hash, "Admin User", "ADMIN", True, 1000, now, now
            )
        
        # Authenticate as admin user
        tokens = await auth_service.authenticate_user(
            email=admin_email,
            password=admin_password,
            remember_me=True
        )
        
        return tokens
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message
        )


@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = Depends(get_db_connection)
):
    """Change user password"""
    try:
        await auth_service.change_password(
            credentials.credentials,
            old_password,
            new_password
        )
        return {"message": "Password changed successfully"}
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )