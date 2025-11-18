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
    """Get summary of XGBoost prediction statistics from real database claims"""
    import sqlite3
    from datetime import datetime, timedelta
    
    try:
        conn = sqlite3.connect('claims.db')
        cursor = conn.cursor()
        
        # Get recent predictions from database
        cursor.execute("""
            SELECT 
                id,
                patient_age,
                diagnosis,
                claimed_amount,
                risk_score,
                risk_category,
                prediction,
                created_at,
                status
            FROM claims
            ORDER BY created_at DESC
            LIMIT 50
        """)
        
        claims = cursor.fetchall()
        conn.close()
        
        if claims:
            risk_scores = [float(claim[4] or 0) for claim in claims]
            
            # Get last 5 for recent predictions
            recent = []
            for claim in claims[:5]:
                recent.append({
                    "claim_id": claim[0],
                    "patient_age": claim[1],
                    "diagnosis": claim[2],
                    "claimed_amount": claim[3],
                    "risk_score": round(float(claim[4] or 0) * 100, 1),  # Convert to percentage
                    "risk_category": claim[5],
                    "prediction": claim[6],
                    "created_at": claim[7],
                    "status": claim[8]
                })
            
            return {
                "data_source": "Real Database Claims (XGBoost Analyzed)",
                "total_predictions": len(claims),
                "average_risk_score": round(sum(risk_scores) / len(risk_scores) * 100, 2),
                "high_risk_predictions": len([score for score in risk_scores if score >= 0.7]),
                "medium_risk_predictions": len([score for score in risk_scores if 0.3 <= score < 0.7]),
                "low_risk_predictions": len([score for score in risk_scores if score < 0.3]),
                "recent_predictions": recent
            }
        else:
            return {
                "data_source": "Real Database Claims",
                "total_predictions": 0,
                "average_risk_score": 0,
                "high_risk_predictions": 0,
                "medium_risk_predictions": 0,
                "low_risk_predictions": 0,
                "message": "No claims found in database yet. Submit your first claim to see analysis!"
            }
    except Exception as e:
        return {
            "error": str(e),
            "message": "Failed to fetch prediction summary from database"
        }

@router.get("/stats")
async def system_stats():
    """Get real-time statistics from database claims analyzed by XGBoost model"""
    import sqlite3
    from datetime import datetime, timedelta
    
    try:
        conn = sqlite3.connect('claims.db')
        cursor = conn.cursor()
        
        # Get all claims from last 30 days
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        cursor.execute("""
            SELECT 
                COUNT(*) as total_claims,
                AVG(risk_score) as avg_risk_score,
                SUM(CASE WHEN risk_score >= 0.7 THEN 1 ELSE 0 END) as high_risk_count,
                SUM(CASE WHEN risk_score >= 0.3 AND risk_score < 0.7 THEN 1 ELSE 0 END) as medium_risk_count,
                SUM(CASE WHEN risk_score < 0.3 THEN 1 ELSE 0 END) as low_risk_count,
                SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved_count,
                SUM(CASE WHEN status = 'flagged' THEN 1 ELSE 0 END) as flagged_count,
                SUM(claimed_amount) as total_claimed_amount,
                risk_category
            FROM claims
            WHERE created_at >= ?
            GROUP BY risk_category
        """, (thirty_days_ago,))
        
        results = cursor.fetchall()
        
        # Aggregate totals
        total_claims = 0
        total_risk = 0
        high_risk = 0
        medium_risk = 0
        low_risk = 0
        approved = 0
        flagged = 0
        total_amount = 0
        category_breakdown = {}
        
        for row in results:
            total_claims += row[0] or 0
            total_risk += (row[1] or 0) * (row[0] or 0)  # Weighted average
            high_risk += row[2] or 0
            medium_risk += row[3] or 0
            low_risk += row[4] or 0
            approved += row[5] or 0
            flagged += row[6] or 0
            total_amount += row[7] or 0
            category = row[8] or 'Unknown'
            category_breakdown[category] = row[0] or 0
        
        avg_risk_score = (total_risk / total_claims) if total_claims > 0 else 0
        
        conn.close()
        
        return {
            "system": "Fraud Detection API - XGBoost Analysis",
            "version": "Production v2.0", 
            "status": "operational",
            "data_source": "Real Database Claims (Last 30 Days)",
            "model": "XGBoost Classifier",
            "total_claims": total_claims,
            "average_risk_score": round(avg_risk_score * 100, 2),  # Convert to percentage
            "risk_distribution": {
                "high_risk": high_risk,
                "medium_risk": medium_risk,
                "low_risk": low_risk
            },
            "category_breakdown": category_breakdown,
            "claim_status": {
                "approved": approved,
                "flagged": flagged,
                "pending": total_claims - approved - flagged
            },
            "financial": {
                "total_claimed_amount": round(total_amount, 2),
                "average_claim_amount": round(total_amount / total_claims, 2) if total_claims > 0 else 0
            },
            "analytics_enabled": True,
            "features": ["xgboost_predictions", "real_time_analysis", "database_integration"]
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": "Failed to fetch real claim statistics",
            "system": "Fraud Detection API",
            "status": "error"
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