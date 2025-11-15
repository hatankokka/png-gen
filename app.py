import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import io

st.set_page_config(page_title="PNG 文字入れツール", layout="wide")
st.title("PNG 文字入れツール（.streamlit 内の画像を使用）")

# ------------------------------
# PNG を置いているフォルダ
# ------------------------------
IMAGE_FOLDER = ".streamlit"

# ------------------------------
# PNG一覧を取得
# ------------------------------
png_files = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(".png")]

if not png_files:
    st.error(".streamlit フォルダに PNG を入れてください。")
    st.stop()

# ------------------------------
# PNG を選択
# ------------------------------
selected_png = st.selectbox("画像を選んでください（.streamlit 内）", png_files)

# 画像読み込み
image_path = os.path.join(IMAGE_FOLDER, selected_png)
base_image = Image.open(image_path).convert("RGBA")

# ------------------------------
# テキスト入力
# ------------------------------
text = st.text_input("画像に載せる文字を入力", "サンプル文字")
font_size = st.slider("文字サイズ", 20, 200, 60)
x = st.number_input("文字位置 X", 0, base_image.width, 50)
y = st.number_input("文字位置 Y", 0, base_image.height, 50)

# ------------------------------
# 文字合成
# ------------------------------
img = base_image.copy()
draw = ImageDraw.Draw(img)

# Streamlit デプロイの場合、標準フォントを使用
font = ImageFont.load_default()

draw.text((x, y), text, fill="white", font=font)

# ------------------------------
# 表示
# ------------------------------
st.subheader("プレビュー")
st.image(img, use_column_width=True)

# ------------------------------
# ダウンロード
# ------------------------------
buf = io.BytesIO()
img.save(buf, format="PNG")
st.download_button(
    "この画像をダウンロード",
    buf.getvalue(),
    file_name="output.png",
    mime="image/png"
)
