"""
Rate limiting utilities
"""
from datetime import datetime
from typing import Dict

# Rate limiting - simple in-memory store
rate_limit_store: Dict[str, list] = {}


def check_rate_limit(client_ip: str, limit: int = 5, window: int = 60) -> bool:
    """Check if client has exceeded rate limit (limit requests per window seconds)"""
    now = datetime.utcnow()
    if client_ip not in rate_limit_store:
        rate_limit_store[client_ip] = []
    
    # Clean old requests outside window
    rate_limit_store[client_ip] = [
        req_time for req_time in rate_limit_store[client_ip]
        if (now - req_time).total_seconds() < window
    ]
    
    # Check if limit exceeded
    if len(rate_limit_store[client_ip]) >= limit:
        return False
    
    # Add current request
    rate_limit_store[client_ip].append(now)
    return True
