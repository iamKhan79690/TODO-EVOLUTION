"""
Task Analysis Service.

Analyzes user task patterns, behaviors, and productivity metrics
to provide intelligent insights and suggestions.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, Counter

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func

from ..models import Task, Message, Conversation
import structlog

logger = structlog.get_logger(__name__)


class TaskAnalysisService:
    """Service for analyzing user task patterns and productivity."""

    def __init__(self, db: Session, user_id: int):
        """
        Initialize the task analysis service.

        Args:
            db: Database session
            user_id: ID of the authenticated user
        """
        self.db = db
        self.user_id = user_id

    async def analyze_productivity_patterns(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze user productivity patterns over time.

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary containing productivity insights
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)

            # Get tasks created in the analysis period
            tasks = self.db.query(Task).filter(
                and_(
                    Task.user_id == self.user_id,
                    Task.created_at >= start_date
                )
            ).all()

            if not tasks:
                return self._get_empty_analysis(days)

            # Basic metrics
            total_tasks = len(tasks)
            completed_tasks = len([t for t in tasks if t.is_completed])
            completion_rate = completed_tasks / total_tasks if total_tasks > 0 else 0

            # Time-based analysis
            daily_creation = self._analyze_daily_task_creation(tasks)
            completion_time = self._analyze_completion_times(tasks)

            # Priority analysis
            priority_patterns = self._analyze_priority_patterns(tasks)

            # Productivity insights
            insights = await self._generate_productivity_insights(
                tasks, daily_creation, completion_time, priority_patterns
            )

            return {
                "analysis_period": f"{days} days",
                "summary": {
                    "total_tasks": total_tasks,
                    "completed_tasks": completed_tasks,
                    "completion_rate": round(completion_rate, 2),
                    "active_tasks": total_tasks - completed_tasks
                },
                "daily_patterns": daily_creation,
                "completion_analysis": completion_time,
                "priority_patterns": priority_patterns,
                "insights": insights,
                "recommendations": await self._generate_recommendations(tasks, insights)
            }

        except Exception as e:
            logger.error("Failed to analyze productivity patterns",
                        user_id=self.user_id,
                        days=days,
                        error=str(e))
            return {"error": str(e)}

    def _get_empty_analysis(self, days: int) -> Dict[str, Any]:
        """Return empty analysis structure."""
        return {
            "analysis_period": f"{days} days",
            "summary": {
                "total_tasks": 0,
                "completed_tasks": 0,
                "completion_rate": 0,
                "active_tasks": 0
            },
            "daily_patterns": {},
            "completion_analysis": {},
            "priority_patterns": {},
            "insights": ["No task data available for analysis"],
            "recommendations": ["Start creating tasks to see productivity insights"]
        }

    def _analyze_daily_task_creation(self, tasks: List[Task]) -> Dict[str, Any]:
        """Analyze daily task creation patterns."""
        daily_counts = defaultdict(int)
        weekday_counts = defaultdict(int)
        hour_counts = defaultdict(int)

        for task in tasks:
            date_key = task.created_at.strftime('%Y-%m-%d')
            weekday = task.created_at.strftime('%A')
            hour = task.created_at.hour

            daily_counts[date_key] += 1
            weekday_counts[weekday] += 1
            hour_counts[hour] += 1

        # Find most productive day and hour
        most_productive_weekday = max(weekday_counts.items(), key=lambda x: x[1]) if weekday_counts else (None, 0)
        most_productive_hour = max(hour_counts.items(), key=lambda x: x[1]) if hour_counts else (None, 0)

        return {
            "daily_creation": dict(daily_counts),
            "weekday_patterns": dict(weekday_counts),
            "hourly_patterns": dict(hour_counts),
            "most_productive_weekday": most_productive_weekday[0],
            "most_productive_hour": most_productive_hour[0],
            "average_tasks_per_day": len(tasks) / max(len(set(t.created_at.date() for t in tasks)), 1)
        }

    def _analyze_completion_times(self, tasks: List[Task]) -> Dict[str, Any]:
        """Analyze task completion times."""
        completed_tasks = [t for t in tasks if t.is_completed and t.updated_at]

        if not completed_tasks:
            return {"average_completion_hours": None, "completion_distribution": {}}

        completion_times = []
        completion_hours = defaultdict(int)

        for task in completed_tasks:
            completion_time = task.updated_at - task.created_at
            hours_to_complete = completion_time.total_seconds() / 3600
            completion_times.append(hours_to_complete)

            # Categorize completion time
            if hours_to_complete < 1:
                category = "under_1_hour"
            elif hours_to_complete < 24:
                category = "same_day"
            elif hours_to_complete < 168:  # 7 days
                category = "within_week"
            else:
                category = "over_week"

            completion_hours[category] += 1

        return {
            "average_completion_hours": round(sum(completion_times) / len(completion_times), 1),
            "median_completion_hours": round(sorted(completion_times)[len(completion_times)//2], 1),
            "completion_distribution": dict(completion_hours),
            "fastest_completion": min(completion_times),
            "slowest_completion": max(completion_times)
        }

    def _analyze_priority_patterns(self, tasks: List[Task]) -> Dict[str, Any]:
        """Analyze priority assignment and completion patterns."""
        priority_data = defaultdict(lambda: {"created": 0, "completed": 0})

        for task in tasks:
            if task.priority:
                priority = task.priority.value
                priority_data[priority]["created"] += 1
                if task.is_completed:
                    priority_data[priority]["completed"] += 1

        # Calculate completion rates by priority
        priority_analysis = {}
        for priority, data in priority_data.items():
            completion_rate = data["completed"] / data["created"] if data["created"] > 0 else 0
            priority_analysis[priority] = {
                "created": data["created"],
                "completed": data["completed"],
                "completion_rate": round(completion_rate, 2)
            }

        return {
            "priority_distribution": dict(priority_data),
            "priority_completion_rates": priority_analysis,
            "most_used_priority": max(priority_data.items(), key=lambda x: x[1]["created"])[0] if priority_data else None
        }

    async def _generate_productivity_insights(
        self,
        tasks: List[Task],
        daily_creation: Dict[str, Any],
        completion_time: Dict[str, Any],
        priority_patterns: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable productivity insights."""
        insights = []

        # Completion rate insights
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.is_completed])
        completion_rate = completed_tasks / total_tasks if total_tasks > 0 else 0

        if completion_rate > 0.8:
            insights.append("Excellent completion rate! You're very consistent.")
        elif completion_rate > 0.6:
            insights.append("Good completion rate. Consider breaking down larger tasks.")
        elif completion_rate < 0.4:
            insights.append("Consider setting more realistic goals or breaking tasks into smaller steps.")

        # Task creation patterns
        most_productive_weekday = daily_creation.get("most_productive_weekday")
        if most_productive_weekday:
            insights.append(f"You're most productive on {most_productive_weekday}s. Plan important tasks then.")

        # Completion time insights
        avg_completion = completion_time.get("average_completion_hours")
        if avg_completion and avg_completion > 168:  # More than a week
            insights.append("Tasks are taking longer than a week to complete. Consider smaller milestones.")

        # Priority insights
        most_used_priority = priority_patterns.get("most_used_priority")
        if most_used_priority == "MEDIUM":
            insights.append("You mostly use MEDIUM priority. Consider varying priorities for better organization.")
        elif most_used_priority == "LOW":
            insights.append("Most tasks are LOW priority. Ensure important tasks get higher priority.")

        # Task volume insights
        avg_daily = daily_creation.get("average_tasks_per_day", 0)
        if avg_daily > 5:
            insights.append("You create many tasks daily. Ensure they're actionable and specific.")
        elif avg_daily < 1:
            insights.append("Consider creating more specific, actionable tasks.")

        return insights

    async def _generate_recommendations(
        self,
        tasks: List[Task],
        insights: List[str]
    ) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []

        # Task management recommendations
        active_tasks = len([t for t in tasks if not t.is_completed])
        if active_tasks > 15:
            recommendations.append("Focus on completing existing tasks before creating new ones.")
        elif active_tasks < 3:
            recommendations.append("Consider adding more specific, actionable tasks to maintain momentum.")

        # Time management recommendations
        completed_tasks = [t for t in tasks if t.is_completed and t.updated_at]
        if completed_tasks:
            avg_completion_time = sum(
                ((t.updated_at - t.created_at).total_seconds() / 3600) for t in completed_tasks
            ) / len(completed_tasks)

            if avg_completion_time > 72:  # 3 days
                recommendations.append("Break larger tasks into smaller, more manageable pieces.")

        # Priority recommendations
        high_priority_incomplete = len([
            t for t in tasks if not t.is_completed and t.priority and t.priority.value in ["HIGH", "URGENT"]
        ])
        if high_priority_incomplete > 5:
            recommendations.append("Address high-priority tasks first to reduce overwhelm.")

        # Consistency recommendations
        completion_rate = len(completed_tasks) / len(tasks) if tasks else 0
        if completion_rate > 0.8:
            recommendations.append("Great consistency! Consider setting more challenging goals.")
        elif completion_rate < 0.5:
            recommendations.append("Review and adjust task expectations to improve completion rates.")

        return recommendations

    async def analyze_task_categories(self) -> Dict[str, Any]:
        """Analyze task categories based on keywords and patterns."""
        try:
            # Get recent tasks
            tasks = self.db.query(Task).filter(
                Task.user_id == self.user_id
            ).order_by(desc(Task.created_at)).limit(100).all()

            if not tasks:
                return {"categories": {}, "insights": []}

            # Simple keyword-based categorization
            category_keywords = {
                "Work": ["work", "project", "meeting", "deadline", "client", "office", "business"],
                "Personal": ["personal", "home", "family", "personal", "private", "life"],
                "Health": ["health", "exercise", "gym", "doctor", "medical", "fitness", "workout"],
                "Learning": ["learn", "study", "course", "book", "reading", "education", "training"],
                "Finance": ["money", "bill", "payment", "budget", "finance", "expense", "saving"],
                "Shopping": ["buy", "shop", "purchase", "store", "grocery", "shopping", "order"],
                "Maintenance": ["fix", "repair", "maintenance", "update", "clean", "organize"]
            }

            task_categories = defaultdict(list)
            uncategorized_tasks = []

            for task in tasks:
                title_lower = task.title.lower()
                desc_lower = (task.description or "").lower()

                categorized = False
                for category, keywords in category_keywords.items():
                    if any(keyword in title_lower or keyword in desc_lower for keyword in keywords):
                        task_categories[category].append(task)
                        categorized = True
                        break

                if not categorized:
                    uncategorized_tasks.append(task)

            # Calculate category statistics
            category_stats = {}
            for category, category_tasks in task_categories.items():
                completed = len([t for t in category_tasks if t.is_completed])
                category_stats[category] = {
                    "count": len(category_tasks),
                    "completed": completed,
                    "completion_rate": round(completed / len(category_tasks), 2) if category_tasks else 0,
                    "examples": [{"title": t.title, "id": t.id} for t in category_tasks[:3]]
                }

            # Generate insights
            insights = []
            if category_stats:
                best_category = max(category_stats.items(), key=lambda x: x[1]["completion_rate"])
                insights.append(f"Your best completion rate is in {best_category[0]} tasks ({best_category[1]['completion_rate']:.0%}).")

                if uncategorized_tasks:
                    insights.append(f"{len(uncategorized_tasks)} tasks could benefit from better categorization.")

            return {
                "categories": category_stats,
                "uncategorized_count": len(uncategorized_tasks),
                "insights": insights,
                "recommendations": await self._generate_category_recommendations(category_stats, uncategorized_tasks)
            }

        except Exception as e:
            logger.error("Failed to analyze task categories",
                        user_id=self.user_id,
                        error=str(e))
            return {"error": str(e)}

    async def _generate_category_recommendations(
        self,
        category_stats: Dict[str, Any],
        uncategorized_tasks: List[Task]
    ) -> List[str]:
        """Generate recommendations based on category analysis."""
        recommendations = []

        # Category-specific recommendations
        if "Work" in category_stats and category_stats["Work"]["completion_rate"] < 0.5:
            recommendations.append("Consider breaking work tasks into smaller, more manageable steps.")

        if "Health" in category_stats and category_stats["Health"]["count"] < 3:
            recommendations.append("Add more health and wellness goals to maintain balance.")

        if len(uncategorized_tasks) > 10:
            recommendations.append("Use clearer, more descriptive task titles to improve organization.")

        return recommendations