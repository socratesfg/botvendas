import asyncio
import base64
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile, FSInputFile
from aiogram.filters import Command, CommandObject
import gateway as gw

# Insira o Token do seu bot do Telegram aqui
TELEGRAM_TOKEN = "8750562442:AAHFHt4DF9ILmkOEa5HFbrpoEJcLFGtHw-A"

# ID do seu Canal VIP privado
ID_CANAL_VIP = "-1004496491614"

# O USERNAME DO SEU BOT (Sem o @)
USERNAME_DO_BOT = "santosleticia_bot"

# SEU ID PESSOAL DO TELEGRAM (Para usar o comando /publicar)
SEU_TELEGRAM_ID = 5178272021  # <--- Coloque o seu ID numérico aqui

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
async def cmd_start(message: Message, command: CommandObject):
    """Gerencia o /start normal e também quando o usuário vem do botão do canal para a vídeo chamada"""
    
    # Se o usuário veio pelo link do canal para a vídeo chamada (?start=videochamada)
    if command.args == "videochamada":
        teclado_video = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💎 Gerar Pix - R$ 80,00", callback_data="comprar_plano_videochamada")]
        ])
        
        await message.answer(
            "<b>🎥 Vídeo Chamada Privada Comigo!</b>\n\n"
            "Duração de 1 hora de conversa exclusiva e sem censura. "
            "Para garantir o seu horário, clique no botão abaixo para gerar o Pix correspondente:",
            reply_markup=teclado_video,
            parse_mode="HTML"
        )
        return

    # Fluxo normal do /start (Envia o vídeo de boas-vindas e os planos gerais)
    caminho_video = "video1.mp4"
    
    teclado = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏳ 15 Dias - R$ 18,90", callback_data="comprar_plano_15dias")],
        [InlineKeyboardButton(text="📅 Mensal - R$ 29,90", callback_data="comprar_plano_mensal")],
        [InlineKeyboardButton(text="♾️ Vitalício - R$ 43,60", callback_data="comprar_plano_vitalicio")],
        [InlineKeyboardButton(text="🎥 Video Chamada - R$ 80,00", callback_data="comprar_plano_videochamada")]
    ])
    
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
        await message.answer(legenda_boas_vindas, reply_markup=teclado, parse_mode="HTML")

# --- COMANDO EXCLUSIVO DO ADMINISTRADOR PARA PUBLICAR NO CANAL ---
@dp.message(Command("publicar"))
async def cmd_publicar_no_canal(message: Message):
    """Publica qualquer foto ou vídeo com legenda opcional e o botão que redireciona para o bot"""
    
    if message.from_user.id != SEU_TELEGRAM_ID:
        return

    teclado_canal = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🎥 Faça uma vídeo chamada comigo", 
            url=f"https://t.me/{USERNAME_DO_BOT}?start=videochamada"
        )]
    ])

    midia_reply = message.reply_to_message

    try:
        if midia_reply and midia_reply.video:
            caption = midia_reply.caption or None
            await bot.send_video(
                chat_id=ID_CANAL_VIP,
                video=midia_reply.video.file_id,
                caption=caption,
                reply_markup=teclado_canal,
                parse_mode="HTML"
            )
            await message.answer("✅ Vídeo publicado com sucesso!")

        elif midia_reply and midia_reply.photo:
            caption = midia_reply.caption or None
            await bot.send_photo(
                chat_id=ID_CANAL_VIP,
                photo=midia_reply.photo[-1].file_id,
                caption=caption,
                reply_markup=teclado_canal,
                parse_mode="HTML"
            )
            await message.answer("✅ Foto publicada com sucesso!")

        else:
            await message.answer(
                "⚠️ <b>Como usar:</b> Envie a foto ou vídeo para o bot e <b>responda a essa mídia</b> com o comando <code>/publicar</code>!"
            )

    except Exception as e:
        await message.answer(f"❌ Erro ao enviar para o canal: {e}")

@dp.callback_query(F.data.startswith("comprar_"))
async def processar_callbacks(callback: CallbackQuery):
    """Processa a seleção de qualquer plano (incluindo o clique para gerar o Pix da vídeo chamada)"""
    dados = callback.data
    plano_id = dados.replace("comprar_", "")
    
    if plano_id in PLANOS:
        plano = PLANOS[plano_id]
        valor = plano["preco"]
        descricao = plano["descricao"]
        
        await callback.message.answer(f"⏳ A gerar o Pix para: <b>{plano['nome']}</b> (R$ {valor:.2f})... Por favor, aguarde.", parse_mode="HTML")
        
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