import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# 1. Cấu hình giao diện Streamlit (Dark Mode, layout rộng)
st.set_page_config(
    page_title="Hệ thống Nghiên cứu Kinh tế Vĩ mô & Lạm phát",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# PHẦN 2: CÁC HÀM XỬ LÝ DỮ LIỆU & CALL API
# -----------------------------------------------------------------------------

@st.cache_data(ttl=86400)  # Cache 24 giờ để tối ưu hiệu năng web
def fetch_wb_inflation(country_iso3):
    """
    Truy vấn chỉ số lạm phát tiêu dùng hàng năm từ World Bank Data360 API.
    """
    api_url = "https://data360api.worldbank.org/v1/data360/data"
    
    # 336 là ID chuẩn của 'Inflation, consumer prices (annual %)' trong Data360
    params = {
        "indicators": "336",
        "countries": country_iso3,
        "timeperiods": "2016,2017,2018,2019,2020,2021,2022,2023,2024,2025"
    }
    
    try:
        response = requests.get(api_url, params=params, timeout=8)
        if response.status_code == 200:
            raw_data = response.json()
            data_list = raw_data.get("data", [])
            
            parsed_records = []
            for item in data_list:
                period = item.get("period")
                value = item.get("value")
                if period is not None and value is not None:
                    parsed_records.append({
                        "Năm": int(period),
                        "Tỷ lệ Lạm phát (%)": round(float(value), 2)
                    })
            
            df_wb = pd.DataFrame(parsed_records).sort_values(by="Năm")
            return df_wb
    except Exception as e:
        st.sidebar.error(f"⚠️ Lỗi kết nối World Bank API: {e}")
    return None


def query_lm_studio(prompt, system_instruction, endpoint_url):
    """
    Gửi prompt cùng ngữ cảnh dữ liệu sang máy chủ LM Studio (thông qua URL Ngrok/Local).
    """
    headers = {
        "Content-Type": "application/json"
    }
    
    # Chuẩn bị payload theo định dạng OpenAI Chat Completions API hỗ trợ bởi LM Studio
    payload = {
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3, # Đặt thấp để mô hình đưa ra câu trả lời chính xác, ít sáng tạo lung tung
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(f"{endpoint_url}/v1/chat/completions", json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return f"❌ Lỗi từ máy chủ LM Studio (Mã lỗi: {response.status_code})"
    except Exception as e:
        return f"❌ Không thể kết nối đến LM Studio qua Endpoint đã cấu hình. Vui lòng kiểm tra lại Ngrok/Server. Chi tiết: {e}"


# -----------------------------------------------------------------------------
# PHẦN 3: THIẾT LẬP DỮ LIỆU MẪU TRONG NƯỚC (DOMESTIC DATASET)
# -----------------------------------------------------------------------------

# Giả lập bộ dữ liệu lịch sử CPI và lạm phát cơ bản trong nước để phục vụ nghiên cứu
@st.cache_data
def get_domestic_data():
    # Dữ liệu theo năm
    annual_data = {
        "Năm": [2019, 2020, 2021, 2022, 2023, 2024, 2025],
        "CPI Bình quân (%)": [2.80, 3.23, 1.84, 3.15, 3.25, 4.08, 3.50],
        "Lạm phát Cơ bản (%)": [2.01, 2.31, 0.81, 2.39, 4.16, 3.20, 2.80]
    }
    df_annual = pd.DataFrame(annual_data)
    
    # Dữ liệu chi tiết 12 tháng gần nhất
    monthly_data = {
        "Tháng/Năm": [
            "07/2025", "08/2025", "09/2025", "10/2025", "11/2025", "12/2025",
            "01/2026", "02/2026", "03/2026", "04/2026", "05/2026", "06/2026"
        ],
        "CPI so với cùng kỳ (%)": [3.12, 3.20, 3.35, 3.10, 3.05, 3.50, 3.65, 3.80, 3.40, 3.42, 3.30, 3.25],
        "Nhóm Giao thông (%)": [-1.20, 0.50, 1.10, 0.80, -0.40, 1.50, 2.10, 3.05, 1.80, 1.15, 0.90, 0.60],
        "Nhóm Hàng ăn (%)": [4.50, 4.30, 4.80, 4.10, 3.90, 4.20, 4.60, 5.10, 4.30, 4.25, 4.10, 4.00]
    }
    df_monthly = pd.DataFrame(monthly_data)
    return df_annual, df_monthly

df_annual_grouped, df_active = get_domestic_data()

# -----------------------------------------------------------------------------
# PHẦN 4: SIDEBAR CẤU HÌNH KỸ THUẬT
# -----------------------------------------------------------------------------

st.sidebar.image("https://img.icons8.com/nolan/96/combo-chart.png", width=60)
st.sidebar.title("Cấu hình Nghiên cứu")

st.sidebar.markdown("### 🔌 Kết nối LM Studio")
# Ô nhập URL Ngrok hoặc Localhost của máy chủ LM Studio
lm_studio_endpoint = st.sidebar.text_input(
    "Endpoint API (Ngrok hoặc Local IP):",
    value="http://localhost:1234",
    placeholder="Ví dụ: https://abcd-12-34.ngrok-free.app"
)

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Mẹo nghiên cứu:**\n"
    "Dữ liệu được tải động từ World Bank Data360 sẽ được nhúng trực tiếp vào bộ não của AI "
    "giúp tăng độ chính xác trong lập luận so sánh vĩ mô quốc tế."
)

# -----------------------------------------------------------------------------
# PHẦN 5: GIAO DIỆN CHÍNH (MAIN LAYOUT)
# -----------------------------------------------------------------------------

st.title("📈 HỆ THỐNG NGHIÊN CỨU VĨ MÔ & TƯƠNG QUAN LẠM PHÁT CO-PILOT")
st.caption("Ứng dụng phân tích dữ liệu CPI nội địa kết hợp API World Bank Data360 và Trợ lý AI cục bộ (RAG)")

# Phân chia bố cục làm 2 cột chính
col1, col2 = st.columns([1.1, 0.9])

# =============================================================================
# CỘT 1: PHẦN SỐ LIỆU VÀ BIỂU ĐỒ TRỰC QUAN HOÁ
# =============================================================================
with col1:
    st.subheader("📊 Số liệu vĩ mô hiện hành")
    
    # 1. Hiển thị bảng số liệu trong nước
    tab_annual, tab_monthly = st.tabs(["🗓️ Theo Năm", "📅 12 Tháng gần nhất"])
    
    with tab_annual:
        st.dataframe(df_annual_grouped, use_container_width=True, hide_index=True)
    with tab_monthly:
        st.dataframe(df_active, use_container_width=True, hide_index=True)
        
    # 2. Phần kết nối và trực quan hoá lạm phát quốc tế (API World Bank)
    st.markdown("---")
    st.markdown("### 🌐 Đối chiếu Lạm phát Quốc tế (World Bank)")
    
    country_selected = st.selectbox(
        "Chọn quốc gia để so sánh tương quan:",
        options=[
            "Mỹ (USA)", 
            "Singapore (SGP)", 
            "Trung Quốc (CHN)", 
            "Thái Lan (THA)", 
            "Hàn Quốc (KOR)"
        ],
        index=0,
        key="wb_country_select"
    )
    
    # Trích xuất mã ISO3 trong dấu ngoặc (Ví dụ: "Mỹ (USA)" -> "USA")
    iso3_code = country_selected.split("(")[1].replace(")", "").strip()
    
    # Truy vấn dữ liệu thực tế từ API World Bank
    with st.spinner("🔄 Đang truy vấn dữ liệu từ máy chủ World Bank..."):
        df_wb_data = fetch_wb_inflation(iso3_code)
        
    if df_wb_data is not None and not df_wb_data.empty:
        # Tạo biểu đồ cột phát sáng màu hổ phách
        fig_wb = px.bar(
            df_wb_data,
            x="Năm",
            y="Tỷ lệ Lạm phát (%)",
            template="plotly_dark",
            text="Tỷ lệ Lạm phát (%)"
        )
        
        fig_wb.update_traces(
            marker_color='rgba(255, 128, 0, 0.85)',
            marker_line_color='#FF8000',
            marker_line_width=1.5,
            textposition='outside',
            hovertemplate="<b>Năm:</b> %{x}<br><b>Lạm phát:</b> %{y}%<extra></extra>"
        )
        
        fig_wb.update_xaxes(
            type='category',
            gridcolor="rgba(255, 255, 255, 0.03)"
        )
        
        fig_wb.update_yaxes(
            title="Phần trăm (%)",
            gridcolor="rgba(255, 255, 255, 0.03)"
        )
        
        fig_wb.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=20, b=0),
            height=300
        )
        
        st.plotly_chart(fig_wb, use_container_width=True, config={'displayModeBar': False})
    else:
        st.warning(f"⚠️ Không nhận được dữ liệu phản hồi từ World Bank cho mã quốc gia {iso3_code}.")


# =============================================================================
# CỘT 2: TRỢ LÝ TRÍ TUỆ NHÂN TẠO CO-PILOT (CHAT RAG)
# =============================================================================
with col2:
    st.subheader("🤖 Trợ lý Phân tích Vĩ mô")
    
    # Khởi tạo bộ nhớ cuộc trò chuyện nếu chưa tồn tại
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # Tạo khung chứa các tin nhắn chat cũ để cuộn
    chat_container = st.container(height=520)
    
    # Hiển thị lịch sử chat
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
    # Nhận phản hồi/câu hỏi mới từ người dùng
    if prompt := st.chat_input("Hỏi về xu hướng lạm phát, áp lực tỷ giá hay đối chiếu quốc tế..."):
        
        # Hiển thị tin nhắn người dùng ngay lập tức lên màn hình
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
                
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # 1. Chuẩn bị dữ liệu nội địa
        recent_monthly_summary = df_active.to_string(index=False)
        annual_summary = df_annual_grouped.to_string(index=False)
        
        # 2. Chuẩn bị dữ liệu World Bank vừa gọi từ API
        wb_summary_text = "Không có dữ liệu quốc tế."
        if df_wb_data is not None:
            wb_summary_text = df_wb_data.to_string(index=False)
            
        # 3. Tạo siêu prompt thiết lập vai trò và nhúng dữ liệu làm ngữ cảnh (RAG)
        system_instruction = f"""
Bạn là một chuyên gia phân tích kinh tế vĩ mô sắc sảo, tốt nghiệp Học viện Tài chính[cite: 1].
Dưới đây là hai nguồn dữ liệu thực tế, đáng tin cậy phục vụ cho quá trình nghiên cứu của bạn[cite: 1]:

--- NGUỒN 1: CHỈ SỐ TRUNG BÌNH TRONG NƯỚC THEO NĂM ---
{annual_summary}

--- NGUỒN 2: CHỈ SỐ LẠM PHÁT THẾ GIỚI TỪ WORLD BANK (Mẫu so sánh: {country_selected}) ---
{wb_summary_text}

--- DỮ LIỆU CHI TIẾT 12 THÁNG GẦN NHẤT TRONG NƯỚC ---
{recent_monthly_summary}

Yêu cầu phân tích:
1. Khi người dùng đặt câu hỏi, hãy luôn tìm cách đối chiếu, liên hệ logic giữa số liệu nội địa và số liệu quốc tế từ World Bank ở trên[cite: 1].
2. Lập luận khoa học, sử dụng ngôn ngữ kinh tế học chuẩn xác (lạm phát cầu kéo, chi phí đẩy, độ trễ chính sách, tỷ giá, nhập khẩu lạm phát)[cite: 1].
3. Trả lời trực diện, ngắn gọn bằng tiếng Việt, tránh lý thuyết suông và TUYỆT ĐỐI không bịa đặt số liệu nằm ngoài các bảng được cung cấp ở trên[cite: 1].
"""
        
        # 4. Gửi yêu cầu phân tích sang LM Studio
        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("🧠 Trợ lý AI đang lập luận vĩ mô..."):
                    ai_response = query_lm_studio(prompt, system_instruction, lm_studio_endpoint)
                    st.markdown(ai_response)
                    
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
