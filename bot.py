import json  # ✅ IMPORTAR JSON
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import os
from flask import Flask, request
# from telegram import Bot
from telegram.ext import Dispatche, Update

# Crea la aplicación Flask
app = Flask(__name__)

# El token de tu bot
TOKEN = "7836540058:AAEkLhgAV8PYl5nWHFBYstxxoXhXImYda3o"
bot = Bot(token=TOKEN)

# Configura el dispatcher
dispatcher = Dispatcher(bot, None, workers=0)

# Diccionario con tarifas (ejemplo)
TARIFAS = {
    "Compañia 1": {"potenciapunta": 0.11, "potenciavalle": 0.04, "energia": 0.12, "alquiler_contador": 0.80, "bono_social": 0.39},
    "Compañia 2": {"potenciapunta": 0.094, "potenciavalle": 0.0465, "energia": 0.128, "alquiler_contador": 0.80, "bono_social": 0.39},
    "Compañia 3": {"potenciapunta": 0.108, "potenciavalle": 0.033, "energia": 0.119, "alquiler_contador": 0.80, "bono_social": 0.39},
    "Compañia 4": {"potenciapunta": 0.068, "potenciavalle": 0.068, "energia": 0.129, "alquiler_contador": 0.80, "bono_social": 0.39}
}

USER_DATA = {}

 def start(update: Update, context: CallbackContext) -> None:
     update.message.reply_text("¡Hola! Soy tu asesor de Tu Ahorro Claro. ¿Quieres saber cuánto puedes ahorrar en tu factura de luz?\n\nUsa /calcular para obtener una estimación de tu factura.")

 def calcular(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    USER_DATA[chat_id] = {}

     update.message.reply_text("Introduce los kW contratados (ejemplo: 3.45):")
     context.user_data["step"] = "kw_contratados"

 def handle_message(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    user_input = update.message.text

    if chat_id not in USER_DATA or "step" not in context.user_data:
        return

    step = context.user_data["step"]

    if step == "kw_contratados":
        USER_DATA[chat_id]["kw_contratados"] = float(user_input)
        await update.message.reply_text("Ahora introduce los kW consumidos (ejemplo: 250):")
        context.user_data["step"] = "kw_consumidos"

    elif step == "kw_consumidos":
        USER_DATA[chat_id]["kw_consumidos"] = float(user_input)

        # Calcular factura para todas las compañías
        mensaje = "Aquí tienes el precio estimado de tu factura con cada compañía:\n\n"
        for compania, datos in TARIFAS.items():
            total_factura = calcular_factura(USER_DATA[chat_id], datos)
            mensaje += f"🔹 {compania}: {total_factura:.2f} €\n"

         update.message.reply_text(mensaje)

        # Limpiar datos del usuario
        del USER_DATA[chat_id]
        del context.user_data["step"]

 def calcular_factura(datos, tarifa):
    kw_contratados = datos["kw_contratados"]
    kw_consumidos = datos["kw_consumidos"]

    termino_potencia_punta = kw_contratados * tarifa["potenciapunta"] * 30  # Precio mensual
    termino_potencia_valle = kw_contratados * tarifa["potenciavalle"] * 30  # Precio mensual
    termino_energia = kw_consumidos * tarifa["energia"]
    alquiler_contador = tarifa["alquiler_contador"]
    bono_social = tarifa["bono_social"]
    impuestos = (termino_potencia_punta + termino_potencia_valle + termino_energia) * 0.05112  # 5.112% impuesto eléctrico
    iva = (termino_potencia_punta + termino_potencia_valle + termino_energia + alquiler_contador + bono_social + impuestos) * 0.21 # 21% iva

    total = termino_potencia_punta + termino_potencia_valle + termino_energia + alquiler_contador + bono_social + impuestos + iva
    return total

@app.route('/')
def home():
    return 'Bot está en funcionamiento'

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data(as_text=True)
    json_obj = json.loads(json_str)  # Convertir string JSON a diccionario

    print("JSON recibido:", json_obj)  # 🔍 Ver qué datos está recibiendo

    if not isinstance(json_obj, dict):
        print("⚠️ ERROR: El JSON recibido no es un diccionario")
        return "Invalid JSON format", 400

    update = Update.de_json(json_obj, bot)
    dispatcher.process_update(update)
    return '', 200
def main():
    # Configura el webhook con la URL de tu servidor
    webhook_url = f"https://botcomparadortelegram.onrender.com/{TOKEN}"
    

    # Configura el bot
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))  # Usando el puerto proporcionado por Render

if __name__ == "__main__":
    main()
