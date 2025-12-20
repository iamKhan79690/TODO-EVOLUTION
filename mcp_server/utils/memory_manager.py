"""
Memory Management System for MCP Server

Monitors and manages memory usage to ensure <100MB per instance constraint.
Provides automatic cleanup and optimization for long-running MCP server processes.
"""

import gc
import threading
import time
import weakref
import psutil
from typing import Dict, Any, Optional, Set, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio
from contextlib import contextmanager


@dataclass
class MemoryStats:
    """Memory usage statistics."""
    rss_mb: float  # Resident Set Size in MB
    vms_mb: float  # Virtual Memory Size in MB
    percent: float  # Memory percentage
    available_mb: float  # Available memory in MB
    timestamp: datetime
    tracked_objects: int = 0
    gc_collections: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rss_mb": round(self.rss_mb, 2),
            "vms_mb": round(self.vms_mb, 2),
            "percent": round(self.percent, 2),
            "available_mb": round(self.available_mb, 2),
            "timestamp": self.timestamp.isoformat(),
            "tracked_objects": self.tracked_objects,
            "gc_collections": self.gc_collections
        }


class MemoryManager:
    """
    Manages memory usage for the MCP server with <100MB target.

    Features:
    - Automatic memory monitoring
    - Garbage collection triggering
    - Object tracking for debugging
    - Memory usage alerts
    - Cleanup recommendations
    """

    def __init__(self, memory_limit_mb: int = 100, check_interval_seconds: int = 30):
        self.memory_limit_bytes = memory_limit_mb * 1024 * 1024
        self.memory_limit_mb = memory_limit_mb
        self.check_interval = check_interval_seconds

        self.process = psutil.Process()
        self.tracked_objects: weakref.WeakSet = weakref.WeakSet()
        self.memory_stats: List[MemoryStats] = []

        self._monitoring_thread = None
        self._stop_monitoring = threading.Event()
        self._lock = threading.RLock()

        # GC tracking
        self.gc_stats = {
            "collections_triggered": 0,
            "last_collection": None,
            "objects_collected": 0
        }

    def start_monitoring(self):
        """Start background memory monitoring thread."""
        self._monitoring_thread = threading.Thread(target=self._monitor_memory, daemon=True)
        self._monitoring_thread.start()
        print(f"🧠 Memory monitoring started (limit: {self.memory_limit_mb}MB)")

    def stop_monitoring(self):
        """Stop background monitoring thread."""
        self._stop_monitoring.set()
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5)
        print("🧠 Memory monitoring stopped")

    def check_memory_usage(self) -> bool:
        """
        Check if current memory usage is within limits.

        Returns:
            True if memory usage is within limits, False otherwise
        """
        try:
            memory_info = self.process.memory_info()
            current_memory = memory_info.rss

            return current_memory < self.memory_limit_bytes
        except Exception:
            return True  # Assume safe if we can't check

    def get_memory_usage(self) -> MemoryStats:
        """
        Get current memory usage statistics.

        Returns:
            MemoryStats object with current usage information
        """
        try:
            memory_info = self.process.memory_info()
            memory_percent = self.process.memory_percent()
            available_memory = psutil.virtual_memory().available / 1024 / 1024

            return MemoryStats(
                rss_mb=memory_info.rss / 1024 / 1024,
                vms_mb=memory_info.vms / 1024 / 1024,
                percent=memory_percent,
                available_mb=available_memory,
                timestamp=datetime.utcnow(),
                tracked_objects=len(self.tracked_objects),
                gc_collections=self.gc_stats["collections_triggered"]
            )
        except Exception as e:
            # Return default stats on error
            return MemoryStats(
                rss_mb=0.0, vms_mb=0.0, percent=0.0, available_mb=0.0,
                timestamp=datetime.utcnow(), tracked_objects=0, gc_collections=0
            )

    def trigger_gc_if_needed(self, force: bool = False) -> Dict[str, Any]:
        """
        Trigger garbage collection if memory usage is high or forced.

        Args:
            force: Force GC regardless of memory usage

        Returns:
            Dictionary with GC results
        """
        before_stats = self.get_memory_usage()

        # Determine if GC should run
        should_run = force or not self.check_memory_usage()

        if not should_run:
            return {
                "gc_triggered": False,
                "reason": "Memory usage within limits",
                "before_memory_mb": before_stats.rss_mb,
                "after_memory_mb": before_stats.rss_mb
            }

        try:
            # Run garbage collection
            gc.collect()

            # Collect generation statistics
            gc_stats = gc.get_stats() if hasattr(gc, 'get_stats') else []

            after_stats = self.get_memory_usage()

            # Update GC tracking
            self.gc_stats["collections_triggered"] += 1
            self.gc_stats["last_collection"] = datetime.utcnow()

            memory_freed = before_stats.rss_mb - after_stats.rss_mb

            result = {
                "gc_triggered": True,
                "reason": "High memory usage" if not force else "Forced",
                "before_memory_mb": round(before_stats.rss_mb, 2),
                "after_memory_mb": round(after_stats.rss_mb, 2),
                "memory_freed_mb": round(memory_freed, 2),
                "gc_stats": gc_stats
            }

            if memory_freed > 0:
                print(f"🧹 GC freed {memory_freed:.1f}MB")

            return result

        except Exception as e:
            return {
                "gc_triggered": True,
                "reason": "High memory usage" if not force else "Forced",
                "error": str(e),
                "before_memory_mb": before_stats.rss_mb,
                "after_memory_mb": before_stats.rss_mb
            }

    def register_object(self, obj: Any) -> bool:
        """
        Register an object for memory tracking.

        Args:
            obj: Object to track

        Returns:
            True if object was registered, False otherwise
        """
        try:
            self.tracked_objects.add(obj)
            return True
        except Exception:
            return False

    def get_memory_trend(self, minutes: int = 60) -> Dict[str, Any]:
        """
        Get memory usage trend over time.

        Args:
            minutes: Number of minutes to look back

        Returns:
            Dictionary with memory trend information
        """
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)

        with self._lock:
            recent_stats = [
                stat for stat in self.memory_stats
                if stat.timestamp >= cutoff_time
            ]

        if not recent_stats:
            return {"error": "No recent memory data available"}

        # Calculate trend
        memory_values = [stat.rss_mb for stat in recent_stats]

        return {
            "period_minutes": minutes,
            "data_points": len(recent_stats),
            "current_mb": memory_values[-1] if memory_values else 0,
            "min_mb": min(memory_values),
            "max_mb": max(memory_values),
            "avg_mb": sum(memory_values) / len(memory_values),
            "trend": "increasing" if memory_values[-1] > memory_values[0] else "decreasing",
            "memory_change_mb": memory_values[-1] - memory_values[0] if memory_values else 0
        }

    def get_cleanup_recommendations(self) -> List[str]:
        """
        Get recommendations for memory cleanup.

        Returns:
            List of cleanup recommendations
        """
        recommendations = []
        current_stats = self.get_memory_usage()

        # Check memory usage percentage
        if current_stats.percent > 80:
            recommendations.append("High memory usage detected - consider triggering GC")

        # Check if close to limit
        if current_stats.rss_mb > self.memory_limit_mb * 0.9:
            recommendations.append(f"Memory usage ({current_stats.rss_mb:.1f}MB) approaching limit ({self.memory_limit_mb}MB)")

        # Check tracked objects
        if current_stats.tracked_objects > 1000:
            recommendations.append("High number of tracked objects - consider cleanup")

        # Check available system memory
        if current_stats.available_mb < 512:  # Less than 512MB available
            recommendations.append("Low system memory available - may impact performance")

        return recommendations

    def _monitor_memory(self):
        """Background thread for monitoring memory usage."""
        while not self._stop_monitoring.wait(self.check_interval):
            try:
                stats = self.get_memory_usage()

                with self._lock:
                    self.memory_stats.append(stats)
                    # Keep only last 1000 records
                    if len(self.memory_stats) > 1000:
                        self.memory_stats = self.memory_stats[-1000:]

                # Check if we need to trigger GC
                if not self.check_memory_usage():
                    self.trigger_gc_if_needed()

            except Exception as e:
                print(f"Memory monitoring error: {e}")

    @contextmanager
    def memory_managed_operation(self, description: str = "operation"):
        """
        Context manager for memory-managed operations.

        Args:
            description: Description of the operation for logging

        Usage:
            with memory_manager.memory_managed_operation("large_data_processing"):
                # Your operation here
                pass
        """
        before_stats = self.get_memory_usage()

        try:
            yield
        finally:
            after_stats = self.get_memory_usage()
            memory_change = after_stats.rss_mb - before_stats.rss_mb

            if abs(memory_change) > 10:  # Log changes > 10MB
                print(f"📊 {description}: Memory change {memory_change:+.1f}MB")

    def force_cleanup(self) -> Dict[str, Any]:
        """
        Force comprehensive cleanup.

        Returns:
            Dictionary with cleanup results
        """
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "actions": []
        }

        # Trigger garbage collection
        gc_result = self.trigger_gc_if_needed(force=True)
        results["actions"].append(gc_result)

        # Clear memory stats if too many
        with self._lock:
            if len(self.memory_stats) > 500:
                old_count = len(self.memory_stats)
                self.memory_stats = self.memory_stats[-100:]  # Keep last 100
                results["actions"].append({
                    "action": "memory_stats_cleanup",
                    "removed_entries": old_count - 100
                })

        return results


# Global memory manager instance
memory_manager = MemoryManager()


# Context manager decorator
def memory_managed(description: str = "operation"):
    """
    Decorator for memory-managed functions.

    Usage:
        @memory_managed("data_processing")
        async def process_large_data():
            # Your implementation
            pass
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            with memory_manager.memory_managed_operation(description):
                return await func(*args, **kwargs)
        return wrapper
    return decorator


# Convenience functions
def get_memory_usage() -> MemoryStats:
    """Get current memory usage statistics."""
    return memory_manager.get_memory_usage()


def check_memory_usage() -> bool:
    """Check if memory usage is within limits."""
    return memory_manager.check_memory_usage()


def trigger_gc_if_needed(force: bool = False) -> Dict[str, Any]:
    """Trigger garbage collection if needed."""
    return memory_manager.trigger_gc_if_needed(force)


def register_object(obj: Any) -> bool:
    """Register an object for memory tracking."""
    return memory_manager.register_object(obj)


def get_memory_trend(minutes: int = 60) -> Dict[str, Any]:
    """Get memory usage trend."""
    return memory_manager.get_memory_trend(minutes)


def get_cleanup_recommendations() -> List[str]:
    """Get memory cleanup recommendations."""
    return memory_manager.get_cleanup_recommendations()