import os
from datetime import datetime

import pandas as pd
import streamlit as st

# ========== 基本設定 ==========
DATA_FILE = "feedback_data.csv"
COLUMNS = ["填寫時間", "姓名", "科系", "滿意度", "意見回饋"]
DEPARTMENTS = ["資訊工程系", "電子工程系", "其他"]
SATISFACTION_LABELS = {
    1: "😞 非常不滿意",
    2: "🙁 不滿意",
    3: "😐 普通",
    4: "🙂 滿意",
    5: "😍 非常滿意",
}

st.set_page_config(page_title="課程回饋表單", page_icon="📝", layout="wide")


# ========== 資料存取 ==========
def load_data() -> pd.DataFrame:
    """讀取已保存的回饋資料，若檔案不存在則回傳空表。"""
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE, encoding="utf-8-sig")
    return pd.DataFrame(columns=COLUMNS)


def save_record(record: dict) -> None:
    """將一筆回饋附加到 CSV 檔中。"""
    df = load_data()
    new_row = pd.DataFrame([record], columns=COLUMNS)
    df = new_row if df.empty else pd.concat([df, new_row], ignore_index=True)
    df.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")


# ========== 側邊欄 ==========
with st.sidebar:
    st.title("📚 課程回饋系統")
    page = st.radio("📂 頁面切換", ["📝 填寫表單", "📊 統計結果"])

    st.divider()
    st.subheader("📖 使用說明")
    st.markdown(
        """
        1. 在 **📝 填寫表單** 輸入姓名（必填）
        2. 選擇科系並拖曳滿意度
        3. 寫下你的意見後按 **🚀 送出**
        4. 到 **📊 統計結果** 查看平均滿意度與圖表
        """
    )

    st.divider()
    st.caption(f"🗂️ 目前共有 **{len(load_data())}** 筆回饋")


# ========== 填寫結果卡片 ==========
def show_result(record: dict) -> None:
    st.success("🎉 感謝你的回饋！以下是你的填寫結果：")
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"**👤 姓名**  \n{record['姓名']}")
        c2.markdown(f"**🏫 科系**  \n{record['科系']}")
        c3.markdown(f"**⭐ 滿意度**  \n{SATISFACTION_LABELS[record['滿意度']]}")
        st.markdown(f"**💬 意見回饋**  \n{record['意見回饋'] or '（未填寫）'}")
        st.caption(f"🕒 填寫時間：{record['填寫時間']}")


# ========== 頁面：填寫表單 ==========
def form_page() -> None:
    st.title("📝 課程回饋表單")
    st.caption("你的意見能幫助我們讓課程變得更好 🙌")

    with st.form("feedback_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("👤 姓名 *", placeholder="請輸入你的姓名")
        with col2:
            department = st.selectbox("🏫 科系", DEPARTMENTS)

        satisfaction = st.select_slider(
            "⭐ 滿意度",
            options=[1, 2, 3, 4, 5],
            value=3,
            format_func=lambda x: SATISFACTION_LABELS[x],
        )
        comment = st.text_area(
            "💬 意見回饋",
            placeholder="例如：上課節奏、作業難度、希望加強的內容……",
            height=120,
        )

        submitted = st.form_submit_button("🚀 送出", type="primary")

    if submitted:
        if not name.strip():
            st.error("⚠️ 請填寫姓名後再送出！")
            st.toast("姓名尚未填寫", icon="⚠️")
            return

        record = {
            "填寫時間": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "姓名": name.strip(),
            "科系": department,
            "滿意度": satisfaction,
            "意見回饋": comment.strip(),
        }
        save_record(record)
        st.session_state.last_record = record
        st.balloons()

    if "last_record" in st.session_state:
        show_result(st.session_state.last_record)


# ========== 頁面：統計結果 ==========
def stats_page() -> None:
    st.title("📊 統計結果")
    df = load_data()

    if df.empty:
        st.info("📭 目前還沒有任何回饋，快去填寫第一份吧！")
        return

    # 指標卡
    c1, c2, c3 = st.columns(3)
    c1.metric("📋 回饋總數", f"{len(df)} 份")
    c2.metric("⭐ 平均滿意度", f"{df['滿意度'].mean():.2f} / 5")
    c3.metric("👍 滿意比例（4 分以上）", f"{(df['滿意度'] >= 4).mean() * 100:.0f}%")

    st.divider()

    # 圖表
    left, right = st.columns(2)
    with left:
        st.subheader("📈 滿意度分布")
        counts = df["滿意度"].value_counts().reindex([1, 2, 3, 4, 5], fill_value=0)
        counts.index = [f"{i} 分" for i in counts.index]
        st.bar_chart(counts, y_label="人數")
    with right:
        st.subheader("🏫 各科系平均滿意度")
        dept_avg = df.groupby("科系")["滿意度"].mean().round(2)
        st.bar_chart(dept_avg, y_label="平均滿意度")

    st.divider()

    # 原始資料
    st.subheader("🗒️ 所有回饋")
    st.dataframe(df.iloc[::-1], hide_index=True)
    st.download_button(
        "📥 下載 CSV",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name="feedback_data.csv",
        mime="text/csv",
    )


# ========== 主程式 ==========
if page == "📝 填寫表單":
    form_page()
else:
    stats_page()