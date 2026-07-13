import streamlit as st
from datetime import datetime
import hashlib

st.set_page_config(
    page_title="👻 한국귀신 상성 테스트",
    page_icon="👻",
)

st.title("👻 한국귀신 상성 테스트")
st.markdown(
"""
생년월일을 입력하면

- 👻 상성이 잘 맞는 한국 귀신
- 😱 상성이 맞지 않는 한국 귀신
- 🍀 행운의 한국 민속 아이템
- 🛡️ 액막이 민속 아이템

을 알려드립니다.

※ 재미로 즐기는 민속 판타지 콘텐츠입니다.
"""
)

ghosts = [
    {
        "name":"도깨비",
        "desc":"장난을 좋아하지만 의리가 있는 존재.",
        "good_item":"복주머니",
        "bad_item":"청동 방울"
    },
    {
        "name":"처녀귀신",
        "desc":"한을 품은 영혼.",
        "good_item":"비녀",
        "bad_item":"쑥과 마늘"
    },
    {
        "name":"물귀신",
        "desc":"물가를 떠도는 귀신.",
        "good_item":"청사초롱",
        "bad_item":"부적"
    },
    {
        "name":"달걀귀신",
        "desc":"둥근 머리로 전해지는 민담 속 존재.",
        "good_item":"호리병",
        "bad_item":"오방색 실"
    },
    {
        "name":"야광귀",
        "desc":"섣달그믐 밤 신발을 훔쳐가는 존재.",
        "good_item":"짚신",
        "bad_item":"체(키질하는 체)"
    },
    {
        "name":"손각시",
        "desc":"슬픈 사연을 간직한 여귀.",
        "good_item":"노리개",
        "bad_item":"경면주사 부적"
    },
    {
        "name":"장산범",
        "desc":"사람의 목소리를 흉내 낸다는 전설의 존재.",
        "good_item":"범무늬 주머니",
        "bad_item":"호랑이 그림"
    },
    {
        "name":"구미호",
        "desc":"천 년을 산 여우.",
        "good_item":"옥비녀",
        "bad_item":"은방울"
    },
    {
        "name":"망태할아버지",
        "desc":"아이들을 훈계하는 민속 속 존재.",
        "good_item":"복주머니",
        "bad_item":"대나무 지팡이"
    },
    {
        "name":"저승사자",
        "desc":"죽은 이를 인도하는 존재.",
        "good_item":"흰 부채",
        "bad_item":"금줄"
    },
]

lucky_items = [
    "복주머니",
    "노리개",
    "청사초롱",
    "부적",
    "금줄",
    "오방색 실",
    "쑥과 마늘",
    "호리병",
    "은비녀",
    "경면주사 부적",
]

birthday = st.date_input(
    "생년월일",
    min_value=datetime(1900,1,1),
    max_value=datetime.today()
)

if st.button("결과 보기"):

    key = birthday.strftime("%Y%m%d")

    h = hashlib.sha256(key.encode()).hexdigest()

    n1 = int(h[:8],16)
    n2 = int(h[8:16],16)
    n3 = int(h[16:24],16)

    good = ghosts[n1 % len(ghosts)]

    bad = ghosts[n2 % len(ghosts)]

    while bad["name"] == good["name"]:
        n2 += 1
        bad = ghosts[n2 % len(ghosts)]

    lucky = lucky_items[n3 % len(lucky_items)]

    st.divider()

    st.subheader("✨ 당신과 가장 잘 맞는 한국 귀신")

    st.success(f"👻 {good['name']}")

    st.write(good["desc"])

    st.info(f"🍀 함께하면 좋은 민속 아이템 : **{good['good_item']}**")

    st.divider()

    st.subheader("⚠️ 상성이 좋지 않은 한국 귀신")

    st.error(f"😱 {bad['name']}")

    st.write(bad["desc"])

    st.warning(f"🛡️ 대비 아이템 : **{bad['bad_item']}**")

    st.divider()

    st.subheader("🎁 오늘의 행운 아이템")

    st.success(f"🍀 {lucky}")

    st.caption("※ 본 결과는 한국 민속을 바탕으로 한 재미용 콘텐츠입니다.")
