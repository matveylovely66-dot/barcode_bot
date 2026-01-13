await start(update, context)
        return

    if query.data == 'qr':
        user_choice[query.from_user.id] = 'qr'
        await qr_submenu(update, context)
    elif query.data == 'barcode':
        user_choice[query.from_user.id] = 'barcode'
        await barcode_submenu(update, context)
    elif query.data.startswith('color_'):
        sub_choice[query.from_user.id] = query.data
        await query.edit_message_text(f"Вы выбрали {query.data.replace('color_', '')} цвет! Пришлите текст или ссылку для QR.")
    elif query.data.startswith('type_'):
        sub_choice[query.from_user.id] = query.data
        await query.edit_message_text(f"Вы выбрали {query.data.replace('type_', '')} тип. Пришлите цифры для штрихкода.")
    elif query.data == 'help':
        await help_submenu(update, context)
    elif query.data == 'profile':
        await profile(update, context)

# ---------- Генерация кода ----------
async def make_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    choice = user_choice.get(update.message.from_user.id)

    if choice == 'qr':
        color = sub_choice.get(update.message.from_user.id, 'color_purple')
        fill, back = ('purple', 'yellow') if color == 'color_purple' else \
                     ('yellow', 'purple') if color == 'color_yellow' else ('black', 'white')

        qr = qrcode.QRCode(box_size=10, border=4)
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color=fill, back_color=back)
        img_file = f"qr_{update.message.from_user.id}.png"
        img.save(img_file)
        await update.message.reply_photo(photo=open(img_file, "rb"), caption="✨ Вот твой QR-код!")

    elif choice == 'barcode':
        b_type = sub_choice.get(update.message.from_user.id, 'type_39')
        if b_type == 'type_39':
            CODE = barcode.get_barcode_class('code39')
        elif b_type == 'type_128':
            CODE = barcode.get_barcode_class('code128')
        else:
            CODE = barcode.get_barcode_class('ean13')
        bar = CODE(text, writer=ImageWriter(), add_checksum=False)
        img_file = f"barcode_{update.message.from_user.id}.png"
        bar.save(img_file)
        await update.message.reply_photo(photo=open(img_file, "rb"), caption="📦 Вот твой Штрихкод!")

    else:
        await update.message.reply_text("Сначала выберите тип кода командой /start 🎯")
        return

    # Увеличиваем статистику и сохраняем
    user_id = str(update.message.from_user.id)
    user_stats[user_id] = user_stats.get(user_id, 0) + 1
    save_stats()

# ---------- Основной запуск ----------
async def set_commands(app):
    commands = [
        BotCommand("start", "Главное меню бота"),
        BotCommand("help", "Помощь и информация"),
        BotCommand("profile", "Профиль пользователя")
    ]
    await app.bot.set_my_commands(commands)

app = ApplicationBuilder().token(os.environ["TELEGRAM_TOKEN"]).build()

# Установка команд меню
import asyncio
asyncio.run(set_commands(app))

# Обработчики
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, make_code))

# Запуск бота
app.run_polling()
