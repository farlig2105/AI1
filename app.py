import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN WEB (DARK MODE & WIDE)
# ==========================================
st.set_page_config(
    page_title="Hệ thống Dữ liệu Vĩ mô & AI (Cloud Version)",
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.title("📈 Dashboard Kinh Tế Vĩ Mô & Trợ Lý AI")
st.markdown("---")

# ==========================================
# 2. CẤU HÌNH SIDEBAR ĐỂ NHẬP URL NGROK
# ==========================================
st.sidebar.header("⚙️ Cấu hình kết nối GPU")
st.sidebar.markdown(
    """
    **Hướng dẫn kết nối với LM Studio ở nhà:**
    1. Chạy lệnh `ngrok http 1235` trên máy tính cá nhân.
    2. Copy đường dẫn `https://...ngrok-free.dev` hoặc `.app` được cấp.
    3. Dán đường dẫn đó vào ô bên dưới.
    """
)

# Ô nhập URL Ngrok động
ngrok_input = st.sidebar.text_input(
    "Đường dẫn Ngrok (HTTPS URL):",
    value="https://xxxx-xxxx-xxxx.ngrok-free.app",
    help="Dán URL sinh ra từ lệnh ngrok trên máy của bạn vào đây."
).strip()

# TỰ ĐỘNG SỬA ĐƯỜNG DẪN THÔNG MINH
base_url = ngrok_input

# Nếu người dùng quên nhập "https://", hệ thống sẽ tự điền vào
if base_url and not base_url.startswith("http"):
    base_url = "https://" + base_url

# Tự động thêm "/v1" vào cuối để kết nối đúng định dạng API của LM Studio
if base_url and not base_url.endswith("/v1"):
    base_url = base_url.rstrip("/") + "/v1"

# ==========================================
# 3. ĐỌC DỮ LIỆU TỪ FILE CSV
# ==========================================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('cpi_data.csv', parse_dates=['Ngay'])
        df = df.sort_values(by='Ngay')
        return df
    except FileNotFoundError:
        st.error("⚠️ Không tìm thấy file 'cpi_data.csv'. Vui lòng chạy file 'get_data.py' trên máy để tạo dữ liệu!")
        return None

df = load_data()

if df is not None:
    data_column = df.columns[1]

    # ==========================================
    # 4. CHIA GIAO DIỆN LÀM 2 CỘT (LAYOUT)
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

    # --- CỘT PHẢI: CHATBOT AI ---
    with col2:
        st.subheader("🤖 Trợ lý AI Phân tích số liệu")
        
        # Chấp nhận cả ngrok-free.app và ngrok-free.dev
        is_valid_ngrok = "ngrok-free" in ngrok_input
        
        if not is_valid_ngrok:
            st.warning("⚠️ Hãy nhập đường dẫn Ngrok hợp lệ vào thanh Sidebar bên trái để kích hoạt Chatbot!")
        else:
            st.success(f"🔌 Đang kết nối trực tiếp với GPU ở nhà qua: {base_url}")

            # 🎯 CẢI TIẾN: Thêm default_headers để vượt qua trang chặn của Ngrok miễn phí
            client = OpenAI(
                base_url=base_url, 
                api_key="lm-studio",
                default_headers={"ngrok-skip-browser-warning": "true"}
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
                    with st.spinner("AI đang xử lý trên GPU cục bộ của bạn..."):
                        response = client.chat.completions.create(
                            model="local-model",
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
                    # 🎯 CẢI TIẾN: In trực tiếp chi tiết lỗi của hệ thống ra màn hình để chẩn đoán
                    st.error(f"⚠️ LỖI KẾT NỐI CHI TIẾT: {e}")
                    
                    st.info(
                        "💡 **Các bước tự kiểm tra nhanh:**\n"
                        "1. **Trên phần mềm LM Studio:** Bạn đã chọn một Model AI ở thanh menu trên cùng và bấm tải (load) nó chưa?\n"
                        "2. **Kiểm tra cổng:** LM Studio đã chuyển thành cổng `1235` và đang hiện nút 'Stop Server' (màu đỏ - tức là server đang chạy) chưa?\n"
                        "3. **Kiểm tra màn hình Ngrok:** Khi bạn bấm gửi tin nhắn trên Web, màn hình đen của Ngrok ở máy tính của bạn có nhảy thêm dòng chữ nào báo nhận tín hiệu không?"
                    )
