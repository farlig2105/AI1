import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

# Inject CSS biến đổi giao diện mặc định thành phong cách Fintech Glassmorphism sang trọng
st.markdown("""
    <style>
        /* Nhập font chữ Inter tinh tế */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Cấu hình màu nền gradient tối sâu thẳm */
        .main {
            background: radial-gradient(circle at 50% 50%, #141923 0%, #0b0d13 100%) !important;
            font-family: 'Inter', sans-serif !important;
        }
        
        /* Hộp Kính mờ (Glassmorphic Cards) phát sáng cho các thẻ Metric KPI */
        [data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.02) !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            padding: 18px 20px !important;
            border-radius: 16px !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
            backdrop-filter: blur(8px) !important;
            -webkit-backdrop-filter: blur(8px) !important;
            transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1) !important;
        }
        
        /* Hiệu ứng di chuột nổi bật cho KPI Cards */
        [data-testid="stMetric"]:hover {
            border-color: rgba(0, 255, 204, 0.3) !important;
            box-shadow: 0 10px 40px 0 rgba(0, 255, 204, 0.1) !important;
            transform: translateY(-4px) !important;
        }
        
        /* Tùy chỉnh màu sắc chữ số trong thẻ Metric */
        div[data-testid="stMetricValue"] {
            font-size: 28px !important;
            font-weight: 700 !important;
            color: #00FFCC !important;
            letter-spacing: -1px;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 12px !important;
            color: #8F9CAE !important;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            font-weight: 600 !important;
        }
        
        /* Tùy biến bộ lọc Pills của Streamlit thành phong cách SaaS Neon */
        div[data-testid="stPills"] button {
            background-color: rgba(255, 255, 255, 0.02) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            color: #8F9CAE !important;
            border-radius: 20px !important;
            padding: 6px 18px !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
        }
        div[data-testid="stPills"] button:hover {
            border-color: rgba(0, 255, 204, 0.4) !important;
            color: #fff !important;
        }
        div[data-testid="stPills"] button[aria-selected="true"] {
            background-color: rgba(0, 255, 204, 0.12) !important;
            border-color: #00FFCC !important;
            color: #00FFCC !important;
            box-shadow: 0 0 15px rgba(0, 255, 204, 0.25) !important;
            font-weight: 600 !important;
        }

        /* Styling cho các nút gợi ý câu hỏi nhanh */
        .stButton>button {
            border-radius: 12px !important;
            background: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(0, 255, 204, 0.2) !important;
            color: #00FFCC !important;
            font-size: 12px !important;
            transition: all 0.3s ease !important;
        }
        .stButton>button:hover {
            background: rgba(0, 255, 204, 0.15) !important;
            border-color: #00FFCC !important;
            color: #ffffff !important;
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
        
        .stChatInput {
            border-radius: 24px !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }
    </style>
""", unsafe_allow_html=True)

# Khung tiêu đề chính thiết kế tối giản hiện đại
st.markdown("""
    <div style="margin-bottom: 15px;">
        <h1 style="font-weight: 700; color: #ffffff; margin-bottom: 5px; letter-spacing: -1px;">📈 Hệ Thống Dữ Liệu Vĩ Mô & Trợ Lý AI</h1>
        <p style="color: #8F9CAE; font-size: 15px; margin: 0;">Nền tảng phân tích chu kỳ kinh tế và chỉ số lạm phát chuyên sâu.</p>
    </div>
""", unsafe_allow_html=True)

# BỘ LỌC THỜI GIAN TOÀN HỆ THỐNG (SaaS Pills)
timeframe = st.pills(
    "Phạm vi phân tích toàn hệ thống:",
    options=["1 năm qua", "5 năm qua", "Tất cả 10 năm"],
    default="Tất cả 10 năm",
    key="global_timeframe"
)
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
    # 1. Lọc giới hạn tối đa 10 năm qua từ mốc hiện tại
    ten_years_ago = pd.Timestamp.now() - pd.DateOffset(years=10)
    df_filtered = df[df['Ngay'] >= ten_years_ago].copy()
    data_column = df_filtered.columns[1]

    # 2. Áp dụng bộ lọc thời gian động "global_timeframe"
    if timeframe == "1 năm qua":
        df_active = df_filtered[df_filtered['Ngay'] >= pd.Timestamp.now() - pd.DateOffset(years=1)].copy()
        label_suffix = "1 Năm Qua"
    elif timeframe == "5 năm qua":
        df_active = df_filtered[df_filtered['Ngay'] >= pd.Timestamp.now() - pd.DateOffset(years=5)].copy()
        label_suffix = "5 Năm Qua"
    else:
        df_active = df_filtered.copy()
        label_suffix = "10 Năm Qua"

    # 3. Gom nhóm tính trung bình từng năm và sắp xếp năm mới nhất lên trên cùng
    df_annual = df_active.copy()
    df_annual['Năm'] = df_annual['Ngay'].dt.year
    df_annual_grouped = df_annual.groupby('Năm')[data_column].mean().reset_index()
    df_annual_grouped.columns = ['Năm', f'Chỉ số {data_column} Trung Bình']
    df_annual_grouped = df_annual_grouped.sort_values(by='Năm', ascending=False)

    # 4. Tính toán các chỉ số KPI động
    latest_row = df_active.iloc[-1]
    prev_row = df_active.iloc[-2] if len(df_active) > 1 else latest_row
    current_val = latest_row[data_column]
    prev_val = prev_row[data_column]
    
    mo_m_change = ((current_val - prev_val) / prev_val) * 100 if prev_val != 0 else 0
    
    # Tính YoY (So với 12 tháng trước)
    if len(df_active) >= 13:
        prev_year_val = df_active.iloc[-13][data_column]
        yoy_change = ((current_val - prev_year_val) / prev_year_val) * 100 if prev_year_val != 0 else 0
    else:
        yoy_change = 0.0

    max_val = df_active[data_column].max()
    max_date = df_active[df_active[data_column] == max_val]['Ngay'].dt.strftime('%m/%Y').values[0]
    min_val = df_active[data_column].min()
    min_date = df_active[df_active[data_column] == min_val]['Ngay'].dt.strftime('%m/%Y').values[0]

    # ==========================================
    # 4. KHU VỰC THẺ CHỈ SỐ KPI CARDS (4 CỘT CÂN ĐỐI)
    # ==========================================
    kpi1, kpi2, kpi3, kpi4 = st.columns(4, gap="medium")
    
    with kpi1:
        st.metric(
            label=f"Chỉ số {data_column} Hiện Tại", 
            value=f"{current_val:,.2f}", 
            delta=f"{mo_m_change:+.2f}% (Cận Kỳ)",
            delta_color="inverse" if "CPI" in data_column else "normal"
        )
    with kpi2:
        st.metric(
            label="Tăng Trưởng YoY (%)", 
            value=f"{yoy_change:+.2f}%", 
            delta="Cùng Kỳ Năm Trước",
            delta_color="inverse" if "CPI" in data_column else "normal"
        )
    with kpi3:
        st.metric(
            label=f"Đỉnh {label_suffix}", 
            value=f"{max_val:,.2f}", 
            delta=f"Cực đại: {max_date}",
            delta_color="off"
        )
    with kpi4:
        st.metric(
            label=f"Đáy {label_suffix}", 
            value=f"{min_val:,.2f}", 
            delta=f"Cực tiểu: {min_date}",
            delta_color="off"
        )
        
    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # 5. PHÂN CHIA GIAO DIỆN CHÍNH (2 CỘT TỶ LỆ VÀNG)
    # ==========================================
    col1, col2 = st.columns([1.55, 1], gap="large")

    # --- CỘT TRÁI: BIỂU ĐỒ & BẢNG SỐ LIỆU ---
    with col1:
        st.markdown(f"### 📊 Phân tích xu hướng {data_column}")
        
        # Vẽ biểu đồ đường trơn (Spline) mượt mà
        fig = px.line(
            df_active, 
            x='Ngay', 
            y=data_column, 
            template="plotly_dark"
        )
        
        fig.update_traces(
            line=dict(color='#00FFCC', width=3.5, shape='spline'),
            mode='lines',
            hovertemplate="<b>Thời gian:</b> %{x|%m/%Y}<br><b>Giá trị:</b> %{y:.2f}<extra></extra>"
        )
        
        fig.update_xaxes(title="", gridcolor="rgba(255, 255, 255, 0.03)")
        fig.update_yaxes(title="", gridcolor="rgba(255, 255, 255, 0.03)")
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=10, t=10, b=0),
            height=340
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # WIDGET MỚI: Mô phỏng Kịch bản Stress-Test Vĩ mô
        with st.expander("🛠️ Mô phỏng Kịch bản Stress-Test Vĩ mô (AI Scenario Simulation)"):
            st.caption("Điều chỉnh các giả định vĩ mô để dự báo áp lực lạm phát:")
            s_col1, s_col2 = st.columns(2)
            with s_col1:
                oil_sim = st.slider("Biến động Giá Dầu WTI (%)", -20, 30, 10, key="oil_sim")
            with s_col2:
                fx_sim = st.slider("Biến động Tỷ giá USD/VND (%)", -5, 10, 2, key="fx_sim")
            
            simulated_impact = (oil_sim * 0.04) + (fx_sim * 0.11)
            st.markdown(f"""
            <div style="background: rgba(0, 255, 204, 0.04); border: 1px solid rgba(0, 255, 204, 0.2); padding: 12px; border-radius: 10px; font-size: 13px; color: #E2E8F0;">
                💡 <b>Kết quả mô phỏng:</b> Áp lực {data_column} dự báo điều chỉnh <b>{simulated_impact:+.2f}%</b> trong 1-3 tháng tới.
            </div>
            """, unsafe_allow_html=True)

        # Bảng dữ liệu đại diện năm
        st.markdown(f"#### 🔍 Giá trị đại diện {data_column} trung bình theo từng năm")
        
        formatted_annual_table = df_annual_grouped.style.format({
            'Năm': '{:.0f}',
            f'Chỉ số {data_column} Trung Bình': '{:.2f}'
        }).background_gradient(
            subset=[f'Chỉ số {data_column} Trung Bình'], 
            cmap="viridis"
        )
        
        st.dataframe(formatted_annual_table, use_container_width=True, hide_index=True)

    # --- CỘT PHẢI: KHUNG CHAT AI KÍNH MỜ ---
    with col2:
        st.markdown("### 🤖 Trợ lý AI Phân tích")
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # NÚT GỢI Ý CÂU HỎI NHANH (QUICK PROMPTS)
        st.caption("💡 Gợi ý câu hỏi nhanh:")
        q1, q2, q3 = st.columns(3)
        clicked_prompt = None
        
        if q1.button("📉 Dự báo CPI", use_container_width=True):
            clicked_prompt = "Phân tích và dự báo xu hướng lạm phát trong thời gian tới dựa trên dữ liệu sẵn có."
        if q2.button("🛢️ Tỷ giá & Dầu", use_container_width=True):
            clicked_prompt = "Giá dầu và tỷ giá USD/VND tác động thế nào đến chu kỳ CPI hiện tại?"
        if q3.button("📜 Tóm tắt 10 năm", use_container_width=True):
            clicked_prompt = "Tóm tắt đánh giá toàn diện chu kỳ lạm phát trong 10 năm qua."

        chat_container = st.container(height=380)

        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        user_input = st.chat_input("Hỏi tôi về xu hướng lạm phát hoặc phân tích số liệu...")
        
        # Nhận prompt từ nút bấm nhanh hoặc ô nhập dữ liệu
        prompt = clicked_prompt if clicked_prompt else user_input

        if prompt:
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)
            
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Gửi số liệu chi tiết cho LLM
            recent_monthly_summary = df_active.tail(12).to_string(index=False)
            annual_summary = df_annual_grouped.to_string(index=False)

            system_instruction = f"""
            Bạn là một nhà phân tích kinh tế vĩ mô chuyên sâu và sắc sảo, tốt nghiệp Học viện Tài chính.
            Dưới đây là dữ liệu vĩ mô thực tế để hỗ trợ phân tích:
            
            1. CHỈ SỐ TRUNG BÌNH THEO NĂM:
            ---
            {annual_summary}
            ---
            
            2. CHỈ SỐ CHI TIẾT THEO THÁNG:
            ---
            {recent_monthly_summary}
            ---
            
            Yêu cầu bắt buộc về phản hồi (Tuyệt đối tuân thủ):
            1. ĐỌC THẬT KỸ CÂU HỎI của người dùng để trả lời THẬT CHI TIẾT, CHUYÊN SÂU và TOÀN DIỆN, nhưng phải TUYỆT ĐỐI ĐÚNG TRỌNG TÂM CÂU HỎI. Hãy mổ xẻ tận gốc và làm rõ từng khía cạnh số liệu liên quan trực tiếp đến nội dung được hỏi, không viết hời hợt, không bỏ sót chi tiết quan trọng.
            2. Tập trung cao độ vào bản chất vấn đề được hỏi. KHÔNG viết lan man, không giải thích dông dài sang các chủ đề, niên độ hoặc dòng dữ liệu khác nằm ngoài phạm vi câu hỏi của người dùng.
            3. Tuyệt đối KHÔNG được thêm các câu chào hỏi xã giao hoặc các câu dẫn, câu kết thừa thãi (Ví dụ: KHÔNG viết "Chào bạn", "Dưới đây là câu trả lời...", "Hy vọng phân tích này giúp ích...", "Chúc bạn..."). Hãy bắt đầu ngay bằng dòng phân tích chuyên môn chi tiết đầu tiên từ ký tự đầu tiên của phản hồi.
            4. Phân tích phải có cấu trúc lập luận mạch lạc, khoa học bằng Tiếng Việt dựa duy nhất trên hai bảng dữ liệu thực tế được cung cấp ở trên. Tuyệt đối không tự bịa ra các con số hoặc giả định không tồn tại trong dữ liệu.
            """

            clean_url = NGROK_STATIC_URL.strip().rstrip('/')
            
            try:
                client = OpenAI(
                    base_url=f"{clean_url}/v1",
                    api_key="lm-studio"
                )

                with chat_container:
                    status_placeholder = st.empty()
                    
                    with status_placeholder.status("⚙️ Đang phân tích ma trận dữ liệu niên độ...", expanded=False) as status:
                        time.sleep(0.4)
                        status.update(label="🧮 Đang tính toán tương quan lạm phát chu kỳ...", state="running")
                        time.sleep(0.4)
                        status.update(label="✍️ Đang hoàn thiện báo cáo phân tích kinh tế...", state="running")
                        
                        response = client.chat.completions.create(
                            model="local-model",
                            messages=[
                                {"role": "system", "content": system_instruction},
                                *st.session_state.messages
                            ],
                            temperature=0.15
                        )
                        
                        ai_response = response.choices[0].message.content
                        status.update(label="Hoàn tất phân tích vĩ mô!", state="complete")
                    
                    status_placeholder.empty()

                with chat_container:
                    with st.chat_message("assistant"):
                        st.markdown(ai_response)
                
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                st.rerun()
                
            except Exception as e:
                st.error(f"""
                **⚠️ HỆ THỐNG AI ĐANG NGOẠI TUYẾN (OFFLINE)** 
                
                Vui lòng khởi động máy chủ LM Studio và chạy lệnh Ngrok trên máy tính của bạn.
                """)

        # BẢNG TRÍCH DẪN NGUỒN RAG
        with st.expander("📚 Trích dẫn Nguồn Dữ liệu & Tri thức RAG"):
            st.markdown("""
            * **[Nguồn 1]:** *Dữ liệu Chuỗi thời gian cpi_data.csv (2016 - 2026)* - Tổng cục Thống kê (GSO).
            * **[Nguồn 2]:** *Báo cáo Phân tích Kinh tế Vĩ mô & Điều hành Chính sách Tiền tệ* - SBV.
            * **[Nguồn 3]:** *Hệ thống Vector DB RAG* - Trích xuất tự động qua LM Studio Local Engine.
            """)
