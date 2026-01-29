"""
Response Compression Middleware
- Gzip compression for API responses
- Performance optimization
"""

from fastapi import Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import gzip
import io


class CompressionMiddleware(BaseHTTPMiddleware):
    """HTTP Response Compression Middleware"""
    
    def __init__(self, app: ASGIApp, minimum_size: int = 500):
        """
        Args:
            app: FastAPI application
            minimum_size: Minimum response size (bytes) to compress
        """
        super().__init__(app)
        self.minimum_size = minimum_size
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Check if client accepts gzip
        accept_encoding = request.headers.get("accept-encoding", "")
        
        if "gzip" not in accept_encoding:
            return response
        
        # Skip compression for certain content types
        content_type = response.headers.get("content-type", "")
        skip_types = ["image/", "video/", "audio/", "application/zip", "application/gzip"]
        
        if any(skip in content_type for skip in skip_types):
            return response
        
        # Get response body
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk
        
        # Skip small responses
        if len(response_body) < self.minimum_size:
            return Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
        
        # Compress response
        gzip_buffer = io.BytesIO()
        with gzip.GzipFile(mode="wb", fileobj=gzip_buffer, compresslevel=6) as gzip_file:
            gzip_file.write(response_body)
        
        compressed_body = gzip_buffer.getvalue()
        
        # Update headers
        headers = dict(response.headers)
        headers["content-encoding"] = "gzip"
        headers["content-length"] = str(len(compressed_body))
        headers["vary"] = "Accept-Encoding"
        
        return Response(
            content=compressed_body,
            status_code=response.status_code,
            headers=headers,
            media_type=response.media_type
        )
