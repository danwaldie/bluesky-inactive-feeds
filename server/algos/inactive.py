from datetime import datetime, timedelta
from typing import Optional

from server.database import User

CURSOR_EOF = 'eof'

def get_handler(days: int):
    """Returns a handler function for the specified inactivity period"""
    def handler(cursor: Optional[str], limit: int) -> dict:
        if cursor == CURSOR_EOF:
            return {
                'cursor': CURSOR_EOF,
                'feed': []
            }

        cutoff = datetime.utcnow() - timedelta(days=days)
        
        # Find users whose last post was before cutoff
        inactive_users = (User
            .select()
            .where(
                (User.last_post_time < cutoff) & 
                (User.last_post_time.is_not(None))
            )
            .order_by(User.last_post_time.desc())
            .limit(limit))

        feed = [{'post': user.last_post_uri} for user in inactive_users]
        
        # Return EOF if we got fewer results than requested
        next_cursor = CURSOR_EOF if len(feed) < limit else str(int(cutoff.timestamp()))
        
        return {
            'cursor': next_cursor,
            'feed': feed
        }
    
    return handler 
