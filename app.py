import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN WEB
# ==========================================
st.set_page_config(
    page_title="Hệ thống Dữ liệu Vĩ mô & AI",
    layout="wide"
)

st.title("📈 Dashboard Kinh Tế Vĩ Mô & Trợ Lý AI (Cloud Engine)")
st.markdown("---")

# ==========================================
# 2. ĐỌC DỮ LIỆU TỪ FILE CSV
# ==========================================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('cpi_data.csv', parse_dates=['Ngay'])
        df = df.sort_values(by='Ngay')
        return df
    except FileNotFoundError:
        st.error("⚠️ Không tìm thấy file 'cpi_data.csv' trong mã nguồn!")
        return None

df = load_data()

if df is not None:
    data_column = df.columns[1]

    # ==========================================
    # 3. CHIA GIAO DIỆN LÀM 2 CỘT (LAYOUT)
    # ==========================================
    col1, col2 = st.columns([3, 2])

    # --- CỘT TRÁI: BIỂU ĐỒ & BẢNG SỐ LIỆU ---
    with col1:
        st.subheader(f"📊 Biểu đồ biến động {data_column}")
        
        fig = px.line(
            df, 
            x='Ngay', 
            y=data_column, 
            title=f"Lịch sử biến động {data_column} từ 2020 đến nay",
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("🔍 Xem bảng dữ liệu chi tiết"):
            st.dataframe(df, use_container_width=True)

    # --- CỘT PHẢI: CHATBOT AI CHẠY 24/7 ---
    with col2:
        st.subheader("🤖 Trợ lý AI Phân tích số liệu")
        
        # Kiểm tra xem người dùng đã cấu hình Secrets trên Streamlit chưa
        if "GEMINI_API_KEY" not in st.secrets:
            st.error("⚠️ Lỗi: Chưa tìm thấy 'GEMINI_API_KEY' trong mục Secrets của Streamlit Cloud!")
            st.info("Vui lòng vào Settings -> Secrets trên Streamlit Cloud để cấu hình khóa API của bạn.")
            st.stop()

        api_key = st.secrets["GEMINI_API_KEY"]

        # Khởi tạo lịch sử chat
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Hiển thị lại các câu trả lời cũ
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Khung chat chính
        if prompt := st.chat_input("Hỏi tôi về xu hướng lạm phát hoặc phân tích số liệu..."):
            st.chat_message("user").markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            # RAG Engine: Trích xuất 15 dòng dữ liệu mới nhất để AI tham chiếu
            latest_data_summary = df.tail(15).to_string(index=False)

            # Đóng gói chỉ thị hệ thống và dữ liệu bảng vào một chuỗi ngữ cảnh
            context_instruction = f"""Bạn là một nhà phân tích kinh tế vĩ mô sắc sảo, tốt nghiệp Học viện Tài chính.
Hãy sử dụng bảng số liệu CPI mới nhất sau đây để phân tích và trả lời câu hỏi của người dùng:
---
{latest_data_summary}
---
Yêu cầu:
1. Ưu tiên sử dụng số liệu thực tế phía trên để phân tích nếu câu hỏi liên quan đến số liệu hoặc xu hướng.
2. Trả lời ngắn gọn, trực diện, chuyên nghiệp bằng Tiếng Việt.
3. Tuyệt đối không tự bịa ra các con số không có trong bảng dữ liệu trên.
"""

            # Chuyển đổi lịch sử chat sang định dạng tương thích của Google Gemini
            contents = []
            
            # 1. Đưa các đoạn hội thoại cũ vào (trừ tin nhắn cuối cùng vừa gõ)
            for msg in st.session_state.messages[:-1]:
                role = "user" if msg["role"] == "user" else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg["content"]}]
                })
            
            # 2. Đưa tin nhắn cuối cùng kèm theo Chỉ dẫn + Dữ liệu RAG vào cuối để AI tập trung xử lý
            final_user_content = f"{context_instruction}\n\n**Câu hỏi của người dùng:** {prompt}"
            contents.append({
                "role": "user",
                "parts": [{"text": final_user_content}]
            })

            # Cấu hình dữ liệu gửi đi (Payload) - Bỏ hoàn toàn trường systemInstruction gây lỗi tương thích!
            payload = {
                "contents": contents,
                "generationConfig": {
                    "temperature": 0.2
                }
            }

            headers = {
                "Content-Type": "application/json"
            }

            try:
                with st.spinner("AI đang phân tích số liệu trên Cloud..."):
                    # Thử gọi API phiên bản ổn định v1 trước
                    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
                    response = requests.post(url, json=payload, headers=headers)
                    response_json = response.json()

                    # Nếu lỗi 404, tự động chuyển hướng sang v1beta làm dự phòng
                    if "error" in response_json and response_json["error"].get("code") == 404:
                        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                        response = requests.post(url, json=payload, headers=headers)
                        response_json = response.json()

                    # Kiểm tra kết quả phản hồi cuối cùng
                    if "error" in response_json:
                        error_msg = response_json["error"].get("message", "Lỗi không xác định")
                        st.error(f"⚠️ Lỗi từ Google API: {error_msg}")
                    else:
                        ai_response = response_json["candidates"][0]["content"]["parts"][0]["text"]
                        
                        with st.chat_message("assistant"):
                            st.markdown(ai_response)
                        st.session_state.messages.append({"role": "assistant", "content": ai_response})
                        
            except Exception as e:
                st.error(f"⚠️ Đã xảy ra lỗi khi kết nối với AI Cloud: {e}")
