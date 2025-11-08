from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from PIL import Image, ImageDraw
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
            return jsonify({'success': False, 'error': 'Arquivo de imagem inválido'})
        
        # Processar imagem
        imagem = Image.open(imagem_file)
        imagem = imagem.convert('RGB')
        largura, altura = imagem.size
        
        # Dividir ao meio
        metade_esq = imagem.crop((0, 0, largura // 2, altura))
        metade_dir = imagem.crop((largura // 2, 0, largura, altura))
        
        # Criar template limpo com canecas
        resultado = criar_template_canecas(metade_esq, metade_dir)
        
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
            'message': '✅ Canecas personalizadas criadas!'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def criar_template_canecas(imagem_esq, imagem_dir):
    """Cria template limpo com 2 canecas brancas redondas"""
    
    # Criar canvas com fundo BRANCO
    largura = 1000
    altura = 600
    canvas = Image.new('RGB', (largura, altura), color='white')
    draw = ImageDraw.Draw(canvas)
    
    # Tamanho das canecas
    diametro_caneca = 300
    raio = diametro_caneca // 2
    
    # Posições das canecas (centralizadas verticalmente)
    y_centro = altura // 2
    pos_esq = (200, y_centro - raio)
    pos_dir = (600, y_centro - raio)
    
    # === CANECA ESQUERDA (alça para ESQUERDA) ===
    desenhar_caneca_redonda(canvas, draw, pos_esq, diametro_caneca, imagem_esq, alça_esquerda=True)
    
    # === CANECA DIREITA (alça para DIREITA) ===
    desenhar_caneca_redonda(canvas, draw, pos_dir, diametro_caneca, imagem_dir, alça_esquerda=False)
    
    return canvas

def desenhar_caneca_redonda(canvas, draw, posicao, diametro, imagem, alça_esquerda=True):
    """Desenha uma caneca redonda branca com imagem personalizada"""
    x, y = posicao
    raio = diametro // 2
    centro_x = x + raio
    centro_y = y + raio
    
    # === CORPO DA CANECA (círculo branco) ===
    draw.ellipse([x, y, x + diametro, y + diametro], fill='white', outline='#e0e0e0', width=3)
    
    # === ÁREA DA IMAGEM (círculo menor dentro da caneca) ===
    diametro_imagem = diametro - 40  # Deixar borda
    raio_imagem = diametro_imagem // 2
    x_imagem = centro_x - raio_imagem
    y_imagem = centro_y - raio_imagem
    
    # Criar máscara circular para a imagem
    mascara = Image.new('L', (diametro_imagem, diametro_imagem), 0)
    draw_mascara = ImageDraw.Draw(mascara)
    draw_mascara.ellipse([0, 0, diametro_imagem, diametro_imagem], fill=255)
    
    # Redimensionar imagem para caber no círculo
    img_redim = imagem.resize((diametro_imagem, diametro_imagem), Image.Resampling.LANCZOS)
    
    # Aplicar máscara circular à imagem
    img_circular = Image.new('RGBA', (diametro_imagem, diametro_imagem))
    img_circular.paste(img_redim, (0, 0), mascara)
    
    # Colocar imagem circular na caneca
    canvas.paste(img_circular, (x_imagem, y_imagem), img_circular)
    
    # === ALÇA DA CANECA ===
    if alça_esquerda:
        # Alça para ESQUERDA
        alça_x1 = x - 30
        alça_x2 = x + 10
    else:
        # Alça para DIREITA
        alça_x1 = x + diametro - 10
        alça_x2 = x + diametro + 30
    
    alça_y1 = centro_y - 40
    alça_y2 = centro_y + 40
    
    # Desenhar alça (semi-círculo)
    draw.arc([alça_x1, alça_y1, alça_x2, alça_y2], start=270, end=90, fill='#cccccc', width=8)
    
    # === BASE DA CANECA ===
    base_y = y + diametro + 5
    base_altura = 15
    base_largura = diametro - 60
    
    # Base retangular
    draw.rectangle([centro_x - base_largura//2, base_y, 
                   centro_x + base_largura//2, base_y + base_altura], 
                   fill='#f0f0f0', outline='#dddddd', width=1)
    
    # Cantos arredondados da base
    draw.ellipse([centro_x - base_largura//2 - 5, base_y - 3, 
                  centro_x - base_largura//2 + 5, base_y + 7], fill='#f0f0f0')
    draw.ellipse([centro_x + base_largura//2 - 5, base_y - 3, 
                  centro_x + base_largura//2 + 5, base_y + 7], fill='#f0f0f0')

@app.route('/download/<path:file_path>')
def download(file_path):
    try:
        return send_file(file_path, as_attachment=True, download_name='canecas_personalizadas.png')
    except:
        return jsonify({'success': False, 'error': 'Arquivo não encontrado'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
