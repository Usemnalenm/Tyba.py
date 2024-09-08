import telebot
import requests
import logging
from datetime import datetime, timedelta

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)

# تهيئة البوت
bot = telebot.TeleBot('7475614869:AAH_RRrepQOF0uDTDdmPGA_EsLmrdSCp4Vc')

# قاموس لتخزين بيانات المستخدمين
user_data_dict = {}

# وظيفة للتحقق من الرصيد
def check_balance(access_token):
    url = "https://ibiza.ooredoo.dz/api/v1/mobile-bff/users/balance"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'User-Agent': "okhttp/4.9.3",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'language': "AR",
        'request-id': "995fd8a7-853c-481d-b9c6-0a24295df76a",
        'flavour-type': "gms"
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        response_json = response.json()
        accounts = response_json.get('accounts', [])
        
        for account in accounts:
            if account.get('label') == 'رصيد التكفل المهدى':
                return account.get('value')
    
    return None

# وظيفة لحساب تاريخ صلاحية الإنترنت
def get_validity_period(balance):
    if balance == '6 جيغا':
        return 'غير محدد'
    else:
        # افتراض صلاحية الإنترنت هي 7 أيام من الآن
        expiry_date = datetime.now() + timedelta(days=7)
        return expiry_date.strftime("%Y-%m-%d")

# التعامل مع أمر البدء
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    welcome_message = ('*أنت الآن مفعل في البوت من قبل المطور*')
    
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        telebot.types.InlineKeyboardButton('إرســـــــال رقــــم الهاتـــف 📱', callback_data='send_number'),
        telebot.types.InlineKeyboardButton('إرســــال لــأنــترنــت 🌐', callback_data='update_otp'),
        telebot.types.InlineKeyboardButton('لــإســـتعلام عـــن رصيـــدي 💳', callback_data='show_balance')
    )

    bot.send_message(message.chat.id, welcome_message, parse_mode='Markdown', reply_markup=markup)

# التعامل مع الاستفسارات التفاعلية
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id

    # إرسال رقم الهاتف
    if call.data == 'send_number':
        bot.send_message(call.message.chat.id, '*يرجى إرسال رقمك الآن للمتابعة العملية*', parse_mode='Markdown')

    # إرسال الإنترنت
    elif call.data == 'update_otp':
        if 'access_token' in user_data_dict.get(user_id, {}):
            balance = check_balance(user_data_dict[user_id]["access_token"])
            if balance is not None:
                bot.send_message(call.message.chat.id, (f"*رصيد التكفل المهدى قبل العملية: 🌐 {balance}*\n"
                                                        f"*التاريخ الصلاحية: {get_validity_period(balance)}*"), parse_mode='Markdown')
            else:
                bot.send_message(call.message.chat.id, "*فشل في استرداد الرصيد.*", parse_mode='Markdown')

            # إرسال الإنترنت (محاولة عدة مرات)
            success = False
            url = 'https://ibiza.ooredoo.dz/api/v1/mobile-bff/users/mgm/info/apply'
            headers = {'Authorization': f'Bearer {user_data_dict[user_id]["access_token"]}', 'Content-Type': 'application/json'}
            payload = {"mgmValue": "ABC"}
            for _ in range(6):
                response = requests.post(url, headers=headers, json=payload)
                if response.status_code == 200:
                    success = True
                    break

            if success:
                bot.send_message(call.message.chat.id, '*تم إرسال الإنترنت بنجاح!*', parse_mode='Markdown')
            else:
                bot.send_message(call.message.chat.id, "*فشل في إرسال الإنترنت.*", parse_mode='Markdown')

            # التحقق من الرصيد بعد التحديث
            balance = check_balance(user_data_dict[user_id]["access_token"])
            if balance is not None:
                bot.send_message(call.message.chat.id, (f"*رصيد التكفل المهدى بعد العملية: 🌐 {balance}*\n"
                                                        f"*التاريخ الصلاحية: {get_validity_period(balance)}*"), parse_mode='Markdown')
            else:
                bot.send_message(call.message.chat.id, "*فشل في استرداد الرصيد بعد العملية.*", parse_mode='Markdown')
        else:
            bot.send_message(call.message.chat.id, "*لم يتم تسجيل الدخول بعد. الرجاء إرسال رقم الهاتف وتأكيد الرمز.*", parse_mode='Markdown')

    # الاستعلام عن الرصيد
    elif call.data == 'show_balance':
        if 'access_token' in user_data_dict.get(user_id, {}):
            balance = check_balance(user_data_dict[user_id]["access_token"])
            if balance is not None:
                bot.send_message(call.message.chat.id, (f"*رصيد التكفل المهدى: 🌐 {balance}*\n"
                                                        f"*التاريخ الصلاحية: {get_validity_period(balance)}*"), parse_mode='Markdown')
            else:
                bot.send_message(call.message.chat.id, "*فشل في استرداد الرصيد.*", parse_mode='Markdown')
        else:
            bot.send_message(call.message.chat.id, "*لم يتم تسجيل الدخول بعد. الرجاء إرسال رقم الهاتف وتأكيد الرمز.*", parse_mode='Markdown')

# التعامل مع الرسائل
@bot.message_handler(func=lambda message: message.text and not message.text.startswith('/'))
def handle_message(message):
    user_id = message.from_user.id
    user_input = message.text

    if user_id in user_data_dict and user_data_dict[user_id].get('awaiting_otp', False):
        otp = user_input
        num = user_data_dict[user_id]['num']

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'client_id': 'ibiza-app',
            'otp': otp,
            'grant_type': 'password',
            'mobile-number': num,
            'language': 'AR',
        }
        response = requests.post('https://ibiza.ooredoo.dz/auth/realms/ibiza/protocol/openid-connect/token', headers=headers, data=data)

        if response.status_code == 200:
            access_token = response.json().get('access_token')
            if access_token:
                bot.reply_to(message, '*تم التحقق من الرمز بنجاح. يتم الآن التحقق من الإنترنت.*', parse_mode='Markdown')
                user_data_dict[user_id]['access_token'] = access_token
                user_data_dict[user_id]['awaiting_otp'] = False

                balance = check_balance(access_token)
                if balance is not None:
                    bot.send_message(message.chat.id, (f"*رصيد التكفل المهدى قبل العملية: 🌐 {balance}*\n"
                                                        f"*التاريخ الصلاحية: {get_validity_period(balance)}*"), parse_mode='Markdown')
                else:
                    bot.send_message(message.chat.id, "*فشل في استرداد الرصيد.*", parse_mode='Markdown')
            else:
                bot.reply_to(message, "*فشل في التحقق من الرمز.*", parse_mode='Markdown')
        else:
            bot.reply_to(message, "*فشل في إرسال رمز التحقق. يرجى المحاولة مرة أخرى.*", parse_mode='Markdown')

    else:
        num = user_input
        user_data_dict[user_id] = {'num': num}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'client_id': 'ibiza-app',
            'grant_type': 'password',
            'mobile-number': num,
            'language': 'AR',
        }
        response = requests.post('https://ibiza.ooredoo.dz/auth/realms/ibiza/protocol/openid-connect/token', headers=headers, data=data)

        if response.status_code == 200:
            bot.reply_to(message, '*تم إرسال رمز التحقق إلى جوالك. يرجى إدخال رمز التحقق.*', parse_mode='Markdown')
            user_data_dict[user_id]['awaiting_otp'] = True
        else:
            bot.reply_to(message, "*فشل في إرسال رمز التحقق. يرجى المحاولة مرة أخرى.*", parse_mode='Markdown')

# بدء تشغيل البوت
if __name__ == '__main__':
    bot.polling(none_stop=True)