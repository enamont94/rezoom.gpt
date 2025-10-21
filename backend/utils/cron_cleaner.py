"""
Cron Cleaner Utility
Handles automatic cleanup of temporary files and old data
"""

import os
import time
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
import schedule
import threading

logger = logging.getLogger(__name__)

class CronCleaner:
    """Automatic cleanup utility for temporary files and old data"""
    
    def __init__(self, temp_dir: str = "tmp", db_path: str = "db/rezoom.db"):
        self.temp_dir = temp_dir
        self.db_path = db_path
        self.cleanup_interval = 10  # minutes
        self.file_retention_hours = 1
        self.db_retention_days = 90
        self.running = False
        self.cleanup_thread = None
    
    def start_cleanup_scheduler(self):
        """Start the cleanup scheduler"""
        if self.running:
            logger.warning("Cleanup scheduler is already running")
            return
        
        self.running = True
        
        # Schedule cleanup tasks
        schedule.every(self.cleanup_interval).minutes.do(self.cleanup_temp_files)
        schedule.every(1).hours.do(self.cleanup_old_activities)
        schedule.every(1).days.do(self.cleanup_old_resume_cache)
        
        # Start scheduler in separate thread
        self.cleanup_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.cleanup_thread.start()
        
        logger.info(f"Cleanup scheduler started (interval: {self.cleanup_interval} minutes)")
    
    def stop_cleanup_scheduler(self):
        """Stop the cleanup scheduler"""
        self.running = False
        schedule.clear()
        logger.info("Cleanup scheduler stopped")
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in cleanup scheduler: {str(e)}")
                time.sleep(60)
    
    def cleanup_temp_files(self) -> Dict[str, Any]:
        """Clean up temporary files older than retention period"""
        try:
            if not os.path.exists(self.temp_dir):
                return {'cleaned': 0, 'message': 'Temp directory does not exist'}
            
            current_time = time.time()
            retention_seconds = self.file_retention_hours * 3600
            cleaned_files = []
            total_size = 0
            
            for filename in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, filename)
                
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getmtime(file_path)
                    
                    if file_age > retention_seconds:
                        try:
                            file_size = os.path.getsize(file_path)
                            os.remove(file_path)
                            cleaned_files.append(filename)
                            total_size += file_size
                        except Exception as e:
                            logger.warning(f"Error removing file {filename}: {str(e)}")
            
            logger.info(f"Cleaned {len(cleaned_files)} temporary files ({total_size} bytes)")
            
            return {
                'cleaned': len(cleaned_files),
                'files': cleaned_files,
                'size_freed': total_size,
                'message': f'Cleaned {len(cleaned_files)} files'
            }
            
        except Exception as e:
            logger.error(f"Error cleaning temp files: {str(e)}")
            return {'cleaned': 0, 'error': str(e)}
    
    def cleanup_old_activities(self) -> Dict[str, Any]:
        """Clean up old activity records from database"""
        try:
            if not os.path.exists(self.db_path):
                return {'cleaned': 0, 'message': 'Database does not exist'}
            
            cutoff_date = (datetime.now() - timedelta(days=self.db_retention_days)).isoformat()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Count records to be deleted
            cursor.execute('''
                SELECT COUNT(*) FROM user_activity 
                WHERE generated_at < ?
            ''', (cutoff_date,))
            records_to_delete = cursor.fetchone()[0]
            
            if records_to_delete > 0:
                # Delete old records
                cursor.execute('''
                    DELETE FROM user_activity 
                    WHERE generated_at < ?
                ''', (cutoff_date,))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"Cleaned {deleted_count} old activity records")
                
                return {
                    'cleaned': deleted_count,
                    'cutoff_date': cutoff_date,
                    'message': f'Cleaned {deleted_count} old activity records'
                }
            else:
                return {
                    'cleaned': 0,
                    'message': 'No old activity records to clean'
                }
                
        except Exception as e:
            logger.error(f"Error cleaning old activities: {str(e)}")
            return {'cleaned': 0, 'error': str(e)}
        finally:
            if 'conn' in locals():
                conn.close()
    
    def cleanup_old_resume_cache(self) -> Dict[str, Any]:
        """Clean up old resume cache records"""
        try:
            if not os.path.exists(self.db_path):
                return {'cleaned': 0, 'message': 'Database does not exist'}
            
            cutoff_date = (datetime.now() - timedelta(days=30)).isoformat()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Count records to be deleted
            cursor.execute('''
                SELECT COUNT(*) FROM resume_cache 
                WHERE created_at < ?
            ''', (cutoff_date,))
            records_to_delete = cursor.fetchone()[0]
            
            if records_to_delete > 0:
                # Delete old records
                cursor.execute('''
                    DELETE FROM resume_cache 
                    WHERE created_at < ?
                ''', (cutoff_date,))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"Cleaned {deleted_count} old resume cache records")
                
                return {
                    'cleaned': deleted_count,
                    'cutoff_date': cutoff_date,
                    'message': f'Cleaned {deleted_count} old resume cache records'
                }
            else:
                return {
                    'cleaned': 0,
                    'message': 'No old resume cache records to clean'
                }
                
        except Exception as e:
            logger.error(f"Error cleaning old resume cache: {str(e)}")
            return {'cleaned': 0, 'error': str(e)}
        finally:
            if 'conn' in locals():
                conn.close()
    
    def cleanup_all(self) -> Dict[str, Any]:
        """Run all cleanup tasks"""
        results = {
            'temp_files': self.cleanup_temp_files(),
            'old_activities': self.cleanup_old_activities(),
            'old_resume_cache': self.cleanup_old_resume_cache(),
            'timestamp': datetime.now().isoformat()
        }
        
        total_cleaned = (
            results['temp_files'].get('cleaned', 0) +
            results['old_activities'].get('cleaned', 0) +
            results['old_resume_cache'].get('cleaned', 0)
        )
        
        results['total_cleaned'] = total_cleaned
        
        logger.info(f"Manual cleanup completed: {total_cleaned} items cleaned")
        
        return results
    
    def get_cleanup_stats(self) -> Dict[str, Any]:
        """Get cleanup statistics"""
        try:
            stats = {
                'temp_dir_exists': os.path.exists(self.temp_dir),
                'db_exists': os.path.exists(self.db_path),
                'scheduler_running': self.running,
                'cleanup_interval': self.cleanup_interval,
                'file_retention_hours': self.file_retention_hours,
                'db_retention_days': self.db_retention_days
            }
            
            # Count temp files
            if os.path.exists(self.temp_dir):
                temp_files = [f for f in os.listdir(self.temp_dir) if os.path.isfile(os.path.join(self.temp_dir, f))]
                stats['temp_files_count'] = len(temp_files)
                stats['temp_files_size'] = sum(
                    os.path.getsize(os.path.join(self.temp_dir, f)) 
                    for f in temp_files
                )
            else:
                stats['temp_files_count'] = 0
                stats['temp_files_size'] = 0
            
            # Count database records
            if os.path.exists(self.db_path):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Count activity records
                cursor.execute('SELECT COUNT(*) FROM user_activity')
                stats['activity_records'] = cursor.fetchone()[0]
                
                # Count resume cache records
                cursor.execute('SELECT COUNT(*) FROM resume_cache')
                stats['resume_cache_records'] = cursor.fetchone()[0]
                
                conn.close()
            else:
                stats['activity_records'] = 0
                stats['resume_cache_records'] = 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting cleanup stats: {str(e)}")
            return {'error': str(e)}
    
    def set_retention_policy(self, file_retention_hours: int = None, 
                           db_retention_days: int = None):
        """Update retention policy settings"""
        if file_retention_hours is not None:
            self.file_retention_hours = file_retention_hours
            logger.info(f"File retention set to {file_retention_hours} hours")
        
        if db_retention_days is not None:
            self.db_retention_days = db_retention_days
            logger.info(f"Database retention set to {db_retention_days} days")
    
    def force_cleanup(self) -> Dict[str, Any]:
        """Force immediate cleanup of all old data"""
        logger.info("Starting forced cleanup")
        
        results = self.cleanup_all()
        
        # Also clean up any files older than 1 hour regardless of retention policy
        if os.path.exists(self.temp_dir):
            current_time = time.time()
            force_cleaned = []
            
            for filename in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, filename)
                
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getmtime(file_path)
                    
                    if file_age > 3600:  # 1 hour
                        try:
                            os.remove(file_path)
                            force_cleaned.append(filename)
                        except Exception as e:
                            logger.warning(f"Error removing file {filename}: {str(e)}")
            
            results['force_cleaned_files'] = len(force_cleaned)
            results['force_cleaned_file_list'] = force_cleaned
        
        logger.info(f"Forced cleanup completed: {results.get('total_cleaned', 0)} items cleaned")
        
        return results

# Global cleaner instance
cleaner = CronCleaner()

def start_cleanup_scheduler():
    """Start the global cleanup scheduler"""
    cleaner.start_cleanup_scheduler()

def stop_cleanup_scheduler():
    """Stop the global cleanup scheduler"""
    cleaner.stop_cleanup_scheduler()

def cleanup_all():
    """Run all cleanup tasks"""
    return cleaner.cleanup_all()

def get_cleanup_stats():
    """Get cleanup statistics"""
    return cleaner.get_cleanup_stats()
