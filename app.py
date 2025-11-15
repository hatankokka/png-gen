import streamlit as st
import base64
import html
import os
from streamlit.components.v1 import html as st_html

st.set_page_config(page_title="外交部ジェネレーター", layout="centered")
st.title("外交部風 画像ジェネレーター（本文1200px／黄色語／反映ボタン／初期化修正）")

# ▼ 背景画像の選択肢
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

# ▼ session_state 初期化
defaults = {
    "main_text": DEFAULT_MAIN,
    "footer_left": DEFAULT_LEFT,
    "footer_right": DEFAULT_RIGHT,
    "yellow_words": DEFAULT_YELLOW_WORDS,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ▼ 背景選択
bg_name = st.selectbox("背景画像を選択", list(BACKGROUND_CHOICES.keys()))
BG_PATH = BACKGROUND_CHOICES[bg_name]

if not os.path.exists(BG_PATH):
    st.error(f"{BG_PATH} が見つかりません。")
    st.stop()

with open(BG_PATH, "rb") as f:
    bg_b64 = base64.b64encode(f.read()).decode("utf-8")

# ▼ 入力欄（常に session_state を value に使用）
main_text_input = st.text_area("本文", value=st.session_state.main_text, key="main_text_input")
footer_left_input = st.text_input("下部ヘッダー（左）", value=st.session_state.footer_left, key="footer_left_input")
footer_right_input = st.text_input("下部ヘッダー（右）", value=st.session_state.footer_right, key="footer_right_input")
yellow_words_input = st.text_area("黄色にしたい単語（改行区切り）",
                                  value=st.session_state.yellow_words,
                                  key="yellow_words_input")

# ▼ 反映ボタン（session_state の本体値に反映 → rerun）
if st.button("★ 反映する"):
    st.session_state.main_text = main_text_input
    st.session_state.footer_left = footer_left_input
    st.session_state.footer_right = footer_right_input
    st.session_state.yellow_words = yellow_words_input
    st.rerun()

# ▼ 初期化ボタン（ウィジェットキーを触らず、本体値だけ戻す）
if st.button("★ 初期テキストに戻す"):
    st.session_state.main_text = DEFAULT_MAIN
    st.session_state.footer_left = DEFAULT_LEFT
    st.session_state.footer_right = DEFAULT_RIGHT
    st.session_state.yellow_words = DEFAULT_YELLOW_WORDS
    st.rerun()

# ▼ JS に渡す値（すべて本体値）
main_js = html.escape(st.session_state.main_text).replace("\n", "\\n")
footer_left_js = html.escape(st.session_state.footer_left)
footer_right_js = html.escape(st.session_state.footer_right)

yellow_words_list = [w.strip() for w in st.session_state.yellow_words.split("\n") if w.strip()]
yellow_words_js = "|".join(yellow_words_list)

# =========================================================
# Canvas 描画（本文 最大1200px・黄色語）
# =========================================================

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
  const mainTextRaw = "{main_js}".replace(/\\\\n/g, "\\n");
  const footerLeft = "{footer_left_js}";
  const footerRight = "{footer_right_js}";
  const yellowWords = "{yellow_words_js}".split("|").filter(x => x.length > 0);

  const img = new Image();
  img.src = "data:image/png;base64,{bg_b64}";
  const canvas = document.getElementById("posterCanvas");
  const ctx = canvas.getContext("2d");

  function drawPoster() {{
    const W = img.naturalWidth;
    const H = img.naturalHeight;

    canvas.width = W;
    canvas.height = H;

    ctx.clearRect(0,0,W,H);
    ctx.drawImage(img,0,0,W,H);

    // 本文
    const lines = mainTextRaw.split("\\n").filter(l => l.trim().length > 0);

    const top = H * 0.28;
    const bottom = H * 0.70;
    const left = W * 0.10;
    const right = W * 0.90;
    const areaW = right - left;
    const areaH = bottom - top;

    let fontSize = 1200;   // ★ 最大1200px
    const minFont = 150;

    function measure(f) {{
      ctx.font = f + "px 'Noto Serif JP','Yu Mincho','serif'";
      let maxW = 0;
      for (const line of lines) {{
        const w = ctx.measureText(line).width;
        if (w > maxW) maxW = w;
      }}
      const totalH = lines.length * f * 1.3;
      return {{ maxW, totalH }};
    }}

    while (fontSize >= minFont) {{
      const {{ maxW, totalH }} = measure(fontSize);
      if (maxW <= areaW && totalH <= areaH) break;
      fontSize -= 20;
    }}

    // 黄色語処理
    function drawColoredLine(line, cx, y) {{
      let segs = [];
      let pos = 0;

      while (pos < line.length) {{
        let matched = false;

        for (const word of yellowWords) {{
          if (line.startsWith(word, pos)) {{
            segs.push({{ text: word, yellow: true }});
            pos += word.length;
            matched = true;
            break;
          }}
        }}

        if (!matched) {{
          segs.push({{ text: line[pos], yellow: false }});
          pos++;
        }}
      }}

      ctx.font = fontSize + "px 'Noto Serif JP','Yu Mincho','serif'";
      let totalW = segs.reduce((s, seg) => s + ctx.measureText(seg.text).width, 0);

      let x = cx - totalW / 2;

      for (const seg of segs) {{
        ctx.textBaseline = "middle";
        ctx.lineJoin = "round";
        ctx.lineWidth = fontSize * 0.12;
        ctx.strokeStyle = "black";
        ctx.fillStyle = seg.yellow ? "#FFD700" : "white";

        ctx.strokeText(seg.text, x, y);
        ctx.fillText(seg.text, x, y);

        x += ctx.measureText(seg.text).width;
      }}
    }}

    // 本文描画
    const {{ totalH }} = measure(fontSize);
    let yStart = top + (areaH - totalH) / 2 + fontSize * 0.5;

    for (const line of lines) {{
      drawColoredLine(line, W * 0.5, yStart);
      yStart += fontSize * 1.3;
    }}

    // ヘッダー（250px固定）
    const hSize = 250;
    ctx.font = hSize + "px 'Noto Serif JP','Yu Mincho','serif'";
    ctx.lineJoin = "round";
    ctx.lineWidth = hSize * 0.10;
    ctx.strokeStyle = "black";
    ctx.fillStyle = "white";
    ctx.textBaseline = "middle";

    if (footerLeft.trim().length > 0) {{
      ctx.textAlign = "left";
      ctx.strokeText(footerLeft, W * 0.15, H * 0.90);
      ctx.fillText(footerLeft, W * 0.15, H * 0.90);
    }}

    if (footerRight.trim().length > 0) {{
      ctx.textAlign = "right";
      ctx.strokeText(footerRight, W * 0.85, H * 0.90);
      ctx.fillText(footerRight, W * 0.85, H * 0.90);
    }}
  }}

  img.onload = drawPoster;

  document.getElementById("downloadBtn").onclick = function() {{
    const link = document.createElement("a");
    link.download = "output.png";
    link.href = canvas.toDataURL("image/png");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }};
</script>
"""

# 描画
st_html(canvas_html, height=950, scrolling=True)
