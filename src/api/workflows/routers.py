from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
import sqlite3
from datetime import datetime, timedelta
import uuid
import sys
import os

# Add parent directory to path to import model service
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .models import (
    ClaimCreate, ClaimResponse, ClaimDetailResponse, ClaimStatusUpdate,
    ClaimStatusHistoryResponse, CompanyDashboardStats, ClaimStatus, ClaimStage
)
from ..auth.routers import get_current_user, require_role
from ..auth.models import TokenData
from ..database import get_db_connection

router = APIRouter()

# Import model service for predictions
try:
    from ..model_service import FraudModelService
    model_service = FraudModelService()
except Exception as e:
    print(f"Warning: Could not load model service: {e}")
    model_service = None

@router.post("/claims", response_model=ClaimResponse)
async def create_claim(
    claim_data: ClaimCreate,
    current_user: TokenData = Depends(get_current_user)
):
    """Create a new claim (customer only)"""
    if current_user.role not in ["customer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers can create claims"
        )
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        claim_id = str(uuid.uuid4())
        
        # Calculate length of stay
        try:
            admission = datetime.strptime(claim_data.admission_date, '%Y-%m-%d')
            discharge = datetime.strptime(claim_data.discharge_date, '%Y-%m-%d')
            length_of_stay = (discharge - admission).days
        except:
            length_of_stay = 1
        
        # Run AI prediction if model is available
        risk_score = None
        risk_category = None
        prediction = None
        explanation = []
        lime_explanation = []
        model_version = None
        
        if model_service:
            try:
                prediction_result = model_service.predict({
                    'patient_age': claim_data.patient_age,
                    'diagnosis': claim_data.diagnosis,
                    'admission_date': claim_data.admission_date,
                    'discharge_date': claim_data.discharge_date,
                    'claimed_amount': claim_data.claimed_amount,
                    'length_of_stay': length_of_stay
                })
                
                risk_score = prediction_result.get('risk_score')
                risk_category = prediction_result.get('risk_category')
                prediction = prediction_result.get('prediction')
                explanation = prediction_result.get('explanation', [])
                lime_explanation = prediction_result.get('lime_explanation', [])
                model_version = prediction_result.get('model_version')
            except Exception as e:
                print(f"Prediction error: {e}")
        
        # Determine initial status based on risk
        if risk_score and risk_score >= 70:
            initial_status = ClaimStatus.MANUAL_REVIEW.value
        else:
            initial_status = ClaimStatus.UNDER_REVIEW.value
        
        # Insert claim
        import json
        cursor.execute("""
            INSERT INTO claims (
                id, user_id, status, current_stage, patient_age, diagnosis,
                admission_date, discharge_date, claimed_amount, description,
                risk_score, risk_category, prediction, explanation,
                lime_explanation, model_version, length_of_stay,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            claim_id, current_user.user_id, initial_status, ClaimStage.AI_PROCESSING.value,
            claim_data.patient_age, claim_data.diagnosis, claim_data.admission_date,
            claim_data.discharge_date, claim_data.claimed_amount, claim_data.description,
            risk_score, risk_category, prediction, str(explanation),
            json.dumps(lime_explanation), model_version, length_of_stay,
            datetime.utcnow(), datetime.utcnow()
        ))
        
        # Add status history
        cursor.execute("""
            INSERT INTO claim_status_history (claim_id, status, changed_by, changed_at)
            VALUES (?, ?, ?, ?)
        """, (claim_id, initial_status, current_user.user_id, datetime.utcnow()))
        
        conn.commit()
        
        # Fetch created claim
        cursor.execute("""
            SELECT id, user_id, status, current_stage, patient_age, diagnosis,
                   claimed_amount, risk_score, risk_category, prediction,
                   created_at, updated_at
            FROM claims WHERE id = ?
        """, (claim_id,))
        
        claim = cursor.fetchone()
        
        return ClaimResponse(
            id=claim[0],
            user_id=claim[1],
            status=claim[2],
            current_stage=claim[3],
            patient_age=claim[4],
            diagnosis=claim[5],
            claimed_amount=claim[6],
            risk_score=claim[7],
            risk_category=claim[8],
            prediction=claim[9],
            created_at=claim[10],
            updated_at=claim[11]
        )
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create claim: {str(e)}"
        )
    finally:
        conn.close()


@router.get('/company/dashboard/approval-rate')
async def get_approval_rate(
    days: int = 30,
    current_user: TokenData = Depends(require_role(["company_admin", "company_staff"]))
):
    """Return approval rate for the last `days` and comparison to previous period"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        end = datetime.utcnow()
        start = end - timedelta(days=days)
        prev_start = start - timedelta(days=days)
        prev_end = start

        # Current period
        cursor.execute("SELECT COUNT(*) FROM claims WHERE created_at >= ? AND created_at <= ?", (start, end))
        total = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM claims WHERE status = 'approved' AND created_at >= ? AND created_at <= ?", (start, end))
        approved = cursor.fetchone()[0] or 0

        # Previous period
        cursor.execute("SELECT COUNT(*) FROM claims WHERE created_at >= ? AND created_at < ?", (prev_start, prev_end))
        prev_total = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM claims WHERE status = 'approved' AND created_at >= ? AND created_at < ?", (prev_start, prev_end))
        prev_approved = cursor.fetchone()[0] or 0

        approval_rate = (approved / total * 100) if total > 0 else 0
        prev_rate = (prev_approved / prev_total * 100) if prev_total > 0 else 0

        trend = approval_rate - prev_rate

        return {
            "approval_rate": round(approval_rate, 2),
            "previous_rate": round(prev_rate, 2),
            "trend": round(trend, 2),
            "total": total
        }
    finally:
        conn.close()


@router.get('/company/dashboard/total-value')
async def get_total_value(
    days: int = 30,
    current_user: TokenData = Depends(require_role(["company_admin", "company_staff"]))
):
    """Return total claimed value for the last `days` and comparison to previous period"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        end = datetime.utcnow()
        start = end - timedelta(days=days)
        prev_start = start - timedelta(days=days)
        prev_end = start

        cursor.execute("SELECT SUM(claimed_amount) FROM claims WHERE created_at >= ? AND created_at <= ?", (start, end))
        total_value = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(claimed_amount) FROM claims WHERE created_at >= ? AND created_at < ?", (prev_start, prev_end))
        prev_value = cursor.fetchone()[0] or 0

        trend = total_value - prev_value

        return {
            "total_value": round(total_value, 2),
            "previous_value": round(prev_value, 2),
            "trend": round(trend, 2)
        }
    finally:
        conn.close()


@router.get('/company/dashboard/avg-processing-time')
async def get_avg_processing_time(
    days: int = 90,
    current_user: TokenData = Depends(require_role(["company_admin", "company_staff"]))
):
    """Average days from submission to final decision (approved/rejected) for last `days` and comparison"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        end = datetime.utcnow()
        start = end - timedelta(days=days)
        prev_start = start - timedelta(days=days)
        prev_end = start

        # Current period - only claims that reached final status
        cursor.execute("""
            SELECT AVG( (julianday(h.changed_at) - julianday(c.created_at)) ) * 24 * 60 * 60
            FROM claim_status_history h
            JOIN claims c ON h.claim_id = c.id
            WHERE h.status IN ('approved','rejected')
              AND h.changed_at >= ? AND h.changed_at <= ?
        """, (start, end))
        avg_seconds = cursor.fetchone()[0] or 0

        cursor.execute("""
            SELECT AVG( (julianday(h.changed_at) - julianday(c.created_at)) ) * 24 * 60 * 60
            FROM claim_status_history h
            JOIN claims c ON h.claim_id = c.id
            WHERE h.status IN ('approved','rejected')
              AND h.changed_at >= ? AND h.changed_at < ?
        """, (prev_start, prev_end))
        prev_avg_seconds = cursor.fetchone()[0] or 0

        # Convert seconds to days
        avg_days = (avg_seconds / (60 * 60 * 24)) if avg_seconds else 0
        prev_avg_days = (prev_avg_seconds / (60 * 60 * 24)) if prev_avg_seconds else 0

        trend = avg_days - prev_avg_days

        return {
            "avg_days": round(avg_days, 2),
            "previous_avg_days": round(prev_avg_days, 2),
            "trend": round(trend, 2)
        }
    finally:
        conn.close()

@router.get("/claims", response_model=List[ClaimResponse])
async def get_user_claims(
    current_user: TokenData = Depends(get_current_user)
):
    """Get all claims for current user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, user_id, status, current_stage, patient_age, diagnosis,
                   claimed_amount, risk_score, risk_category, prediction,
                   created_at, updated_at
            FROM claims
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (current_user.user_id,))
        
        claims = cursor.fetchall()
        results = []
        for claim in claims:
            claim_id = claim[0]
            # Fetch documents for this claim from documents table
            cursor.execute("""
                SELECT id, filename, filepath, document_type, file_size, uploaded_by, uploaded_at, description
                FROM documents WHERE claim_id = ?
                ORDER BY uploaded_at DESC
            """, (claim_id,))
            docs = cursor.fetchall()
            documents = [
                {
                    "id": d[0],
                    "filename": d[1],
                    "filepath": d[2],
                    "document_type": d[3],
                    "file_size": d[4],
                    "uploaded_by": d[5],
                    "uploaded_at": d[6],
                    "description": d[7]
                }
                for d in docs
            ]

            results.append(ClaimResponse(
                id=claim[0],
                user_id=claim[1],
                status=claim[2],
                current_stage=claim[3],
                patient_age=claim[4],
                diagnosis=claim[5],
                claimed_amount=claim[6],
                risk_score=claim[7],
                risk_category=claim[8],
                prediction=claim[9],
                created_at=claim[10],
                updated_at=claim[11],
                documents=documents
            ))

        return results
        
    finally:
        conn.close()

@router.get("/claims/{claim_id}", response_model=ClaimDetailResponse)
async def get_claim_detail(
    claim_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Get detailed information about a claim"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Fetch claim with user info
        cursor.execute("""
            SELECT c.id, c.user_id, c.status, c.current_stage, c.patient_age, c.diagnosis,
                   c.admission_date, c.discharge_date, c.claimed_amount, c.description,
                   c.risk_score, c.risk_category, c.prediction, c.explanation,
                   c.lime_explanation, c.model_version, c.length_of_stay,
                   c.created_at, c.updated_at, u.full_name
            FROM claims c
            LEFT JOIN users u ON c.user_id = u.id
            WHERE c.id = ?
        """, (claim_id,))
        
        claim = cursor.fetchone()
        
        if not claim:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Claim not found"
            )
        
        # Check access
        if current_user.role == "customer" and claim[1] != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this claim"
            )
        
        # Fetch status history
        cursor.execute("""
            SELECT h.id, h.claim_id, h.status, h.notes, h.changed_by,
                   u.full_name, h.changed_at
            FROM claim_status_history h
            JOIN users u ON h.changed_by = u.id
            WHERE h.claim_id = ?
            ORDER BY h.changed_at DESC
        """, (claim_id,))
        
        history = cursor.fetchall()
        status_history = [
            {
                "id": h[0],
                "status": h[2],
                "notes": h[3],
                "changed_by": h[4],
                "changed_by_name": h[5],
                "changed_at": h[6]
            }
            for h in history
        ]
        
        # Parse explanation
        import ast
        import json
        try:
            explanation_list = ast.literal_eval(claim[13]) if claim[13] else []
        except:
            explanation_list = []
        
        # Parse LIME explanation
        try:
            lime_explanation_list = json.loads(claim[14]) if claim[14] else []
        except:
            lime_explanation_list = []
        # Fetch attached documents for this claim
        cursor.execute("""
            SELECT id, filename, filepath, document_type, file_size, uploaded_by, uploaded_at, description
            FROM documents WHERE claim_id = ?
            ORDER BY uploaded_at DESC
        """, (claim_id,))
        docs = cursor.fetchall()
        documents = [
            {
                "id": d[0],
                "filename": d[1],
                "filepath": d[2],
                "document_type": d[3],
                "file_size": d[4],
                "uploaded_by": d[5],
                "uploaded_at": d[6],
                "description": d[7]
            }
            for d in docs
        ]
        
        return ClaimDetailResponse(
            id=claim[0],
            user_id=claim[1],
            status=claim[2],
            current_stage=claim[3],
            patient_age=claim[4],
            diagnosis=claim[5],
            admission_date=claim[6],
            discharge_date=claim[7],
            claimed_amount=claim[8],
            description=claim[9],
            risk_score=claim[10],
            risk_category=claim[11],
            prediction=claim[12],
            explanation=explanation_list,
            lime_explanation=lime_explanation_list,
            model_version=claim[15],
            length_of_stay=claim[16],
            created_at=claim[17],
            updated_at=claim[18],
            full_name=claim[19],
            status_history=status_history,
            documents=documents
        )
        
    finally:
        conn.close()

@router.get("/claims/{claim_id}/status")
async def get_claim_status(
    claim_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Get claim status and workflow stage"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, status, current_stage, updated_at
            FROM claims WHERE id = ?
        """, (claim_id,))
        
        claim = cursor.fetchone()
        
        if not claim:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Claim not found"
            )
        
        return {
            "claim_id": claim[0],
            "status": claim[1],
            "current_stage": claim[2],
            "updated_at": claim[3]
        }
        
    finally:
        conn.close()

@router.patch("/claims/{claim_id}/status")
async def update_claim_status_simple(
    claim_id: str,
    status_data: dict,
    current_user: TokenData = Depends(require_role(["company_admin", "company_staff"]))
):
    """Update claim status (company staff only) - Simple version for frontend"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if claim exists
        cursor.execute("SELECT id FROM claims WHERE id = ?", (claim_id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Claim not found"
            )
        
        new_status = status_data.get('status')
        notes = status_data.get('notes', f'Status updated to {new_status}')
        
        # Update claim status
        cursor.execute("""
            UPDATE claims
            SET status = ?, updated_at = ?
            WHERE id = ?
        """, (new_status, datetime.utcnow(), claim_id))
        
        # Add to status history
        cursor.execute("""
            INSERT INTO claim_status_history (claim_id, status, notes, changed_by, changed_at)
            VALUES (?, ?, ?, ?, ?)
        """, (claim_id, new_status, notes, current_user.user_id, datetime.utcnow()))
        
        conn.commit()
        
        return {"message": "Claim status updated successfully", "new_status": new_status}
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update claim status: {str(e)}"
        )
    finally:
        conn.close()

@router.put("/claims/{claim_id}/status")
async def update_claim_status(
    claim_id: str,
    status_update: ClaimStatusUpdate,
    current_user: TokenData = Depends(require_role(["company_admin", "company_staff"]))
):
    """Update claim status (company staff only)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if claim exists
        cursor.execute("SELECT id FROM claims WHERE id = ?", (claim_id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Claim not found"
            )
        
        # Update claim status
        cursor.execute("""
            UPDATE claims
            SET status = ?, updated_at = ?
            WHERE id = ?
        """, (status_update.status.value, datetime.utcnow(), claim_id))
        
        # Add to status history
        cursor.execute("""
            INSERT INTO claim_status_history (claim_id, status, notes, changed_by, changed_at)
            VALUES (?, ?, ?, ?, ?)
        """, (claim_id, status_update.status.value, status_update.notes,
              current_user.user_id, datetime.utcnow()))
        
        conn.commit()
        
        return {"message": "Claim status updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update claim status: {str(e)}"
        )
    finally:
        conn.close()

@router.get("/company/claims", response_model=List[ClaimResponse])
async def get_all_claims(
    status: Optional[str] = Query(None),
    risk_category: Optional[str] = Query(None),
    min_risk_score: Optional[float] = Query(None),
    limit: int = Query(100, le=1000),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=1000),
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query('created_at'),
    sort_dir: Optional[str] = Query('desc'),
    current_user: TokenData = Depends(require_role(["company_admin", "company_staff"]))
):
    """Get all claims with filters (company staff only)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Base query with optional join to users for searching by name
        base_select = "SELECT c.id, c.user_id, c.status, c.current_stage, c.patient_age, c.diagnosis, c.claimed_amount, c.risk_score, c.risk_category, c.prediction, c.created_at, c.updated_at"
        base_from = " FROM claims c"
        params = []

        if search:
            base_from += " LEFT JOIN users u ON c.user_id = u.id"

        query = base_select + base_from + " WHERE 1=1"
        
        if status:
            query += " AND c.status = ?"
            params.append(status)
        
        if risk_category:
            query += " AND c.risk_category = ?"
            params.append(risk_category)
        
        if min_risk_score is not None:
            query += " AND c.risk_score >= ?"
            params.append(min_risk_score)

        if search:
            # search by claim id or user full_name
            query += " AND (c.id LIKE ? OR u.full_name LIKE ? )"
            term = f"%{search}%"
            params.extend([term, term])
        
        # Sorting
        allowed_sorts = {'created_at': 'c.created_at', 'claimed_amount': 'c.claimed_amount', 'risk_score': 'c.risk_score'}
        sort_col = allowed_sorts.get(sort_by, 'c.created_at')
        sort_direction = 'ASC' if sort_dir.lower() == 'asc' else 'DESC'

        # Pagination: compute LIMIT and OFFSET
        page_size = min(max(1, page_size), 1000)
        offset = (max(1, page) - 1) * page_size

        query += f" ORDER BY {sort_col} {sort_direction} LIMIT ? OFFSET ?"
        params.append(page_size)
        params.append(offset)
        
        cursor.execute(query, params)
        claims = cursor.fetchall()
        results = []
        for claim in claims:
            claim_id = claim[0]
            cursor.execute("""
                SELECT id, filename, filepath, document_type, file_size, uploaded_by, uploaded_at, description
                FROM documents WHERE claim_id = ?
                ORDER BY uploaded_at DESC
            """, (claim_id,))
            docs = cursor.fetchall()
            documents = [
                {
                    "id": d[0],
                    "filename": d[1],
                    "filepath": d[2],
                    "document_type": d[3],
                    "file_size": d[4],
                    "uploaded_by": d[5],
                    "uploaded_at": d[6],
                    "description": d[7]
                }
                for d in docs
            ]

            results.append(ClaimResponse(
                id=claim[0],
                user_id=claim[1],
                status=claim[2],
                current_stage=claim[3],
                patient_age=claim[4],
                diagnosis=claim[5],
                claimed_amount=claim[6],
                risk_score=claim[7],
                risk_category=claim[8],
                prediction=claim[9],
                created_at=claim[10],
                updated_at=claim[11],
                documents=documents
            ))

        return results
        
    finally:
        conn.close()

@router.get("/company/dashboard/stats", response_model=CompanyDashboardStats)
async def get_dashboard_stats(
    current_user: TokenData = Depends(require_role(["company_admin", "company_staff"]))
):
    """Get dashboard statistics (company staff only)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Total claims
        cursor.execute("SELECT COUNT(*) FROM claims")
        total_claims = cursor.fetchone()[0]
        
        # Status counts
        cursor.execute("SELECT COUNT(*) FROM claims WHERE status = 'under_review'")
        pending_review = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM claims WHERE status = 'approved'")
        approved = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM claims WHERE status = 'rejected'")
        rejected = cursor.fetchone()[0]
        
        # Risk category counts
        cursor.execute("SELECT COUNT(*) FROM claims WHERE risk_category = 'high'")
        high_risk = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM claims WHERE risk_category = 'medium'")
        medium_risk = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM claims WHERE risk_category = 'low'")
        low_risk = cursor.fetchone()[0]
        
        # Average processing time
        cursor.execute("""
            SELECT AVG(
                CAST((julianday(updated_at) - julianday(created_at)) * 24 AS REAL)
            ) FROM claims
            WHERE status IN ('approved', 'rejected')
        """)
        avg_time = cursor.fetchone()[0] or 0
        
        return CompanyDashboardStats(
            total_claims=total_claims,
            pending_review=pending_review,
            approved=approved,
            rejected=rejected,
            high_risk=high_risk,
            medium_risk=medium_risk,
            low_risk=low_risk,
            avg_processing_time_hours=round(avg_time, 2)
        )
        
    finally:
        conn.close()
