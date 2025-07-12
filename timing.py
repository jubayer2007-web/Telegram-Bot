from datetime import datetime

def within_allowed_time():
    now = datetime.now().time()
    start = datetime.strptime("07:00", "%H:%M").time()
    end = datetime.strptime("23:59", "%H:%M").time()
    return start <= now <= end
