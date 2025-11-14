from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import json
import os
import sys

# Fix import by adding current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import analytics service - FIXED import
try:
    # Direct import from same directory
    from analytics import analytics_service
    print("✅ Successfully imported analytics_service")
except ImportError as e:
    print(f"❌ Failed to import analytics_service: {e}")
    # Create mock service as fallback
    class MockAnalyticsService:
        def record_prediction(self, prediction, risk_score):
            print(f"Mock: Recording {prediction} with score {risk_score}")
        def get_analytics(self):
            return {
                "status": "mock_service", 
                "message": "Real analytics service not available",
                "system_health": {"status": "healthy", "uptime_seconds": 0},
                "prediction_analytics": {"total_predictions": 0}
            }
    analytics_service = MockAnalyticsService()

router = APIRouter()

# Simple in-memory storage for analytics
prediction_history = []

@router.get("/")
async def analytics_dashboard():
    """Analytics dashboard root"""
    return {
        "message": "Analytics Dashboard - WORKING!",
        "endpoints": {
            "health": "GET /analytics/health",
            "predictions_summary": "GET /analytics/predictions/summary", 
            "stats": "GET /analytics/stats",
            "system_analytics": "GET /analytics/system"
        },
        "status": "active",
        "total_predictions": len(prediction_history)
    }

@router.get("/health")
async def analytics_health():
    """Analytics service health check"""
    return {
        "status": "healthy",
        "service": "analytics",
        "version": "1.0",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@router.get("/predictions/summary")
async def predictions_summary():
    """Get summary of prediction statistics"""
    if prediction_history:
        risk_scores = [p.get('risk_score', 0) for p in prediction_history]
        return {
            "total_predictions": len(prediction_history),
            "average_risk_score": sum(risk_scores) / len(risk_scores),
            "high_risk_predictions": len([score for score in risk_scores if score > 0.7]),
            "low_risk_predictions": len([score for score in risk_scores if score < 0.3]),
            "recent_predictions": prediction_history[-5:] if len(prediction_history) > 5 else prediction_history
        }
    else:
        return {
            "total_predictions": 0,
            "average_risk_score": 0,
            "high_risk_predictions": 0,
            "low_risk_predictions": 0,
            "message": "No predictions recorded yet"
        }

@router.get("/stats")
async def system_stats():
    """Get system statistics"""
    return {
        "system": "Fraud Detection API",
        "version": "Week 4", 
        "status": "operational",
        "analytics_enabled": True,
        "features": ["prediction_tracking", "health_monitoring", "real-time_stats"]
    }

@router.get("/system")
async def system_analytics():
    """Get comprehensive system analytics"""
    return analytics_service.get_analytics()

@router.post("/record_prediction")
async def record_prediction(prediction_data: Dict[str, Any]):
    """Record a prediction for analytics"""
    prediction_history.append(prediction_data)
    
    # Record in analytics service
    risk_score = prediction_data.get('risk_score', 0.5)
    prediction_type = "Fraud" if risk_score > 0.7 else "Legitimate"
    analytics_service.record_prediction(prediction_type, risk_score)
    
    return {
        "status": "recorded", 
        "prediction_id": len(prediction_history),
        "message": "Prediction recorded successfully"
    }

print("✅ Analytics routes loaded successfully!")