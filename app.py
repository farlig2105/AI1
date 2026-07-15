import streamlit as st
import pandas as pd
import plotly.express as px
import time  # Thêm thư viện time để làm hiệu ứng chuyển chữ mượt mà
from openai import OpenAI

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN WEB
# ==========================================
st.set_page_config(
    page_title="Hệ thống Dữ liệu Vĩ mô & AI",
    layout="wide"
)

st.title("📈 Dashboard Kinh Tế Vĩ Mô & Trợ Lý AI")
st.markdown("---")

# ==========================================
# 2. ĐƯỜNG DẪN NGROK CỐ ĐỊNH 
# ==========================================
# Hãy dán đường dẫn cố định của bạn vào đây:
NGROK_STATIC_URL = "https://decode-thigh-dinginess.ngrok-free.dev"

# Hiển thị trạng thái kết nối ở Sidebar
st.sidebar.header("⚙️ Trạng thái Hệ thống")
st.sidebar.success("🟢 Đã cấu hình máy chủ AI cố định")
st.sidebar.caption(f"Endpoint: {NGROK_STATIC_URL}")

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
        st.error("⚠️ Không tìm thấy file 'cpi_data.csv' trong mã nguồn!")
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

    # --- CỘT PHẢI: CHATBOT AI CÓ KHUNG CUỘN TRƯỢT ---
    with col2:
        st.subheader("🤖 Trợ lý AI Phân tích số liệu")
        
        # Khởi tạo lịch sử chat
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Khung cuộn cố định (Chiều cao 500px)
        chat_container = st.container(height=500)

        # Hiển thị lại các câu trả lời cũ
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Khung chat chính (Bên dưới khung cuộn)
        if prompt := st.chat_input("Hỏi tôi về xu hướng lạm phát hoặc phân tích số liệu..."):
            
            # Hiển thị ngay câu hỏi của user vào khung cuộn
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)
            
            st.session_state.messages.append({"role": "user", "content": prompt})

            # RAG Engine: Trích xuất 15 dòng dữ liệu mới nhất
            latest_data_summary = df.tail(15).to_string(index=False)

            system_instruction = f"""
            Bạn là một nhà phân tích kinh tế vĩ mô sắc sảo, tốt nghiệp Học viện Tài chính.
            Dưới đây là 15 dòng số liệu mới nhất trong cơ sở dữ liệu của chúng ta:
            ---
            {latest_data_summary}
            ---
            Yêu cầu:
            1. Ưu tiên sử dụng số liệu thực tế phía trên để trả lời câu hỏi nếu liên quan.
            2. Trả lời ngắn gọn, trực diện bằng Tiếng Việt.
            3. Tuyệt đối không tự bịa ra các con số không có trong bảng dữ liệu trên.
            """

            clean_url = NGROK_STATIC_URL.strip().rstrip('/')
            
            try:
                # Khởi tạo kết nối tới LM Studio qua link Ngrok cố định
                client = OpenAI(
                    base_url=f"{clean_url}/v1",
                    api_key="lm-studio"
                )

                # 🛠️ HIỆU ỨNG LOAD CHỮ CHUYỂN ĐỘNG LINH HOẠT
                with chat_container:
                    # Tạo một placeholder tạm thời để hiển thị trạng thái loading
                    status_placeholder = st.empty()
                    
                    with status_placeholder.status("🤖 Đang đọc dữ liệu CPI...", expanded=False) as status:
                        time.sleep(0.6)  # Tạo độ trễ ngắn để người dùng kịp nhìn chữ thay đổi
                        
                        status.update(label="🧮 Đang thực hiện tính toán...", state="running")
                        time.sleep(0.6)
                        
                        status.update(label="✍️ Đang đưa ra kết luận...", state="running")
                        
                        # Gọi API thực tế từ LM Studio
                        response = client.chat.completions.create(
                            model="local-model",
                            messages=[
                                {"role": "system", "content": system_instruction},
                                *st.session_state.messages
                            ],
                            temperature=0.2
                        )
                        
                        ai_response = response.choices[0].message.content
                        status.update(label="Đã hoàn thành phân tích!", state="complete")
                    
                    # Xoá bỏ hoàn toàn khung trạng thái load sau khi đã có câu trả lời
                    status_placeholder.empty()

                # Hiển thị câu trả lời chính thức của AI vào khung cuộn
                with chat_container:
                    with st.chat_message("assistant"):
                        st.markdown(ai_response)
                
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                
            except Exception as e:
                st.error(f"""
                **⚠️ KHÔNG THỂ KẾT NỐI ĐẾN MÁY CHỦ AI** 
                
                Hệ thống AI đang ngoại tuyến (Offline). 
                """)
                
                st.info(f"""
                **💡 Cách kích hoạt nhanh máy chủ:**
                
                1. Mở phần mềm **LM Studio** trên máy tính của bạn, chọn model và đảm bảo Server đã được bật (cổng `1235`).
                2. Mở CMD trên máy tính và chạy lệnh:
                   `ngrok http 1235 --domain={clean_url.replace("https://", "")}`
                """)
