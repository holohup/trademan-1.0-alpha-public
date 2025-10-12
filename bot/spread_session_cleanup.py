"""
Session cleanup and timeout management for spread creation.

This module provides session timeout and cleanup mechanisms to prevent
memory leaks and ensure security by automatically cleaning up stale sessions.
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional
from spread_state import cleanup_stale_sessions, get_active_sessions_count
from spread_error_handling import log_spread_operation


# Configure logging for session cleanup
logger = logging.getLogger('spread_session_cleanup')


class SessionCleanupManager:
    """
    Manages automatic cleanup of stale spread creation sessions.
    
    Provides periodic cleanup of expired sessions and monitoring
    of session activity for security and performance.
    """
    
    def __init__(
        self,
        cleanup_interval_seconds: int = 300,  # 5 minutes
        max_session_age_seconds: int = 1800,  # 30 minutes
        max_concurrent_sessions: int = 100
    ):
        """
        Initialize session cleanup manager.
        
        Args:
            cleanup_interval_seconds: How often to run cleanup
            max_session_age_seconds: Maximum session age before cleanup
            max_concurrent_sessions: Maximum number of concurrent sessions allowed
        """
        self.cleanup_interval = cleanup_interval_seconds
        self.max_session_age = max_session_age_seconds
        self.max_concurrent_sessions = max_concurrent_sessions
        self.cleanup_task = None
        self.is_running = False
        
    async def start_cleanup_task(self) -> None:
        """
        Start the automatic session cleanup task.
        
        This should be called when the bot starts up to begin
        periodic session cleanup.
        """
        if self.is_running:
            logger.warning("Session cleanup task is already running")
            return
            
        self.is_running = True
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info(
            f"Started session cleanup task with "
            f"{self.cleanup_interval}s interval, {self.max_session_age}s max age"
        )
        
    async def stop_cleanup_task(self) -> None:
        """
        Stop the automatic session cleanup task.
        
        This should be called when the bot shuts down to clean up
        the background task.
        """
        if not self.is_running:
            return
            
        self.is_running = False
        
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
            
        logger.info("Stopped session cleanup task")
        
    async def _cleanup_loop(self) -> None:
        """
        Main cleanup loop that runs periodically.
        
        Performs session cleanup and monitoring at regular intervals.
        """
        while self.is_running:
            try:
                await self.perform_cleanup()
                await asyncio.sleep(self.cleanup_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(
                    f"Error in session cleanup loop: {str(e)}",
                    exc_info=True
                )
                # Continue running even if cleanup fails
                await asyncio.sleep(self.cleanup_interval)
                
    async def perform_cleanup(self) -> Dict[str, int]:
        """
        Perform session cleanup and return statistics.
        
        Returns:
            Dictionary with cleanup statistics:
            - cleaned_sessions: Number of sessions cleaned up
            - active_sessions: Number of active sessions remaining
            - cleanup_time_ms: Time taken for cleanup in milliseconds
        """
        start_time = time.time()
        
        try:
            # Perform cleanup
            cleaned_count = cleanup_stale_sessions(self.max_session_age)
            
            # Get session count after cleanup
            sessions_after = get_active_sessions_count()
            
            # Calculate cleanup time
            cleanup_time_ms = int((time.time() - start_time) * 1000)
            
            # Log cleanup results
            if cleaned_count > 0:
                logger.info(
                    f"Cleaned up {cleaned_count} stale sessions, "
                    f"{sessions_after} active sessions remaining"
                )
                
                # Log cleanup operation
                log_spread_operation(
                    operation="session_cleanup",
                    user_id=0,  # System operation
                    success=True,
                    details={
                        'cleaned_sessions': cleaned_count,
                        'active_sessions': sessions_after,
                        'cleanup_time_ms': cleanup_time_ms
                    }
                )
            
            # Check for too many concurrent sessions
            if sessions_after > self.max_concurrent_sessions:
                logger.warning(
                    f"High number of active sessions: {sessions_after} "
                    f"(max: {self.max_concurrent_sessions})"
                )
            
            return {
                'cleaned_sessions': cleaned_count,
                'active_sessions': sessions_after,
                'cleanup_time_ms': cleanup_time_ms
            }
            
        except Exception as e:
            logger.error(
                f"Error during session cleanup: {str(e)}",
                exc_info=True
            )
            
            # Log failed cleanup operation
            log_spread_operation(
                operation="session_cleanup",
                user_id=0,
                success=False,
                error=e
            )
            
            return {
                'cleaned_sessions': 0,
                'active_sessions': 0,
                'cleanup_time_ms': int((time.time() - start_time) * 1000)
            }
            
    async def force_cleanup_user_session(self, user_id: int) -> bool:
        """
        Force cleanup of a specific user's session.
        
        Args:
            user_id: Telegram user ID to clean up
            
        Returns:
            True if session was found and cleaned, False otherwise
        """
        try:
            from spread_state import clear_state, get_state
            
            # Check if user has active session
            if get_state(user_id):
                clear_state(user_id)
                
                logger.info(f"Force cleaned session for user {user_id}")
                
                log_spread_operation(
                    operation="force_session_cleanup",
                    user_id=user_id,
                    success=True
                )
                
                return True
            
            return False
                
        except Exception as e:
            logger.error(
                f"Error force cleaning session for user {user_id}: {str(e)}",
                exc_info=True
            )
            
            log_spread_operation(
                operation="force_session_cleanup",
                user_id=user_id,
                success=False,
                error=e
            )
            
            return False
            
    def get_cleanup_stats(self) -> Dict[str, Any]:
        """
        Get current cleanup manager statistics.
        
        Returns:
            Dictionary with current statistics and configuration
        """
        stats = {
            'is_running': self.is_running,
            'cleanup_interval_seconds': self.cleanup_interval,
            'max_session_age_seconds': self.max_session_age,
            'max_concurrent_sessions': self.max_concurrent_sessions,
            'active_sessions': get_active_sessions_count()
        }
        return stats


# Global cleanup manager instance
_cleanup_manager = None


def get_cleanup_manager() -> SessionCleanupManager:
    """
    Get the global session cleanup manager instance.
    
    Returns:
        SessionCleanupManager instance
    """
    global _cleanup_manager
    if _cleanup_manager is None:
        _cleanup_manager = SessionCleanupManager()
    return _cleanup_manager


async def start_session_cleanup() -> None:
    """
    Start the global session cleanup task.
    
    This should be called during bot initialization.
    """
    manager = get_cleanup_manager()
    await manager.start_cleanup_task()


async def stop_session_cleanup() -> None:
    """
    Stop the global session cleanup task.
    
    This should be called during bot shutdown.
    """
    manager = get_cleanup_manager()
    await manager.stop_cleanup_task()


async def manual_session_cleanup() -> Dict[str, int]:
    """
    Perform manual session cleanup and return statistics.
    
    Returns:
        Dictionary with cleanup statistics
    """
    manager = get_cleanup_manager()
    return await manager.perform_cleanup()


async def cleanup_user_session(user_id: int) -> bool:
    """
    Force cleanup of a specific user's session.
    
    Args:
        user_id: Telegram user ID to clean up
        
    Returns:
        True if session was cleaned, False otherwise
    """
    manager = get_cleanup_manager()
    return await manager.force_cleanup_user_session(user_id)


def get_session_stats() -> Dict[str, Any]:
    """
    Get current session statistics.
    
    Returns:
        Dictionary with session statistics
    """
    manager = get_cleanup_manager()
    return manager.get_cleanup_stats()


# Session timeout validation function
async def validate_session_age(user_id: int, max_age_seconds: int = 1800) -> bool:
    """
    Validate that a user's session is not too old.
    
    Args:
        user_id: Telegram user ID
        max_age_seconds: Maximum allowed session age in seconds
        
    Returns:
        True if session is valid, False if too old or doesn't exist
    """
    try:
        from spread_state import _state_storage
        
        stored_data = _state_storage.get(user_id)
        if not stored_data:
            return False
            
        session_age = time.time() - stored_data['timestamp']
        return session_age <= max_age_seconds
        
    except Exception as e:
        logger.error(
            f"Error validating session age for user {user_id}: {str(e)}",
            exc_info=True
        )
        return False


# Monitoring functions
def get_session_monitoring_data() -> Dict[str, Any]:
    """
    Get comprehensive session monitoring data.
    
    Returns:
        Dictionary with monitoring information
    """
    try:
        from spread_state import _state_storage
        
        current_time = time.time()
        session_ages = []
        
        for user_id, stored_data in _state_storage.items():
            age = current_time - stored_data['timestamp']
            session_ages.append(age)
            
        if session_ages:
            avg_age = sum(session_ages) / len(session_ages)
            max_age = max(session_ages)
            min_age = min(session_ages)
        else:
            avg_age = max_age = min_age = 0
            
        return {
            'total_sessions': len(_state_storage),
            'average_session_age_seconds': avg_age,
            'oldest_session_age_seconds': max_age,
            'newest_session_age_seconds': min_age,
            'cleanup_manager_running': get_cleanup_manager().is_running
        }
        
    except Exception as e:
        logger.error(
            f"Error getting session monitoring data: {str(e)}",
            exc_info=True
        )
        return {
            'total_sessions': 0,
            'average_session_age_seconds': 0,
            'oldest_session_age_seconds': 0,
            'newest_session_age_seconds': 0,
            'cleanup_manager_running': False
        }