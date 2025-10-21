from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sqlite3
from datetime import datetime, timedelta
import json

router = APIRouter()

class ActivityRequest(BaseModel):
    email: str
    job_title: str
    ats_score: Optional[int] = None
    action_type: str = "resume_generated"  # resume_generated, resume_downloaded, resume_emailed

class ActivityResponse(BaseModel):
    success: bool
    activity_id: int
    message: str

class ActivityStats(BaseModel):
    total_activities: int
    recent_activities: List[Dict[str, Any]]
    top_job_titles: List[Dict[str, Any]]
    average_ats_score: float
    success_rate: float

@router.post("/log", response_model=ActivityResponse)
async def log_activity(request: ActivityRequest):
    """
    Log user activity
    """
    try:
        # Validate inputs
        if not request.email or "@" not in request.email:
            raise HTTPException(status_code=400, detail="Valid email is required")
        
        if not request.job_title.strip():
            raise HTTPException(status_code=400, detail="Job title is required")
        
        # Connect to database
        conn = sqlite3.connect('db/rezoom.db')
        cursor = conn.cursor()
        
        # Insert activity
        cursor.execute('''
            INSERT INTO user_activity (email, job_title, ats_score, generated_at)
            VALUES (?, ?, ?, ?)
        ''', (
            request.email,
            request.job_title,
            request.ats_score,
            datetime.now().isoformat()
        ))
        
        activity_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return ActivityResponse(
            success=True,
            activity_id=activity_id,
            message="Activity logged successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error logging activity: {str(e)}")

@router.get("/stats", response_model=ActivityStats)
async def get_activity_stats(days: int = 30):
    """
    Get activity statistics
    """
    try:
        conn = sqlite3.connect('db/rezoom.db')
        cursor = conn.cursor()
        
        # Calculate date range
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Total activities in date range
        cursor.execute('''
            SELECT COUNT(*) FROM user_activity 
            WHERE generated_at >= ?
        ''', (start_date,))
        total_activities = cursor.fetchone()[0]
        
        # Recent activities
        cursor.execute('''
            SELECT email, job_title, ats_score, generated_at
            FROM user_activity 
            WHERE generated_at >= ?
            ORDER BY generated_at DESC
            LIMIT 10
        ''', (start_date,))
        
        recent_activities = []
        for row in cursor.fetchall():
            recent_activities.append({
                "email": row[0],
                "job_title": row[1],
                "ats_score": row[2],
                "generated_at": row[3]
            })
        
        # Top job titles
        cursor.execute('''
            SELECT job_title, COUNT(*) as count
            FROM user_activity 
            WHERE generated_at >= ?
            GROUP BY job_title
            ORDER BY count DESC
            LIMIT 5
        ''', (start_date,))
        
        top_job_titles = []
        for row in cursor.fetchall():
            top_job_titles.append({
                "job_title": row[0],
                "count": row[1]
            })
        
        # Average ATS score
        cursor.execute('''
            SELECT AVG(ats_score) FROM user_activity 
            WHERE generated_at >= ? AND ats_score IS NOT NULL
        ''', (start_date,))
        avg_score_result = cursor.fetchone()[0]
        average_ats_score = round(avg_score_result, 2) if avg_score_result else 0
        
        # Success rate (ATS score > 70)
        cursor.execute('''
            SELECT COUNT(*) FROM user_activity 
            WHERE generated_at >= ? AND ats_score > 70
        ''', (start_date,))
        successful_count = cursor.fetchone()[0]
        success_rate = round((successful_count / total_activities * 100), 2) if total_activities > 0 else 0
        
        conn.close()
        
        return ActivityStats(
            total_activities=total_activities,
            recent_activities=recent_activities,
            top_job_titles=top_job_titles,
            average_ats_score=average_ats_score,
            success_rate=success_rate
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting activity stats: {str(e)}")

@router.get("/user/{email}")
async def get_user_activities(email: str, limit: int = 10):
    """
    Get activities for a specific user
    """
    try:
        if not email or "@" not in email:
            raise HTTPException(status_code=400, detail="Valid email is required")
        
        conn = sqlite3.connect('db/rezoom.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, job_title, ats_score, generated_at
            FROM user_activity 
            WHERE email = ?
            ORDER BY generated_at DESC
            LIMIT ?
        ''', (email, limit))
        
        activities = []
        for row in cursor.fetchall():
            activities.append({
                "id": row[0],
                "job_title": row[1],
                "ats_score": row[2],
                "generated_at": row[3]
            })
        
        conn.close()
        
        return {
            "email": email,
            "activities": activities,
            "total": len(activities)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user activities: {str(e)}")

@router.get("/dashboard")
async def get_dashboard_data():
    """
    Get dashboard data for admin/analytics
    """
    try:
        conn = sqlite3.connect('db/rezoom.db')
        cursor = conn.cursor()
        
        # Today's activities
        today = datetime.now().date().isoformat()
        cursor.execute('''
            SELECT COUNT(*) FROM user_activity 
            WHERE DATE(generated_at) = ?
        ''', (today,))
        today_activities = cursor.fetchone()[0]
        
        # This week's activities
        week_start = (datetime.now() - timedelta(days=7)).date().isoformat()
        cursor.execute('''
            SELECT COUNT(*) FROM user_activity 
            WHERE DATE(generated_at) >= ?
        ''', (week_start,))
        week_activities = cursor.fetchone()[0]
        
        # This month's activities
        month_start = (datetime.now() - timedelta(days=30)).date().isoformat()
        cursor.execute('''
            SELECT COUNT(*) FROM user_activity 
            WHERE DATE(generated_at) >= ?
        ''', (month_start,))
        month_activities = cursor.fetchone()[0]
        
        # Average ATS score this month
        cursor.execute('''
            SELECT AVG(ats_score) FROM user_activity 
            WHERE DATE(generated_at) >= ? AND ats_score IS NOT NULL
        ''', (month_start,))
        avg_score_result = cursor.fetchone()[0]
        avg_ats_score = round(avg_score_result, 2) if avg_score_result else 0
        
        # Top performing job titles (high ATS scores)
        cursor.execute('''
            SELECT job_title, AVG(ats_score) as avg_score, COUNT(*) as count
            FROM user_activity 
            WHERE DATE(generated_at) >= ? AND ats_score IS NOT NULL
            GROUP BY job_title
            HAVING count >= 2
            ORDER BY avg_score DESC
            LIMIT 5
        ''', (month_start,))
        
        top_performing = []
        for row in cursor.fetchall():
            top_performing.append({
                "job_title": row[0],
                "avg_score": round(row[1], 2),
                "count": row[2]
            })
        
        # Recent high-scoring resumes
        cursor.execute('''
            SELECT email, job_title, ats_score, generated_at
            FROM user_activity 
            WHERE ats_score >= 80
            ORDER BY generated_at DESC
            LIMIT 5
        ''')
        
        recent_high_scores = []
        for row in cursor.fetchall():
            recent_high_scores.append({
                "email": row[0][:3] + "***@***",  # Anonymize email
                "job_title": row[1],
                "ats_score": row[2],
                "generated_at": row[3]
            })
        
        conn.close()
        
        return {
            "summary": {
                "today_activities": today_activities,
                "week_activities": week_activities,
                "month_activities": month_activities,
                "avg_ats_score": avg_ats_score
            },
            "top_performing_jobs": top_performing,
            "recent_high_scores": recent_high_scores,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting dashboard data: {str(e)}")

@router.delete("/cleanup")
async def cleanup_old_activities(days: int = 90):
    """
    Clean up old activities (older than specified days)
    """
    try:
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        conn = sqlite3.connect('db/rezoom.db')
        cursor = conn.cursor()
        
        # Count records to be deleted
        cursor.execute('''
            SELECT COUNT(*) FROM user_activity 
            WHERE generated_at < ?
        ''', (cutoff_date,))
        records_to_delete = cursor.fetchone()[0]
        
        # Delete old records
        cursor.execute('''
            DELETE FROM user_activity 
            WHERE generated_at < ?
        ''', (cutoff_date,))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "deleted_records": deleted_count,
            "cutoff_date": cutoff_date,
            "message": f"Cleaned up {deleted_count} old activity records"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cleaning up activities: {str(e)}")

@router.get("/export")
async def export_activities(format: str = "json", days: int = 30):
    """
    Export activities data
    """
    try:
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        conn = sqlite3.connect('db/rezoom.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT email, job_title, ats_score, generated_at
            FROM user_activity 
            WHERE generated_at >= ?
            ORDER BY generated_at DESC
        ''', (start_date,))
        
        activities = []
        for row in cursor.fetchall():
            activities.append({
                "email": row[0],
                "job_title": row[1],
                "ats_score": row[2],
                "generated_at": row[3]
            })
        
        conn.close()
        
        if format.lower() == "csv":
            # Convert to CSV format
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["Email", "Job Title", "ATS Score", "Generated At"])
            
            for activity in activities:
                writer.writerow([
                    activity["email"],
                    activity["job_title"],
                    activity["ats_score"],
                    activity["generated_at"]
                ])
            
            return {
                "format": "csv",
                "data": output.getvalue(),
                "count": len(activities)
            }
        else:
            return {
                "format": "json",
                "data": activities,
                "count": len(activities)
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting activities: {str(e)}")
