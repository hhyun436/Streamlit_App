import streamlit as st
from googleapiclient.discovery import build
import pandas as pd
import re
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from datetime import datetime

# 한글 깨짐 방지를 위한 matplotlib 설정 (Streamlit Cloud 환경용)
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False

# 1. 유튜브 영상 ID 추출 함수
def extract_video_id(url):
    pattern = r'(?:v=|\/v\/|youtu\.be\/|\/embed\/|\/shorts\/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

# 2. 유튜브 댓글 수집 함수
def get_youtube_comments(api_key, video_id, max_count):
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        comments = []
        next_page_token = None
        
        while len(comments) < max_count:
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=min(100, max_count - len(comments)),
                pageToken=next_page_token,
                order="relevance" # 유용한 댓글 순으로 먼저 가져옴
            )
            response = request.execute()
            
            for item in response.get('items', []):
                snippet = item['snippet']['topLevelComment']['snippet']
                text = snippet['textDisplay']
                like_count = snippet['likeCount']
                published_at = snippet['publishedAt']
                
                comments.append({
                    'text': text,
                    'likes': like_count,
                    'date': pd.to_datetime(published_at)
                })
                
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
                
        return pd.DataFrame(comments)
    except Exception as e:
        st.error(f"데이터를 가져오는 중 오류가 발생했습니다: {e}")
        return None

# --- UI 레이아웃 구성 ---
st.set_page_config(page_title="유튜브 댓글 분석기", layout="wide")
st.title("📊 YouTube 댓글 트렌드 분석기")
st.markdown("유튜브 영상의 댓글을 수집하여 시간별 추이, 반응도, 핵심 키워드를 시각화합니다.")

# 사이드바 설정 (API 키 및 옵션)
st.sidebar.header("⚙️ 설정")
api_key = st.sidebar.text_input("YouTube API Key를 입력하세요", type="password", help="Google Cloud Console에서 발급받은 API 키가 필요합니다.")
max_comments = st.sidebar.slider("수집할 댓글 개수", min_value=10, max_value=500, value=100, step=10)

# 메인 입력창
video_url = st.text_input("분석할 유튜브 영상 링크(URL)를 입력하세요", placeholder="https://www.youtube.com/watch?v=...")

if video_url:
    video_id = extract_video_id(video_url)
    
    if not video_id:
        st.error("올바른 유튜브 URL 형식이 아닙니다. 링크를 다시 확인해주세요.")
    else:
        # 영상 임베드 화면 표시
        st.subheader("📺 선택한 영상")
        st.video(video_url)
        
        # 분석 시작 버튼
        if st.button("🚀 댓글 분석 시작"):
            if not api_key:
                st.warning("사이드바에 YouTube API Key를 먼저 입력해주세요!")
            else:
                with st.spinner("댓글을 열심히 수집하고 분석하는 중입니다..."):
                    df = get_youtube_comments(api_key, video_id, max_comments)
                    
                    if df is not None and not df.empty:
                        st.success(f"총 {len(df)}개의 댓글 수집 완료!")
                        
                        # 화면을 두 구역으로 분할
                        col1, col2 = st.columns(2)
                        
                        # --- 1. 시간대별 댓글 작성 추이 ---
                        with col1:
                            st.subheader("📈 시간대별 댓글 작성 추이")
                            # 날짜별로 정렬 및 카운트
                            df['just_date'] = df['date'].dt.date
                            date_counts = df.groupby('just_date').size().reset_index(name='댓글 수')
                            date_counts = date_counts.sort_values('just_date')
                            
                            # 시각화
                            fig, ax = plt.subplots(figsize=(7, 4))
                            ax.plot(date_counts['just_date'], date_counts['댓글 수'], marker='o', color='#FF0000', linewidth=2)
                            ax.set_xlabel('작성 날짜')
                            ax.set_ylabel('댓글 수')
                            plt.xticks(rotation=45)
                            plt.grid(True, linestyle='--', alpha=0.5)
                            st.pyplot(fig)
                        
                        # --- 2. 댓글 반응도 (좋아요 상위 댓글) ---
                        with col2:
                            st.subheader("🔥 가장 반응이 뜨거운 댓글 (좋아요 순)")
                            top_liked = df.nlargest(5, 'likes')[['text', 'likes']]
                            
                            for idx, row in top_liked.iterrows():
                                # HTML 태그 제거 간단한 처리
                                clean_text = re.sub('<[^<]+?>', '', row['text'])
                                st.markdown(f"**👍 좋아요 {row['likes']}개**")
                                st.caption(f"\"{clean_text}\"")
                                st.markdown("---")
                        
                        # --- 3. 한글 워드클라우드 ---
                        st.subheader("🔤 댓글 키워드 워드클라우드 (한글 중심)")
                        
                        # 한글 및 공백만 남기기 text 정제
                        all_text = " ".join(df['text'].values)
                        korean_text = re.sub(r'[^가-힣\s]', '', all_text)
                        
                        if len(korean_text.strip()) > 5:
                            # Streamlit Cloud 환경에는 기본 나눔폰트 등이 없으므로 
                            # 워드클라우드 내장 기본 폰트를 쓰되 무작위 에러 방지를 위해 기본 세팅 적용
                            wordcloud = WordCloud(
                                width=800, 
                                height=400, 
                                background_color='white',
                                min_font_size=10
                            ).generate(korean_text)
                            
                            fig_wc, ax_wc = plt.subplots(figsize=(10, 5))
                            ax_wc.imshow(wordcloud, interpolation='bilinear')
                            ax_wc.axis('off')
                            st.pyplot(fig_wc)
                        else:
                            st.info("분석할 만큼 충분한 한글 키워드가 댓글에 포함되어 있지 않습니다.")
                            
                    elif df is not None and df.empty:
                        st.info("이 영상에는 댓글이 존재하지 않거나 비활성화되어 있습니다.")
