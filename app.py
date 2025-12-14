# app.py
import streamlit as st
import requests

API_BASE = "https://backend-practice-z7d5.onrender.com"  # 替换为你的 Render 地址
st.set_page_config(page_title="📝 我的笔记", layout="wide")

if "token" not in st.session_state:
    st.session_state.token = ""

col1, col2 = st.columns(2)

with col1:
    st.subheader("會員註冊")
    email = st.text_input("電子信箱")
    password = st.text_input("密碼", type="password")
    if st.button("會員註冊"):
        try:
            r = requests.post(f"{API_BASE}/auth/register", 
                            json={"email": email, "password": password})
            if r.status_code == 200:
                st.success("會員註冊成功！請登入")
            else:
                st.error(f"註冊失敗: {r.json()['detail']}")
        except Exception as e:
            st.error(f"錯誤: {e}")

with col2:
    st.subheader("使用者登入")
    login_email = st.text_input("帳號 (電子信箱)")
    login_pw = st.text_input("密碼", type="password", key="login_pw")
    if st.button("登入"):
        try:
            # 🔴 删除旧代码:
            # r = requests.post(f"{API_BASE}/auth/token",
            #                 data={"username": login_email, "password": login_pw})
            
            # 🟢 修正后的代码:
            # 1. 使用 params (对应 Swagger 的 query)
            # 2. 字段名改成 email (对应 Swagger 的定义)
            r = requests.post(
                f"{API_BASE}/auth/token",
                params={"email": login_email, "password": login_pw} 
            )

            if r.status_code == 200:
                st.session_state.token = r.json()["access_token"]
                st.success("登入成功！")
                st.rerun()
            else:
                # 建议打印出具体的错误信息，方便调试
                st.error(f"登入失敗: {r.text}") 
        except Exception as e:
            st.error(f"登入錯誤: {e}")

if st.session_state.token:
    st.divider()
    st.header("📝 我的筆記")
    
    with st.expander("➕ 新增筆記", expanded=False):
        title = st.text_input("標題")
        content = st.text_area("內容")
        if st.button("儲存筆記"):
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            r = requests.post(f"{API_BASE}/notes/",
                            json={"title": title, "content": content},
                            headers=headers)
            if r.status_code == 200:
                st.success("筆記已儲存！")
                st.rerun()
            else:
                st.error("儲存失敗")
    
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        notes = requests.get(f"{API_BASE}/notes/", headers=headers).json()
        
        for note in notes:
            with st.container(border=True):
                st.subheader(note["title"])
                st.write(note["content"])
                st.caption(f"建立時間: {note['created_at']}")
    except Exception as e:
        st.error(f"讀取筆記失敗: {e}")