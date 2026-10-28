import json

# ==========================================================
# PARTE 1: ESTRUCTURA DE DATOS (NO MODIFICAR)
# ==========================================================
class Regla:
    def __init__(self, id_regla, antecedentes, consecuente):
        self.id_regla = id_regla
        self.antecedentes = set(antecedentes)  
        self.consecuente = consecuente

    def __str__(self):
        return f"{self.id_regla}: {' AND '.join(self.antecedentes)} -> {self.consecuente}"

class MotorInferencia:
    def __init__(self, ruta_kb):
        self.reglas = self.cargar_kb(ruta_kb)
        self.memoria_trabajo = set()
        self.traza_explicacion = [] # Sugerencia para almacenar el orden de las reglas activadas

    def cargar_kb(self, ruta):
        """Carga las reglas desde un archivo JSON."""
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            return [Regla(r.get('id'), r['antecedentes'], r['consecuente']) for r in datos['reglas']]
        except Exception as e:
            print(f"Error al cargar la Base de Conocimiento: {e}")
            return []

    # ==========================================================
    # PARTE 2: MOTORES DE INFERENCIA (A DESARROLLAR)
    # ==========================================================
    def ejecutar_inferencia(self, hechos_iniciales, objetivo) -> bool:
        """
        Motor de Encadenamiento hacia Adelante (Forward Chaining).
        Debe retornar True si el objetivo es consecuencia lógica, False en caso contrario.
        Además, debe registrar la traza de explicación.
        """
        self.memoria_trabajo = set(hechos_iniciales) #Memoria
        self.traza_explicacion = [] #toca reiniciar para cada ejecucion dio mio
        deducidos: set[Regla] = set() #los deducidos, incia conjunto vacio

        #si el objetivo ya esta presente, devolver de una vez
        if objetivo in self.memoria_trabajo:
            return True

        while self.memoria_trabajo != deducidos:
            deducidos = set(self.memoria_trabajo)

            for r in self.reglas:
                if r.antecedentes <= deducidos:
                    #si el consecuente llega a ser la meta
                    if r.consecuente == objetivo:
                        if r.id_regla not in self.traza_explicacion:
                            self.traza_explicacion.append(r.id_regla)

                        return True

                    #si es un nuevo hecho, agregarlo a memory
                    if r.consecuente not in self.memoria_trabajo:
                        self.memoria_trabajo.add(r.consecuente)
                        if r.id_regla not in self.traza_explicacion:
                            self.traza_explicacion.append(r.id_regla)
    
        # TODO: Implementar la lógica iterativa basada en el punto fijo.
        
        return False # Cambiar por el resultado lógico

    def ejecutar_inferencia_atras(self, hechos_iniciales, objetivo) -> bool:
        """
        Motor de Encadenamiento hacia Atrás (Backward Chaining).
        Debe retornar True si el objetivo puede ser probado, False en caso contrario.
        Debe manejar adecuadamente la recursividad (goal-driven) y los casos base.
        """

        if objetivo in hechos_iniciales:
            return True

        candidatas = self._obtener_reglas_con_conclusion(objetivo)
        sub_meta: bool

        for regla in candidatas:
            sub_meta = True

            for premisa in regla.antecedentes:
                if not self.ejecutar_inferencia_atras(hechos_iniciales, premisa):
                    sub_meta = False

            if sub_meta:
                self.traza_explicacion.append(regla.id_regla)
                return True

        return False # Cambiar por el resultado lógico

    def _obtener_reglas_con_conclusion(self, objetivo) -> list[Regla]:
        reglas: list[Regla] = []
        for r in self.reglas:
            if r.consecuente == objetivo:
                reglas.append(r)

        return reglas

# ==========================================================
# PARTE 3: EJECUCIÓN (PUEDEN MODIFICAR PARA PRUEBAS)
# ==========================================================

""" if __name__ == "__main__":
    # 1. Inicializar el motor con el archivo de reglas
    motor = MotorInferencia("base_conocimiento.json")

    # 2. Definir caso clínico de prueba
    sintomas = ["Fiebre", "Tos", "Dificultad_Respiratoria"]
    hipotesis = "Neumonia"

    print(f"--- Sistema Experto de Diagnóstico ---")
    print(f"Síntomas iniciales: {sintomas}")
    print(f"Objetivo a verificar: {hipotesis}\n")

    # 3. Ejecutar Inferencia hacia Adelante
    print("--- Motor Hacia Adelante ---")
    resultado_adelante = motor.ejecutar_inferencia(sintomas, hipotesis)
    print(f"¿Es consecuencia lógica?: {resultado_adelante}\n")

    # 4. Ejecutar Inferencia hacia Atrás
    #print("--- Motor Hacia Atrás ---")
    #resultado_atras = motor.ejecutar_inferencia_atras(sintomas, hipotesis)
    #print(f"¿Es demostrable?: {resultado_atras}")
 """
 
#testeo hecho con IA
if __name__ == "__main__":
    motor = MotorInferencia("base_conocimiento.json")
    print(f"Reglas cargadas: {len(motor.reglas)}\n")   # debe decir 52
    reglas_por_id = {r.id_regla: r for r in motor.reglas}

    # (nombre, hechos iniciales, objetivo, resultado esperado)
    base_arbovirus = ["fiebre_alta", "escalofrios", "fatiga_extrema", "debilidad_muscular",
                      "dolor_articular", "dolor_muscular", "erupcion_cutanea", "prurito_leve"]

    casos = [
        ("1. Neumonía hasta alerta (4 niveles)",
         ["dolor_toracico", "tos_con_flema", "dificultad_respiratoria", "fiebre_alta",
          "escalofrios", "estertores_crepitantes", "saturacion_oxigeno_baja"],
         "alerta_gravedad_respiratoria_severa", True),

        ("2. Dengue hasta alerta (5 rondas)",
         base_arbovirus + ["dolor_retroocular_intenso", "sangrado_mucosas_espontaneo"],
         "alerta_dengue_con_signos_alarma", True),

        ("3. Diferenciador: mismos síntomas base, chikungunya SÍ",
         base_arbovirus + ["artralgia_severa_extremidades"],
         "sospecha_chikungunya", True),

        ("4. Diferenciador: mismos síntomas base, dengue NO",
         base_arbovirus + ["artralgia_severa_extremidades"],
         "sospecha_dengue_clasico", False),

        ("5. Gastroenteritis hasta deshidratación grave",
         ["dolor_abdominal_difuso", "nauseas", "diarrea_acuosa", "vomito_frecuente",
          "fiebre_alta", "escalofrios", "signos_deshidratacion_severa"],
         "alerta_deshidratacion_grado_tres", True),

        ("6. Objetivo ya presente en los hechos",
         ["fiebre_alta", "tos_seca"],
         "tos_seca", True),

        ("7. Falta el hecho clave (sin estertores) -> punto fijo",
         ["dolor_toracico", "tos_con_flema", "dificultad_respiratoria", "fiebre_alta", "escalofrios"],
         "neumonia_bacteriana_comun", False),
    ]

    for nombre, hechos, objetivo, esperado in casos:
        resultado = motor.ejecutar_inferencia_atras(hechos, objetivo)
        estado = "OK" if resultado == esperado else "FALLO"
        print(f"[{estado}] {nombre}")
        print(f"   Objetivo: {objetivo} -> {resultado} (esperado {esperado})")
        print("   Traza:")
        for id_regla in motor.traza_explicacion:
            print(f"     {reglas_por_id[id_regla]}")
        if not motor.traza_explicacion:
            print("     (ninguna regla disparada)")
        print(f"   Memoria final: {len(motor.memoria_trabajo)} hechos\n") 