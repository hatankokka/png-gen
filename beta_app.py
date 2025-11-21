import streamlit as st
import base64
import html
import os
import json
from streamlit.components.v1 import html as st_html

# =========================================================
# フォント定義
# =========================================================
FONT_DIR = "fonts"

FONT_LABELS = {
    "BIZUDMincho-Regular.ttf": "01. 明朝",
    "UnGungseo.ttf": "02. KOREA FONT",
}

AA_FONT_FILE = "ms-pgothic-regular.ttf"

FONT_MAP = {label: fname for fname, label in FONT_LABELS.items()}
FONT_LABEL_LIST = list(FONT_LABELS.values())


ss = st.session_state
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
# モード選択
# =========================================================
mode_label = st.radio(
    T["mode_select"],
    [T["normal_mode"], T["aa_mode"]]
)

if mode_label == T["normal_mode"]:
    mode_internal = "NORMAL"
else:
    mode_internal = "AA"


# =========================================================
# NGワード読み込み ~ 画像生成全て
# =========================================================
if agreed:
    
    # =========================================================
    # モード別フォント選択
    # =========================================================
    if mode_internal == "NORMAL":
        font_choice_label = st.selectbox("フォント選択", FONT_LABEL_LIST)
        ss.font_choice = FONT_MAP[font_choice_label]
    else:
        ss.font_choice = AA_FONT_FILE

    # =========================================================
    # Base64変換
    # =========================================================
    font_path = os.path.join(FONT_DIR, ss.font_choice)
    with open(font_path, "rb") as f:
        font_b64 = base64.b64encode(f.read()).decode()


    # =========================================================
    # Base64変換
    # =========================================================
    font_path = os.path.join(FONT_DIR, ss.font_choice)
    with open(font_path, "rb") as f:
        font_b64 = base64.b64encode(f.read()).decode()

    
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

const MAX_WIDTH = 1300;
const FONT_MAX = 420;
const FONT_MIN = 40;

let LINE_GAP = (mode === "AA") ? 1.05 : 1.30;

const img = new Image();
img.src = "data:image/png;base64," + bgData;

const canvas = document.getElementById("posterCanvas");
const ctx = canvas.getContext("2d");

img.onload = async function() {
    try { await document.fonts.load("30px customFont"); } catch(e){}
    drawPoster();
};

function drawPoster() {

    const lines = textRaw.split("\\n");

    const origW = img.naturalWidth;
    const origH = img.naturalHeight;

    let scale = (origW > MAX_WIDTH) ? (MAX_WIDTH / origW) : 1.0;
    const W = Math.floor(origW * scale);
    const H = Math.floor(origH * scale);

    canvas.width = W;
    canvas.height = H;

    ctx.drawImage(img, 0, 0, W, H);

    const marginX = W * 0.08;
    const marginTop = H * 0.18;
    const marginBottom = H * 0.20;

    const areaW = W - marginX * 2;
    const areaH = H - marginTop - marginBottom;

    // === バイナリサーチ ===
    function canFit(fontSize) {
        ctx.font = fontSize + "px customFont";

        let maxLineWidth = 0;
        for (const line of lines) {
            const w = ctx.measureText(line).width;
            if (w > maxLineWidth) maxLineWidth = w;
        }
        const totalHeight = lines.length * fontSize * LINE_GAP;
        return (maxLineWidth <= areaW) && (totalHeight <= areaH);
    }

    let low = FONT_MIN, high = FONT_MAX, best = FONT_MIN;
    while (low <= high) {
        const mid = Math.floor((low + high) / 2);
        if (canFit(mid)) { best = mid; low = mid + 1; }
        else { high = mid - 1; }
    }

    let fontSize = best;

    // === モード別補正 ===
    if (mode === "AA") {
        const lineCount = lines.length;
        const maxLen = Math.max(...lines.map(x => x.length), 0);
        const K_line = 1 / (1 + 0.015 * Math.max(lineCount - 3, 0));
        const K_len  = 1 / (1 + 0.015 * Math.max(maxLen - 20, 0));
        fontSize = best * K_line * K_len * 1.50;
    } else {
        const lineCount = lines.length;
        const maxLen = Math.max(...lines.map(x => x.length), 0);
        const K_line = 1 / (1 + 0.010 * Math.max(lineCount - 3, 0));
        const K_len  = 1 / (1 + 0.010 * Math.max(maxLen - 10, 0));
        fontSize = best * K_line * K_len;
    }

    if (fontSize < 10) fontSize = 10;
    ctx.font = fontSize + "px customFont";
    ctx.textBaseline = "middle";

    const totalTextHeight = lines.length * fontSize * LINE_GAP;
    let currentY = marginTop + (areaH - totalTextHeight) / 2 + fontSize * 0.5;

    function drawColoredLine(line, centerX, y) {
        ctx.font = fontSize + "px customFont";

        if (mode === "AA") {
            ctx.fillStyle = "white";
            ctx.textAlign = "left";
            ctx.fillText(line, marginX, y);
            return;
        }

        let segs = [];
        let pos = 0;

        while (pos < line.length) {
            let matched = false;

            for (const w of yellowWords) {
                if (w && line.startsWith(w, pos)) {
                    segs.push({ text: w, yellow: true });
                    pos += w.length;
                    matched = true;
                    break;
                }
            }
            if (!matched) {
                segs.push({ text: line[pos], yellow: false });
                pos++;
            }
        }

        let totalW = 0;
        for (const seg of segs) totalW += ctx.measureText(seg.text).width;

        let cursorX = centerX - totalW / 2;
        for (const seg of segs) {
            ctx.fillStyle = seg.yellow ? "#FFD700" : "white";
            ctx.fillText(seg.text, cursorX, y);
            cursorX += ctx.measureText(seg.text).width;
        }
    }

    for (const line of lines) {
        drawColoredLine(line, W * 0.5, currentY);
        currentY += fontSize * LINE_GAP;
    }

    const footerY = H * 0.90;
    const footerFont = Math.max(22, Math.floor(H * 0.035));
    ctx.font = footerFont + "px customFont";
    ctx.fillStyle = "white";
    ctx.textAlign = "left";
    ctx.fillText(footerLeft, W * 0.06, footerY);
    ctx.textAlign = "right";
    ctx.fillText(footerRight, W * 0.94, footerY);
}

document.getElementById("saveBtn").onclick = function() {
    canvas.toBlob(function(blob){
        if (!blob) return;
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url; a.download = "generated.jpg";
        document.body.appendChild(a); a.click();
        setTimeout(()=>{ URL.revokeObjectURL(url); a.remove(); }, 400);
    }, "image/jpeg", 0.90);
};

document.getElementById("tweetBtn").onclick = function() {
    const text = encodeURIComponent({{TWEET_TEXT}});
    window.open("https://twitter.com/intent/tweet?text=" + text, "_blank");
};
</script>
"""
