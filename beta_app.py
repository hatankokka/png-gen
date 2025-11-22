import streamlit as st
import base64
import html
import os
import json
import glob
from PIL import Image
import io
from pathlib import Path
from streamlit.components.v1 import html as st_html

# ★ ここに移動する（重要）
ss = st.session_state

# =========================================================
# フォント定義
# =========================================================
FONT_DIR = "fonts"

FONT_LABELS = {
    "BIZUDMincho-Regular.ttf": "01. MINCHO",
    "UnGungseo.ttf": "02. KOREA FONT",
    "NotoSansJP-Regular.ttf": "03. ALMIGHTY FONT",
    "NotoSansEgyptianHieroglyphs-Regular.ttf": "04. HIEROGLYPH FONT",
}

AA_FONT_FILE = "ms-pgothic-regular.ttf"

FONT_MAP = {label: fname for fname, label in FONT_LABELS.items()}
FONT_LABEL_LIST = list(FONT_LABELS.values())

st.set_page_config(page_title="大判焼外交部ジェネレーター", layout="centered")

# -----------------------------------------------------------
# 翻訳JSONを読み込む関数（上に置く）
# -----------------------------------------------------------
def load_lang_initial_ja():
    with open("languages/ja.json", "r", encoding="utf-8") as f:
        return json.load(f)
        
# -----------------------------------------------------------
# ★ 初回ロード時：session_state を初期化し、ja.json の初期値を読み込む
# -----------------------------------------------------------
if "initialized" not in st.session_state:
    st.session_state.initialized = True

    ja = load_lang_initial_ja()

    st.session_state.main_text = ja["default_main"]
    st.session_state.footer_left = ja["default_footer_left"]
    st.session_state.footer_right = ja["default_footer_right"]
    st.session_state.yellow_words = ja["default_yellow"]
    st.session_state.lang = "ja"
    
    st.session_state.bg_choice = "01"
    


# -----------------------------------------------------------
# 翻訳JSONを読み込む関数
# -----------------------------------------------------------
def load_lang(lang_code):
    with open(f"languages/{lang_code}.json", "r", encoding="utf-8") as f:
        return json.load(f)

# -----------------------------------------------------------
# 言語一覧
# -----------------------------------------------------------
LANG_OPTIONS = {
    "ja": "日本語",
    "en": "English",
    "ko": "한국어",
    "zh_cn": "简体中文",
    "zh_tw": "繁體中文",
    "fr": "Français",
    "es": "Español",
    "de": "Deutsch",
    "it": "Italiano",
    "pt": "Português",
    "ar": "العربية",
    "fa": "فارسی",
    "tl": "Tagalog",
    "th": "ภาษาไทย",
    "mn": "Монгол",
    "vi": "Tiếng Việt",
    "ru": "Русский",
    "he": "עברית",
    "ms": "Bahasa Melayu",
    "egy": "𓂀 Egyptian Hieroglyphs"
}

# -----------------------------------------------------------
# 初期言語設定
# -----------------------------------------------------------
if "lang" not in st.session_state:
    st.session_state.lang = "ja"

current_code = st.session_state.lang

# -----------------------------------------------------------
# ★ 言語辞書の読み込み（タイトルより前に必要）
# -----------------------------------------------------------
T = load_lang(st.session_state.lang)

# -----------------------------------------------------------
# タイトル & 作者
# -----------------------------------------------------------
st.title(T["title"])
st.markdown(T["author"], unsafe_allow_html=True)

# -----------------------------------------------------------
# 言語選択（作者の直下）
# -----------------------------------------------------------
selected_code = st.selectbox(
    "言語 / Language",
    options=list(LANG_OPTIONS.keys()),
    index=list(LANG_OPTIONS.keys()).index(current_code),
    format_func=lambda code: LANG_OPTIONS[code]
)

# ★ 言語変更処理
if selected_code != st.session_state.lang:
    st.session_state.lang = selected_code
    lang_data = load_lang(selected_code)
    st.session_state.main_text = lang_data["default_main"]
    st.session_state.footer_left = lang_data["default_footer_left"]
    st.session_state.footer_right = lang_data["default_footer_right"]
    st.session_state.yellow_words = lang_data["default_yellow"]
    st.rerun()

# -----------------------------------------------------------
# アスキーアート参考リンク
# -----------------------------------------------------------
st.markdown(T["ascii_links"])

# -----------------------------------------------------------
# 注意事項
# -----------------------------------------------------------
st.markdown("### " + T["notice_title"])
st.markdown(T["notice_body"])

# -----------------------------------------------------------
# 同意チェック
# -----------------------------------------------------------
agreed = st.checkbox(T["agree_label"])
if not agreed:
    st.warning(T["agree_warning"])



# =========================================================
# モード選択
# =========================================================
mode_label = st.radio(
    T["mode_select"],
    [T["normal_mode"], T["aa_mode"]]
)

if mode_label == T["normal_mode"]:
    mode_internal = "NORMAL"
else:
    mode_internal = "AA"


# =========================================================
# NGワード読み込み ~ 画像生成全て
# =========================================================
if agreed:

    # =========================================================
    # モード別フォント選択（多言語対応）
    # =========================================================
    if mode_internal == "NORMAL":
        font_choice_label = st.selectbox(T["font_select"], FONT_LABEL_LIST)
        ss.font_choice = FONT_MAP[font_choice_label]
    else:
        ss.font_choice = AA_FONT_FILE

    # ★ここに移動（正しい位置）
    font_path = os.path.join(FONT_DIR, ss.font_choice)
    with open(font_path, "rb") as f:
        font_b64 = base64.b64encode(f.read()).decode()

    # =========================================================
    # Base64変換
    # =========================================================
    font_path = os.path.join(FONT_DIR, ss.font_choice)
    with open(font_path, "rb") as f:
        font_b64 = base64.b64encode(f.read()).decode()

    # =========================================================
    # NGワード読み込み
    # =========================================================
    NG_FILE = ".streamlit/ng_words.txt"
    if os.path.exists(NG_FILE):
        with open(NG_FILE, "r", encoding="utf-8") as f:
            NG_WORDS = [w.strip() for w in f if w.strip()]
    else:
        NG_WORDS = []

    # =========================================================
    # 背景画像（カードUI：画像クリックで選択）
    # =========================================================
    BACKGROUND_CHOICES = {
        Path(p).stem.replace("background", ""): p
        for p in sorted(glob.glob(".streamlit/background*.png"))
    }

    keys = list(BACKGROUND_CHOICES.keys())
    st.markdown("### " + T["background_select"])

    cols = st.columns(3)

    selected = ss.bg_choice if "bg_choice" in ss else keys[0]

    # ---------------------------------------------------------
    # ★ 超軽量：サムネイルを Pillow で動的生成（Base64廃止）
    # ---------------------------------------------------------


    st.markdown("### 背景画像を選択")

    cols = st.columns(3)

    keys = list(BACKGROUND_CHOICES.keys())
    selected = ss.bg_choice if "bg_choice" in ss else keys[0]

    for i, key in enumerate(keys):
        with cols[i % 3]:

            # 選択枠
            border = "3px solid #ff4b4b" if key == selected else "3px solid rgba(0,0,0,0)"

            # ★ フル画像を読み込んで縮小（120px）
            img = Image.open(BACKGROUND_CHOICES[key])
            img_thumb = img.copy()
            img_thumb.thumbnail((120, 200))   # ← ここで小さくする

            # ★ PNGをBase64化（縮小版だから10〜30KB）
            buf = io.BytesIO()
            img_thumb.save(buf, format="PNG")
            thumb_b64 = base64.b64encode(buf.getvalue()).decode()

            # ★ HTMLへ縮小版だけ表示（軽い！）
            st.markdown(
                f"""
                <div style="position:relative; width:120px; margin-bottom:8px;">
                    <img src="data:image/png;base64,{thumb_b64}"
                        style="width:120px; border-radius:8px; border:{border};">
                </div>
                """,
                unsafe_allow_html=True
            )

            # ★ 背景選択ボタン
            if st.button(f"👉 {key}", key=f"bg_btn_{key}"):
                ss.bg_choice = key
                st.rerun()

    # ---------------------------------------------------------
    # ★ 本番背景は従来のフルサイズ Base64（生成用なのでOK）
    # ---------------------------------------------------------
    with open(BACKGROUND_CHOICES[ss.bg_choice], "rb") as f:
        bg_b64_raw = f.read()

    bg_b64 = base64.b64encode(bg_b64_raw).decode()
    bg_b64_safe = html.escape(bg_b64)

 
    # =========================================================
    # 入力欄（本文 / フッター）
    # =========================================================
    ss.main_text = st.text_area(T["main_text"], ss.main_text if "main_text" in ss else "", height=250)
    ss.footer_left = st.text_input(T["footer_left"], ss.footer_left if "footer_left" in ss else "")
    ss.footer_right = st.text_input(T["footer_right"], ss.footer_right if "footer_right" in ss else "")

    # =========================================================
    # 黄色単語
    # =========================================================
    if mode_internal == "NORMAL":
        ss.yellow_words = st.text_area(T["yellow_words"], ss.yellow_words if "yellow_words" in ss else "")
    else:
        ss.yellow_words = ""

    # =========================================================
    # Apply / Reset
    # =========================================================
    col_apply, col_reset = st.columns(2)

    with col_apply:
        if st.button(T["apply"]):
            st.rerun()

    with col_reset:
        if st.button(T["reset"]):
            keep_bg = ss.bg_choice
            keep_font = ss.font_choice if "font_choice" in ss else None
            st.session_state.clear()
            st.session_state.bg_choice = keep_bg
            if keep_font:
                st.session_state.font_choice = keep_font
            st.rerun()

    # =========================================================
    # NGチェック
    # =========================================================
    if mode_internal == "NORMAL":
        found = [ng for ng in NG_WORDS if ng and ng in ss.main_text]
        if found:
            st.error("⚠ NG word → " + ", ".join(found))
            st.stop()

    # =========================================================
    # JSデータ生成
    # =========================================================
    main_js = json.dumps(ss.main_text)
    footer_left_js = json.dumps(ss.footer_left)
    footer_right_js = json.dumps(ss.footer_right)
    yellow_js = "|".join([w.strip() for w in ss.yellow_words.split("\n") if w.strip()])
    mode_js = json.dumps(mode_internal)
    watermark_js = json.dumps(T["watermark"]) 

    # =========================================================
    # ★巨大 JSテンプレート（キャンバス本体）
    # =========================================================
    html_template = """
<style>
@font-face {
    font-family: "customFont";
    src: url("data:font/ttf;base64,{{FONTDATA}}") format("truetype");
}


★★ここまで追加★★

body { margin: 0; padding: 0; }
</style>

<div style="display:flex;flex-direction:column;align-items:center;gap:16px;">

  <button id="saveBtn" style="
      padding:12px 24px;border-radius:999px;border:none;
      background:#4CAF50;color:white;font-weight:700;
      cursor:pointer;font-size:14px;">
    {{SAVE}}
  </button>

  <button id="tweetBtn" style="
      padding:12px 24px;border-radius:999px;border:none;
      background:#1DA1F2;color:white;font-weight:700;
      cursor:pointer;font-size:14px;">
    {{TWEET}}
  </button>

  <canvas id="posterCanvas" style="
      max-width:100%;border-radius:16px;
      box-shadow:0 10px 30px rgba(0,0,0,0.6);"></canvas>
</div>

<script>
const bgData      = "{{BGDATA}}";
const textRaw     = {{MAIN}};
const footerLeft  = {{LEFT}};
const footerRight = {{RIGHT}};
const yellowWords = "{{YELLOW}}".split("|").filter(x=>x.length>0);
const mode        = {{MODE}};
const watermark  = {{WATERMARK}};


const MAX_WIDTH = 1300;
const FONT_MAX = 420;
const FONT_MIN = 40;

let LINE_GAP = (mode === "AA") ? 1.05 : 1.30;

const img = new Image();
img.src = "data:image/png;base64," + bgData;

const canvas = document.getElementById("posterCanvas");
const ctx = canvas.getContext("2d");

img.onload = async function() {
    try {
        await document.fonts.load("30px customFont");

        // 🔥 必須：shaping 完了を待つ
        await document.fonts.ready;

    } catch(e){}
    drawPoster();
};




function drawPoster() {

    const lines = textRaw.split("\\n");

    const origW = img.naturalWidth;
    const origH = img.naturalHeight;

    let scale = (origW > MAX_WIDTH) ? (MAX_WIDTH / origW) : 1.0;
    const W = Math.floor(origW * scale);
    const H = Math.floor(origH * scale);

    canvas.width = W;
    canvas.height = H;

    ctx.drawImage(img, 0, 0, W, H);

    const marginX = W * 0.08;
    const marginTop = H * 0.18;
    const marginBottom = H * 0.20;

    const areaW = W - marginX * 2;
    const areaH = H - marginTop - marginBottom;

    // === バイナリサーチ ===
    function canFit(fontSize) {
        ctx.font = `${fontSize}px customFont, sans-serif`;


        let maxLineWidth = 0;
        for (const line of lines) {
            const w = ctx.measureText(line).width;
            if (w > maxLineWidth) maxLineWidth = w;
        }
        const totalHeight = lines.length * fontSize * LINE_GAP;
        return (maxLineWidth <= areaW) && (totalHeight <= areaH);
    }

    let low = FONT_MIN, high = FONT_MAX, best = FONT_MIN;
    while (low <= high) {
        const mid = Math.floor((low + high) / 2);
        if (canFit(mid)) { best = mid; low = mid + 1; }
        else { high = mid - 1; }
    }

    let fontSize = best;

    // === モード別補正 ===
    if (mode === "AA") {
        const lineCount = lines.length;
        const maxLen = Math.max(...lines.map(x => x.length), 0);
        const K_line = 1 / (1 + 0.015 * Math.max(lineCount - 3, 0));
        const K_len  = 1 / (1 + 0.015 * Math.max(maxLen - 20, 0));
        fontSize = best * K_line * K_len * 1.50;
    } else {
        const lineCount = lines.length;
        const maxLen = Math.max(...lines.map(x => x.length), 0);
        const K_line = 1 / (1 + 0.010 * Math.max(lineCount - 3, 0));
        const K_len  = 1 / (1 + 0.010 * Math.max(maxLen - 10, 0));
        fontSize = best * K_line * K_len;
    }
    if (fontSize < 10) fontSize = 10;

    // ★ フォントに Devanagari/Tamil のフォールバックを追加
    ctx.font = `${fontSize}px customFont, sans-serif`;
    ctx.textBaseline = "middle";

    const totalTextHeight = lines.length * fontSize * LINE_GAP;
    let currentY = marginTop + (areaH - totalTextHeight) / 2 + fontSize * 0.5;

    function drawColoredLine(line, centerX, y) {
        // ★ ここも同じフォント設定に修正
        ctx.font = `${fontSize}px customFont, sans-serif`;

        if (mode === "AA") {
            ctx.fillStyle = "white";
            ctx.textAlign = "left";
            ctx.fillText(line, marginX, y);
            return;
        }

        let segs = [];

        // Unicode-safe glyph 分割
        const glyphs = Array.from(line);
        let pos = 0;

        while (pos < glyphs.length) {
            let matched = false;

            // 黄色語の一致判定も Unicode-safe にする
            for (const w of yellowWords) {
                if (!w) continue;

                const wGlyphs = Array.from(w);
                const slice = glyphs.slice(pos, pos + wGlyphs.length).join("");

                if (slice === w) {
                    segs.push({ text: w, yellow: true });
                    pos += wGlyphs.length;
                    matched = true;
                    break;
                }
            }

            if (!matched) {
                segs.push({ text: glyphs[pos], yellow: false });
                pos++;
            }
        }


        let totalW = 0;
        for (const seg of segs) totalW += ctx.measureText(seg.text).width;

        let cursorX = centerX - totalW / 2;
        for (const seg of segs) {
            ctx.fillStyle = seg.yellow ? "#FFD700" : "white";
            ctx.fillText(seg.text, cursorX, y);
            cursorX += ctx.measureText(seg.text).width;
        }
    }

    for (const line of lines) {
        drawColoredLine(line, W * 0.5, currentY);
        currentY += fontSize * LINE_GAP;
    }

    const footerY = H * 0.90;
    const footerFont = Math.max(22, Math.floor(H * 0.035));
    ctx.font = `${footerFont}px customFont, sans-serif`;
    ctx.fillStyle = "white";
    ctx.textAlign = "left";
    ctx.fillText(footerLeft, W * 0.06, footerY);
    ctx.textAlign = "right";
    ctx.fillText(footerRight, W * 0.94, footerY);
    
    ctx.font = `${footerFont}px customFont, sans-serif`;
    ctx.fillStyle = "white";

    ctx.textAlign = "left";
    ctx.fillText(footerLeft, W * 0.06, footerY);

    ctx.textAlign = "right";
    ctx.fillText(footerRight, W * 0.94, footerY);

    // === Watermark（右上 / footer の半分サイズ） ===
    const watermarkFont = Math.floor(footerFont * 0.5);
    ctx.font = `${watermarkFont}px customFont, sans-serif`;
    ctx.fillStyle = "rgba(255,255,255,0.85)";
    ctx.textAlign = "right";
    ctx.fillText(watermark, W * 0.97, H * 0.07);
}

document.getElementById("saveBtn").onclick = function() {
    canvas.toBlob(function(blob){
        if (!blob) return;
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url; a.download = "generated.jpg";
        document.body.appendChild(a); a.click();
        setTimeout(()=>{ URL.revokeObjectURL(url); a.remove(); }, 400);
    }, "image/jpeg", 0.90);
};

document.getElementById("tweetBtn").onclick = function() {
    const text = encodeURIComponent({{TWEET_TEXT}});
    window.open("https://twitter.com/intent/tweet?text=" + text, "_blank");
};
</script>
"""
    
    # ★ Devanagari / Tamil フォント埋め込み
    html_template = html_template.replace("{{FONTDATA_DEV}}", fontdata_dev)
    html_template = html_template.replace("{{FONTDATA_TA}}", fontdata_ta)

    # =========================================================
    # SAVE / TWEET / TWEET_TEXT の置換 ※ここが if agreed の中に必要！
    # =========================================================
    html_template = html_template.replace("{{SAVE}}", T["save"])
    html_template = html_template.replace("{{TWEET}}", T["tweet"])
    tweet_template_js = json.dumps(T["tweet_template"])
    html_template = html_template.replace("{{TWEET_TEXT}}", tweet_template_js)

    # =========================================================
    # ★最終 HTML生成 ※これも if agreed の中！
    # =========================================================
    html_final = (
        html_template
            .replace("{{MAIN}}", main_js)
            .replace("{{LEFT}}", footer_left_js)
            .replace("{{RIGHT}}", footer_right_js)
            .replace("{{YELLOW}}", yellow_js)
            .replace("{{FONTDATA}}", font_b64)
            .replace("{{BGDATA}}", bg_b64_safe)
            .replace("{{MODE}}", mode_js)
            .replace("{{WATERMARK}}", watermark_js)
    )

    st_html(html_final, height=1050, scrolling=True)




























