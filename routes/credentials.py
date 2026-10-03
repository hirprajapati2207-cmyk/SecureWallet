from flask import Blueprint, render_template, request, redirect, url_for, flash, g, jsonify
from security.authentication import login_required
from security.encryption import encrypt_password, decrypt_password
from database.database import get_db

bp = Blueprint('credentials', __name__, url_prefix='/credentials')

@bp.route('/')
@login_required
def index():
    db = get_db()
    credentials = db.execute(
        'SELECT c.credential_id, c.website_name, c.website_url, c.username, cat.category_name '
        'FROM credentials c LEFT JOIN categories cat ON c.category_id = cat.category_id '
        'WHERE c.user_id = ? ORDER BY c.created_at DESC',
        (g.user['user_id'],)
    ).fetchall()
        
    return render_template('credentials/index.html', credentials=credentials)

@bp.route('/<int:id>/reveal', methods=['POST'])
@login_required
def reveal(id):
    db = get_db()
    cred = db.execute(
        'SELECT encrypted_password FROM credentials WHERE credential_id = ? AND user_id = ?',
        (id, g.user['user_id'])
    ).fetchone()
    
    if cred:
        try:
            decrypted = decrypt_password(cred['encrypted_password'])
            db.execute('INSERT INTO activity_logs (user_id, action, description) VALUES (?, ?, ?)',
                       (g.user['user_id'], 'VIEW_PASSWORD', f'Viewed password for credential ID {id}'))
            db.commit()
            return jsonify({'success': True, 'password': decrypted})
        except Exception:
            return jsonify({'success': False, 'error': 'Decryption failed'}), 500
            
    return jsonify({'success': False, 'error': 'Credential not found or unauthorized'}), 404

@bp.route('/add', methods=('GET', 'POST'))
@login_required
def add():
    db = get_db()
    if request.method == 'POST':
        website_name = request.form['website_name']
        website_url = request.form['website_url']
        username = request.form['username']
        password = request.form['password']
        category_id = request.form.get('category_id') or None
        new_category = request.form.get('new_category')
        notes = request.form['notes']
        
        if not website_name or not password:
            flash('Website name and password are required.')
        else:
            if new_category and new_category.strip():
                cur = db.execute('INSERT INTO categories (user_id, category_name) VALUES (?, ?)', 
                                 (g.user['user_id'], new_category.strip()))
                category_id = cur.lastrowid

            encrypted_pw = encrypt_password(password)
            db.execute(
                'INSERT INTO credentials (user_id, category_id, website_name, website_url, username, encrypted_password, notes) '
                'VALUES (?, ?, ?, ?, ?, ?, ?)',
                (g.user['user_id'], category_id, website_name, website_url, username, encrypted_pw, notes)
            )
            db.execute('INSERT INTO activity_logs (user_id, action, description) VALUES (?, ?, ?)',
                       (g.user['user_id'], 'ADD_CREDENTIAL', f'Added credential for {website_name}'))
            db.commit()
            flash('Credential added successfully.')
            return redirect(url_for('credentials.index'))
            
    categories = db.execute('SELECT * FROM categories WHERE user_id = ?', (g.user['user_id'],)).fetchall()
    return render_template('credentials/add.html', categories=categories)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    db = get_db()
    cred = db.execute(
        'SELECT website_name FROM credentials WHERE credential_id = ? AND user_id = ?',
        (id, g.user['user_id'])
    ).fetchone()
    
    if cred:
        db.execute('DELETE FROM credentials WHERE credential_id = ? AND user_id = ?', (id, g.user['user_id']))
        db.execute('INSERT INTO activity_logs (user_id, action, description) VALUES (?, ?, ?)',
                   (g.user['user_id'], 'DELETE_CREDENTIAL', f'Deleted credential for {cred["website_name"]}'))
        db.commit()
        flash('Credential deleted successfully.')
    else:
        flash('Credential not found or unauthorized.')
        
    return redirect(url_for('credentials.index'))

@bp.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit(id):
    db = get_db()
    cred = db.execute(
        'SELECT * FROM credentials WHERE credential_id = ? AND user_id = ?',
        (id, g.user['user_id'])
    ).fetchone()

    if not cred:
        flash('Credential not found.')
        return redirect(url_for('credentials.index'))

    if request.method == 'POST':
        website_name = request.form['website_name']
        website_url = request.form['website_url']
        username = request.form['username']
        password = request.form['password']
        category_id = request.form.get('category_id') or None
        new_category = request.form.get('new_category')
        notes = request.form['notes']

        if not website_name or not password:
            flash('Website name and password are required.')
        else:
            if new_category and new_category.strip():
                cur = db.execute('INSERT INTO categories (user_id, category_name) VALUES (?, ?)', 
                                 (g.user['user_id'], new_category.strip()))
                category_id = cur.lastrowid

            encrypted_pw = encrypt_password(password)
            db.execute(
                'UPDATE credentials SET category_id = ?, website_name = ?, website_url = ?, username = ?, encrypted_password = ?, notes = ?, updated_at = CURRENT_TIMESTAMP WHERE credential_id = ? AND user_id = ?',
                (category_id, website_name, website_url, username, encrypted_pw, notes, id, g.user['user_id'])
            )
            db.execute('INSERT INTO activity_logs (user_id, action, description) VALUES (?, ?, ?)',
                       (g.user['user_id'], 'EDIT_CREDENTIAL', f'Updated credential for {website_name}'))
            db.commit()
            flash('Credential updated successfully.')
            return redirect(url_for('credentials.index'))

    categories = db.execute('SELECT * FROM categories WHERE user_id = ?', (g.user['user_id'],)).fetchall()
    
    cred_dict = dict(cred)
    try:
        cred_dict['decrypted_password'] = decrypt_password(cred['encrypted_password'])
    except Exception:
        cred_dict['decrypted_password'] = ''
        
    return render_template('credentials/edit.html', cred=cred_dict, categories=categories)
