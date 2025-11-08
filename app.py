from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from PIL import Image, ImageDraw, ImageFont
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
        psd_file = request.files.get('psd')
        
        if imagem_file.filename == '':
            return jsonify({'success': False, 'error': 'Arquivo de imagem inválido'})
        
        # Processar imagem
        imagem = Image.open(imagem_file)
        imagem = imagem.convert('RGB')
        largura, altura = imagem.size
        
        # Dividir ao meio
        metade_esq = imagem.crop((0, 0, largura // 2, altura))
        metade_dir = imagem.crop((largura // 2, 0, largura, altura))
        
        # SEMPRE criar layout personalizado (baseado no que você me descreveu)
        resultado = criar_layout_canecas(metade_esq, metade_dir, largura, altura)
        
        # Gerar preview
        buffer = io.BytesIO()
        resultado.save(buffer, 'PNG', optimize=True)
        preview_data = base64.b64encode(buffer.getvalue()).decode()
        
        # Salvar arquivo
        os.makedirs('temp', exist_ok=True)
        file_id = hashlib.md5(preview_data.encode()).hexdigest()[:8]
        output_path = f'temp/resultado_{file_id}.png'
        resultado.save(output_path, 'PNG', optimize=True)
        
        return jsonify({
            'success': True,
            'preview': f'data:image/png;base64,{preview_data}',
            'download_id': output_path,
            'message': '✅ Mockup personalizado gerado!'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def criar_layout_canecas(metade_esq, metade_dir, largura_original, altura_original):
    """Cria layout específico para canecas baseado na descrição do PSD"""
    
    # Criar canvas principal
    largura_canvas = 1000
    altura_canvas = 800
    canvas = Image.new('RGB', (largura_canvas, altura_canvas), color='#1a1a1a')
    draw = ImageDraw.Draw(canvas)
    
    # === CABEÇALHO ===
    draw.rectangle([0, 0, largura_canvas, 100], fill='#2d2d2d')
    
    # Título principal (do seu PSD)
    draw.text((50, 30), "A EVOLUÇÃO DO HOMEM", fill='#ffffff', font=ImageFont.load_default())
    draw.text((largura_canvas - 200, 30), "HOMER", fill='#ff6b6b', font=ImageFont.load_default())
    
    # === ÁREA DAS CANECAS ===
    # Redimensionar metades para caber no layout
    tamanho_caneca = (300, 400)
    caneca_esq = metade_esq.resize(tamanho_caneca, Image.Resampling.LANCZOS)
    caneca_dir = metade_dir.resize(tamanho_caneca, Image.Resampling.LANCZOS)
    
    # Posicionar canecas
    pos_x_esq = 100
    pos_x_dir = 550
    pos_y = 150
    
    # Adicionar molduras às canecas
    def adicionar_moldura(imagem, cor='#444'):
        moldura_size = (imagem.width + 20, imagem.height + 20)
        moldura = Image.new('RGB', moldura_size, color=cor)
        moldura.paste(imagem, (10, 10))
        return moldura
    
    caneca_esq_com_moldura = adicionar_moldura(caneca_esq, '#555')
    caneca_dir_com_moldura = adicionar_moldura(caneca_dir, '#555')
    
    # Colocar canecas no canvas
    canvas.paste(caneca_esq_com_moldura, (pos_x_esq, pos_y))
    canvas.paste(caneca_dir_com_moldura, (pos_x_dir, pos_y))
    
    # === LABELS DAS CANECAS ===
    draw.rectangle([pos_x_esq, pos_y + 430, pos_x_esq + 340, pos_y + 460], fill='#333')
    draw.rectangle([pos_x_dir, pos_y + 430, pos_x_dir + 340, pos_y + 460], fill='#333')
    
    draw.text((pos_x_esq + 100, pos_y + 440), "CANECA ESQUERDA", fill='#fff')
    draw.text((pos_x_dir + 100, pos_y + 440), "CANECA DIREITA", fill='#fff')
    
    # === RODAPÉ ===
    draw.rectangle([0, altura_canvas - 80, largura_canvas, altura_canvas], fill='#2d2d2d')
    draw.text((50, altura_canvas - 50), "Necroletário", fill='#ccc')
    draw.text((largura_canvas - 150, altura_canvas - 50), "Homestágio", fill='#ccc')
    
    # === DETALHES EXTRAS ===
    # Linha decorativa
    draw.line([0, 100, largura_canvas, 100], fill='#444', width=2)
    draw.line([0, altura_canvas - 80, largura_canvas, altura_canvas - 80], fill='#444', width=2)
    
    return canvas

@app.route('/download/<path:file_path>')
def download(file_path):
    try:
        return send_file(file_path, as_attachment=True, download_name='mockup_canecas.png')
    except:
        return jsonify({'success': False, 'error': 'Arquivo não encontrado'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
