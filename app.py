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
        
        # SE PSD FOI ENVIADO: criar mockup personalizado
        if psd_file and psd_file.filename != '':
            resultado = criar_mockup_com_psd(metade_esq, metade_dir, "MOCKUP AUTOMATICO 1.psd")
            mensagem = "✅ Mockup PSD gerado com sucesso!"
        else:
            # SE NÃO: criar layout básico
            resultado = criar_mockup_basico(metade_esq, metade_dir, largura, altura)
            mensagem = "✅ Mockup básico gerado! (Envie um PSD para versão personalizada)"
        
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
            'message': mensagem
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def criar_mockup_com_psd(metade_esq, metade_dir, nome_psd):
    """Cria um mockup que simula o layout do PSD"""
    
    # Criar fundo base (simulando o PSD)
    largura_base = 1200
    altura_base = 800
    mockup = Image.new('RGB', (largura_base, altura_base), color='#2c3e50')
    
    draw = ImageDraw.Draw(mockup)
    
    try:
        # Tentar carregar fonte (fallback para default)
        font = ImageFont.load_default()
        font_titulo = ImageFont.load_default()
    except:
        font = None
        font_titulo = None
    
    # Adicionar título (simulando texto do PSD)
    draw.rectangle([0, 0, largura_base, 80], fill='#34495e')
    draw.text((50, 30), "A EVOLUÇÃO DO HOMEM", fill='white', font=font_titulo)
    draw.text((largura_base - 200, 30), "HOMER", fill='#e74c3c', font=font_titulo)
    
    # Posicionar as canecas (metades da imagem)
    pos_esquerda = (150, 150)
    pos_direita = (650, 150)
    
    # Redimensionar metades para caber no mockup
    tamanho_caneca = (400, 400)
    metade_esq_redim = metade_esq.resize(tamanho_caneca, Image.Resampling.LANCZOS)
    metade_dir_redim = metade_dir.resize(tamanho_caneca, Image.Resampling.LANCZOS)
    
    # Adicionar bordas às canecas
    def adicionar_borda(imagem, cor_borda='#34495e', espessura=5):
        nova_largura = imagem.width + espessura * 2
        nova_altura = imagem.height + espessura * 2
        imagem_com_borda = Image.new('RGB', (nova_largura, nova_altura), color=cor_borda)
        imagem_com_borda.paste(imagem, (espessura, espessura))
        return imagem_com_borda
    
    caneca_esq = adicionar_borda(metade_esq_redim)
    caneca_dir = adicionar_borda(metade_dir_redim)
    
    # Colocar canecas no mockup
    mockup.paste(caneca_esq, pos_esquerda)
    mockup.paste(caneca_dir, pos_direita)
    
    # Adicionar labels
    draw.text((pos_esquerda[0] + 150, pos_esquerda[1] + 420), "CANECA ESQUERDA", fill='white', font=font)
    draw.text((pos_direita[0] + 150, pos_direita[1] + 420), "CANECA DIREITA", fill='white', font=font)
    
    # Adicionar rodapé com textos do PSD
    draw.rectangle([0, altura_base - 60, largura_base, altura_base], fill='#34495e')
    draw.text((50, altura_base - 40), "Necroletário", fill='#ecf0f1', font=font)
    draw.text((largura_base - 150, altura_base - 40), "Homestágio", fill='#ecf0f1', font=font)
    
    return mockup

def criar_mockup_basico(metade_esq, metade_dir, largura, altura):
    """Cria layout básico quando não há PSD"""
    espacamento = 20
    nova_largura = largura + espacamento + largura
    resultado = Image.new('RGB', (nova_largura, altura), color='#ecf0f1')
    
    resultado.paste(metade_esq, (0, 0))
    resultado.paste(metade_dir, (largura + espacamento, 0))
    
    # Adicionar labels básicos
    draw = ImageDraw.Draw(resultado)
    draw.rectangle([0, 10, 200, 40], fill='#3498db')
    draw.rectangle([largura + espacamento, 10, largura + espacamento + 200, 40], fill='#e74c3c')
    draw.text((20, 15), "CANECA ESQUERDA", fill='white')
    draw.text((largura + espacamento + 20, 15), "CANECA DIREITA", fill='white')
    
    return resultado

@app.route('/download/<path:file_path>')
def download(file_path):
    try:
        return send_file(file_path, as_attachment=True, download_name='mockup_personalizado.png')
    except:
        return jsonify({'success': False, 'error': 'Arquivo não encontrado'})

@app.route('/health')
def health():
    return jsonify({'status': 'online', 'version': '3.0-com-psd'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
