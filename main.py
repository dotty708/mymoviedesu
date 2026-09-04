import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="영화 데이터 그래프 도감 2 - 분포와 관계", layout="wide")
st.title("영화 데이터 그래프 도감 2 - 분포와 관계")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data():
    # 1년간 박스오피스 10위권에 든 영화 216편의 요약표를 불러옵니다
    df = pd.read_csv(DATA_URL)
    # 장르가 세로막대 기호(|)로 여러 개 적힌 영화는 첫 번째 장르만 씁니다
    df["장르"] = df["genre"].str.split("|").str[0]
    return df


df = load_data()

# ── 그래프 1. 장르별 영화 편수 도넛 ──
st.header("1. 장르별 영화 편수 (도넛)")
genre_count = df["장르"].value_counts().reset_index()
genre_count.columns = ["장르", "편수"]

fig = px.pie(
    genre_count,
    names="장르",
    values="편수",
    hole=0.45,  # 가운데 구멍을 뚫어 도넛 모양으로
)
# 조각에 마우스를 올리면 편수와 비율이 보이게 합니다
fig.update_traces(hovertemplate="%{label}<br>%{value}편 (%{percent})<extra></extra>")
st.plotly_chart(fig, width="stretch")

# '이 그래프로 알 수 있는 것' 한 문장을 적는 자리
st.text_input("이 그래프로 알 수 있는 것", key="note1")

st.divider()

# ── 그래프 2. 장르 → 영화 트리맵 ──
st.header("2. 장르 속 영화 크기 비교 (트리맵)")

# 트리맵은 크기 값이 비어 있으면 그려지지 않으므로 결측치를 먼저 걸러 냅니다
tree_df = df.dropna(subset=["total_audi"])

fig2 = px.treemap(
    tree_df,
    path=["장르", "movie_name"],  # 바깥칸=장르, 안쪽칸=영화
    values="total_audi",          # 칸의 넓이 = 총 관객
    color="장르",
)
# customdata로 총 관객을 넘겨 주면 hovertemplate에서 콤마를 찍어 보여 줄 수 있습니다
fig2.update_traces(
    hovertemplate="%{label}<br>총 관객 %{value:,.0f}명<extra></extra>",
    root_color="lightgrey",
)
fig2.update_layout(margin=dict(t=30, l=10, r=10, b=10))
st.plotly_chart(fig2, width="stretch")

st.text_input("이 그래프로 알 수 있는 것", key="note2")

st.divider()

# ── 그래프 3. 총 관객 히스토그램 ──
st.header("3. 총 관객 분포 (히스토그램)")

hist_df = df.dropna(subset=["total_audi"])

fig3 = px.histogram(
    hist_df,
    x="total_audi",
    nbins=30,  # 막대(구간) 개수. 숫자를 바꿔 보며 분포 모양을 살펴보세요
    labels={"total_audi": "총 관객(명)"},
)
fig3.update_traces(hovertemplate="관객 구간 %{x}<br>영화 %{y}편<extra></extra>")
fig3.update_layout(yaxis_title="영화 편수", bargap=0.05)
st.plotly_chart(fig3, width="stretch")

# 어느 구간에 가장 많이 몰려 있는지 직접 계산해서 문장으로 보여 줍니다
counts, bin_edges = pd.cut(hist_df["total_audi"], bins=30, retbins=True)
top_bin = counts.value_counts().idxmax()          # 영화가 가장 많이 든 구간
top_bin_n = counts.value_counts().max()           # 그 구간의 영화 편수

# 관객 수가 가장 많은 영화 한 편 찾기
best = hist_df.loc[hist_df["total_audi"].idxmax()]

st.info(
    f"영화가 가장 많이 몰린 구간은 **약 {top_bin.left:,.0f}명 ~ {top_bin.right:,.0f}명** 이며, "
    f"이 구간에만 **{top_bin_n}편**이 들어 있습니다.\n\n"
    f"총 관객이 가장 많은 영화는 **{best['movie_name']}** 으로 "
    f"**{best['total_audi']:,.0f}명**입니다."
)

st.text_input("이 그래프로 알 수 있는 것", key="note3")

st.divider()

# ── 그래프 4. 개봉일 스크린수 vs 총 관객 산점도 ──
st.header("4. 개봉일 스크린수와 총 관객의 관계 (산점도)")

scat_df = df.dropna(subset=["first_scrn", "total_audi"])

fig4 = px.scatter(
    scat_df,
    x="first_scrn",
    y="total_audi",
    color="장르",                 # 장르별로 점 색을 다르게
    hover_name="movie_name",      # 마우스를 올리면 영화명이 제목으로 뜸
    labels={"first_scrn": "개봉일 스크린수(개)", "total_audi": "총 관객(명)"},
)
fig4.update_traces(marker=dict(size=9, opacity=0.75))
st.plotly_chart(fig4, width="stretch")

st.text_input("이 그래프로 알 수 있는 것", key="note4")

st.divider()

# ── 그래프 5. 편수 10편 이상 장르의 상자 그림 ──
st.header("5. 장르별 총 관객 분포 (상자 그림)")

box_df = df.dropna(subset=["total_audi"])

# 편수가 10편 이상인 장르만 추려 냅니다 (표본이 적으면 상자 모양이 왜곡되기 때문)
big_genres = box_df["장르"].value_counts()
big_genres = big_genres[big_genres >= 10].index
box_df = box_df[box_df["장르"].isin(big_genres)]

fig5 = px.box(
    box_df,
    x="장르",
    y="total_audi",
    color="장르",
    points="outliers",        # 상자 밖으로 튀는 값만 점으로 표시
    hover_name="movie_name",  # 그 점에 마우스를 올리면 영화명이 보임
    labels={"total_audi": "총 관객(명)"},
)
fig5.update_layout(showlegend=False)
st.plotly_chart(fig5, width="stretch")

st.caption(f"영화가 10편 이상인 장르만 표시했습니다: {', '.join(big_genres)}")

st.text_input("이 그래프로 알 수 있는 것", key="note5")

st.divider()

# ── 그래프 6. 첫 주 관객을 점 크기로 넣은 버블 그래프 ──
st.header("6. 첫 주 관객을 점 크기로 (버블 그래프)")

bub_df = df.dropna(subset=["first_scrn", "total_audi", "first_week_audi"])

fig6 = px.scatter(
    bub_df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",   # 점 크기 = 첫 주 관객
    color="장르",
    hover_name="movie_name",
    size_max=45,              # 가장 큰 점의 최대 크기
    labels={
        "first_scrn": "개봉일 스크린수(개)",
        "total_audi": "총 관객(명)",
        "first_week_audi": "첫 주 관객(명)",
    },
)
fig6.update_traces(marker=dict(opacity=0.65, line=dict(width=0.5, color="white")))
st.plotly_chart(fig6, width="stretch")

st.text_input("이 그래프로 알 수 있는 것", key="note6")

st.divider()

# ── 그래프 7. 제작 국가 → 장르 선버스트 ──
st.header("7. 제작 국가에서 장르로 (선버스트)")

sun_df = df.dropna(subset=["nation", "장르"]).copy()
# 편수를 세기 위해 모든 행에 1을 넣은 열을 만듭니다
sun_df["편수"] = 1

fig7 = px.sunburst(
    sun_df,
    path=["nation", "장르"],  # 안쪽 원=국가, 바깥 원=장르
    values="편수",
    color="nation",
)
fig7.update_traces(hovertemplate="%{label}<br>%{value:.0f}편<extra></extra>")
fig7.update_layout(margin=dict(t=30, l=10, r=10, b=10))
st.plotly_chart(fig7, width="stretch")

st.text_input("이 그래프로 알 수 있는 것", key="note7")
