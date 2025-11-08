from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from PIL import Image, ImageDraw
import io
import base64
import os
import hashlib

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/processar', methods=['POST'])
def processar_imagem():
    try:
        if 'imagem' not in request.files:
            return jsonify({'success': False, 'error': 'Por favor, envie uma imagem'})
        
        imagem_file = request.files['imagem']
        
        if imagem_file.filename == '':
            return jsonify({'success': False, 'error': 'Arquivo de imagem inválido'})
        
        # Processar a imagem
        with Image.open(imagem_file) as img:
            imagem = img.convert('RGB')
            largura, altura = imagem.size
            
            # Dividir imagem ao meio
            metade_esquerda = imagem.crop((0, 0, largura // 2, altura))
            metade_direita = imagem.crop((largura // 2, 0, largura, altura))
            
            # Criar mockup de demonstração
            resultado = criar_mockup_demo(metade_esquerda, metade_direita, largura, altura)
            
            # Gerar preview
            buffer = io.BytesIO()
            resultado.save(buffer, format='PNG', optimize=True)
            buffer.seek(0)
            preview_data = base64.b64encode(buffer.getvalue()).decode()
            
            # Salvar para download
            os.makedirs('temp', exist_ok=True)
            file_hash = hashlib.md5(preview_data.encode()).hexdigest()[:10]
            output_path = f"temp/resultado_{file_hash}.png"
            resultado.save(output_path, 'PNG', optimize=True)
            
            return jsonify({
                'success': True,
                'preview': f"data:image/png;base64,{preview_data}",
                'download_id': output_path,
                'message': '✅ Mockup gerado com sucesso! Imagem dividida em duas metades.'
            })
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro: {str(e)}'})

def criar_mockup_demo(esquerda, direita, largura, altura):
    """Cria layout de mockup para demonstração"""
    # Criar imagem com as duas metades lado a lado
    espacamento = 20
    nova_largura = largura + espacamento + largura
    nova_altura = max(esquerda.height, direita.height) + 50  # espaço para labels
    
    resultado = Image.new('RGB', (nova_largura, nova_altura), color='#f0f0f0')
    
    # Calcular posições centralizadas
    y_pos = (nova_altura - esquerda.height) // 2
    
    # Colocar as metades
    resultado.paste(esquerda, (10, y_pos))
    resultado.paste(direita, (largura + espacamento, y_pos))
    
    # Adicionar labels
    draw = ImageDraw.Draw(resultado)
    
    # Labels simples
    draw.rectangle([5, 10, 150, 35], fill='#667eea')
    draw.rectangle([largura + espacamento - 5, 10, largura + espacamento + 145, 35], fill='#764ba2')
    
    # Texto branco
    draw.text((15, 15), "CANECA ESQUERDA", fill='white')
    draw.text((largura + espacamento + 5, 15), "CANECA DIREITA", fill='white')
    
    return resultado

@app.route('/download/<path:file_path>')
def download(file_path):
    try:
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name='mockup_canecas.png')
        else:
            return jsonify({'success': False, 'error': 'Arquivo não encontrado'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health')
def health():
    return jsonify({'status': 'online', 'version': '2.0-stable'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
