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
# フォント選択（通常モード）
# =========================================================
if mode == "通常モード":
    if "font_choice" in ss and ss.font_choice in FONT_LABEL_LIST:
        default_font_idx = FONT_LABEL_LIST.index(ss.font_choice)
    else:
        default_font_idx = 0

    selected_label = st.selectbox(
        "フォントを選択（通常モードのみ）",
        FONT_LABEL_LIST, index=default_font_idx
    )
    ss.font_choice = selected_label
    font_filename = FONT_MAP[selected_label]

    with open(os.path.join(FONT_DIR, font_filename), "rb") as f:
        font_b64 = base64.b64encode(f.read()).decode()

else:
    aa_path = os.path.join(FONT_DIR, AA_FONT_FILE)
    if not os.path.exists(aa_path):
        st.error("フォントが不足しています： ms-pgothic-regular.ttf")
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

# セッション初期化
for key, value in {
    "main_text": DEFAULT_MAIN,
    "footer_left": DEFAULT_LEFT,
    "footer_right": DEFAULT_RIGHT,
    "yellow_words": DEFAULT_YELLOW,
    "bg_choice": "背景 01",
}.items():
    ss.setdefault(key, value)

# =========================================================
# 背景選択
# =========================================================
bg_choice = st.selectbox("背景画像を選択", list(BACKGROUND_CHOICES.keys()))
ss.bg_choice = bg_choice

with open(BACKGROUND_CHOICES[bg_choice], "rb") as f:
    bg_b64 = base64.b64encode(f.read()).decode()

bg_b64_safe = html.escape(bg_b64)

# =========================================================
# 入力欄
# =========================================================
ss.main_text = st.text_area("本文", ss.main_text, height=230)
ss.footer_left = st.text_input("下部（左）", ss.footer_left)
ss.footer_right = st.text_input("下部（右）", ss.footer_right)

if mode == "通常モード":
    ss.yellow_words = st.text_area("黄色単語（改行区切り）", ss.yellow_words)
else:
    ss.yellow_words = ""

# =========================================================
# リセット
# =========================================================
if st.button("初期値に戻す"):
    keep_bg = ss.bg_choice
    keep_font = ss.font_choice if "font_choice" in ss else None
    st.session_state.clear()
    st.session_state.bg_choice = keep_bg
    if keep_font:
        st.session_state.font_choice = keep_font
    st.rerun()

# =========================================================
# NGワードチェック
# =========================================================
if mode == "通常モード":
    found = [ng for ng in NG_WORDS if ng in ss.main_text]
    if found:
        st.error("⚠ NGワード検出 → " + ", ".join(found))
        st.stop()

# =========================================================
# JS 用データ
# =========================================================
main_js = json.dumps(ss.main_text)
footer_left_js = json.dumps(ss.footer_left)
footer_right_js = json.dumps(ss.footer_right)
yellow_js = "|".join([w.strip() for w in ss.yellow_words.split("\n") if w.strip()])
mode_js = json.dumps("AA" if mode == "ASCIIアートモード" else "NORMAL")

# =========================================================
# HTML + JS（完全版）
# =========================================================
html_final = f"""
<style>
@font-face {{
    font-family: "customFont";
    src: url("data:font/ttf;base64,{font_b64}") format("truetype");
}}
</style>

<canvas id="posterCanvas" style="max-width:100%;border-radius:12px;box-shadow:0 0 20px rgba(0,0,0,0.5);"></canvas><br>

<button id="saveBtn" style="
    padding:12px 22px;border-radius:999px;border:none;
    background:#4CAF50;color:white;font-weight:700;cursor:pointer;margin-right:10px;">
    保存（JPEG）
</button>

<button id="tweetBtn" style="
    padding:12px 22px;border-radius:999px;border:none;
    background:#1DA1F2;color:white;font-weight:700;cursor:pointer;">
    Xに投稿（画像は自分で貼る）
</button>

<script>
const bgData = "{bg_b64_safe}";
const textRaw = {main_js};
const footerLeft = {footer_left_js};
const footerRight = {footer_right_js};
const yellowWords = "{yellow_js}".split("|").filter(x=>x.length>0);
const mode = {mode_js};

const MAX_WIDTH = 1300;
const FONT_MAX = 400;
const FONT_MIN = 24;
let LINE_GAP = (mode === "AA") ? 1.05 : 1.30;

const img = new Image();
img.src = "data:image/png;base64," + bgData;

const canvas = document.getElementById("posterCanvas");
const ctx = canvas.getContext("2d");

img.onload = async function() {{
    await document.fonts.load("30px customFont");
    drawPoster();
}};

function drawPoster() {{
    const lines = textRaw.split("\\n");

    const origW = img.naturalWidth;
    const origH = img.naturalHeight;

    let scale = (origW > MAX_WIDTH) ? MAX_WIDTH / origW : 1;
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

    function canFit(fs_raw) {{
        const fs = (mode === "AA") ? fs_raw * 0.95 : fs_raw;
        ctx.font = fs + "px customFont";

        let maxWidth = 0;
        for (const line of lines) {{
            maxWidth = Math.max(maxWidth, ctx.measureText(line).width);
        }}

        const totalH = lines.length * fs * LINE_GAP;

        return (maxWidth <= areaW) && (totalH <= areaH);
    }}

    let low = FONT_MIN, high = FONT_MAX, best = FONT_MIN;

    while (low <= high) {{
        let mid = Math.floor((low + high) / 2);
        if (canFit(mid)) {{
            best = mid;
            low = mid + 1;
        }} else {{
            high = mid - 1;
        }}
    }}

    const fontSize = best;
    ctx.font = fontSize + "px customFont";
    ctx.textBaseline = "middle";

    const totalTextHeight = lines.length * fontSize * LINE_GAP;
    let y = marginTop + (areaH - totalTextHeight) / 2 + fontSize * 0.5;

    function drawLine(line, cx, y) {{
        if (mode === "AA") {{
            ctx.fillStyle = "white";
            ctx.textAlign = "left";
            ctx.fillText(line, marginX, y);
            return;
        }}

        let segs = [];
        let pos = 0;
        while (pos < line.length) {{
            let matched = false;
            for (const w of yellowWords) {{
                if (w && line.startsWith(w, pos)) {{
                    segs.push({{text:w, yellow:true}});
                    pos += w.length;
                    matched = true;
                    break;
                }}
            }}
            if (!matched) {{
                segs.push({{text:line[pos], yellow:false}});
                pos++;
            }}
        }}

        let width = segs.reduce((s,g)=>s + ctx.measureText(g.text).width, 0);
        let x = cx - width / 2;

        for (const s of segs) {{
            ctx.fillStyle = s.yellow ? "#FFD700" : "white";
            ctx.fillText(s.text, x, y);
            x += ctx.measureText(s.text).width;
        }}
    }}

    for (const line of lines) {{
        drawLine(line, W * 0.5, y);
        y += fontSize * LINE_GAP;
    }}

    const footerY = H * 0.90;
    const footerSize = Math.max(22, Math.floor(H * 0.035));
    ctx.font = footerSize + "px customFont";

    ctx.fillStyle = "white";
    ctx.textAlign = "left";
    ctx.fillText(footerLeft, W * 0.06, footerY);

    ctx.textAlign = "right";
    ctx.fillText(footerRight, W * 0.94, footerY);
}}

document.getElementById("saveBtn").onclick = function() {{
    canvas.toBlob(function(blob){{
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url; a.download = "generated.jpg";
        document.body.appendChild(a); a.click();
        setTimeout(()=>{{ URL.revokeObjectURL(url); a.remove(); }}, 300);
    }}, "image/jpeg", 0.90);
}};

document.getElementById("tweetBtn").onclick = function() {{
    const text = encodeURIComponent(
        "この画像は『大判焼外交部ジェネレーター』で作りました。\\n" +
        "https://ikan-no-i-gen.streamlit.app/\\n" +
        "※画像は自動投稿されません。画像は自分で貼ってください。"
    );
    window.open("https://twitter.com/intent/tweet?text=" + text, "_blank");
}};
</script>
"""

st_html(html_final, height=1100, scrolling=True)
