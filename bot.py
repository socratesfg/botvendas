import asyncio
import base64
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile, FSInputFile
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest
import gateway as gw

# Insira o Token do seu bot do Telegram aqui
TELEGRAM_TOKEN = "8750562442:AAHFHt4DF9ILmkOEa5HFbrpoEJcLFGtHw-A"

# ID do seu Canal VIP privado (substitua pelo ID real, ex: -1001234567890)
ID_CANAL_VIP = "-1001234567890"

# SEU ID PESSOAL DO TELEGRAM (Substitua pelos números fornecidos pelo @userinfobot)
SEU_TELEGRAM_ID = 5178272021

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
    
    # Cria os botões de seleção de planos do menu principal
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

# --- COMANDO EXCLUSIVO DO ADMINISTRADOR (SOMENTE VOCÊ PODE USAR) ---
@dp.message(Command("publicar"))
async def cmd_publicar_no_canal(message: Message):
    """Envia o conteúdo diretamente para o Canal VIP com o botão de vídeo chamada flutuante"""
    
    # Trava de segurança: ignora completamente se não for você enviando o comando
    if message.from_user.id != SEU_TELEGRAM_ID:
        return

    caminho_video = "video1.mp4"
    
    # Botão com o callback exclusivo para abrir o Pix flutuante
    teclado_canal = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎥 Faça uma vídeo chamada comigo", callback_data="chamada_vip_pix")]
    ])
    
    legenda = (
        "🔥 <b>Conteúdo exclusivo liberado no canal!</b>\n\n"
        "Quer conversar comigo em uma vídeo chamada privada? "
        "Clique no botão abaixo para gerar o Pix e agendar!"
    )

    try:
        if os.path.exists(caminho_video):
            video_file = FSInputFile(caminho_video)
            await bot.send_video(
                chat_id=ID_CANAL_VIP,
                video=video_file,
                caption=legenda,
                has_spoiler=True,
                reply_markup=teclado_canal,
                parse_mode="HTML"
            )
            await message.answer("✅ Publicação enviada para o canal VIP com sucesso!")
        else:
            await message.answer(f"⚠️ O ficheiro '{caminho_video}' não foi encontrado na pasta do bot.")
    except Exception as e:
        await message.answer(f"❌ Erro ao enviar para o canal: {e}")

# --- POP-UP FLUTUANTE EXCLUSIVO PARA O CANAL VIP ---
@dp.callback_query(F.data == "chamada_vip_pix")
async def processar_call_flutuante(callback: CallbackQuery):
    """Gera o Pix e exibe diretamente em um pop-up flutuante no ecrã para membros do VIP"""
    user_id = callback.from_user.id
    
    try:
        # Checa se quem clicou é realmente membro do canal VIP
        membro = await bot.get_chat_member(chat_id=ID_CANAL_VIP, user_id=user_id)
        
        if membro.status in ['creator', 'administrator', 'member']:
            plano = PLANOS["plano_videochamada"]
            
            # Gera a cobrança no gateway
            cobranca = await gw.gerar_pix_cobranca(plano["preco"], plano["descricao"])
            
            if cobranca.get("success"):
                pix_code = cobranca.get("pix_copia_cola")
                # Exibe a janela flutuante (Pop-up) com o Pix
                await callback.answer(
                    text=f"🎥 PIX VIDEOCHAMADA (R$ 80,00)\n\nCopie o código abaixo:\n\n{pix_code}",
                    show_alert=True
                )
            else:
                await callback.answer(text="❌ Erro ao gerar o Pix. Tente novamente em instantes.", show_alert=True)
        else:
            # Não é membro VIP
            await callback.answer(text="🔒 Apenas membros do Grupo VIP podem agendar vídeo chamada!", show_alert=True)
            
    except TelegramBadRequest:
        await callback.answer(text="⚠️ Ocorreu um erro ao verificar sua assinatura.", show_alert=True)


@dp.callback_query(F.data.startswith("comprar_"))
async def processar_callbacks(callback: CallbackQuery):
    """Processa a seleção dos planos padrão do /start (MANTIDO IGUAL)"""
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