import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json

class AnalyticsService:
    def __init__(self):
        self.request_count = 0
        self.prediction_stats = {
            "total_predictions": 0,
            "fraud_predictions": 0,
            "legitimate_predictions": 0,
            "average_risk_score": 0,
            "requests_by_hour": {}
        }
        self.start_time = datetime.now()

    def record_prediction(self, prediction: str, risk_score: float):
        """Record prediction statistics"""
        self.request_count += 1
        self.prediction_stats["total_predictions"] += 1

        if prediction == "Fraud":
            self.prediction_stats["fraud_predictions"] += 1
        else:
            self.prediction_stats["legitimate_predictions"] += 1

        # Update average risk score
        current_avg = self.prediction_stats["average_risk_score"]
        total = self.prediction_stats["total_predictions"]
        self.prediction_stats["average_risk_score"] = (
            (current_avg * (total - 1)) + risk_score
        ) / total

        # Record hour of request
        current_hour = datetime.now().strftime("%H:00")
        if current_hour not in self.prediction_stats["requests_by_hour"]:
            self.prediction_stats["requests_by_hour"][current_hour] = 0
        self.prediction_stats["requests_by_hour"][current_hour] += 1

    def get_analytics(self) -> Dict[str, Any]:
        """Get comprehensive analytics data"""
        uptime = datetime.now() - self.start_time
        fraud_rate = 0
        if self.prediction_stats["total_predictions"] > 0:
            fraud_rate = (
                self.prediction_stats["fraud_predictions"] /
                self.prediction_stats["total_predictions"] * 100
            )
        
        return {
            "system_health": {
                "status": "healthy",
                "uptime_seconds": int(uptime.total_seconds()),
                "start_time": self.start_time.isoformat(),
                "total_requests": self.request_count
            },
            "prediction_analytics": {
                **self.prediction_stats,
                "fraud_rate_percentage": round(fraud_rate, 2),
                "legitimate_rate_percentage": round(100 - fraud_rate, 2)
            },
            "performance": {
                "requests_per_minute": self.request_count / max(1, uptime.total_seconds() / 60),
                "most_active_hour": self._get_most_active_hour()
            }
        }

    def _get_most_active_hour(self) -> str:
        """Get the hour with most requests"""
        if not self.prediction_stats["requests_by_hour"]:
            return "No data"
        return max(
            self.prediction_stats["requests_by_hour"].items(),
            key=lambda x: x[1]
        )[0]

# Global analytics instance
analytics_service = AnalyticsService()