import streamlit as st
import base64
import html
import os
from streamlit.components.v1 import html as st_html

st.set_page_config(page_title="大判焼外交部ジェネレーター ver.2.0", layout="centered")

# =========================================================
# タイトル
# =========================================================
st.title("大判焼外交部ジェネレーター ver.2.0")

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
- 投稿・転載等は **利用者の自己責任** でお願いします。

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
FONT_MAP = {label: fname for fname, label in FONT_LABELS.items()}

selected_label = st.selectbox("フォントを選択", list(FONT_LABELS.values()))
font_filename = FONT_MAP[selected_label]

with open(os.path.join(FONT_DIR, font_filename), "rb") as f:
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
ss = st.session_state
if "main_text" not in ss: ss.main_text = DEFAULT_MAIN
if "footer_left" not in ss: ss.footer_left = DEFAULT_LEFT
if "footer_right" not in ss: ss.footer_right = DEFAULT_RIGHT
if "yellow_words" not in ss: ss.yellow_words = DEFAULT_YELLOW
if "bg_choice" not in ss: ss.bg_choice = "背景 01"

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
    bg_b64_raw = f.read()
    bg_b64 = base64.b64encode(bg_b64_raw).decode()

# HTML embed は JS 文字列で壊れるため HTML エスケープする（重要）
bg_b64_safe = html.escape(bg_b64)

# =========================================================
# 入力欄
# =========================================================
ss.main_text  = st.text_area("本文", ss.main_text, height=220)
ss.footer_left  = st.text_input("下部（左）", ss.footer_left)
ss.footer_right = st.text_input("下部（右）", ss.footer_right)
ss.yellow_words = st.text_area("黄色単語（改行区切り）", ss.yellow_words)

# =========================================================
# Apply / Reset
# =========================================================
if st.button("反映する"):
    st.rerun()

if st.button("初期テキストに戻す"):
    keep_bg = ss.bg_choice
    keep_font = selected_label
    st.session_state.clear()
    st.session_state.bg_choice = keep_bg
    st.session_state.font_choice = keep_font
    st.rerun()

# =========================================================
# NGワードチェック
# =========================================================
found = [ng for ng in NG_WORDS if ng in ss.main_text]
if found:
    st.error("⚠ NGワード → " + ", ".join(found))
    st.stop()

# =========================================================
# JS 用データ
# =========================================================
main_js = html.escape(ss.main_text).replace("\n", "\\n")
footer_left_js = html.escape(ss.footer_left)
footer_right_js = html.escape(ss.footer_right)
yellow_js = "|".join([w.strip() for w in ss.yellow_words.split("\n") if w.strip()])

# =========================================================
# HTML + JS（背景画像修正版）
# =========================================================
html_template = """
<style>
@font-face {
    font-family: "customFont";
    src: url("data:font/ttf;base64,{{FONTDATA}}") format("truetype");
}
</style>

<div style="display:flex;flex-direction:column;align-items:center;gap:16px;">

  <button id="saveBtn" style="
      padding:12px 24px;
      border-radius:999px;
      border:none;
      background:#4CAF50;
      color:white;
      font-weight:700;
      cursor:pointer;">
    画像を保存（JPEG）
  </button>

  <button id="tweetBtn" style="
      padding:12px 24px;
      border-radius:999px;
      border:none;
      background:#1DA1F2;
      color:white;
      font-weight:700;
      cursor:pointer;">
    𝕏に投稿する（画像は貼ってね）
  </button>

  <canvas id="posterCanvas" style="
      max-width:100%;
      border-radius:16px;
      box-shadow:0 10px 30px rgba(0,0,0,0.6);"></canvas>
</div>

<script>
// ===== Python → JS で安全受け取り =====
const bgData = "{{BGDATA}}";  // ← ここが重要（壊れない）
// ======================================

const textRaw    = "{{MAIN}}".replace(/\\\\n/g,"\\n");
const footerLeft = "{{LEFT}}";
const footerRight = "{{RIGHT}}";
const yellowWords = "{{YELLOW}}".split("|").filter(x=>x.length>0);

const img = new Image();
img.src = "data:image/png;base64," + bgData;  // ← JS 内で連結（安全）

const canvas = document.getElementById("posterCanvas");
const ctx = canvas.getContext("2d");

img.onload = async function() {
    await document.fonts.load("30px customFont");
    drawPoster();
};

function drawPoster() {

    const W = img.naturalWidth;
    const H = img.naturalHeight;
    canvas.width = W;
    canvas.height = H;

    ctx.drawImage(img, 0, 0, W, H);

    const VW = 7000, VH = 9000;
    const S = Math.min(W / VW, H / VH);

    const virtualTop = 2500;
    const virtualBottom = 6500;
    const areaW = VW * 0.9;
    const areaH = virtualBottom - virtualTop;

    const lines = textRaw.split("\\n");
    const lineGap = 1.3;
    let fontSize = 400;

    function maxWidth(fs) {
        ctx.font = `${fs*S}px customFont`;
        let m=0;
        for(const l of lines){
            m = Math.max(m, ctx.measureText(l).width);
        }
        return m/S;
    }

    function totalHeight(fs){
        return lines.length * fs * lineGap;
    }

    while(fontSize >= 80){
        if(maxWidth(fontSize) <= areaW && totalHeight(fontSize) <= areaH) break;
        fontSize -= 20;
    }

    function drawColoredLine(line, vx, vy) {
        ctx.font = `${fontSize*S}px customFont`;
        const xCenter = vx*S;
        const y = vy*S;

        let segs=[], pos=0;
        while(pos < line.length){
            let matched=false;
            for(const w of yellowWords){
                if(w && line.startsWith(w,pos)){
                    segs.push({text:w,yellow:true});
                    pos+=w.length;
                    matched=true;
                    break;
                }
            }
            if(!matched){
                segs.push({text:line[pos],yellow:false});
                pos++;
            }
        }

        let totalW=0;
        for(const seg of segs){
            totalW+=ctx.measureText(seg.text).width;
        }

        let cursor=xCenter-totalW/2;
        for(const seg of segs){
            ctx.fillStyle = seg.yellow ? "#FFD700" : "white";
            ctx.textBaseline = "middle";
            ctx.fillText(seg.text, cursor, y);
            cursor+=ctx.measureText(seg.text).width;
        }
    }

    let tH = totalHeight(fontSize);
    let yStart = virtualTop + (areaH - tH) / 2;

    for(const line of lines){
        drawColoredLine(line, VW*0.5, yStart);
        yStart += fontSize*lineGap;
    }

    const footerY = 8200;
    ctx.fillStyle="white";
    ctx.textBaseline="middle";
    ctx.font = `${280*S}px customFont`;

    ctx.textAlign="left";
    ctx.fillText(footerLeft, (VW*0.05)*S, footerY*S);

    ctx.textAlign="right";
    ctx.fillText(footerRight, (VW*0.95)*S, footerY*S);
}

document.getElementById("saveBtn").onclick = function(){
    canvas.toBlob(function(blob){
        const url=URL.createObjectURL(blob);
        const a=document.createElement("a");
        a.href=url;
        a.download="generated.jpg";
        document.body.appendChild(a);
        a.click();
        setTimeout(()=>{URL.revokeObjectURL(url);a.remove();},400);
    }, "image/jpeg", 0.88);
};

document.getElementById("tweetBtn").onclick=function(){
    const text=encodeURIComponent(
        "この画像は『大判焼外交部ジェネレーター』で作りました。\\nhttps://ikan-no-i-gen.streamlit.app/\\n※画像は自動投稿されません。自分で貼ってください。"
    );
    window.open("https://twitter.com/intent/tweet?text="+text,"_blank");
};
</script>
"""

# 出力
html_final = (
    html_template
    .replace("{{MAIN}}", main_js)
    .replace("{{LEFT}}", footer_left_js)
    .replace("{{RIGHT}}", footer_right_js)
    .replace("{{YELLOW}}", yellow_js)
    .replace("{{FONTDATA}}", font_b64)
    .replace("{{BGDATA}}", bg_b64_safe)     # ← ここが重要
)

st_html(html_final, height=1050, scrolling=True)

