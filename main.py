import streamlit as st
import pandas as pd
import altair as alt

# ---------------------------
# 🎯 기본 설정
# ---------------------------
st.set_page_config(page_title="MBTI by Country", page_icon="🌍", layout="wide")

st.title("🌍 국가별 MBTI 분포 분석 대시보드")
st.markdown("**특정 MBTI 유형이 높은 국가 TOP 10**을 시각적으로 확인할 수 있는 대시보드입니다.")

# ---------------------------
# 📂 데이터 불러오기
# ---------------------------
@st.cache_data
def load_data():
    # 업로드된 CSV 파일 경로 또는 URL 수정 가능
    df = pd.read_csv("countriesMBTI_16types.csv")
    return df

df = load_data()

# ---------------------------
# 🔍 데이터 확인
# ---------------------------
st.subheader("데이터 미리보기")
st.dataframe(df.head())

# ---------------------------
# 🧠 사용자 입력
# ---------------------------
st.sidebar.header("🔧 분석 설정")

# MBTI 컬럼명 자동 탐색
mbti_cols = [c for c in df.columns if "mbti" in c.lower() or "type" in c.lower() or "personality" in c.lower()]

if not mbti_cols:
    st.error("❗ MBTI 관련 컬럼을 찾을 수 없습니다. 파일에 'MBTI' 또는 'type' 단어가 포함된 컬럼이 있는지 확인해주세요.")
    st.stop()

# 국가 컬럼 추정
country_cols = [c for c in df.columns if "country" in c.lower() or "nation" in c.lower() or "location" in c.lower()]
if not country_cols:
    st.error("❗ 국가 관련 컬럼을 찾을 수 없습니다. 파일에 'country' 또는 'nation' 단어가 포함된 컬럼이 있는지 확인해주세요.")
    st.stop()

country_col = country_cols[0]
mbti_col = mbti_cols[0]

# ---------------------------
# 📊 유형 선택
# ---------------------------
unique_mbti = sorted(df[mbti_col].dropna().unique())
selected_type = st.sidebar.selectbox("분석할 MBTI 유형 선택", unique_mbti, index=0)

# ---------------------------
# 📈 집계 및 시각화
# ---------------------------
st.subheader(f"🧩 {selected_type} 유형이 많은 국가 TOP 10")

# 국가별 개수 집계
top_countries = (
    df[df[mbti_col] == selected_type]
    .groupby(country_col)
    .size()
    .reset_index(name="count")
    .sort_values("count", ascending=False)
    .head(10)
)

# 시각화: Altair
chart = (
    alt.Chart(top_countries)
    .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
    .encode(
        x=alt.X("count:Q", title="인원 수", axis=alt.Axis(grid=False)),
        y=alt.Y(f"{country_col}:N", sort='-x', title="국가"),
        color=alt.Color("count:Q", scale=alt.Scale(scheme="tealblues")),
        tooltip=[country_col, "count"]
    )
    .properties(width=700, height=400)
    .configure_axis(labelFontSize=12, titleFontSize=13)
)

st.altair_chart(chart, use_container_width=True)

# ---------------------------
# 🧾 부가 기능
# ---------------------------
with st.expander("🔎 상세 데이터 보기"):
    st.dataframe(top_countries)

st.markdown("---")
st.caption("📘 데이터 출처: countriesMBTI_16types.csv | 시각화: Altair | 작성자: Streamlit Cloud 예시 앱")

