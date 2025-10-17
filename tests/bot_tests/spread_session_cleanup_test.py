"""
Tests for spread creation session cleanup and monitoring functionality.

This module tests the session timeout, cleanup mechanisms, and monitoring
for spread creation sessions.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from spread_session_cleanup import (
    SessionCleanupManager,
    get_cleanup_manager,
    start_session_cleanup,
    stop_session_cleanup,
    manual_session_cleanup,
    cleanup_user_session,
    get_session_stats,
    validate_session_age,
    get_session_monitoring_data,
)


class TestSessionCleanupManager:
    """Test the SessionCleanupManager class."""

    def test_init_with_default_values(self):
        """Test SessionCleanupManager initialization with default values."""
        manager = SessionCleanupManager()
        
        assert manager.cleanup_interval == 300  # 5 minutes
        assert manager.max_session_age == 1800  # 30 minutes
        assert manager.max_concurrent_sessions == 100
        assert manager.cleanup_task is None
        assert manager.is_running is False

    def test_init_with_custom_values(self):
        """Test SessionCleanupManager initialization with custom values."""
        manager = SessionCleanupManager(
            cleanup_interval_seconds=600,
            max_session_age_seconds=3600,
            max_concurrent_sessions=50
        )
        
        assert manager.cleanup_interval == 600
        assert manager.max_session_age == 3600
        assert manager.max_concurrent_sessions == 50

    @pytest.mark.asyncio
    async def test_start_cleanup_task(self):
        """Test starting the cleanup task."""
        manager = SessionCleanupManager()
        
        with patch.object(manager, '_cleanup_loop') as mock_cleanup_loop:
            mock_cleanup_loop.return_value = AsyncMock()
            
            await manager.start_cleanup_task()
            
            assert manager.is_running is True
            assert manager.cleanup_task is not None

    @pytest.mark.asyncio
    async def test_start_cleanup_task_already_running(self):
        """Test starting cleanup task when already running."""
        manager = SessionCleanupManager()
        manager.is_running = True
        
        with patch('spread_session_cleanup.logger') as mock_logger:
            await manager.start_cleanup_task()
            
            mock_logger.warning.assert_called_with(
                "Session cleanup task is already running"
            )

    @pytest.mark.asyncio
    async def test_stop_cleanup_task(self):
        """Test stopping the cleanup task."""
        manager = SessionCleanupManager()
        
        # Create a real task that we can cancel
        async def dummy_task():
            await asyncio.sleep(10)  # Long running task
        
        task = asyncio.create_task(dummy_task())
        manager.cleanup_task = task
        manager.is_running = True
        
        await manager.stop_cleanup_task()
        
        assert manager.is_running is False
        assert task.cancelled()

    @pytest.mark.asyncio
    async def test_stop_cleanup_task_not_running(self):
        """Test stopping cleanup task when not running."""
        manager = SessionCleanupManager()
        manager.is_running = False
        
        # Should not raise any errors
        await manager.stop_cleanup_task()
        
        assert manager.is_running is False

    @pytest.mark.asyncio
    @patch('spread_session_cleanup.cleanup_stale_sessions')
    @patch('spread_session_cleanup.get_active_sessions_count')
    @patch('spread_session_cleanup.log_spread_operation')
    async def test_perform_cleanup_success(self, mock_log_op, mock_get_count, mock_cleanup):
        """Test successful cleanup operation."""
        manager = SessionCleanupManager()
        
        # Mock cleanup results
        mock_cleanup.return_value = 3  # 3 sessions cleaned
        mock_get_count.return_value = 5  # 5 sessions remaining
        
        result = await manager.perform_cleanup()
        
        # Check cleanup was called with correct max age
        mock_cleanup.assert_called_once_with(manager.max_session_age)
        
        # Check result
        assert result['cleaned_sessions'] == 3
        assert result['active_sessions'] == 5
        assert 'cleanup_time_ms' in result
        
        # Check logging
        mock_log_op.assert_called_once()

    @pytest.mark.asyncio
    @patch('spread_session_cleanup.cleanup_stale_sessions')
    @patch('spread_session_cleanup.get_active_sessions_count')
    async def test_perform_cleanup_no_sessions_cleaned(self, mock_get_count, mock_cleanup):
        """Test cleanup when no sessions need cleaning."""
        manager = SessionCleanupManager()
        
        # Mock cleanup results
        mock_cleanup.return_value = 0  # No sessions cleaned
        mock_get_count.return_value = 2  # 2 sessions remaining
        
        with patch('spread_session_cleanup.log_spread_operation') as mock_log_op:
            result = await manager.perform_cleanup()
            
            # Should not log when no sessions cleaned
            mock_log_op.assert_not_called()
            
            assert result['cleaned_sessions'] == 0
            assert result['active_sessions'] == 2

    @pytest.mark.asyncio
    @patch('spread_session_cleanup.cleanup_stale_sessions')
    @patch('spread_session_cleanup.get_active_sessions_count')
    async def test_perform_cleanup_high_session_count(self, mock_get_count, mock_cleanup):
        """Test cleanup with high session count warning."""
        manager = SessionCleanupManager(max_concurrent_sessions=10)
        
        # Mock cleanup results
        mock_cleanup.return_value = 0
        mock_get_count.return_value = 15  # Above threshold
        
        with patch('spread_session_cleanup.logger') as mock_logger:
            result = await manager.perform_cleanup()
            
            # Should log warning about high session count
            mock_logger.warning.assert_called_once()
            warning_call = mock_logger.warning.call_args[0][0]
            assert 'High number of active sessions' in warning_call

    @pytest.mark.asyncio
    @patch('spread_session_cleanup.cleanup_stale_sessions')
    async def test_perform_cleanup_error(self, mock_cleanup):
        """Test cleanup when an error occurs."""
        manager = SessionCleanupManager()
        
        # Mock cleanup to raise an error
        test_error = Exception("Test cleanup error")
        mock_cleanup.side_effect = test_error
        
        with patch('spread_session_cleanup.log_spread_operation') as mock_log_op:
            with patch('spread_session_cleanup.logger') as mock_logger:
                result = await manager.perform_cleanup()
                
                # Check error logging
                mock_logger.error.assert_called_once()
                
                # Check failed operation logging
                mock_log_op.assert_called_once()
                call_args = mock_log_op.call_args[1]
                assert call_args['success'] is False
                assert call_args['error'] == test_error
                
                # Check result
                assert result['cleaned_sessions'] == 0
                assert result['active_sessions'] == 0

    @pytest.mark.asyncio
    @patch('spread_state.get_state')
    @patch('spread_state.clear_state')
    @patch('spread_session_cleanup.log_spread_operation')
    async def test_force_cleanup_user_session_success(self, mock_log_op, mock_clear, mock_get):
        """Test successful force cleanup of user session."""
        manager = SessionCleanupManager()
        user_id = 12345
        
        # Mock user has active session
        mock_get.return_value = {'some': 'session_data'}
        
        result = await manager.force_cleanup_user_session(user_id)
        
        # Check session was cleared
        mock_clear.assert_called_once_with(user_id)
        
        # Check success logging
        mock_log_op.assert_called_once()
        call_args = mock_log_op.call_args[1]
        assert call_args['operation'] == 'force_session_cleanup'
        assert call_args['user_id'] == user_id
        assert call_args['success'] is True
        
        assert result is True

    @pytest.mark.asyncio
    @patch('spread_state.get_state')
    async def test_force_cleanup_user_session_no_session(self, mock_get):
        """Test force cleanup when user has no session."""
        manager = SessionCleanupManager()
        user_id = 12345
        
        # Mock user has no active session
        mock_get.return_value = None
        
        result = await manager.force_cleanup_user_session(user_id)
        
        assert result is False

    @pytest.mark.asyncio
    @patch('spread_state.get_state')
    async def test_force_cleanup_user_session_error(self, mock_get):
        """Test force cleanup when an error occurs."""
        manager = SessionCleanupManager()
        user_id = 12345
        
        # Mock error during get_state
        test_error = Exception("Test error")
        mock_get.side_effect = test_error
        
        with patch('spread_session_cleanup.log_spread_operation') as mock_log_op:
            with patch('spread_session_cleanup.logger') as mock_logger:
                result = await manager.force_cleanup_user_session(user_id)
                
                # Check error logging
                mock_logger.error.assert_called_once()
                
                # Check failed operation logging
                mock_log_op.assert_called_once()
                call_args = mock_log_op.call_args[1]
                assert call_args['success'] is False
                assert call_args['error'] == test_error
                
                assert result is False

    @patch('spread_session_cleanup.get_active_sessions_count')
    def test_get_cleanup_stats(self, mock_get_count):
        """Test getting cleanup statistics."""
        manager = SessionCleanupManager(
            cleanup_interval_seconds=600,
            max_session_age_seconds=3600,
            max_concurrent_sessions=50
        )
        manager.is_running = True
        
        mock_get_count.return_value = 10
        
        stats = manager.get_cleanup_stats()
        
        assert stats['is_running'] is True
        assert stats['cleanup_interval_seconds'] == 600
        assert stats['max_session_age_seconds'] == 3600
        assert stats['max_concurrent_sessions'] == 50
        assert stats['active_sessions'] == 10


class TestGlobalFunctions:
    """Test global session cleanup functions."""

    @patch('spread_session_cleanup._cleanup_manager', None)
    def test_get_cleanup_manager_creates_instance(self):
        """Test that get_cleanup_manager creates a new instance."""
        manager = get_cleanup_manager()
        
        assert isinstance(manager, SessionCleanupManager)
        
        # Should return same instance on subsequent calls
        manager2 = get_cleanup_manager()
        assert manager is manager2

    @pytest.mark.asyncio
    @patch('spread_session_cleanup.get_cleanup_manager')
    async def test_start_session_cleanup(self, mock_get_manager):
        """Test starting global session cleanup."""
        mock_manager = Mock()
        mock_manager.start_cleanup_task = AsyncMock()
        mock_get_manager.return_value = mock_manager
        
        await start_session_cleanup()
        
        mock_manager.start_cleanup_task.assert_called_once()

    @pytest.mark.asyncio
    @patch('spread_session_cleanup.get_cleanup_manager')
    async def test_stop_session_cleanup(self, mock_get_manager):
        """Test stopping global session cleanup."""
        mock_manager = Mock()
        mock_manager.stop_cleanup_task = AsyncMock()
        mock_get_manager.return_value = mock_manager
        
        await stop_session_cleanup()
        
        mock_manager.stop_cleanup_task.assert_called_once()

    @pytest.mark.asyncio
    @patch('spread_session_cleanup.get_cleanup_manager')
    async def test_manual_session_cleanup(self, mock_get_manager):
        """Test manual session cleanup."""
        mock_manager = Mock()
        mock_manager.perform_cleanup = AsyncMock(return_value={'cleaned': 5})
        mock_get_manager.return_value = mock_manager
        
        result = await manual_session_cleanup()
        
        mock_manager.perform_cleanup.assert_called_once()
        assert result == {'cleaned': 5}

    @pytest.mark.asyncio
    @patch('spread_session_cleanup.get_cleanup_manager')
    async def test_cleanup_user_session(self, mock_get_manager):
        """Test cleaning up specific user session."""
        mock_manager = Mock()
        mock_manager.force_cleanup_user_session = AsyncMock(return_value=True)
        mock_get_manager.return_value = mock_manager
        
        result = await cleanup_user_session(12345)
        
        mock_manager.force_cleanup_user_session.assert_called_once_with(12345)
        assert result is True

    @patch('spread_session_cleanup.get_cleanup_manager')
    def test_get_session_stats(self, mock_get_manager):
        """Test getting session statistics."""
        mock_manager = Mock()
        mock_manager.get_cleanup_stats.return_value = {'stats': 'data'}
        mock_get_manager.return_value = mock_manager
        
        result = get_session_stats()
        
        mock_manager.get_cleanup_stats.assert_called_once()
        assert result == {'stats': 'data'}


class TestSessionValidation:
    """Test session validation functions."""

    @pytest.mark.asyncio
    @patch('spread_state._state_storage', {})
    async def test_validate_session_age_no_session(self):
        """Test validating session age when no session exists."""
        result = await validate_session_age(12345)
        
        assert result is False

    @pytest.mark.asyncio
    async def test_validate_session_age_valid_session(self):
        """Test validating session age for valid session."""
        user_id = 12345
        current_time = time.time()
        
        # Mock session storage with recent session
        mock_storage = {
            user_id: {
                'state': {'some': 'data'},
                'timestamp': current_time - 300  # 5 minutes ago
            }
        }
        
        with patch('spread_state._state_storage', mock_storage):
            result = await validate_session_age(user_id, max_age_seconds=1800)
            
            assert result is True

    @pytest.mark.asyncio
    async def test_validate_session_age_expired_session(self):
        """Test validating session age for expired session."""
        user_id = 12345
        current_time = time.time()
        
        # Mock session storage with old session
        mock_storage = {
            user_id: {
                'state': {'some': 'data'},
                'timestamp': current_time - 2000  # 33+ minutes ago
            }
        }
        
        with patch('spread_state._state_storage', mock_storage):
            result = await validate_session_age(user_id, max_age_seconds=1800)
            
            assert result is False

    @pytest.mark.asyncio
    async def test_validate_session_age_error(self):
        """Test validating session age when error occurs."""
        with patch('spread_state._state_storage') as mock_storage:
            # Mock error accessing storage
            mock_storage.get.side_effect = Exception("Test error")
            
            with patch('spread_session_cleanup.logger') as mock_logger:
                result = await validate_session_age(12345)
                
                mock_logger.error.assert_called_once()
                assert result is False


class TestSessionMonitoring:
    """Test session monitoring functions."""

    def test_get_session_monitoring_data_no_sessions(self):
        """Test monitoring data when no sessions exist."""
        mock_storage = {}
        
        with patch('spread_state._state_storage', mock_storage):
            with patch('spread_session_cleanup.get_cleanup_manager') as mock_get_manager:
                mock_manager = Mock()
                mock_manager.is_running = True
                mock_get_manager.return_value = mock_manager
                
                result = get_session_monitoring_data()
                
                assert result['total_sessions'] == 0
                assert result['average_session_age_seconds'] == 0
                assert result['oldest_session_age_seconds'] == 0
                assert result['newest_session_age_seconds'] == 0
                assert result['cleanup_manager_running'] is True

    def test_get_session_monitoring_data_with_sessions(self):
        """Test monitoring data with active sessions."""
        current_time = time.time()
        
        # Mock session storage with multiple sessions
        mock_storage = {
            12345: {
                'state': {'some': 'data'},
                'timestamp': current_time - 300  # 5 minutes ago
            },
            67890: {
                'state': {'other': 'data'},
                'timestamp': current_time - 600  # 10 minutes ago
            },
            11111: {
                'state': {'more': 'data'},
                'timestamp': current_time - 100  # 1.67 minutes ago
            }
        }
        
        with patch('spread_state._state_storage', mock_storage):
            with patch('spread_session_cleanup.get_cleanup_manager') as mock_get_manager:
                mock_manager = Mock()
                mock_manager.is_running = False
                mock_get_manager.return_value = mock_manager
                
                result = get_session_monitoring_data()
                
                assert result['total_sessions'] == 3
                assert result['average_session_age_seconds'] == pytest.approx(333.33, rel=1e-1)
                assert result['oldest_session_age_seconds'] == pytest.approx(600, rel=1e-1)
                assert result['newest_session_age_seconds'] == pytest.approx(100, rel=1e-1)
                assert result['cleanup_manager_running'] is False

    def test_get_session_monitoring_data_error(self):
        """Test monitoring data when error occurs."""
        with patch('spread_state._state_storage') as mock_storage:
            # Mock error accessing storage
            mock_storage.items.side_effect = Exception("Test error")
            
            with patch('spread_session_cleanup.logger') as mock_logger:
                result = get_session_monitoring_data()
                
                mock_logger.error.assert_called_once()
                
                # Should return default values on error
                assert result['total_sessions'] == 0
                assert result['average_session_age_seconds'] == 0
                assert result['oldest_session_age_seconds'] == 0
                assert result['newest_session_age_seconds'] == 0
                assert result['cleanup_manager_running'] is False


class TestCleanupLoop:
    """Test the cleanup loop functionality."""

    @pytest.mark.asyncio
    async def test_cleanup_loop_normal_operation(self):
        """Test normal cleanup loop operation."""
        manager = SessionCleanupManager(cleanup_interval_seconds=0.1)  # Fast for testing
        
        # Mock perform_cleanup to track calls
        cleanup_calls = []
        
        async def mock_perform_cleanup():
            cleanup_calls.append(time.time())
            return {'cleaned_sessions': 0, 'active_sessions': 0, 'cleanup_time_ms': 10}
        
        manager.perform_cleanup = mock_perform_cleanup
        
        # Start the loop
        manager.is_running = True
        loop_task = asyncio.create_task(manager._cleanup_loop())
        
        # Let it run for a short time
        await asyncio.sleep(0.25)
        
        # Stop the loop
        manager.is_running = False
        loop_task.cancel()
        
        try:
            await loop_task
        except asyncio.CancelledError:
            pass
        
        # Should have made at least 2 cleanup calls
        assert len(cleanup_calls) >= 2

    @pytest.mark.asyncio
    async def test_cleanup_loop_with_error(self):
        """Test cleanup loop continues after errors."""
        manager = SessionCleanupManager(cleanup_interval_seconds=0.1)
        
        # Mock perform_cleanup to raise error first time, then succeed
        call_count = 0
        
        async def mock_perform_cleanup():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Test error")
            return {'cleaned_sessions': 0, 'active_sessions': 0, 'cleanup_time_ms': 10}
        
        manager.perform_cleanup = mock_perform_cleanup
        
        with patch('spread_session_cleanup.logger') as mock_logger:
            # Start the loop
            manager.is_running = True
            loop_task = asyncio.create_task(manager._cleanup_loop())
            
            # Let it run for a short time
            await asyncio.sleep(0.25)
            
            # Stop the loop
            manager.is_running = False
            loop_task.cancel()
            
            try:
                await loop_task
            except asyncio.CancelledError:
                pass
            
            # Should have logged error but continued running
            mock_logger.error.assert_called()
            assert call_count >= 2  # Should have tried again after error