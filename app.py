import streamlit as st
import base64
import html
import os
from streamlit.components.v1 import html as st_html

st.set_page_config(page_title="外交部ジェネレーター", layout="centered")
st.title("外交部風 画像ジェネレーター（背景切替版 Canvas 完全対応）")

# ▼ 背景画像の選択肢（あなたのフォルダに合わせて設定済み）
BACKGROUND_CHOICES = {
    "背景 01": ".streamlit/background01.png",
    "背景 02": ".streamlit/background02.png",
}

# ▼ UI：背景を選択
bg_name = st.selectbox("背景画像を選択", list(BACKGROUND_CHOICES.keys()))

BG_PATH = BACKGROUND_CHOICES[bg_name]

if not os.path.exists(BG_PATH):
    st.error(f"{BG_PATH} が見つかりません。フォルダ構造を確認してください。")
    st.stop()

# ▼ 背景画像を Base64 化
with open(BG_PATH, "rb") as f:
    bg_b64 = base64.b64encode(f.read()).decode("utf-8")

# ▼ 入力 UI
main_text = st.text_area("本文（複数行OK・自動縮小対応）", "")
footer_left = st.text_input("下部ヘッダー（左）", "")
footer_right = st.text_input("下部ヘッダー（右）", "")

# ▼ HTMLエスケープ
main_js = html.escape(main_text).replace("\n", "\\n")
footer_left_js = html.escape(footer_left)
footer_right_js = html.escape(footer_right)

# ▼ Canvas 描画用 HTML（すべて再現版）
canvas_html = f"""
<div style="display:flex;flex-direction:column;align-items:center;gap:16px;">
  <button id="downloadBtn"
    style="
      padding:10px 20px;
      border-radius:999px;
      border:none;
      background:#f7d48b;
      color:#3b2409;
      font-weight:600;
      letter-spacing:0.08em;
      cursor:pointer;">
    画像をダウンロード
  </button>

  <canvas id="posterCanvas"
    style="max-width:100%;height:auto;border-radius:16px;box-shadow:0 10px 30px rgba(0,0,0,0.6);">
  </canvas>
</div>

<script>
  const mainTextRaw = "{main_js}".replace(/\\\\n/g, "\\n");
  const footerLeft = "{footer_left_js}";
  const footerRight = "{footer_right_js}";

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
    ctx.drawImage(img, 0, 0, W, H);

    const mainText = mainTextRaw || "";

    // ★ 本文エリア（背景画像の比率から算出）
    const top = H * 0.28;
    const bottom = H * 0.70;
    const left = W * 0.10;
    const right = W * 0.90;
    const areaW = right - left;
    const areaH = bottom - top;

    // ★ 本文フォント自動縮小
    let maxFont = 600;
    let minFont = 150;
    let fontSize = maxFont;
    const lines = mainText.split("\\n");

    function measure(fontPx) {{
      ctx.font = fontPx + "px 'Noto Serif JP','Yu Mincho','serif'";
      let maxLineW = 0;
      for (const line of lines) {{
        const w = ctx.measureText(line).width;
        if (w > maxLineW) maxLineW = w;
      }}
      const totalH = lines.length * fontPx * 1.30;
      return {{ maxLineW, totalH }};
    }}

    if (mainText.trim().length > 0) {{
      while (fontSize >= minFont) {{
        const {{maxLineW, totalH}} = measure(fontSize);
        if (maxLineW <= areaW && totalH <= areaH) break;
        fontSize -= 20;
      }}
      if (fontSize < minFont) fontSize = minFont;

      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.lineJoin = "round";

      const {{totalH}} = measure(fontSize);
      let y = top + (areaH - totalH) / 2 + fontSize * 0.5;

      for (const line of lines) {{
        const x = left + areaW / 2;
        ctx.font = fontSize + "px 'Noto Serif JP','Yu Mincho','serif'";
        ctx.lineWidth = fontSize * 0.12;
        ctx.strokeStyle = "black";
        ctx.fillStyle = "white";
        ctx.strokeText(line, x, y);
        ctx.fillText(line, x, y);
        y += fontSize * 1.30;
      }}
    }}

    // ★ 下部ヘッダー（左右）
    const footerFont = 200;
    ctx.font = footerFont + "px 'Noto Serif JP','Yu Mincho','serif'";
    ctx.textBaseline = "middle";
    ctx.lineJoin = "round";
    ctx.lineWidth = footerFont * 0.10;
    ctx.strokeStyle = "black";
    ctx.fillStyle = "white";

    // 左側
    if (footerLeft.trim().length > 0) {{
      ctx.textAlign = "left";
      ctx.strokeText(footerLeft, W * 0.15, H * 0.90);
      ctx.fillText(footerLeft, W * 0.15, H * 0.90);
    }}

    // 右側
    if (footerRight.trim().length > 0) {{
      ctx.textAlign = "right";
      ctx.strokeText(footerRight, W * 0.85, H * 0.90);
      ctx.fillText(footerRight, W * 0.85, H * 0.90);
    }}
  }}

  img.onload = function() {{
    drawPoster();
  }};

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
