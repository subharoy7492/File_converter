import hashlib
import logging
import os
import re
import shutil
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath

import streamlit as st
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from converters import get_available_converters, get_converter


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="ANSI to Unicode Document Converter",
    page_icon="🔄",
    layout="centered",
)

# Inject Tailwind CSS via CDN and custom styling for crisp fonts and button colors
st.markdown(
    """
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* Force crisp font rendering on large/Retina screens to avoid blurring */
        html, body, [class*="css"] {
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            text-rendering: optimizeLegibility;
        }

        /* Hide default Streamlit header/footer branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Custom styling adjustments for Streamlit widgets to match Tailwind theme */
        .stSelectbox div[data-baseweb="select"] {
            border-radius: 0.5rem;
            border-color: #cbd5e1;
        }
        .stFileUploader section {
            border: 2px dashed #cbd5e1 !important;
            border-radius: 0.75rem;
            background-color: #f8fafc;
        }

        /* Vibrant Blue styling for Streamlit submit and download buttons */
        .stButton button, .stDownloadButton a {
            background-color: #2563eb !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            border-radius: 0.75rem !important;
            border: none !important;
            transition: background-color 0.2s ease-in-out !important;
        }
        .stButton button:hover, .stDownloadButton a:hover {
            background-color: #1d4ed8 !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

ENGLISH_FONTS = {
    "arial", "calibri", "times new roman", "courier new", "georgia",
    "verdana", "tahoma", "trebuchet ms", "segoe ui", "helvetica",
    "garamond", "cambria", "consolas", "impact", "century gothic",
    "myriad pro",
}

BIJOY_MARKER_CHARS = set(
    "‡‰ˆþÏØÜÝÞßáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ Žž ¾¼"
)

BIJOY_EXPLICIT_TOKENS = {
    "xd", "xydy", "rm", "d", "dþ", "d«", "z", "u", "r",
    "q", "e", "a", "b", "c", "p", "s",
}

FALLBACK_ENGLISH_VOCAB = {
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "i",
    "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
    "this", "but", "his", "by", "from", "they", "we", "say", "her",
    "she", "or", "an", "will", "my", "one", "all", "would", "there",
    "their", "what", "so", "up", "out", "if", "about", "who", "get",
    "which", "go", "me", "when", "make", "can", "like", "time", "no",
    "just", "him", "know", "take", "people", "into", "year", "your",
    "good", "some", "could", "them", "see", "other", "than", "then",
    "now", "look", "only", "come", "its", "over", "think", "also",
    "back", "after", "use", "two", "how", "our", "work", "first",
    "well", "way", "even", "new", "want", "because", "any", "these",
    "give", "day", "most", "us", "is", "are", "was", "were",
}


@st.cache_resource
def get_english_vocab() -> set[str]:
    try:
        from nltk.corpus import stopwords, words

        return set(words.words()).union(set(stopwords.words("english")))
    except (ImportError, LookupError, OSError):
        return FALLBACK_ENGLISH_VOCAB


ENGLISH_VOCAB = get_english_vocab()


def is_genuine_english_word(word: str) -> bool:
    clean = word.lower().strip(".,!?:;\"'()[]{}<>-")

    if not clean:
        return False

    if clean in BIJOY_EXPLICIT_TOKENS:
        return False

    if any(char in BIJOY_MARKER_CHARS for char in clean):
        return False

    if clean.replace(".", "").replace("-", "").isnumeric():
        return True

    return clean in ENGLISH_VOCAB


def convert_phrase_stream(full_text, converter_engine, keep_english=True):
    if not full_text:
        return full_text

    if not keep_english:
        return converter_engine.convert_phrase(full_text)

    tokens = re.findall(r"\S+|\s+", full_text)
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
    for phrase_text, is_english in phrases:
        if is_english:
            output.append(phrase_text)
        else:
            output.append(converter_engine.convert_phrase(phrase_text))

    result = "".join(output)
    return re.sub(r"([ক-হয়ড়ঢ়ৎ])\s+গু\s+([ক-হয়ড়ঢ়ৎ])", r"\1 = \2", result)


def set_run_font(run, target_font: str) -> None:
    run.font.name = target_font

    r_pr = run._element.get_or_add_rPr()
    r_fonts = r_pr.rFonts

    if r_fonts is None:
        r_fonts = OxmlElement("w:rFonts")
        r_pr.insert(0, r_fonts)

    for attribute in ("ascii", "hAnsi", "eastAsia", "cs"):
        r_fonts.set(qn(f"w:{attribute}"), target_font)


def process_paragraph_docx(paragraph, target_font, converter_engine, keep_english):
    if not paragraph.text or not paragraph.text.strip():
        return

    original_text = paragraph.text
    converted_text = convert_phrase_stream(
        original_text,
        converter_engine,
        keep_english,
    )

    if converted_text != original_text and paragraph.runs:
        paragraph.runs[0].text = converted_text
        set_run_font(paragraph.runs[0], target_font)

        for run in paragraph.runs[1:]:
            run.text = ""


def process_table_docx(table, target_font, converter_engine, keep_english):
    for row in table.rows:
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                process_paragraph_docx(
                    paragraph,
                    target_font,
                    converter_engine,
                    keep_english,
                )

            for nested_table in cell.tables:
                process_table_docx(
                    nested_table,
                    target_font,
                    converter_engine,
                    keep_english,
                )


def process_docx(input_path, output_path, target_font, converter_engine, keep_english):
    doc = Document(input_path)

    for paragraph in doc.paragraphs:
        process_paragraph_docx(
            paragraph,
            target_font,
            converter_engine,
            keep_english,
        )

    for table in doc.tables:
        process_table_docx(
            table,
            target_font,
            converter_engine,
            keep_english,
        )

    doc.save(output_path)


def safe_extract_zip(zip_file: zipfile.ZipFile, destination: str) -> None:
    destination_path = Path(destination).resolve()

    for member in zip_file.infolist():
        member_name = member.filename.replace("\\", "/")
        relative_path = PurePosixPath(member_name)

        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise ValueError("Unsafe path found in the IDML archive.")

        target_path = destination_path.joinpath(*relative_path.parts).resolve()

        if os.path.commonpath([str(destination_path), str(target_path)]) != str(
            destination_path
        ):
            raise ValueError("Unsafe path found in the IDML archive.")

        if member.is_dir():
            target_path.mkdir(parents=True, exist_ok=True)
            continue

        target_path.parent.mkdir(parents=True, exist_ok=True)

        with zip_file.open(member) as source, open(target_path, "wb") as target:
            shutil.copyfileobj(source, target)


def process_idml(input_path, output_path, target_font, converter_engine, keep_english=True):
    extract_dir = f"{input_path}_extracted"
    shutil.rmtree(extract_dir, ignore_errors=True)
    os.makedirs(extract_dir, exist_ok=True)

    try:
        with zipfile.ZipFile(input_path, "r") as zip_ref:
            safe_extract_zip(zip_ref, extract_dir)

        stories_dir = os.path.join(extract_dir, "Stories")

        if os.path.isdir(stories_dir):
            for story_file in os.listdir(stories_dir):
                if not story_file.lower().endswith(".xml"):
                    continue

                file_path = os.path.join(stories_dir, story_file)

                try:
                    tree = ET.parse(file_path)
                except ET.ParseError:
                    logger.warning("Skipping invalid IDML XML: %s", file_path)
                    continue

                root = tree.getroot()
                file_modified = False

                for range_element in root.iter():
                    if not range_element.tag.endswith("CharacterStyleRange"):
                        continue

                    applied_language = range_element.attrib.get(
                        "AppliedLanguage", ""
                    ).lower()
                    applied_font = range_element.attrib.get(
                        "AppliedFont", ""
                    ).lower()

                    if keep_english and (
                        "english" in applied_language
                        or any(font in applied_font for font in ENGLISH_FONTS)
                    ):
                        continue

                    range_modified = False

                    for content_element in range_element.iter():
                        if (
                            content_element.tag.endswith("Content")
                            and content_element.text
                        ):
                            original_text = content_element.text
                            converted_text = convert_phrase_stream(
                                original_text,
                                converter_engine,
                                keep_english,
                            )

                            if converted_text != original_text:
                                content_element.text = converted_text
                                range_modified = True

                    if range_modified:
                        range_element.attrib["AppliedFont"] = target_font
                        range_element.attrib["Composer"] = (
                            "$ID/HL Composer Engine"
                        )
                        file_modified = True

                if file_modified:
                    tree.write(
                        file_path,
                        encoding="utf-8",
                        xml_declaration=True,
                    )

        archive_files = []

        for folder_name, _, filenames in os.walk(extract_dir):
            for filename in filenames:
                file_path = os.path.join(folder_name, filename)
                archive_name = os.path.relpath(
                    file_path,
                    extract_dir,
                ).replace(os.sep, "/")
                archive_files.append((file_path, archive_name))

        archive_files.sort(
            key=lambda item: (item[1] != "mimetype", item[1])
        )

        with zipfile.ZipFile(
            output_path,
            "w",
            compression=zipfile.ZIP_DEFLATED,
        ) as zip_out:
            for file_path, archive_name in archive_files:
                if archive_name == "mimetype":
                    zip_out.write(
                        file_path,
                        archive_name,
                        compress_type=zipfile.ZIP_STORED,
                    )
                else:
                    zip_out.write(file_path, archive_name)

    finally:
        shutil.rmtree(extract_dir, ignore_errors=True)


def get_converter_options():
    available = get_available_converters()

    if isinstance(available, dict):
        options = list(available.keys())
        labels = {key: str(available[key]) for key in options}
    else:
        options = list(available)
        labels = {option: str(option) for option in options}

    return options, labels


# --- Tailwind Styled UI Header ---
st.markdown(
    """
    <div class="bg-gradient-to-r from-blue-600 to-indigo-700 text-white p-8 rounded-2xl shadow-lg mb-8 text-center">
        <div class="inline-flex items-center justify-center bg-white/10 p-3 rounded-full mb-4">
            <span class="text-3xl">🔄</span>
        </div>
        <h1 class="text-3xl font-extrabold tracking-tight mb-2">ANSI to Unicode Document Converter</h1>
        <p class="text-blue-100 text-base max-w-xl mx-auto">
            Seamlessly convert ANSI and Bijoy encoded text in Microsoft Word (.docx) and Adobe InDesign (.idml) documents into clean Bengali Unicode.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    converter_options, converter_labels = get_converter_options()
except Exception as exc:
    st.error(f"Could not load converter options: {exc}")
    st.stop()

if not converter_options:
    st.error("No converters are available. Check your converters.py file.")
    st.stop()


# --- Form Container wrapped in a Tailwind Card ---
st.markdown(
    """
    <div class="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm mb-6">
    """,
    unsafe_allow_html=True,
)

with st.form("conversion_form"):
    st.markdown("<p class='text-slate-800 font-semibold mb-2'>Upload Document (.docx or .idml)</p>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        label="",
        type=["docx", "idml"],
        help="Supported formats: .docx and .idml",
        label_visibility="collapsed"
    )

    col1, col2 = st.columns(2)
    with col1:
        mapping_version = st.selectbox(
            "Converter Version",
            options=converter_options,
            format_func=lambda option: converter_labels[option],
        )
    with col2:
        target_font = st.selectbox(
            "Target Font",
            options=["Vrinda", "Kalpurush", "Shonar Bangla"],
            index=1,
        )

    keep_english = st.checkbox(
        "Keep English words and punctuation marks",
        value=False,
        help=(
            "Detected English words are kept unchanged. English text explicitly "
            "marked in IDML styles is also skipped."
        ),
    )

    st.markdown("<div class='mt-4'></div>", unsafe_allow_html=True)
    submitted = st.form_submit_button(
        "✨ Convert & Download",
        use_container_width=True,
    )

st.markdown("</div>", unsafe_allow_html=True)


if submitted:
    st.session_state.pop("conversion_result", None)

    if uploaded_file is None:
        st.error("Please upload a DOCX or IDML file.")
        st.stop()

    filename = Path(uploaded_file.name).name
    extension = Path(filename).suffix.lower()

    if extension not in {".docx", ".idml"}:
        st.error("Unsupported file format. Upload a DOCX or IDML file.")
        st.stop()

    try:
        converter_engine = get_converter(mapping_version)
    except (ValueError, KeyError) as exc:
        st.error(f"Could not load the selected converter: {exc}")
        st.stop()

    output_filename = f"Unicode_{filename}"
    file_bytes = uploaded_file.getvalue()

    with st.spinner("Converting document..."):
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                input_path = os.path.join(temp_dir, f"input{extension}")
                output_path = os.path.join(temp_dir, output_filename)

                with open(input_path, "wb") as input_file:
                    input_file.write(file_bytes)

                if extension == ".docx":
                    process_docx(
                        input_path,
                        output_path,
                        target_font,
                        converter_engine,
                        keep_english,
                    )
                    mime_type = (
                        "application/vnd.openxmlformats-officedocument."
                        "wordprocessingml.document"
                    )
                else:
                    process_idml(
                        input_path,
                        output_path,
                        target_font,
                        converter_engine,
                        keep_english,
                    )
                    mime_type = "application/vnd.adobe.indesign-idml-package"

                with open(output_path, "rb") as output_file:
                    converted_bytes = output_file.read()

            st.session_state["conversion_result"] = {
                "data": converted_bytes,
                "filename": output_filename,
                "mime": mime_type,
            }
            st.success("Conversion completed successfully!")

        except Exception as exc:
            logger.exception("Document conversion failed")
            st.error(f"Conversion failed: {exc}")


result = st.session_state.get("conversion_result")

if result:
    st.markdown("<div class='mb-4'></div>", unsafe_allow_html=True)
    st.download_button(
        label="📥 Download Converted Document",
        data=result["data"],
        file_name=result["filename"],
        mime=result["mime"],
        use_container_width=True,
    )

# --- Footer ---
st.markdown(
    """
    <div class="text-center mt-10 mb-6 text-slate-400 text-sm">
        Powered by 
        <a href="https://banglaharaf.com" target="_blank" class="text-blue-600 font-medium hover:underline">
            Bangla Haraf Font Foundry
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)
