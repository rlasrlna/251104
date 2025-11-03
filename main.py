import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt

# --------------------------
# 기본 설정
# --------------------------
st.set_page_config(page_title="MBTI World Dashboard", page_icon="🌎", layout="wide")

st.title("🌍 국가별 MBTI 데이터 통합 대시보드")
st.markdown("""
업로드한 CSV 데이터를 기반으로  
**좌측 지도**에서는 각 국가의 대표 MBTI를,  
**우측 그래프**에서는 선택한 MBTI 유형의 상위 10개 국가를 시각화합니다.
""")

# --------------------------
# 파일 업로드
# --------------------------
uploaded_file = st.file_uploader("📁 MBTI 데이터 CSV 업로드", type=["csv"])
if uploaded_file is None:
    st.info("👆 먼저 CSV 파일을 업로드해주세요.")
    st.stop()

try:
    df = pd.read_csv(uploaded_file)
    st.success("✅ 파일이 성공적으로 업로드되었습니다!")
except Exception as e:
    st.error(f"❌ 파일을 읽는 중 오류가 발생했습니다: {e}")
    st.stop()

with st.expander("🔎 데이터 미리보기"):
    st.dataframe(df.head())

# --------------------------
# 컬럼 설정
# --------------------------
country_col = "Country"
mbti_cols = [c for c in df.columns if c != country_col]

# --------------------------
# 🧩 국가별 MBTI Top3 계산
# --------------------------
top_types = []
for _, row in df.iterrows():
    country = row[country_col]
    sorted_types = row[mbti_cols].sort_values(ascending=False)
    top1 = sorted_types.index[0]
    top2 = sorted_types.index[1]
    top3 = sorted_types.index[2]
    top_types.append({
        "Country": country,
        "Top1_Type": top1,
        "Top1_Value": sorted_types.iloc[0],
        "Top2_Type": top2,
        "Top2_Value": sorted_types.iloc[1],
        "Top3_Type": top3,
        "Top3_Value": sorted_types.iloc[2]
    })

df_top = pd.DataFrame(top_types)

# --------------------------
# 🎨 16개 MBTI 색상 팔레트
# --------------------------
mbti_colors = {
    "ISTJ": "#1f77b4", "ISFJ": "#aec7e8", "INFJ": "#9467bd", "INTJ": "#8c564b",
    "ISTP": "#2ca02c", "ISFP": "#98df8a", "INFP": "#ff7f0e", "INTP": "#ffbb78",
    "ESTP": "#d62728", "ESFP": "#ff9896", "ENFP": "#e377c2", "ENTP": "#f7b6d2",
    "ESTJ": "#7f7f7f", "ESFJ": "#c7c7c7", "ENFJ": "#bcbd22", "ENTJ": "#17becf"
}

# --------------------------
# 🎛️ 사이드바 설정
# --------------------------
st.sidebar.header("🧭 분석 설정")
selected_type = st.sidebar.selectbox("분석할 MBTI 유형 선택", mbti_cols, index=0)

# --------------------------
# 2열 레이아웃
# --------------------------
left_col, right_col = st.columns([1.2, 1])

# --------------------------
# 🗺️ 왼쪽: Plotly 지도
# --------------------------
with left_col:
    st.subheader("🗺️ 국가별 대표 MBTI 지도")
    fig = px.choropleth(
        df_top,
        locations="Country",
        locationmode="country names",
        color="Top1_Type",
        color_discrete_map=mbti_colors,
        hover_name="Country",
        hover_data={
            "Top1_Type": True, "Top1_Value": True,
            "Top2_Type": True, "Top2_Value": True,
            "Top3_Type": True, "Top3_Value": True,
            "Country": False
        },
        title="각 국가에서 비율이 가장 높은 MBTI 유형",
        projection="natural earth"
    )
    fig.update_layout(
        legend_title_text="MBTI 유형",
        coloraxis_showscale=False,
        geo=dict(showframe=False, showcoastlines=True),
        margin=dict(l=10, r=10, t=40, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)

# --------------------------
# 📊 오른쪽: Altair 막대그래프
# --------------------------
with right_col:
    st.subheader(f"📈 {selected_type} 유형 비율 상위 10개 국가")
    top_countries = (
        df[[country_col, selected_type]]
        .sort_values(by=selected_type, ascending=False)
        .head(10)
    )

    bar_chart = (
        alt.Chart(top_countries)
        .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
        .encode(
            x=alt.X(f"{selected_type}:Q", title="비율(%)"),
            y=alt.Y(f"{country_col}:N", sort='-x', title="국가"),
            color=alt.Color(f"{selected_type}:Q", scale=alt.Scale(scheme="tealblues")),
            tooltip=[country_col, selected_type]
        )
        .properties(width="container", height=450)
    )

    st.altair_chart(bar_chart, use_container_width=True)

# --------------------------
# 📋 데이터 테이블
# --------------------------
st.markdown("### 📋 국가별 MBTI Top3 데이터")
with st.expander("세부 데이터 보기"):
    st.dataframe(df_top)

st.markdown("---")
st.caption("📘 시각화: Plotly + Altair | 데이터: 업로드된 CSV | 제작: Streamlit Cloud Demo")
