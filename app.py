

import streamlit as st

# --- QUITAMOS EL TRY-EXCEPT PARA VER EL ERROR REAL ---
# Si falla aquí, Python te mostrará una pantalla negra con letras rojas (Traceback).
# Sácale captura a eso, que es lo que necesitamos ver.

from modules.math_engine import MathEngine
from modules.ai_tutor import AITutor
from modules.database_manager import DatabaseManager

# -----------------------------------------------------

st.set_page_config(page_title="Tutor Teleco IA", page_icon="🎓")

# --- GESTIÓN DE SESIÓN ---
if 'usuario' not in st.session_state:
    st.session_state['usuario'] = None # Guardará el objeto usuario completo {id, email, creditos}

# Si NO está logueado, mostramos Login/Registro
if not st.session_state['usuario']:
    st.title("🔐 Acceso Estudiantes")
    
    # Pestañas para elegir acción
    tab1, tab2 = st.tabs(["Iniciar Sesión", "Registrarse (Nuevo)"])
    
    db = DatabaseManager() # Conectamos a Supabase
    
    with tab1:
        email_login = st.text_input("Email")
        pass_login = st.text_input("Contraseña", type="password")
        if st.button("Entrar", key="btn_login"):
            usuario_logueado = db.iniciar_sesion(email_login, pass_login)
            if usuario_logueado:
                st.session_state['usuario'] = usuario_logueado
                st.rerun()
            else:
                st.error("Email o contraseña incorrectos.")

    with tab2:
        st.write("Crea tu cuenta y recibe **5 créditos gratis**.")
        email_reg = st.text_input("Tu Email", key="reg_email")
        pass_reg = st.text_input("Crea una contraseña", type="password", key="reg_pass")
        if st.button("Crear Cuenta", key="btn_reg"):
            if len(pass_reg) < 6:
                st.warning("La contraseña debe tener al menos 6 caracteres.")
            else:
                exito, mensaje = db.registrar_usuario(email_reg, pass_reg)
                if exito:
                    st.success(mensaje)
                    st.info("Ahora ve a la pestaña 'Iniciar Sesión' y entra.")
                else:
                    st.error(mensaje)
    
    st.stop() # Paramos aquí si no hay usuario

# --- APLICACIÓN PRINCIPAL (SOLO SI ESTÁ LOGUEADO) ---
# Recuperamos datos frescos de la DB por si gastó créditos
db = DatabaseManager()
# Nota: En una app real haríamos una llamada a DB aquí para refrescar créditos, 
# pero por eficiencia usamos lo que devuelve gastar_credito.

user = st.session_state['usuario']
creditos_visuales = user['creditos']

st.title("🎓 Tutor de Análisis")

# Barra Superior
col1, col2 = st.columns([3,1])
col1.caption(f"Usuario: {user['email']}")
col2.metric("Créditos", creditos_visuales)

# --- (El resto del código de Mates y Chat es igual) ---
if 'ejercicio' not in st.session_state:
    engine = MathEngine()
    st.session_state['ejercicio'] = engine.generar_problema(tipo="derivada", dificultad=1)
    st.session_state['chat_history'] = [] 

tutor = AITutor()

with st.sidebar:
    st.header("⚙️ Panel")
    if st.button("Cerrar Sesión"):
        st.session_state['usuario'] = None
        st.rerun()
        
    tema = st.radio("Tema", ["Derivadas", "Integrales"])
    dificultad = st.selectbox("Nivel", [1, 2, 3])
    
    if st.button("Nuevo Problema"):
        engine = MathEngine()
        tipo = "derivada" if tema == "Derivadas" else "integral"
        st.session_state['ejercicio'] = engine.generar_problema(tipo, dificultad)
        st.session_state['chat_history'] = [] 
        st.rerun()

    st.divider()
    # Enlace REAL a tu pasarela de pago
    link_pago = "TU_URL_DE_LEMON_SQUEEZY_AQUI" 
    
    # Usamos link_button que abre una pestaña nueva
    st.link_button("💎 Comprar 50 Créditos (5€)", link_pago)
    
    # Mantenemos el de simulación solo para ti (oculto por usuario si quieres)
    if user['email'] == "tu_email_admin@gmail.com": 
        if st.button("🔧 Admin: Recargar (+5)"):
            db.recargar_saldo(user['id'], 5)
            st.rerun()

ejer = st.session_state['ejercicio']
st.info(ejer['titulo'])
st.latex(ejer['problema_latex'])
with st.expander("Ver Solución"):
    st.latex(ejer['solucion_latex'])

st.divider()
st.subheader("💬 Chat IA")
for msg in st.session_state['chat_history']:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Duda (1 crédito)...")
if prompt:
    # GASTAR CRÉDITO REAL EN NUBE
    exito, saldo_restante = db.gastar_credito(user['id'])
    
    if exito:
        st.session_state['usuario']['creditos'] = saldo_restante # Actualizamos memoria local
        
        st.session_state['chat_history'].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Consultando..."):
                respuesta = tutor.explicar_duda(ejer, prompt, st.session_state['chat_history'])
                st.markdown(respuesta)
        
        st.session_state['chat_history'].append({"role": "assistant", "content": respuesta})
        st.rerun()
    else:
        st.error("⛔ Sin saldo. Simula un pago en el menú.")