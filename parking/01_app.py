import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="서울시 공영주차장 안내",
    page_icon="🅿️",
    layout="wide"
)

st.title("🅿️ 서울시 공영주차장 안내 서비스")

uploaded_file = st.file_uploader(
    "서울시 공영주차장 CSV 업로드",
    type=["csv"]
)

if uploaded_file:

    # ===========================
    # CSV 읽기 (자동 인코딩)
    # ===========================

    df = None

    for enc in ["utf-8", "utf-8-sig", "cp949", "euc-kr"]:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding=enc)
            st.success(f"{enc} 인코딩으로 읽었습니다.")
            break
        except:
            pass

    if df is None:
        st.error("CSV 파일을 읽을 수 없습니다.")
        st.stop()

    # ===========================
    # 컬럼명 공백 제거
    # ===========================

    df.columns = df.columns.str.strip()

    # ===========================
    # 좌표 없는 데이터 제거
    # ===========================

    df = df.dropna(subset=["위도", "경도"])

    df["위도"] = pd.to_numeric(df["위도"], errors="coerce")
    df["경도"] = pd.to_numeric(df["경도"], errors="coerce")

    df = df.dropna(subset=["위도", "경도"])

    st.subheader("📋 데이터")

    st.dataframe(df)

    # ===========================
    # 검색
    # ===========================

    keyword = st.text_input(
        "주소 또는 주차장명을 입력하세요",
        placeholder="예) 강남구, 송파구, 테헤란로"
    )

    if keyword:

        result = df[
            df["주소"].astype(str).str.contains(keyword, case=False, na=False)
            |
            df["주차장명"].astype(str).str.contains(keyword, case=False, na=False)
        ]

    else:

        result = df

    if result.empty:

        st.warning("검색 결과가 없습니다.")
        st.stop()

    st.success(f"{len(result)}개의 주차장을 찾았습니다.")

    # ===========================
    # 지도
    # ===========================

    center_lat = result.iloc[0]["위도"]
    center_lon = result.iloc[0]["경도"]

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=13
    )

    for _, row in result.iterrows():

        popup = f"""
        <b>{row['주차장명']}</b><br>
        주소 : {row['주소']}<br>
        기본요금 : {row.get('기본 주차 요금','-')}<br>
        기본시간 : {row.get('기본 주차 시간(분 단위)','-')}분<br>
        추가요금 : {row.get('추가 단위 요금','-')}<br>
        """

        folium.Marker(
            [row["위도"], row["경도"]],
            tooltip=row["주차장명"],
            popup=popup,
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)

    st.subheader("🗺️ 공영주차장 위치")

    st_folium(
        m,
        width=1000,
        height=600
    )

    # ===========================
    # 검색 결과
    # ===========================

    st.subheader("📍 검색 결과")

    show_columns = []

    for col in [
        "주차장명",
        "주소",
        "기본 주차 요금",
        "기본 주차 시간(분 단위)",
        "추가 단위 요금",
        "운영요일",
        "평일 운영 시작시각",
        "평일 운영 종료시각"
    ]:
        if col in result.columns:
            show_columns.append(col)

    st.dataframe(
        result[show_columns],
        use_container_width=True
    )
