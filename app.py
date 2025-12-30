import streamlit as st

# --- CONFIGURACIÓN GLOBAL ---
st.set_page_config(page_title="Tutor Teleco IA", page_icon="🎓")

# -----------------------------------------------------------------------------
# 🔧 CONFIGURACIÓN DEL DUEÑO (TÚ)
# -----------------------------------------------------------------------------
# 1. Pega aquí el enlace "Share" que copiaste de tu producto en Lemon Squeezy
LINK_LEMON_SQUEEZY = "https://tutoria.lemonsqueezy.com/checkout/buy/a9159b0c-ca5c-4aad-9ca4-97333206d033" 

# 2. Pon aquí TU email para que solo TÚ veas el botón de recarga mágica
EMAIL_ADMIN = "mariocalero2001@gmail.com" 
# -----------------------------------------------------------------------------

# --- IMPORTACIONES ---
try:
    from modules.math_engine import MathEngine
    from modules.ai_tutor import AITutor
    from modules.database_manager import DatabaseManager
except ImportError:
    st.error("⚠️ Error Crítico: Faltan módulos. Asegúrate de que subiste la carpeta 'modules' a GitHub.")
    st.stop()

# --- GESTIÓN DE SESIÓN (LOGIN) ---
if 'usuario' not in st.session_state:
    st.session_state['usuario'] = None

# Si NO está logueado, mostramos Login/Registro
if not st.session_state['usuario']:
    st.title("🔐 Acceso Estudiantes")
    
    tab1, tab2 = st.tabs(["Iniciar Sesión", "Registrarse (Nuevo)"])
    
    # Intentamos conectar a la BD. Si falla la config de secretos, avisamos.
    try:
        db = DatabaseManager()
    except Exception as e:
        st.error(f"Error de conexión: {e}. Revisa tus secrets.toml")
        st.stop()
    
    with tab1:
        email_login = st.text_input("Email")
        pass_login = st.text_input("Contraseña", type="password")
        if st.button("Entrar", key="btn_login"):
            with st.spinner("Validando credenciales..."):
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
                with st.spinner("Creando usuario..."):
                    exito, mensaje = db.registrar_usuario(email_reg, pass_reg)
                    if exito:
                        st.success(mensaje)
                        st.info("Ahora ve a la pestaña 'Iniciar Sesión' y entra.")
                    else:
                        st.error(mensaje)
    
    st.stop() # Bloqueamos el resto de la app hasta que entre

# --- APLICACIÓN PRINCIPAL (DENTRO) ---

# Refrescamos conexión a BD
db = DatabaseManager()
user = st.session_state['usuario']
creditos_visuales = user['creditos']

st.title("🎓 Tutor de Análisis")

# --- BARRA SUPERIOR DE ESTADO (MODIFICADA) ---
col1, col2, col3 = st.columns([3, 2, 1]) # Creamos 3 huecos: Nombre, Créditos, Botón

col1.caption(f"👤 Estudiante: **{user['email']}**")

# Mostramos los créditos (Verde si hay, Rojo si no)
if creditos_visuales > 0:
    col2.success(f"🪙 Créditos: {creditos_visuales}")
else:
    col2.error(f"🪙 Créditos: {creditos_visuales}")

# Botón para refrescar saldo manualmente
if col3.button("🔄", help="Actualizar saldo si has pagado"):
    # 1. Consultamos el saldo real en la Nube
    datos = db.supabase.table("perfiles_usuarios").select("creditos").eq("id", user['id']).execute()
    
    if datos.data:
        nuevo_saldo = datos.data[0]['creditos']
        # 2. Actualizamos la memoria de la App
        st.session_state['usuario']['creditos'] = nuevo_saldo
        st.toast("✅ Saldo actualizado") # Mensaje flotante bonito
        st.rerun() # Recargamos la interfaz

# Inicialización de Memoria del Ejercicio
if 'ejercicio' not in st.session_state:
    engine = MathEngine()
    st.session_state['ejercicio'] = engine.generar_problema(tipo="derivada", dificultad=1)
    st.session_state['chat_history'] = [] 

tutor = AITutor()

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configuración")
    
    tema = st.radio("Tema", ["Derivadas", "Integrales"])
    dificultad = st.selectbox("Nivel", [1, 2, 3], format_func=lambda x: f"Nivel {x}")
    
    if st.button("🔄 Nuevo Problema"):
        engine = MathEngine()
        tipo = "derivada" if tema == "Derivadas" else "integral"
        st.session_state['ejercicio'] = engine.generar_problema(tipo, dificultad)
        st.session_state['chat_history'] = [] 
        st.rerun()

    st.divider()
    st.subheader("💳 Recargas")
    
    # Botón de Pago REAL
    st.link_button("💎 Comprar 50 Créditos (5€)", LINK_LEMON_SQUEEZY)
    
    # Botón de Admin (Solo visible para ti)
    if user['email'] == EMAIL_ADMIN: 
        st.divider()
        st.write("🔧 **Zona Admin**")
        if st.button("Recargarme (+5)"):
            db.recargar_saldo(user['id'], 5)
            # Actualizamos visualmente el estado local para verlo al instante
            st.session_state['usuario']['creditos'] += 5
            st.success("¡Autorecarga completada!")
            st.rerun()

    st.divider()
    if st.button("Cerrar Sesión"):
        st.session_state['usuario'] = None
        st.rerun()

# --- ZONA DEL PROBLEMA ---
ejer = st.session_state['ejercicio']
st.info(f"📝 {ejer['titulo']}")
st.latex(ejer['problema_latex'])

with st.expander("👁️ Ver Solución Correcta"):
    st.latex(ejer['solucion_latex'])

st.divider()

# --- CHATBOT ---
st.subheader("💬 Chat con el Profesor IA")

for msg in st.session_state['chat_history']:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Pregunta tu duda (Cuesta 1 crédito)...")

if prompt:
    # 1. Intentamos gastar el crédito en la nube
    exito, saldo_restante = db.gastar_credito(user['id'])
    
    if exito:
        # Actualizamos el saldo en la memoria local para que la barra superior cambie
        st.session_state['usuario']['creditos'] = saldo_restante 
        
        # A. Guardar y mostrar mensaje usuario
        st.session_state['chat_history'].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # B. Generar respuesta IA
        with st.chat_message("assistant"):
            with st.spinner("Analizando paso a paso..."):
                respuesta = tutor.explicar_duda(ejer, prompt, st.session_state['chat_history'])
                st.markdown(respuesta)
        
        # C. Guardar respuesta
        st.session_state['chat_history'].append({"role": "assistant", "content": respuesta})
        st.rerun() # Recargamos para refrescar el contador de créditos visual
    else:
        st.error("⛔ ¡Te has quedado sin créditos!")
        st.markdown(f"Necesitas recargar para seguir. [Haz clic aquí]({LINK_LEMON_SQUEEZY})")