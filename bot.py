import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
import qrcode
import barcode
from barcode.writer import ImageWriter

# Словарь для хранения выбора пользователя
user_choice = {}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("QR-код", callback_data='qr')],
        [InlineKeyboardButton("Штрихкод", callback_data='barcode')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выбери тип кода:", reply_markup=reply_markup)

# Обработка нажатия кнопки
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_choice[query.from_user.id] = query.data
    await query.edit_message_text(text=f"Вы выбрали {query.data}. Пришлите текст или цифры.")

# Генерация кода
async def make_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    choice = user_choice.get(update.message.from_user.id)
    
    if choice == 'qr':
        img = qrcode.make(text)
        img_file = f"qr_{update.message.from_user.id}.png"
        img.save(img_file)
        await update.message.reply_photo(photo=open(img_file, "rb"))
    elif choice == 'barcode':
        CODE39 = barcode.get_barcode_class('code39')
        bar = CODE39(text, writer=ImageWriter(), add_checksum=False)
        img_file = f"barcode_{update.message.from_user.id}.png"
        bar.save(img_file)
        await update.message.reply_photo(photo=open(f"{img_file}", "rb"))
    else:
        await update.message.reply_text("Сначала выберите тип кода командой /start")

# Запуск бота
app = ApplicationBuilder().token(os.environ["TELEGRAM_TOKEN"]).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, make_code))

app.run_polling()
