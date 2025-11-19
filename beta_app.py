import streamlit as st
import base64
import html
import os
import json
from streamlit.components.v1 import html as st_html

st.set_page_config(page_title="大判焼外交部ジェネレーター ver2.3", layout="centered")

# =========================================================
# タイトル
# =========================================================
st.title("大判焼外交部ジェネレーター ver2.3（通常 / ASCIIアート切替版）")

# =========================================================
# 注意事項
# =========================================================
st.markdown("""
### ⚠️ 注意事項・禁止事項

当アプリは **娯楽目的のパロディ画像生成ツール** です。

#### 【禁止事項】
- 差別・侮辱・民族憎悪を助長する表現  
- 特定個人・団体の誹謗中傷  
- 名誉毀損・プライバシー侵害  
- 公序良俗に反する内容  
- 法令違反につながる利用  

#### 【免責事項】
- 生成物によるトラブルに **当方は一切責任を負いません。**
- SNS等への投稿・転載は **利用者の自己責任** でお願いします。

---
""")

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
    "背景 01": ".streamlit/background01.png",
    "背景 02": ".streamlit/background02.png",
    "背景 03": ".streamlit/background03.png",
    "背景 04": ".streamlit/background04.png",
}

# =========================================================
# フォント
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

# =========================================================
# モード選択
# =========================================================
mode = st.radio("モード選択", ["通常モード", "ASCIIアートモード"])

# =========================================================
# フォント選択（通常モードのみ）
# =========================================================
if mode == "通常モード":
    if "font_choice" in ss and ss.font_choice in FONT_LABEL_LIST:
        default_idx = FONT_LABEL_LIST.index(ss.font_choice)
    else:
        default_idx = 0

    selected_label = st.selectbox(
        "フォントを選択（通常モードのみ）",
        FONT_LABEL_LIST, index=default_idx
    )
    ss.font_choice = selected_label
    font_filename = FONT_MAP[selected_label]

    with open(os.path.join(FONT_DIR, font_filename), "rb") as f:
        font_b64 = base64.b64encode(f.read()).decode()
else:
    aa_path = os.path.join(FONT_DIR, AA_FONT_FILE)
    if not os.path.exists(aa_path):
        st.error(f"フォント {AA_FONT_FILE} がありません。fonts/ に置いてください。")
        st.stop()
    with open(aa_path, "rb") as f:
        font_b64 = base64.b64encode(f.read()).decode()

# =========================================================
# 初期値
# =========================================================
DEFAULT_MAIN = """“われわれは
回転焼派に告げる
大判焼問題で
火遊びをするな
火遊びをすれば
今川焼と同盟を組む”"""

DEFAULT_LEFT = "大判焼外交部報道官"
DEFAULT_RIGHT = "2015年11月15日"
DEFAULT_YELLOW = "火遊び"

# =========================================================
# session_state
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
    ss.bg_choice = "背景 01"

# =========================================================
# 背景選択
# =========================================================
bg_choice = st.selectbox(
    "背景画像を選択",
    list(BACKGROUND_CHOICES.keys()),
    index=list(BACKGROUND_CHOICES.keys()).index(ss.bg_choice)
)
ss.bg_choice = bg_choice

with open(BACKGROUND_CHOICES[bg_choice], "rb") as f:
    bg_data = base64.b64encode(f.read()).decode()
bg_safe = html.escape(bg_data)

# =========================================================
# 入力欄
# =========================================================
ss.main_text = st.text_area("本文", ss.main_text, height=250)
ss.footer_left = st.text_input("下部（左）", ss.footer_left)
ss.footer_right = st.text_input("下部（右）", ss.footer_right)

if mode == "通常モード":
    ss.yellow_words = st.text_area("黄色単語（改行区切り）", ss.yellow_words)
else:
    ss.yellow_words = ""


# =========================================================
# Apply / Reset
# =========================================================
col1, col2 = st.columns(2)
with col1:
    if st.button("反映する"):
        st.rerun()

with col2:
    if st.button("初期テキストに戻す"):
        keep_bg = ss.bg_choice
        keep_font = ss.font_choice if "font_choice" in ss else None
        st.session_state.clear()
        ss.bg_choice = keep_bg
        if keep_font:
            ss.font_choice = keep_font
        st.rerun()

# =========================================================
# NGワードチェック
# =========================================================
if mode == "通常モード":
    found = [ng for ng in NG_WORDS if ng in ss.main_text]
    if found:
        st.error("NGワードが含まれています: " + ", ".join(found))
        st.stop()

# =========================================================
# JSに渡すテキスト（JSON）
# =========================================================
main_js = json.dumps(ss.main_text)
left_js = json.dumps(ss.footer_left)
right_js = json.dumps(ss.footer_right)
mode_js = json.dumps("AA" if mode == "ASCIIアートモード" else "NORMAL")

yellow_js = "|".join([w.strip() for w in ss.yellow_words.split("\n") if w.strip()])


# =========================================================
# HTML + JS（黄色対応・AA対応の修復版）
# =========================================================
#
# ★ 通常：drawColoredLine() で黄色ハイライト
# ★ AA：左寄せ・単色
# ★ フォントサイズ探索は marginTop/marginBottom を厳守
#
html_template = """
<style>
@font-face {
    font-family: "customFont";
    src: url("data:font/ttf;base64,{{FONT}}") format("truetype");
}
</style>

<div style="display:flex;flex-direction:column;align-items:center;">
  <button id="saveBtn">画像を保存（JPEG）</button>
  <button id="tweetBtn">Xに投稿する（画像は貼ってね）</button>
  <canvas id="posterCanvas" style="max-width:100%;border-radius:12px;"></canvas>
</div>

<script>
const bgData      = "{{BG}}";
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


img.onload = async () => {
    await document.fonts.load("30px customFont");
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

    const areaW = W - marginX*2;
    const areaH = H - marginTop - marginBottom;

    // ========== 黄色対応の描画関数 ==========
    function drawColoredLine(line, centerX, y) {
        ctx.font = fontSize + "px customFont";

        let segs = [];
        let pos = 0;
        while (pos < line.length) {
            let found = false;
            for (const w of yellowWords) {
                if (w && line.startsWith(w, pos)) {
                    segs.push({text:w, yellow:true});
                    pos += w.length;
                    found = true;
                    break;
                }
            }
            if (!found) {
                segs.push({text:line[pos], yellow:false});
                pos++;
            }
        }

        let totalW = 0;
        for (const s of segs) {
            totalW += ctx.measureText(s.text).width;
        }

        let x = centerX - totalW/2;

        for (const s of segs) {
            ctx.fillStyle = s.yellow ? "#FFD700" : "white";
            ctx.fillText(s.text, x, y);
            x += ctx.measureText(s.text).width;
        }
    }

    // ========== フォントサイズ探索 ==========
    function canFit(size) {
        ctx.font = size + "px customFont";

        let maxWidth = 0;
        for (const line of lines) {
            const w = ctx.measureText(line).width;
            if (w > maxWidth) maxWidth = w;
        }

        const totalH = lines.length * size * LINE_GAP;
        return maxWidth <= areaW && totalH <= areaH;
    }

    let low = FONT_MIN;
    let high = FONT_MAX;
    let best = FONT_MIN;

    while (low <= high) {
        const mid = Math.floor((low + high)/2);
        if (canFit(mid)) {
            best = mid;
            low = mid + 1;
        } else {
            high = mid - 1;
        }
    }

    let fontSize = best;

    // ========== Y開始位置（中央寄せ） ==========
    const totalH = lines.length * fontSize * LINE_GAP;
    let currentY = marginTop + (areaH - totalH)/2 + fontSize*0.5;

    // ========== 各行描画（通常：黄色 / AA：左寄せ） ==========
    for (const line of lines) {

        if (mode === "AA") {
            ctx.textAlign = "left";
            ctx.fillStyle = "white";
            ctx.fillText(line, marginX, currentY);

        } else {
            ctx.textAlign = "center";
            drawColoredLine(line, W/2, currentY);
        }

        currentY += fontSize * LINE_GAP;
    }

    // ========== フッター ==========
    const footerY = H * 0.90;
    const footerFont = Math.max(22, Math.floor(H * 0.035));

    ctx.font = footerFont + "px customFont";
    ctx.textAlign = "left";
    ctx.fillStyle = "white";
    ctx.fillText(footerLeft, W*0.06, footerY);

    ctx.textAlign = "right";
    ctx.fillText(footerRight, W*0.94, footerY);
}


document.getElementById("saveBtn").onclick = function() {
    canvas.toBlob((blob)=> {
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "generated.jpg";
        document.body.appendChild(a);
        a.click();
        setTimeout(()=>{URL.revokeObjectURL(url); a.remove();}, 400);
    }, "image/jpeg", 0.90);
};

document.getElementById("tweetBtn").onclick = function() {
    const text = encodeURIComponent(
        "この画像は『大判焼外交部ジェネレーター』で作りました。\\nhttps://ikan-no-i-gen.streamlit.app/"
    );
    window.open("https://twitter.com/intent/tweet?text=" + text, "_blank");
};
</script>
"""


html_final = (
    html_template
        .replace("{{MAIN}}", main_js)
        .replace("{{LEFT}}", left_js)
        .replace("{{RIGHT}}", right_js)
        .replace("{{YELLOW}}", yellow_js)
        .replace("{{FONT}}", font_b64)
        .replace("{{BG}}", bg_safe)
        .replace("{{MODE}}", mode_js)
)

st_html(html_final, height=1100, scrolling=True)

