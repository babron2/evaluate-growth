import json
import streamlit as st
from datetime import datetime, timedelta, date
from gcp_modules import Gcs_client

st.markdown(
    """
    <style>
    body > div {
        padding: 20% 20% 10% 10%;
    }
    [data-testid="column"] {
        box-shadow: 0 4px 15px rgba(0,0,0,.2);
        border-radius: 15px;
        border: solid #fff;
        padding: 10% 10% 10% 10%;
        text-align: center;
        font-family: "Source Sans Pro", sans-serif, "Segoe UI", Roboto, sans-serif;
        font-size: 1rem;
        font-weight: 400;
        -- color: rgb(49, 51, 63);
        --background-color: rgba(0, 0, 0, 0.5);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

growth_dic = {
    "顔を見つめる": 1,
    "声を出す": 1,
    "左右対称に体を動かす": 1,
    "大きな音に反応する": 1,
    "意味なくにっこりする": 1,
    "頭をあげる": 3,
    "声を出して笑う": 3,
    "顔を見て笑う": 4,
    "ガラガラをふる": 4,
    "首がすわる": 4,
    "かん高い声を出す": 4.5,
    "追視をする": 4.5,
    "両手を合わせる": 4.5,
    "声の方に振り向く": 6,
    "物に手を伸ばす": 6,
    "寝返りをする": 7.5,
    "支えなしに座る": 7.5,
    "いないいないばあを喜ぶ": 8,
    "物を持ちかえる": 8,
    "2つの物をもつ": 8,
    "はいはいをする": 10,
    "つかまり立ちができる": 10,
    "意味なくパパ、ママをいう": 10,
    "つたい歩きができる": 11,
    "知らない人を意識する": 11,
    "一人で立っていられる": 14,
    "意味のある一語をいう": 14,
    "なぐりがきで絵が描ける": 14,
    "コップから水を飲む": 15,
    "上手に歩く": 15,
    "３語以上話す": 16,
    "積み木を積み上げる": 16,
}

st.markdown("# 発達予報")
with st.expander("利用規約", expanded=False):
    st.write(
        """
        このアプリは、子どもの成長や発達に関する情報を提供することを目的としたものです。
        主な機能は、現在の月齢に基づいた発達検査と、生後16ヶ月までに獲得するであろう動きを予測することです。
        ただし、アプリの情報は一般的な指標であり、個々の子どもの発達には個人差があります。

        したがって、アプリの情報を参考にしながらも、必要に応じて専門家にご相談ください。
        
        利用者が提供したデータを収集し、アプリの改善や機能の追加などに使用する可能性があります。
        ただし、利用者のプライバシーを尊重し、収集したデータは適切に保管され、第三者に開示されることはありません。

        アプリの情報を用いた判断や行動によって生じた損害やトラブルについて、開発者は責任を負いかねます。

        以上の注意事項を踏まえて、このアプリを安心して利用していただけます。
        """
    )

# ラベルとデフォルトの日付を指定して、日付入力を作成する
st.markdown("## お子さまのニックネームを入力してください")
name = st.text_input("ニックネーム", "たろちゃん")

st.markdown("## お子さまの誕生日を入力してださい。")
to_day = date.today()
year = st.selectbox(
    "年", ([int(year) for year in range(to_day.year - 2, to_day.year + 1)])
)
month = st.selectbox("月", ([int(year) for year in range(1, 13)]))
day = st.selectbox("日", ([int(day) for day in range(1, 31)]))
date_string = f"{year}-{month}-{day}"
birth_day = datetime.strptime(date_string, "%Y-%m-%d").date()
past_month = round((to_day - birth_day).days / 30)
# 現在の前後の発達行動
month_growth = {}
pre_count = 0
for key, value in growth_dic.items():
    if past_month - 3 <= value <= past_month:
        month_growth[key] = "pre"
        pre_count += 1
    elif past_month + 1 <= value <= past_month + 2:
        month_growth[key] = "post"

if not st.session_state.get("button", False):
    push_button = st.button("次へ進む")
else:
    push_button = True
if push_button:
    if past_month > 16:
        st.markdown("予報可能な月齢は16ヶ月までです")
    else:
        st.session_state.button = push_button
        st.markdown(f"## {name}さんが現在可能な動きや行動を選択して下さい。月齢:{past_month}ヶ月")
        # 発達チェック
        ok_num = 0  # チェックボックスの初期値をFalseに設定
        ok_list = []
        not_ok_list = []
        for growth, label in month_growth.items():
            check = st.checkbox(f"{growth}")
            if check:
                # すでにできている行動
                ok_list.append(growth)
            elif label == "pre":  # アドバンスな動きは判定しない
                not_ok_list.append(growth)
            # できた数を数える
            ok_num += check

    if not st.session_state.get("yohou", False):
        push_yohou = st.button("予報開始")
    else:
        push_yohou = True
    if push_yohou:
        st.markdown(f"### 結果")
        st.session_state.yohou = push_yohou
        if ok_num <= pre_count // 2:
            st.write("少し発達がゆっくりです。心配な場合は、専門家にご相談ください。")
            lag_month = 2
        else:
            st.write("順調に発達しています。")
            lag_month = 0

        st.markdown(f"### {name}さんの発達予報")
        growth_predict = {}
        first_count = 0
        for key, value in growth_dic.items():
            # 経過月以降の発達行動
            if value <= past_month:
                continue
            # 日付を足し算する
            pred_day = birth_day + timedelta(days=30 * value)
            year = pred_day.year
            month = pred_day.month + lag_month
            label = f"{year}年{month}月"
            if first_count == 0:
                key = "\n".join(not_ok_list + [key])
            growth_predict[label] = growth_predict.get(label, "") + f"\n{key}"
            first_count += 1

        for label, value in growth_predict.items():
            col = st.columns(1)[0]
            with col:
                st.markdown(f"### {label}")
                for v in value.split():
                    st.text(v)

        # gcに記録
        ts = int(datetime.timestamp(datetime.now()))
        info_json = {
            "timestamp": [ts],
            "name": [name],
            "birth_day": [str(birth_day)],
            "evaluate_day": [str(to_day)],
            "growth_month": [past_month],
            "ok_list": ok_list,
            "not_ok_list": not_ok_list,
        }
        gc = Gcs_client()
        growth_data = json.dumps(info_json)
        gc.upload_gcs("growth-data", growth_data, f"{ts}.json", dry_run=False)
