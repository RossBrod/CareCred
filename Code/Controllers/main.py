from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import logging
from typing import Optional

from .auth_controller import auth_router
from .blockchain_controller import router as blockchain_router
from .user_controller import user_router
from .session_controller import session_router
from .credit_controller import credit_router
from .messaging_controller import messaging_router
from .admin_controller import admin_router
from .public_controller import public_router

# Middleware for request timing and logging
class TimingMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = time.time()
            
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    process_time = time.time() - start_time
                    message["headers"].append((b"X-Process-Time", str(process_time).encode()))
                await send(message)
            
            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logging.info("CareCred API starting up...")
    yield
    # Shutdown
    logging.info("CareCred API shutting down...")


# Initialize FastAPI application
app = FastAPI(
    title="CareCred API",
    description="""
    CareCred is a platform connecting college students with seniors to provide 
    various services in exchange for educational credits.
    
    ## Features
    
    * **User Management**: Registration and authentication for students, seniors, and admins
    * **Session Management**: Request, schedule, and manage help sessions with GPS verification
    * **Credit System**: Earn and disburse educational credits with blockchain verification
    * **Messaging**: Secure communication between users with emergency alert system
    * **Institution Integration**: Direct disbursement to educational institutions
    * **Real-time Monitoring**: Session tracking and anomaly detection
    
    ## Authentication
    
    Most endpoints require authentication via JWT tokens. Include the token in the Authorization header:
    ```
    Authorization: Bearer <your_jwt_token>
    ```
    """,
    version="1.0.0",
    contact={
        "name": "CareCred Support",
        "email": "support@carecred.com",
    },
    license_info={
        "name": "Proprietary",
    },
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://app.carecred.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.carecred.com"]
)

# Custom timing middleware
app.add_middleware(TimingMiddleware)

# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent error format"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "timestamp": time.time(),
                "path": str(request.url)
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logging.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "Internal server error",
                "timestamp": time.time(),
                "path": str(request.url)
            }
        }
    )

# Include routers with prefixes and tags
app.include_router(
    public_router,
    prefix="/api/v1/public",
    tags=["Public"]
)

app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

app.include_router(
    user_router,
    prefix="/api/v1/users",
    tags=["Users"]
)

app.include_router(
    session_router,
    prefix="/api/v1/sessions",
    tags=["Sessions"]
)

app.include_router(
    credit_router,
    prefix="/api/v1/credits",
    tags=["Credits"]
)

app.include_router(
    messaging_router,
    prefix="/api/v1/messaging",
    tags=["Messaging"]
)

app.include_router(
    admin_router,
    prefix="/api/v1/admin",
    tags=["Administration"]
)

app.include_router(
    blockchain_router,
    prefix="/api/v1/blockchain",
    tags=["Blockchain"]
)

# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """System health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    }

@app.get("/", tags=["System"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to CareCred API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }