import streamlit as st
import base64
import html
import os
from streamlit.components.v1 import html as st_html

st.set_page_config(page_title="大判焼外交部ジェネレーター", layout="centered")

# =========================================================
# タイトル
# =========================================================
st.title("大判焼外交部ジェネレーター（フォント選択版）")

# =========================================================
# ⚠️ 注意事項・禁止事項・免責事項
# =========================================================
st.markdown("""
### ⚠️ 注意事項・禁止事項

当アプリは **娯楽目的のパロディ画像生成ツール** です。

#### 【禁止事項】
- 差別・侮辱・民族憎悪を助長する表現  
- 特定個人・団体への誹謗中傷  
- 名誉毀損・プライバシー侵害  
- 公序良俗に反する内容  
- 法令違反につながる利用  

#### 【免責事項】
- 生成された画像・文言の利用により生じたトラブルに  
  **当方は一切責任を負いません。**
- SNS投稿・転載なども **利用者の自己責任** でお願いします。

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
# 背景
# =========================================================
BACKGROUND_CHOICES = {
    "背景 01": ".streamlit/background01.png",
    "背景 02": ".streamlit/background02.png",
    "背景 03": ".streamlit/background03.png",
    "背景 04": ".streamlit/background04.png",
}

# =========================================================
# フォント自動検出
# =========================================================
FONT_DIR = "fonts"
FONT_LABELS = {
    "BIZUDMincho-Regular.ttf": "01. 明朝",
    "kppuskum.ttf": "02. 国規",
}

FONT_FILES = [f for f in os.listdir(FONT_DIR) if f.lower().endswith(".ttf")]
FONT_OPTIONS = [FONT_LABELS.get(f, f) for f in FONT_FILES]

if "font_choice" not in st.session_state:
    st.session_state.font_choice = FONT_OPTIONS[0]

selected_label = st.selectbox("フォントを選択", FONT_OPTIONS)
st.session_state.font_choice = selected_label

# ラベル → ファイル名変換
font_filename = None
for fname, label in FONT_LABELS.items():
    if label == selected_label:
        font_filename = fname
        break
if font_filename is None:
    font_filename = selected_label

# フォント読込
with open(os.path.join(FONT_DIR, font_filename), "rb") as f:
    font_b64 = base64.b64encode(f.read()).decode("utf-8")

# =========================================================
# 初期値
# =========================================================
DEFAULT_MAIN = """“われわれは
回転焼派に告げる
大判焼問題で
火遊びをするな
火遊びをすれば
必ず身を滅ぼす”"""

DEFAULT_LEFT  = "大判焼外交部報道官"
DEFAULT_RIGHT = "2015年11月15日"
DEFAULT_YELLOW = "火遊び"

# =========================================================
# session_state 初期化
# =========================================================
ss = st.session_state
if "main_text" not in ss:      ss.main_text = DEFAULT_MAIN
if "footer_left" not in ss:    ss.footer_left = DEFAULT_LEFT
if "footer_right" not in ss:   ss.footer_right = DEFAULT_RIGHT
if "yellow_words" not in ss:   ss.yellow_words = DEFAULT_YELLOW
if "bg_choice" not in ss:      ss.bg_choice = "背景 01"

# session_state 安全装置
if ss.bg_choice not in BACKGROUND_CHOICES:
    ss.bg_choice = "背景 01"

# =========================================================
# 背景選択
# =========================================================
bg_name = st.selectbox(
    "背景画像を選択",
    list(BACKGROUND_CHOICES.keys()),
    index=list(BACKGROUND_CHOICES.keys()).index(ss.bg_choice)
)
ss.bg_choice = bg_name

BG_PATH = BACKGROUND_CHOICES[bg_name]
with open(BG_PATH, "rb") as f:
    bg_b64 = base64.b64encode(f.read()).decode("utf-8")

# =========================================================
# 入力欄
# =========================================================
main_text_input = st.text_area("本文", ss.main_text, height=220)
footer_left_input  = st.text_input("下部ヘッダー（左）", ss.footer_left)
footer_right_input = st.text_input("下部ヘッダー（右）", ss.footer_right)
yellow_words_input = st.text_area("黄色にしたい単語（改行区切り）", ss.yellow_words)

if st.button("反映する"):
    ss.main_text = main_text_input
    ss.footer_left = footer_left_input
    ss.footer_right = footer_right_input
    ss.yellow_words = yellow_words_input
    st.rerun()

if st.button("初期テキストに戻す"):
    keep_bg = ss.bg_choice
    keep_font = ss.font_choice
    ss.clear()
    ss.bg_choice = keep_bg
    ss.font_choice = keep_font
    st.rerun()

# =========================================================
# NGチェック
# =========================================================
found = [ng for ng in NG_WORDS if ng in ss.main_text]
if found:
    st.error("⚠ NGワード → " + ", ".join(found))
    st.stop()

# =========================================================
# JSへ渡す値
# =========================================================
main_js        = html.escape(ss.main_text).replace("\n", "\\n")
footer_left_js = html.escape(ss.footer_left)
footer_right_js = html.escape(ss.footer_right)
yellow_js      = "|".join([w.strip() for w in ss.yellow_words.split("\n") if w.strip()])

# =========================================================
# HTMLテンプレ（f-string 不使用 → 波括弧OK）
# =========================================================
html_template = """
<style>
@font-face {
    font-family: "customFont";
    src: url("data:font/ttf;base64,{{FONTDATA}}") format("truetype");
}
</style>

<div style="display:flex;flex-direction:column;align-items:center;gap:16px;">
  <button id="saveBtn"
    style="padding:12px 24px;border-radius:999px;border:none;background:#4CAF50;color:white;font-weight:700;cursor:pointer;">
    画像を保存（JPEG）
  </button>
  <canvas id="posterCanvas"
    style="max-width:100%;border-radius:16px;box-shadow:0 10px 30px rgba(0,0,0,0.6);"></canvas>
</div>

<script>
const textRaw    = "{{MAIN}}".replace(/\\\\n/g,"\\n");
const footerLeft = "{{LEFT}}";
const footerRight = "{{RIGHT}}";
const yellowWords = "{{YELLOW}}".split("|").filter(x=>x.length>0);

const img = new Image();
img.src = "data:image/png;base64,{{BG}}";

const canvas = document.getElementById("posterCanvas");
const ctx = canvas.getContext("2d");

img.onload = function(){ drawPoster(); };

function drawPoster() {

    const W = img.naturalWidth;
    const H = img.naturalHeight;

    canvas.width = W;
    canvas.height = H;
    ctx.drawImage(img,0,0,W,H);

    const VW = 7000;
    const VH = 9000;
    const S = Math.min(W / VW, H / VH);

    const virtualTop = 2500;
    const virtualBottom = 6500;
    const areaW = VW * 0.90;
    const areaH = virtualBottom - virtualTop;

    const lines = textRaw.split("\\n");
    const lineGap = 1.3;

    let fontSize = 400;

    function maxWidth(fs){
        ctx.font = `${fs * S}px customFont`;
        let m=0;
        for(const l of lines){ m = Math.max(m, ctx.measureText(l).width); }
        return m / S;
    }

    function totalHeight(fs){
        return lines.length * fs * lineGap;
    }

    while(fontSize >= 80){
        if(maxWidth(fontSize) <= areaW && totalHeight(fontSize) <= areaH) break;
        fontSize -= 20;
    }

    function drawColoredLine(line, vx, vy){
        ctx.font = `${fontSize * S}px customFont`;

        const x = vx * S;
        const y = vy * S;

        let segs=[];
        let pos=0;

        while(pos < line.length){
            let matched=false;
            for(const w of yellowWords){
                if(line.startsWith(w,pos)){
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

        let totalW = segs.reduce((s,a)=>s+ctx.measureText(a.text).width,0);
        let cursor = x - totalW/2;

        for(const seg of segs){
            ctx.fillStyle = seg.yellow ? "#FFD700" : "white";
            ctx.textBaseline="middle";
            ctx.fillText(seg.text, cursor, y);
            cursor += ctx.measureText(seg.text).width;
        }
    }

    let tH = totalHeight(fontSize);
    let yStart = virtualTop + (areaH - tH)/2;

    for(const line of lines){
        drawColoredLine(line, VW*0.5, yStart);
        yStart += fontSize * lineGap;
    }

    const footerY = 8200;

    ctx.fillStyle="white";
    ctx.textBaseline="middle";
    ctx.font = `${280 * S}px customFont`;

    ctx.textAlign="left";
    ctx.fillText(footerLeft, (VW*0.05)*S, footerY*S);

    ctx.textAlign="right";
    ctx.fillText(footerRight, (VW*0.95)*S, footerY*S);
}

// 保存ボタン
document.getElementById("saveBtn").onclick = function(){
    canvas.toBlob(function(blob){
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "generated.jpg";
        document.body.appendChild(a);
        a.click();
        setTimeout(()=>{ URL.revokeObjectURL(url); a.remove(); }, 400);
    }, "image/jpeg", 0.88);
};
</script>
"""

# テンプレ置換
html_final = (
    html_template
    .replace("{{MAIN}}", main_js)
    .replace("{{LEFT}}", footer_left_js)
    .replace("{{RIGHT}}", footer_right_js)
    .replace("{{YELLOW}}", yellow_js)
    .replace("{{BG}}", bg_b64)
    .replace("{{FONTDATA}}", font_b64)
)

# 出力
st_html(html_final, height=950, scrolling=True)

