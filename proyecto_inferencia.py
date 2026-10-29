import json
import timeit

# ==========================================================
# PARTE 1: ESTRUCTURA DE DATOS (NO MODIFICAR)
# ==========================================================
class Regla:
    def __init__(self, id_regla: int, antecedentes: set[str], consecuente: str) -> None:
        self.id_regla: int = id_regla
        self.antecedentes: set[str] = set(antecedentes)  
        self.consecuente: str = consecuente

    def __str__(self):
        return f"{self.id_regla}: {' AND '.join(self.antecedentes)} -> {self.consecuente}"

class MotorInferencia:
    def __init__(self, ruta_kb: str):
        self.reglas: list[Regla] = self.cargar_kb(ruta_kb)
        self.memoria_trabajo: set[str] = set()
        self.traza_explicacion: list[int] = [] # Sugerencia para almacenar el orden de las reglas activadas

    def cargar_kb(self, ruta: str) -> list[Regla]:
        """Carga las reglas desde un archivo JSON."""
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            return [Regla(int(r.get('id')), r['antecedentes'], r['consecuente']) for r in datos['reglas']]
        except Exception as e:
            print(f"Error al cargar la Base de Conocimiento: {e}")
            return []

    # ==========================================================
    # PARTE 2: MOTORES DE INFERENCIA (A DESARROLLAR)
    # ==========================================================
    def ejecutar_inferencia(self, hechos_iniciales: list[str], objetivo: str) -> bool:
        """
        Motor de Encadenamiento hacia Adelante (Forward Chaining).
        Debe retornar True si el objetivo es consecuencia lógica, False en caso contrario.
        Además, debe registrar la traza de explicación.
        """
        self.memoria_trabajo = set(hechos_iniciales) #Memoria
        self.traza_explicacion = [] #toca reiniciar para cada ejecucion dio mio
        deducidos: set[str] = set() #los deducidos, incia conjunto vacio

        #si el objetivo ya esta presente, devolver de una vez
        if objetivo in self.memoria_trabajo:
            return True

        while self.memoria_trabajo != deducidos:
            deducidos = set(self.memoria_trabajo)

            for r in self.reglas:
                if r.antecedentes <= deducidos: # antecedentes es subconjunto de deducidos?
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

        return False

    def ejecutar_inferencia_atras(self, hechos_iniciales: list[str], objetivo: str) -> bool:
        """
        Motor de Encadenamiento hacia Atrás (Backward Chaining).
        Debe retornar True si el objetivo puede ser probado, False en caso contrario.
        Debe manejar adecuadamente la recursividad (goal-driven) y los casos base.
        """

        if objetivo in hechos_iniciales:
            return True

        candidatas: list[Regla] = self._obtener_candidatas(objetivo)
        sub_meta: bool

        for regla in candidatas:
            sub_meta = True

            for premisa in regla.antecedentes:
                if not self.ejecutar_inferencia_atras(hechos_iniciales, premisa):
                    sub_meta = False

            if sub_meta:
                self.traza_explicacion.append(regla.id_regla)
                return True

        return False

    def _obtener_candidatas(self, objetivo) -> list[Regla]:

        reglas: list[Regla] = []
        for r in self.reglas:
            if r.consecuente == objetivo:
                reglas.append(r)

        return reglas

# ==========================================================
# PARTE 3: EJECUCIÓN (PUEDEN MODIFICAR PARA PRUEBAS)
# ==========================================================


if __name__ == "__main__":

    # Hola profe, qué más? 
    # Aquí le dejamos los tres casitos de nuestra base de conocimiento
    # Usamos tipado, porque se ve chévere

    # Sobre el experimento final -- tiempos 
    # Quisimos averiguar cuál es más rápido 
    
    # CASO 1
    s1: list[str] = ['fiebre_alta', 'escalofrios', 'dolor_toracico', 'tos_con_flema', 'dificultad_respiratoria', 'estertores_crepitantes', 'saturacion_oxigeno_baja']
    
    # CASO 2
    # -> Acá se trata de dos pacientes con síntomas muy parecidos (difieren en uno)
    # -> El primer paciente si tiene sospecha de dengue clásico, mientras que el segundo no

    s2: list[str] = ['fiebre_alta', 'escalofrios', 'fatiga_extrema', 'debilidad_muscular', 'dolor_articular', 'dolor_muscular', 'erupcion_cutanea', 'prurito_leve', 'dolor_retroocular_intenso'] #paciente A
    s3: list[str] = ['fiebre_alta', 'escalofrios', 'fatiga_extrema', 'debilidad_muscular', 'dolor_articular', 'dolor_muscular', 'erupcion_cutanea', 'prurito_leve', 'artralgia_severa_extremidades'] #paciente B
    
    # CASO 3
    # -> Este caso es similar al primero, pero sin todos los síntomas 
    s4: list[str] = ['fiebre_alta', 'escalofrios', 'dolor_toracico', 'tos_con_flema', 'dificultad_respiratoria']

    tins: int = 1000000

    print(f'{tins = }')
    
    casos: list[tuple] = [
        # sintomas, hipótesis                                 Esperanza
        (s1, 'alerta_gravedad_respiratoria_severa'),        # TRUE
        (s2, 'sospecha_dengue_clasico'),                    # TRUE
        (s3, 'sospecha_dengue_clasico'),                    # FALSE
        (s4, 'neumonia_bacteriana_comun')                   # TRUE
    ]

    suma_1: float = 0.0
    suma_2: float = 0.0
    i: int = 1

    for sintomas, hipotesis in casos:    

        print(f'\n ====== Caso {i} ======')
        i += 1

        # 1. Inicializar el motor con el archivo de reglas
        motor: MotorInferencia = MotorInferencia('base_conocimiento.json')

        # 2. Introducción al sistema
        print(f"--- Sistema Experto de Diagnóstico ---")
        print(f"Síntomas iniciales: {sintomas}")
        print(f"Objetivo a verificar: {hipotesis}\n")

        # 3. Ejecución Inferencia hacia adelante
        print("--- Motor Hacia Adelante ---")
        adelante: bool = motor.ejecutar_inferencia(sintomas, hipotesis)
        print(f"¿Es consecuencia lógica?: {adelante}")
        
        # Añadido: tiempo
        tiempo_1: float = timeit.timeit(
                lambda: motor.ejecutar_inferencia(sintomas, hipotesis),
                number = tins
            )
        print(f'Demora -> {tiempo_1:.4f}s\n')

        # 4. Ejecutar Inferencia hacia Atrás
        print("--- Motor Hacia Atrás ---")
        atras: bool = motor.ejecutar_inferencia_atras(sintomas, hipotesis)
        print(f"¿Es demostrable?: {atras}")
        
        # Añadido: tiempo
        tiempo_2: float = timeit.timeit(
                lambda: motor.ejecutar_inferencia_atras(sintomas, hipotesis),
                number = tins
            )
        print(f'Demora -> {tiempo_2:.4f}s \n')

        suma_1 += tiempo_1
        suma_2 += tiempo_2

    print(f'\n === Resumen de tiempos ===')
    print(f'Adelante  -> {suma_1:.4f}s')
    print(f'Atrás     -> {suma_2:.4f}s')
    print(f'diff -> {abs(suma_1 - suma_2):.4f}s')