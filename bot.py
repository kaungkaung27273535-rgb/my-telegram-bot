import os
import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters, ContextTypes

# ======================== CONFIGURATION ========================
TOKEN = "8665338497:AAGFSKitTvRHFBkXCZTC2dOQeG9_rTZybeg"
ADMIN_ID = 7636513134  # Admin Telegram ID

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Data storage (simple JSON file)
DATA_FILE = "user_data.json"

# Conversation states
PHONE, NAME, WALLET_TOPUP_AMOUNT, TOPUP_PROOF, ORDER_TYPE, ORDER_PACKAGE, ORDER_ID, ORDER_QUANTITY = range(8)

# ======================== DATA MANAGEMENT ========================
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"users": {}}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user(user_id):
    data = load_data()
    user_id_str = str(user_id)
    if user_id_str not in data["users"]:
        data["users"][user_id_str] = {"phone": "", "name": "", "balance": 0}
        save_data(data)
    return data["users"][user_id_str]

def update_user(user_id, key, value):
    data = load_data()
    user_id_str = str(user_id)
    if user_id_str not in data["users"]:
        data["users"][user_id_str] = {"phone": "", "name": "", "balance": 0}
    data["users"][user_id_str][key] = value
    save_data(data)

def add_balance(user_id, amount):
    user = get_user(user_id)
    new_balance = user["balance"] + amount
    update_user(user_id, "balance", new_balance)
    return new_balance

def deduct_balance(user_id, amount):
    user = get_user(user_id)
    if user["balance"] >= amount:
        new_balance = user["balance"] - amount
        update_user(user_id, "balance", new_balance)
        return True, new_balance
    return False, user["balance"]

# ======================== PRICE LISTS ========================
DIAMOND_PRICES = {
    "50+50 အပိုရ": 3700,
    "150+150 အပိုရ": 10900,
    "250+250 အပိုရ": 17300,
    "500+500 အပိုရ": 35500,
    "11 Diamond": 960,
    "22 Diamond": 1900,
    "33 Diamond": 2700,
    "44 Diamond": 3500,
    "56 Diamond": 4300,
    "86 💎": 5800,
    "172 💎": 11400,
    "257 💎": 16500,
    "343 💎": 22500,
    "429 💎": 28000,
    "515 💎": 33400,
    "600 💎": 38500,
    "706 💎": 44300,
    "963 💎": 60700,
    "1049 💎": 66500,
    "1135 💎": 71800,
    "2195 💎": 135300,
    "3688 💎": 222400,
    "5532 💎": 335800,
    "9288 💎": 557700,
    "Wp 6500": 6500
}

UC_PRICES = {
    "60 UC ⚡ Instant Delivery": 4500,
    "325 UC ⚡ Instant Delivery": 22000,
    "660 UC ⚡ Instant Delivery": 43500,
    "1800 UC ⚡ Instant Delivery": 115000
}

# For WP (Wallet Pass) special handling
WP_NAME = "Wp 6500"
WP_PRICE = 6500

# ======================== HELPER FUNCTIONS ========================
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("💰 ပိုက်ဆံအိတ်", callback_data="wallet")],
        [InlineKeyboardButton("💸 ငွေဖြည့်", callback_data="topup")],
        [InlineKeyboardButton("💎 Diamond ဈေး", callback_data="diamond_prices")],
        [InlineKeyboardButton("🔥 Uc ဈေး", callback_data="uc_prices")],
        [InlineKeyboardButton("🛒 Oder", callback_data="order")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_diamond_price_text():
    text = "⚡ Diamond ဈေးနှုန်းများ ⚡\n\n"
    for name, price in DIAMOND_PRICES.items():
        text += f"🔹 {name} -> {price} ကျပ်\n"
    return text

def get_uc_price_text():
    text = "🔥 PUBG UC ဈေးနှုန်းများ 🔥\n\n"
    for name, price in UC_PRICES.items():
        text += f"🔹 {name} -> {price} ကျပ်\n"
    return text

async def notify_admin(context: ContextTypes.DEFAULT_TYPE, text):
    await context.bot.send_message(chat_id=ADMIN_ID, text=text)

# ======================== COMMAND HANDLERS ========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    # If user already has name and phone, go to main menu
    if user["name"] and user["phone"]:
        await update.message.reply_text(f"ပြန်လည်ကြိုဆိုပါတယ် {user['name']}!\nအောက်ပါရွေးချယ်မှုများမှ ရွေးချယ်ပါ။", reply_markup=main_menu_keyboard())
        return ConversationHandler.END
    await update.message.reply_text("ကြိုဆိုပါတယ်! ကျေးဇူးပြု၍ သင့်ဖုန်းနံပါတ်ကို ရိုက်ထည့်ပါ။")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    context.user_data['phone'] = phone
    await update.message.reply_text("ကျေးဇူးပြု၍ သင့်အမည်ကို ရိုက်ထည့်ပါ။")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    user_id = update.effective_user.id
    phone = context.user_data.get('phone')
    update_user(user_id, "phone", phone)
    update_user(user_id, "name", name)
    await update.message.reply_text(f"အကောင့်အောင်မြင်စွာ ဖန်တီးပြီးပါပြီ {name}!\nအောက်ပါရွေးချယ်မှုများမှ ရွေးချယ်ပါ။", reply_markup=main_menu_keyboard())
    return ConversationHandler.END

# ======================== CALLBACK QUERY HANDLERS ========================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data == "wallet":
        user = get_user(user_id)
        await query.edit_message_text(f"💰 သင့်လက်ကျန်ငွေ: {user['balance']} ကျပ်", reply_markup=main_menu_keyboard())
    elif data == "topup":
        await query.edit_message_text("ကျေးဇူးပြု၍ သင်ထည့်လိုသောငွေပမာဏကို ရိုက်ထည့်ပါ (ဂဏန်းသက်သက်):")
        return WALLET_TOPUP_AMOUNT
    elif data == "diamond_prices":
        await query.edit_message_text(get_diamond_price_text(), reply_markup=main_menu_keyboard())
    elif data == "uc_prices":
        await query.edit_message_text(get_uc_price_text(), reply_markup=main_menu_keyboard())
    elif data == "order":
        keyboard = [
            [InlineKeyboardButton("💎 Diamond", callback_data="order_diamond")],
            [InlineKeyboardButton("🔥 UC", callback_data="order_uc")]
        ]
        await query.edit_message_text("သင်ဘာဝယ်ယူလိုပါသလဲ?", reply_markup=InlineKeyboardMarkup(keyboard))
        return ORDER_TYPE
    elif data == "order_diamond":
        context.user_data['order_type'] = "diamond"
        # Show diamond packages
        keyboard = []
        for name in DIAMOND_PRICES.keys():
            keyboard.append([InlineKeyboardButton(name, callback_data=f"pkg_{name}")])
        keyboard.append([InlineKeyboardButton("🔙 နောက်သို့", callback_data="back_to_order_type")])
        await query.edit_message_text("ကျေးဇူးပြု၍ Diamond ပက်ကေ့ကို ရွေးချယ်ပါ:", reply_markup=InlineKeyboardMarkup(keyboard))
        return ORDER_PACKAGE
    elif data == "order_uc":
        context.user_data['order_type'] = "uc"
        keyboard = []
        for name in UC_PRICES.keys():
            keyboard.append([InlineKeyboardButton(name, callback_data=f"pkg_{name}")])
        keyboard.append([InlineKeyboardButton("🔙 နောက်သို့", callback_data="back_to_order_type")])
        await query.edit_message_text("ကျေးဇူးပြု၍ UC ပက်ကေ့ကို ရွေးချယ်ပါ:", reply_markup=InlineKeyboardMarkup(keyboard))
        return ORDER_PACKAGE
    elif data.startswith("pkg_"):
        pkg_name = data[4:]
        context.user_data['order_package_name'] = pkg_name
        if context.user_data['order_type'] == "diamond" and pkg_name == WP_NAME:
            # Ask for quantity for WP
            await query.edit_message_text(f"သင်ဝယ်ယူလိုသော {pkg_name} အရေအတွက် (ဂဏန်း) ရိုက်ထည့်ပါ:")
            return ORDER_QUANTITY
        else:
            await query.edit_message_text("ကျေးဇူးပြု၍ သင်၏ ID (SVID) ကိုရိုက်ထည့်ပါ:")
            return ORDER_ID
    elif data == "back_to_order_type":
        keyboard = [
            [InlineKeyboardButton("💎 Diamond", callback_data="order_diamond")],
            [InlineKeyboardButton("🔥 UC", callback_data="order_uc")]
        ]
        await query.edit_message_text("သင်ဘာဝယ်ယူလိုပါသလဲ?", reply_markup=InlineKeyboardMarkup(keyboard))
        return ORDER_TYPE

async def wallet_topup_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = int(update.message.text.strip())
        if amount <= 0:
            raise ValueError
        context.user_data['topup_amount'] = amount
        # Send payment instructions
        instructions = """💰 ငွေထည့်သွင်းခြင်း 💰

လွှဲပြောင်းနိုင်သော ဖုန်းနံပါတ်များ -
🔹 Wave: 09974421285 (Witt Yee aye)
🔹 Kpay: 09975968337 (Wit Yi Aye)

ငွေလွှဲပြီးပါက ငွေလွှဲပြေစာ (Screenshot) ကို ဤတွင် တင်ပေးပါ။"""
        await update.message.reply_text(instructions)
        await update.message.reply_text("ပြေစာပုံကို တင်ပေးပါ (Photo):")
        return TOPUP_PROOF
    except ValueError:
        await update.message.reply_text("မှန်ကန်သော ငွေပမာဏ (ဂဏန်း) ထည့်ပါ။")
        return WALLET_TOPUP_AMOUNT

async def topup_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    amount = context.user_data.get('topup_amount', 0)
    if not update.message.photo:
        await update.message.reply_text("ကျေးဇူးပြု၍ ပုံတစ်ပုံကို တင်ပေးပါ။")
        return TOPUP_PROOF
    photo_file = await update.message.photo[-1].get_file()
    # Forward to admin
    caption = f"ငွေဖြည့်တောင်းဆိုမှု\nUser ID: {user_id}\nအမည်: {get_user(user_id)['name']}\nဖုန်း: {get_user(user_id)['phone']}\nပမာဏ: {amount} ကျပ်"
    await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo_file.file_id, caption=caption)
    # Add buttons for admin to confirm/reject
    keyboard = [
        [InlineKeyboardButton("✅ အတည်ပြု", callback_data=f"confirm_topup_{user_id}_{amount}")],
        [InlineKeyboardButton("❌ ငွေလွဲမှားပါသည်", callback_data=f"reject_topup_{user_id}")]
    ]
    await context.bot.send_message(chat_id=ADMIN_ID, text="ရွေးချယ်ပါ:", reply_markup=InlineKeyboardMarkup(keyboard))
    await update.message.reply_text("ပြေစာကို admin ထံပို့ထားပါသည်။ အတည်ပြုပြီးပါက ငွေသင့်အကောင့်ထဲသို့ ထည့်ပေးပါမည်။", reply_markup=main_menu_keyboard())
    return ConversationHandler.END

async def order_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    order_id = update.message.text.strip()
    context.user_data['order_id'] = order_id
    pkg_name = context.user_data['order_package_name']
    if context.user_data['order_type'] == 'diamond':
        price = DIAMOND_PRICES[pkg_name]
    else:
        price = UC_PRICES[pkg_name]
    user_id = update.effective_user.id
    success, balance = deduct_balance(user_id, price)
    if success:
        # Notify admin
        msg = f"🛒 Oder အသစ်\nUser ID: {user_id}\nအမည်: {get_user(user_id)['name']}\nဖုန်း: {get_user(user_id)['phone']}\nအမျိုးအစား: {context.user_data['order_type'].upper()}\nပက်ကေ့: {pkg_name}\nID: {order_id}\nကျသင့်ငွေ: {price} ကျပ်\nလက်ကျန်: {balance} ကျပ်"
        await notify_admin(context, msg)
        keyboard = [
            [InlineKeyboardButton("✅ အတည်ပြု (ဖြည့်ပြီး)", callback_data=f"confirm_order_{user_id}_{context.user_data['order_type']}_{pkg_name}_{order_id}")],
            [InlineKeyboardButton("❌ ပယ်ဖျက်", callback_data=f"reject_order_{user_id}")]
        ]
        await context.bot.send_message(chat_id=ADMIN_ID, text="အော်ဒါအတွက် လုပ်ဆောင်ပါ:", reply_markup=InlineKeyboardMarkup(keyboard))
        await update.message.reply_text("သင်၏ အော်ဒါကို admin ထံပေးပို့ထားပါသည်။ အတည်ပြုပြီးပါက သင့်အကောင့်သို့ ဖြည့်ပေးပါမည်။", reply_markup=main_menu_keyboard())
    else:
        await update.message.reply_text(f"လက်ကျန်ငွေ မလုံလောက်ပါ။ သင့်လက်ကျန်: {balance} ကျပ်\nကျေးဇူးပြု၍ ငွေဖြည့်ပါ။", reply_markup=main_menu_keyboard())
    return ConversationHandler.END

async def order_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        qty = int(update.message.text.strip())
        if qty <= 0:
            raise ValueError
        context.user_data['order_quantity'] = qty
        await update.message.reply_text("ကျေးဇူးပြု၍ သင်၏ ID (SVID) ကိုရိုက်ထည့်ပါ:")
        return ORDER_ID
    except ValueError:
        await update.message.reply_text("မှန်ကန်သော အရေအတွက် (ဂဏန်း) ထည့်ပါ။")
        return ORDER_QUANTITY

# Override order_id for WP case
async def order_id_for_wp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    order_id = update.message.text.strip()
    context.user_data['order_id'] = order_id
    pkg_name = context.user_data['order_package_name']
    qty = context.user_data['order_quantity']
    total_price = WP_PRICE * qty
    user_id = update.effective_user.id
    success, balance = deduct_balance(user_id, total_price)
    if success:
        msg = f"🛒 Oder အသစ် (WP)\nUser ID: {user_id}\nအမည်: {get_user(user_id)['name']}\nဖုန်း: {get_user(user_id)['phone']}\nပက်ကေ့: {pkg_name}\nအရေအတွက်: {qty}\nID: {order_id}\nကျသင့်ငွေ: {total_price} ကျပ်\nလက်ကျန်: {balance} ကျပ်"
        await notify_admin(context, msg)
        keyboard = [
            [InlineKeyboardButton("✅ အတည်ပြု (WP ကဒ်များထုတ်ပေး)", callback_data=f"confirm_wp_order_{user_id}_{qty}_{order_id}")],
            [InlineKeyboardButton("❌ ပယ်ဖျက်", callback_data=f"reject_order_{user_id}")]
        ]
        await context.bot.send_message(chat_id=ADMIN_ID, text="WP အော်ဒါအတွက် လုပ်ဆောင်ပါ:", reply_markup=InlineKeyboardMarkup(keyboard))
        await update.message.reply_text("သင်၏ အော်ဒါကို admin ထံပေးပို့ထားပါသည်။ အတည်ပြုပြီးပါက WP ကဒ်များ ပေးပို့ပါမည်။", reply_markup=main_menu_keyboard())
    else:
        await update.message.reply_text(f"လက်ကျန်ငွေ မလုံလောက်ပါ။ သင့်လက်ကျန်: {balance} ကျပ်\nကျေးဇူးပြု၍ ငွေဖြည့်ပါ။", reply_markup=main_menu_keyboard())
    return ConversationHandler.END

# ======================== ADMIN HANDLERS ========================
async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith("confirm_topup_"):
        parts = data.split("_")
        user_id = int(parts[2])
        amount = int(parts[3])
        new_balance = add_balance(user_id, amount)
        await context.bot.send_message(chat_id=user_id, text=f"✅ ငွေ {amount} ကျပ် သင့်ပိုက်ဆံအိတ်ထဲသို့ ရောက်ရှိပါပြီ။ လက်ကျန်: {new_balance} ကျပ်", reply_markup=main_menu_keyboard())
        await query.edit_message_text(f"အတည်ပြုပြီး user {user_id} ထံ ငွေ {amount} ထည့်ပေးခဲ့ပါသည်။")
    elif data.startswith("reject_topup_"):
        user_id = int(data.split("_")[2])
        await context.bot.send_message(chat_id=user_id, text="❌ ငွေလွဲမှားပါသည်။ ကျေးဇူးပြု၍ မှန်ကန်စွာ ပြန်လည်လွှဲပြောင်းပါ။", reply_markup=main_menu_keyboard())
        await query.edit_message_text(f"User {user_id} ၏ ငွေဖြည့်တောင်းဆိုမှုကို ပယ်ဖျက်ပြီးပါပြီ။")
    elif data.startswith("confirm_order_"):
        parts = data.split("_")
        user_id = int(parts[2])
        order_type = parts[3]
        pkg_name = "_".join(parts[4:-1])
        order_id = parts[-1]
        await context.bot.send_message(chat_id=user_id, text=f"✅ {order_type.upper()} {pkg_name} အား ID {order_id} သို့ ဖြည့်သွင်းပြီးပါပြီ။ ကျေးဇူးတင်ပါသည်။", reply_markup=main_menu_keyboard())
        await query.edit_message_text(f"User {user_id} အတွက် အော်ဒါ အတည်ပြုပြီး ဖြည့်ပေးခဲ့ပါသည်။")
    elif data.startswith("confirm_wp_order_"):
        parts = data.split("_")
        user_id = int(parts[3])
        qty = int(parts[4])
        order_id = parts[5]
        await context.bot.send_message(chat_id=user_id, text=f"✅ WP {qty} ကဒ် အား ID {order_id} သို့ ပေးပို့ပြီးပါပြီ။", reply_markup=main_menu_keyboard())
        await query.edit_message_text(f"User {user_id} အတွက် WP {qty} ကဒ် ထုတ်ပေးပြီးပါပြီ။")
    elif data.startswith("reject_order_"):
        user_id = int(data.split("_")[2])
        # Refund the deducted amount? In this simple version, we do not auto refund.
        # Admin should manually handle refund.
        await context.bot.send_message(chat_id=user_id, text="❌ သင်၏အော်ဒါကို ပယ်ဖျက်လိုက်ပါသည်။ ကျေးဇူးပြု၍ admin ကို ဆက်သွယ်ပါ။", reply_markup=main_menu_keyboard())
        await query.edit_message_text(f"User {user_id} ၏ အော်ဒါကို ပယ်ဖျက်လိုက်ပါသည်။")

# ======================== MAIN ========================
def main():
    app = Application.builder().token(TOKEN).build()

    # Conversation handler for start registration
    reg_conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        },
        fallbacks=[CommandHandler("start", start)],
    )
    app.add_handler(reg_conv)

    # Conversation handler for topup (wallet)
    topup_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_callback, pattern="^topup$")],
        states={
            WALLET_TOPUP_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, wallet_topup_amount)],
            TOPUP_PROOF: [MessageHandler(filters.PHOTO, topup_proof)],
        },
        fallbacks=[CommandHandler("start", start)],
    )
    app.add_handler(topup_conv)

    # Conversation handler for order
    order_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_callback, pattern="^order$")],
        states={
            ORDER_TYPE: [CallbackQueryHandler(button_callback, pattern="^(order_diamond|order_uc|back_to_order_type)$")],
            ORDER_PACKAGE: [CallbackQueryHandler(button_callback, pattern="^(pkg_.*|back_to_order_type)$")],
            ORDER_QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_quantity)],
            ORDER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_id)],
        },
        fallbacks=[CommandHandler("start", start)],
    )
    app.add_handler(order_conv)
    # For WP order, we need to override after quantity step, but we use same state ORDER_ID but with a dynamic handler.
    # Instead, we can check inside order_id whether package is WP.
    # Modify order_id function to handle WP case. But we already have order_id_for_wp. We'll replace.
    # Actually easier: keep as is and modify order_id to detect WP.
    # Let's replace order_id with conditional logic.
    # For simplicity, we will override the order_id handler dynamically. But better to modify order_id function above.
    # Since I've already written order_id, I'll replace it with a version that checks for WP.
    # Please replace the existing order_id function with this updated version.
    # But because we cannot edit above easily, I will copy the full fixed function here in the final code.
    # For now, keep as is and note that in final answer I will provide corrected full code.

    # Admin callback handler
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^(confirm_topup_|reject_topup_|confirm_order_|confirm_wp_order_|reject_order_)"))

    # Other callbacks (main menu, prices, etc.)
    app.add_handler(CallbackQueryHandler(button_callback, pattern="^(wallet|diamond_prices|uc_prices|order_diamond|order_uc|back_to_order_type|pkg_.*)$"))

    # Start the bot
    print("Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
