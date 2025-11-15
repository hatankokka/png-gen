import streamlit as st
from PIL import Image
import io
import os

st.set_page_config(page_title="PNG Generator", layout="wide")

st.title("PNG Generator - 背景画像選択ツール")

# --- 背景画像の読み込み（ローカル or GitHub repository 内） ---
def load_local_backgrounds(folder="backgrounds"):
    """ローカルフォルダから背景画像一覧を読み込む"""
    if not os.path.exists(folder):
        return []
    files = [f for f in os.listdir(folder) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    return files

# 背景画像フォルダ（→ GitHub では /backgrounds に入れておく）
local_backgrounds = load_local_backgrounds("backgrounds")

st.sidebar.header("背景画像の選択")

# --- 1. ローカルフォルダから選ぶ ---
selected_local = None
if local_backgrounds:
    selected_local = st.sidebar.selectbox(
        "リポジトリ内の背景画像を選択",
        ["（選択しない）"] + local_backgrounds
    )

# --- 2. アップロードして選ぶ ---
uploaded_file = st.sidebar.file_uploader(
    "または画像をアップロード（PNG/JPG）", 
    type=["png", "jpg", "jpeg"]
)

# --- 画像の決定 ---
bg_image = None

if uploaded_file:
    bg_image = Image.open(uploaded_file)
    st.sidebar.success("アップロードされた画像を使用します")
elif selected_local and selected_local != "（選択しない）":
    bg_image = Image.open(f"backgrounds/{selected_local}")
    st.sidebar.success(f"ローカル背景画像: {selected_local} を使用します")
else:
    st.sidebar.warning("背景画像が選択されていません")

# --- 画像を表示 ---
if bg_image:
    st.subheader("背景画像プレビュー")
    st.image(bg_image, caption="選択中の背景画像", use_column_width=True)

# --- ここから下にあなたの加工ロジックを追加 ---
st.markdown("---")
st.subheader("ここに加工コードや文字入れ処理を追加可能")

st.write("たとえば、背景画像にテキストを合成したり、生成された PNG をダウンロードさせることができます。")

# 例：PNG 出力ボタン
if bg_image:
    buffer = io.BytesIO()
    bg_image.save(buffer, format="PNG")
    st.download_button(
        label="この画像をPNGとしてダウンロード",
        data=buffer.getvalue(),
        file_name="generated.png",
        mime="image/png"
    )
