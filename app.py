import io
import zipfile
import os
from flask import Flask, request, send_file, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from PIL import Image
import fitz

# Optional: better PDF compression
try:
    from pikepdf import Pdf  # type: ignore
    HAS_PIKEPDF = True
except ImportError:
    HAS_PIKEPDF = False

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB total request size

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB per file

def check_file_size(file_obj):
    """Check if file exceeds max size"""
    file_obj.seek(0, os.SEEK_END)
    size = file_obj.tell()
    file_obj.seek(0)
    if size > MAX_FILE_SIZE:
        raise ValueError(f'File exceeds {MAX_FILE_SIZE // (1024*1024)} MB limit')
    return size

@app.route('/')
@limiter.limit("100 per hour")
def index():
    return render_template('index.html')

@app.route('/ads.txt')
def ads_txt():
    ads_path = os.path.join(os.path.dirname(__file__), 'ads.txt')
    return send_file(ads_path, mimetype='text/plain')

@app.route('/googleffad24874dea0564.html')
def google_verify():
    verify_path = os.path.join(os.path.dirname(__file__), 'googleffad24874dea0564.html')
    return send_file(verify_path, mimetype='text/html')

@app.route('/google-site-verification-mJTBf60hu7amVnqkdlIfe8dLJVQvNbBlQYahOAzYIqU.html')
def google_verify_txt():
    verify_path = os.path.join(os.path.dirname(__file__), 'google-site-verification-mJTBf60hu7amVnqkdlIfe8dLJVQvNbBlQYahOAzYIqU.html')
    return send_file(verify_path, mimetype='text/html')

# Serve verification files from static folder as fallback
@app.route('/googleffad24874dea0564.html')
def google_static_verify():
    return app.send_static_file('googleffad24874dea0564.html')

@app.route('/google-site-verification-mJTBf60hu7amVnqkdlIfe8dLJVQvNbBlQYahOAzYIqU.html')
def google_static_verify2():
    return app.send_static_file('google-site-verification-mJTBf60hu7amVnqkdlIfe8dLJVQvNbBlQYahOAzYIqU.html')

@app.route('/merge', methods=['POST'])
@limiter.limit("30 per hour")
def merge_pdfs():
    files = request.files.getlist('files')
    if not files:
        return 'No files provided', 400
    merger = PdfMerger()
    try:
        for f in files:
            if f and f.filename.lower().endswith('.pdf'):
                check_file_size(f.stream)
                merger.append(f)
    except ValueError as e:
        return str(e), 413
    except Exception as e:
        return f'Error processing files: {str(e)}', 400
    out = io.BytesIO()
    merger.write(out)
    merger.close()
    out.seek(0)
    return send_file(out, as_attachment=True, download_name='merged.pdf', mimetype='application/pdf')

@app.route('/split', methods=['POST'])
@limiter.limit("30 per hour")
def split_pdf():
    file = request.files.get('file')
    if not file or not file.filename.lower().endswith('.pdf'):
        return 'Upload a PDF', 400
    try:
        check_file_size(file.stream)
        reader = PdfReader(file)
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, 'w') as zf:
            for i, page in enumerate(reader.pages, start=1):
                writer = PdfWriter()
                writer.add_page(page)
                single_buf = io.BytesIO()
                writer.write(single_buf)
                zf.writestr(f'page_{i}.pdf', single_buf.getvalue())
        zip_buf.seek(0)
        return send_file(zip_buf, as_attachment=True, download_name='split_pages.zip', mimetype='application/zip')
    except ValueError as e:
        return str(e), 413
    except Exception as e:
        return f'Error: {str(e)}', 400

@app.route('/images2pdf', methods=['POST'])
@limiter.limit("30 per hour")
def images_to_pdf():
    files = request.files.getlist('images')
    images = []
    for f in files:
        try:
            check_file_size(f.stream)
            img = Image.open(f.stream).convert('RGB')
            images.append(img)
        except ValueError as e:
            return str(e), 413
        except Exception:
            continue
    if not images:
        return 'No valid images uploaded', 400
    out = io.BytesIO()
    images[0].save(out, format='PDF', save_all=True, append_images=images[1:])
    out.seek(0)
    return send_file(out, as_attachment=True, download_name='images.pdf', mimetype='application/pdf')

@app.route('/pdf2images', methods=['POST'])
@limiter.limit("30 per hour")
def pdf_to_images():
    file = request.files.get('file')
    if not file or not file.filename.lower().endswith('.pdf'):
        return 'Upload a PDF', 400
    try:
        check_file_size(file.stream)
        data = file.read()
        doc = fitz.open(stream=data, filetype='pdf')
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, 'w') as zf:
            for i, page in enumerate(doc, start=1):
                pix = page.get_pixmap()
                img_bytes = pix.tobytes('png')
                zf.writestr(f'page_{i}.png', img_bytes)
        zip_buf.seek(0)
        return send_file(zip_buf, as_attachment=True, download_name='pdf_pages.zip', mimetype='application/zip')
    except ValueError as e:
        return str(e), 413
    except Exception as e:
        return f'Error: {str(e)}', 400

@app.route('/compress', methods=['POST'])
@limiter.limit("30 per hour")
def compress_pdf():
    file = request.files.get('file')
    if not file or not file.filename.lower().endswith('.pdf'):
        return 'Upload a PDF', 400
    try:
        check_file_size(file.stream)
        data = file.read()
        out = io.BytesIO()
        
        if HAS_PIKEPDF:
            try:
                pdf = Pdf.open(io.BytesIO(data))
                pdf.save(out, optimize_streams=True)
                out.seek(0)
                return send_file(out, as_attachment=True, download_name='compressed.pdf', mimetype='application/pdf')
            except Exception:
                pass
        
        # Fallback: rewrite with PyPDF2
        reader = PdfReader(io.BytesIO(data))
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.write(out)
        out.seek(0)
        return send_file(out, as_attachment=True, download_name='compressed.pdf', mimetype='application/pdf')
    except ValueError as e:
        return str(e), 413
    except Exception as e:
        return f'Error: {str(e)}', 400

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
