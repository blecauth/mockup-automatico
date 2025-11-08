from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from PIL import Image, ImageDraw, ImageFilter
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
        
        # Criar mockup com CANECAS VISÍVEIS
        resultado = criar_mockup_com_canecas(metade_esq, metade_dir)
        
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
            'message': '✅ Canecas personalizadas criadas com sucesso!'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def criar_mockup_com_canecas(imagem_esq, imagem_dir):
    """Cria mockup com CANECAS BRANCAS visíveis personalizadas com as imagens"""
    
    # Criar canvas principal
    largura = 1000
    altura = 1000
    canvas = Image.new('RGB', (largura, altura), color='#1a1a1a')
    draw = ImageDraw.Draw(canvas)
    
    # === CABEÇALHO ===
    draw.rectangle([0, 0, largura, 100], fill='#2d2d2d')
    draw.text((50, 35), "A EVOLUÇÃO DO HOMEM", fill='white', font_size=20)
    draw.text((largura - 120, 35), "HOMER", fill='#ff4444', font_size=20)
    
    # === TÍTULOS DAS CANECAS ===
    draw.text((180, 120), "Não me perturbe", fill='#cccccc', font_size=16)
    draw.text((630, 120), "Estou ocupada fazendo nada", fill='#cccccc', font_size=16)
    
    # === CRIAR CANECAS BRANCAS PERSONALIZADAS ===
    tamanho_caneca = (300, 400)
    
    # Redimensionar imagens
    img_esq_redim = imagem_esq.resize(tamanho_caneca, Image.Resampling.LANCZOS)
    img_dir_redim = imagem_dir.resize(tamanho_caneca, Image.Resampling.LANCZOS)
    
    # Posições das canecas
    pos_esq = (100, 180)
    pos_dir = (550, 180)
    
    # === CANECA ESQUERDA - BRANCA COM IMAGEM ===
    caneca_esq = criar_caneca_branca_com_imagem(img_esq_redim)
    canvas.paste(caneca_esq, pos_esq)
    
    # === CANECA DIREITA - BRANCA COM IMAGEM ===
    caneca_dir = criar_caneca_branca_com_imagem(img_dir_redim)
    canvas.paste(caneca_dir, pos_dir)
    
    # === LABELS DAS CANECAS ===
    draw.rectangle([pos_esq[0] - 10, pos_esq[1] + 420, pos_esq[0] + 310, pos_esq[1] + 460], fill='#333333')
    draw.rectangle([pos_dir[0] - 10, pos_dir[1] + 420, pos_dir[0] + 310, pos_dir[1] + 460], fill='#333333')
    
    draw.text((pos_esq[0] + 80, pos_esq[1] + 435), "CANECA ESQUERDA", fill='white', font_size=14)
    draw.text((pos_dir[0] + 80, pos_dir[1] + 435), "CANECA DIREITA", fill='white', font_size=14)
    
    # === TEXTO "Rescolação" ===
    draw.text((largura // 2 - 50, 650), "Rescolação", fill='#aaaaaa', font_size=16)
    
    # === RODAPÉ ===
    draw.rectangle([0, altura - 80, largura, altura], fill='#2d2d2d')
    draw.text((50, altura - 50), "Necroletário", fill='#999999', font_size=14)
    draw.text((largura - 150, altura - 50), "Homestágio", fill='#999999', font_size=14)
    
    return canvas

def criar_caneca_branca_com_imagem(imagem):
    """Cria uma caneca BRANCA com a imagem personalizada no centro"""
    largura, altura = 320, 420  # Tamanho maior para incluir borda branca
    
    # Criar caneca branca (fundo)
    caneca = Image.new('RGB', (largura, altura), color='white')
    draw = ImageDraw.Draw(caneca)
    
    # Adicionar borda arredondada à caneca
    draw.rounded_rectangle([0, 0, largura, altura], radius=25, fill='white', outline='#cccccc', width=3)
    
    # Área onde a imagem será colocada (centralizada, menor que a caneca)
    area_imagem = (40, 40, largura - 40, altura - 80)  # Deixar espaço para a base
    
    # Redimensionar imagem para caber na área
    img_redim = imagem.resize((area_imagem[2] - area_imagem[0], area_imagem[3] - area_imagem[1]), 
                             Image.Resampling.LANCZOS)
    
    # Colocar imagem na caneca
    caneca.paste(img_redim, area_imagem[:2])
    
    # Adicionar base da caneca
    draw.rectangle([80, altura - 40, largura - 80, altura - 20], fill='#e0e0e0')  # Base cinza
    draw.ellipse([70, altura - 50, 90, altura - 30], fill='#e0e0e0')  # Lateral esquerda
    draw.ellipse([largura - 90, altura - 50, largura - 70, altura - 30], fill='#e0e0e0')  # Lateral direita
    
    # Adicionar alça da caneca
    draw.ellipse([largura - 50, altura // 2 - 40, largura - 10, altura // 2 + 40], 
                outline='#cccccc', width=3)
    
    return caneca

@app.route('/download/<path:file_path>')
def download(file_path):
    try:
        return send_file(file_path, as_attachment=True, download_name='canecas_personalizadas.png')
    except:
        return jsonify({'success': False, 'error': 'Arquivo não encontrado'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
