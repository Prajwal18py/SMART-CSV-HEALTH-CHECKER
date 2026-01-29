"""
Database Functions
Handle all database operations for analyses and user data
"""
import streamlit as st
from datetime import datetime
from config.supabase_config import supabase
from auth.auth_functions import get_current_user
from utils.logger import get_logger

logger = get_logger()

def save_analysis(filename: str, health_score: float, total_rows: int, 
                 total_columns: int, issues_high: int, issues_medium: int, 
                 issues_low: int, analysis_data: dict = None):
    """
    Save analysis results to database
    
    Args:
        filename: Name of analyzed file
        health_score: Overall health score (0-100)
        total_rows: Number of rows
        total_columns: Number of columns
        issues_high: High severity issues count
        issues_medium: Medium severity issues count
        issues_low: Low severity issues count
        analysis_data: Additional analysis data (JSON)
    
    Returns:
        dict: Success status and inserted data
    """
    try:
        user = get_current_user()
        if not user:
            return {"success": False, "error": "User not authenticated"}
        
        data = {
            "user_id": user.id,
            "filename": filename,
            "health_score": round(health_score, 2),
            "total_rows": total_rows,
            "total_columns": total_columns,
            "issues_high": issues_high,
            "issues_medium": issues_medium,
            "issues_low": issues_low,
            "analysis_data": analysis_data or {},
            "created_at": datetime.utcnow().isoformat()
        }
        
        response = supabase.table('analyses').insert(data).execute()
        
        logger.info(f"✅ Analysis saved: {filename} (Score: {health_score})")
        return {"success": True, "data": response.data}
    
    except Exception as e:
        logger.error(f"❌ Error saving analysis: {e}")
        return {"success": False, "error": str(e)}


def get_user_analyses(limit: int = 50):
    """
    Get all analyses for current user
    
    Args:
        limit: Maximum number of records to return
    
    Returns:
        list: List of analysis records
    """
    try:
        user = get_current_user()
        if not user:
            return []
        
        response = supabase.table('analyses')\
            .select("*")\
            .eq('user_id', user.id)\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()
        
        logger.info(f"✅ Retrieved {len(response.data)} analyses")
        return response.data
    
    except Exception as e:
        logger.error(f"❌ Error fetching analyses: {e}")
        return []


def get_analysis_by_id(analysis_id: str):
    """
    Get specific analysis by ID
    
    Args:
        analysis_id: UUID of analysis
    
    Returns:
        dict: Analysis record or None
    """
    try:
        response = supabase.table('analyses')\
            .select("*")\
            .eq('id', analysis_id)\
            .single()\
            .execute()
        
        return response.data
    
    except Exception as e:
        logger.error(f"❌ Error fetching analysis: {e}")
        return None


def delete_analysis(analysis_id: str):
    """
    Delete analysis by ID
    
    Args:
        analysis_id: UUID of analysis to delete
    
    Returns:
        dict: Success status
    """
    try:
        user = get_current_user()
        if not user:
            return {"success": False, "error": "User not authenticated"}
        
        # Verify ownership before deleting
        analysis = get_analysis_by_id(analysis_id)
        if not analysis or analysis['user_id'] != user.id:
            return {"success": False, "error": "Unauthorized"}
        
        supabase.table('analyses').delete().eq('id', analysis_id).execute()
        
        logger.info(f"✅ Analysis deleted: {analysis_id}")
        return {"success": True}
    
    except Exception as e:
        logger.error(f"❌ Error deleting analysis: {e}")
        return {"success": False, "error": str(e)}


def get_user_stats():
    """
    Get statistics for current user
    
    Returns:
        dict: User statistics
    """
    try:
        user = get_current_user()
        if not user:
            return {}
        
        analyses = get_user_analyses(limit=1000)
        
        if not analyses:
            return {
                "total_analyses": 0,
                "avg_health_score": 0,
                "total_issues_fixed": 0,
                "files_analyzed": 0
            }
        
        total = len(analyses)
        avg_score = sum(a['health_score'] for a in analyses) / total if total > 0 else 0
        total_issues = sum(a['issues_high'] + a['issues_medium'] + a['issues_low'] for a in analyses)
        
        stats = {
            "total_analyses": total,
            "avg_health_score": round(avg_score, 2),
            "total_issues_found": total_issues,
            "files_analyzed": len(set(a['filename'] for a in analyses)),
            "last_analysis": analyses[0]['created_at'] if analyses else None
        }
        
        logger.info(f"✅ User stats calculated: {stats}")
        return stats
    
    except Exception as e:
        logger.error(f"❌ Error calculating stats: {e}")
        return {}