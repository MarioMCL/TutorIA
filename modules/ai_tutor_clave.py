import openai
import streamlit as st

class AITutor:
    def __init__(self):
        # Intentamos obtener la clave de los secretos de Streamlit
        try:
            self.api_key = st.secrets["OPENAI_API_KEY"]
            self.client = openai.OpenAI(api_key=self.api_key)
            self.available = True
        except Exception:
            self.available = False
            print("⚠️ AVISO: No se encontró la API Key de OpenAI.")

    def explicar_duda(self, ejercicio_contexto, duda_usuario, historial_chat):
        """
        ejercicio_contexto: Diccionario con el problema y la solución exacta (del MathEngine).
        duda_usuario: La pregunta del alumno (string).
        historial_chat: Lista de mensajes previos para mantener el hilo.
        """
        
        if not self.available:
            return "Error de configuración: Falta la API Key de OpenAI."

        # 1. Construimos el Prompt de Sistema (La personalidad del Tutor)
        # Le inyectamos "La Verdad" (solucion_str) para que no calcule, solo explique.
        system_prompt = f"""
        Eres un profesor experto de Matemáticas de Bachillerato y Universidad.
        Tu objetivo es ayudar al alumno a entender el siguiente ejercicio.
        
        DATOS DEL PROBLEMA (VERDAD ABSOLUTA - NO LOS MODIFIQUES):
        - Función: {ejercicio_contexto['funcion_str']}
        - Solución Correcta: {ejercicio_contexto['solucion_str']}
        
        INSTRUCCIONES:
        1. Responde a la duda del alumno basándote en la solución correcta.
        2. Sé breve, didáctico y usa un tono motivador.
        3. Si usas fórmulas matemáticas, envuélvelas en formato LaTeX usando signos de dólar, ejemplo: $x^2$.
        4. NO des la solución completa si el alumno solo pide una pista.
        """

        # 2. Preparamos los mensajes para la API
        messages = [{"role": "system", "content": system_prompt}]
        
        # Añadimos el historial previo de la conversación (para que tenga memoria)
        for msg in historial_chat:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Añadimos la duda actual
        messages.append({"role": "user", "content": duda_usuario})

        # 3. Llamada a OpenAI (Modelo barato y rápido: gpt-4o-mini)
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.3 # Baja temperatura para que sea más preciso/serio
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error conectando con el Tutor IA: {str(e)}"