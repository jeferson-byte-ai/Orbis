"""
OAuth Service - Google and GitHub authentication
"""
import httpx
from typing import Dict, Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.config import settings
from backend.db.models import User, OAuthProvider
from backend.core.security import create_access_token, create_refresh_token


class OAuthService:
    """Handle OAuth authentication flows"""
    
    # OAuth provider configurations
    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
    GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
    GITHUB_USER_INFO_URL = "https://api.github.com/user"
    GITHUB_EMAIL_URL = "https://api.github.com/user/emails"
    
    async def get_google_auth_url(self, redirect_uri: str, state: str) -> str:
        """Generate Google OAuth authorization URL"""
        if not settings.google_client_id:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Google OAuth is not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env"
            )
        
        params = {
            "client_id": settings.google_client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "consent"
        }
        
        query_string = "&".join([f"{key}={value}" for key, value in params.items()])
        return f"{self.GOOGLE_AUTH_URL}?{query_string}"
    
    async def get_github_auth_url(self, redirect_uri: str, state: str) -> str:
        """Generate GitHub OAuth authorization URL"""
        if not settings.github_client_id:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="GitHub OAuth is not configured. Please set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET in .env"
            )
        
        params = {
            "client_id": settings.github_client_id,
            "redirect_uri": redirect_uri,
            "state": state,
            "scope": "user:email"
        }
        
        query_string = "&".join([f"{key}={value}" for key, value in params.items()])
        return f"{self.GITHUB_AUTH_URL}?{query_string}"
    
    async def exchange_google_code(self, code: str, redirect_uri: str) -> Dict:
        """Exchange Google authorization code for access token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.GOOGLE_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code"
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange Google code for token"
                )
            
            return response.json()
    
    async def exchange_github_code(self, code: str, redirect_uri: str) -> Dict:
        """Exchange GitHub authorization code for access token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.GITHUB_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": settings.github_client_id,
                    "client_secret": settings.github_client_secret,
                    "redirect_uri": redirect_uri
                },
                headers={"Accept": "application/json"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange GitHub code for token"
                )
            
            return response.json()
    
    async def get_google_user_info(self, access_token: str) -> Dict:
        """Get user info from Google"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.GOOGLE_USER_INFO_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get Google user info"
                )
            
            return response.json()
    
    async def get_github_user_info(self, access_token: str) -> Dict:
        """Get user info from GitHub"""
        async with httpx.AsyncClient() as client:
            # Get user profile
            user_response = await client.get(
                self.GITHUB_USER_INFO_URL,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json"
                }
            )
            
            if user_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get GitHub user info"
                )
            
            user_data = user_response.json()
            
            # Get user emails
            email_response = await client.get(
                self.GITHUB_EMAIL_URL,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json"
                }
            )
            
            if email_response.status_code == 200:
                emails = email_response.json()
                # Find primary verified email
                primary_email = next(
                    (email for email in emails if email.get("primary") and email.get("verified")),
                    None
                )
                if primary_email:
                    user_data["email"] = primary_email["email"]
            
            return user_data
    
    async def authenticate_with_google(
        self,
        db: Session,
        code: str,
        redirect_uri: str
    ) -> Tuple[str, str, User]:
        """Authenticate user with Google OAuth"""
        # Exchange code for token
        token_data = await self.exchange_google_code(code, redirect_uri)
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get access token from Google"
            )
        
        # Get user info
        user_info = await self.get_google_user_info(access_token)
        
        email = user_info.get("email")
        google_id = user_info.get("id")
        name = user_info.get("name")
        picture = user_info.get("picture")
        
        if not email or not google_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get required user info from Google"
            )
        
        # Find or create user
        user = self._find_or_create_oauth_user(
            db=db,
            provider="google",
            provider_id=google_id,
            email=email,
            name=name,
            avatar_url=picture
        )
        
        # Generate tokens
        jwt_access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        
        return jwt_access_token, refresh_token, user
    
    async def authenticate_with_github(
        self,
        db: Session,
        code: str,
        redirect_uri: str
    ) -> Tuple[str, str, User]:
        """Authenticate user with GitHub OAuth"""
        # Exchange code for token
        token_data = await self.exchange_github_code(code, redirect_uri)
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get access token from GitHub"
            )
        
        # Get user info
        user_info = await self.get_github_user_info(access_token)
        
        email = user_info.get("email")
        github_id = str(user_info.get("id"))
        name = user_info.get("name") or user_info.get("login")
        avatar = user_info.get("avatar_url")
        
        if not email or not github_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get required user info from GitHub. Please make sure your email is public."
            )
        
        # Find or create user
        user = self._find_or_create_oauth_user(
            db=db,
            provider="github",
            provider_id=github_id,
            email=email,
            name=name,
            avatar_url=avatar
        )
        
        # Generate tokens
        jwt_access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        
        return jwt_access_token, refresh_token, user
    
    def _find_or_create_oauth_user(
        self,
        db: Session,
        provider: str,
        provider_id: str,
        email: str,
        name: Optional[str] = None,
        avatar_url: Optional[str] = None
    ) -> User:
        """Find existing user or create new one from OAuth data"""
        # Check if OAuth provider record exists
        oauth_provider = db.query(OAuthProvider).filter(
            OAuthProvider.provider == provider,
            OAuthProvider.provider_user_id == provider_id
        ).first()
        
        if oauth_provider:
            # Return existing user
            return oauth_provider.user
        
        # Check if user exists with this email
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # Create new user
            # Generate unique username from email
            username = email.split("@")[0]
            base_username = username
            counter = 1
            
            while db.query(User).filter(User.username == username).first():
                username = f"{base_username}{counter}"
                counter += 1
            
            user = User(
                email=email,
                username=username,
                full_name=name,
                avatar_url=avatar_url,
                is_verified=True,  # Email verified by OAuth provider
                password_hash=""  # No password for OAuth users
            )
            db.add(user)
            db.flush()  # Get user.id
        
        # Create OAuth provider record
        oauth_record = OAuthProvider(
            user_id=user.id,
            provider=provider,
            provider_user_id=provider_id,
            access_token="",  # We don't store these for security
            refresh_token=""
        )
        db.add(oauth_record)
        db.commit()
        db.refresh(user)
        
        return user


oauth_service = OAuthService()
