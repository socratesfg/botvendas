import asyncio
import base64
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile, FSInputFile
from aiogram.filters import Command
import gateway as gw

# Insira o Token do seu bot do Telegram aqui
TELEGRAM_TOKEN = "8750562442:AAHFHt4DF9ILmkOEa5HFbrpoEJcLFGtHw-A"

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Planos e preços configurados
PLANOS = {
    "plano_15dias": {
        "nome": "15 Dias de Acesso",
        "preco": 18.90,
        "descricao": "Acesso VIP por 15 dias"
    },
    "plano_mensal": {
        "nome": "Acesso Mensal",
        "preco": 29.90,
        "descricao": "Acesso VIP Mensal"
    },
    "plano_vitalicio": {
        "nome": "Acesso Vitalício",
        "preco": 43.60,
        "descricao": "Acesso VIP Vitalício Permanente"
    },
    "plano_videochamada": {
        "nome": "Videochamada Privada",
        "preco": 80.00, 
        "descricao": "1 hora em video chamada comigo!"
    }
}

@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Envia uma única mensagem contendo o vídeo com spoiler, o texto de boas-vindas e os botões dos planos"""
    
    caminho_video = "video1.mp4"
    
    # Cria os botões de seleção de planos
    teclado = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏳ 15 Dias - R$ 18,90", callback_data="comprar_plano_15dias")],
        [InlineKeyboardButton(text="📅 Mensal - R$ 29,90", callback_data="comprar_plano_mensal")],
        [InlineKeyboardButton(text="♾️ Vitalício - R$ 43,60", callback_data="comprar_plano_vitalicio")],
        [InlineKeyboardButton(text="🎥 Video Chamada - R$ 80,00", callback_data="comprar_plano_videochamada")]
    ])
    
    # Texto unificado de boas-vindas e chamada para ação
    legenda_boas_vindas = (
        "😈 <b> Veio conferir de perto, amor?</b>\n\n"
        "<i>Se você deseja me ver pelada e fazendo tudo o que você tem vontade, o meu grupo VIP é o único lugar onde posto todo tipo de conteúdo que voce imaginar.</i>\n\n"
        "Escolhe o teu plano aí embaixo e vem gozar comigo! 💦"
    )

    if os.path.exists(caminho_video):
        video_file = FSInputFile(caminho_video)
        # Envia o vídeo, a legenda e os botões TUDO NUMA SÓ MENSAGEM
        await message.answer_video(
            video=video_file,
            caption=legenda_boas_vindas,
            has_spoiler=True,
            reply_markup=teclado,
            parse_mode="HTML"
        )
    else:
        print(f"Aviso: O ficheiro '{caminho_video}' não foi encontrado. A enviar apenas texto.")
        await message.answer(legenda_boas_vindas, reply_markup=teclado, parse_mode="HTML")

@dp.callback_query(F.data.startswith("comprar_"))
async def processar_callbacks(callback: CallbackQuery):
    """Processa a seleção do plano, comunica com o ePague e envia o QR Code e o Pix Copia e Cola"""
    dados = callback.data
    plano_id = dados.replace("comprar_", "")
    
    if plano_id in PLANOS:
        plano = PLANOS[plano_id]
        valor = plano["preco"]
        descricao = plano["descricao"]
        
        await callback.message.answer(f"⏳ A gerar o Pix para: <b>{plano['nome']}</b> (R$ {valor:.2f})... Por favor, aguarde.", parse_mode="HTML")
        
        # Chama a função de geração de Pix no gateway.py
        cobranca = await gw.gerar_pix_cobranca(valor, descricao)
        
        if cobranca.get("success"):
            pix_copia_cola = cobranca.get("pix_copia_cola")
            qr_base64 = cobranca.get("qr_code_base64")
            
            # Se veio a imagem em base64, envia como foto do QR Code
            if qr_base64:
                try:
                    if "," in qr_base64:
                        qr_base64 = qr_base64.split(",")[1]
                    
                    image_data = base64.b64decode(qr_base64)
                    photo_file = BufferedInputFile(image_data, filename="qrcode.png")
                    
                    await callback.message.answer_photo(
                        photo=photo_file,
                        caption=f"✅ <b>Cobrança gerada com sucesso! ({plano['nome']})</b>\n\nEscaneie o QR Code acima ou use o código abaixo:",
                        parse_mode="HTML"
                    )
                except Exception as e:
                    print(f"Erro ao enviar foto do QR Code: {e}")
            
            # Envia o Pix Copia e Cola em formato de texto
            await callback.message.answer(
                f"📋 <b>Pix Copia e Cola:</b>\n\n"
                f"<code>{pix_copia_cola}</code>",
                parse_mode="HTML"
            )
        else:
            await callback.message.answer("❌ Ocorreu um erro ao comunicar com o gateway de pagamento. Tente novamente mais tarde.")
            
    await callback.answer()

async def main():
    print("Bot a iniciar...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot interrompido pelo utilizador.")