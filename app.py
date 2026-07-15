import streamlit as st
import pandas as pd
import plotly.express as px
import time
from openai import OpenAI

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN WEB & CSS SIÊU PREMIUM (1000x UI)
# ==========================================
st.set_page_config(
    page_title="Hệ thống Dữ liệu Vĩ mô & AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject CSS "ma thuật" để thay đổi toàn diện giao diện mặc định của Streamlit
st.markdown("""
    <style>
        /* Nhập font chữ Inter tinh tế */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Cấu hình màu nền gradient chuyển động chìm tối sang trọng */
        .main {
            background: radial-gradient(circle at 50% 50%, #141923 0%, #0b0d13 100%) !important;
            font-family: 'Inter', sans-serif !important;
        }
        
        /* Biến đổi các thẻ Metric mặc định thành các hộp Kính mờ (Glassmorphic Cards) phát sáng */
        [data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.02) !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            padding: 20px 25px !important;
            border-radius: 16px !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
            backdrop-filter: blur(8px) !important;
            -webkit-backdrop-filter: blur(8px) !important;
            transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1) !important;
        }
        
        /* Hiệu ứng di chuột cực bay bổng cho các thẻ KPI */
        [data-testid="stMetric"]:hover {
            border-color: rgba(0, 255, 204, 0.3) !important;
            box-shadow: 0 10px 40px 0 rgba(0, 255, 204, 0.1) !important;
            transform: translateY(-4px) !important;
        }
        
        /* Tùy chỉnh màu sắc và kích thước chữ trong thẻ Metric */
        div[data-testid="stMetricValue"] {
            font-size: 32px !important;
            font-weight: 700 !important;
            color: #00FFCC !important;
            letter-spacing: -1px;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 13px !important;
            color: #8F9CAE !important;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-weight: 600 !important;
        }
        
        /* Làm đẹp thanh cuộn khung chat mỏng nhẹ nghệ thuật */
        ::-webkit-scrollbar {
            width: 5px;
            height: 5px;
        }
        ::-webkit-scrollbar-track {
            background: transparent;
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(0, 255, 204, 0.2);
            border-radius: 10px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(0, 255, 204, 0.5);
        }
        
        /* Bo tròn góc cho thanh nhập chat nhập liệu */
        .stChatInput {
            border-radius: 24px !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }
    </style>
""", unsafe_allow_html=True)

# Khung tiêu đề chính thiết kế tối giản hiện đại
st.markdown("""
    <div style="margin-bottom: 25px;">
        <h1 style="font-weight: 700; color: #ffffff; margin-bottom: 5px; letter-spacing: -1px;">📈 Hệ Thống Dữ Liệu Vĩ Mô & Trợ Lý AI</h1>
        <p style="color: #8F9CAE; font-size: 15px; margin: 0;">Nền tảng phân tích chu kỳ kinh tế và chỉ số lạm phát chuyên sâu.</p>
    </div>
""", unsafe_allow_html=True)
st.markdown("---")

# ==========================================
# 2. ĐƯỜNG DẪN NGROK CỐ ĐỊNH (decode-thigh-dinginess)
# ==========================================
NGROK_STATIC_URL = "https://decode-thigh-dinginess.ngrok-free.dev"

# Thiết kế Sidebar tinh tế
st.sidebar.markdown("### 🖥️ MÁY CHỦ HỆ THỐNG")
st.sidebar.markdown(
    f"""
    <div style="background: rgba(0, 255, 204, 0.03); border: 1px solid rgba(0, 255, 204, 0.15); padding: 18px; border-radius: 14px; backdrop-filter: blur(5px);">
        <span style="color: #00FFCC; font-weight: 700; font-size: 14px;">● AI ENGINE ONLINE</span><br>
        <small style="color: #6C7A8C; display: block; margin-top: 5px;">Ngrok Endpoint:</small>
        <code style="color: #E2E8F0; font-size: 11px; word-break: break-all; background: rgba(0,0,0,0.2); padding: 2px 6px; border-radius: 4px; display: block; margin-top: 3px;">{NGROK_STATIC_URL}</code>
    </div>
    """, 
    unsafe_allow_html=True
)
st.sidebar.markdown("---")
st.sidebar.caption("Phát triển bởi Nhóm nghiên cứu Học viện Tài chính.")

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
    # Lọc dữ liệu gốc trong vòng 10 năm qua (phục vụ vẽ biểu đồ chi tiết)
    ten_years_ago = pd.Timestamp.now() - pd.DateOffset(years=10)
    df_filtered = df[df['Ngay'] >= ten_years_ago].copy()
    data_column = df_filtered.columns[1]

    # 🎯 TIẾN HÀNH GOM NHÓM TÍNH TRUNG BÌNH TỪNG NĂM (DÀNH CHO BẢNG SỐ LIỆU)
    df_annual = df_filtered.copy()
    df_annual['Năm'] = df_annual['Ngay'].dt.year
    # Tính trung bình và làm tròn 2 chữ số thập phân
    df_annual_grouped = df_annual.groupby('Năm')[data_column].mean().reset_index()
    df_annual_grouped.columns = ['Năm', f'Chỉ số {data_column} Trung Bình']

    # Tính toán chỉ số cho các thẻ KPI đầu trang
    latest_row = df_filtered.iloc[-1]
    prev_row = df_filtered.iloc[-2] if len(df_filtered) > 1 else latest_row
    current_val = latest_row[data_column]
    prev_val = prev_row[data_column]
    
    mo_m_change = ((current_val - prev_val) / prev_val) * 100 if prev_val != 0 else 0
    max_val = df_filtered[data_column].max()
    max_date = df_filtered[df_filtered[data_column] == max_val]['Ngay'].dt.strftime('%m/%Y').values[0]
    min_val = df_filtered[data_column].min()
    min_date = df_filtered[df_filtered[data_column] == min_val]['Ngay'].dt.strftime('%m/%Y').values[0]

    # ==========================================
    # 4. KHU VỰC THẺ CHỈ SỐ KPI CARDS (SIÊU ĐẸP)
    # ==========================================
    kpi1, kpi2, kpi3 = st.columns(3, gap="medium")
    
    with kpi1:
        st.metric(
            label=f"Chỉ số {data_column} Hiện Tại", 
            value=f"{current_val:,.2f}", 
            delta=f"{mo_m_change:+.2f}% (Cận Kỳ)",
            delta_color="inverse" if "CPI" in data_column else "normal"
        )
    with kpi2:
        st.metric(
            label="Đỉnh 10 Năm Qua", 
            value=f"{max_val:,.2f}", 
            delta=f"Cực đại vào tháng {max_date}",
            delta_color="off"
        )
    with kpi3:
        st.metric(
            label="Đáy 10 Năm Qua", 
            value=f"{min_val:,.2f}", 
            delta=f"Cực tiểu vào tháng {min_date}",
            delta_color="off"
        )
        
    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # 5. PHÂN CHIA GIAO DIỆN CHÍNH (2 CỘT TỶ LỆ VÀNG)
    # ==========================================
    col1, col2 = st.columns([1.55, 1], gap="large")

    # --- CỘT TRÁI: BIỂU ĐỒ CHI TIẾT & BẢNG TỔNG HỢP NĂM ---
    with col1:
        st.markdown(f"### 📊 Phân tích xu hướng {data_column}")
        
        # Biểu đồ đường vẽ mượt spline neon cyan phát sáng
        fig = px.line(
            df_filtered, 
            x='Ngay', 
            y=data_column, 
            template="plotly_dark"
        )
        
        fig.update_traces(
            line=dict(color='#00FFCC', width=3.5, shape='spline'),
            mode='lines',
            hovertemplate="<b>Thời gian:</b> %{x|%m/%Y}<br><b>Giá trị:</b> %{y:.2f}<extra></extra>"
        )
        
        fig.update_xaxes(
            title="",
            gridcolor="rgba(255, 255, 255, 0.03)",
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
            gridcolor="rgba(255, 255, 255, 0.03)"
        )
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=10, t=20, b=0),
            height=380
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # Bảng dữ liệu đại diện năm (Rút gọn tối đa, loại bỏ con lăn)
        st.markdown(f"#### 🔍 Giá trị đại diện {data_column} trung bình theo từng năm")
        
        # Áp dụng heatmap coolwarm thời thượng cho bảng gom nhóm
        formatted_annual_table = df_annual_grouped.style.format({
            'Năm': '{:.0f}',
            f'Chỉ số {data_column} Trung Bình': '{:.2f}'
        }).background_gradient(
            subset=[f'Chỉ số {data_column} Trung Bình'], 
            cmap="viridis" # Dải chuyển sắc lục-lam-vàng cực sáng trên nền dark mode
        )
        
        # Hiển thị bảng vừa khít (chỉ 10 dòng nên không bao giờ hiện thanh cuộn ngang dọc)
        st.dataframe(formatted_annual_table, use_container_width=True)
        
        # Nút tải xuống dữ liệu năm tinh gọn
        csv_annual_data = df_annual_grouped.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Xuất bảng tóm tắt năm (.CSV)",
            data=csv_annual_data,
            file_name=f"{data_column.lower()}_annual_averages.csv",
            mime="text/csv"
        )

    # --- CỘT PHẢI: KHUNG CHAT KÍNH MỜ ---
    with col2:
        st.markdown("### 🤖 Trợ lý AI Phân tích")
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Khung chứa hội thoại kính mờ tinh tế
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

            # RAG Engine: Gửi cả số liệu chi tiết và bảng trung bình năm để AI có góc nhìn sắc bén nhất
            recent_monthly_summary = df_filtered.tail(12).to_string(index=False)
            annual_summary = df_annual_grouped.to_string(index=False)

            system_instruction = f"""
            Bạn là một nhà phân tích kinh tế vĩ mô sắc sảo, tốt nghiệp Học viện Tài chính.
            Dưới đây là dữ liệu vĩ mô thực tế để hỗ trợ phân tích:
            
            1. CHỈ SỐ TRUNG BÌNH THEO NĂM (10 năm qua):
            ---
            {annual_summary}
            ---
            
            2. CHỈ SỐ CHI TIẾT THEO THÁNG (12 tháng gần nhất):
            ---
            {recent_monthly_summary}
            ---
            
            Yêu cầu:
            1. Phân tích xu hướng dài hạn dựa trên dữ liệu năm và biến động ngắn hạn dựa trên dữ liệu tháng.
            2. Trả lời ngắn gọn, trực diện, lập luận logic bằng Tiếng Việt.
            3. Tuyệt đối không tự bịa ra các con số không tồn tại trong hai bảng dữ liệu trên.
            """

            clean_url = NGROK_STATIC_URL.strip().rstrip('/')
            
            try:
                client = OpenAI(
                    base_url=f"{clean_url}/v1",
                    api_key="lm-studio"
                )

                # Hiệu ứng đổi trạng thái load động cực chất
                with chat_container:
                    status_placeholder = st.empty()
                    
                    with status_placeholder.status("⚙️ Đang phân tích ma trận dữ liệu niên độ...", expanded=False) as status:
                        time.sleep(0.5)
                        status.update(label="🧮 Đang tính toán tương quan lạm phát chu kỳ...", state="running")
                        time.sleep(0.5)
                        status.update(label="✍️ Đang hoàn thiện báo cáo phân tích kinh tế...", state="running")
                        
                        response = client.chat.completions.create(
                            model="local-model",
                            messages=[
                                {"role": "system", "content": system_instruction},
                                *st.session_state.messages
                            ],
                            temperature=0.2
                        )
                        
                        ai_response = response.choices[0].message.content
                        status.update(label="Hoàn tất phân tích vĩ mô!", state="complete")
                    
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
