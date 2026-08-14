from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS schedules_v5 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            status TEXT,
            detail TEXT,
            color TEXT,
            start_date TEXT,
            end_date TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/events', methods=['GET'])
def get_events():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("SELECT id, name, status, detail, color, start_date, end_date FROM schedules_v5")
    rows = c.fetchall()
    conn.close()
    
    events = []
    default_statuses = ['연차', '출장', '교육', '세미나', '휴무']
    
    for row in rows:
        name = row[1]
        status = row[2]
        detail = row[3]
        color = row[4]
        
        final_title = name
        if status != '직접선택' and status not in default_statuses:
            final_title += f"-{status}"
        if detail:
            final_title += f"-{detail}"
        
        events.append({
            'id': row[0],
            'title': final_title,
            'start': row[5],
            'end': row[6],
            'backgroundColor': color,
            'borderColor': color,
            'extendedProps': {
                'name': name,
                'status': status,
                'detail': detail
            }
        })
    return jsonify(events)

@app.route('/add', methods=['POST'])
def add_event():
    data = request.json
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("INSERT INTO schedules_v5 (name, status, detail, color, start_date, end_date) VALUES (?, ?, ?, ?, ?, ?)", 
              (data.get('name'), data.get('status'), data.get('detail'), data.get('color'), data.get('start'), data.get('end')))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/delete', methods=['POST'])
def delete_event():
    data = request.json
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("DELETE FROM schedules_v5 WHERE id = ?", (data.get('id'),))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    init_db()
    # 클라우드 배포용 포트 설정
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)