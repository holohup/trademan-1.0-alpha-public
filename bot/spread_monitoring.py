"""
Monitoring dashboard for spread creation activity.

This module provides monitoring capabilities for tracking spread creation
metrics, session activity, and system health for the spread creation system.
"""

import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque

from spread_session_cleanup import get_session_monitoring_data, get_session_stats
from spread_logging import get_spread_logger


class SpreadCreationMonitor:
    """
    Monitor for tracking spread creation activity and metrics.
    
    Provides real-time monitoring of spread creation operations,
    session activity, and system performance metrics.
    """
    
    def __init__(self, max_history_size: int = 1000):
        """
        Initialize the spread creation monitor.
        
        Args:
            max_history_size: Maximum number of events to keep in history
        """
        self.max_history_size = max_history_size
        self.logger = get_spread_logger()
        
        # Event history storage
        self.creation_attempts = deque(maxlen=max_history_size)
        self.creation_successes = deque(maxlen=max_history_size)
        self.creation_errors = deque(maxlen=max_history_size)
        self.user_actions = deque(maxlen=max_history_size)
        self.api_calls = deque(maxlen=max_history_size)
        
        # Metrics counters
        self.metrics = {
            'total_attempts': 0,
            'total_successes': 0,
            'total_errors': 0,
            'total_user_actions': 0,
            'total_api_calls': 0,
            'start_time': time.time()
        }
        
        # Performance tracking
        self.performance_data = {
            'avg_creation_time_ms': 0,
            'avg_api_response_time_ms': 0,
            'error_rate_percent': 0,
            'success_rate_percent': 0
        }
    
    def record_creation_attempt(
        self,
        user_id: int,
        far_leg_ticker: str,
        near_leg_ticker: str,
        timestamp: Optional[float] = None
    ) -> None:
        """
        Record a spread creation attempt.
        
        Args:
            user_id: Telegram user ID
            far_leg_ticker: Far leg ticker symbol
            near_leg_ticker: Near leg ticker symbol
            timestamp: Event timestamp (defaults to current time)
        """
        event = {
            'timestamp': timestamp or time.time(),
            'user_id': user_id,
            'far_leg_ticker': far_leg_ticker,
            'near_leg_ticker': near_leg_ticker,
            'event_type': 'creation_attempt'
        }
        
        self.creation_attempts.append(event)
        self.metrics['total_attempts'] += 1
        self._update_performance_metrics()
    
    def record_creation_success(
        self,
        user_id: int,
        spread_id: int,
        far_leg_ticker: str,
        near_leg_ticker: str,
        duration_ms: Optional[float] = None,
        timestamp: Optional[float] = None
    ) -> None:
        """
        Record a successful spread creation.
        
        Args:
            user_id: Telegram user ID
            spread_id: Created spread ID
            far_leg_ticker: Far leg ticker symbol
            near_leg_ticker: Near leg ticker symbol
            duration_ms: Creation duration in milliseconds
            timestamp: Event timestamp (defaults to current time)
        """
        event = {
            'timestamp': timestamp or time.time(),
            'user_id': user_id,
            'spread_id': spread_id,
            'far_leg_ticker': far_leg_ticker,
            'near_leg_ticker': near_leg_ticker,
            'duration_ms': duration_ms,
            'event_type': 'creation_success'
        }
        
        self.creation_successes.append(event)
        self.metrics['total_successes'] += 1
        self._update_performance_metrics()
    
    def record_creation_error(
        self,
        user_id: int,
        error_type: str,
        error_message: str,
        far_leg_ticker: Optional[str] = None,
        near_leg_ticker: Optional[str] = None,
        timestamp: Optional[float] = None
    ) -> None:
        """
        Record a spread creation error.
        
        Args:
            user_id: Telegram user ID
            error_type: Type of error that occurred
            error_message: Error message
            far_leg_ticker: Far leg ticker symbol (if available)
            near_leg_ticker: Near leg ticker symbol (if available)
            timestamp: Event timestamp (defaults to current time)
        """
        event = {
            'timestamp': timestamp or time.time(),
            'user_id': user_id,
            'error_type': error_type,
            'error_message': error_message,
            'far_leg_ticker': far_leg_ticker,
            'near_leg_ticker': near_leg_ticker,
            'event_type': 'creation_error'
        }
        
        self.creation_errors.append(event)
        self.metrics['total_errors'] += 1
        self._update_performance_metrics()
    
    def record_user_action(
        self,
        user_id: int,
        action: str,
        details: Optional[Dict[str, Any]] = None,
        timestamp: Optional[float] = None
    ) -> None:
        """
        Record a user action during spread creation.
        
        Args:
            user_id: Telegram user ID
            action: Action performed by user
            details: Additional action details
            timestamp: Event timestamp (defaults to current time)
        """
        event = {
            'timestamp': timestamp or time.time(),
            'user_id': user_id,
            'action': action,
            'details': details or {},
            'event_type': 'user_action'
        }
        
        self.user_actions.append(event)
        self.metrics['total_user_actions'] += 1
    
    def record_api_call(
        self,
        user_id: int,
        endpoint: str,
        method: str,
        response_status: Optional[int] = None,
        duration_ms: Optional[float] = None,
        timestamp: Optional[float] = None
    ) -> None:
        """
        Record an API call made during spread creation.
        
        Args:
            user_id: Telegram user ID
            endpoint: API endpoint called
            method: HTTP method
            response_status: HTTP response status
            duration_ms: Call duration in milliseconds
            timestamp: Event timestamp (defaults to current time)
        """
        event = {
            'timestamp': timestamp or time.time(),
            'user_id': user_id,
            'endpoint': endpoint,
            'method': method,
            'response_status': response_status,
            'duration_ms': duration_ms,
            'event_type': 'api_call'
        }
        
        self.api_calls.append(event)
        self.metrics['total_api_calls'] += 1
        self._update_performance_metrics()
    
    def get_dashboard_data(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data for monitoring.
        
        Args:
            time_window_hours: Time window for recent activity (hours)
            
        Returns:
            Dictionary with dashboard data
        """
        cutoff_time = time.time() - (time_window_hours * 3600)
        
        # Filter recent events
        recent_attempts = [e for e in self.creation_attempts if e['timestamp'] > cutoff_time]
        recent_successes = [e for e in self.creation_successes if e['timestamp'] > cutoff_time]
        recent_errors = [e for e in self.creation_errors if e['timestamp'] > cutoff_time]
        recent_actions = [e for e in self.user_actions if e['timestamp'] > cutoff_time]
        recent_api_calls = [e for e in self.api_calls if e['timestamp'] > cutoff_time]
        
        # Calculate rates
        total_recent = len(recent_attempts)
        success_rate = (len(recent_successes) / total_recent * 100) if total_recent > 0 else 0
        error_rate = (len(recent_errors) / total_recent * 100) if total_recent > 0 else 0
        
        # Get session data
        session_data = get_session_monitoring_data()
        cleanup_stats = get_session_stats()
        
        # Calculate hourly activity
        hourly_activity = self._calculate_hourly_activity(recent_attempts, time_window_hours)
        
        # Get top error types
        error_types = self._get_top_error_types(recent_errors)
        
        # Get most active users
        active_users = self._get_most_active_users(recent_actions)
        
        # Get API performance
        api_performance = self._get_api_performance(recent_api_calls)
        
        return {
            'overview': {
                'time_window_hours': time_window_hours,
                'total_attempts': len(recent_attempts),
                'total_successes': len(recent_successes),
                'total_errors': len(recent_errors),
                'success_rate_percent': round(success_rate, 2),
                'error_rate_percent': round(error_rate, 2),
                'total_user_actions': len(recent_actions),
                'total_api_calls': len(recent_api_calls)
            },
            'performance': self.performance_data.copy(),
            'sessions': session_data,
            'cleanup': cleanup_stats,
            'activity': {
                'hourly_attempts': hourly_activity,
                'recent_attempts': recent_attempts[-10:],  # Last 10 attempts
                'recent_errors': recent_errors[-10:]  # Last 10 errors
            },
            'analysis': {
                'top_error_types': error_types,
                'most_active_users': active_users,
                'api_performance': api_performance
            },
            'system': {
                'monitor_uptime_hours': round((time.time() - self.metrics['start_time']) / 3600, 2),
                'total_events_tracked': sum([
                    self.metrics['total_attempts'],
                    self.metrics['total_successes'],
                    self.metrics['total_errors'],
                    self.metrics['total_user_actions'],
                    self.metrics['total_api_calls']
                ])
            }
        }
    
    def get_user_activity(self, user_id: int, time_window_hours: int = 24) -> Dict[str, Any]:
        """
        Get activity data for a specific user.
        
        Args:
            user_id: Telegram user ID
            time_window_hours: Time window for activity (hours)
            
        Returns:
            Dictionary with user activity data
        """
        cutoff_time = time.time() - (time_window_hours * 3600)
        
        # Filter user events
        user_attempts = [e for e in self.creation_attempts 
                        if e['user_id'] == user_id and e['timestamp'] > cutoff_time]
        user_successes = [e for e in self.creation_successes 
                         if e['user_id'] == user_id and e['timestamp'] > cutoff_time]
        user_errors = [e for e in self.creation_errors 
                      if e['user_id'] == user_id and e['timestamp'] > cutoff_time]
        user_actions = [e for e in self.user_actions 
                       if e['user_id'] == user_id and e['timestamp'] > cutoff_time]
        
        # Calculate user-specific metrics
        total_attempts = len(user_attempts)
        success_rate = (len(user_successes) / total_attempts * 100) if total_attempts > 0 else 0
        
        return {
            'user_id': user_id,
            'time_window_hours': time_window_hours,
            'total_attempts': total_attempts,
            'total_successes': len(user_successes),
            'total_errors': len(user_errors),
            'success_rate_percent': round(success_rate, 2),
            'total_actions': len(user_actions),
            'recent_attempts': user_attempts[-5:],
            'recent_errors': user_errors[-5:],
            'most_common_actions': self._get_most_common_actions(user_actions)
        }
    
    def _update_performance_metrics(self) -> None:
        """Update performance metrics based on recent data."""
        # Calculate average creation time
        recent_successes = list(self.creation_successes)[-100:]  # Last 100 successes
        creation_times = [e['duration_ms'] for e in recent_successes if e.get('duration_ms')]
        if creation_times:
            self.performance_data['avg_creation_time_ms'] = round(sum(creation_times) / len(creation_times), 2)
        
        # Calculate average API response time
        recent_api_calls = list(self.api_calls)[-100:]  # Last 100 API calls
        api_times = [e['duration_ms'] for e in recent_api_calls if e.get('duration_ms')]
        if api_times:
            self.performance_data['avg_api_response_time_ms'] = round(sum(api_times) / len(api_times), 2)
        
        # Calculate error and success rates
        total_attempts = self.metrics['total_attempts']
        if total_attempts > 0:
            self.performance_data['success_rate_percent'] = round(
                (self.metrics['total_successes'] / total_attempts) * 100, 2
            )
            self.performance_data['error_rate_percent'] = round(
                (self.metrics['total_errors'] / total_attempts) * 100, 2
            )
    
    def _calculate_hourly_activity(self, events: List[Dict], hours: int) -> List[Dict]:
        """Calculate hourly activity distribution."""
        hourly_counts = defaultdict(int)
        current_time = time.time()
        
        for event in events:
            # Calculate which hour bucket this event falls into
            hours_ago = int((current_time - event['timestamp']) / 3600)
            if hours_ago < hours:
                hourly_counts[hours_ago] += 1
        
        # Create hourly data for the specified time window
        hourly_data = []
        for hour in range(hours):
            hourly_data.append({
                'hours_ago': hour,
                'count': hourly_counts[hour],
                'timestamp': current_time - (hour * 3600)
            })
        
        return hourly_data
    
    def _get_top_error_types(self, errors: List[Dict], limit: int = 5) -> List[Dict]:
        """Get the most common error types."""
        error_counts = defaultdict(int)
        
        for error in errors:
            error_type = error.get('error_type', 'Unknown')
            error_counts[error_type] += 1
        
        # Sort by count and return top errors
        sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {'error_type': error_type, 'count': count}
            for error_type, count in sorted_errors[:limit]
        ]
    
    def _get_most_active_users(self, actions: List[Dict], limit: int = 5) -> List[Dict]:
        """Get the most active users by action count."""
        user_counts = defaultdict(int)
        
        for action in actions:
            user_id = action.get('user_id')
            if user_id:
                user_counts[user_id] += 1
        
        # Sort by count and return top users
        sorted_users = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {'user_id': user_id, 'action_count': count}
            for user_id, count in sorted_users[:limit]
        ]
    
    def _get_api_performance(self, api_calls: List[Dict]) -> Dict[str, Any]:
        """Get API performance metrics."""
        if not api_calls:
            return {'total_calls': 0, 'avg_response_time_ms': 0, 'error_rate_percent': 0}
        
        total_calls = len(api_calls)
        response_times = [call['duration_ms'] for call in api_calls if call.get('duration_ms')]
        error_calls = [call for call in api_calls if call.get('response_status', 200) >= 400]
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        error_rate = (len(error_calls) / total_calls) * 100 if total_calls > 0 else 0
        
        return {
            'total_calls': total_calls,
            'avg_response_time_ms': round(avg_response_time, 2),
            'error_rate_percent': round(error_rate, 2),
            'successful_calls': total_calls - len(error_calls)
        }
    
    def _get_most_common_actions(self, actions: List[Dict], limit: int = 5) -> List[Dict]:
        """Get the most common user actions."""
        action_counts = defaultdict(int)
        
        for action in actions:
            action_type = action.get('action', 'unknown')
            action_counts[action_type] += 1
        
        # Sort by count and return top actions
        sorted_actions = sorted(action_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {'action': action_type, 'count': count}
            for action_type, count in sorted_actions[:limit]
        ]


# Global monitor instance
_monitor: Optional[SpreadCreationMonitor] = None


def get_monitor() -> SpreadCreationMonitor:
    """
    Get the global spread creation monitor instance.
    
    Returns:
        SpreadCreationMonitor instance
    """
    global _monitor
    if _monitor is None:
        _monitor = SpreadCreationMonitor()
    return _monitor


# Convenience functions for recording events
def record_creation_attempt(user_id: int, far_leg_ticker: str, near_leg_ticker: str) -> None:
    """Record a spread creation attempt."""
    monitor = get_monitor()
    monitor.record_creation_attempt(user_id, far_leg_ticker, near_leg_ticker)


def record_creation_success(
    user_id: int,
    spread_id: int,
    far_leg_ticker: str,
    near_leg_ticker: str,
    duration_ms: Optional[float] = None
) -> None:
    """Record a successful spread creation."""
    monitor = get_monitor()
    monitor.record_creation_success(user_id, spread_id, far_leg_ticker, near_leg_ticker, duration_ms)


def record_creation_error(
    user_id: int,
    error_type: str,
    error_message: str,
    far_leg_ticker: Optional[str] = None,
    near_leg_ticker: Optional[str] = None
) -> None:
    """Record a spread creation error."""
    monitor = get_monitor()
    monitor.record_creation_error(user_id, error_type, error_message, far_leg_ticker, near_leg_ticker)


def record_user_action(user_id: int, action: str, details: Optional[Dict[str, Any]] = None) -> None:
    """Record a user action."""
    monitor = get_monitor()
    monitor.record_user_action(user_id, action, details)


def record_api_call(
    user_id: int,
    endpoint: str,
    method: str,
    response_status: Optional[int] = None,
    duration_ms: Optional[float] = None
) -> None:
    """Record an API call."""
    monitor = get_monitor()
    monitor.record_api_call(user_id, endpoint, method, response_status, duration_ms)


def get_dashboard_data(time_window_hours: int = 24) -> Dict[str, Any]:
    """Get dashboard data for monitoring."""
    monitor = get_monitor()
    return monitor.get_dashboard_data(time_window_hours)


def get_user_activity(user_id: int, time_window_hours: int = 24) -> Dict[str, Any]:
    """Get activity data for a specific user."""
    monitor = get_monitor()
    return monitor.get_user_activity(user_id, time_window_hours)