import streamlit as st
import base64
import html
import os
from streamlit.components.v1 import html as st_html

st.set_page_config(page_title="外交部ジェネレーター", layout="centered")
st.title("外交部風 画像ジェネレーター（最終完全版・フォント最大化＋縦収まり対応）")

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

# ▼ session_state 初期設定
if "main_text" not in st.session_state:
    st.session_state.main_text = DEFAULT_MAIN
if "footer_left" not in st.session_state:
    st.session_state.footer_left = DEFAULT_LEFT
if "footer_right" not in st.session_state:
    st.session_state.footer_right = DEFAULT_RIGHT
if "yellow_words" not in st.session_state:
    st.session_state.yellow_words = DEFAULT_YELLOW_WORDS

# ▼ 背景（保持する）
if "bg_choice" not in st.session_state:
    st.session_state.bg_choice = "背景 01"

bg_name = st.selectbox(
    "背景画像を選択",
    list(BACKGROUND_CHOICES.keys()),
    index=list(BACKGROUND_CHOICES.keys()).index(st.session_state.bg_choice),
)
st.session_state.bg_choice = bg_name

BG_PATH = BACKGROUND_CHOICES[bg_name]
with open(BG_PATH, "rb") as f:
    bg_b64 = base64.b64encode(f.read()).decode("utf-8")

# ▼ 入力 UI
main_text_input = st.text_area("本文", value=st.session_state.main_text)
footer_left_input = st.text_input("下部ヘッダー（左）", value=st.session_state.footer_left)
footer_right_input = st.text_input("下部ヘッダー（右）", value=st.session_state.footer_right)
yellow_words_input = st.text_area("黄色にしたい単語（改行区切り）",
                                  value=st.session_state.yellow_words)

# ▼ 反映する
if st.button("★ 反映する"):
    st.session_state.main_text = main_text_input
    st.session_state.footer_left = footer_left_input
    st.session_state.footer_right = footer_right_input
    st.session_state.yellow_words = yellow_words_input
    st.rerun()

# ▼ 初期化（背景は保持）
if st.button("★ 初期テキストに戻す"):
    keep_bg = st.session_state.bg_choice
    st.session_state.clear()
    st.session_state.bg_choice = keep_bg
    st.rerun()

# ▼ JSへ渡す値
main_js = html.escape(st.session_state.main_text).replace("\n", "\\n")
footer_left_js = html.escape(st.session_state.footer_left)
footer_right_js = html.escape(st.session_state.footer_right)

yellow_words_list = [
    w.strip() for w in st.session_state.yellow_words.split("\n") if w.strip()
]
yellow_words_js = "|".join(yellow_words_list)

# =========================================================
# Canvas 描画 HTML（最大行幅 → 縦収まりチェック方式）
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
  const textRaw = "{main_js}".replace(/\\\\n/g, "\\n");
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

    const lines = textRaw.split("\\n");  // ★ 空行保持

    const top = H * 0.28;
    const bottom = H * 0.70;
    const left = W * 0.10;
    const right = W * 0.90;
    const areaW = right - left;
    const areaH = bottom - top;

    let fontSize = 1200;      // ★ 最大フォント
    const minFont = 150;
    const lineGap = 1.3;

    // --- 横幅チェック（最大行幅）
    function maxLineWidth(fs) {{
      ctx.font = fs + "px 'Noto Serif JP','Yu Mincho','serif'";
      let maxW = 0;
      for (const line of lines) {{
        const w = ctx.measureText(line).width;
        if (w > maxW) maxW = w;
      }}
      return maxW;
    }}

    // --- 縦方向チェック（空行も含めた行数 × 行間）
    function totalHeight(fs) {{
      return lines.length * fs * lineGap;
    }}

    // ① 横幅でフォントを決定
    while (fontSize >= minFont) {{
      if (maxLineWidth(fontSize) <= areaW) break;
      fontSize -= 20;
    }}

    // ② 縦が収まるかチェック
    while (fontSize >= minFont) {{
      if (totalHeight(fontSize) <= areaH) break;
      fontSize -= 20;
    }}

    // ---- 描画（黄色語対応）
    function drawColoredLine(line, x, y) {{
      let segments = [];
      let pos = 0;

      while (pos < line.length) {{
        let matched = false;

        for (const w of yellowWords) {{
          if (line.startsWith(w, pos)) {{
            segments.push({{ "text": w, "yellow": true }});
            pos += w.length;
            matched = true;
            break;
          }}
        }}
        if (!matched) {{
          segments.push({{ "text": line[pos], "yellow": false }});
          pos++;
        }}
      }}

      ctx.font = fontSize + "px 'Noto Serif JP','Yu Mincho','serif'";
      let totalWidth = segments.reduce((s,a)=>s+ctx.measureText(a.text).width,0);
      let cursor = x - totalWidth/2;

      for (const seg of segments) {{
        ctx.lineJoin = "round";
        ctx.strokeStyle = "black";
        ctx.lineWidth = fontSize * 0.12;
        ctx.fillStyle = seg.yellow ? "#FFD700" : "white";
        ctx.textBaseline = "middle";

        ctx.strokeText(seg.text, cursor, y);
        ctx.fillText(seg.text, cursor, y);

        cursor += ctx.measureText(seg.text).width;
      }}
    }}

    // ---- 本文描画
    const totalH = totalHeight(fontSize);
    let y = top + (areaH - totalH) / 2 + fontSize * 0.5;

    for (const line of lines) {{
      drawColoredLine(line, W*0.5, y);
      y += fontSize * lineGap;
    }}

    // ---- ヘッダー 250px
    const hSize = 250;
    ctx.font = hSize + "px 'Noto Serif JP','Yu Mincho','serif'";
    ctx.strokeStyle = "black";
    ctx.lineWidth = hSize * 0.10;
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

# 描画
st_html(canvas_html, height=950, scrolling=True)
