import streamlit as st
import base64
import html
import os
from streamlit.components.v1 import html as st_html

st.set_page_config(page_title="外交部ジェネレーター", layout="centered")
st.title("外交部風 画像ジェネレーター（Canvas版 / 画像処理なし）")

# ▼ 入力欄
main_text = st.text_area("本文（複数行OK・改行はそのまま反映されます）", "")
footer_text = st.text_input("下のヘッダー（署名・日付など）", "")

# ▼ 背景画像を base64 でエンコード
BG_PATH = "background.png"
if not os.path.exists(BG_PATH):
    st.error("background.png が見つかりません（リポジトリ直下に置いてください）。")
    st.stop()

with open(BG_PATH, "rb") as f:
    bg_b64 = base64.b64encode(f.read()).decode("utf-8")

# ▼ JS に渡すためにエスケープ
main_text_js = html.escape(main_text).replace("\n", "\\n")
footer_text_js = html.escape(footer_text).replace("\n", "\\n")

# ▼ HTML + JS（Canvasで合成してダウンロードもできる）
canvas_html = f"""
<div style="display:flex;flex-direction:column;align-items:center;gap:12px;">
  <div>
    <button id="downloadBtn"
      style="
        padding:8px 16px;
        border-radius:999px;
        border:none;
        background:#f7d48b;
        color:#3b2409;
        font-weight:600;
        letter-spacing:0.08em;
        cursor:pointer;">
      画像をダウンロード
    </button>
  </div>
  <canvas id="posterCanvas" style="max-width:100%;height:auto;border-radius:12px;box-shadow:0 12px 30px rgba(0,0,0,0.5);"></canvas>
</div>

<script>
  const mainTextRaw = "{main_text_js}".replace(/\\\\n/g, "\\n");
  const footerTextRaw = "{footer_text_js}".replace(/\\\\n/g, "\\n");

  const img = new Image();
  img.src = "data:image/png;base64,{bg_b64}";

  const canvas = document.getElementById("posterCanvas");
  const ctx = canvas.getContext("2d");

  function drawPoster() {{
    const W = img.naturalWidth;
    const H = img.naturalHeight;
    canvas.width = W;
    canvas.height = H;

    // 背景
    ctx.clearRect(0,0,W,H);
    ctx.drawImage(img, 0, 0, W, H);

    const mainText = mainTextRaw || "";
    const footerText = footerTextRaw || "";

    // レイアウト（Python版と同じ比率にしている）
    const top = H * 0.28;
    const bottom = H * 0.70;
    const left = W * 0.10;
    const right = W * 0.90;
    const areaW = right - left;
    const areaH = bottom - top;

    // ===== 本文 =====
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
      const totalH = lines.length * fontPx * 1.3;
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

      const {{maxLineW, totalH}} = measure(fontSize);
      let y = top + (areaH - totalH) / 2 + fontSize * 0.5;

      // 縁取り＋白文字
      for (const line of lines) {{
        const x = left + areaW / 2;
        ctx.font = fontSize + "px 'Noto Serif JP','Yu Mincho','serif'";
        ctx.lineWidth = fontSize * 0.12;  // 縁取りの太さ
        ctx.strokeStyle = "rgba(0,0,0,1)";
        ctx.fillStyle = "rgba(255,255,255,1)";
        ctx.strokeText(line, x, y);
        ctx.fillText(line, x, y);
        y += fontSize * 1.3;
      }}
    }}

    // ===== ヘッダー（署名・日付） =====
    if (footerText.trim().length > 0) {{
      const footerFont = 200;
      ctx.font = footerFont + "px 'Noto Serif JP','Yu Mincho','serif'";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.lineJoin = "round";
      ctx.lineWidth = footerFont * 0.10;
      ctx.strokeStyle = "rgba(0,0,0,1)";
      ctx.fillStyle = "rgba(255,255,255,1)";

      const x = W / 2;
      const y = H * 0.90;   // 画面下 90% の位置
      ctx.strokeText(footerText, x, y);
      ctx.fillText(footerText, x, y);
    }}
  }}

  img.onload = function() {{
    drawPoster();
  }};

  // ダウンロード
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

# Streamlit に埋め込み
# height は適当に大きめにしておく（A0縦でも収まるように）
st_html(canvas_html, height=900, scrolling=True)
