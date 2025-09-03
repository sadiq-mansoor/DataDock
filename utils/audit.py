import os
import json
from datetime import datetime
from database.models import AuditLog
from database.connection import get_db
from config import Config

def log_action(user_id, action, details=None, ip_address=None):
    """Log user action to database and file"""
    try:
        # Log to database
        db = next(get_db())
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            details=details or {},
            ip_address=ip_address,
            timestamp=datetime.utcnow()
        )
        db.add(audit_log)
        db.commit()
        db.close()
        
        # Log to file (immutable local storage)
        log_to_file(user_id, action, details, ip_address)
        
    except Exception as e:
        print(f"Error logging action: {e}")

def log_to_file(user_id, action, details, ip_address):
    """Log action to local file for immutable storage"""
    try:
        # Create logs directory if it doesn't exist
        os.makedirs(Config.LOGS_DIR, exist_ok=True)
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "details": details or {},
            "ip_address": ip_address
        }
        
        # Append to audit log file
        with open(Config.AUDIT_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
            
    except Exception as e:
        print(f"Error writing to audit log file: {e}")

def get_audit_logs(user_id=None, action=None, start_date=None, end_date=None, limit=100):
    """Retrieve audit logs with optional filters"""
    db = next(get_db())
    try:
        query = db.query(AuditLog)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        if action:
            query = query.filter(AuditLog.action == action)
        
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)
        
        logs = query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
        return logs
        
    finally:
        db.close()

def export_audit_logs(start_date=None, end_date=None, format='csv'):
    """Export audit logs to file"""
    logs = get_audit_logs(start_date=start_date, end_date=end_date, limit=10000)
    
    if format == 'csv':
        return export_audit_logs_csv(logs)
    elif format == 'json':
        return export_audit_logs_json(logs)
    else:
        raise ValueError("Unsupported format")

def export_audit_logs_csv(logs):
    """Export audit logs to CSV format"""
    import pandas as pd
    
    data = []
    for log in logs:
        data.append({
            'timestamp': log.timestamp,
            'user_id': log.user_id,
            'action': log.action,
            'details': json.dumps(log.details) if log.details else '',
            'ip_address': log.ip_address
        })
    
    df = pd.DataFrame(data)
    
    # Create exports directory if it doesn't exist
    os.makedirs(Config.EXPORTS_DIR, exist_ok=True)
    
    filename = f"audit_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join(Config.EXPORTS_DIR, filename)
    
    df.to_csv(filepath, index=False)
    return filepath

def export_audit_logs_json(logs):
    """Export audit logs to JSON format"""
    data = []
    for log in logs:
        data.append({
            'timestamp': log.timestamp.isoformat(),
            'user_id': log.user_id,
            'action': log.action,
            'details': log.details,
            'ip_address': log.ip_address
        })
    
    # Create exports directory if it doesn't exist
    os.makedirs(Config.EXPORTS_DIR, exist_ok=True)
    
    filename = f"audit_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join(Config.EXPORTS_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str)
    
    return filepath
