from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from PIL import Image
import psd_tools
from psd_tools import PSDImage
import io
import base64
import os
import tempfile

app = Flask(__name__)
CORS(app)

# Configurações
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/processar', methods=['POST'])
def processar_imagem():
    try:
        # Verificar se arquivos foram enviados
        if 'psd' not in request.files or 'imagem' not in request.files:
            return jsonify({'success': False, 'error': 'Por favor, envie ambos os arquivos'})
        
        psd_file = request.files['psd']
        imagem_file = request.files['imagem']
        
        # Verificar se arquivos têm nome
        if psd_file.filename == '' or imagem_file.filename == '':
            return jsonify({'success': False, 'error': 'Arquivos inválidos'})
        
        # Criar diretório temp se não existir
        os.makedirs('temp', exist_ok=True)
        
        # Processar PSD
        psd = PSDImage.open(psd_file)
        
        # Processar imagem - dividir ao meio
        imagem = Image.open(imagem_file).convert('RGB')
        largura, altura = imagem.size
        
        metade_esquerda = imagem.crop((0, 0, largura // 2, altura))
        metade_direita = imagem.crop((largura // 2, 0, largura, altura))
        
        # Gerar composite para preview
        composite = psd.composite()
        
        # Salvar preview
        preview_buffer = io.BytesIO()
        composite.save(preview_buffer, format='PNG')
        preview_data = base64.b64encode(preview_buffer.getvalue()).decode()
        
        # Para versão inicial, vamos retornar a imagem original processada
        # (A manipulação de camadas PSD precisa do arquivo real para testar)
        output_buffer = io.BytesIO()
        composite.save(output_buffer, format='PNG')
        output_buffer.seek(0)
        
        # Salvar arquivo temporário
        output_path = f"temp/output_{len(preview_data)}.png"
        with open(output_path, 'wb') as f:
            f.write(output_buffer.getvalue())
        
        return jsonify({
            'success': True,
            'preview': f"data:image/png;base64,{preview_data}",
            'download_id': output_path,
            'message': 'Processamento inicial concluído! Envie feedback para ajustarmos as camadas.'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download/<path:file_path>')
def download(file_path):
    try:
        return send_file(file_path, as_attachment=True, download_name='mockup_final.png')
    except Exception as e:
        return str(e)

@app.route('/health')
def health():
    return jsonify({'status': 'online', 'message': 'Sistema de mockup funcionando!'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
