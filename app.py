import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from openai import OpenAI

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN WEB & CSS PREMIUM
# ==========================================
st.set_page_config(
    page_title="Hệ thống Dữ liệu Vĩ mô & AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS ĐỘT PHÁ - PHONG CÁCH SEGMENTED CONTROL & TABLES NÂNG CẤP
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    .main {
        background: #0B0F19 !important;
    }
    
    /* Glassmorphic Cards */
    .glass-card {
        background: rgba(17, 24, 39, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 15px;
    }
    
    /* Metric Cards */
    [data-testid="stMetric"] {
        background: rgba(17, 24, 39, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        padding: 18px 22px !important;
        border-radius: 16px !important;
        backdrop-filter: blur(10px) !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stMetric"]:hover {
        border-color: rgba(16, 185, 129, 0.4) !important;
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.15) !important;
        transform: translateY(-2px) !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 26px !important;
        font-weight: 800 !important;
        color: #10B981 !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 11px !important;
        color: #94A3B8 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600 !important;
    }
    
    /* SEGMENTED CONTROL TABS */
    div[data-testid="stTabs"] [data-baseweb="tab-highlight"],
    div[data-testid="stTabs"] [data-baseweb="tab-border-bar"],
    div[data-testid="stTabs"] [role="tablist"]::after {
        display: none !important;
        height: 0px !important;
        background-color: transparent !important;
        border: none !important;
    }

    div[data-testid="stTabs"] [role="tablist"],
    div[data-testid="stTabs"] [data-baseweb="tab-list"] {
        display: flex !important;
        width: 100% !important;
        background: #111827 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 14px !important;
        padding: 6px !important;
        gap: 6px !important;
        margin-bottom: 24px !important;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.4) !important;
    }

    div[data-testid="stTabs"] button[role="tab"],
    div[data-testid="stTabs"] [data-baseweb="tab"] {
        flex: 1 1 0% !important;
        width: 100% !important;
        height: 44px !important;
        border-radius: 10px !important;
        border: none !important;
        background: transparent !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0 12px !important;
        border-bottom: none !important;
    }

    div[data-testid="stTabs"] button[role="tab"] p,
    div[data-testid="stTabs"] button[role="tab"] span {
        color: #94A3B8 !important;
        font-weight: 600 !important;
        font-size: 13.5px !important;
        margin: 0 !important;
        transition: color 0.2s ease !important;
        white-space: nowrap !important;
    }

    div[data-testid="stTabs"] button[role="tab"]:hover {
        background: rgba(255, 255, 255, 0.04) !important;
    }
    div[data-testid="stTabs"] button[role="tab"]:hover p {
        color: #F8FAFC !important;
    }

    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"],
    div[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #0D9488 0%, #0284C7 100%) !important;
        box-shadow: 0 4px 14px rgba(13, 148, 136, 0.35) !important;
        border-bottom: none !important;
    }

    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] p,
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] span {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }
    
    div[data-testid="stPills"] button {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        color: #94A3B8 !important;
        border-radius: 20px !important;
        font-size: 12px !important;
    }
    div[data-testid="stPills"] button[aria-selected="true"] {
        background-color: rgba(16, 185, 129, 0.15) !important;
        border-color: #10B981 !important;
        color: #10B981 !important;
    }

    .ai-welcome {
        border: 1px dashed rgba(16, 185, 129, 0.3);
        background: rgba(16, 185, 129, 0.02);
        border-radius: 14px;
        padding: 20px;
        text-align: center;
        margin-top: 10px;
    }
    
    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.1); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# Header chính
h_col1, h_col2 = st.columns([3, 1])
with h_col1:
    st.markdown("""
    <div style="margin-bottom: 12px;">
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
    <div style="background: rgba(16, 185, 129, 0.03); border: 1px solid rgba(16, 185, 129, 0.15); padding: 15px; border-radius: 12px;">
        <span style="color: #10B981; font-weight: 700; font-size: 13px;">● AI ENGINE ONLINE</span><br>
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
    # 5. BỐ TRÍ LAYOUT TAB
    # ==========================================
    col1, col2 = st.columns([1.3, 1], gap="large")

    with col1:
        tab_theory, tab_chart, tab_table, tab_sim, tab_insights = st.tabs([
            "💡 Lý thuyết",
            "📈 Biểu đồ Chu kỳ", 
            "📊 Bảng Niên độ", 
            "🛠️ Mô phỏng Kịch bản",
            "📌 Highlight Vĩ mô"
        ])

        # TAB 1: LÝ THUYẾT CHI TIẾT
        with tab_theory:
            st.markdown("##### 🛒 1. Nhập môn Kinh tế Vĩ mô: CPI & Lạm phát là gì?")
            st.caption("Ví dụ trực quan về biến động sức mua thực tế:")
            
            st.markdown("""
            <div class="glass-card" style="border-left: 4px solid #10B981;">
                <p style="font-size: 13px; color: #E2E8F0; margin: 0; line-height: 1.6;">
                    💡 <b>Ví dụ trực quan:</b> Giả sử năm ngoái bạn mang <b>100.000 VNĐ</b> đi chợ mua được <b>2 bát phở</b>. Năm nay, vẫn cầm 100.000 VNĐ đó bạn chỉ mua được <b>1 bát phở và 1 ly trà đá</b>.
                    <br>→ Đồng tiền của bạn đã bị giảm sức mua. Sự suy giảm sức mua đó chính là <b>Lạm phát</b>, và công cụ để tính toán chính xác mức độ tăng giá phở/trà đá đó là <b>Chỉ số CPI</b>.
                </p>
            </div>
            """, unsafe_allow_html=True)

            c_th1, c_th2 = st.columns(2)
            with c_th1:
                st.markdown("""
                <div class="glass-card" style="height: 100%;">
                    <h6 style="color: #10B981; margin-top:0; font-size: 14px;">🧺 CPI (Consumer Price Index)</h6>
                    <span style="background: rgba(16,185,129,0.1); color: #10B981; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight:700;">THƯỚC ĐO TĨNH</span>
                    <p style="font-size: 12px; color: #CBD5E1; line-height: 1.6; margin-top: 10px;">
                        • <b>Tên gọi:</b> Chỉ số Giá tiêu dùng.<br>
                        • <b>Bản chất:</b> Tưởng tượng Tổng cục Thống kê (GSO) gom khoảng 752 mặt hàng thiết yếu vào một <b>"Chiếc Giỏ Hàng Chuẩn"</b>.<br>
                        • <b>Cách hoạt động:</b> Định kỳ hàng tháng, GSO đi cộng tổng số tiền cần thiết để mua "Giỏ Hàng" này. Sự chênh lệch tổng số tiền so với gốc gọi là CPI.
                    </p>
                </div>
                """, unsafe_allow_html=True)
            with c_th2:
                st.markdown("""
                <div class="glass-card" style="height: 100%;">
                    <h6 style="color: #F43F5E; margin-top:0; font-size: 14px;">🎈 Lạm phát (Inflation)</h6>
                    <span style="background: rgba(244,63,94,0.1); color: #F43F5E; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight:700;">TỐC ĐỘ TĂNG TRƯỜNG</span>
                    <p style="font-size: 12px; color: #CBD5E1; line-height: 1.6; margin-top: 10px;">
                        • <b>Bản chất:</b> Là <b>tốc độ biến động (%)</b> của mặt bằng giá chung theo thời gian.<br>
                        • <b>Mối đe dọa:</b> Lạm phát nhẹ (2-3%/năm) kích thích sản xuất. Nhưng lạm phát quá cao làm giảm giá trị tiền lương, gây mất giá đồng tiền.<br>
                        • <b>Nguyên nhân chính:</b> Do chi phí đầu vào tăng (Dầu khí, tỷ giá) hoặc do lượng cung tiền lớn.
                    </p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("##### 🔗 2. Mối quan hệ tương tác & Công thức liên kết")
            
            st.markdown("""
            * **CPI là biến đầu vào → Lạm phát là kết quả đầu ra:** 
              CPI đóng vai trò như thước đo độ cao. Tỷ lệ Lạm phát chính là tốc độ mà độ cao đó gia tăng (YoY - Year on Year):
            """)
            
            st.latex(r"\text{Tỷ lệ Lạm phát (YoY)} = \frac{\text{CPI}_{\text{Kỳ này}} - \text{CPI}_{\text{Cùng kỳ năm ngoái}}}{\text{CPI}_{\text{Cùng kỳ năm ngoái}}} \times 100\%")

            st.markdown("""
            <div class="glass-card" style="margin-top: 12px; padding: 16px;">
                <b style="color: #10B981; font-size: 13px;">📖 Giải thích chi tiết ký hiệu công thức:</b>
                <ul style="font-size: 12px; color: #CBD5E1; margin-top: 10px; margin-bottom: 0; padding-left: 20px; line-height: 1.8;">
                    <li><b>Tỷ lệ Lạm phát (YoY):</b> Mức độ gia tăng giá cả so với cùng kỳ năm trước, tính bằng %.</li>
                    <li><b>CPI<sub>Kỳ này</sub>:</b> Chỉ số CPI thu thập tại thời điểm hiện tại.</li>
                    <li><b>CPI<sub>Cùng kỳ năm ngoái</sub>:</b> Chỉ số CPI thu thập đúng vào tháng này của 1 năm trước.</li>
                    <li><b>Thao tác trừ:</b> Đo lường mức độ biến động tuyệt đối về điểm số.</li>
                    <li><b>Thao tác chia & nhân 100%:</b> Quy đổi về tỷ lệ phần trăm (%) chuẩn hóa.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            * **Cơ chế tác động 2 chiều:**
              1. **Chiều thuận:** Giá các mặt hàng chiến lược (Dầu, Tỷ giá USD/VND) tăng → Chi phí sản xuất & vận chuyển tăng → **CPI tăng** → **Lạm phát tăng**.
              2. **Chiều ngược:** Người dân kỳ vọng lạm phát cao → Ồ ạt mua tài sản tích trữ (BĐS, Vàng) → Lực cầu tăng đột biến → **Tiếp tục đẩy CPI tăng**.
            """)

            st.markdown("---")
            st.markdown("##### 🚀 3. Tại sao cần 'Dự báo Đa nguồn Thời gian thực'?")
            st.markdown("""
            <div class="glass-card" style="background: rgba(16, 185, 129, 0.02); border: 1px solid rgba(16, 185, 129, 0.15);">
                <b style="color: #F43F5E; font-size: 13px;">⚠️ Hạn chế của Phương pháp Thống kê Truyền thống:</b>
                <p style="font-size: 12px; color: #94A3B8; margin-top: 4px; line-height: 1.5;">
                    Báo cáo CPI chính thức thường chỉ công bố <b>mỗi tháng 1 lần (với độ trễ 20-30 ngày)</b>. Khi có cú sốc giá dầu thế giới, chính sách cần thông tin ngay lập tức chứ không thể chờ đến cuối tháng.
                </p>
                <b style="color: #10B981; font-size: 13px;">💡 Giải pháp Nowcasting Đa nguồn (Real-Time AI):</b>
                <p style="font-size: 12px; color: #CBD5E1; margin-top: 4px; line-height: 1.6;">
                    Ứng dụng kết hợp <b>3 tầng dữ liệu</b> liên tục:
                    <br>1. <b>Nguồn Tần suất cao (Cập nhật hàng ngày):</b> Giá Dầu WTI/Brent, Tỷ giá USD/VND, Giá Vàng.
                    <br>2. <b>Nguồn Dữ liệu Lịch sử:</b> Chuỗi CPI chính thống của GSO để làm mốc nền tảng.
                    <br>3. <b>Trí tuệ Nhân tạo (RAG + LLM):</b> Truy xuất văn bản điều hành vĩ mô để tính toán <b>Dự báo CPI tức thời</b>, loại bỏ hoàn toàn độ trễ báo cáo.
                </p>
            </div>
            """, unsafe_allow_html=True)

        # TAB 2: BIỂU ĐỒ CHU KỲ
        with tab_chart:
            show_sma = st.checkbox("Hiển thị Đường trung bình động SMA (12 tháng)", value=True)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_active['Ngay'], y=df_active[data_column],
                mode='lines', name=data_column,
                line=dict(color='#10B981', width=3)
            ))
            if show_sma:
                fig.add_trace(go.Scatter(
                    x=df_active['Ngay'], y=df_active['SMA12'],
                    mode='lines', name='SMA 12 Tháng',
                    line=dict(color='#F43F5E', width=2, dash='dot')
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

        # TAB 3: BẢNG NIÊN ĐỘ
        with tab_table:
            st.markdown("##### 📊 Số liệu CPI trung bình từng năm")
            
            min_cpi = df_annual_grouped[f'Chỉ số {data_column} Trung Bình'].min()
            max_cpi = df_annual_grouped[f'Chỉ số {data_column} Trung Bình'].max()
            cpi_range = max_cpi - min_cpi if max_cpi != min_cpi else 1
            
            rows_html = ""
            for idx, row in df_annual_grouped.iterrows():
                year = int(row['Năm'])
                val = row[f'Chỉ số {data_column} Trung Bình']
                pct = 25 + ((val - min_cpi) / cpi_range) * 75
                
                rows_html += f"""<tr>
<td style="text-align: center; font-weight: 700; color: #F8FAFC;">
<span style="background: rgba(16, 185, 129, 0.12); color: #34D399; padding: 5px 14px; border-radius: 8px; border: 1px solid rgba(52, 211, 153, 0.25); font-size: 13px; display: inline-block;">
{year}
</span>
</td>
<td style="text-align: right; font-weight: 800; color: #10B981; font-size: 15px; padding-right: 20px;">
{val:,.2f}
</td>
<td style="vertical-align: middle; padding-left: 15px; padding-right: 15px;">
<div style="background: rgba(255, 255, 255, 0.06); border-radius: 10px; height: 10px; width: 100%; overflow: hidden; border: 1px solid rgba(255, 255, 255, 0.05);">
<div style="width: {pct:.1f}%; height: 100%; background: linear-gradient(90deg, #059669 0%, #10B981 50%, #34D399 100%); border-radius: 10px; box-shadow: 0 0 10px rgba(16, 185, 129, 0.5);"></div>
</div>
</td>
</tr>"""

            table_html = f"""<style>
.custom-cpi-table-container {{
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
    margin-bottom: 20px;
    background: #111827;
}}
.custom-cpi-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    color: #F1F5F9;
}}
.custom-cpi-table th {{
    background: #1E293B;
    color: #34D399;
    padding: 14px 16px;
    font-weight: 700;
    border-bottom: 2px solid rgba(255, 255, 255, 0.1);
    text-transform: uppercase;
    letter-spacing: 0.8px;
    font-size: 11px;
}}
.custom-cpi-table tr {{
    transition: background 0.2s ease;
}}
.custom-cpi-table tr:nth-child(even) {{
    background: rgba(255, 255, 255, 0.02);
}}
.custom-cpi-table tr:hover {{
    background: rgba(16, 185, 129, 0.08) !important;
}}
.custom-cpi-table td {{
    padding: 13px 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    vertical-align: middle;
}}
</style>
<div class="custom-cpi-table-container">
<table class="custom-cpi-table">
<thead>
<tr>
<th style="text-align: center; width: 22%;">Năm</th>
<th style="text-align: right; width: 38%; padding-right: 20px;">CPI Trung Bình</th>
<th style="text-align: left; width: 40%; padding-left: 15px;">Mức độ Tương quan Chu kỳ</th>
</tr>
</thead>
<tbody>
{rows_html}
</tbody>
</table>
</div>"""
            st.markdown(table_html, unsafe_allow_html=True)
            
            csv_data = df_active.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Tải xuống dữ liệu CSV chi tiết",
                data=csv_data,
                file_name="du_lieu_vi_mo_cpi.csv",
                mime="text/csv",
                use_container_width=True
            )

        # TAB 4: MÔ PHỎNG KỊCH BẢN
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
            
            # ĐÃ SỬA LỖI &rr; THÀNH KÝ TỰ MŨI TÊN CHUẨN →
            st.markdown(f"""
            <div class="glass-card" style="margin-top:10px; margin-bottom:15px; border-left: 4px solid {'#F43F5E' if sim_impact > 0 else '#10B981'};">
                <div style="font-size:12px; color:#94A3B8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">DỰ BÁO ĐIỀU CHỈNH CPI CẬN KỲ</div>
                <div style="font-size:26px; font-weight:800; color:{'#FB7185' if sim_impact > 0 else '#34D399'}; margin: 4px 0;">
                    {sim_impact:+.2f}% → ~{projected_cpi:,.2f} điểm
                </div>
                <small style="color:#64748B;">Mô hình ước lượng dựa trên trọng số biến động năng lượng & hàng hóa nhập khẩu.</small>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("##### 📋 Phân tích Cơ chế Tác động Chi tiết")
            
            oil_color = "#FB7185" if oil_impact > 0 else ("#34D399" if oil_impact < 0 else "#94A3B8")
            oil_bg = "rgba(244, 63, 94, 0.12)" if oil_impact > 0 else ("rgba(16, 185, 129, 0.12)" if oil_impact < 0 else "rgba(148, 163, 184, 0.1)")
            
            fx_color = "#FB7185" if fx_impact > 0 else ("#34D399" if fx_impact < 0 else "#94A3B8")
            fx_bg = "rgba(244, 63, 94, 0.12)" if fx_impact > 0 else ("rgba(16, 185, 129, 0.12)" if fx_impact < 0 else "rgba(148, 163, 184, 0.1)")
            
            total_color = "#FB7185" if sim_impact > 0 else ("#34D399" if sim_impact < 0 else "#94A3B8")
            total_bg = "rgba(244, 63, 94, 0.18)" if sim_impact > 0 else ("rgba(16, 185, 129, 0.18)" if sim_impact < 0 else "rgba(148, 163, 184, 0.1)")

            table_html_sim = f"""<style>
.explain-table-container {{
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
    margin-top: 10px;
    background: #111827;
}}
.explain-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    color: #F1F5F9;
}}
.explain-table th {{
    background: #1E293B;
    color: #34D399;
    padding: 12px 14px;
    text-align: left;
    font-weight: 700;
    border-bottom: 2px solid rgba(255, 255, 255, 0.1);
    text-transform: uppercase;
    letter-spacing: 0.6px;
    font-size: 11px;
}}
.explain-table td {{
    padding: 13px 14px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    vertical-align: middle;
    line-height: 1.5;
}}
.explain-table tr:hover {{
    background: rgba(255, 255, 255, 0.03);
}}
.badge-value {{
    display: inline-block;
    padding: 4px 10px;
    border-radius: 6px;
    font-weight: 700;
    font-size: 12px;
}}
</style>
<div class="explain-table-container">
<table class="explain-table">
<thead>
<tr>
<th style="width: 20%;">Biến số Vĩ mô</th>
<th style="width: 15%; text-align: center;">Điều chỉnh</th>
<th style="width: 12%; text-align: center;">Trọng số</th>
<th style="width: 16%; text-align: center;">Đóng góp CPI</th>
<th style="width: 37%;">Cơ chế truyền dẫn & Tác động thực tế</th>
</tr>
</thead>
<tbody>
<tr>
<td><b style="color: #F8FAFC;">🛢️ Giá Dầu WTI</b></td>
<td style="text-align: center;">
<span class="badge-value" style="background: {oil_bg}; color: {oil_color}; border: 1px solid {oil_color}40;">{oil_sim:+d}%</span>
</td>
<td style="text-align: center; color: #94A3B8; font-weight: 600;">0.04</td>
<td style="text-align: center;">
<span class="badge-value" style="background: {oil_bg}; color: {oil_color}; font-size: 13px;">{oil_impact:+.2f}%</span>
</td>
<td style="color: #CBD5E1; font-size: 12.5px;">Tác động trực tiếp lên nhóm Giao thông (xăng dầu), lan tỏa sang chi phí vận tải, logistics và giá thành sản xuất hàng hóa.</td>
</tr>
<tr>
<td><b style="color: #F8FAFC;">💵 Tỷ giá USD/VND</b></td>
<td style="text-align: center;">
<span class="badge-value" style="background: {fx_bg}; color: {fx_color}; border: 1px solid {fx_color}40;">{fx_sim:+d}%</span>
</td>
<td style="text-align: center; color: #94A3B8; font-weight: 600;">0.11</td>
<td style="text-align: center;">
<span class="badge-value" style="background: {fx_bg}; color: {fx_color}; font-size: 13px;">{fx_impact:+.2f}%</span>
</td>
<td style="color: #CBD5E1; font-size: 12.5px;">Tạo áp lực "Nhập khẩu lạm phát" (Imported Inflation), làm tăng chi phí nguyên vật liệu, máy móc & hàng hóa đầu vào.</td>
</tr>
<tr style="background: rgba(16, 185, 129, 0.05); border-top: 1px solid rgba(16, 185, 129, 0.2);">
<td><b style="color: #34D399; font-size: 13.5px;">📊 Tổng hợp Stress-Test</b></td>
<td style="text-align: center; color: #64748B;">—</td>
<td style="text-align: center; color: #64748B;">—</td>
<td style="text-align: center;">
<span class="badge-value" style="background: {total_bg}; color: {total_color}; font-size: 14px; border: 1px solid {total_color}50;">{sim_impact:+.2f}%</span>
</td>
<td style="color: #F8FAFC; font-weight: 500; font-size: 12.5px;">
Tổng hợp biến số khiến CPI dự báo <b style="color: {total_color};">{'tăng' if sim_impact > 0 else 'giảm'} {abs(sim_impact):.2f}%</b>, ước đạt mức <b>~{projected_cpi:,.2f} điểm</b>.
</td>
</tr>
</tbody>
</table>
</div>"""
            st.markdown(table_html_sim, unsafe_allow_html=True)

        # TAB 5: HIGHLIGHT VĨ MÔ
        with tab_insights:
            st.markdown("##### 📌 Tóm tắt Điểm nóng Vĩ mô")
            st.markdown(f"""
            * **Biến động đỉnh điểm:** Chỉ số đạt đỉnh **{max_val:,.2f}** vào tháng **{max_date}**.
            * **Tốc độ tăng trưởng:** Mức tăng YoY hiện tại đạt **{yoy_change:+.2f}%**.
            * **Xu hướng trung hạn:** Đường SMA 12 tháng đang {'đi lên' if df_active['SMA12'].iloc[-1] > df_active['SMA12'].iloc[-6] else 'đi ngang/giảm'}, phản ánh áp lực chu kỳ tích lũy.
            """)

    # ==========================================
    # 6. CỘT PHẢI: AI ASSISTANT VỚI ACTION INDICATOR
    # ==========================================
    with col2:
        st.markdown("### 🤖 Trợ lý AI Phân tích & Dự báo Lạm phát")
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        st.caption("💡 Gợi ý câu hỏi trọng tâm:")
        q1, q2, q3 = st.columns(3)
        clicked_prompt = None
        if q1.button("📉 Dự báo CPI quý tới", use_container_width=True):
            clicked_prompt = "Hãy đưa ra dự báo chỉ số CPI và xu hướng lạm phát cụ thể trong các tháng tới dựa trên chuỗi số liệu đã có."
        if q2.button("🛢️ Giá dầu & Tỷ giá", use_container_width=True):
            clicked_prompt = "Tác động truyền dẫn của biến động Giá dầu và Tỷ giá USD/VND lên áp lực lạm phát hiện tại là bao nhiêu?"
        if q3.button("🏦 Chính sách tiền tệ", use_container_width=True):
            clicked_prompt = "Áp lực lạm phát hiện nay ảnh hưởng trực tiếp thế nào đến quyết định điều hành lãi suất của Ngân hàng Nhà nước?"

        chat_container = st.container(height=400)

        # Hàm xác định câu chỉ ra hành động phù hợp với trọng tâm câu hỏi
        def get_action_description(prompt_text: str) -> tuple[str, str]:
            p_lower = prompt_text.lower()
            if any(k in p_lower for k in ["dự báo", "cpi", "tháng tới", "quý tới", "xu hướng"]):
                act_status = "⚡ Đang trích xuất chuỗi lịch sử CPI, tính toán đường SMA12 và mô phỏng xu hướng lạm phát cận kỳ..."
                act_heading = "🎯 **Hành động phân tích:** Đang tổng hợp chuỗi thời gian CPI cận kỳ, phân tích độ lệch so với đỉnh/đáy lịch sử và tính toán kịch bản dự báo lạm phát..."
            elif any(k in p_lower for k in ["dầu", "giá dầu", "tỷ giá", "usd", "wti", "vàng"]):
                act_status = "⚡ Đang tính toán hệ số truyền dẫn từ biến động Giá Dầu WTI và Tỷ giá USD/VND vào CPI..."
                act_heading = "🎯 **Hành động phân tích:** Đang đo lường mức độ ảnh hưởng của chi phí năng lượng nhập khẩu và áp lực tỷ giá đến mặt bằng giá tiêu dùng..."
            elif any(k in p_lower for k in ["tiền tệ", "lãi suất", "nhnn", "ngân hàng", "chính sách"]):
                act_status = "⚡ Đang đối chiếu chỉ tiêu lạm phát mục tiêu và đánh giá dư địa điều hành chính sách tiền tệ..."
                act_heading = "🎯 **Hành động phân tích:** Đang đánh giá tác động của áp lực lạm phát hiện tại lên không gian điều hành lãi suất và thanh khoản của Ngân hàng Nhà nước..."
            else:
                act_status = f"⚡ Đang truy vấn cơ sở dữ liệu vĩ mô và tổng hợp luận điểm cho câu hỏi: '{prompt_text[:30]}...' "
                act_heading = f"🎯 **Hành động phân tích:** Đang truy xuất tập số liệu vĩ mô thời gian thực và phân tích trọng tâm câu hỏi của người dùng..."
            
            return act_status, act_heading

        # Render lịch sử trò chuyện
        with chat_container:
            if len(st.session_state.messages) == 0:
                st.markdown("""
                <div class="ai-welcome">
                    <div style="font-size: 32px; margin-bottom: 5px;">🎈</div>
                    <div style="color: #ffffff; font-weight: 700; font-size: 15px;">Trợ lý AI Phân tích & Dự báo Lạm phát</div>
                    <p style="color: #64748B; font-size: 12px; margin-top: 5px;">
                        Đặt câu hỏi phân tích kinh tế vĩ mô hoặc chọn một trong các gợi ý phía trên để bắt đầu.
                    </p>
                </div>
                """, unsafe_allow_html=True)

            for msg in st.session_state.messages:
                if msg.get("content"):
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])

        user_input = st.chat_input("Nhập câu hỏi phân tích vĩ mô...")
        prompt_to_send = clicked_prompt if clicked_prompt else user_input

        if prompt_to_send:
            # 1. Thêm câu hỏi người dùng vào history
            st.session_state.messages.append({"role": "user", "content": prompt_to_send})
            
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt_to_send)

                with st.chat_message("assistant"):
                    act_status, act_heading = get_action_description(prompt_to_send)
                    
                    # Trạng thái tĩnh/động hiển thị khi AI đang suy nghĩ
                    status_box = st.empty()
                    status_box.markdown(f"""
                    <div style="background: rgba(13, 148, 136, 0.12); border: 1px solid rgba(13, 148, 136, 0.35); padding: 10px 14px; border-radius: 10px; font-size: 12.5px; color: #2DD4BF; margin-bottom: 12px;">
                        {act_status}
                    </div>
                    """, unsafe_allow_html=True)

                    message_placeholder = st.empty()
                    full_response = ""

                    try:
                        # Khởi tạo OpenAI client kèm header tránh bị ngrok chặn
                        client = OpenAI(
                            base_url=f"{NGROK_STATIC_URL}/v1",
                            api_key="lm-studio",
                            default_headers={"ngrok-skip-browser-warning": "true"},
                            timeout=35.0
                        )

                        system_prompt = f"""
Bạn là Chuyên gia Phân tích Kinh tế Vĩ mô & Dự báo Lạm phát chuyên sâu tại Việt Nam.

DỮ LIỆU VĨ MÔ THỜI GIAN THỰC ĐANG CÓ TRONG HỆ THỐNG:
- Chỉ số {data_column} cận kỳ: {current_val:,.2f} điểm
- Tăng trưởng so với cùng kỳ năm trước (YoY): {yoy_change:+.2f}%
- Mức biến động cận kỳ (MoM): {mo_m_change:+.2f}%
- Đỉnh lịch sử ({label_suffix}): {max_val:,.2f} điểm (Tháng {max_date})
- Đáy lịch sử ({label_suffix}): {min_val:,.2f} điểm (Tháng {min_date})

YÊU CẦU QUAN TRỌNG VỀ ĐỊNH DẠNG VÀ NỘI DUNG:
1. Mở đầu câu trả lời BẮT BUỘC bằng đúng dòng chỉ định hành động sau đây (đã được tối ưu đúng trọng tâm câu hỏi):
{act_heading}

2. Sau dòng hành động trên, xuống dòng và trình bày câu trả lời trực diện, sắc bén, chia theo các đầu dòng rõ ràng, lập luận bằng con số cụ thể ở trên.
"""

                        messages_payload = [{"role": "system", "content": system_prompt}]
                        for m in st.session_state.messages:
                            if m.get("content"):
                                messages_payload.append({"role": m["role"], "content": m["content"]})

                        response = client.chat.completions.create(
                            model="local-model",
                            messages=messages_payload,
                            stream=True
                        )

                        for chunk in response:
                            if chunk.choices and len(chunk.choices) > 0 and chunk.choices[0].delta.content:
                                full_response += chunk.choices[0].delta.content
                                message_placeholder.markdown(full_response + "▌")

                        status_box.empty() # Xóa dòng trạng thái tạm thời
                        
                        if full_response.strip():
                            # Nếu AI không tự tạo dòng act_heading, tự động bổ sung vào đầu
                            if not full_response.strip().startswith("🎯"):
                                full_response = f"{act_heading}\n\n{full_response}"
                            message_placeholder.markdown(full_response)
                        else:
                            full_response = f"{act_heading}\n\n⚠️ *Không nhận được phản hồi từ mô hình AI Local. Vui lòng kiểm tra lại LM Studio đã nạp Model chưa.*"
                            message_placeholder.warning(full_response)

                    except Exception as e:
                        status_box.empty()
                        full_response = f"{act_heading}\n\n⚠️ **Lỗi kết nối Máy chủ AI Ngrok ({NGROK_STATIC_URL}):**\n\n`{str(e)}`\n\n💡 *Gợi ý:* Hãy kiểm tra máy chủ LM Studio đã bật Local Server và Ngrok đang chạy kết nối."
                        message_placeholder.error(full_response)

            if full_response.strip():
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            st.rerun()
