import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# 페이지 설정 (넓은 화면 사용)
st.set_page_config(page_title="팀 근태 현황 달력", layout="wide")

# 1. DB 초기화
def init_db():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS schedules_streamlit (
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

init_db()

# 2. 데이터 추가/조회/삭제 함수
def add_schedule(name, status, detail, color, start, end):
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("INSERT INTO schedules_streamlit (name, status, detail, color, start_date, end_date) VALUES (?, ?, ?, ?, ?, ?)", 
              (name, status, detail, color, start, end))
    conn.commit()
    conn.close()

def get_schedules():
    conn = sqlite3.connect('attendance.db')
    df = pd.read_sql("SELECT * FROM schedules_streamlit", conn)
    conn.close()
    return df

def delete_schedule(schedule_id):
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("DELETE FROM schedules_streamlit WHERE id = ?", (schedule_id,))
    conn.commit()
    conn.close()

# 3. 사이드바 (입력 및 조작부)
st.sidebar.title("📌 팀 근태 관리")

name_list = ["🏢 회사 휴무", "장현준", "김동기", "최상철", "강택규", "김현준", "권회준", "김민호", "오진영", "강한수", "최지훈", "박현수", "테이", "라나"]
selected_name = st.sidebar.selectbox("1. 인원 선택", name_list)

status_options = {
    "연차": "#FF6B6B",
    "출장": "#4DABF7",
    "교육": "#51CF66",
    "세미나": "#FCC419",
    "휴무": "#868e96",
    "직접선택": "#845EF7"
}

selected_status = st.sidebar.selectbox("2. 근태 선택", list(status_options.keys()))

custom_color = "#845EF7"
if selected_status == "직접선택":
    custom_color = st.sidebar.color_picker("막대기 색상 선택", "#845EF7")
    final_color = custom_color
else:
    final_color = status_options[selected_status]

detail_text = st.sidebar.text_input("상세내용 (선택)", placeholder="예: 태국, 재택, 오전 등")

st.sidebar.markdown("---")
st.sidebar.subheader("📅 기간 선택 및 등록")
start_date = st.sidebar.date_input("시작일", datetime.now())
end_date = st.sidebar.date_input("종료일 (마지막 날까지)", datetime.now())

if st.sidebar.button("✨ 일정 등록하기", type="primary"):
    if start_date > end_date:
        st.sidebar.error("시작일이 종료일보다 클 수 없습니다.")
    else:
        # 종료일까지 포함하기 위해 +1일 처리 (드래그 느낌 구현)
        real_end = end_date + timedelta(days=1)
        add_schedule(selected_name, selected_status, detail_text, final_color, str(start_date), str(real_end))
        st.sidebar.success("일정이 등록되었습니다!")
        st.rerun()

# 4. 메인 화면 (달력 및 현황판)
st.title("🗓️ 팀 근태 현황판")

df = get_schedules()

if not df.empty:
    st.markdown("### 📋 등록된 일정 목록 (삭제 관리)")
    for index, row in df.iterrows():
        # 타이틀 조합
        title = row['name']
        if row['status'] != '직접선택':
            title += f"-{row['status']}"
        if row['detail']:
            title += f"-{row['detail']}"
            
        col1, col2, col3 = st.columns([3, 3, 1])
        with col1:
            st.markdown(f"**{title}**")
        with col2:
            st.caption(f"기간: {row['start_date']} ~ {(datetime.strptime(row['end_date'], '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')}")
        with col3:
            if st.button("🗑️ 삭제", key=f"del_{row['id']}"):
                delete_schedule(row['id'])
                st.rerun()
else:
    st.info("등록된 일정이 없습니다. 좌측에서 일정을 등록해 보세요!")