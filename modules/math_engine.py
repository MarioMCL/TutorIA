import sympy as sp
import random

class MathEngine:
    def __init__(self):
        self.x = sp.symbols('x')

    def _generar_coeficiente(self):
        # Evitamos el 0
        choices = [-5, -4, -3, -2, -1, 2, 3, 4, 5]
        return random.choice(choices)

    def _generar_funcion_base(self):
        x = self.x
        # Funciones elementales
        funciones = [
            x**random.randint(2, 4), # Polinomios no muy altos
            sp.sin(x),
            sp.cos(x),
            sp.exp(x)
        ]
        return random.choice(funciones)

    def generar_problema(self, tipo="derivada", dificultad=1):
        """
        Genera problemas matemáticos de análisis.
        tipo: 'derivada' o 'integral'
        """
        x = self.x
        coef1 = self._generar_coeficiente()
        coef2 = self._generar_coeficiente()
        f1 = self._generar_funcion_base()
        f2 = self._generar_funcion_base()

        # --- LÓGICA DE CONSTRUCCIÓN ---
        operacion_nombre = ""
        
        if dificultad == 1:
            funcion = coef1 * f1 + coef2 * f2
            operacion_nombre = "Suma/Resta (Inmediata)"
        elif dificultad == 2:
            funcion = (coef1 * f1) * f2
            operacion_nombre = "Producto / Por Partes"
        else:
            # Dificultad 3 (Simplificada para evitar caos)
            inner = coef1 * x
            funcion = sp.sin(inner) 
            operacion_nombre = "Regla de la Cadena / Sustitución"

        # --- RESOLUCIÓN ---
        if tipo == "derivada":
            resultado = sp.diff(funcion, x)
            enunciado_latex = f"f(x) = {sp.latex(funcion)}"
            solucion_latex = f"f'(x) = {sp.latex(resultado)}"
            titulo = "Calcula la Derivada"
        
        else: # TIPO INTEGRAL
            resultado = sp.integrate(funcion, x)
            # Añadimos la constante de integración manualmente visualmente
            enunciado_latex = f"\\int ({sp.latex(funcion)}) \\, dx"
            solucion_latex = f"{sp.latex(resultado)} + C"
            titulo = "Calcula la Integral Indefinida"

        return {
            "titulo": titulo,
            "tipo_operacion": operacion_nombre,
            "problema_latex": enunciado_latex,
            "solucion_latex": solucion_latex,
            "funcion_str": str(funcion),
            "solucion_str": str(resultado)
        }