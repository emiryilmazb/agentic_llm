"""
Middleware components for the FastAPI application.
"""
import time
import logging
from typing import Callable, Dict
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT
)
logger = logging.getLogger("api")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging request information."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request, log information, and call the next middleware.
        
        Args:
            request: The incoming request
            call_next: The next middleware to call
            
        Returns:
            The response from the next middleware
        """
        start_time = time.time()
        
        # Get client IP
        forwarded_for = request.headers.get("X-Forwarded-For")
        client_ip = forwarded_for.split(",")[0] if forwarded_for else request.client.host
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path} from {client_ip}"
        )
        
        # Process request
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response: {response.status_code} for {request.method} {request.url.path} "
                f"processed in {process_time:.4f}s"
            )
            
            # Add processing time header
            response.headers["X-Process-Time"] = f"{process_time:.4f}"
            
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Error: {str(e)} during {request.method} {request.url.path} "
                f"processed in {process_time:.4f}s"
            )
            raise

class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting requests."""
    
    def __init__(self, app: ASGIApp, rate_limit_per_minute: int = None):
        """
        Initialize the rate limiting middleware.
        
        Args:
            app: The ASGI application
            rate_limit_per_minute: Maximum number of requests per minute per IP
        """
        super().__init__(app)
        self.rate_limit = rate_limit_per_minute or settings.RATE_LIMIT_PER_MINUTE
        self.requests: Dict[str, Dict[float, int]] = {}  # IP -> (timestamp -> count)
        self.window_size = 60  # 1 minute in seconds

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request, apply rate limiting, and call the next middleware.
        
        Args:
            request: The incoming request
            call_next: The next middleware to call
            
        Returns:
            The response from the next middleware
        """
        # Skip rate limiting for certain paths
        if request.url.path in ["/", "/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Get client IP
        forwarded_for = request.headers.get("X-Forwarded-For")
        client_ip = forwarded_for.split(",")[0] if forwarded_for else request.client.host
        
        # Clean up old entries
        self._cleanup_old_requests(client_ip)
        
        # Check rate limit
        current_count = self._get_request_count(client_ip)
        
        if current_count >= self.rate_limit:
            # Return 429 Too Many Requests
            return Response(
                content={"status": "error", "message": "Rate limit exceeded"},
                status_code=429,
                media_type="application/json"
            )
        
        # Track this request
        self._track_request(client_ip)
        
        # Process the request
        return await call_next(request)
    
    def _cleanup_old_requests(self, client_ip: str) -> None:
        """
        Remove requests older than the window size.
        
        Args:
            client_ip: Client IP address
        """
        if client_ip not in self.requests:
            return
            
        current_time = time.time()
        self.requests[client_ip] = {
            timestamp: count 
            for timestamp, count in self.requests[client_ip].items() 
            if current_time - timestamp < self.window_size
        }
    
    def _get_request_count(self, client_ip: str) -> int:
        """
        Get the current request count for the client IP.
        
        Args:
            client_ip: Client IP address
            
        Returns:
            Current request count within the window
        """
        if client_ip not in self.requests:
            return 0
            
        return sum(self.requests[client_ip].values())
    
    def _track_request(self, client_ip: str) -> None:
        """
        Track a new request for the client IP.
        
        Args:
            client_ip: Client IP address
        """
        current_time = time.time()
        
        if client_ip not in self.requests:
            self.requests[client_ip] = {}
            
        self.requests[client_ip][current_time] = 1
