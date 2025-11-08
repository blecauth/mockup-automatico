from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from PIL import Image
import io
import base64
import os
import hashlib

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/processar', methods=['POST'])
def processar_imagem():
    try:
        if 'imagem' not in request.files:
            return jsonify({'success': False, 'error': 'Envie uma imagem'})
        
        imagem_file = request.files['imagem']
        
        if imagem_file.filename == '':
            return jsonify({'success': False, 'error': 'Arquivo inválido'})
        
        # Abrir e processar imagem
        imagem = Image.open(imagem_file)
        imagem = imagem.convert('RGB')
        
        largura, altura = imagem.size
        
        # Dividir ao meio
        metade_esq = imagem.crop((0, 0, largura // 2, altura))
        metade_dir = imagem.crop((largura // 2, 0, largura, altura))
        
        # Criar imagem resultado (lado a lado)
        espacamento = 20
        nova_largura = largura + espacamento + largura
        resultado = Image.new('RGB', (nova_largura, altura), color='white')
        
        resultado.paste(metade_esq, (0, 0))
        resultado.paste(metade_dir, (largura + espacamento, 0))
        
        # Salvar preview
        buffer = io.BytesIO()
        resultado.save(buffer, 'PNG')
        preview_data = base64.b64encode(buffer.getvalue()).decode()
        
        # Salvar arquivo
        os.makedirs('temp', exist_ok=True)
        file_id = hashlib.md5(preview_data.encode()).hexdigest()[:8]
        output_path = f'temp/resultado_{file_id}.png'
        resultado.save(output_path, 'PNG')
        
        return jsonify({
            'success': True,
            'preview': f'data:image/png;base64,{preview_data}',
            'download_id': output_path,
            'message': '✅ Imagem processada com sucesso!'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download/<path:file_path>')
def download(file_path):
    try:
        return send_file(file_path, as_attachment=True, download_name='mockup.png')
    except:
        return jsonify({'success': False, 'error': 'Arquivo não encontrado'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
