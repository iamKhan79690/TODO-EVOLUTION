"""
Performance Monitoring System for MCP Server

Tracks tool execution metrics, response times, and resource usage to ensure
performance targets (<200ms response times, 100 concurrent executions) are met.
"""

import sys
from pathlib import Path

# Ensure MCP server root is in path
MCP_ROOT = Path(__file__).parent.parent
if str(MCP_ROOT) not in sys.path:
    sys.path.insert(0, str(MCP_ROOT))

import time
import threading
import psutil
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from collections import deque, defaultdict
from datetime import datetime, timedelta
import asyncio
import json

from utils.correlation_ids import get_correlation_id


@dataclass
class PerformanceMetric:
    """Single performance metric measurement."""
    tool_name: str
    correlation_id: str
    start_time: float
    end_time: float
    success: bool
    error_type: Optional[str] = None
    user_id: Optional[str] = None

    @property
    def duration_ms(self) -> float:
        """Get duration in milliseconds."""
        return (self.end_time - self.start_time) * 1000

    @property
    def timestamp(self) -> datetime:
        """Get metric timestamp."""
        return datetime.fromtimestamp(self.start_time)


@dataclass
class PerformanceStats:
    """Aggregated performance statistics."""
    tool_name: str
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    total_duration_ms: float = 0.0
    min_duration_ms: float = float('inf')
    max_duration_ms: float = 0.0
    recent_durations: deque = field(default_factory=lambda: deque(maxlen=1000))

    @property
    def success_rate(self) -> float:
        """Get success rate as percentage."""
        return (self.successful_calls / self.total_calls * 100) if self.total_calls > 0 else 0.0

    @property
    def avg_duration_ms(self) -> float:
        """Get average duration in milliseconds."""
        return (self.total_duration_ms / self.total_calls) if self.total_calls > 0 else 0.0

    @property
    def p95_duration_ms(self) -> float:
        """Get 95th percentile duration."""
        if not self.recent_durations:
            return 0.0
        sorted_durations = sorted(list(self.recent_durations))
        index = int(len(sorted_durations) * 0.95)
        return sorted_durations[min(index, len(sorted_durations) - 1)]

    @property
    def p99_duration_ms(self) -> float:
        """Get 99th percentile duration."""
        if not self.recent_durations:
            return 0.0
        sorted_durations = sorted(list(self.recent_durations))
        index = int(len(sorted_durations) * 0.99)
        return sorted_durations[min(index, len(sorted_durations) - 1)]

    def add_metric(self, metric: PerformanceMetric):
        """Add a metric to the statistics."""
        self.total_calls += 1
        self.total_duration_ms += metric.duration_ms
        self.recent_durations.append(metric.duration_ms)

        if metric.success:
            self.successful_calls += 1
        else:
            self.failed_calls += 1

        self.min_duration_ms = min(self.min_duration_ms, metric.duration_ms)
        self.max_duration_ms = max(self.max_duration_ms, metric.duration_ms)

    def to_dict(self) -> Dict[str, Any]:
        """Convert statistics to dictionary."""
        return {
            "tool_name": self.tool_name,
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "success_rate": self.success_rate,
            "avg_duration_ms": self.avg_duration_ms,
            "p95_duration_ms": self.p95_duration_ms,
            "p99_duration_ms": self.p99_duration_ms,
            "min_duration_ms": self.min_duration_ms if self.min_duration_ms != float('inf') else 0.0,
            "max_duration_ms": self.max_duration_ms,
            "recent_calls_count": len(self.recent_durations)
        }


class PerformanceMonitor:
    """Main performance monitoring system."""

    def __init__(self, max_metrics: int = 10000):
        self.max_metrics = max_metrics
        self.metrics: deque = deque(maxlen=max_metrics)
        self.stats: Dict[str, PerformanceStats] = defaultdict(PerformanceStats)
        self.concurrent_requests: int = 0
        self.max_concurrent: int = 0
        self.start_time = time.time()
        self._lock = threading.RLock()
        self._monitoring_thread = None
        self._stop_monitoring = threading.Event()

    def start_monitoring(self):
        """Start background monitoring thread."""
        self._monitoring_thread = threading.Thread(target=self._monitor_system_metrics, daemon=True)
        self._monitoring_thread.start()
        print("📊 Performance monitoring started")

    def stop_monitoring(self):
        """Stop background monitoring thread."""
        self._stop_monitoring.set()
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5)
        print("📊 Performance monitoring stopped")

    def start_request(self, tool_name: str, user_id: Optional[str] = None) -> str:
        """
        Start tracking a request.

        Args:
            tool_name: Name of the MCP tool being called
            user_id: Optional user ID

        Returns:
            Request ID for tracking
        """
        request_id = f"{tool_name}_{int(time.time() * 1000000)}"

        with self._lock:
            self.concurrent_requests += 1
            self.max_concurrent = max(self.max_concurrent, self.concurrent_requests)

        return request_id

    def end_request(
        self,
        request_id: str,
        tool_name: str,
        start_time: float,
        success: bool = True,
        error_type: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        """
        End tracking a request.

        Args:
            request_id: Request ID from start_request
            tool_name: Name of the MCP tool
            start_time: Start time from time.time()
            success: Whether the request was successful
            error_type: Type of error if failed
            user_id: Optional user ID
        """
        end_time = time.time()
        correlation_id = get_correlation_id()

        metric = PerformanceMetric(
            tool_name=tool_name,
            correlation_id=correlation_id,
            start_time=start_time,
            end_time=end_time,
            success=success,
            error_type=error_type,
            user_id=user_id
        )

        with self._lock:
            self.metrics.append(metric)
            self.stats[tool_name].add_metric(metric)
            self.concurrent_requests = max(0, self.concurrent_requests - 1)

        # Alert if performance targets are not met
        if metric.duration_ms > 200:  # 200ms target
            self._log_performance_issue("High response time", metric)

    def _log_performance_issue(self, issue: str, metric: PerformanceMetric):
        """Log performance issues."""
        print(f"🚨 Performance Issue: {issue}")
        print(f"   Tool: {metric.tool_name}")
        print(f"   Duration: {metric.duration_ms:.2f}ms")
        print(f"   Correlation ID: {metric.correlation_id}")
        print(f"   Timestamp: {metric.timestamp}")

    def _monitor_system_metrics(self):
        """Background thread for monitoring system metrics."""
        while not self._stop_monitoring.wait(1.0):  # Check every second
            try:
                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024

                # Alert if memory usage is high
                if memory_mb > 100:  # 100MB target
                    print(f"⚠️ High memory usage: {memory_mb:.1f}MB")

            except Exception:
                pass  # Ignore monitoring errors

    def get_stats(self, tool_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get performance statistics.

        Args:
            tool_name: Optional tool name to get stats for

        Returns:
            Dictionary with performance statistics
        """
        with self._lock:
            if tool_name:
                if tool_name in self.stats:
                    return self.stats[tool_name].to_dict()
                else:
                    return {"error": f"No stats found for tool: {tool_name}"}

            # Return overall stats
            overall_stats = {
                "uptime_seconds": time.time() - self.start_time,
                "total_metrics": len(self.metrics),
                "current_concurrent_requests": self.concurrent_requests,
                "max_concurrent_requests": self.max_concurrent,
                "tool_stats": {name: stats.to_dict() for name, stats in self.stats.items()},
                "system_info": self._get_system_info()
            }

            return overall_stats

    def _get_system_info(self) -> Dict[str, Any]:
        """Get current system information."""
        try:
            process = psutil.Process()
            return {
                "memory_mb": process.memory_info().rss / 1024 / 1024,
                "memory_percent": process.memory_percent(),
                "cpu_percent": process.cpu_percent(),
                "threads": process.num_threads()
            }
        except Exception:
            return {"error": "Unable to get system info"}

    def get_recent_metrics(self, count: int = 100, tool_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get recent metrics.

        Args:
            count: Number of recent metrics to return
            tool_name: Optional tool name to filter by

        Returns:
            List of recent metrics
        """
        with self._lock:
            recent = list(self.metrics)[-count:]
            if tool_name:
                recent = [m for m in recent if m.tool_name == tool_name]

            return [
                {
                    "tool_name": m.tool_name,
                    "correlation_id": m.correlation_id,
                    "duration_ms": m.duration_ms,
                    "success": m.success,
                    "error_type": m.error_type,
                    "timestamp": m.timestamp.isoformat(),
                    "user_id": m.user_id
                }
                for m in recent
            ]

    def check_performance_targets(self) -> Dict[str, Any]:
        """
        Check if performance targets are being met.

        Returns:
            Dictionary with target compliance information
        """
        targets_met = True
        issues = []

        # Check response time targets
        for tool_name, stats in self.stats.items():
            if stats.p95_duration_ms > 200:  # 200ms target
                targets_met = False
                issues.append(f"{tool_name}: P95 response time {stats.p95_duration_ms:.1f}ms > 200ms")

            if stats.success_rate < 99:  # 99% success rate target
                targets_met = False
                issues.append(f"{tool_name}: Success rate {stats.success_rate:.1f}% < 99%")

        # Check concurrent execution target
        if self.max_concurrent < 50:  # Expect to handle at least 50 concurrent
            issues.append(f"Max concurrent requests: {self.max_concurrent} (target: 50+)")

        # Check memory usage
        try:
            memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
            if memory_mb > 100:  # 100MB target
                targets_met = False
                issues.append(f"Memory usage: {memory_mb:.1f}MB > 100MB")
        except Exception:
            pass

        return {
            "targets_met": targets_met,
            "issues": issues,
            "summary": "All targets met" if targets_met else f"Issues found: {len(issues)}"
        }


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


# Context manager for performance tracking
class PerformanceContext:
    """Context manager for tracking tool performance."""

    def __init__(self, tool_name: str, user_id: Optional[str] = None):
        self.tool_name = tool_name
        self.user_id = user_id
        self.start_time = None
        self.request_id = None

    def __enter__(self):
        """Enter performance tracking context."""
        self.start_time = time.time()
        self.request_id = performance_monitor.start_request(self.tool_name, self.user_id)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit performance tracking context."""
        if self.start_time:
            success = exc_type is None
            error_type = exc_type.__name__ if exc_type else None
            performance_monitor.end_request(
                self.request_id,
                self.tool_name,
                self.start_time,
                success=success,
                error_type=error_type,
                user_id=self.user_id
            )


def track_performance(tool_name: str, user_id: Optional[str] = None):
    """
    Decorator to automatically track function performance.

    Usage:
        @track_performance("add_task")
        async def add_task_function(param1, param2, user_id=None):
            # Function implementation
            pass
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            async with PerformanceContext(tool_name, user_id):
                return await func(*args, **kwargs)
        return wrapper
    return decorator


# Convenience functions
def get_performance_stats(tool_name: Optional[str] = None) -> Dict[str, Any]:
    """Get performance statistics."""
    return performance_monitor.get_stats(tool_name)


def check_performance_targets() -> Dict[str, Any]:
    """Check if performance targets are being met."""
    return performance_monitor.check_performance_targets()