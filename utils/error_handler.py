#!/usr/bin/env python3
"""
Shared error handling utilities for the multi-agent system
"""

import logging
import time
from typing import Optional, Any, Dict

# Configure logging
logger = logging.getLogger(__name__)

class ErrorHandler:
    """Centralized error handling for the multi-agent system"""
    
    @staticmethod
    def handle_api_request_error(e: Exception, context: str = "") -> Dict[str, Any]:
        """
        Handle API request errors with consistent logging and response format
        
        Args:
            e: The exception that occurred
            context: Additional context about where the error occurred
            
        Returns:
            Standardized error response dictionary
        """
        error_message = f"Error in {context}: {str(e)}" if context else f"Error: {str(e)}"
        logger.error(error_message, exc_info=True)
        
        return {
            "error": True,
            "message": str(e),
            "context": context,
            "type": type(e).__name__
        }
    
    @staticmethod
    def handle_backend_request_error(e: Exception, elapsed_time: float, url: str = "") -> str:
        """
        Handle backend request errors with timing information
        
        Args:
            e: The exception that occurred
            elapsed_time: Time taken for the request
            url: The URL that was being accessed
            
        Returns:
            Formatted error message
        """
        logger.error(f"Backend request failed after {elapsed_time:.2f}s to {url}: {str(e)}")
        return f"[Error contacting backend: {e}]"
    
    @staticmethod
    def log_request_timing(start_time: float, context: str = "Request") -> float:
        """
        Log request timing information
        
        Args:
            start_time: Start time of the request
            context: Context description for the request
            
        Returns:
            Elapsed time in seconds
        """
        elapsed = time.time() - start_time
        print(f"[{context}-Response Time: {elapsed:.2f} seconds]")
        return elapsed
    
    @staticmethod
    def safe_execute(func, *args, default_return=None, context: str = "", **kwargs):
        """
        Safely execute a function with error handling
        
        Args:
            func: Function to execute
            *args: Positional arguments for the function
            default_return: Value to return if function fails
            context: Context description for error logging
            **kwargs: Keyword arguments for the function
            
        Returns:
            Function result or default_return if function fails
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Safe execution failed in {context}: {str(e)}", exc_info=True)
            return default_return

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class TransitionError(Exception):
    """Custom exception for transition-related errors"""
    pass

class ConfigurationError(Exception):
    """Custom exception for configuration-related errors"""
    pass
