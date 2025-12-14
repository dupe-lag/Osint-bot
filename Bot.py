import logging
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import requests
from bs4 import BeautifulSoup
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
import socket
import urllib.parse

TOKEN = "7983638744:AAH4g6JSpc2Vh48FNz3_z97Ua8Kqwv6klPc"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔍 Search by Username", callback_data='osint_username')],
        [InlineKeyboardButton("🌐 Website Parsing", callback_data='parse_website')],
        [InlineKeyboardButton("📡 IP Information", callback_data='ip_info')],
        [InlineKeyboardButton("📚 Wikipedia Search", callback_data='wiki_search')],
        [InlineKeyboardButton("🔎 Phone Lookup", callback_data='phone_lookup')],
        [InlineKeyboardButton("👤 VK Parsing", callback_data='vk_parse')],
        [InlineKeyboardButton("🆔 VK ID by Username", callback_data='vk_id')],
        [InlineKeyboardButton("📱 Telegram ID", callback_data='tg_id')],
        [InlineKeyboardButton("🌐 Useful Sites", callback_data='useful_sites')],
        [InlineKeyboardButton("🤖 Useful Bots", callback_data='useful_bots')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        "🕵️ *OSINT Parsing Bot*\n\n"
        "Choose an option from the menu:\n\n"
        "• *Search by Username* - search accounts by username\n"
        "• *Website Parsing* - extract data from web pages\n"
        "• *IP Information* - geolocation and IP info\n"
        "• *Wikipedia Search* - search information on Wikipedia\n"
        "• *Phone Lookup* - info about a phone number\n"
        "• *VK Parsing* - VK profile info\n"
        "• *VK ID by Username* - get VK ID by username\n"
        "• *Telegram ID* - get Telegram ID by username\n"
        "• *Useful Sites* - list of OSINT sites\n"
        "• *Useful Bots* - list of OSINT bots"
    )
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)

async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if query.data == 'osint_username':
        user_data[user_id] = {'action': 'osint_username'}
        await query.edit_message_text("Enter the username to search:")
    
    elif query.data == 'parse_website':
        user_data[user_id] = {'action': 'parse_website'}
        await query.edit_message_text("Enter the website URL to parse:")
    
    elif query.data == 'ip_info':
        user_data[user_id] = {'action': 'ip_info'}
        await query.edit_message_text("Enter the IP address to check:")
    
    elif query.data == 'wiki_search':
        user_data[user_id] = {'action': 'wiki_search'}
        await query.edit_message_text("Enter the search query for Wikipedia:")
    
    elif query.data == 'phone_lookup':
        user_data[user_id] = {'action': 'phone_lookup'}
        await query.edit_message_text("Enter the phone number (with country code):")
    
    elif query.data == 'vk_parse':
        user_data[user_id] = {'action': 'vk_parse'}
        await query.edit_message_text("Enter VK username or ID:")
    
    elif query.data == 'vk_id':
        user_data[user_id] = {'action': 'vk_id'}
        await query.edit_message_text("Enter VK username to get ID:")
    
    elif query.data == 'tg_id':
        user_data[user_id] = {'action': 'tg_id'}
        await query.edit_message_text("Enter Telegram username (without @):")
    
    elif query.data == 'useful_sites':
        await useful_sites(update, context)
    
    elif query.data == 'useful_bots':
        await useful_bots(update, context)
    
    elif query.data == 'back_to_menu':
        await show_main_menu(update, context)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔍 Search by Username", callback_data='osint_username')],
        [InlineKeyboardButton("🌐 Website Parsing", callback_data='parse_website')],
        [InlineKeyboardButton("📡 IP Information", callback_data='ip_info')],
        [InlineKeyboardButton("📚 Wikipedia Search", callback_data='wiki_search')],
        [InlineKeyboardButton("🔎 Phone Lookup", callback_data='phone_lookup')],
        [InlineKeyboardButton("👤 VK Parsing", callback_data='vk_parse')],
        [InlineKeyboardButton("🆔 VK ID by Username", callback_data='vk_id')],
        [InlineKeyboardButton("📱 Telegram ID", callback_data='tg_id')],
        [InlineKeyboardButton("🌐 Useful Sites", callback_data='useful_sites')],
        [InlineKeyboardButton("🤖 Useful Bots", callback_data='useful_bots')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text("🕵️ Choose an action:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("🕵️ Choose an action:", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()
    
    if user_id not in user_data:
        await update.message.reply_text("Please select an action from the menu.")
        return
    
    action = user_data[user_id]['action']
    
    if action == 'osint_username':
        await username_search(update, text)
    elif action == 'parse_website':
        await website_parse(update, text)
    elif action == 'ip_info':
        await ip_info(update, text)
    elif action == 'wiki_search':
        await wiki_search(update, text)
    elif action == 'phone_lookup':
        await phone_lookup(update, text)
    elif action == 'vk_parse':
        await vk_parse(update, text)
    elif action == 'vk_id':
        await vk_get_id(update, text)
    elif action == 'tg_id':
        await tg_get_id(update, text)
    
    keyboard = [[InlineKeyboardButton("⬅️ Back to Menu", callback_data='back_to_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose next action:", reply_markup=reply_markup)

# ----------------- OSINT Functions -----------------
async def username_search(update: Update, username):
    try:
        platforms = {
            "GitHub": f"https://github.com/{username}",
            "Twitter": f"https://twitter.com/{username}",
            "Instagram": f"https://instagram.com/{username}",
            "Reddit": f"https://reddit.com/user/{username}",
            "Steam": f"https://steamcommunity.com/id/{username}",
            "Vk": f"https://vk.com/{username}",
            "Facebook": f"https://facebook.com/{username}",
            "LinkedIn": f"https://linkedin.com/in/{username}",
            "Pinterest": f"https://pinterest.com/{username}",
            "SoundCloud": f"https://soundcloud.com/{username}",
            "Telegram": f"https://t.me/{username}",
            "YouTube": f"https://youtube.com/@{username}",
            "Twitch": f"https://twitch.tv/{username}",
            "TikTok": f"https://tiktok.com/@{username}",
            "Spotify": f"https://open.spotify.com/user/{username}",
            "Medium": f"https://medium.com/@{username}"
        }
        results = []
        headers = {'User-Agent': 'Mozilla/5.0'}
        for platform, url in platforms.items():
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    if platform == "Instagram":
                        if "Sorry, this page isn't available." not in response.text:
                            results.append(f"✅ {platform}: {url}")
                        else:
                            results.append(f"❌ {platform}: not found")
                    elif platform == "Twitter":
                        if "This account has been suspended" not in response.text and "Page not found" not in response.text:
                            results.append(f"✅ {platform}: {url}")
                        else:
                            results.append(f"❌ {platform}: not found")
                    else:
                        results.append(f"✅ {platform}: {url}")
                else:
                    results.append(f"❌ {platform}: not found")
            except:
                results.append(f"❌ {platform}: error checking")
        result_text = f"🔍 *Search results for {username}:*\n\n" + "\n".join(results)
        await update.message.reply_text(result_text, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Error during search: {str(e)}")

async def website_parse(update: Update, url):
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else "Not found"
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc['content'] if meta_desc else "No description"
        links = soup.find_all('a', href=True)
        external_links = [a['href'] for a in links if a['href'].startswith('http')]
        result_text = (
            f"🌐 *Parsing results:* {url}\n\n"
            f"📝 *Title:* {title}\n\n"
            f"📄 *Description:* {description}\n\n"
            f"🔗 *Total links found:* {len(links)}\n"
            f"🌍 *External links:* {len(external_links)}"
        )
        await update.message.reply_text(result_text, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Error parsing website: {str(e)}")

async def ip_info(update: Update, ip):
    try:
        try:
            socket.inet_aton(ip)
        except socket.error:
            await update.message.reply_text("❌ Invalid IP format")
            return
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            whois_url = f"https://www.whois.com/whois/{ip}"
            response = requests.get(whois_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            whois_data = soup.find('pre', {'class': 'df-raw'})
            if whois_data:
                whois_text = whois_data.text[:500] + "..." if len(whois_data.text) > 500 else whois_data.text
                result_text = f"📡 *IP Information:* {ip}\n\n```\n{whois_text}\n```"
            else:
                result_text = f"📡 *IP Information:* {ip}\n\nCould not get WHOIS info"
            await update.message.reply_text(result_text, parse_mode='Markdown')
        except:
            await update.message.reply_text("❌ Could not retrieve IP information")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def wiki_search(update: Update, query):
    try:
        search_url = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(query)}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        if soup.find('div', {'id': 'noarticletext'}):
            await update.message.reply_text("❌ Article not found on Wikipedia")
            return
        title = soup.find('h1', {'id': 'firstHeading'})
        page_title = title.text if title else query
        content = soup.find('div', {'id': 'mw-content-text'})
        if content:
            first_paragraph = content.find('p')
            summary = first_paragraph.text[:1000] + "..." if first_paragraph and len(first_paragraph.text) > 1000 else first_paragraph.text if first_paragraph else "Could not extract content"
        else:
            summary = "Could not extract content"
        result_text = f"📚 *Wikipedia: {page_title}*\n\n{summary}\n\n🔗 *Link:* {search_url}"
        await update.message.reply_text(result_text, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Wikipedia search error: {str(e)}")

async def phone_lookup(update: Update, phone_number):
    try:
        parsed_number = phonenumbers.parse(phone_number, None)
        if not phonenumbers.is_valid_number(parsed_number):
            await update.message.reply_text("❌ Invalid phone number")
            return
        carrier_name = carrier.name_for_number(parsed_number, "en")
        region = geocoder.description_for_number(parsed_number, "en")
        time_zones = timezone.time_zones_for_number(parsed_number)
        result_text = (
            f"📞 *Phone Information:* {phone_number}\n\n"
            f"📱 *Carrier:* {carrier_name if carrier_name else 'Unknown'}\n"
            f"🌍 *Region:* {region if region else 'Unknown'}\n"
            f"🕐 *Time zone:* {', '.join(time_zones) if time_zones else 'Unknown'}\n"
            f"✅ *Valid:* {'Yes' if phonenumbers.is_valid_number(parsed_number) else 'No'}\n"
            f"🌐 *Possible number:* {'Yes' if phonenumbers.is_possible_number(parsed_number) else 'No'}"
        )
        await update.message.reply_text(result_text, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Error checking phone: {str(e)}")

# ----------------- VK and Telegram -----------------
async def vk_parse(update: Update, username):
    try:
        user_id = await get_vk_id(username)
        if not user_id:
            await update.message.reply_text("❌ VK user not found")
            return
        url = f"https://vk.com/{username}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('title')
        profile_name = title.text.split('|')[0].strip() if title else "Unknown"
        followers_match = re.search(r'(\d+)\s*followers', response.text)
        friends_match = re.search(r'(\d+)\s*friends', response.text)
        photos_match = re.search(r'(\d+)\s*photos', response.text)
        followers_text = followers_match.group(1) if followers_match else "Unknown"
        friends_text = friends_match.group(1) if friends_match else "Unknown"
        photos_text = photos_match.group(1) if photos_match else "Unknown"
        result_text = (
            f"👤 *VK Profile Information:*\n\n"
            f"📛 *Name:* {profile_name}\n"
            f"🆔 *ID:* {user_id}\n"
            f"👥 *Followers:* {followers_text}\n"
            f"🤝 *Friends:* {friends_text}\n"
            f"📸 *Photos:* {photos_text}\n"
            f"🔗 *Link:* {url}"
        )
        await update.message.reply_text(result_text, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Error parsing VK: {str(e)}")

async def vk_get_id(update: Update, username):
    try:
        user_id = await get_vk_id(username)
        if user_id:
            result_text = (
                f"👤 *VK ID:*\n\n"
                f"📛 *Username:* {username}\n"
                f"🆔 *ID:* {user_id}\n"
                f"🔗 *Link:* https://vk.com/id{user_id}"
            )
            await update.message.reply_text(result_text, parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ VK user not found")
    except Exception as e:
        await update.message.reply_text(f"❌ Error getting VK ID: {str(e)}")

async def tg_get_id(update: Update, username):
    try:
        url = f"https://t.me/{username}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find('title')
            profile_name = title.text.replace('Telegram: Contact ', '').strip() if title else "Unknown"
            desc_elem = soup.find('div', {'class': 'tgme_page_description'})
            description = desc_elem.text.strip() if desc_elem else "Not found"
            members_elem = soup.find('div', {'class': 'tgme_page_extra'})
            members_text = members_elem.text.strip() if members_elem else "Unknown"
            result_text = (
                f"👤 *Telegram Profile Information:*\n\n"
                f"📛 *Name:* {profile_name}\n"
                f"🔗 *Username:* @{username}\n"
                f"📝 *Description:* {description}\n"
                f"👥 *Members/Followers:* {members_text}\n"
                f"🌐 *Link:* {url}"
            )
            await update.message.reply_text(result_text, parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ Telegram user not found")
    except Exception as e:
        await update.message.reply_text(f"❌ Error getting Telegram info: {str(e)}")

async def get_vk_id(username):
    try:
        url = f"https://vk.com/{username}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        id_match = re.search(r'"uid":"(\d+)"', response.text)
        if id_match:
            return id_match.group(1)
        id_match = re.search(r'\"id\":(\d+)', response.text)
