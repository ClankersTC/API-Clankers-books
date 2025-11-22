from datetime import datetime, timezone

def calculate_time_ago(date_obj: datetime) -> str:
    """
    Calcula la diferencia entre ahora y la fecha dada.
    Retorna string tipo '2 days ago', 'just now', '1 year ago'.
    """
    if not date_obj:
        return ""
        
    # Aseguramos que ambas fechas tengan zona horaria (UTC)
    now = datetime.now(timezone.utc)
    if date_obj.tzinfo is None:
        date_obj = date_obj.replace(tzinfo=timezone.utc)
        
    diff = now - date_obj
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} min{'s' if minutes > 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif seconds < 2592000: # 30 días
        days = int(seconds / 86400)
        return f"{days} day{'s' if days > 1 else ''} ago"
    elif seconds < 31536000: # 1 año
        months = int(seconds / 2592000)
        return f"{months} month{'s' if months > 1 else ''} ago"
    else:
        years = int(seconds / 31536000)
        return f"{years} year{'s' if years > 1 else ''} ago"