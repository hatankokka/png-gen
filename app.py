import streamlit as st
import base64
import html
import os
from streamlit.components.v1 import html as st_html

st.set_page_config(page_title="外交部ジェネレーター", layout="centered")

# -------------------------------
# タイトル
# -------------------------------
st.title("外交部風 画像ジェネレーター（7行まで1000px固定／8行以上縮小）")

# =========================================================
# ⚠️ 注意事項（タイトルの直下に表示）
# =========================================================
st.markdown("""
### ⚠️ 注意事項・禁止事項

当アプリは **娯楽目的の画像生成ツール** です。  
以下の行為は禁止しています。

#### 【禁止事項】
- 差別・侮辱・民族憎悪を助長する表現  
- 特定の個人・団体への誹謗中傷  
- 名誉毀損・プライバシー侵害  
- 公序良俗に反する内容  
- なりすまし、虚偽情報の拡散  
- 法令違反につながる利用  

#### 【免責事項】
- 当アプリで生成された画像・テキストの利用・公開・拡散によって生じた  
  **いかなる損害・トラブルについても当方は一切の責任を負いません。**
- 利用者による投稿内容についても **当方は責任を負いません。**

節度を守ってご利用ください。

---
""")

# =========================================================
# NGワードリスト読み込み (.streamlit/ng_words.txt)
# =========================================================
NG_WORDS_FILE = ".streamlit/ng_words.txt"

if os.path.exists(NG_WORDS_FILE):
    with open(NG_WORDS_FILE, "r", encoding="utf-8") as f:
        NG_WORDS = [w.strip() for w in f if w.strip()]
else:
    NG_WORDS = []


# ▼ 背景画像
BACKGROUND_CHOICES = {
    "背景 01": ".streamlit/background01.png",
    "背景 02": ".streamlit/background02.png",
}

# ▼ 初期テキスト
DEFAULT_MAIN = """“われわれは
回転焼派に告げる
大判焼問題で
火遊びをするな


火遊びをすれば
必ず身を滅ぼす”"""

DEFAULT_LEFT = "大判焼外交部報道官"
DEFAULT_RIGHT = "2015年11月1日"
DEFAULT_YELLOW_WORDS = "火遊び"

# ▼ session_state 初期
if "main_text" not in st.session_state:
    st.session_state.main_text = DEFAULT_MAIN
if "footer_left" not in st.session_state:
    st.session_state.footer_left = DEFAULT_LEFT
if "footer_right" not in st.session_state:
    st.session_state.footer_right = DEFAULT_RIGHT
if "yellow_words" not in st.session_state:
    st.session_state.yellow_words = DEFAULT_YELLOW_WORDS

# ▼ 背景（保持）
if "bg_choice" not in st.session_state:
    st.session_state.bg_choice = "背景 01"

bg_name = st.selectbox(
    "背景画像を選択",
    list(BACKGROUND_CHOICES.keys()),
    index=list(BACKGROUND_CHOICES.keys()).index(st.session_state.bg_choice)
)
st.session_state.bg_choice = bg_name

BG_PATH = BACKGROUND_CHOICES[bg_name]
with open(BG_PATH, "rb") as f:
    bg_b64 = base64.b64encode(f.read()).decode("utf-8")

# ▼ 入力 UI
main_text_input = st.text_area("本文", value=st.session_state.main_text)
footer_left_input = st.text_input("下部ヘッダー（左）", value=st.session_state.footer_left)
footer_right_input = st.text_input("下部ヘッダー（右）", value=st.session_state.footer_right)
yellow_words_input = st.text_area("黄色にしたい単語（改行区切り）", value=st.session_state.yellow_words)

# ▼ 反映
if st.button("★ 反映する"):
    st.session_state.main_text = main_text_input
    st.session_state.footer_left = footer_left_input
    st.session_state.footer_right = footer_right_input
    st.session_state.yellow_words = yellow_words_input
    st.rerun()

# ▼ 初期化（背景維持）
if st.button("★ 初期テキストに戻す"):
    keep_bg = st.session_state.bg_choice
    st.session_state.clear()
    st.session_state.bg_choice = keep_bg
    st.rerun()

# =========================================================
# NGワード検査（Canvas 描画前に実施）
# =========================================================

found_ng = []
for ng in NG_WORDS:
    if ng in st.session_state.main_text:
        found_ng.append(ng)

if found_ng:
    st.error(f"エラー：NGワード（{', '.join(found_ng)}）が本文に含まれています。修正してください。")
    st.stop()  # ← ここで停止＝Canvas が出ない


# ▼ JS渡し
main_js = html.escape(st.session_state.main_text).replace("\n", "\\n")
footer_left_js = html.escape(st.session_state.footer_left)
footer_right_js = html.escape(st.session_state.footer_right)

yellow_words_list = [w.strip() for w in st.session_state.yellow_words.split("\n") if w.strip()]
yellow_words_js = "|".join(yellow_words_list)


# ============================================================
# Canvas描画 HTML（7行以内1000px固定／8行以上は縮小）
# ============================================================

canvas_html = f"""
<div style="display:flex;flex-direction:column;align-items:center;gap:16px;">
  <button id="downloadBtn"
    style="padding:10px 20px;border-radius:999px;border:none;
           background:#f7d48b;color:#3b2409;font-weight:600;
           letter-spacing:0.08em;cursor:pointer;">
    画像をダウンロード
  </button>

  <canvas id="posterCanvas"
    style="max-width:100%;height:auto;border-radius:16px;
           box-shadow:0 10px 30px rgba(0,0,0,0.6);"></canvas>
</div>

<script>
  const textRaw = "{main_js}".replace(/\\\\n/g, "\\n");
  const footerLeft = "{footer_left_js}";
  const footerRight = "{footer_right_js}";
  const yellowWords = "{yellow_words_js}".split("|").filter(x=>x.length>0);

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

    const top = H * 0.28;
    const bottom = H * 0.70;
    const left = W * 0.10;
    const right = W * 0.90;

    const areaW = right - left;
    const areaH = bottom - top;

    const lineGap = 1.3;

    let fontSize;

    // ★ 7行以内 → 1000px固定
    if (lineCount <= 7) {{
        fontSize = 1000;
    }} else {{
        fontSize = 1000; // 8行以上は縮小開始
    }}

    function maxLineWidth(fs) {{
        ctx.font = fs + "px 'Noto Serif JP','Yu Mincho','serif'";
        let maxW = 0;
        for (const line of lines) {{
            const w = ctx.measureText(line).width;
            if (w > maxW) maxW = w;
        }}
        return maxW;
    }}

    function totalHeight(fs) {{
        return lines.length * fs * lineGap;
    }}

    // 7行以内 → 横幅だけチェック
    if (lineCount <= 7) {{
        while (fontSize >= 150) {{
            if (maxLineWidth(fontSize) <= areaW) break;
            fontSize -= 20;
        }}
    }}

    // 8行以上 → 横幅→縦収まりを両方チェック
    if (lineCount >= 8) {{
        while (fontSize >= 150) {{
            if (maxLineWidth(fontSize) <= areaW &&
                totalHeight(fontSize) <= areaH) break;
            fontSize -= 20;
        }}
    }}

    // ---- 黄色語描画
    function drawColoredLine(line, x, y) {{
        let segs = [];
        let pos = 0;

        while (pos < line.length) {{
            let matched = false;
            for (const w of yellowWords) {{
                if (line.startsWith(w, pos)) {{
                    segs.push({{"text": w, "yellow": true}});
                    pos += w.length;
                    matched = true;
                    break;
                }}
            }}
            if (!matched) {{
                segs.push({{"text": line[pos], "yellow": false}});
                pos++;
            }}
        }}

        ctx.font = fontSize + "px 'Noto Serif JP','Yu Mincho','serif'";
        ctx.lineJoin = "round";

        let totalWidth = segs.reduce((s,a)=>s+ctx.measureText(a.text).width,0);
        let cursor = x - totalWidth/2;

        for (const seg of segs) {{
            ctx.strokeStyle = "black";
            ctx.lineWidth = fontSize * 0.12;
            ctx.fillStyle = seg.yellow ? "#FFD700" : "white";
            ctx.textBaseline = "middle";

            ctx.strokeText(seg.text, cursor, y);
            ctx.fillText(seg.text, cursor, y);

            cursor += ctx.measureText(seg.text).width;
        }}
    }}

    const totalH = totalHeight(fontSize);
    let y = top + (areaH-totalH)/2 + fontSize*0.5;

    for (const line of lines) {{
        drawColoredLine(line, W*0.5, y);
        y += fontSize * lineGap;
    }}

    // ---- 下部ヘッダー
    const hSize = 250;
    ctx.font = hSize + "px 'Noto Serif JP','Yu Mincho','serif'";
    ctx.strokeStyle = "black";
    ctx.lineWidth = hSize*0.10;
    ctx.fillStyle = "white";
    ctx.textBaseline = "middle";

    if (footerLeft.trim().length > 0) {{
        ctx.textAlign = "left";
        ctx.strokeText(footerLeft, W*0.15, H*0.90);
        ctx.fillText(footerLeft, W*0.15, H*0.90);
    }}

    if (footerRight.trim().length > 0) {{
        ctx.textAlign = "right";
        ctx.strokeText(footerRight, W*0.85, H*0.90);
        ctx.fillText(footerRight, W*0.85, H*0.90);
    }}
  }}

  img.onload = drawPoster;

  document.getElementById("downloadBtn").onclick = function() {{
      const a = document.createElement("a");
      a.download = "output.png";
      a.href = canvas.toDataURL("image/png");
      a.click();
  }};
</script>
"""

st_html(canvas_html, height=950, scrolling=True)
