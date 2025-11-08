from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import os
import tempfile

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
            return jsonify({'success': False, 'error': 'Por favor, envie a imagem'})
        
        imagem_file = request.files['imagem']
        
        if imagem_file.filename == '':
            return jsonify({'success': False, 'error': 'Arquivo de imagem inválido'})
        
        # Processar a imagem - dividir ao meio
        imagem = Image.open(imagem_file).convert('RGB')
        largura, altura = imagem.size
        
        # Dividir imagem
        metade_esquerda = imagem.crop((0, 0, largura // 2, altura))
        metade_direita = imagem.crop((largura // 2, 0, largura, altura))
        
        # Criar imagem de resultado (layout de mockup)
        # Para demonstração, vamos criar um layout simples
        resultado = criar_mockup_demo(metade_esquerda, metade_direita, largura, altura)
        
        # Gerar preview
        buffer = io.BytesIO()
        resultado.save(buffer, format='PNG', quality=95)
        preview_data = base64.b64encode(buffer.getvalue()).decode()
        
        # Salvar para download
        os.makedirs('temp', exist_ok=True)
        output_path = f"temp/resultado_{hash(preview_data)}.png"
        resultado.save(output_path, 'PNG', quality=95)
        
        return jsonify({
            'success': True,
            'preview': f"data:image/png;base64,{preview_data}",
            'download_id': output_path,
            'message': '✅ Mockup gerado com sucesso! (Versão Demo - Próximo passo: PSD)'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro no processamento: {str(e)}'})

def criar_mockup_demo(esquerda, direita, largura, altura):
    """Cria um layout de mockup para demonstração"""
    # Criar imagem resultado (2x mais larga para mostrar as duas metades)
    resultado = Image.new('RGB', (largura * 2, altura), color='white')
    
    # Colocar as metades lado a lado
    resultado.paste(esquerda, (0, 0))
    resultado.paste(direita, (largura, 0))
    
    # Adicionar labels para identificação
    draw = ImageDraw.Draw(resultado)
    
    try:
        # Tentar usar fonte básica
        font = ImageFont.load_default()
        draw.text((10, 10), "Caneca Esquerda", fill='black', font=font)
        draw.text((largura + 10, 10), "Caneca Direita", fill='black', font=font)
    except:
        # Se der erro na fonte, continuar sem texto
        pass
    
    return resultado

@app.route('/download/<path:file_path>')
def download(file_path):
    try:
        return send_file(file_path, as_attachment=True, download_name='mockup_gerado.png')
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health')
def health():
    return jsonify({'status': 'online', 'version': '1.0-demo'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
