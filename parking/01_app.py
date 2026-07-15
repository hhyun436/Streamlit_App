import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

st.set_page_config(
    page_title="공영주차장 안내",
    page_icon="🅿️",
    layout="wide"
)

st.title("🅿️ 공영주차장 정보 제공 서비스")

uploaded_file = st.file_uploader(
    "공영주차장 CSV 업로드",
    type="csv"
)

if uploaded_file:

    df = pd.read_csv(uploaded_file)

    st.success("CSV 업로드 완료!")

    st.subheader("데이터 미리보기")
    st.dataframe(df)

    address = st.text_input(
        "검색할 주소를 입력하세요",
        placeholder="예) 서울특별시 강남구 테헤란로"
    )

    if address:

        geolocator = Nominatim(user_agent="parking_app")

        location = geolocator.geocode(address)

        if location:

            user_location = (
                location.latitude,
                location.longitude
            )

            distances = []

            for _, row in df.iterrows():

                parking = (
                    row["위도"],
                    row["경도"]
                )

                dist = geodesic(
                    user_location,
                    parking
                ).km

                distances.append(dist)

            df["거리(km)"] = distances

            nearest = df.sort_values("거리(km)").iloc[0]

            st.subheader("가장 가까운 공영주차장")

            st.write("###", nearest["주차장명"])
            st.write("📍 주소 :", nearest["주소"])
            st.write("💰 기본요금 :", nearest["기본요금"])
            st.write("➕ 추가요금 :", nearest["추가요금"])
            st.write(f"📏 거리 : {nearest['거리(km)']:.2f} km")

            m = folium.Map(
                location=user_location,
                zoom_start=13
            )

            folium.Marker(
                user_location,
                tooltip="검색한 위치",
                icon=folium.Icon(color="red")
            ).add_to(m)

            for _, row in df.iterrows():

                popup = f"""
                <b>{row['주차장명']}</b><br>
                주소 : {row['주소']}<br>
                기본요금 : {row['기본요금']}<br>
                추가요금 : {row['추가요금']}
                """

                folium.Marker(
                    [row["위도"], row["경도"]],
                    tooltip=row["주차장명"],
                    popup=popup,
                    icon=folium.Icon(color="blue", icon="info-sign")
                ).add_to(m)

            st.subheader("지도")

            st_folium(
                m,
                width=900,
                height=600
            )

            st.subheader("거리순 주차장")

            st.dataframe(
                df.sort_values("거리(km)")
            )

        else:
            st.error("주소를 찾을 수 없습니다.")
