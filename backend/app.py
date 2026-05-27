from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os

from core.search_service import SearchService

app = Flask(__name__)
search_service = SearchService()

UPLOAD_FOLDER = '/tmp/audio_uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    
    results = search_service.vector_search(query)
    return jsonify(results)

@app.route('/hybrid-search', methods=['GET'])
def hybrid_search():
    query = request.args.get('q')
    category = request.args.get('category')
    
    if not query or not category:
        return jsonify({"error": "Parameters 'q' and 'category' are required"}), 400
        
    results = search_service.hybrid_search(query, category)
    return jsonify(results)

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            transcript = search_service.transcribe_audio(filepath)
            return jsonify({"transcript": transcript})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            os.remove(filepath) # Clean up the uploaded file

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)