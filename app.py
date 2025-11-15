import streamlit as st
import base64
import html
import os
from streamlit.components.v1 import html as st_html

st.set_page_config(page_title="外交部ジェネレーター", layout="centered")
st.title("外交部風 画像ジェネレーター（本文1200px・ヘッダー250px）")

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
initial_values = {
    "main_text": DEFAULT_MAIN,
    "footer_left": DEFAULT_LEFT,
    "footer_right": DEFAULT_RIGHT,
    "yellow_words": DEFAULT_YELLOW_WORDS
}
for key, value in initial_values.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ▼ 背景選択
bg_name = st.selectbox("背景画像を選択", list(BACKGROUND_CHOICES.keys()))
BG_PATH = BACKGROUND_CHOICES[bg_name]

if not os.path.exists(BG_PATH):
    st.error(f"{BG_PATH} が見つかりません")
    st.stop()

with open(BG_PATH, "rb") as f:
    bg_b64 = base64.b64encode(f.read()).decode("utf-8")

# ▼ 入力欄（UI側入力）
main_text_input = st.text_area("本文", st.session_state.main_text, key="main_text_input")
footer_left_input = st.text_input("下部ヘッダー（左）", st.session_state.footer_left, key="footer_left_input")
footer_right_input = st.text_input("下部ヘッダー（右）", st.session_state.footer_right, key="footer_right_input")
yellow_words_input = st.text_area(
    "黄色にしたい単語（改行区切り）",
    st.session_state.yellow_words,
    key="yellow_words_input"
)

# ▼ 反映ボタン
if st.button("★ 反映する"):
    st.session_state.main_text = main_text_input
    st.session_state.footer_left = footer_left_input
    st.session_state.footer_right = footer_right_input
    st.session_state.yellow_words = yellow_words_input
    st.rerun()

# ▼ 初期化ボタン
if st.button("★ 初期テキストに戻す"):
    st.session_state.main_text = DEFAULT_MAIN
    st.session_state.footer_left = DEFAULT_LEFT
    st.session_state.footer_right = DEFAULT_RIGHT
    st.session_state.yellow_words = DEFAULT_YELLOW_WORDS
    st.rerun()

# ▼ JS に渡す値
main_js = html.escape(st.session_state.main_text).replace("\n", "\\n")
footer_left_js = html.escape(st.session_state.footer_left)
footer_right_js = html.escape(st.session_state.footer_right)

# 黄色単語を JS に渡す形式に変換
yellow_words_list = [
    w.strip() for w in st.session_state.yellow_words.split("\n") if w.strip()
]
yellow_words_js = "|".join(yellow_words_list)

# ============================================
# Canvas描画 HTML（本文最大1200px対応）
# ============================================

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
           box-shadow:0 10px 30px rgba(0,0,0,0.6);">
  </canvas>
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

    ctx.clearRect(0, 0, W, H);
    ctx.drawImage(img, 0, 0, W, H);

    // ---- 本文行処理 ----
    const lines = mainTextRaw.split("\\n").filter(l => l.trim().length > 0);

    const top = H * 0.28;
    const bottom = H * 0.70;
    const left = W * 0.10;
    const right = W * 0.90;
    const areaW = right - left;
    const areaH = bottom - top;

    // ===== 本文フォント：最大1200px =====
    let fontSize = 1200;
    const minFont = 150;

    function measure(fs) {{
      ctx.font = fs + "px 'Noto Serif JP','Yu Mincho','serif'";
      let maxW = 0;
      for (const line of lines) {{
        const w = ctx.measureText(line).width;
        if (w > maxW) maxW = w;
      }}
      const totalH = lines.length * fs * 1.3;
      return {{ maxW, totalH }};
    }}

    // 自動縮小ループ
    while (fontSize >= minFont) {{
      const {{ maxW, totalH }} = measure(fontSize);
      if (maxW <= areaW && totalH <= areaH) break;
      fontSize -= 20;
    }}

    // ---- 黄色語処理 ----
    function drawColoredLine(line, xCenter, y) {{
      let segments = [];
      let pos = 0;

      while (pos < line.length) {{
        let matched = false;

        for (const word of yellowWords) {{
          if (line.startsWith(word, pos)) {{
            segments.push({{ text: word, yellow: true }});
            pos += word.length;
            matched = true;
            break;
          }}
        }}

        if (!matched) {{
          segments.push({{ text: line[pos], yellow: false }});
          pos++;
        }}
      }}

      let totalWidth = 0;
      ctx.font = fontSize + "px 'Noto Serif JP','Yu Mincho','serif'";
      for (const seg of segments) {{
        totalWidth += ctx.measureText(seg.text).width;
      }}

      let cursorX = xCenter - totalWidth / 2;

      for (const seg of segments) {{
        ctx.font = fontSize + "px 'Noto Serif JP','Yu Mincho','serif'";
        ctx.textBaseline = "middle";
        ctx.lineJoin = "round";
        ctx.strokeStyle = "black";
        ctx.lineWidth = fontSize * 0.12;
        ctx.fillStyle = seg.yellow ? "#FFD700" : "white";

        ctx.strokeText(seg.text, cursorX, y);
        ctx.fillText(seg.text, cursorX, y);

        cursorX += ctx.measureText(seg.text).width;
      }}
    }}

    // ---- 本文描画 ----
    if (lines.length > 0) {{
      const {{ totalH }} = measure(fontSize);
      let y = top + (areaH - totalH) / 2 + fontSize * 0.5;

      for (const line of lines) {{
        drawColoredLine(line, W * 0.50, y);
        y += fontSize * 1.3;
      }}
    }}

    // ---- ヘッダー（固定250px）----
    const headerSize = 250;

    ctx.font = headerSize + "px 'Noto Serif JP','Yu Mincho','serif'";
    ctx.lineJoin = "round";
    ctx.lineWidth = headerSize * 0.10;
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

st_html(canvas_html, height=950, scrolling=True)
