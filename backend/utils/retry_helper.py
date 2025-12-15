"""
Retry helper module for API calls with graceful error handling
"""

import asyncio
import functools
import logging
from typing import Any, Callable, Optional, Type, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RetryConfig:
    """Configuration for retry behavior"""
    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True


# Default retry configurations for different types of operations
SEARCH_API_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    initial_delay=1.0,
    max_delay=10.0,
    exponential_base=2.0,
    jitter=True
)

DATABASE_RETRY_CONFIG = RetryConfig(
    max_attempts=5,
    initial_delay=0.5,
    max_delay=5.0,
    exponential_base=1.5,
    jitter=True
)

LLM_RETRY_CONFIG = RetryConfig(
    max_attempts=2,
    initial_delay=2.0,
    max_delay=30.0,
    exponential_base=2.0,
    jitter=False
)


def with_graceful_retry(
    config: RetryConfig = SEARCH_API_RETRY_CONFIG,
    default_return: Any = None,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for retrying function calls with graceful error handling
    
    Args:
        config: Retry configuration
        default_return: Default return value if all retries fail
        exceptions: Tuple of exception types to catch and retry on
        
    Returns:
        Decorated function that will retry on specified exceptions
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(config.max_attempts):
                try:
                    if attempt > 0:
                        delay = _calculate_delay(attempt, config)
                        logger.info(f"Retrying {func.__name__} (attempt {attempt + 1}/{config.max_attempts}) after {delay:.2f}s delay")
                        await asyncio.sleep(delay)
                    
                    return await func(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    if attempt == config.max_attempts - 1:
                        logger.error(f"All {config.max_attempts} attempts failed for {func.__name__}: {str(e)}")
                        if default_return is not None:
                            return default_return
                        raise e
                    
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}")
            
            # This should not be reached, but just in case
            if default_return is not None:
                return default_return
            raise last_exception
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(config.max_attempts):
                try:
                    if attempt > 0:
                        delay = _calculate_delay(attempt, config)
                        logger.info(f"Retrying {func.__name__} (attempt {attempt + 1}/{config.max_attempts}) after {delay:.2f}s delay")
                        import time
                        time.sleep(delay)
                    
                    return func(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    if attempt == config.max_attempts - 1:
                        logger.error(f"All {config.max_attempts} attempts failed for {func.__name__}: {str(e)}")
                        if default_return is not None:
                            return default_return
                        raise e
                    
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}")
            
            # This should not be reached, but just in case
            if default_return is not None:
                return default_return
            raise last_exception
        
        # Return appropriate wrapper based on whether function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def _calculate_delay(attempt: int, config: RetryConfig) -> float:
    """
    Calculate delay for retry attempt with exponential backoff and jitter
    
    Args:
        attempt: Current attempt number (0-based)
        config: Retry configuration
        
    Returns:
        Delay in seconds
    """
    delay = config.initial_delay * (config.exponential_base ** attempt)
    delay = min(delay, config.max_delay)
    
    if config.jitter:
        # Add jitter to avoid thundering herd problems
        import random
        jitter_factor = 0.8 + (random.random() * 0.4)  # 0.8 to 1.2
        delay *= jitter_factor
    
    return delay


async def retry_with_backoff(
    func: Callable,
    *args,
    config: RetryConfig = SEARCH_API_RETRY_CONFIG,
    default_return: Any = None,
    exceptions: tuple = (Exception,),
    **kwargs
) -> Any:
    """
    Standalone function for retrying with backoff
    
    Args:
        func: Function to retry
        *args: Function arguments
        config: Retry configuration
        default_return: Default return value if all retries fail
        exceptions: Exception types to catch and retry on
        **kwargs: Function keyword arguments
        
    Returns:
        Result of function call or default_return
    """
    last_exception = None
    
    for attempt in range(config.max_attempts):
        try:
            if attempt > 0:
                delay = _calculate_delay(attempt, config)
                logger.info(f"Retrying function call (attempt {attempt + 1}/{config.max_attempts}) after {delay:.2f}s delay")
                await asyncio.sleep(delay)
            
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
                
        except exceptions as e:
            last_exception = e
            if attempt == config.max_attempts - 1:
                logger.error(f"All {config.max_attempts} attempts failed: {str(e)}")
                if default_return is not None:
                    return default_return
                raise e
            
            logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
    
    # This should not be reached, but just in case
    if default_return is not None:
        return default_return
    raise last_exception


class CircuitBreaker:
    """
    Simple circuit breaker implementation for preventing cascading failures
    """
    
    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    def is_open(self) -> bool:
        """Check if circuit is open"""
        if self.state == "open":
            import time
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half-open"
                return False
            return True
        return False
    
    def record_success(self):
        """Record a successful call"""
        self.failure_count = 0
        self.state = "closed"
    
    def record_failure(self):
        """Record a failed call"""
        self.failure_count += 1
        import time
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")