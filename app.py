import streamlit as st
import base64
import html
import os
from streamlit.components.v1 import html as st_html

st.set_page_config(page_title="大判焼外交部ジェネレーター", layout="centered")

# =========================================================
# タイトル
# =========================================================
st.title("大判焼外交部ジェネレーター")

# =========================================================
# ⚠️ 注意事項
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
- SNS 投稿や転載も **利用者の自己責任** で行ってください。

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
}

# =========================================================
# 初期値
# =========================================================
DEFAULT_MAIN = """“われわれは
回転焼派に告げる
大判焼問題で
火遊びをするな

火遊びをすれば
必ず身を滅ぼす”"""

DEFAULT_LEFT = "大判焼外交部報道官"
DEFAULT_RIGHT = "2015年11月1日"
DEFAULT_YELLOW = "火遊び"

# =========================================================
# session_state
# =========================================================
if "main_text" not in st.session_state: st.session_state.main_text = DEFAULT_MAIN
if "footer_left" not in st.session_state: st.session_state.footer_left = DEFAULT_LEFT
if "footer_right" not in st.session_state: st.session_state.footer_right = DEFAULT_RIGHT
if "yellow_words" not in st.session_state: st.session_state.yellow_words = DEFAULT_YELLOW
if "bg_choice" not in st.session_state: st.session_state.bg_choice = "背景 01"

# =========================================================
# 背景選択
# =========================================================
bg_name = st.selectbox(
    "背景画像を選択",
    list(BACKGROUND_CHOICES.keys()),
    index=list(BACKGROUND_CHOICES.keys()).index(st.session_state.bg_choice)
)
st.session_state.bg_choice = bg_name

BG_PATH = BACKGROUND_CHOICES[bg_name]
with open(BG_PATH, "rb") as f:
    bg_b64 = base64.b64encode(f.read()).decode("utf-8")

# =========================================================
# 入力欄
# =========================================================
main_text_input = st.text_area("本文", value=st.session_state.main_text, height=200)
footer_left_input = st.text_input("下部ヘッダー（左）", value=st.session_state.footer_left)
footer_right_input = st.text_input("下部ヘッダー（右）", value=st.session_state.footer_right)
yellow_words_input = st.text_area("黄色にしたい単語（改行区切り）", value=st.session_state.yellow_words)

# =========================================================
# ボタン
# =========================================================

if st.button("反映する"):
    st.session_state.main_text = main_text_input
    st.session_state.footer_left = footer_left_input
    st.session_state.footer_right = footer_right_input
    st.session_state.yellow_words = yellow_words_input
    st.rerun()

if st.button("初期テキストに戻す"):
    keep_bg = st.session_state.bg_choice
    st.session_state.clear()
    st.session_state.bg_choice = keep_bg
    st.rerun()

# =========================================================
# NGチェック
# =========================================================
found = [ng for ng in NG_WORDS if ng in st.session_state.main_text]
if found:
    st.error("⚠ エラー：NGワードが含まれています → " + ", ".join(found))
    st.stop()

# =========================================================
# JSに渡す値
# =========================================================
main_js = html.escape(st.session_state.main_text).replace("\n", "\\n")
footer_left_js = html.escape(st.session_state.footer_left)
footer_right_js = html.escape(st.session_state.footer_right)
yellow_js = "|".join([w.strip() for w in st.session_state.yellow_words.split("\n") if w.strip()])

# =========================================================
# HTML & JS（画像コピー + X投稿）
# =========================================================

html_code = """
<div style="display:flex;flex-direction:column;align-items:center;gap:16px;">

  <button id="copyBtn"
    style="padding:12px 24px;border-radius:999px;border:none;
           background:#FFD700;color:black;font-weight:700;cursor:pointer;">
    画像をコピー
  </button>

  <button id="tweetBtn"
    style="padding:12px 24px;border-radius:999px;border:none;
           background:#1DA1F2;color:white;font-weight:700;cursor:pointer;">
    X に投稿する
  </button>

  <canvas id="posterCanvas"
    style="max-width:100%;border-radius:16px;
           box-shadow:0 10px 30px rgba(0,0,0,0.6);">
  </canvas>

</div>

<script>
const textRaw = "{{MAIN}}".replace(/\\\\n/g,"\\n");
const footerLeft = "{{LEFT}}";
const footerRight = "{{RIGHT}}";
const yellowWords = "{{YELLOW}}".split("|").filter(x => x.length > 0);

const img = new Image();
img.src = "data:image/png;base64,{{BG}}";

const canvas = document.getElementById("posterCanvas");
const ctx = canvas.getContext("2d");

img.onload = function(){ drawPoster(); };

function drawPoster(){

    const W = img.naturalWidth;
    const H = img.naturalHeight;

    canvas.width = W;
    canvas.height = H;

    ctx.drawImage(img,0,0,W,H);

    const lines = textRaw.split("\\n");
    const lineCount = lines.length;

    const top = H*0.28, bottom = H*0.70;
    const left = W*0.10, right = W*0.90;

    const areaW = right-left;
    const areaH = bottom-top;
    const lineGap = 1.3;

    let fontSize = 1000;

    function maxWidth(fs){
        ctx.font = fs + "px serif";
        let m = 0;
        for(const l of lines){
            m = Math.max(m, ctx.measureText(l).width);
        }
        return m;
    }

    function totalHeight(fs){
        return lines.length * fs * lineGap;
    }

    if(lineCount <= 7){
        while(fontSize >= 150){
            if(maxWidth(fontSize) <= areaW) break;
            fontSize -= 20;
        }
    } else {
        while(fontSize >= 150){
            if(maxWidth(fontSize) <= areaW && totalHeight(fontSize) <= areaH) break;
            fontSize -= 20;
        }
    }

    function drawColoredLine(line, x, y){
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

        ctx.font = fontSize+"px serif";
        ctx.lineJoin="round";

        let totalW = segs.reduce((s,a)=>s + ctx.measureText(a.text).width, 0);
        let cursor = x - totalW/2;

        for(const seg of segs){
            ctx.strokeStyle="black";
            ctx.lineWidth = fontSize*0.12;
            ctx.fillStyle = seg.yellow ? "#FFD700" : "white";
            ctx.textBaseline = "middle";

            ctx.strokeText(seg.text, cursor, y);
            ctx.fillText(seg.text, cursor, y);

            cursor += ctx.measureText(seg.text).width;
        }
    }

    let tH = totalHeight(fontSize);
    let y = top + (areaH - tH)/2 + fontSize*0.5;

    for(const line of lines){
        drawColoredLine(line, W*0.5, y);
        y += fontSize * lineGap;
    }

    const hSize = 250;
    ctx.font = hSize+"px serif";
    ctx.strokeStyle="black";
    ctx.lineWidth=hSize*0.10;
    ctx.fillStyle="white";
    ctx.textBaseline="middle";

    if(footerLeft.trim().length>0){
        ctx.textAlign="left";
        ctx.strokeText(footerLeft, W*0.15, H*0.90);
        ctx.fillText(footerLeft, W*0.15, H*0.90);
    }

    if(footerRight.trim().length>0){
        ctx.textAlign="right";
        ctx.strokeText(footerRight, W*0.85, H*0.90);
        ctx.fillText(footerRight, W*0.85, H*0.90);
    }
}

// ----------------------------------------------------------
// ① 画像コピー（ユーザー操作 → 100%成功）
// ----------------------------------------------------------
document.getElementById("copyBtn").onclick = function(){
    canvas.toBlob(async function(blob){
        try{
            await navigator.clipboard.write([
                new ClipboardItem({"image/png": blob})
            ]);
            alert("✔ 画像をコピーしました！\\nX 投稿画面で Ctrl+V してください。");
        } catch(e){
            alert("画像コピーに失敗しました。Chrome / Edge を使用してください。");
        }
    });
};

// ----------------------------------------------------------
// ② X投稿（100%成功）
// ----------------------------------------------------------
document.getElementById("tweetBtn").onclick = function(){

    const text = encodeURIComponent(
        "この画像は大判焼外交部ジェネレーターを使ったパロディ画像です\\n" +
        "https://ikan-no-i-gen.streamlit.app/"
    );

    const url = "https://twitter.com/intent/tweet?text=" + text;
    window.open(url, "_blank");
};

</script>
"""

html_code = html_code.replace("{{MAIN}}", main_js)
html_code = html_code.replace("{{LEFT}}", footer_left_js)
html_code = html_code.replace("{{RIGHT}}", footer_right_js)
html_code = html_code.replace("{{YELLOW}}", yellow_js)
html_code = html_code.replace("{{BG}}", bg_b64)

st_html(html_code, height=950, scrolling=True)
