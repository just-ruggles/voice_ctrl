import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import paho.mqtt.client as paho
import json

# 🎨 Estilos personalizados
st.markdown("""
    <style>
    .stApp {
        background-image: url("https://media.sidefx.com/uploads/multiverse.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    .custom-title {
        font-size: 40px;
        color: red;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .custom-subheader {
        font-size: 28px;
        color: white;
        font-weight: bold;
        margin-bottom: 30px;
    }
    .bk-root .bk-btn {
        background-color: #007BFF !important;
        color: white !important;
        font-weight: bold;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 18px;
    }
    </style>
""", unsafe_allow_html=True)

# 🏷️ Títulos
st.markdown('<div class="custom-title">INTERFACES MULTIMODALES</div>', unsafe_allow_html=True)
st.markdown('<div class="custom-subheader">CONTROL POR VOZ</div>', unsafe_allow_html=True)

# 🖼️ Imagen
try:
    image = Image.open('voice_ctrl.jpg')
    st.image(image, width=200)
except FileNotFoundError:
    st.warning("⚠️ Imagen 'voice_ctrl.jpg' no encontrada. Asegúrate de que está en el mismo directorio.")

# 🎤 Botón e instrucción
st.write("🎙️ Toca el botón y habla:")

stt_button = Button(label="🎤 Inicio", width=200)
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

# 📡 MQTT Config
broker = "157.230.214.127"
port = 1883

client1 = paho.Client("GIT-HUBC")

def on_publish(client, userdata, result):
    print("✅ El dato ha sido publicado.")

def on_message(client, userdata, message):
    time.sleep(1)
    message_received = str(message.payload.decode("utf-8"))
    st.write("📥 Mensaje recibido:", message_received)

client1.on_publish = on_publish
client1.on_message = on_message
client1.connect(broker, port)

# 🚀 Publicar voz detectada
if result and "GET_TEXT" in result:
    texto = result.get("GET_TEXT").strip()
    st.success(f"🗣️ Detectado: {texto}")
    message = json.dumps({"Act1": texto})
    client1.publish("voice_ctrl", message)

# 📁 Crear carpeta temp si no existe
temp_dir = "temp"
if not os.path.exists(temp_dir):
    try:
        os.mkdir(temp_dir)
    except Exception as e:
        st.error(f"❌ Error al crear la carpeta 'temp': {e}")
