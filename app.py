from flask import Flask, render_template, request, jsonify
import os
import json
import gspread
from google.oauth2.service_account import Credentials
import uuid

app = Flask(__name__)

# 구글 시트를 매번 신선하게 불러오는 안정적인 함수
def get_sheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    google_creds = os.environ.get('GOOGLE_CREDENTIALS')
    
    if google_creds:
        # Render 환경
        creds_dict = json.loads(google_creds)
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    else:
        # 로컬 테스트 환경
        creds = Credentials.from_service_account_file('secret.json', scopes=scope)
        
    client = gspread.authorize(creds)
    # 🚨 중요: 구글 스프레드시트 이름이 '근태달력DB'와 띄어쓰기까지 정확히 일치해야 합니다!
    return client.open('근태달력DB').sheet1

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/events', methods=['GET'])
def get_events():
    try:
        sheet = get_sheet()
        records = sheet.get_all_records()
        
        events = []
        default_statuses = ['연차', '출장', '교육', '세미나', '휴무']
        
        for row in records:
            name = str(row.get('name', ''))
            status = str(row.get('status', ''))
            detail = str(row.get('detail', ''))
            color = str(row.get('color', ''))
            
            final_title = name
            if status != '직접선택' and status not in default_statuses:
                final_title += f"-{status}"
            if detail:
                final_title += f"-{detail}"
            
            events.append({
                'id': str(row.get('id', '')),
                'title': final_title,
                'start': str(row.get('start_date', '')),
                'end': str(row.get('end_date', '')),
                'backgroundColor': color,
                'borderColor': color,
                'extendedProps': {
                    'name': name,
                    'status': status,
                    'detail': detail
                }
            })
        return jsonify(events)
    except Exception as e:
        print(f"조회 에러: {e}")
        return jsonify([])

@app.route('/add', methods=['POST'])
def add_event():
    try:
        data = request.json
        new_id = str(uuid.uuid4())[:8]
        
        row_data = [
            new_id,
            data.get('name'),
            data.get('status'),
            data.get('detail'),
            data.get('color'),
            data.get('start'),
            data.get('end')
        ]
        
        sheet = get_sheet()
        sheet.append_row(row_data)
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"등록 에러: {e}") # Render 로그에 상세 에러를 찍어줍니다
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/delete', methods=['POST'])
def delete_event():
    try:
        data = request.json
        target_id = str(data.get('id'))
        
        sheet = get_sheet()
        records = sheet.get_all_records()
        
        for i, row in enumerate(records):
            if str(row.get('id')) == target_id:
                sheet.delete_rows(i + 2)
                break
                
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"삭제 에러: {e}")
        return jsonify({'status': 'error'})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)