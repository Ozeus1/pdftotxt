from flask import Flask, request, render_template_string
import PyPDF2

app = Flask(__name__)

# HTML para interface gráfica
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Text Extractor</title>
</head>
<body>
    <h1>Extrator de Texto de PDF</h1>
    <form action="/" method="post" enctype="multipart/form-data">
        <label for="pdf_file">Selecione o arquivo PDF:</label>
        <input type="file" id="pdf_file" name="pdf_file" accept=".pdf" required>
        <button type="submit">Converter</button>
    </form>
    {% if extracted_text %}
        <h2>Texto Extraído:</h2>
        <pre>{{ extracted_text }}</pre>
    {% endif %}
</body>
</html>
"""

def extract_text_from_pdf(pdf_path):
    """
    Extrai texto de um arquivo PDF.

    :param pdf_path: Caminho para o arquivo PDF.
    :return: Texto extraído do PDF.
    """
    try:
        with open(pdf_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            extracted_text = ''
            for page in reader.pages:
                extracted_text += page.extract_text()
            return extracted_text
    except Exception as e:
        return f"Erro ao processar o arquivo PDF: {e}"

@app.route("/", methods=["GET", "POST"])
def upload_and_extract():
    extracted_text = None
    if request.method == "POST":
        # Verifica se um arquivo foi enviado
        if "pdf_file" in request.files:
            pdf_file = request.files["pdf_file"]
            if pdf_file.filename.endswith(".pdf"):
                # Salva temporariamente o arquivo
                temp_path = "temp.pdf"
                pdf_file.save(temp_path)
                
                # Extrai o texto do PDF
                extracted_text = extract_text_from_pdf(temp_path)
                
                # Salva o texto extraído em output.txt
                with open("output.txt", "w", encoding="utf-8") as output_file:
                    output_file.write(extracted_text)
    
    # Renderiza o HTML
    return render_template_string(HTML_TEMPLATE, extracted_text=extracted_text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

