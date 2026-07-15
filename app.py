import streamlit as st
import pandas as pd
import numpy as np

# Thiết lập cấu hình trang hiển thị rộng (Wide mode)
st.set_page_config(
    page_title="Dashboard Kinh Tế Vĩ Mô & Trợ Lý AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 1. SIDEBAR (Cấu hình kết nối AI) ---
with st.sidebar:
    st.subheader("⚙️ Cấu hình Kết nối AI")
    ngrok_url = st.text_input(
        "Đường dẫn Ngrok (URL)", 
        value="https://decode-thigh-dinginess.ngrok-free.app"
    )

# --- 2. GIAO DIỆN CHÍNH (Chia làm 2 cột) ---
st.title("📈 Dashboard Kinh Tế Vĩ Mô & Trợ Lý AI")
st.markdown("---")

col1, col2 = st.columns([1.2, 1])

# --- CỘT LỆCH TRÁI: Biểu đồ CPI ---
with col1:
    st.subheader("📊 Biểu đồ biến động CPI")
    st.caption("Lịch sử biến động CPI từ 2020 đến nay")
    
    # Giả lập dữ liệu CPI giống như trong ảnh của bạn
    years = np.arange(1950, 2027)
    cpi_values = 30 + (years - 1950)**1.55 * 0.45
    df_cpi = pd.DataFrame({"Năm": years, "CPI": cpi_values})
    
    # Hiển thị biểu đồ đường
    st.line_chart(df_cpi.set_index("Năm"))
    
    # Bảng dữ liệu chi tiết thu gọn
    with st.expander("🔍 Xem bảng dữ liệu chi tiết"):
        st.write(df_cpi)


# --- CỘT LỆCH PHẢI: Trợ lý AI (Khu vực đã được sửa đổi) ---
with col2:
    st.subheader("💬 Trợ lý AI Phân tích số liệu")

    # Khởi tạo bộ nhớ lưu trữ lịch sử chat nếu chưa có
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": "Chào bạn! Tôi rất vui được giúp đỡ. Bạn cần hỗ trợ gì về kinh tế vĩ mô hay phân tích dữ liệu?"},
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": "Vâng, tôi sẵn sàng lắng nghe. Bạn muốn tôi phân tích khía cạnh nào của nền kinh tế?\n\nBạn có thể đặt câu hỏi liên quan đến xu hướng lạm phát (dựa trên dữ liệu CPI), chính sách tiền tệ, hay bất kỳ chủ đề vĩ mô nào khác nhé."},
            {"role": "user", "content": "chính sách không chính xác của chính phủ có thể ảnh hưởng như thế nào tới nền kinh tế?"},
            {"role": "assistant", "content": "Đây là một câu hỏi mang tính lý thuyết vĩ mô rất sâu sắc. Về bản chất, mọi chính sách kinh tế đều được xây dựng dựa trên các giả định về hành vi của chủ thể và trạng thái cân bằng của thị trường. Khi những giả định này sai lệch hoặc việc thực thi không phù hợp với điều kiện thực tế, tác động tiêu cực có thể lan tỏa rất mạnh mẽ qua nhiều kênh."}
        ]

    # KHÓA CHÍNH Ở ĐÂY: Tạo container với chiều cao cố định (ví dụ: 450px)
    # Thuộc tính `height` giúp kích hoạt thanh cuộn tự động khi tin nhắn vượt quá chiều cao này.
    chat_container = st.container(height=480)

    # Hiển thị toàn bộ lịch sử chat bên trong container cuộn
    with chat_container:
        for msg in st.session_state.messages:
            # Thiết lập avatar màu đỏ cho User và màu cam cho Assistant giống ảnh mẫu
            avatar_icon = "🔴" if msg["role"] == "user" else "🍊"
            with st.chat_message(msg["role"], avatar=avatar_icon):
                st.write(msg["content"])

    # Ô nhập câu hỏi của người dùng (nằm cố định phía dưới khung chat)
    if prompt := st.chat_input("Nhập câu hỏi của bạn ở đây..."):
        # 1. Thêm câu hỏi của User vào trạng thái session
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # 2. Xử lý logic gọi API/Ngrok của bạn ở đây để lấy câu trả lời từ AI
        # (Dưới đây là phản hồi giả lập để demo)
        dummy_ai_response = f"Hệ thống đã nhận được câu hỏi: '{prompt}'. Phản hồi đang được xử lý qua máy chủ kết nối tại: {ngrok_url}"
        
        # 3. Thêm phản hồi của AI vào trạng thái session
        st.session_state.messages.append({"role": "assistant", "content": dummy_ai_response})
        
        # Rerun lại app để cập nhật giao diện và tự động cuộn xuống tin nhắn mới nhất
        st.rerun()
