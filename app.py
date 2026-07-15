import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI

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

        # Khởi tạo kết nối trực tiếp với Google Gemini (sử dụng giao diện tương thích OpenAI)
        client = OpenAI(
            api_key=st.secrets["GEMINI_API_KEY"],
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

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

            # RAG Engine: Trích xuất 15 dòng dữ liệu mới nhất
            latest_data_summary = df.tail(15).to_string(index=False)

            system_instruction = f"""
            Bạn là một nhà phân tích kinh tế vĩ mô sắc sảo.
            Dưới đây là 15 dòng số liệu mới nhất trong cơ sở dữ liệu của chúng ta:
            ---
            {latest_data_summary}
            ---
            Yêu cầu:
            1. Ưu tiên sử dụng số liệu thực tế phía trên để trả lời câu hỏi nếu liên quan.
            2. Trả lời ngắn gọn, trực diện bằng Tiếng Việt.
            3. Tuyệt đối không tự bịa ra các con số không có trong bảng dữ liệu trên.
            """

            try:
                with st.spinner("AI đang xử lý thông tin trên Cloud..."):
                    response = client.chat.completions.create(
                        model="gemini-1.5-flash", # Dòng model miễn phí, siêu nhanh và thông minh của Google
                        messages=[
                            {"role": "system", "content": system_instruction},
                            *st.session_state.messages
                        ],
                        temperature=0.2
                    )
                    
                    ai_response = response.choices[0].message.content
                
                with st.chat_message("assistant"):
                    st.markdown(ai_response)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                
            except Exception as e:
                st.error(f"⚠️ Đã xảy ra lỗi khi gọi AI Cloud: {e}")
