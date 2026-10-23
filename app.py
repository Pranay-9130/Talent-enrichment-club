"""
Talent Enrichment Club - Full Stack Web Application
Supports both Web Browser portal and connects with talent_enrichment_club.db
"""

import os
import sqlite3
import csv
import io
from flask import Flask, render_template, request, jsonify, send_file, Response

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'talent_enrichment_club.db')

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = 'talent-enrichment-club-secret-key-2026'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            department TEXT,
            uid TEXT,
            email TEXT,
            event TEXT,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            name TEXT,
            email TEXT,
            department TEXT,
            uid TEXT,
            role TEXT DEFAULT 'student',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            category TEXT,
            description TEXT,
            date TEXT,
            venue TEXT,
            max_seats INTEGER DEFAULT 50
        )
    ''')
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password, name, email, department, uid, role)
        VALUES ('admin', 'admin123', 'Club Administrator', 'admin@talentclub.org', 'Administration', 'ADMIN001', 'admin')
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats', methods=['GET'])
def get_stats():
    conn = get_db()
    cursor = conn.cursor()
    total_members = cursor.execute('SELECT COUNT(*) FROM members').fetchone()[0]
    total_events = cursor.execute('SELECT COUNT(*) FROM events').fetchone()[0]
    sports_count = cursor.execute("SELECT COUNT(*) FROM members WHERE event LIKE '%Sports%'").fetchone()[0]
    cultural_count = cursor.execute("SELECT COUNT(*) FROM members WHERE event LIKE '%Cultural%'").fetchone()[0]
    arts_count = cursor.execute("SELECT COUNT(*) FROM members WHERE event LIKE '%Arts%'").fetchone()[0]
    conn.close()
    return jsonify({
        'success': True,
        'stats': {
            'total_members': total_members,
            'total_events': total_events,
            'sports_count': sports_count,
            'cultural_count': cultural_count,
            'arts_count': arts_count
        }
    })

@app.route('/api/events', methods=['GET', 'POST'])
def handle_events():
    conn = get_db()
    cursor = conn.cursor()
    if request.method == 'POST':
        data = request.get_json() or {}
        title = data.get('title', '').strip()
        category = data.get('category', '').strip()
        description = data.get('description', '').strip()
        date = data.get('date', '').strip()
        venue = data.get('venue', '').strip()
        max_seats = int(data.get('max_seats', 50))
        if not title or not category:
            conn.close()
            return jsonify({'success': False, 'message': 'Title and Category are required.'}), 400
        cursor.execute('''
            INSERT INTO events (title, category, description, date, venue, max_seats)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, category, description, date, venue, max_seats))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return jsonify({'success': True, 'message': 'Event created successfully!', 'id': new_id})

    # GET request
    category = request.args.get('category')
    if category and category != 'All':
        events = cursor.execute('SELECT * FROM events WHERE category = ? ORDER BY id DESC', (category,)).fetchall()
    else:
        events = cursor.execute('SELECT * FROM events ORDER BY id DESC').fetchall()
    
    events_list = [dict(row) for row in events]
    conn.close()
    return jsonify({'success': True, 'events': events_list})

@app.route('/api/members', methods=['GET'])
def get_members():
    event_filter = request.args.get('event')
    search = request.args.get('search')
    dept = request.args.get('department')
    
    query = 'SELECT * FROM members WHERE 1=1'
    params = []
    
    if event_filter and event_filter != 'All':
        query += ' AND event LIKE ?'
        params.append(f'%{event_filter}%')
        
    if dept and dept != 'All':
        query += ' AND department = ?'
        params.append(dept)
        
    if search:
        query += ' AND (name LIKE ? OR uid LIKE ? OR email LIKE ?)'
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
        
    query += ' ORDER BY id DESC'
    
    conn = get_db()
    members = conn.cursor().execute(query, params).fetchall()
    members_list = [dict(row) for row in members]
    conn.close()
    return jsonify({'success': True, 'members': members_list})

@app.route('/api/member/register-event', methods=['POST'])
def register_member_event():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    department = data.get('department', '').strip()
    uid = data.get('uid', '').strip()
    email = data.get('email', '').strip()
    event = data.get('event', '').strip()
    
    if not (name and department and uid and email and event):
        return jsonify({'success': False, 'message': 'Please fill all required registration details.'}), 400
        
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if student already registered for this exact event
    existing = cursor.execute('''
        SELECT id FROM members WHERE uid = ? AND event = ?
    ''', (uid, event)).fetchone()
    
    if existing:
        conn.close()
        return jsonify({'success': False, 'message': f'UID {uid} is already registered for {event}.'}), 409
        
    cursor.execute('''
        INSERT INTO members (name, department, uid, email, event)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, department, uid, email, event))
    conn.commit()
    inserted_id = cursor.lastrowid
    conn.close()
    
    return jsonify({
        'success': True,
        'message': 'Registration completed successfully!',
        'registration_id': inserted_id,
        'member': {
            'id': inserted_id,
            'name': name,
            'department': department,
            'uid': uid,
            'email': email,
            'event': event
        }
    })

@app.route('/api/member/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM members WHERE id = ?', (member_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': f'Member registration #{member_id} removed.'})

@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    department = data.get('department', '').strip()
    uid = data.get('uid', '').strip()
    role = data.get('role', 'student').strip()
    
    if not (username and password and name and email and uid):
        return jsonify({'success': False, 'message': 'All user credentials and details are required.'}), 400
        
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (username, password, name, email, department, uid, role)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (username, password, name, email, department, uid, role))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return jsonify({
            'success': True,
            'message': 'Account registered successfully! You can now log in.',
            'user': {
                'id': user_id,
                'username': username,
                'name': name,
                'email': email,
                'department': department,
                'uid': uid,
                'role': role
            }
        })
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'success': False, 'message': 'Username already exists. Please choose another.'}), 409

@app.route('/api/login', methods=['POST'])
def login_user():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required.'}), 400
        
    conn = get_db()
    user = conn.cursor().execute('''
        SELECT id, username, name, email, department, uid, role
        FROM users
        WHERE username = ? AND password = ?
    ''', (username, password)).fetchone()
    conn.close()
    
    if user:
        return jsonify({
            'success': True,
            'message': f'Welcome back, {user["name"]}!',
            'user': dict(user)
        })
    else:
        return jsonify({'success': False, 'message': 'Invalid username or password.'}), 401

@app.route('/api/export-csv', methods=['GET'])
def export_csv():
    conn = get_db()
    members = conn.cursor().execute('SELECT id, name, department, uid, email, event, registered_at FROM members ORDER BY id ASC').fetchall()
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Department', 'UID', 'Email', 'Event', 'Registration Date'])
    for m in members:
        writer.writerow([m['id'], m['name'], m['department'], m['uid'], m['email'], m['event'], m['registered_at']])
        
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=Talent_Enrichment_Club_Members.csv"}
    )

if __name__ == '__main__':
    print("=" * 60)
    print(" Talent Enrichment Club - Server Running")
    print(" Open in Browser: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
