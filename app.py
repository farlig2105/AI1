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

# CSS ĐỘT PHÁ - PHONG CÁCH SEGMENTED CONTROL (SHADCN / LINEAR UI)
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
        
        /* =========================================================
           THIẾT KẾ TAB MỚI: SEGMENTED CONTROL CỰC ĐẸP (NO RED LINE)
           ========================================================= */
        
        /* 1. Xóa bỏ triệt để thanh gạch chân màu đỏ & xám mặc định */
        div[data-testid="stTabs"] [data-baseweb="tab-highlight"],
        div[data-testid="stTabs"] [data-baseweb="tab-border-bar"],
        div[data-testid="stTabs"] [role="tablist"]::after {
            display: none !important;
            height: 0px !important;
            background-color: transparent !important;
            border: none !important;
        }

        /* 2. Khung chứa danh sách Tab (Thanh trượt Segmented Control) */
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

        /* 3. Thẻ Tab dạng Nút bấm bo góc đối xứng 100% */
        div[data-testid="stTabs"] button[role="tab"],
        div[data-testid="stTabs"] [data-baseweb="tab"] {
            flex: 1 1 0% !important; /* Ép giãn đều 100% đối xứng */
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

        /* Chữ trong Tab mặc định */
        div[data-testid="stTabs"] button[role="tab"] p,
        div[data-testid="stTabs"] button[role="tab"] span {
            color: #94A3B8 !important;
            font-weight: 600 !important;
            font-size: 13.5px !important;
            margin: 0 !important;
            transition: color 0.2s ease !important;
            white-space: nowrap !important;
        }

        /* 4. Hiệu ứng Hover */
        div[data-testid="stTabs"] button[role="tab"]:hover {
            background: rgba(255, 255, 255, 0.04) !important;
        }
        div[data-testid="stTabs"] button[role="tab"]:hover p {
            color: #F8FAFC !important;
        }

        /* 5. TAB ĐƯỢC CHỌN (ACTIVE) - Gradient Emerald sang Cyan */
        div[data-testid="stTabs"] button[role="tab"][aria-selected="true"],
        div[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, #0D9488 0%, #0284C7 100%) !important;
            box-shadow: 0 4px 14px rgba(13, 148, 136, 0.35) !important;
            border-bottom: none !important;
        }

        /* Chữ của Active Tab */
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
                    <br>&rarr; Đồng tiền của bạn đã bị giảm sức mua. Sự suy giảm sức mua đó chính là <b>Lạm phát</b>, và công cụ để tính toán chính xác mức độ tăng giá phở/trà đá đó là <b>Chỉ số CPI</b>.
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
                    <span style="background: rgba(244,63,94,0.1); color: #F43F5E; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight:700;">TỐC ĐỘ TĂNG TRƯỞNG</span>
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

        with tab_table:
            st.markdown("##### Số liệu trung bình từng năm")
            formatted_annual_table = df_annual_grouped.style.format({
                'Năm': '{:.0f}',
                f'Chỉ số {data_column} Trung Bình': '{:.2f}'
            }).background_gradient(subset=[f'Chỉ số {data_column} Trung Bình'], cmap="mako")
            
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
                    <div style="font-size:24px; font-weight:700; color:{'#F43F5E' if sim_impact > 0 else '#10B981'};">
                        {sim_impact:+.2f}% &rarr; ~{projected_cpi:,.2f} điểm
                    </div>
                    <small style="color:#64748B;">Mô hình ước lượng dựa trên trọng số biến động năng lượng & hàng hóa nhập khẩu.</small>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("##### 📋 Phân tích Cơ chế Tác động Chi tiết")
            
            oil_color = "#F43F5E" if oil_impact > 0 else ("#10B981" if oil_impact < 0 else "#94A3B8")
            fx_color = "#F43F5E" if fx_impact > 0 else ("#10B981" if fx_impact < 0 else "#94A3B8")
            total_color = "#F43F5E" if sim_impact > 0 else ("#10B981" if sim_impact < 0 else "#94A3B8")

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
                    background: rgba(16, 185, 129, 0.08);
                    color: #10B981;
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
                    <tr style="background: rgba(16, 185, 129, 0.03);">
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

        with tab_insights:
            st.markdown("##### 📌 Tóm tắt Điểm nóng Vĩ mô")
            st.markdown(f"""
            * **Biến động đỉnh điểm:** Chỉ số đạt đỉnh **{max_val:,.2f}** vào tháng **{max_date}**.
            * **Tốc độ tăng trưởng:** Mức tăng YoY hiện tại đạt **{yoy_change:+.2f}%**.
            * **Xu hướng trung hạn:** Đường SMA 12 tháng đang {'đi lên' if df_active['SMA12'].iloc[-1] > df_active['SMA12'].iloc[-6] else 'đi ngang/giảm'}, phản ánh áp lực chu kỳ tích lũy.
            """)

    # --- CỘT PHẢI: AI ASSISTANT ---
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

        chat_container = st.container(height=380)

        with chat_container:
            if len(st.session_state.messages) == 0:
                st.markdown("""
                    <div class="ai-welcome">
                        <div style="font-size: 32px; margin-bottom: 5px;">🎈</div>
                        <div style="color: #ffffff; font-weight: 700; font-size: 15px;">Trợ lý AI Phân tích & Dự báo Lạm phát</div>
                        <p style="color: #64748B; font-size: 12px; margin-top: 5px;">
                            Trả lời trực tiếp, chính xác trọng tâm về <b>Dự báo Lạm phát, CPI</b> và các biến số vĩ mô liên quan. Không lan man.
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

        user_input = st.chat_input("Hỏi trực diện về dự báo lạm phát, CPI hoặc vĩ mô...")
        prompt = clicked_prompt if clicked_prompt else user_input

        if prompt:
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)
            
            st.session_state.messages.append({"role": "user", "content": prompt})

            recent_monthly_summary = df_active.tail(12).to_string(index=False)
            annual_summary = df_annual_grouped.to_string(index=False)

            system_instruction = f"""
            Bạn là một Chuyên gia Phân tích & Dự báo Lạm phát Vĩ mô cấp cao (nghiên cứu sinh/giảng viên chuyên ngành Kinh tế chính trị - Tài chính tại Học viện Tài chính).

            🎯 QUY TẮC PHẢN HỒI BẮT BỘC:
            1. **TRẢ LỜI CHÍNH XÁC TRỌNG TÂM:** 
               - Đi thẳng vào bản chất câu hỏi của người dùng. Tuyệt đối KHÔNG viết lời chào mừng, KHÔNG mở bài xã giao.
               - Không đưa ra các thông tin ngoài phạm vi câu hỏi. Câu trả lời phải súc tích, đắt giá, luận điểm rõ ràng.

            2. **TRỌNG TÂM CỐT LÕI - LẠM PHÁT & CPI:**
               - Trọng tâm công việc chính của bạn là phân tích, đánh giá và DỰ BÁO LẠM PHÁT / CPI.
               - Với các câu hỏi vĩ mô liên quan (Tỷ giá, Lãi suất, Giá dầu...), hãy trả lời chính xác và chốt lại tác động tới áp lực lạm phát của Việt Nam.

            3. **CẤU TRÚC PHẢN HỒI:**
               - Bắt đầu ngay bằng KẾT LUẬN hoặc CÂU TRẢ LỜI TRỰC TIẾP ở ngay câu đầu tiên.
               - Trình bày các luận điểm minh chứng bằng các gạch đầu dòng ngắn gọn.

            📊 DỮ LIỆU VĨ MÔ THỰC TẾ CUNG CẤP:
            
            - TRUNG BÌNH THEO NĂM:
            {annual_summary}
            
            - CHI TIẾT 12 THÁNG GẦN NHẤT:
            {recent_monthly_summary}
            """

            clean_url = NGROK_STATIC_URL.strip().rstrip('/')
            
            try:
                client = OpenAI(
                    base_url=f"{clean_url}/v1",
                    api_key="lm-studio"
                )

                with chat_container:
                    status_placeholder = st.empty()
                    with status_placeholder.status("⚙️ Đang xử lý câu hỏi...", expanded=False) as status:
                        time.sleep(0.2)
                        status.update(label="🧮 Đang truy xuất dữ liệu & dự báo...", state="running")
                        
                        response = client.chat.completions.create(
                            model="local-model",
                            messages=[
                                {"role": "system", "content": system_instruction},
                                *st.session_state.messages
                            ],
                            temperature=0.1
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
