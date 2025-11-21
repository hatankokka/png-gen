import streamlit as st
import base64
import html
import os
import json
from streamlit.components.v1 import html as st_html

st.set_page_config(page_title="大判焼外交部ジェネレーター ver2.4", layout="centered")

# -----------------------------------------------------------
# ★ 一時的に session_state を全クリア（初回のみ）
# -----------------------------------------------------------
if "initialized" not in st.session_state:
    st.session_state.clear()
    st.session_state.initialized = True


# -----------------------------------------------------------
# 翻訳JSONを読み込む関数（上に置く）
# -----------------------------------------------------------
def load_lang(lang_code):
    with open(f"languages/{lang_code}.json", "r", encoding="utf-8") as f:
        return json.load(f)


# -----------------------------------------------------------
# 言語選択（セレクトボックス版 / 完全安定型）
# -----------------------------------------------------------
LANG_OPTIONS = {
    "ja": "日本語",
    "en": "English"
}

# 初期言語
if "lang" not in st.session_state:
    st.session_state.lang = "ja"

current_code = st.session_state.lang

# セレクトボックス（表示は日本語/English、中身はja/en）
selected_code = st.selectbox(
    "言語 / Language",
    options=list(LANG_OPTIONS.keys()),
    index=list(LANG_OPTIONS.keys()).index(current_code),
    format_func=lambda code: LANG_OPTIONS[code]
)

# ★ 言語が変わったら初期値も切り替え（方法2）
if selected_code != st.session_state.lang:
    st.session_state.lang = selected_code

    lang_data = load_lang(selected_code)
    st.session_state.main_text = lang_data["default_main"]
    st.session_state.footer_left = lang_data["default_footer_left"]
    st.session_state.footer_right = lang_data["default_footer_right"]
    st.session_state.yellow_words = lang_data["default_yellow"]

    st.rerun()


# -----------------------------------------------------------
# ★★★ 言語が確定した「あと」で翻訳辞書を読み込む ★★★
# -----------------------------------------------------------
T = load_lang(st.session_state.lang)


# =========================================================
# タイトル
# =========================================================
#st.title("大判焼外交部ジェネレーター ver2.4 (軽量版)")
st.title(T["title"])


# =========================================================
# 注意事項
# =========================================================
st.markdown("### " + T["notice_title"])
st.markdown(T["notice_body"])

# -----------------------------------------------------------
# 注意事項 同意チェック
# -----------------------------------------------------------
agreed = st.checkbox(T["agree_label"])

if not agreed:
    st.warning(T["agree_warning"])

# =========================================================
# NGワード読み込み ~ 画像生成全て
# =========================================================
if agreed:

    # =========================================================
    # NGワード読み込み
    # =========================================================
    NG_FILE = ".streamlit/ng_words.txt"
    if os.path.exists(NG_FILE):
        with open(NG_FILE, "r", encoding="utf-8") as f:
            NG_WORDS = [w.strip() for w in f if w.strip()]
    else:
        NG_WORDS = []

    # =========================================================
    # 背景画像
    # =========================================================
    BACKGROUND_CHOICES = {
        "01": ".streamlit/background01.png",
        "02": ".streamlit/background02.png",
        "03": ".streamlit/background03.png",
        "04": ".streamlit/background04.png",
        "05": ".streamlit/background05.png",
        "06": ".streamlit/background06.png",
        "07": ".streamlit/background07.png",
    }
    BG_LABELS = list(BACKGROUND_CHOICES.keys())

    bg_choice = st.selectbox(
        T["background_select"],
        BG_LABELS,
        index=BG_LABELS.index(ss.bg_choice) if "bg_choice" in ss else 0
    )
    ss.bg_choice = bg_choice

    with open(BACKGROUND_CHOICES[bg_choice], "rb") as f:
        bg_b64_raw = f.read()
        bg_b64 = base64.b64encode(bg_b64_raw).decode()

    bg_b64_safe = html.escape(bg_b64)

    # =========================================================
    # 入力欄（本文 / フッター）
    # =========================================================
    ss.main_text = st.text_area(T["main_text"], ss.main_text if "main_text" in ss else "", height=250)
    ss.footer_left = st.text_input(T["footer_left"], ss.footer_left if "footer_left" in ss else "")
    ss.footer_right = st.text_input(T["footer_right"], ss.footer_right if "footer_right" in ss else "")

    # =========================================================
    # 黄色単語
    # =========================================================
    if mode_internal == "NORMAL":
        ss.yellow_words = st.text_area(T["yellow_words"], ss.yellow_words if "yellow_words" in ss else "")
    else:
        ss.yellow_words = ""

    # =========================================================
    # Apply / Reset
    # =========================================================
    col_apply, col_reset = st.columns(2)

    with col_apply:
        if st.button(T["apply"]):
            st.rerun()

    with col_reset:
        if st.button(T["reset"]):
            keep_bg = ss.bg_choice
            keep_font = ss.font_choice if "font_choice" in ss else None
            st.session_state.clear()
            st.session_state.bg_choice = keep_bg
            if keep_font:
                st.session_state.font_choice = keep_font
            st.rerun()

    # =========================================================
    # NGチェック
    # =========================================================
    if mode_internal == "NORMAL":
        found = [ng for ng in NG_WORDS if ng and ng in ss.main_text]
        if found:
            st.error("⚠ NG word → " + ", ".join(found))
            st.stop()

    # =========================================================
    # JSデータ生成
    # =========================================================
    main_js = json.dumps(ss.main_text)
    footer_left_js = json.dumps(ss.footer_left)
    footer_right_js = json.dumps(ss.footer_right)
    yellow_js = "|".join([w.strip() for w in ss.yellow_words.split("\n") if w.strip()])
    mode_js = json.dumps(mode_internal)

    # =========================================================
    # ★巨大 JSテンプレート（キャンバス本体）
    # =========================================================
    html_template = """
<style>
@font-face {
    font-family: "customFont";
    src: url("data:font/ttf;base64,{{FONTDATA}}") format("truetype");
}
body { margin: 0; padding: 0; }
</style>

<div style="display:flex;flex-direction:column;align-items:center;gap:16px;">

  <button id="saveBtn" style="
      padding:12px 24px;border-radius:999px;border:none;
      background:#4CAF50;color:white;font-weight:700;
      cursor:pointer;font-size:14px;">
    {{SAVE}}
  </button>

  <button id="tweetBtn" style="
      padding:12px 24px;border-radius:999px;border:none;
      background:#1DA1F2;color:white;font-weight:700;
      cursor:pointer;font-size:14px;">
    {{TWEET}}
  </button>

  <canvas id="posterCanvas" style="
      max-width:100%;border-radius:16px;
      box-shadow:0 10px 30px rgba(0,0,0,0.6);"></canvas>
</div>

<script>
const bgData      = "{{BGDATA}}";
const textRaw     = {{MAIN}};
const footerLeft  = {{LEFT}};
const footerRight = {{RIGHT}};
const yellowWords = "{{YELLOW}}".split("|").filter(x=>x.length>0);
const mode        = {{MODE}};
</script>
"""

    # =========================================================
    # SAVE / TWEET / TWEET_TEXT の多言語置換
    # =========================================================
    html_template = html_template.replace("{{SAVE}}", T["save"])
    html_template = html_template.replace("{{TWEET}}", T["tweet"])
    tweet_template_js = json.dumps(T["tweet_template"])
    html_template = html_template.replace("{{TWEET_TEXT}}", tweet_template_js)

    # =========================================================
    # ★最終 HTML 生成
    # =========================================================
    html_final = (
        html_template
            .replace("{{MAIN}}", main_js)
            .replace("{{LEFT}}", footer_left_js)
            .replace("{{RIGHT}}", footer_right_js)
            .replace("{{YELLOW}}", yellow_js)
            .replace("{{FONTDATA}}", font_b64)
            .replace("{{BGDATA}}", bg_b64_safe)
            .replace("{{MODE}}", mode_js)
    )

    st_html(html_final, height=1050, scrolling=True)


