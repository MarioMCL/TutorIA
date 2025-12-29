import streamlit as st
from supabase import create_client, Client

class DatabaseManager:
    def __init__(self):
        # Intentamos conectar con Supabase usando los secretos
        try:
            url = st.secrets["supabase"]["url"]
            key = st.secrets["supabase"]["key"]
            self.supabase: Client = create_client(url, key)
            self.conectado = True
        except Exception as e:
            st.error(f"Error conectando a Supabase: {e}")
            self.conectado = False

    def registrar_usuario(self, email, password):
        """
        Crea usuario en Auth. 
        Nota: No insertamos en la tabla 'perfiles_usuarios' manualmente porque
        ya configuramos un TRIGGER en Supabase que lo hace automático.
        """
        try:
            auth_response = self.supabase.auth.sign_up({
                "email": email, 
                "password": password
            })
            
            if auth_response.user:
                return True, "Registro exitoso. ¡Ya puedes entrar!"
            
            # Si no hay user y no hubo excepción, quizás requiere confirmación de email
            # o el usuario ya existía.
            return False, "No se pudo crear el usuario (¿Quizás ya existe?)."
            
        except Exception as e:
            return False, f"Error: {e}"

    def iniciar_sesion(self, email, password):
        """Loguea y devuelve el objeto usuario con sus créditos"""
        try:
            auth_response = self.supabase.auth.sign_in_with_password({
                "email": email, 
                "password": password
            })
            
            if auth_response.user:
                user_id = auth_response.user.id
                # Consultamos los créditos (que el Trigger debió crear)
                data = self.supabase.table("perfiles_usuarios").select("creditos").eq("id", user_id).execute()
                
                # Si por alguna razón el trigger falló y no hay fila, devolvemos 0
                creditos = data.data[0]['creditos'] if data.data else 0
                
                return {
                    "id": user_id,
                    "email": email,
                    "creditos": creditos
                }
            return None
        except Exception:
            return None

    def gastar_credito(self, user_id):
        """Resta 1 crédito en la nube"""
        try:
            # 1. Obtenemos saldo actual
            data = self.supabase.table("perfiles_usuarios").select("creditos").eq("id", user_id).execute()
            if not data.data:
                return False, 0
                
            creditos_actuales = data.data[0]['creditos']
            
            # 2. Si tiene saldo, restamos
            if creditos_actuales > 0:
                nuevo_saldo = creditos_actuales - 1
                self.supabase.table("perfiles_usuarios").update({"creditos": nuevo_saldo}).eq("id", user_id).execute()
                return True, nuevo_saldo
            else:
                return False, 0
        except Exception as e:
            print(f"Error gastando crédito: {e}")
            return False, 0
    
    def recargar_saldo(self, user_id, cantidad):
        """Suma créditos (Simulación de pago)"""
        try:
            data = self.supabase.table("perfiles_usuarios").select("creditos").eq("id", user_id).execute()
            if data.data:
                saldo = data.data[0]['creditos']
                self.supabase.table("perfiles_usuarios").update({"creditos": saldo + cantidad}).eq("id", user_id).execute()
        except Exception as e:
            print(f"Error recargando: {e}")