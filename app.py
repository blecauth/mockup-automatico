from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from PIL import Image
import io
import base64
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/processar', methods=['POST'])
def processar_imagem():
    try:
        if 'psd' not in request.files or 'imagem' not in request.files:
            return jsonify({'success': False, 'error': 'Por favor, envie ambos os arquivos'})
        
        psd_file = request.files['psd']
        imagem_file = request.files['imagem']
        
        # Nesta versão inicial, vamos processar apenas a imagem
        # (adicionaremos o PSD depois que o build funcionar)
        imagem = Image.open(imagem_file).convert('RGB')
        
        # Dividir a imagem ao meio (simulação do processo)
        largura, altura = imagem.size
        metade_esquerda = imagem.crop((0, 0, largura // 2, altura))
        metade_direita = imagem.crop((largura // 2, 0, largura, altura))
        
        # Criar uma imagem composta para demonstração
        resultado = Image.new('RGB', (largura, altura * 2))
        resultado.paste(metade_esquerda, (0, 0))
        resultado.paste(metade_direita, (0, altura))
        
        # Gerar preview
        buffer = io.BytesIO()
        resultado.save(buffer, format='PNG')
        preview_data = base64.b64encode(buffer.getvalue()).decode()
        
        # Salvar para download
        os.makedirs('temp', exist_ok=True)
        output_path = f"temp/resultado_{hash(preview_data)}.png"
        resultado.save(output_path)
        
        return jsonify({
            'success': True,
            'preview': f"data:image/png;base64,{preview_data}",
            'download_id': output_path,
            'message': 'Versão demo funcionando! Próximo passo: integrar PSD.'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download/<path:file_path>')
def download(file_path):
    return send_file(file_path, as_attachment=True, download_name='mockup.png')

@app.route('/health')
def health():
    return jsonify({'status': 'online'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
