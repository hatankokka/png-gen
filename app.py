import streamlit as st
import cv2
import numpy as np
import io
import os

st.set_page_config(page_title="外交部ジェネレーター", layout="centered")
st.title("外交部風 画像ジェネレーター（OpenCV版 / Pillow不使用）")

# ========= 入力欄 =========
main_text = st.text_area("本文（最大600px・自動縮小）", "")
footer_text = st.text_input("下のヘッダー（署名・日付・200px固定）", "")

# ========= 背景PNG =========
BG_PATH = "background.png"
if not os.path.exists(BG_PATH):
    st.error(f"{BG_PATH} が見つかりません。")
    st.stop()

bg = cv2.imread(BG_PATH, cv2.IMREAD_UNCHANGED)
if bg is None:
    st.error(f"{BG_PATH} の読み込みに失敗しました。")
    st.stop()

# BG を BGRA に変換（透明対応）
if bg.shape[2] == 3:
    bg = cv2.cvtColor(bg, cv2.COLOR_BGR2BGRA)

H, W = bg.shape[:2]

# ========= フォント設定 =========
# ⬇⬇⬇ ルート直下に置かれたフォントを使用
FONT_PATH = "BIZUDMincho-Regular.ttf"

if not os.path.exists(FONT_PATH):
    st.error(f"フォントファイルが見つかりません: {FONT_PATH}")
    st.stop()

# FreeType 読み込み（OpenCVの日本語描画用）
try:
    ft = cv2.freetype.createFreeType2()
    ft.loadFontData(FONT_PATH, 0)
except Exception as e:
    st.error("OpenCV FreeType モジュールが利用できません。")
    st.write(e)
    st.stop()

FONT_MAIN_MAX = 600
FONT_MAIN_MIN = 150
FONT_FOOTER = 200

# ========= 本文描画エリア =========
CENTER_TOP    = int(H * 0.28)
CENTER_BOTTOM = int(H * 0.70)
CENTER_LEFT   = int(W * 0.10)
CENTER_RIGHT  = int(W * 0.90)

CENTER_W = CENTER_RIGHT - CENTER_LEFT
CENTER_H = CENTER_BOTTOM - CENTER_TOP

# ========= テキスト描画用関数 =========

def draw_text(img, text, x, y, font_size, color=(255,255,255), outline=8):
    """縁取り（アウトライン）文字を描画"""
    for ox in range(-outline, outline+1):
        for oy in range(-outline, outline+1):
            ft.putText(img, text, (x+ox, y+oy), font_size,
                       (0,0,0), thickness=-1, line_type=cv2.LINE_AA)
    ft.putText(img, text, (x, y), font_size,
               color, thickness=-1, line_type=cv2.LINE_AA)


def wrap_text(text, font_size, max_width):
    """文字幅に合わせて改行する処理（1文字ずつ判定）"""
    lines = []
    cur = ""
    for ch in text:
        size, _ = ft.getTextSize(cur + ch, font_size, thickness=-1)
        if size[0] <= max_width:
            cur += ch
        else:
            lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    return lines


def autoshrink(text, max_w, max_h):
    """本文のフォント自動縮小"""
    size = FONT_MAIN_MAX
    while size >= FONT_MAIN_MIN:
        lines = wrap_text(text, size, max_w)
        total_height = len(lines) * int(size * 1.3)
        max_line_w = max(ft.getTextSize(line, size, thickness=-1)[0][0] for line in lines)

        if total_height <= max_h and max_line_w <= max_w:
            return size, lines

        size -= 15

    return FONT_MAIN_MIN, wrap_text(text, FONT_MAIN_MIN, max_w)

# ================= 描画処理 =================

if main_text:
    img = bg.copy()

    # ---- 本文 ----
    font_size, lines = autoshrink(main_text, CENTER_W, CENTER_H)
    total_height = int(len(lines) * font_size * 1.3)
    y_start = CENTER_TOP + (CENTER_H - total_height) // 2

    for i, line in enumerate(lines):
        line_w, _ = ft.getTextSize(line, font_size, thickness=-1)
        x = CENTER_LEFT + (CENTER_W - line_w[0]) // 2
        y = int(y_start + i * font_size * 1.3)
        draw_text(img, line, x, y, font_size)

    # ---- ヘッダー ----
    if footer_text:
        footer_w, _ = ft.getTextSize(footer_text, FONT_FOOTER, thickness=-1)
        x = (W - footer_w[0]) // 2
        y = int(H * 0.90)
        draw_text(img, footer_text, x, y, FONT_FOOTER, outline=5)

    # BGR(A) → RGBA
    preview = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
    st.image(preview)

    # ---- ダウンロード ----
    buf = io.BytesIO()
    _, enc = cv2.imencode(".png", cv2.cvtColor(preview, cv2.COLOR_RGBA2BGRA))
    buf.write(enc.tobytes())

    st.download_button("画像をダウンロード", buf.getvalue(),
                       "output.png", "image/png")
