import streamlit as st
from PIL import Image
import os

st.set_page_config(page_title="PNG Selector", layout="wide")
st.title("PNG セレクター（リポジトリ内の画像から選択）")

# ------------------------------
# 画像フォルダの場所（あなたのリポジトリに合わせて変更）
# ------------------------------
IMAGE_FOLDER = "images"   # 例: /images に png を置く

# ------------------------------
# フォルダ内のPNGファイル一覧を取得
# ------------------------------
def get_png_files(folder):
    if not os.path.exists(folder):
        return []
    return [
        f for f in os.listdir(folder)
        if f.lower().endswith(".png")
    ]

png_files = get_png_files(IMAGE_FOLDER)

if not png_files:
    st.error(f"フォルダ '{IMAGE_FOLDER}' に PNG がありません。配置してください。")
    st.stop()

# ------------------------------
# PNG を選択（プルダウン）
# ------------------------------
selected_png = st.selectbox(
    "画像を選択してください：",
    png_files
)

# ------------------------------
# 選択された画像を読み込む
# ------------------------------
image_path = os.path.join(IMAGE_FOLDER, selected_png)
image = Image.open(image_path)

# ------------------------------
# 画像プレビュー
# ------------------------------
st.subheader("選択された画像")
st.image(image, use_column_width=True)

# ------------------------------
# PNG ダウンロード
# ------------------------------
with open(image_path, "rb") as f:
    st.download_button(
        label="この PNG をダウンロード",
        data=f,
        file_name=selected_png,
        mime="image/png"
    )
