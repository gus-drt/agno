import asyncio
import logging
import html
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import TELEGRAM_BOT_TOKEN, ALLOWED_USER_ID, get_current_mode, set_current_mode
from agent_runner import agent_runner
from memory_manager import memory_manager
from telegram_formatter import markdown_to_telegram_html, sanitize_text

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if ALLOWED_USER_ID and user_id != ALLOWED_USER_ID:
        await update.message.reply_text("Acesso negado.")
        return
    await update.message.reply_text(
        "👋 <b>Olá! Eu sou o Agno.</b>\n\n"
        "Você pode alternar os modos de inteligência usando:\n"
        "• <code>/mode sdk</code> (Google Antigravity SDK)\n"
        "• <code>/mode cli</code> (Terminal CLI)\n\n"
        "Use <code>/status</code> para checar o modo atual.",
        parse_mode="HTML"
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if ALLOWED_USER_ID and user_id != ALLOWED_USER_ID:
        return
    current_mode = get_current_mode()
    await update.message.reply_text(
        f"⚙️ Modo atual do Agente: <b>{current_mode.upper()}</b>",
        parse_mode="HTML"
    )

async def mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if ALLOWED_USER_ID and user_id != ALLOWED_USER_ID:
        return
        
    if not context.args:
        await update.message.reply_text("Uso correto: <code>/mode sdk</code> ou <code>/mode cli</code>", parse_mode="HTML")
        return
        
    new_mode = context.args[0].lower()
    if new_mode not in ["sdk", "cli"]:
        await update.message.reply_text("Modo inválido. Escolha <code>sdk</code> ou <code>cli</code>.", parse_mode="HTML")
        return
        
    set_current_mode(new_mode)
    
    try:
        await agent_runner.switch_mode(new_mode)
        await update.message.reply_text(f"✅ Modo alterado com sucesso para: <b>{new_mode.upper()}</b>", parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao iniciar o modo {new_mode.upper()}: {str(e)}\n\n(Dica: verifique se as credenciais no .env estão corretas!)")

async def safe_edit_text(message, text: str):
    """
    Tenta formatar e editar a mensagem usando HTML elegante do Telegram.
    Se a API do Telegram falhar por entidade aberta ou formato, faz fallback seguro para texto limpo.
    """
    clean = sanitize_text(text)
    if not clean:
        return
        
    formatted = markdown_to_telegram_html(text)
    try:
        await message.edit_text(formatted, parse_mode="HTML")
    except Exception:
        try:
            await message.edit_text(clean)
        except Exception:
            pass

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if ALLOWED_USER_ID and user_id != ALLOWED_USER_ID:
        return

    user_text = update.message.text
    reply_msg = await update.message.reply_text("⏳ Processando...")
    
    current_text = ""
    last_edit_time = asyncio.get_event_loop().time()
    buffer = ""
    tool_msg = None
    tool_text = ""
    
    try:
        async for item in agent_runner.chat_stream(user_text):
            if item["type"] == "token":
                buffer += item["content"]
                current_text += item["content"]
                
                # Se exceder o limite seguro do Telegram (~3900 caracteres), inicia nova mensagem
                if len(current_text) > 3900:
                    await safe_edit_text(reply_msg, current_text)
                    reply_msg = await update.message.reply_text("...")
                    current_text = ""
                    buffer = ""
                    last_edit_time = asyncio.get_event_loop().time()
                    continue
                
                now = asyncio.get_event_loop().time()
                # Atualização a cada 1.2 segundos para garantir fluidez e evitar rate limit
                if now - last_edit_time > 1.2 and buffer:
                    await safe_edit_text(reply_msg, current_text)
                    last_edit_time = now
                    buffer = ""
                    
            elif item["type"] == "tool_call":
                tool_text += f"{html.escape(item['content'])}\n"
                if not tool_msg:
                    tool_msg = await update.message.reply_text(f"<i>{tool_text}</i>", parse_mode="HTML")
                else:
                    try:
                        await tool_msg.edit_text(f"<i>{tool_text}</i>", parse_mode="HTML")
                    except Exception:
                        pass
                
            elif item["type"] == "error":
                await update.message.reply_text(f"⚠️ Erro no agente: {item['content']}")
                
        if current_text:
            await safe_edit_text(reply_msg, current_text)
        else:
            # Caso a resposta tenha sido apenas execução de ferramentas sem texto
            clean_check = sanitize_text(current_text)
            if not clean_check:
                try:
                    await reply_msg.edit_text("✅ Operação concluída.")
                except Exception:
                    pass
            
        memory_manager.log_interaction("agent", sanitize_text(current_text))
            
    except Exception as e:
        await update.message.reply_text(f"Ocorreu um erro na comunicação: {e}")

async def bot_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Exceção capturada no handler do Telegram:", exc_info=context.error)

async def run_bot():
    await agent_runner.start()
    
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("mode", mode_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(bot_error_handler)
    
    print("Bot do Telegram iniciado...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    # Loop infinito para manter a aplicação viva
    stop_signal = asyncio.Event()
    await stop_signal.wait()
