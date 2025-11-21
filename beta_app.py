import streamlit as st
import base64
import html
import os
import json
from streamlit.components.v1 import html as st_html

st.set_page_config(page_title="大判焼外交部ジェネレーター ver2.4", layout="centered")

# -----------------------------------------------------------
# ★ 一時的に session_state を全クリアして古い値を削除する ★
# -----------------------------------------------------------
st.session_state.clear()


# -----------------------------------------------------------
# 言語選択（国旗アイコンボタン版）
# -----------------------------------------------------------

# 表示名 → 内部言語コード のマッピング
LANG_OPTIONS = {
    "🇯🇵 日本語": "ja",
    "🇺🇸 English": "en",
    # 今後追加する場合はここに書くだけ：
    # "🇹🇼 繁體中文": "zh-Hant",
    # "🇨🇳 简体中文": "zh-Hans",
    # "🇰🇷 한국어": "ko",
}

# 初回起動時のデフォルト言語
if "lang" not in st.session_state:
    st.session_state.lang = "ja"

current_lang = st.session_state.lang

# 国旗ボタンUI（押すと即切り替え）
cols = st.columns(len(LANG_OPTIONS))

for i, (disp, code) in enumerate(LANG_OPTIONS.items()):
    if cols[i].button(disp):
        st.session_state.lang = code
        st.rerun()  # 押した瞬間に切り替え



# -----------------------------------------------------------
# 翻訳JSONを読み込む
# -----------------------------------------------------------
def load_lang(lang_code):
    with open(f"languages/{lang_code}.json", "r", encoding="utf-8") as f:
        return json.load(f)

T = load_lang(st.session_state.lang)   # ← 翻訳辞書


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

# 表示ラベルも数字のみ
BG_LABELS = list(BACKGROUND_CHOICES.keys())

# =========================================================
# フォント
# =========================================================
FONT_DIR = "fonts"
FONT_LABELS = {
    "BIZUDMincho-Regular.ttf": "01. 明朝",
    "UnGungseo.ttf": "02. KOREA FONT",
}
# ASCIIアートモード用フォント（ms PGothic 風）
AA_FONT_FILE = "ms-pgothic-regular.ttf"

FONT_MAP = {label: fname for fname, label in FONT_LABELS.items()}
FONT_LABEL_LIST = list(FONT_LABELS.values())

ss = st.session_state

# -----------------------------------------------------------
# モード選択（多言語対応：内部値を固定化）
# -----------------------------------------------------------

MODE_OPTIONS = {
    T["normal_mode"]: "NORMAL",
    T["aa_mode"]: "AA",
}

mode_display = st.radio(
    T["mode_select"],
    options=list(MODE_OPTIONS.keys()),
    horizontal=True
)

mode_internal = MODE_OPTIONS[mode_display]


# -----------------------------------------------------------
# アスキーアート参照リンク
# ----------------------------------------------------------
# ASCIIアート参考リンクを表示
st.markdown(T["ascii_links"])

# =========================================================
# フォント選択（NORMALのみ）
# =========================================================
if mode_internal == "NORMAL":
    if "font_choice" in ss and ss.font_choice in FONT_LABEL_LIST:
        default_font_idx = FONT_LABEL_LIST.index(ss.font_choice)
    else:
        default_font_idx = 0

    selected_label = st.selectbox(
        T["font_select"],
        FONT_LABEL_LIST,
        index=default_font_idx
    )
    ss.font_choice = selected_label
    font_filename = FONT_MAP[selected_label]

    with open(os.path.join(FONT_DIR, font_filename), "rb") as f:
        font_b64 = base64.b64encode(f.read()).decode()
else:
    # ASCIIアートモード：ms PGothic
    aa_path = os.path.join(FONT_DIR, AA_FONT_FILE)
    if not os.path.exists(aa_path):
        st.error(f"フォント {AA_FONT_FILE} が見つかりません。fonts/ に配置してください。")
        st.stop()

    with open(aa_path, "rb") as f:
        font_b64 = base64.b64encode(f.read()).decode()

# =========================================================
# 初期値
# =========================================================
DEFAULT_MAIN = T["default_main"]
DEFAULT_LEFT = T["default_footer_left"]
DEFAULT_RIGHT = T["default_footer_right"]
DEFAULT_YELLOW = T["default_yellow"]

# =========================================================
# session_state 初期化
# =========================================================
if "main_text" not in ss:
    ss.main_text = DEFAULT_MAIN
if "footer_left" not in ss:
    ss.footer_left = DEFAULT_LEFT
if "footer_right" not in ss:
    ss.footer_right = DEFAULT_RIGHT
if "yellow_words" not in ss:
    ss.yellow_words = DEFAULT_YELLOW
if "bg_choice" not in ss:
    ss.bg_choice = "01"

# =========================================================
# 背景選択
# =========================================================
bg_choice = st.selectbox(
    T["background_select"],
    BG_LABELS,
    index=BG_LABELS.index(ss.bg_choice)
)
ss.bg_choice = bg_choice

with open(BACKGROUND_CHOICES[bg_choice], "rb") as f:
    bg_b64_raw = f.read()
    bg_b64 = base64.b64encode(bg_b64_raw).decode()

bg_b64_safe = html.escape(bg_b64)

# =========================================================
# 入力欄
# =========================================================
#ss.main_text = st.text_area("本文", ss.main_text, height=250)
ss.main_text = st.text_area(T["main_text"], ss.main_text, height=250)

#ss.footer_left = st.text_input("下部（左）", ss.footer_left)
#ss.footer_right = st.text_input("下部（右）", ss.footer_right)
ss.footer_left = st.text_input(T["footer_left"], ss.footer_left)
ss.footer_right = st.text_input(T["footer_right"], ss.footer_right)


if mode_internal == "NORMAL":
    ss.yellow_words = st.text_area(T["yellow_words"], ss.yellow_words)
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
# NGワードチェック（NORMALのみ）
# =========================================================
if mode_internal == "NORMAL":
    found = [ng for ng in NG_WORDS if ng and ng in ss.main_text]
    if found:
        st.error("⚠ NG word → " + ", ".join(found))
        st.stop()


# =========================================================
# JS用データ生成（JSON経由で安全に渡す）
# =========================================================
# どちらのモードでも JSON 文字列として JS に渡す
main_js = json.dumps(ss.main_text)
footer_left_js = json.dumps(ss.footer_left)
footer_right_js = json.dumps(ss.footer_right)
mode_js = json.dumps(mode_internal)


yellow_js = "|".join([w.strip() for w in ss.yellow_words.split("\n") if w.strip()])

# =========================================================
# HTML + JS（全部入り）
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
const textRaw     = {{MAIN}};        // JSON 文字列 → JS 文字列
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

    // === バイナリサーチ: 物理的に収まる最大フォント ===
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
        if (canFit(mid)) {
            best = mid;
            low = mid + 1;
        } else {
            high = mid - 1;
        }
    }

    let fontSize = best;

    // === モード別 補正（ver2.3.1：ASCIIアートをより確実に縮小） ===
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
        for (const seg of segs) {
            totalW += ctx.measureText(seg.text).width;
        }

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
};   <!-- ★ここだけ修正：drawPoster を明示的に終了 -->

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

html_template = html_template.replace("{{SAVE}}", T["save"])
html_template = html_template.replace("{{TWEET}}", T["tweet"])
tweet_template_js = json.dumps(T["tweet_template"])
html_template = html_template.replace("{{TWEET_TEXT}}", tweet_template_js)


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






















