import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

st.set_page_config(
    page_title="서울시 공영주차장 안내",
    page_icon="🅿️",
    layout="wide"
)

st.title("🅿️ 서울시 공영주차장 안내")

uploaded_file = st.file_uploader(
    "서울시 공영주차장 CSV 업로드",
    type=["csv"]
)

if uploaded_file:

    # -------------------------
    # CSV 읽기 (자동 인코딩)
    # -------------------------
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
        st.error("CSV를 읽을 수 없습니다.")
        st.stop()

    # -------------------------
    # 좌표 없는 데이터 제거
    # -------------------------
    df = df.dropna(subset=["위도", "경도"])

    df["위도"] = pd.to_numeric(df["위도"])
    df["경도"] = pd.to_numeric(df["경도"])

    st.subheader("데이터 미리보기")
    st.dataframe(df)

    address = st.text_input(
        "주소를 입력하세요",
        placeholder="예) 서울특별시 강남구 테헤란로"
    )

    if address:

        geolocator = Nominatim(user_agent="parking_app")

        location = geolocator.geocode(address)

        if location is None:
            st.error("주소를 찾을 수 없습니다.")
            st.stop()

        user_location = (
            location.latitude,
            location.longitude
        )

        # -------------------------
        # 거리 계산
        # -------------------------
        distances = []

        for _, row in df.iterrows():

            parking = (
                row["위도"],
                row["경도"]
            )

            distances.append(
                geodesic(
                    user_location,
                    parking
                ).km
            )

        df["거리(km)"] = distances

        nearest = df.sort_values("거리(km)").iloc[0]

        st.subheader("가장 가까운 공영주차장")

        c1, c2 = st.columns(2)

        with c1:

            st.metric(
                "주차장",
                nearest["주차장명"]
            )

            st.write("📍", nearest["주소"])

            st.write(
                f"💰 기본요금 : {nearest['기본 주차 요금']}원"
            )

            st.write(
                f"⏰ 기본시간 : {nearest['기본 주차 시간(분 단위)']}분"
            )

            if pd.notna(nearest["추가 단위 요금"]):
                st.write(
                    f"➕ 추가요금 : {nearest['추가 단위 요금']}원"
                )

            st.write(
                f"📏 거리 : {nearest['거리(km)']:.2f} km"
            )

        # -------------------------
        # 지도
        # -------------------------

        m = folium.Map(
            location=user_location,
            zoom_start=13
        )

        folium.Marker(
            user_location,
            tooltip="검색 위치",
            icon=folium.Icon(color="red")
        ).add_to(m)

        for _, row in df.iterrows():

            popup = f"""
            <b>{row['주차장명']}</b><br>
            주소 : {row['주소']}<br>
            기본요금 : {row['기본 주차 요금']}원<br>
            기본시간 : {row['기본 주차 시간(분 단위)']}분<br>
            추가요금 : {row['추가 단위 요금']}원
            """

            folium.Marker(
                [row["위도"], row["경도"]],
                tooltip=row["주차장명"],
                popup=popup,
                icon=folium.Icon(color="blue")
            ).add_to(m)

        st.subheader("공영주차장 지도")

        st_folium(
            m,
            width=1000,
            height=650
        )

        st.subheader("거리순 주차장")

        st.dataframe(
            df.sort_values("거리(km)")[
                [
                    "주차장명",
                    "주소",
                    "기본 주차 요금",
                    "기본 주차 시간(분 단위)",
                    "거리(km)"
                ]
            ]
        )
