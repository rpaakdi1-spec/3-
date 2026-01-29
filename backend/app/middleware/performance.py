"""
Performance Monitoring Middleware
- Request/Response timing
- Slow query detection
- Memory usage tracking
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import psutil
from loguru import logger
from typing import Callable


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Performance Monitoring Middleware"""
    
    def __init__(
        self,
        app: ASGIApp,
        slow_request_threshold: float = 1.0,
        enable_memory_tracking: bool = True
    ):
        """
        Args:
            app: FastAPI application
            slow_request_threshold: Threshold (seconds) for slow request logging
            enable_memory_tracking: Enable memory usage tracking
        """
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold
        self.enable_memory_tracking = enable_memory_tracking
        self.process = psutil.Process()
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Start timing
        start_time = time.time()
        
        # Memory before request (if enabled)
        memory_before = None
        if self.enable_memory_tracking:
            try:
                memory_before = self.process.memory_info().rss / 1024 / 1024  # MB
            except:
                pass
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Memory after request (if enabled)
        memory_after = None
        memory_diff = None
        if self.enable_memory_tracking and memory_before is not None:
            try:
                memory_after = self.process.memory_info().rss / 1024 / 1024  # MB
                memory_diff = memory_after - memory_before
            except:
                pass
        
        # Add performance headers
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        
        if memory_after is not None:
            response.headers["X-Memory-Usage"] = f"{memory_after:.2f}MB"
        
        # Log slow requests
        if duration > self.slow_request_threshold:
            log_data = {
                "method": request.method,
                "path": request.url.path,
                "duration": f"{duration:.3f}s",
                "status": response.status_code
            }
            
            if memory_diff is not None:
                log_data["memory_delta"] = f"{memory_diff:.2f}MB"
            
            logger.warning(f"Slow request detected: {log_data}")
        else:
            # Log normal requests at debug level
            logger.debug(
                f"{request.method} {request.url.path} "
                f"- {response.status_code} "
                f"- {duration:.3f}s"
            )
        
        return response


class QueryPerformanceTracker:
    """Database Query Performance Tracker"""
    
    def __init__(self):
        self.slow_queries = []
        self.query_count = 0
        self.total_query_time = 0.0
    
    def track_query(self, query: str, duration: float, threshold: float = 0.5):
        """
        Track database query performance
        
        Args:
            query: SQL query string
            duration: Query execution time (seconds)
            threshold: Slow query threshold (seconds)
        """
        self.query_count += 1
        self.total_query_time += duration
        
        if duration > threshold:
            self.slow_queries.append({
                "query": query[:200],  # First 200 chars
                "duration": duration,
                "timestamp": time.time()
            })
            
            logger.warning(
                f"Slow query detected ({duration:.3f}s): {query[:100]}..."
            )
    
    def get_stats(self):
        """Get query performance statistics"""
        avg_query_time = (
            self.total_query_time / self.query_count
            if self.query_count > 0
            else 0
        )
        
        return {
            "total_queries": self.query_count,
            "total_time": round(self.total_query_time, 3),
            "average_time": round(avg_query_time, 3),
            "slow_queries_count": len(self.slow_queries),
            "recent_slow_queries": self.slow_queries[-10:]  # Last 10
        }
    
    def reset(self):
        """Reset statistics"""
        self.slow_queries = []
        self.query_count = 0
        self.total_query_time = 0.0


# Global query tracker instance
query_tracker = QueryPerformanceTracker()
