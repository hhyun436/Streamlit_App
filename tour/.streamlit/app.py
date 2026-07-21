import streamlit as st
import requests
import pandas as pd
import random
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="대한민국 축제 탐방",
    page_icon="🎉",
    layout="wide"
)

API_KEY = st.secrets["TOUR_API_KEY"]

st.title("🎉 대한민국 축제 탐방")
st.caption("한국관광공사 TourAPI 활용")

# ------------------------
# API 호출
# ------------------------

url = "https://apis.data.go.kr/B551011/KorService1/searchFestival1"

params = {
    "serviceKey": API_KEY,
    "MobileOS": "ETC",
    "MobileApp": "FestivalApp",
    "_type": "json",
    "listYN": "Y",
    "arrange": "A",
    "numOfRows": 200,
    "pageNo": 1,
    "eventStartDate": datetime.today().strftime("%Y%m%d")
}

response = requests.get(url, params=params)

try:
    items = response.json()["response"]["body"]["items"]["item"]
except:
    st.error("API 데이터를 불러오지 못했습니다.")
    st.stop()

df = pd.DataFrame(items)

# ------------------------
# 필요한 컬럼
# ------------------------

columns = [
    "title",
    "addr1",
    "firstimage",
    "eventstartdate",
    "eventenddate"
]

for c in columns:
    if c not in df.columns:
        df[c] = ""

df = df[columns]

# ------------------------
# 지역 만들기
# ------------------------

df["지역"] = df["addr1"].str.split().str[0]

# ------------------------
# 상태
# ------------------------

today = int(datetime.today().strftime("%Y%m%d"))

def status(row):

    try:
        s = int(row["eventstartdate"])
        e = int(row["eventenddate"])

        if s <= today <= e:
            return "🟢 진행중"

        elif today < s:
            return "🟡 예정"

        else:
            return "⚫ 종료"

    except:
        return ""

df["상태"] = df.apply(status, axis=1)

# ------------------------
# 사이드바
# ------------------------

st.sidebar.header("검색")

regions = ["전체"] + sorted(df["지역"].dropna().unique())

region = st.sidebar.selectbox(
    "지역",
    regions
)

keyword = st.sidebar.text_input("축제명 검색")

# ------------------------
# 필터
# ------------------------

result = df.copy()

if region != "전체":
    result = result[result["지역"] == region]

if keyword:
    result = result[result["title"].str.contains(keyword, case=False)]

# ------------------------
# 추천
# ------------------------

st.subheader("🎲 오늘의 추천 축제")

if st.button("추천받기"):

    if len(result):

        festival = result.sample(1).iloc[0]

        st.success(f"오늘은 **{festival['title']}** 어떠세요?")

# ------------------------
# 그래프
# ------------------------

st.subheader("📊 지역별 축제 수")

count = result["지역"].value_counts().reset_index()
count.columns = ["지역","축제수"]

fig = px.bar(
    count,
    x="지역",
    y="축제수",
    color="축제수"
)

st.plotly_chart(fig, use_container_width=True)

# ------------------------
# 다운로드
# ------------------------

csv = result.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    "CSV 다운로드",
    csv,
    "festival.csv",
    "text/csv"
)

# ------------------------
# 카드 출력
# ------------------------

st.subheader(f"축제 {len(result)}개")

for _, row in result.iterrows():

    col1, col2 = st.columns([1,3])

    with col1:

        if row["firstimage"]:
            st.image(row["firstimage"], width=180)
        else:
            st.image("https://via.placeholder.com/180x120?text=No+Image")

    with col2:

        st.markdown(f"### {row['title']}")

        st.write(row["상태"])

        st.write("📍", row["addr1"])

        st.write(
            f"📅 {row['eventstartdate']} ~ {row['eventenddate']}"
        )

    st.divider()
