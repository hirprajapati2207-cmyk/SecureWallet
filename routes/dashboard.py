from flask import Blueprint, render_template, g
from security.authentication import login_required
from database.database import get_db

bp = Blueprint('dashboard', __name__)

@bp.route('/dashboard')
@login_required
def index():
    db = get_db()
    # Get stats
    creds_count = db.execute('SELECT COUNT(*) FROM credentials WHERE user_id = ?', (g.user['user_id'],)).fetchone()[0]
    cats_count = db.execute('SELECT COUNT(*) FROM categories WHERE user_id = ?', (g.user['user_id'],)).fetchone()[0]
    
    # Get recent logs
    logs = db.execute('SELECT * FROM activity_logs WHERE user_id = ? ORDER BY created_at DESC LIMIT 5', (g.user['user_id'],)).fetchall()
    
    return render_template('dashboard/index.html', creds_count=creds_count, cats_count=cats_count, logs=logs)
