import openai
import streamlit as st

class AITutor:
    def __init__(self):
        # Intentamos leer la clave de los secretos de Streamlit
        try:
            self.api_key = st.secrets["OPENAI_API_KEY"]
            self.client = openai.OpenAI(api_key=self.api_key)
            self.modo_simulacion = False # ¡Vamos en serio!
        except Exception:
            # Si falla (no has creado el secrets.toml), volvemos a simulación
            self.modo_simulacion = True
            print("⚠️ AVISO: No se detectó API Key. Usando modo simulación.")

    def explicar_duda(self, ejercicio_contexto, duda_usuario, historial_chat):
        
        # --- MODO REAL (CONECTADO A GPT-4o-mini) ---
        if not self.modo_simulacion:
            try:
                # 1. Definimos la personalidad del profesor
                system_prompt = f"""
                Eres un profesor universitario de Ingeniería de Telecomunicaciones.
                Estás ayudando a un alumno con ejercicios de Cálculo.
                
                CONTEXTO DEL EJERCICIO (VERDAD MATEMÁTICA):
                - Enunciado: {ejercicio_contexto['problema_latex']}
                - Función interna: {ejercicio_contexto['funcion_str']}
                - Solución Correcta: {ejercicio_contexto['solucion_str']}
                
                TU OBJETIVO:
                Responde a la duda del alumno: "{duda_usuario}"
                
                REGLAS:
                1. NO resuelvas el ejercicio completo si no te lo piden, da pistas.
                2. Si el alumno se equivoca, corrígele amablemente.
                3. Usa formato LaTeX para las fórmulas (entre signos $).
                4. Sé conciso.
                """

                # 2. Preparamos la conversación
                messages = [{"role": "system", "content": system_prompt}]
                
                # Añadimos memoria (últimos 4 mensajes para ahorrar tokens)
                for msg in historial_chat[-4:]:
                    messages.append({"role": msg["role"], "content": msg["content"]})
                
                messages.append({"role": "user", "content": duda_usuario})

                # 3. Llamada a la API
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini", # El modelo más rápido y barato para esto
                    messages=messages,
                    temperature=0.3 # Creatividad baja para ser preciso en mates
                )
                return response.choices[0].message.content

            except Exception as e:
                return f"❌ Error conectando con OpenAI: {e}. (Revisa tu saldo o tu clave)"

        # --- FALLBACK (POR SI FALLA LA CLAVE) ---
        else:
            return "🤖 **[MODO SIMULACIÓN]** Configura tu API Key en `.streamlit/secrets.toml` para activar la IA real."