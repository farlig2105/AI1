import streamlit as st
import pandas as pd
import plotly.express as px
import time
from openai import OpenAI

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN WEB & CSS CUSTOM
# ==========================================
st.set_page_config(
    page_title="Hệ thống Dữ liệu Vĩ mô & AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Custom CSS để "SaaS hóa" toàn bộ giao diện
st.markdown("""
    <style>
        /* Tùy chỉnh font chữ và nền tối cao cấp */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        html, body, [data-testid="stSidebar"] {
            font-family: 'Inter', sans-serif;
        }
        
        /* Làm đẹp các khối Metric (Chỉ số) */
        div[data-testid="stMetricValue"] {
            font-size: 28px !important;
            font-weight: 700 !important;
            color: #00FFCC !important;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 14px !important;
            color: #AEB7C2 !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        /* Hiệu ứng bo góc và viền mờ cho các Container */
        div[data-testid="stVerticalBlock"] > div {
            border-radius: 12px;
        }
        
        /* Tùy biến thanh cuộn đẹp mắt */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: rgba(255,255,255,0.02);
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(0, 255, 204, 0.3);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(0, 255, 204, 0.6);
        }
    </style>
""", unsafe_allow_html=True)

st.title("📈 Dashboard Kinh Tế Vĩ Mô & Trợ Lý AI")
st.markdown("---")

# ==========================================
# 2. ĐƯỜNG DẪN NGROK CỐ ĐỊNH 
# ==========================================
NGROK_STATIC_URL = "https://TÊN_MIỀN_CỦA_BẠN.ngrok-free.app"

# Thiết kế Sidebar tinh gọn, chuyên nghiệp
st.sidebar.markdown("### 🖥️ MÁY CHỦ HỆ THỐNG")
st.sidebar.markdown(
    f"""
    <div style="background-color: rgba(0, 255, 204, 0.05); border: 1px solid rgba(0, 255, 204, 0.2); padding: 15px; border-radius: 10px;">
        <span style="color: #00FFCC; font-weight: bold;">● AI ENGINE ONLINE</span><br>
        <small style="color: #888;">Ngrok Endpoint:</small><br>
        <code style="color: #fff; font-size: 11px;">{NGROK_STATIC_URL}</code>
    </div>
    """, 
    unsafe_allow_html=True
)
st.sidebar.markdown("---")
st.sidebar.caption("Phát triển bởi Nhóm nghiên cứu Kinh tế vĩ mô.")

# ==========================================
# 3. ĐỌC & XỬ LÝ DỮ LIỆU TỪ FILE CSV
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
    # Lọc dữ liệu trong vòng 10 năm trở lại đây
    ten_years_ago = pd.Timestamp.now() - pd.DateOffset(years=10)
    df_filtered = df[df['Ngay'] >= ten_years_ago].copy()
    data_column = df_filtered.columns[1]

    # Tính toán các chỉ số vĩ mô cho KPI Cards
    latest_row = df_filtered.iloc[-1]
    prev_row = df_filtered.iloc[-2] if len(df_filtered) > 1 else latest_row
    
    current_val = latest_row[data_column]
    prev_val = prev_row[data_column]
    
    # Tính % biến động so với kỳ trước (Tháng trước)
    mo_m_change = ((current_val - prev_val) / prev_val) * 100 if prev_val != 0 else 0
    
    max_val = df_filtered[data_column].max()
    max_date = df_filtered[df_filtered[data_column] == max_val]['Ngay'].dt.strftime('%m/%Y').values[0]
    
    min_val = df_filtered[data_column].min()
    min_date = df_filtered[df_filtered[data_column] == min_val]['Ngay'].dt.strftime('%m/%Y').values[0]

    # ==========================================
    # 4. KHU VỰC THẺ CHỈ SỐ KPI CARDS (MỚI)
    # ==========================================
    kpi1, kpi2, kpi3 = st.columns(3)
    
    with kpi1:
        st.metric(
            label=f"Chỉ số {data_column} Hiện Tại", 
            value=f"{current_val:,.2f}", 
            delta=f"{mo_m_change:+.2f}% (MoM)",
            delta_color="inverse" if "CPI" in data_column else "normal"  # CPI tăng thì đỏ (inverse), giảm thì xanh
        )
    with kpi2:
        st.metric(
            label="Đỉnh 10 Năm Qua", 
            value=f"{max_val:,.2f}", 
            delta=f"Đạt vào tháng {max_date}",
            delta_color="off"
        )
    with kpi3:
        st.metric(
            label="Đáy 10 Năm Qua", 
            value=f"{min_val:,.2f}", 
            delta=f"Đạt vào tháng {min_date}",
            delta_color="off"
        )
        
    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # 5. CHIA GIAO DIỆN LÀM 2 CỘT (LAYOUT CHÍNH)
    # ==========================================
    col1, col2 = st.columns([1.6, 1], gap="large")

    # --- CỘT TRÁI: BIỂU ĐỒ NEON & BẢNG SỐ LIỆU CHUYỂN SẮC ---
    with col1:
        st.markdown(f"### 📊 Phân tích xu hướng {data_column}")
        
        # Thiết kế biểu đồ chuẩn Fintech
        fig = px.line(
            df_filtered, 
            x='Ngay', 
            y=data_column, 
            template="plotly_dark"
        )
        
        # Nâng cấp đường vẽ thành Neon Cyan, bo cong spline mềm mại
        fig.update_traces(
            line=dict(color='#00FFCC', width=3.5, shape='spline'),
            mode='lines',
            hovertemplate="<b>Thời gian:</b> %{x|%m/%Y}<br><b>Giá trị:</b> %{y:.2f}<extra></extra>"
        )
        
        # Thêm các nút lọc nhanh thời gian tiện lợi
        fig.update_xaxes(
            title="",
            gridcolor="rgba(255, 255, 255, 0.05)",
            rangeslider_visible=False,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1 năm qua", step="year", stepmode="backward"),
                    dict(count=5, label="5 năm qua", step="year", stepmode="backward"),
                    dict(step="all", label="Tất cả 10 năm")
                ]),
                bgcolor="rgba(30, 34, 42, 0.9)",
                activecolor="#00FFCC",
                font=dict(color="#fff", size=11)
            )
        )
        
        fig.update_yaxes(
            title="",
            gridcolor="rgba(255, 255, 255, 0.05)"
        )
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=10, t=20, b=0),
            height=380
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # Bảng dữ liệu định dạng màu nhiệt độ (Gradient) chuyên nghiệp
        with st.expander("🔍 Bảng số liệu vĩ mô chi tiết (Gradient Heatmap)"):
            
            # Làm đẹp bảng bằng Pandas Styler (Chuyển đổi định dạng ngày và màu sắc ô)
            styled_df = df_filtered.copy()
            styled_df['Ngay'] = styled_df['Ngay'].dt.strftime('%Y-%m-%d')
            
            # Áp dụng dải màu chuyển sắc sang trọng từ lục sang đỏ dựa trên giá trị chỉ số
            formatted_table = styled_df.style.format({
                data_column: "{:.2f}"
            }).background_gradient(
                subset=[data_column], 
                cmap="coolwarm"  # Đỏ cho giá trị cao, Xanh cho giá trị thấp
            )
            
            st.dataframe(formatted_table, use_container_width=True, height=250)
            
            # Tích hợp nút tải nhanh CSV ngay dưới bảng
            csv_data = df_filtered.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Tải xuống dữ liệu sạch (.CSV)",
                data=csv_data,
                file_name=f"{data_column.lower()}_10years_clean.csv",
                mime="text/csv"
            )

    # --- CỘT PHẢI: CHATBOT AI KHUNG KÍNH MỜ ---
    with col2:
        st.markdown("### 🤖 Trợ lý AI Phân tích")
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Khung cuộn cố định được bo viền cực đẹp
        chat_container = st.container(height=450)

        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        if prompt := st.chat_input("Hỏi tôi về xu hướng lạm phát hoặc phân tích số liệu..."):
            
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)
            
            st.session_state.messages.append({"role": "user", "content": prompt})

            # RAG Engine: Lấy dữ liệu 10 năm để gửi cho AI (đầy đủ thông tin hơn bản cũ)
            latest_data_summary = df_filtered.to_string(index=False)

            system_instruction = f"""
            Bạn là một nhà phân tích kinh tế vĩ mô sắc sảo, tốt nghiệp Học viện Tài chính.
            Dưới đây là số liệu thực tế trong 10 năm qua để bạn phân tích:
            ---
            {latest_data_summary}
            ---
            Yêu cầu:
            1. Ưu tiên sử dụng số liệu thực tế phía trên để phân tích xu hướng hoặc trả lời câu hỏi của người dùng.
            2. Trả lời ngắn gọn, trực diện, luận điểm sắc bén bằng Tiếng Việt.
            3. Tuyệt đối không tự bịa ra các con số không có trong bảng dữ liệu trên.
            """

            clean_url = NGROK_STATIC_URL.strip().rstrip('/')
            
            try:
                client = OpenAI(
                    base_url=f"{clean_url}/v1",
                    api_key="lm-studio"
                )

                # Hiệu ứng đổi chữ trạng thái cực ngầu
                with chat_container:
                    status_placeholder = st.empty()
                    
                    with status_placeholder.status("⚙️ Đang trích xuất chuỗi thời gian CPI...", expanded=False) as status:
                        time.sleep(0.5)
                        status.update(label="🧮 Đang tính toán ma trận lạm phát lũy kế...", state="running")
                        time.sleep(0.5)
                        status.update(label="✍️ Đang tổng hợp báo cáo kinh tế vĩ mô...", state="running")
                        
                        response = client.chat.completions.create(
                            model="local-model",
                            messages=[
                                {"role": "system", "content": system_instruction},
                                *st.session_state.messages
                            ],
                            temperature=0.2
                        )
                        
                        ai_response = response.choices[0].message.content
                        status.update(label="Kết xuất hoàn tất!", state="complete")
                    
                    status_placeholder.empty()

                with chat_container:
                    with st.chat_message("assistant"):
                        st.markdown(ai_response)
                
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                
            except Exception as e:
                st.error(f"""
                **⚠️ HỆ THỐNG AI ĐANG NGOẠI TUYẾN (OFFLINE)** 
                
                Vui lòng khởi động máy chủ LM Studio và chạy lệnh Ngrok trên máy tính của bạn.
                """)
