#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import io
import urllib.parse

st.set_page_config(page_title="画像ジェネレーター", layout="centered")
st.title("🖼 固定背景テキストジェネレーター（PNG版）")

# ▼ 入力欄
text = st.text_area("テキストを入力（自動縮小します）")

# ▼ フォント設定
font_size_max = 80
font_size_min = 10
font_path = os.path.join("fonts", "BIZUDMincho-Medium.ttf")

# ▼ 背景PNG（固定）
bg = Image.open("background.png").convert("RGBA")
W, H = bg.size

# ▼ 自動フォント縮小関数
def auto_shrink(text, draw, font_path, max_w, max_h, max_size, min_size):
    size = max_size
    while size >= min_size:
        font = ImageFont.truetype(font_path, size)
        bbox = draw.multiline_textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        if w <= max_w and h <= max_h:
            return font
        size -= 2
    return ImageFont.truetype(font_path, min_size)

# ▼ 文字入力がある場合のみ処理
if text:

    # 編集用画像コピー
    img = bg.copy()
    draw = ImageDraw.Draw(img)

    # テキストを収める最大エリア
    max_w = W * 0.85
    max_h = H * 0.60

    # 自動縮小フォント取得
    font = auto_shrink(text, draw, font_path, max_w, max_h, font_size_max, font_size_min)

    # サイズ計算
    bbox = draw.multiline_textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    x = int((W - text_w) / 2)
    y = int((H - text_h) / 2)

    # ▼ 縁取り付き文字描画
    def draw_outline(draw, x, y, t, font):
        for ox in range(-3, 4):
            for oy in range(-3, 4):
                draw.multiline_text((x + ox, y + oy), t, font=font, fill="#000000")
        draw.multiline_text((x, y), t, font=font, fill="#FFFFFF")

    draw_outline(draw, x, y, text, font)

    # 表示
    st.image(img)

    # ▼ ダウンロード
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.download_button("画像をダウンロード", buf.getvalue(), "output.png", "image/png")

    # ▼ X投稿ボタン（投稿文なし）
    tweet_url = "https://twitter.com/intent/tweet"
    st.markdown(
        f"""
        <a href="{tweet_url}" target="_blank">
            <button style="
                padding: 12px 20px;
                font-size: 20px;
                background-color: #1DA1F2;
                color: white;
                border-radius: 8px;
                border: none;
                cursor: pointer;
            ">
                X に投稿する
            </button>
        </a>
        """,
        unsafe_allow_html=True
    )

