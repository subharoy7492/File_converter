import os
import sys
import zipfile
import shutil
import traceback
import subprocess
import json
import winreg
import xml.etree.ElementTree as ET
from flask import Flask, render_template_string, request, send_file, jsonify
from docx import Document

from converters import CONVERTERS, get_converter

sys.setrecursionlimit(10000)

app = Flask(__name__)
UPLOAD_FOLDER = os.path.abspath('uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ANSI_FONT_KEYWORDS = ['sutonny', 'bijoy', 'stm', 'soumili', 'ansi', 'bangla', 'bengali']

def is_ansi_font(font_name):
    if not font_name:
        return True
    font_lower = font_name.lower()
    return any(keyword in font_lower for keyword in ANSI_FONT_KEYWORDS)

def find_illustrator_executable():
    registry_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\illustrator.exe"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\illustrator.exe"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\illustrator.exe")
    ]
    for root_key, sub_key in registry_paths:
        try:
            with winreg.OpenKey(root_key, sub_key) as key:
                exe_path, _ = winreg.QueryValueEx(key, "")
                if exe_path and os.path.exists(exe_path):
                    return exe_path
        except OSError:
            continue
    raise FileNotFoundError("Adobe Illustrator is not installed or registered on this machine.")

def process_ai(input_path, output_path, target_font, converter_instance):
    abs_input_path = os.path.abspath(input_path)
    abs_output_path = os.path.abspath(output_path)
    illustrator_exe = find_illustrator_executable()

    script_dir = os.path.dirname(abs_input_path)
    extracted_json_path = os.path.join(script_dir, "ai_extracted.json")
    converted_json_path = os.path.join(script_dir, "ai_converted.json")
    jsx_script_path = os.path.abspath("temp_convert_script.jsx")
    log_file_path = os.path.abspath("jsx_error.log")

    js_input = abs_input_path.replace('\\', '\\\\')
    js_output = abs_output_path.replace('\\', '\\\\')
    js_extracted = extracted_json_path.replace('\\', '\\\\')
    js_converted = converted_json_path.replace('\\', '\\\\')
    js_log = log_file_path.replace('\\', '\\\\')

    for temp_f in [extracted_json_path, converted_json_path, jsx_script_path, log_file_path]:
        if os.path.exists(temp_f):
            try: os.remove(temp_f)
            except Exception: pass

    extract_jsx = f"""
    (function () {{
        app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
        var inputFile = new File("{js_input}");
        var outputFile = new File("{js_extracted}");

        function escapeJSON(str) {{
            if (!str) return "";
            return str.replace(/\\\\/g, "\\\\\\\\").replace(/"/g, '\\\\"').replace(/\\n/g, "\\\\n").replace(/\\r/g, "\\\\r").replace(/\\t/g, "\\\\t");
        }}

        try {{
            var doc = app.open(inputFile);
            var jsonItems = [];

            for (var i = 0; i < doc.textFrames.length; i++) {{
                var tf = doc.textFrames[i];
                var rawTxt = tf.contents;
                var fontName = "";
                try {{
                    fontName = tf.textRange.characterAttributes.textFont.name;
                }} catch(e) {{}}
                jsonItems.push('{{"index":' + i + ',"font":"' + escapeJSON(fontName) + '","text":"' + escapeJSON(rawTxt) + '"}}');
            }}

            doc.close(SaveOptions.DONOTSAVECHANGES);
            outputFile.open("w");
            outputFile.encoding = "UTF-8";
            outputFile.write("[" + jsonItems.join(",") + "]");
            outputFile.close();
        }} catch (e) {{
            var errFile = new File("{js_log}");
            errFile.open("w");
            errFile.write("Extraction Error: " + e.toString());
            errFile.close();
        }} finally {{ app.quit(); }}
    }})();
    """

    with open(jsx_script_path, "w", encoding="utf-8") as f:
        f.write(extract_jsx)

    subprocess.Popen([illustrator_exe, "-r", jsx_script_path]).wait()

    if not os.path.exists(extracted_json_path):
        raise RuntimeError("Failed to extract text from AI file.")

    with open(extracted_json_path, "r", encoding="utf-8") as f:
        extracted_data = json.load(f, strict=False)

    converted_data = []
    for item in extracted_data:
        font_name = item.get("font", "")
        original_text = item.get("text", "")
        
        if is_ansi_font(font_name):
            converted_data.append({
                "index": item["index"],
                "text": converter_instance.convert(original_text),
                "convert_font": True
            })
        else:
            converted_data.append({
                "index": item["index"],
                "text": original_text,
                "convert_font": False
            })

    with open(converted_json_path, "w", encoding="utf-8") as f:
        json.dump(converted_data, f, ensure_ascii=False)

    inject_jsx = f"""
    (function () {{
        app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
        var inputFile = new File("{js_input}");
        var outputFile = new File("{js_output}");
        var dataFile = new File("{js_converted}");

        try {{
            dataFile.open("r");
            dataFile.encoding = "UTF-8";
            var convertedData = eval("(" + dataFile.read() + ")");
            dataFile.close();

            var doc = app.open(inputFile);
            if (doc) {{
                for (var i = 0; i < convertedData.length; i++) {{
                    var item = convertedData[i];
                    var tf = doc.textFrames[item.index];
                    if (tf) {{
                        tf.contents = item.text;
                        if (item.convert_font) {{
                            try {{
                                tf.textRange.characterAttributes.textFont = app.textFonts.getByName("{target_font}");
                            }} catch (fontErr) {{}}

                            var composerNames = ["Adbe World Ready EveryLine", "Adbe World Ready SingleLine"];
                            for (var j = 0; j < tf.paragraphs.length; j++) {{
                                for (var k = 0; k < composerNames.length; k++) {{
                                    try {{
                                        tf.paragraphs[j].composer = composerNames[k];
                                        break;
                                    }} catch (compErr) {{}}
                                }}
                            }}
                        }}
                    }}
                }}
                var saveOpts = new IllustratorSaveOptions();
                saveOpts.pdfCompatible = true;
                doc.saveAs(outputFile, saveOpts);
                doc.close(SaveOptions.DONOTSAVECHANGES);
            }}
        }} catch (mainErr) {{
            var errFile = new File("{js_log}");
            errFile.open("w");
            errFile.write("Injection Error: " + mainErr.toString());
            errFile.close();
        }} finally {{ app.quit(); }}
    }})();
    """

    with open(jsx_script_path, "w", encoding="utf-8") as f:
        f.write(inject_jsx)

    subprocess.Popen([illustrator_exe, "-r", jsx_script_path]).wait()

    for temp_f in [extracted_json_path, converted_json_path, jsx_script_path, log_file_path]:
        if os.path.exists(temp_f):
            try: os.remove(temp_f)
            except Exception: pass

def process_docx(input_path, output_path, target_font, converter_instance):
    doc = Document(input_path)

    def process_runs(runs):
        for run in runs:
            if run.text and run.text.strip():
                font_name = run.font.name
                if is_ansi_font(font_name):
                    run.text = converter_instance.convert(run.text)
                    run.font.name = target_font

    for paragraph in doc.paragraphs:
        process_runs(paragraph.runs)

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    process_runs(paragraph.runs)

    doc.save(output_path)

def process_idml(input_path, output_path, target_font, converter_instance):
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

                    for elem in root.iter():
                        applied_font = elem.attrib.get('AppliedFont', '')
                        if is_ansi_font(applied_font):
                            if elem.tag.endswith('Content') and elem.text:
                                elem.text = converter_instance.convert(elem.text)
                                modified = True
                            if 'AppliedFont' in elem.attrib:
                                elem.attrib['AppliedFont'] = target_font
                                modified = True

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

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>STM / Soumili ANSI to Unicode File Converter</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-slate-50 text-slate-800 font-sans min-h-screen flex flex-col justify-between">
    <header class="w-full bg-white border-b border-slate-200 py-4 px-6">
        <h1 class="text-xl font-bold text-slate-900">STM / Soumili Converter (Font-Safe)</h1>
    </header>
    <main class="flex-grow flex items-center justify-center p-6">
        <div class="bg-white p-8 rounded-2xl shadow-xl w-full max-w-md space-y-6">
            <form action="/convert" method="post" enctype="multipart/form-data" class="space-y-4">
                <div>
                    <label class="block text-sm font-bold text-slate-700 mb-2">Converter Engine Version</label>
                    <select name="converter_version" class="w-full p-2 border border-slate-300 rounded-lg">
                        {% for key, info in converters.items() %}
                            <option value="{{ key }}">{{ info.name }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div>
                    <label class="block text-sm font-bold text-slate-700 mb-2">Select File (.docx, .idml, .ai)</label>
                    <input type="file" name="file" accept=".docx,.idml,.ai" required class="w-full p-2 border border-slate-300 rounded-lg">
                </div>
                <div>
                    <label class="block text-sm font-bold text-slate-700 mb-2">Target Font</label>
                    <select name="target_font" class="w-full p-2 border border-slate-300 rounded-lg">
                        <option value="Kalpurush" selected>Kalpurush</option>
                        <option value="SolaimanLipi">SolaimanLipi</option>
                        <option value="Vrinda">Vrinda</option>
                    </select>
                </div>
                <button type="submit" class="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg transition-all">Convert Document</button>
            </form>
        </div>
    </main>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, converters=CONVERTERS)

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({'error': 'No selected file'}), 400

    version_key = request.form.get('converter_version', 'bijoy_v1')
    try:
        converter_instance = get_converter(version_key)
    except ValueError as err:
        return jsonify({'error': str(err)}), 400

    target_font = request.form.get('target_font', 'Kalpurush')
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()

    input_path = os.path.join(app.config['UPLOAD_FOLDER'], 'input_' + filename)
    output_filename = 'Unicode_' + filename
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

    file.save(input_path)

    try:
        if ext == '.docx':
            process_docx(input_path, output_path, target_font, converter_instance)
        elif ext == '.idml':
            process_idml(input_path, output_path, target_font, converter_instance)
        elif ext == '.ai':
            process_ai(input_path, output_path, target_font, converter_instance)
        else:
            return jsonify({'error': f'Unsupported file format extension: {ext}'}), 400

        return send_file(output_path, as_attachment=True, download_name=output_filename)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(input_path):
            try: os.remove(input_path)
            except Exception: pass

if __name__ == '__main__':
    app.run(debug=True, port=5000)