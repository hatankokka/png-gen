# 大判焼外交部ジェネレーター ver.2.0

北朝鮮風のプロパガンダ調レイアウトで  
**大判焼・今川焼・回転焼問題を題材にしたパロディ画像**  
を生成できる Streamlit アプリです。

> ⚠ 本アプリは **娯楽目的のパロディ生成ツール** であり、  
> 実在の個人・団体とは一切関係ありません。

---

##主な機能

- 背景画像の選択（4種類）
- 本文テキスト入力
- 黄色強調語（ハイライトワード）の指定
- 日付・署名の入力
- **カスタムフォント対応（明朝 / 韓国フォント UnGungseo）**
- 文字サイズの自動調整（背景ごとに最適化）
- PNG → JPEG 保存機能
- X（旧 Twitter）投稿リンクボタン
- NGワードフィルタ（`.streamlit/ng_words.txt`）

---

##使用フォント

- **BIZ UD明朝**
- **UnGungseo.ttf**  
  韓国の標語風の雰囲気を出すために利用しています。

これらは `fonts/` ディレクトリに置き、アプリ内部で Base64 化して HTML に埋め込み表示します。

---

##技術構成

- **Python / Streamlit**
- HTML5 Canvas（テキスト描画 + 背景合成）
- JavaScript による画像生成（JPEG 出力）
- カスタムフォントの Base64 埋め込み
- `st.session_state` による状態保持
- NG ワードチェック機能

背景画像は `.streamlit/backgroundXX.png` に配置します。

---

##ローカルでの起動方法

```bash
pip install streamlit
streamlit run app.py
