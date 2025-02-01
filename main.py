import os
import subprocess
import logging
import re
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# إعدادات البوت
TOKEN = "6908154131:AAEVK32ucDCxyyjNRt9gS3QEfysVOT3jQzg"
REPO_PATH = "/data/data/com.termux/files/home/TVNAI1.github.io"  # المسار المحلي لمستودع GitHub
HTML_FILE = os.path.join(REPO_PATH, "player.html")

# إعدادات الـ Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# إنشاء صفحة HTML ديناميكيًا
def generate_html(sources, poster_url):
    html_content = f'''
<!DOCTYPE html>
<html lang="ar">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مشغل الفيديو</title>
    <link rel="stylesheet" href="https://cdn.plyr.io/3.7.8/plyr.css">
    <style>
        body {{ background-color: black; text-align: center; margin: 0; padding: 0; }}
        .container {{ width: 100vw; height: 100vh; display: flex; align-items: center; justify-content: center; }}
        video {{ width: 90%; max-width: 800px; border: 2px solid white; }}
    </style>
</head>
<body>
    <div class="container">
        <video controls poster="{poster_url}">
            {"".join(sources)}
            <track kind="captions" label="English" srclang="en" 
                   src="https://cdn.plyr.io/static/demo/View_From_A_Blue_Moon_Trailer-HD.en.vtt" default>
        </video>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/plyr/3.6.7/plyr.min.js"></script>
    <script> const player = new Plyr('video'); </script>
</body>
</html>
    '''
    
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    logger.info("✅ تم إنشاء أو تحديث الملف player.html")
    
    # دفع التحديثات إلى GitHub
    push_to_github()

# تحديث المستودع ورفع التغييرات إلى GitHub
def push_to_github():
    try:
        commands = [
            ["git", "add", "player.html"],
            ["git", "commit", "-m", "تحديث صفحة المشغل"],
            ["git", "push", "origin", "main"]
        ]
        
        for cmd in commands:
            subprocess.run(cmd, cwd=REPO_PATH, check=True)
        
        logger.info("🚀 تم تحديث GitHub Pages بنجاح!")
    
    except Exception as e:
        logger.error(f"⚠️ فشل تحديث GitHub: {e}")

# استقبال الروابط من تيليجرام وتحديث الصفحة
async def handle_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text
        matches = re.findall(r'(\d+P)"([^"]+)"', text)
        
        if matches:
            sources = [f'<source src="{url}" type="video/mp4" size="{size[:-1]}" />' for size, url in matches]
            
            generate_html(sources, poster_url="https://cdn.plyr.io/static/demo/View_From_A_Blue_Moon_Trailer-HD.jpg")
            
            await update.message.reply_text(
                f"✅ تم تحديث المشغل!\n🔗 رابط التشغيل: https://Ahmd3301.github.io/player.html\n📹 عدد الجودات: {len(matches)}"
            )
        else:
            await update.message.reply_text("❌ الصيغة غير صحيحة! أرسل الروابط بهذا الشكل:\n1080P\"رابط_1080\", 720P\"رابط_720\"")
    
    except Exception as e:
        logger.error(f"⚠️ خطأ: {str(e)}")
        await update.message.reply_text("⚠️ حدث خطأ أثناء المعالجة")

# تشغيل البوت
def main():
    # إنشاء صفحة HTML أولية
    generate_html([], poster_url="https://cdn.plyr.io/static/demo/View_From_A_Blue_Moon_Trailer-HD.jpg")
    
    # تشغيل بوت تيليجرام
    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_links))
    
    logger.info("🤖 البوت يعمل الآن...")
    application.run_polling()

if __name__ == "__main__":
    main()
