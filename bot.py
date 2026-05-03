from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import json
import os

TOKEN = "8763686384:AAGOStovIU4x_DKhkxq05DYqZtWKoN2HkB8"
ADMIN_ID =5543035961

# 📁 Mahsulotlarni yuklash
if os.path.exists("products.json"):
    with open("products.json", "r") as f:
        products = json.load(f)
else:
    products = []

admin_step = {}
temp_product = {}

# 💾 Saqlash funksiyasi
def save_products():
    with open("products.json", "w") as f:
        json.dump(products, f)

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🛍 Mahsulotlar"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text("Do‘konga xush kelibsiz!", reply_markup=reply_markup)

# MENU
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not products:
        await update.message.reply_text("Hozircha mahsulot yo‘q 😔")
        return

    for i, item in enumerate(products):
        keyboard = [
            [InlineKeyboardButton("🛒 Buyurtma berish", callback_data=f"buy_{i}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=item["photo"],
            caption=f"{item['name']}\n💰 {item['price']}",
            reply_markup=reply_markup
        )

# BUTTON
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    index = int(query.data.split("_")[1])
    context.user_data["product"] = products[index]

    await query.message.reply_text("Ismingizni yozing:")
    context.user_data["step"] = "name"

# ADD (faqat admin)
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ADMIN_ID:
        return
    
    admin_step[update.effective_chat.id] = "name"
    await update.message.reply_text("Mahsulot nomini yozing:")

# MESSAGE HANDLER
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id

    # ADMIN QO‘SHISH
    if user_id == ADMIN_ID and user_id in admin_step:
        step = admin_step[user_id]

        if step == "name":
            temp_product["name"] = update.message.text
            admin_step[user_id] = "price"
            await update.message.reply_text("Narxini yozing:")
            return

        elif step == "price":
            temp_product["price"] = update.message.text
            admin_step[user_id] = "photo"
            await update.message.reply_text("Rasm yuboring:")
            return

        elif step == "photo":
            if update.message.photo:
                photo = update.message.photo[-1].file_id
                temp_product["photo"] = photo

                products.append(temp_product.copy())
                save_products()  # 💾 saqlash

                admin_step.pop(user_id)
                temp_product.clear()

                await update.message.reply_text("✅ Mahsulot qo‘shildi!")
            else:
                await update.message.reply_text("Iltimos rasm yuboring!")
            return

    # BUYURTMA
    if "step" not in context.user_data:
        return

    if context.user_data["step"] == "name":
        context.user_data["name"] = update.message.text
        await update.message.reply_text("Telefon raqamingizni yozing:")
        context.user_data["step"] = "phone"

    elif context.user_data["step"] == "phone":
        context.user_data["phone"] = update.message.text

        product = context.user_data["product"]

        text = f"""🛒 Yangi buyurtma!

👤 Ism: {context.user_data['name']}
📞 Tel: {context.user_data['phone']}

📦 Mahsulot: {product['name']}
💰 Narx: {product['price']}
"""

        await context.bot.send_message(chat_id=ADMIN_ID, text=text)

        await update.message.reply_text("✅ Buyurtma qabul qilindi!")
        context.user_data.clear()

# APP
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add", add))
app.add_handler(CallbackQueryHandler(button))

app.add_handler(MessageHandler(filters.Regex("^🛍 Mahsulotlar$"), menu))
app.add_handler(MessageHandler(filters.ALL, message_handler))

print("Bot ishlayapti...")
app.run_polling()
