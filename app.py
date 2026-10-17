import os
import sys
import zipfile
import shutil
import tempfile
import traceback
import ssl
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import streamlit as st
from docx import Document
from converters import get_available_converters, get_converter

# Keep the same English-detection and conversion logic from the original Flask app.
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


try:
    for resource in ["punkt", "punkt_tab", "words", "stopwords"]:
        try:
            if resource == "punkt_tab":
                nltk.data.find("tokenizers/punkt_tab")
            elif resource == "punkt":
                nltk.data.find("tokenizers/punkt")
            else:
                nltk.data.find(f"corpora/{resource}")
        except LookupError:
            nltk.download(resource, quiet=True)
    from nltk.corpus import words, stopwords
    ENGLISH_VOCAB = set(words.words()).union(set(stopwords.words("english")))
except Exception:
    ENGLISH_VOCAB = {
        "the", "be", "to", "of", "and", "a", "in", "that", "have", "i", "it", "for", "not", "on", "with",
        "he", "as", "you", "do", "at", "this", "but", "his", "by", "from", "they", "we", "say", "her",
        "she", "or", "an", "will", "my", "one", "all", "would", "there", "their", "what", "so", "up",
        "out", "if", "about", "who", "get", "which", "go", "me", "when", "make", "can", "like", "time",
        "no", "just", "him", "know", "take", "people", "into", "year", "your", "good", "some", "could",
        "them", "see", "other", "than", "then", "now", "look", "only", "come", "its", "over", "think",
        "also", "back", "after", "use", "two", "how", "our", "work", "first", "well", "way", "even",
        "new", "want", "because", "any", "these", "give", "day", "most", "us", "is", "are", "was", "were"
    }

sys.setrecursionlimit(10000)

ENGLISH_FONTS = {
    'arial', 'calibri', 'times new roman', 'courier new', 'georgia',
    'verdana', 'tahoma', 'trebuchet ms', 'segoe ui', 'helvetica',
    'garamond', 'cambria', 'consolas', 'impact', 'century gothic', 'myriad pro'
}

BIJOY_MARKER_CHARS = set("‡‰ˆþÏØÜÝÞßáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ Žž ¾¼")

BIJOY_EXPLICIT_TOKENS = {
    "xd", "xydy", "rm", "d", "dþ", "d«", "d", "z", "u", "r", "q", "e", "a", "b", "c", "p", "s",
}

# ==============================================================================
# PHRASE STREAM BOUNDARY DETECTION
# ==============================================================================
def is_genuine_english_word(word):
    clean = word.lower().strip(".,!?:;\"'()[]{}<>-")
    if not clean:
        return False

    if clean in BIJOY_EXPLICIT_TOKENS:
        return False

    if any(c in BIJOY_MARKER_CHARS for c in clean):
        return False

    if clean.replace('.', '').replace('-', '').isnumeric():
        return True

    if clean in ENGLISH_VOCAB:
        return True

    return False


def convert_phrase_stream(full_text, converter_engine, keep_english=True):
    if not full_text:
        return full_text

    if not keep_english:
        return converter_engine.convert_phrase(full_text)

    tokens = re.findall(r'\S+|\s+', full_text)

    phrases = []
    current_phrase = []
    current_is_english = None

    for token in tokens:
        if token.isspace():
            current_phrase.append(token)
            continue

        token_is_english = is_genuine_english_word(token)

        if current_is_english is None:
            current_is_english = token_is_english
            current_phrase.append(token)
        elif token_is_english == current_is_english:
            current_phrase.append(token)
        else:
            phrases.append(("".join(current_phrase), current_is_english))
            current_phrase = [token]
            current_is_english = token_is_english

    if current_phrase:
        phrases.append(("".join(current_phrase), current_is_english))

    output = []
    for phrase_text, is_eng in phrases:
        if is_eng:
            output.append(phrase_text)
        else:
            output.append(converter_engine.convert_phrase(phrase_text))

    res = "".join(output)
    res = re.sub(r'([ক-হয়ড়ঢ়ৎ])\s+গু\s+([ক-হয়ড়ঢ়ৎ])', r'\1 = \2', res)
    return res


def process_paragraph_docx(paragraph, target_font, converter_engine, keep_english):
    if not paragraph.text or not paragraph.text.strip():
        return

    full_text = paragraph.text
    converted_full = convert_phrase_stream(full_text, converter_engine, keep_english)

    if converted_full != full_text:
        runs = paragraph.runs
        if runs:
            runs[0].text = converted_full
            runs[0].font.name = target_font
            for r in runs[1:]:
                r.text = ""


def process_docx(input_path, output_path, target_font, converter_engine, keep_english):
    doc = Document(input_path)

    for paragraph in doc.paragraphs:
        process_paragraph_docx(paragraph, target_font, converter_engine, keep_english)

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    process_paragraph_docx(paragraph, target_font, converter_engine, keep_english)

    doc.save(output_path)


def process_idml(input_path, output_path, target_font, converter_engine=None, keep_english=True):
    extract_dir = input_path + "_extracted"
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)

    with zipfile.ZipFile(input_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

    stories_dir = os.path.join(extract_dir, 'Stories')

    if os.path.exists(stories_dir):
        for story_file in os.listdir(stories_dir):
            if story_file.endswith('.xml'):
                file_path = os.path.join(stories_dir, story_file)
                try:
                    tree = ET.parse(file_path)
                    root = tree.getroot()
                    modified = False

                    for range_elem in root.iter():
                        if range_elem.tag.endswith('CharacterStyleRange'):
                            applied_language = range_elem.attrib.get('AppliedLanguage', '').lower()
                            applied_font = range_elem.attrib.get('AppliedFont', '').lower()

                            if keep_english and ('english' in applied_language or any(f in applied_font for f in ENGLISH_FONTS)):
                                continue

                            for content_elem in range_elem.iter():
                                if content_elem.tag.endswith('Content') and content_elem.text:
                                    original_text = content_elem.text
                                    converted_text = convert_phrase_stream(original_text, converter_engine, keep_english)
                                    if converted_text != original_text:
                                        content_elem.text = converted_text
                                        modified = True

                            if modified:
                                range_elem.attrib['AppliedFont'] = target_font
                                range_elem.attrib['Composer'] = '$ID/HL Composer Engine'

                    if modified:
                        tree.write(file_path, encoding='utf-8', xml_declaration=True)

                except ET.ParseError:
                    continue

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_out:
        for folder_name, subfolders, filenames in os.walk(extract_dir):
            for filename in filenames:
                filepath = os.path.join(folder_name, filename)
                arcname = os.path.relpath(filepath, extract_dir)

                if filename == 'mimetype':
                    zip_out.write(filepath, arcname, compress_type=zipfile.ZIP_STORED)
                else:
                    zip_out.write(filepath, arcname)

    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)




# ----------------------------- Streamlit UI ----------------------------------
st.set_page_config(
    page_title="Bangla Haraf | ANSI to Unicode Converter",
    page_icon="🔤",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
}
@import url('https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800&display=swap');
:root { --ink:#172554; --blue:#3156d9; --violet:#6d45d9; }
.stApp {
  background:
    radial-gradient(ellipse at 8% 0%, rgba(99,102,241,.15), transparent 34%),
    radial-gradient(ellipse at 100% 8%, rgba(14,165,233,.12), transparent 28%),
    #f5f7fc;
  color: #172033;
  font-family: Inter, 'Hind Siliguri', sans-serif;
}
.block-container { max-width: 860px; padding-top: 2.2rem; padding-bottom: 2.5rem; }
.hero {
  background: linear-gradient(125deg, #172554 0%, #3730a3 52%, #6d45d9 100%);
  border-radius: 25px; padding: 28px 30px 26px; color: white;
  box-shadow: 0 18px 48px rgba(49, 46, 129, .22); margin-bottom: 22px;
  position: relative; overflow: hidden;
}
.hero:after { content:'অ আ ক খ'; position:absolute; right:18px; bottom:-12px;
  font-family:'Hind Siliguri',sans-serif; font-size:46px; font-weight:700;
  color:rgba(255,255,255,.10); letter-spacing:5px; }
.eyebrow { text-transform:uppercase; letter-spacing:2px; font-size:11px;
  font-weight:800; color:#c7d2fe; margin-bottom:9px; }
.hero h1 { font-size:clamp(25px,4vw,36px); line-height:1.15; margin:0 0 10px;
  color:white; font-weight:800; }
.hero p { margin:0; max-width:610px; color:#e0e7ff; font-size:14px; line-height:1.7; }
.panel {
  background:rgba(255,255,255,.94); border:1px solid #e4e8f2;
  border-radius:20px; padding:22px 24px; margin-bottom:16px;
  box-shadow:0 7px 25px rgba(26, 42, 85, .045);
}
.panel-title { font-size:16px; font-weight:800; color:#1e2a54; margin-bottom:4px; }
.panel-sub { color:#73809a; font-size:12px; margin-bottom:17px; }
div[data-testid="stFileUploader"] section { border:1.5px dashed #aab8e9;
  border-radius:15px; background:#f8faff; }
div[data-testid="stFileUploader"] section small { color:#64748b; }
.stButton > button, .stDownloadButton > button {
  border:0; border-radius:12px; min-height:46px; font-weight:700;
  background:linear-gradient(100deg,#3156d9,#7047dc); color:white;
  box-shadow:0 7px 16px rgba(79,70,229,.18); transition:transform .15s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
  color:white; transform:translateY(-1px); border:0;
}
div[data-baseweb="select"] > div { border-radius:11px; border-color:#dce2f0; }
div[data-testid="stCheckbox"] { background:#f7f8ff; padding:12px 14px; border-radius:12px; }
.note { background:#eef2ff; color:#39477a; padding:12px 14px; border-radius:12px;
  font-size:12px; line-height:1.6; border:1px solid #dfe5ff; }
.footer { text-align:center; color:#8791a8; font-size:12px; padding:14px 0 4px; }
.footer a { color:#4f46e5; font-weight:700; text-decoration:none; }
hr { border-color:#e7eaf2; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>ANSI → Unicode<br>Document Converter</h1>
  <p>Convert All Old ANSI Bengali text in Microsoft Word and InDesign documents to standard Unicode Bengali.</p>
</div>
""", unsafe_allow_html=True)

try:
    converter_names = get_available_converters()
except Exception as exc:
    st.error("Could not load converter versions. Check that your existing `converters` module/package is in the same project folder.")
    st.code(str(exc))
    st.stop()

with st.container():
    st.markdown('<div class="panel-title">📤 Upload your document</div><div class="panel-sub">Supported formats: Microsoft Word (.docx) and Adobe InDesign (.idml)</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Choose a .docx or .idml file",
        type=["docx", "idml"],
        help="Your original file is not modified. A converted copy will be created for download.",
    )

    left, right = st.columns(2, gap="medium")
    with left:
        mapping_version = st.selectbox(
            "Converter / mapping version",
            options=converter_names,
            help="Select the mapping version available in your converters module.",
        )
    with right:
        target_font = st.selectbox(
            "Target Bengali font",
            options=["Vrinda", "Kalpurush", "Shonar Bangla"],
            index=1,
        )

    keep_english = st.checkbox(
        "Keep detected English words and punctuation unchanged",
        value=True,
        help="English detection follows the vocabulary and ANSI marker rules in your original app. Review mixed-language documents after conversion.",
    )

    st.markdown('<div class="note">Tip: If English words are being converted incorrectly, try switching this option off/on and compare the output. Complex InDesign layouts should always be checked in InDesign after conversion.</div>', unsafe_allow_html=True)
    st.write("")
    convert_clicked = st.button("✨ Convert document", use_container_width=True)

if convert_clicked and uploaded is not None:
    ext = Path(uploaded.name).suffix.lower()
    if ext not in {".docx", ".idml"}:
        st.error("Unsupported file type. Please upload a .docx or .idml file.")
        st.stop()

    converter_engine = get_converter(mapping_version)
    safe_name = Path(uploaded.name).name
    output_filename = f"Unicode_{safe_name}"

    with st.spinner("Converting your document…"):
        temp_dir = tempfile.mkdtemp(prefix="banglaharaf_converter_")
        input_path = os.path.join(temp_dir, safe_name)
        output_path = os.path.join(temp_dir, output_filename)
        try:
            with open(input_path, "wb") as f:
                f.write(uploaded.getvalue())

            if ext == ".docx":
                process_docx(input_path, output_path, target_font, converter_engine, keep_english)
            else:
                process_idml(input_path, output_path, target_font, converter_engine, keep_english)

            with open(output_path, "rb") as f:
                converted_bytes = f.read()

            st.success("Conversion completed. Your original document has not been changed.")
            st.markdown("**Converted file**")
            st.write(f"📄 `{output_filename}`")
            st.download_button(
                label="⬇️ Download converted document",
                data=converted_bytes,
                file_name=output_filename,
                mime=("application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                      if ext == ".docx" else "application/vnd.adobe.indesign-idml-package"),
                use_container_width=True,
            )
            st.caption("Please proofread Bengali conjuncts, matras, and mixed English/Bengali text before publishing.")
        except Exception as exc:
            st.error("Conversion failed.")
            st.exception(exc)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

st.markdown("""
<hr>
<div class="footer">Powered by <a href="https://banglaharaf.com" target="_blank">Bangla Haraf Font Foundry</a><br>
Made for Bengali publishing workflows</div>
""", unsafe_allow_html=True)
