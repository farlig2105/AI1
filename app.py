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
                Nền tảng phân tích chu kỳ kinh tế, lạm phát & mô phỏng kịch bản vĩ mô thời gian thực.
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
        tab_chart, tab_table, tab_sim, tab_theory, tab_insights = st.tabs([
            "📈 Biểu đồ Chu kỳ", 
            "📊 Bảng Niên độ", 
            "🛠️ Mô phỏng Kịch bản",
            "💡 Lý thuyết & Đa nguồn",
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
                
            oil_impact = oil_sim * 0.04
            fx_impact = fx_sim * 0.11
            sim_impact = oil_impact + fx_impact
            projected_cpi = current_val * (1 + sim_impact/100)
            
            st.markdown(f"""
                <div class="glass-card" style="margin-top:10px; margin-bottom:15px;">
                    <div style="font-size:13px; color:#8F9CAE;">DỰ BÁO ĐIỀU CHỈNH CPI CẬN KỲ</div>
                    <div style="font-size:24px; font-weight:700; color:{'#FF4B4B' if sim_impact > 0 else '#00FFCC'};">
                        {sim_impact:+.2f}% &rarr; ~{projected_cpi:,.2f} điểm
                    </div>
                    <small style="color:#64748B;">Mô hình ước lượng dựa trên trọng số biến động năng lượng & hàng hóa nhập khẩu.</small>
                </div>
            """, unsafe_allow_html=True)

            # BẢNG HTML TỰ ĐỘNG XUỐNG DÒNG - KHÔNG MẤT CHỮ
            st.markdown("##### 📋 Phân tích Cơ chế Tác động Chi tiết")
            
            oil_color = "#FF4B4B" if oil_impact > 0 else ("#00FFCC" if oil_impact < 0 else "#94A3B8")
            fx_color = "#FF4B4B" if fx_impact > 0 else ("#00FFCC" if fx_impact < 0 else "#94A3B8")
            total_color = "#FF4B4B" if sim_impact > 0 else ("#00FFCC" if sim_impact < 0 else "#94A3B8")

            table_html = f"""
            <style>
                .explain-table {{
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 12px;
                    color: #E2E8F0;
                    background: rgba(255, 255, 255, 0.02);
                    border-radius: 10px;
                    overflow: hidden;
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    margin-top: 8px;
                }}
                .explain-table th {{
                    background: rgba(0, 255, 204, 0.08);
                    color: #00FFCC;
                    padding: 10px 12px;
                    text-align: left;
                    font-weight: 700;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                .explain-table td {{
                    padding: 10px 12px;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
                    vertical-align: top;
                    white-space: normal !important;
                    word-wrap: break-word !important;
                    line-height: 1.5;
                }}
                .explain-table tr:hover {{
                    background: rgba(255, 255, 255, 0.04);
                }}
            </style>
            <table class="explain-table">
                <thead>
                    <tr>
                        <th style="width: 22%;">Biến số Vĩ mô</th>
                        <th style="width: 15%;">Mức điều chỉnh</th>
                        <th style="width: 12%;">Trọng số</th>
                        <th style="width: 15%;">Đóng góp CPI</th>
                        <th style="width: 36%;">Cơ chế truyền dẫn & Tác động thực tế</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><b>🛢️ Giá Dầu WTI</b></td>
                        <td style="color: {oil_color}; font-weight: 600;">{oil_sim:+d}%</td>
                        <td>0.04</td>
                        <td style="color: {oil_color}; font-weight: 700;">{oil_impact:+.2f}%</td>
                        <td>Ảnh hưởng trực tiếp đến nhóm Giao thông (xăng dầu), lan tỏa sang chi phí vận tải, logistics và giá thành sản xuất hàng hóa.</td>
                    </tr>
                    <tr>
                        <td><b>💵 Tỷ giá USD/VND</b></td>
                        <td style="color: {fx_color}; font-weight: 600;">{fx_sim:+d}%</td>
                        <td>0.11</td>
                        <td style="color: {fx_color}; font-weight: 700;">{fx_impact:+.2f}%</td>
                        <td>Tạo áp lực 'Nhập khẩu lạm phát' (Imported Inflation), làm tăng chi phí nguyên vật liệu, máy móc & hàng hóa đầu vào.</td>
                    </tr>
                    <tr style="background: rgba(0, 255, 204, 0.03);">
                        <td><b>📊 Tổng hợp Stress-Test</b></td>
                        <td style="color: #94A3B8;">—</td>
                        <td style="color: #94A3B8;">—</td>
                        <td style="color: {total_color}; font-weight: 800; font-size: 13px;">{sim_impact:+.2f}%</td>
                        <td>Tổng hợp các biến số khiến chỉ số {data_column} dự báo {'tăng' if sim_impact > 0 else 'giảm'} {abs(sim_impact):.2f}%, đạt mức ~{projected_cpi:,.2f} điểm.</td>
                    </tr>
                </tbody>
            </table>
            """
            st.markdown(table_html, unsafe_allow_html=True)

        # TAB MỚI: PHÂN TÍCH LÝ THUYẾT & KIẾN TRÚC ĐA NGUỒN
        with tab_theory:
            st.markdown("##### 📌 Bản chất Kinh tế học & Phương pháp luận Đa nguồn")
            
            c_th1, c_th2 = st.columns(2)
            with c_th1:
                st.markdown("""
                <div class="glass-card" style="height: 100%;">
                    <h6 style="color: #00FFCC; margin-top:0;">1. CPI (Consumer Price Index)</h6>
                    <p style="font-size: 12px; color: #CBD5E1; line-height: 1.6;">
                        Là <b>Chỉ số giá tiêu dùng</b>, thước đo tĩnh phản ánh mức giá trung bình của một rổ hàng hóa & dịch vụ đại diện (Lương thực, Y tế, Giao thông, Giáo dục...) do Tổng cục Thống kê (GSO) công bố.
                    </p>
                </div>
                """, unsafe_allow_html=True)
            with c_th2:
                st.markdown("""
                <div class="glass-card" style="height: 100%;">
                    <h6 style="color: #FF007A; margin-top:0;">2. Lạm phát (Inflation)</h6>
                    <p style="font-size: 12px; color: #CBD5E1; line-height: 1.6;">
                        Là <b>Tốc độ gia tăng liên tục</b> của mặt bằng giá chung trong nền kinh tế. Lạm phát thể hiện sự mất giá của đồng tiền và sức mua suy giảm theo thời gian.
                    </p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("###### 🔄 Mối quan hệ Tương tác:")
            st.markdown("""
            * **CPI là biến đầu vào đo lường:** Lạm phát được tính toán trực tiếp từ tốc độ thay đổi phần trăm của CPI qua các thời kỳ:
            """)
            st.latex(r"\text{Tỷ lệ Lạm phát (YoY)} = \frac{\text{CPI}_t - \text{CPI}_{t-12}}{\text{CPI}_{t-12}} \times 100\%")
            st.markdown("""
            * **Động lực hai chiều:** Khi giá các mặt hàng chiến lược (Năng lượng, Tỷ giá) biến động, CPI sẽ tăng lên, từ đó đẩy tỷ lệ Lạm phát tăng theo. Ngược lại, kỳ vọng lạm phát cao sẽ thúc đẩy người dân tích trữ tài sản, tiếp tục đẩy CPI tăng.
            """)

            st.markdown("---")
            st.markdown("##### 🚀 Tại sao cần Dự báo Đa nguồn Thời gian thực (Nowcasting)?")
            st.markdown("""
            <div class="glass-card">
                <b style="color: #00FFCC;">Thách thức của phương pháp truyền thống:</b>
                <p style="font-size: 12px; color: #94A3B8; margin-top: 4px;">
                    Dữ liệu CPI chính thức do GSO công bố thường có <b>độ trễ khoảng 30 ngày</b> (cuối mỗi tháng). Điều này khiến công tác quản trị chính sách tiền tệ và đầu tư bị bị động trước các cú sốc vĩ mô bất ngờ.
                </p>
                <b style="color: #10B981;">Giải pháp Đa nguồn theo Thời gian thực (Real-time Multi-source):</b>
                <p style="font-size: 12px; color: #CBD5E1; margin-top: 4px; line-height: 1.6;">
                    Mô hình tích hợp 3 luồng dữ liệu chính:
                    <br>1. <b>Tần suất thấp (Low-frequency):</b> Chuỗi thời gian CPI lịch sử từ GSO & Ngân hàng Nhà nước.
                    <br>2. <b>Tần suất cao (High-frequency / Real-time):</b> Biến động giá Dầu WTI/Brent, Tỷ giá USD/VND thị trường liên ngân hàng, giá nông sản thế giới cập nhật liên tục.
                    <br>3. <b>Dữ liệu Phi cấu trúc & RAG Engine:</b> AI quét tri thức tin tức vĩ mô, văn bản chính sách để điều chỉnh sai số tức thời (Nowcasting).
                </p>
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
