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

当アプリは **娯楽目的の画像生成ツール** です。以下の利用は禁止します。

#### 【禁止事項】
- 差別・侮辱・民族憎悪を助長する表現
- 特定の個人・団体への誹謗中傷
- 名誉毀損・プライバシー侵害
- 公序良俗に反する内容
- 虚偽情報や悪意あるミスリード
- 法令違反につながる利用

#### 【免責事項】
- 当アプリで作成された画像・投稿内容について  
  **当方は一切の責任を負いません。**
- ユーザーによるSNS投稿・再利用についても  
  **責任は利用者本人にあります。**

節度を守ってご利用ください。
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
# 初期テキスト
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
# session_state 初期化
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
# 入力UI
# =========================================================
main_text_input = st.text_area("本文", value=st.session_state.main_text, height=200)
footer_left_input = st.text_input("下部ヘッダー（左）", value=st.session_state.footer_left)
footer_right_input = st.text_input("下部ヘッダー（右）", value=st.session_state.footer_right)
yellow_words_input = st.text_area("黄色にしたい単語（改行区切り）", value=st.session_state.yellow_words)

# =========================================================
# 反映ボタン
# =========================================================
if st.button("反映する"):
    st.session_state.main_text = main_text_input
    st.session_state.footer_left = footer_left_input
    st.session_state.footer_right = footer_right_input
    st.session_state.yellow_words = yellow_words_input
    st.rerun()

# =========================================================
# 初期化ボタン（背景維持）
# =========================================================
if st.button("初期テキストに戻す"):
    keep = st.session_state.bg_choice
    st.session_state.clear()
    st.session_state.bg_choice = keep
    st.rerun()

# =========================================================
# NGワード検査
# =========================================================
found_ng = []
for ng in NG_WORDS:
    if ng in st.session_state.main_text:
        found_ng.append(ng)

if found_ng:
    st.error("⚠ エラー：NGワードが含まれています → " + ", ".join(found_ng))
    st.stop()

# =========================================================
# JSへ渡す値
# =========================================================
main_js = html.escape(st.session_state.main_text).replace("\n", "\\n")
footer_left_js = html.escape(st.session_state.footer_left)
footer_right_js = html.escape(st.session_state.footer_right)

yellow_list = [w.strip() for w in st.session_state.yellow_words.split("\n") if w.strip()]
yellow_js = "|".join(yellow_list)

# =========================================================
# Canvas + X投稿ボタン
# =========================================================
canvas_html = f"""
<div style="display:flex;flex-direction:column;align-items:center;gap:16px;">

  <button id="downloadBtn"
    style="padding:10px 20px;border-radius:999px;border:none;
           background:#f7d48b;color:#3b2409;font-weight:600;cursor:pointer;">
    画像をダウンロード
  </button>

  <button id="tweetBtn"
    style="padding:10px 20px;border-radius:999px;border:none;
           background:#1DA1F2;color:white;font-weight:600;cursor:pointer;">
    X に投稿する
  </button>

  <canvas id="posterCanvas"
    style="max-width:100%;height:auto;border-radius:16px;
           box-shadow:0 10px 30px rgba(0,0,0,0.6);">
  </canvas>
</div>

<script>
const textRaw = "{main_js}".replace(/\\\\n/g,"\\n");
const footerLeft = "{footer_left_js}";
const footerRight = "{footer_right_js}";
const yellowWords = "{yellow_js}".split("|").filter(x=>x.length>0);

const img = new Image();
img.src = "data:image/png;base64,{bg_b64}";
const canvas = document.getElementById("posterCanvas");
const ctx = canvas.getContext("2d");

function drawPoster() {{
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

    let fontSize = (lineCount <= 7) ? 1000 : 1000;

    function maxWidth(fs){{
        ctx.font = fs+"px 'Noto Serif JP','Yu Mincho','serif'";
        let m = 0;
        for(const l of lines) m = Math.max(m, ctx.measureText(l).width);
        return m;
    }}

    function totalHeight(fs) {{
        return lines.length * fs * lineGap;
    }}

    if (lineCount <= 7) {{
        while (fontSize >= 150) {{
            if (maxWidth(fontSize) <= areaW) break;
            fontSize -= 20;
        }}
    }} else {{
        while (fontSize >= 150) {{
            if (maxWidth(fontSize) <= areaW && totalHeight(fontSize) <= areaH) break;
            fontSize -= 20;
        }}
    }}

    function drawColoredLine(line,x,y){{
        let segs=[];
        let pos=0;
        while(pos<line.length){{
            let matched=false;
            for(const w of yellowWords){{
                if(line.startsWith(w,pos)){{
                    segs.push({{text:w,yellow:true}});
                    pos+=w.length;
                    matched=true; break;
                }}
            }}
            if(!matched){{
                segs.push({{text:line[pos],yellow:false}});
                pos++;
            }}
        }}

        ctx.font = fontSize+"px 'Noto Serif JP','Yu Mincho','serif'";
        ctx.lineJoin="round";

        let totalW = segs.reduce((s,a)=>s+ctx.measureText(a.text).width,0);
        let cursor = x - totalW/2;

        for(const seg of segs){{
            ctx.strokeStyle="black";
            ctx.lineWidth=fontSize*0.12;
            ctx.fillStyle = seg.yellow ? "#FFD700" : "white";
            ctx.textBaseline="middle";

            ctx.strokeText(seg.text,cursor,y);
            ctx.fillText(seg.text,cursor,y);

            cursor += ctx.measureText(seg.text).width;
        }}
    }}

    const tH = totalHeight(fontSize);
    let y = top + (areaH - tH)/2 + fontSize*0.5;

    for(const line of lines){{
        drawColoredLine(line, W*0.5, y);
        y += fontSize * lineGap;
    }}

    const hSize=250;
    ctx.font = hSize+"px 'Noto Serif JP','Yu Mincho','serif'";
    ctx.strokeStyle="black";
    ctx.lineWidth=hSize*0.10;
    ctx.fillStyle="white";
    ctx.textBaseline="middle";

    if(footerLeft.trim().length>0){{
        ctx.textAlign="left";
        ctx.strokeText(footerLeft, W*0.15, H*0.90);
        ctx.fillText(footerLeft, W*0.15, H*0.90);
    }}

    if(footerRight.trim().length>0){{
        ctx.textAlign="right";
        ctx.strokeText(footerRight, W*0.85, H*0.90);
        ctx.fillText(footerRight, W*0.85, H*0.90);
    }}
}}

img.onload = drawPoster;

// =========================================================
// 画像ダウンロード
// =========================================================
document.getElementById("downloadBtn").onclick = function(){{
    const a = document.createElement("a");
    a.download = "output.png";
    a.href = canvas.toDataURL("image/png");
    a.click();
}};

// =========================================================
// X投稿（画像コピー → 投稿画面へ）
// =========================================================
document.getElementById("tweetBtn").onclick = async function(){

    // ★ 先に X 投稿画面を開く（ポップアップブロック対策）
    const text = encodeURIComponent(
        "この画像は大判焼外交部ジェネレーターを使ったパロディ画像です\n" +
        "https://ikan-no-i-gen.streamlit.app/"
    );
    const url = "https://twitter.com/intent/tweet?text=" + text;
    window.open(url, "_blank");

    // ★ 次に画像コピー（この順番が重要）
    canvas.toBlob(async function(blob){
        try {
            await navigator.clipboard.write([
                new ClipboardItem({"image/png": blob})
            ]);
            alert("画像をコピーしました！\nXの投稿画面で Ctrl+V（ペースト）してください。");
        } catch(e){
            alert("画像コピーに失敗しました。Chrome / Edge を使用してください。");
            console.error(e);
        }
    });

};

</script>
"""

st_html(canvas_html, height=950, scrolling=True)

