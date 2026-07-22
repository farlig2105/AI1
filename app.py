import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from openai import OpenAI

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN WEB & CSS SIÊU PREMIUM
# ==========================================
st.set_page_config(
    page_title="Hệ thống Dữ liệu Vĩ mô & AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS nâng cấp hiệu ứng Glow, Glassmorphism và layout cân đối
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }
        
        .main {
            background: radial-gradient(circle at 50% 0%, #1a2035 0%, #0a0c10 100%) !important;
        }
        
        .glass-card {
            background: rgba(255, 255, 255, 0.025);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 20px;
            backdrop-filter: blur(12px);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            margin-bottom: 15px;
        }
        
        [data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.02) !important;
            border: 1px solid rgba(0, 255, 204, 0.15) !important;
            padding: 16px 20px !important;
            border-radius: 16px !important;
            backdrop-filter: blur(10px) !important;
            transition: all 0.3s ease !important;
        }
        [data-testid="stMetric"]:hover {
            border-color: rgba(0, 255, 204, 0.4) !important;
            box-shadow: 0 0 25px rgba(0, 255, 204, 0.15) !important;
            transform: translateY(-2px) !important;
        }
        div[data-testid="stMetricValue"] {
            font-size: 26px !important;
            font-weight: 800 !important;
            color: #00FFCC !important;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 11px !important;
            color: #94A3B8 !important;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600 !important;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: rgba(255, 255, 255, 0.03);
            padding: 6px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        .stTabs [data-baseweb="tab"] {
            height: 40px;
            border-radius: 8px;
            color: #94A3B8;
            font-weight: 600;
            font-size: 13px;
            border: none !important;
        }
        .stTabs [aria-selected="true"] {
            background-color: rgba(0, 255, 204, 0.15) !important;
            color: #00FFCC !important;
            border: 1px solid rgba(0, 255, 204, 0.3) !important;
        }
        
        div[data-testid="stPills"] button {
            background-color: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            color: #94A3B8 !important;
            border-radius: 20px !important;
            font-size: 12px !important;
        }
        div[data-testid="stPills"] button[aria-selected="true"] {
            background-color: rgba(0, 255, 204, 0.15) !important;
            border-color: #00FFCC !important;
            color: #00FFCC !important;
        }

        .ai-welcome {
            border: 1px dashed rgba(0, 255, 204, 0.3);
            background: rgba(0, 255, 204, 0.02);
            border-radius: 14px;
            padding: 20px;
            text-align: center;
            margin-top: 10px;
        }
        
        ::-webkit-scrollbar { width: 4px; height: 4px; }
        ::-webkit-scrollbar-thumb { background: rgba(0, 255, 204, 0.2); border-radius: 4px; }
    </style>
""", unsafe_allow_html=True)

# Header chính
h_col1, h_col2 = st.columns([3, 1])
with h_col1:
    st.markdown("""
        <div style="margin-bottom: 10px;">
            <h2 style="font-weight: 800; color: #ffffff; margin: 0; letter-spacing: -0.5px;">
                📈 Hệ Thống Dữ Liệu Vĩ Mô & Trợ Lý AI
            </h2>
            <p style="color: #64748B; font-size: 14px; margin: 4px 0 0 0;">
                Nền tảng phân tích chu kỳ kinh tế, lạm phát & mô phỏng kịch bản vĩ mô.
            </p>
        </div>
    """, unsafe_allow_html=True)
with h_col2:
    st.markdown("""
        <div style="text-align: right; padding-top: 5px;">
            <span style="background: rgba(16, 185, 129, 0.15); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.3); padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">
                🟢 Live Data System
            </span>
        </div>
    """, unsafe_allow_html=True)

# BỘ LỌC THỜI GIAN
timeframe = st.pills(
    "Phạm vi phân tích:",
    options=["1 năm qua", "5 năm qua", "Tất cả 10 năm"],
    default="Tất cả 10 năm",
    key="global_timeframe"
)
st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

# ==========================================
# 2. CONFIG NGROK CỐ ĐỊNH
# ==========================================
NGROK_STATIC_URL = "https://decode-thigh-dinginess.ngrok-free.dev"

st.sidebar.markdown("### 🖥️ HỆ THỐNG MÁY CHỦ")
st.sidebar.markdown(
    f"""
    <div style="background: rgba(0, 255, 204, 0.03); border: 1px solid rgba(0, 255, 204, 0.15); padding: 15px; border-radius: 12px;">
        <span style="color: #00FFCC; font-weight: 700; font-size: 13px;">● AI ENGINE ONLINE</span><br>
        <small style="color: #64748B; display: block; margin-top: 4px;">Ngrok Static Endpoint:</small>
        <code style="color: #E2E8F0; font-size: 10px; word-break: break-all; background: rgba(0,0,0,0.3); padding: 3px 6px; border-radius: 4px; display: block; margin-top: 4px;">{NGROK_STATIC_URL}</code>
    </div>
    """, 
    unsafe_allow_html=True
)

if st.sidebar.button("🧹 Xóa lịch sử hội thoại AI", use_container_width=True):
    st.session_state.messages = []
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("Phát triển bởi Nhóm nghiên cứu Học viện Tài chính.")

# ==========================================
# 3. ĐỌC & XỬ LÝ DỮ LIỆU
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
    ten_years_ago = pd.Timestamp.now() - pd.DateOffset(years=10)
    df_filtered = df[df['Ngay'] >= ten_years_ago].copy()
    data_column = df_filtered.columns[1]

    if timeframe == "1 năm qua":
        df_active = df_filtered[df_filtered['Ngay'] >= pd.Timestamp.now() - pd.DateOffset(years=1)].copy()
        label_suffix = "1 Năm Qua"
    elif timeframe == "5 năm qua":
        df_active = df_filtered[df_filtered['Ngay'] >= pd.Timestamp.now() - pd.DateOffset(years=5)].copy()
        label_suffix = "5 Năm Qua"
    else:
        df_active = df_filtered.copy()
        label_suffix = "10 Năm Qua"

    df_active['SMA12'] = df_active[data_column].rolling(window=12, min_periods=1).mean()

    df_annual = df_active.copy()
    df_annual['Năm'] = df_annual['Ngay'].dt.year
    df_annual_grouped = df_annual.groupby('Năm')[data_column].mean().reset_index()
    df_annual_grouped.columns = ['Năm', f'Chỉ số {data_column} Trung Bình']
    df_annual_grouped = df_annual_grouped.sort_values(by='Năm', ascending=False)

    latest_row = df_active.iloc[-1]
    prev_row = df_active.iloc[-2] if len(df_active) > 1 else latest_row
    current_val = latest_row[data_column]
    prev_val = prev_row[data_column]
    mo_m_change = ((current_val - prev_val) / prev_val) * 100 if prev_val != 0 else 0
    
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
    # 4. KPI CARDS
    # ==========================================
    kpi1, kpi2, kpi3, kpi4 = st.columns(4, gap="small")
    with kpi1:
        st.metric(label=f"Chỉ số {data_column}", value=f"{current_val:,.2f}", delta=f"{mo_m_change:+.2f}% (Cận Kỳ)")
    with kpi2:
        st.metric(label="Tăng Trưởng YoY", value=f"{yoy_change:+.2f}%", delta="So với cùng kỳ")
    with kpi3:
        st.metric(label=f"Đỉnh {label_suffix}", value=f"{max_val:,.2f}", delta=f"Tháng {max_date}", delta_color="off")
    with kpi4:
        st.metric(label=f"Đáy {label_suffix}", value=f"{min_val:,.2f}", delta=f"Tháng {min_date}", delta_color="off")

    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # 5. BỐ TRÍ LAYOUT
    # ==========================================
    col1, col2 = st.columns([1.3, 1], gap="large")

    with col1:
        tab_chart, tab_table, tab_sim, tab_insights = st.tabs([
            "📈 Biểu đồ Chu kỳ", 
            "📊 Bảng Niên độ", 
            "🛠️ Mô phỏng Kịch bản",
            "📌 Highlight Vĩ mô"
        ])

        with tab_chart:
            show_sma = st.checkbox("Hiển thị Đường trung bình động SMA (12 tháng)", value=True)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_active['Ngay'], y=df_active[data_column],
                mode='lines', name=data_column,
                line=dict(color='#00FFCC', width=3)
            ))
            if show_sma:
                fig.add_trace(go.Scatter(
                    x=df_active['Ngay'], y=df_active['SMA12'],
                    mode='lines', name='SMA 12 Tháng',
                    line=dict(color='#FF007A', width=2, dash='dot')
                ))

            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=10, r=10, t=10, b=10),
                height=380,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            fig.update_xaxes(gridcolor="rgba(255, 255, 255, 0.05)")
            fig.update_yaxes(gridcolor="rgba(255, 255, 255, 0.05)")
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        with tab_table:
            st.markdown("##### Số liệu trung bình từng năm")
            formatted_annual_table = df_annual_grouped.style.format({
                'Năm': '{:.0f}',
                f'Chỉ số {data_column} Trung Bình': '{:.2f}'
            }).background_gradient(subset=[f'Chỉ số {data_column} Trung Bình'], cmap="viridis")
            
            st.dataframe(formatted_annual_table, use_container_width=True, height=280, hide_index=True)
            
            csv_data = df_active.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Tải xuống dữ liệu CSV chi tiết",
                data=csv_data,
                file_name="du_lieu_vi_mo_cpi.csv",
                mime="text/csv",
                use_container_width=True
            )

        with tab_sim:
            st.markdown("##### 🧪 Stress-Test Áp lực Lạm phát")
            st.caption("Điều chỉnh tham số giả định để mô phỏng tác động:")
            
            sc1, sc2 = st.columns(2)
            with sc1:
                oil_sim = st.slider("Biến động Giá Dầu WTI (%)", -20, 30, 10)
            with sc2:
                fx_sim = st.slider("Tỷ giá USD/VND (%)", -5, 10, 2)
                
            sim_impact = (oil_sim * 0.04) + (fx_sim * 0.11)
            projected_cpi = current_val * (1 + sim_impact/100)
            
            # ĐÃ ĐƯỢC SỬA: Thay $\rightarrow$ bằng mũi tên unicode → thuần túy
            st.markdown(f"""
                <div class="glass-card" style="margin-top:10px;">
                    <div style="font-size:13px; color:#8F9CAE;">DỰ BÁO ĐIỀU CHỈNH CPI CẬN KỲ</div>
                    <div style="font-size:24px; font-weight:700; color:{'#FF4B4B' if sim_impact > 0 else '#00FFCC'};">
                        {sim_impact:+.2f}% &rarr; ~{projected_cpi:,.2f} điểm
                    </div>
                    <small style="color:#64748B;">Mô hình ước lượng dựa trên trọng số biến động năng lượng & hàng hóa nhập khẩu.</small>
                </div>
            """, unsafe_allow_html=True)

        with tab_insights:
            st.markdown("##### 📌 Tóm tắt Điểm nóng Vĩ mô")
            st.markdown(f"""
            * **Biến động đỉnh điểm:** Chỉ số đạt đỉnh **{max_val:,.2f}** vào tháng **{max_date}**.
            * **Tốc độ tăng trưởng:** Mức tăng YoY hiện tại đạt **{yoy_change:+.2f}%**.
            * **Xu hướng trung hạn:** Đường SMA 12 tháng đang {'đi lên' if df_active['SMA12'].iloc[-1] > df_active['SMA12'].iloc[-6] else 'đi ngang/giảm'}, phản ánh áp lực chu kỳ tích lũy.
            """)

    # --- CỘT PHẢI: AI ASSISTANT ---
    with col2:
        st.markdown("### 🤖 Trợ lý AI Phân tích")
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        st.caption("💡 Câu hỏi gợi ý:")
        q1, q2, q3 = st.columns(3)
        clicked_prompt = None
        if q1.button("📉 Dự báo CPI", use_container_width=True):
            clicked_prompt = "Phân tích và dự báo xu hướng lạm phát cận kỳ dựa trên dữ liệu sẵn có."
        if q2.button("🛢️ Giá dầu & Tỷ giá", use_container_width=True):
            clicked_prompt = "Biến động giá dầu và tỷ giá tác động thế nào đến lạm phát Việt Nam?"
        if q3.button("📜 Tóm tắt 10 năm", use_container_width=True):
            clicked_prompt = "Tóm tắt toàn diện chu kỳ lạm phát trong 10 năm qua."

        chat_container = st.container(height=380)

        with chat_container:
            if len(st.session_state.messages) == 0:
                st.markdown("""
                    <div class="ai-welcome">
                        <div style="font-size: 32px; margin-bottom: 5px;">🤖</div>
                        <div style="color: #ffffff; font-weight: 700; font-size: 15px;">Tôi là Trợ lý AI Vĩ mô</div>
                        <p style="color: #64748B; font-size: 12px; margin-top: 5px;">
                            Sẵn sàng giải đáp các câu hỏi về chu kỳ lạm phát, CPI, chỉ số kinh tế dựa trên dữ liệu thực tế từ GSO & SBV.
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

        user_input = st.chat_input("Hỏi AI về xu hướng CPI hoặc phân tích vĩ mô...")
        prompt = clicked_prompt if clicked_prompt else user_input

        if prompt:
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)
            
            st.session_state.messages.append({"role": "user", "content": prompt})

            recent_monthly_summary = df_active.tail(12).to_string(index=False)
            annual_summary = df_annual_grouped.to_string(index=False)

            system_instruction = f"""
            Bạn là một nhà phân tích kinh tế vĩ mô chuyên sâu, tốt nghiệp Học viện Tài chính.
            Dữ liệu vĩ mô thực tế:
            
            TRUNG BÌNH THEO NĂM:
            {annual_summary}
            
            CHI TIẾT 12 THÁNG GẦN NHẤT:
            {recent_monthly_summary}
            
            Yêu cầu phản hồi:
            1. Đọc kỹ câu hỏi, phân tích CHI TIẾT, CHUYÊN SÂU và TOÀN DIỆN đúng trọng tâm.
            2. Không chào hỏi xã giao thừa thãi (Không viết "Chào bạn", "Dưới đây là..."). Bắt đầu ngay bằng nội dung phân tích.
            3. Lập luận dựa trên số liệu thực tế được cung cấp.
            """

            clean_url = NGROK_STATIC_URL.strip().rstrip('/')
            
            try:
                client = OpenAI(
                    base_url=f"{clean_url}/v1",
                    api_key="lm-studio"
                )

                with chat_container:
                    status_placeholder = st.empty()
                    with status_placeholder.status("⚙️ Đang xử lý ma trận dữ liệu...", expanded=False) as status:
                        time.sleep(0.3)
                        status.update(label="🧮 Đang tính toán tương quan vĩ mô...", state="running")
                        
                        response = client.chat.completions.create(
                            model="local-model",
                            messages=[
                                {"role": "system", "content": system_instruction},
                                *st.session_state.messages
                            ],
                            temperature=0.15
                        )
                        ai_response = response.choices[0].message.content
                        status.update(label="Hoàn tất!", state="complete")
                    
                    status_placeholder.empty()

                with chat_container:
                    with st.chat_message("assistant"):
                        st.markdown(ai_response)
                
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                st.rerun()
                
            except Exception as e:
                st.error("⚠️ Không thể kết nối với AI Engine. Vui lòng kiểm tra lại Ngrok / LM Studio!")

        with st.expander("📚 Nguồn Dữ liệu & Tri thức RAG"):
            st.markdown("""
            * **[GSO]:** Tổng cục Thống kê Việt Nam (*cpi_data.csv*).
            * **[SBV]:** Ngân hàng Nhà nước Việt Nam.
            * **[RAG Engine]:** LM Studio Local Vector Indexing.
            """)
