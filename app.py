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

st.title("📈 Dashboard Kinh Tế Vĩ Mô & Trợ Lý AI")
st.markdown("---")

# ==========================================
# 2. CẤU HÌNH SIDEBAR (ĐƯỜNG DẪN NGROK)
# ==========================================
st.sidebar.header("⚙️ Cấu hình Kết nối AI")
ngrok_url = st.sidebar.text_input(
    "Đường dẫn Ngrok (URL)", 
    placeholder="https://xxx-xxx.ngrok-free.dev",
    help="Nhập địa chỉ ngrok public trỏ đến LM Studio trên máy tính của bạn."
)

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

    # --- CỘT PHẢI: CHATBOT AI CHẠY LOCAL (CÓ KHUNG TRƯỢT) ---
    with col2:
        st.subheader("🤖 Trợ lý AI Phân tích số liệu")
        
        # Khởi tạo lịch sử chat trong session_state
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # 🎯 TẠO KHUNG CUỘN CỐ ĐỊNH (Chiều cao 500px)
        # Khung này giúp tin nhắn tự trượt lên trên và có thanh cuộn để xem lại
        chat_container = st.container(height=500)

        # Hiển thị lại các câu trả lời cũ BÊN TRONG khung cuộn
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Khung nhập câu hỏi (nằm bên dưới khung cuộn)
        if prompt := st.chat_input("Hỏi tôi về xu hướng lạm phát hoặc phân tích số liệu..."):
            
            # 1. Hiển thị ngay câu hỏi của user vào khung cuộn
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)
            
            # Lưu vào lịch sử chat
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Kiểm tra xem đã nhập đường dẫn Ngrok chưa
            if not ngrok_url:
                st.warning("⚠️ Vui lòng cấu hình 'Đường dẫn Ngrok' ở Sidebar bên trái!")
                st.stop()

            # RAG Engine: Trích xuất 15 dòng dữ liệu mới nhất để AI tham chiếu
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

            # Chuẩn hóa đường dẫn URL Ngrok
            clean_url = ngrok_url.strip().rstrip('/')
            
            try:
                # Khởi tạo kết nối tới LM Studio qua Ngrok
                client = OpenAI(
                    base_url=f"{clean_url}/v1",
                    api_key="lm-studio"
                )

                # Gọi AI và hiển thị hiệu ứng load ngầm
                with st.spinner("Đang gửi truy vấn đến LM Studio..."):
                    response = client.chat.completions.create(
                        model="local-model",
                        messages=[
                            {"role": "system", "content": system_instruction},
                            *st.session_state.messages
                        ],
                        temperature=0.2
                    )
                    
                    ai_response = response.choices[0].message.content
                
                # 2. Hiển thị câu trả lời của AI BÊN TRONG khung cuộn (Sẽ tự động đẩy các tin nhắn cũ trượt lên)
                with chat_container:
                    with st.chat_message("assistant"):
                        st.markdown(ai_response)
                
                # Lưu câu trả lời của AI vào lịch sử chat
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                
            except Exception as e:
                # Hiển thị thông báo lỗi chi tiết
                st.error(f"""
                **⚠️ LỖI KẾT NỐI CHI TIẾT:** 
                
                The endpoint `{clean_url}` is offline hoặc không thể phản hồi.
                
                `ERR_NGROK_3200` / ConnectionError
                """)
                
                st.info("""
                **💡 Các bước tự kiểm tra nhanh:**
                
                1. **Trên phần mềm LM Studio:** Bạn đã chọn một Model AI ở thanh menu trên cùng và bấm tải (load) nó chưa?
                2. **Kiểm tra cổng:** LM Studio đã chuyển thành cổng `1235` (hoặc cổng bạn đang cấu hình) và đang hiện nút màu đỏ **'Stop Server'** chưa?
                3. **Kiểm tra màn hình Ngrok:** Màn hình CMD của Ngrok có đang chạy và hiển thị đúng đường dẫn không?
                """)
