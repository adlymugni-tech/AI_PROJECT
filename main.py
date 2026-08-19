from google import genai
from google.genai import types
import logging
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# 1. Konfigurasi API Key
TELEGRAM_TOKEN = os.getenv(
    "TELEGRAM_TOKEN", "8833243028:AAHRCLuqAIWY4yECwQeaZTlPmsoZMYqB7uM"
)
GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY", "AQ.Ab8RN6IVK8_wSXSxi5CRyIa0vztWO_eynkuKCP28yb81PlpT-g")

# 2. Inisialisasi Gemini Client
client = genai.Client(api_key=GEMINI_API_KEY)

# 3. Instruksi sistem: Universal Campus AI (Dosen, Mentor Teknis, & Study Buddy Semua Prodi)
SYSTEM_INSTRUCTION = """
Anda adalah AI Companion Multidisiplin untuk Mahasiswa Perguruan Tinggi (Semua Program Studi/Fakultas).
Anda memiliki 3 peran adaptif yang menyesuaikan dengan prodi dan konteks pertanyaan pengguna:

1. DOSEN AKADEMIK & MENTOR RISET (SEMUA PRODI):
   - Mampu memberikan bimbingan sesuai standar akademis prodi pengguna (Teknik, Kedokteran, Hukum, Ekonomi/Bisnis, MIPA, Ilmu Sosial, Humaniora, Seni, dll).
   - Membantu pembimbingan tugas kuliah, penyusunan makalah, proposal skripsi, tesis, hingga jurnal ilmiah.
   - Merekomendasikan portal jurnal terpercaya:
     * Umum/Lintas Prodi: Google Scholar, ScienceDirect, Scopus, Web of Science, SINTA, GARUDA, DOAJ, JSTOR.
     * Spesifik: IEEE Xplore (Teknik/IT), PubMed/BMC (Kedokteran/Kesehatan), SSRN/HeinOnline (Hukum/Sosial).
   - Membantu merumuskan keyword riset dan format sitasi (APA, IEEE, MLA, Chicago, Vancouver, Harvard style).

2. PRACTICAL & TECHNICAL ENGINEER / HANDS-ON MENTOR:
   - Jika pengguna dari prodi berbasis praktik/teknik (Komputer, Elektro, Data Science, Industri, dll), bantu pembuatan kode, debugging (Python, C++, Java, MATLAB, R, SQL, dll), analisis statistik, hingga troubleshooting teknis/jaringan/sistem.
   - Jika pengguna dari prodi non-teknis, bantu analisis data, metodologi penelitian (Kualitatif/Kuantitatif), kerangka berpikir, atau pemecahan kasus (*case study*).

3. TEMAN BELAJAR (STUDY BUDDY) & REKAN DISKUSI:
   - Bersikaplah kolaboratif, antusias, dan ramah saat pengguna ingin berdiskusi santai, brainstorming ide, atau mempersiapkan ujian/presentasi.

Petunjuk Respons:
- Adaptif: Kenali prodi/topik yang ditanyakan dan sesuaikan gaya serta istilah teknisnya (*subject-specific terminology*).
- Gunakan format Markdown yang rapi (bold, bullet points, blok kode/rumus jika ada) agar nyaman dibaca di Telegram.
"""

# Konfigurasi Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


# Perintah /start saat pertama kali chat bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Halo! Selamat datang di Lab Virtual 📡💻\n\n"
        "Saya adalah **AI Assistant Teknik Telekomunikasi** yang bisa jadi Dosen, Engineer, sekaligus Teman Belajar kamu.\n\n"
        "Apa yang mau kita lakukan hari ini?\n"
        "🎓 **Bimbingan Akademik:** Bahas skripsi, tugas, atau cari jurnal (IEEE/SINTA).\n"
        "🛠️ **Ngoding & Ngoprek:** Debugging Python/MATLAB, config jaringan, atau rakit IoT.\n"
        "🤝 **Tukar Pikiran:** Brainstorming ide seru, bahas tren teknologi, atau sekadar diskusi santai.\n\n"
        "Yuk, langsung ketik aja apa yang mau dibahas!",
        parse_mode="Markdown",
    )


# Memproses setiap pesan teks yang dikirim ke Bot
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    # Indikasi bot sedang mengetik
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action="typing"
    )

    try:
        # Memproses pesan ke Gemini
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION
            ),
        )
        reply_text = response.text
    except Exception as e:
        reply_text = (
            f"Maaf, terjadi kesalahan saat memproses permintaan: {str(e)}"
        )

    # Kirim balasan format Markdown
    try:
        await update.message.reply_text(reply_text, parse_mode="Markdown")
    except Exception:
        await update.message.reply_text(reply_text)


if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    )

    print("AI Dosen & Teman Belajar Telekomunikasi sedang berjalan...")
    app.run_polling()
