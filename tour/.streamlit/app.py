import datetime
import random
import requests
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

# --- 페이지 설정 ---
st.set_page_config(
    page_title="🎉 전국 축제 탐험대",
    page_icon="🎈",
    layout="wide"
)

# --- API 키 가져오기 ---
# Streamlit Secrets에서 API 키를 안전하게 불러옵니다.
try:
    API_KEY = st.secrets["TOUR_API_KEY"]
except Exception:
    st.error("API 키를 찾을 수 없습니다. Secrets 설정(TOUR_API_KEY)을 확인해주세요.")
    st.stop()


# --- API 데이터 로딩 함수 (캐싱 처리) ---
@st.cache_data(ttl=3600)  # 1시간 동안 API 결과 캐싱
def fetch_festivals(event_start_date: str):
    """한국관광공사 TourAPI 4.0 행사정보조회 Endpoint"""
    url = "http://apis.data.go.kr/B551011/KorService1/searchFestival1"
    params = {
        "serviceKey": API_KEY,
        "numOfRows": "100",
        "pageNo": "1",
        "MobileOS": "ETC",
        "MobileApp": "FestivalApp",
        "_type": "json",
        "listYN": "Y",
        "arrange": "A",  # 대표이미지가 있는 정렬
        "eventStartDate": event_start_date
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
        if not items:
            return pd.DataFrame()
            
        df = pd.DataFrame(items)
        # 지도 및 일자 처리를 위한 주요 컬럼 정리
        df["mapx"] = pd.to_numeric(df["mapx"], errors="coerce")
        df["mapy"] = pd.to_numeric(df["mapy"], errors="coerce")
        return df
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()

# --- 데이터 준비 ---
today_str = datetime.datetime.now().strftime("%Y%m%d")
df_festivals = fetch_festivals(today_str)

# --- UI 레이아웃 ---
st.title("🎉 대한민국 구석구석 축제 탐험대")
st.caption("한국관광공사 Open API 기반 실시간 축제 검색 & 추천 웹앱")

if df_festivals.empty:
    st.warning("현재 조회된 축제 정보가 없거나 API 키 설정에 문제가 있습니다.")
    st.stop()

# 탭 구성: [🗺️ 축제 지도 & D-Day] / [🎲 이번 주말 어디 가? 룰렛]
tab1, tab2 = st.tabs(["🗺️ 축제 지도 & D-Day", "🎲 랜덤 축제 추천 룰렛"])


# ==========================================
# Tab 1: 축제 지도 & D-Day 카운트다운
# ==========================================
with tab1:
    st.subheader("📍 진행 중 / 예정된 축제 한눈에 보기")
    
    # 1. D-Day 연산
    def calc_dday(start_date_str):
        try:
            s_date = datetime.datetime.strptime(str(start_date_str), "%Y%m%d").date()
            today = datetime.date.today()
            diff = (s_date - today).days
            if diff == 0:
                return "🔥 TODAY 시작!"
            elif diff < 0:
                return "🎈 진행 중"
            else:
                return f"⏳ D-{diff}"
        except Exception:
            return "-"

    df_festivals["D-Day"] = df_festivals["eventstartdate"].apply(calc_dday)

    # Sidebar 검색 필터
    st.sidebar.header("🔍 축제 필터링")
    search_keyword = st.sidebar.text_input("축제 이름 검색", "")
    
    filtered_df = df_festivals.copy()
    if search_keyword:
        filtered_df = filtered_df[filtered_df["title"].str.contains(search_keyword, na=False)]

    col_map, col_list = st.columns([1.2, 0.8])

    with col_map:
        # Folium 지도 생성 (한국 중심)
        m = folium.Map(location=[36.5, 127.5], zoom_start=7)
        
        # 좌표값이 유효한 데이터만 마커 추가
        valid_coords = filtered_df.dropna(subset=["mapx", "mapy"])
        for _, row in valid_coords.iterrows():
            if row["mapx"] > 0 and row["mapy"] > 0:
                popup_html = f"""
                <div style="width:200px">
                    <h4>{row['title']}</h4>
                    <p><b>기간:</b> {row.get('eventstartdate', '')} ~ {row.get('eventenddate', '')}</p>
                    <p><b>장소:</b> {row.get('addr1', '정보 없음')}</p>
                </div>
                """
                folium.Marker(
                    location=[row["mapy"], row["mapx"]],
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=f"[{row['D-Day']}] {row['title']}",
                    icon=folium.Icon(color="red" if "TODAY" in row["D-Day"] else "blue", icon="star")
                ).add_to(m)

        st_folium(m, width="100%", height=500, returned_objects=[])

    with col_list:
        st.write(f"총 **{len(filtered_df)}**개의 축제가 검색되었습니다.")
        
        # 카드 형태로 목록 보여주기
        for _, row in filtered_df.head(10).iterrows():
            with st.expander(f"[{row['D-Day']}] {row['title']}"):
                img_url = row.get("firstimage")
                if img_url:
                    st.image(img_url, use_column_width=True)
                st.write(f"**위치:** {row.get('addr1', '정보 없음')}")
                st.write(f"**기간:** {row.get('eventstartdate')} ~ {row.get('eventenddate')}")
                if row.get("tel"):
                    st.write(f"**문의:** {row.get('tel')}")


# ==========================================
# Tab 2: 재미 요소 - 랜덤 축제 룰렛
# ==========================================
with tab2:
    st.subheader("🎲 주말에 뭐 하지? 랜덤 축제 뽑기!")
    st.write("어디로 갈지 고민된다면 룰렛을 돌려 결정해 보세요.")

    if st.button("✨ 오늘의 랜덤 축제 뽑기!", type="primary"):
        random_row = filtered_df.sample(n=1).iloc[0]
        
        st.balloons()  # 성공 축하 효과
        
        st.markdown(f"### 🎉 당첨된 축제: **{random_row['title']}**")
        
        r_col1, r_col2 = st.columns([1, 1])
        with r_col1:
            img = random_row.get("firstimage")
            if img:
                st.image(img, caption=random_row['title'], use_column_width=True)
            else:
                st.info("📷 해당 축제는 대표 이미지가 없습니다.")
        
        with r_col2:
            st.success(f"**상태:** {random_row['D-Day']}")
            st.write(f"📍 **주소:** {random_row.get('addr1', '주소 정보 없음')}")
            st.write(f"📅 **일정:** {random_row.get('eventstartdate')} ~ {random_row.get('eventenddate')}")
            if random_row.get('tel'):
                st.write(f"📞 **전화번호:** {random_row.get('tel')}")
