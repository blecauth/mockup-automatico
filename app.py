from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from PIL import Image, ImageDraw, ImageOps
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
        
        # Criar mockup com canecas personalizadas
        resultado = criar_mockup_canecas(metade_esq, metade_dir)
        
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
            'message': '✅ Canecas personalizadas geradas com sucesso!'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def criar_mockup_canecas(imagem_esq, imagem_dir):
    """Cria mockup com canecas personalizadas aplicando as imagens nas áreas brancas"""
    
    # Criar canvas principal (base do seu PSD)
    largura = 1000
    altura = 800
    canvas = Image.new('RGB', (largura, altura), color='#1e1e1e')
    draw = ImageDraw.Draw(canvas)
    
    # === CABEÇALHO (do seu PSD) ===
    draw.rectangle([0, 0, largura, 80], fill='#2d2d2d')
    draw.text((50, 25), "A EVOLUÇÃO DO HOMEM", fill='white')
    draw.text((largura - 150, 25), "HOMER", fill='#ff4444')
    
    # === CRIAR CANECAS PERSONALIZADAS ===
    
    # Tamanho das áreas das canecas
    largura_caneca = 350
    altura_caneca = 450
    
    # Redimensionar imagens para caber nas canecas
    img_esq_redim = imagem_esq.resize((largura_caneca, altura_caneca), Image.Resampling.LANCZOS)
    img_dir_redim = imagem_dir.resize((largura_caneca, altura_caneca), Image.Resampling.LANCZOS)
    
    # Posições das canecas
    pos_esq = (80, 120)
    pos_dir = (530, 120)
    
    # === CANECA ESQUERDA PERSONALIZADA ===
    caneca_esq = criar_caneca_personalizada(img_esq_redim, pos_esq)
    canvas.paste(caneca_esq, pos_esq, caneca_esq)  # Usar máscara alpha
    
    # === CANECA DIREITA PERSONALIZADA ===
    caneca_dir = criar_caneca_personalizada(img_dir_redim, pos_dir)
    canvas.paste(caneca_dir, pos_dir, caneca_dir)  # Usar máscara alpha
    
    # === ADICIONAR EFEITO 3D/ILUMINAÇÃO ÀS CANECAS ===
    adicionar_efeito_caneca(canvas, pos_esq, largura_caneca, altura_caneca)
    adicionar_efeito_caneca(canvas, pos_dir, largura_caneca, altura_caneca)
    
    # === LABELS ===
    draw.text((pos_esq[0] + 100, pos_esq[1] + altura_caneca + 20), "CANECA ESQUERDA", fill='#ccc')
    draw.text((pos_dir[0] + 100, pos_dir[1] + altura_caneca + 20), "CANECA DIREITA", fill='#ccc')
    
    # === RODAPÉ (do seu PSD) ===
    draw.rectangle([0, altura - 60, largura, altura], fill='#2d2d2d')
    draw.text((50, altura - 40), "Necroletário", fill='#aaa')
    draw.text((largura - 150, altura - 40), "Homestágio", fill='#aaa')
    
    return canvas

def criar_caneca_personalizada(imagem, posicao):
    """Cria uma caneca personalizada aplicando a imagem em formato de caneca"""
    
    largura, altura = imagem.size
    
    # Criar máscara em formato de caneca (área branca do seu PSD)
    mascara = Image.new('L', (largura, altura), 0)
    draw_mascara = ImageDraw.Draw(mascara)
    
    # Desenhar formato de caneca (retângulo com bordas arredondadas + alça)
    
    # Corpo principal da caneca (retângulo arredondado)
    draw_mascara.rounded_rectangle([10, 10, largura - 10, altura - 60], 
                                 radius=20, fill=255)
    
    # Alça da caneca
    draw_mascara.ellipse([largura - 40, altura//2 - 30, largura - 10, altura//2 + 30], fill=255)
    draw_mascara.rectangle([largura - 40, altura//2 - 30, largura - 25, altura//2 + 30], fill=255)
    
    # Aplicar máscara à imagem
    imagem_com_mascara = Image.new('RGBA', (largura, altura))
    imagem_com_mascara.paste(imagem, (0, 0), mascara)
    
    return imagem_com_mascara

def adicionar_efeito_caneca(canvas, posicao, largura, altura):
    """Adiciona efeitos de iluminação e sombra para dar aspecto 3D"""
    draw = ImageDraw.Draw(canvas, 'RGBA')
    
    x, y = posicao
    
    # Sombra suave atrás da caneca
    for i in range(5):
        draw.rounded_rectangle(
            [x - i, y - i, x + largura + i, y + altura + i],
            radius=25, outline=(0, 0, 0, 30)
        )
    
    # Realce de luz (efeito 3D)
    draw.rounded_rectangle(
        [x + 5, y + 5, x + largura - 5, y + 15],
        radius=10, fill=(255, 255, 255, 80)
    )

@app.route('/download/<path:file_path>')
def download(file_path):
    try:
        return send_file(file_path, as_attachment=True, download_name='canecas_personalizadas.png')
    except:
        return jsonify({'success': False, 'error': 'Arquivo não encontrado'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
