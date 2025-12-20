# F1 Strategy Predictor PRO: Engine de Optimización de Carrera

##  Introducción
Este proyecto es un simulador de ingeniería de carrera que determina la estrategia de paradas en boxes óptima para un Gran Premio de Fórmula 1. El sistema utiliza datos reales de telemetría de la temporada 2023 para modelar el comportamiento de cada piloto y circuito, permitiendo predecir el tiempo total de carrera bajo distintas variables ambientales y técnicas.

##  Origen y Extracción de Datos
El sistema utiliza la librería **FastF1**, que actúa como puente con los servidores de telemetría de la FIA.
- **Fuente**: Datos oficiales de sesiones de carrera de 2023.
- **Procesamiento de Ritmo Base**: 
    - Se extraen los tiempos de vuelta (`LapTime`) del piloto seleccionado.
    - Se aplican filtros de limpieza: se eliminan vueltas con `PitInTime` o `PitOutTime` (vueltas de entrada/salida de boxes) y vueltas no precisas (`IsAccurate == False`).
    - **Cálculo de Mediana**: Se utiliza la mediana estadística en lugar del promedio para ignorar "outliers" (vueltas lentas por tráfico, banderas amarillas o errores puntuales), obteniendo el ritmo real constante del vehículo.

##  Variables Consideradas para el Cálculo
Para encontrar la estrategia más rápida, el motor de simulación procesa las siguientes variables:

1. **Parámetros de Compuestos (Soft, Medium, Hard)**:
   - **Compuesto Delta**: Diferencia de velocidad intrínseca entre gomas (ej. Soft es -0.6s más rápido que Medium).
   - **Degradación Base**: Incremento de tiempo por vuelta según el desgaste.
2. **Condiciones Ambientales**:
   - **Temperatura**: El sistema aplica un factor de desgaste (+2% por cada grado sobre 25°C).
3. **Física del Monoplaza**:
   - **Carga de Combustible**: Mejora de ritmo de ~0.04s por vuelta debido a la reducción de masa.
   - **The Cliff (El Acantilado)**: Penalización exponencial de tiempo cuando un neumático supera su límite de vueltas útiles (Soft: 15, Medium: 25, Hard: 35).
4. **Logística de Pits**:
   - **Pit Loss**: Tiempo fijo perdido en el carril de boxes (default 22s).

##  Metodología de Optimización
El simulador emplea un algoritmo de **Fuerza Bruta Optimizado** mediante `itertools`:
- **Generación de Combinaciones**: El sistema genera todas las permutaciones posibles de vueltas de parada y tipos de neumáticos.
- **Validación de Reglas (Constraints)**:
    - Longitud mínima de stint: 5 vueltas.
    - Longitud máxima por compuesto para evitar fallos estructurales.
    - Uso obligatorio de diferentes compuestos si la simulación así lo requiere.
- **Simulación en Paralelo**: Evalúa cada estrategia calculando el tiempo acumulado vuelta por vuelta y selecciona la que minimiza el cronómetro total de carrera.

##  Casos de Uso
- **Análisis Post-Carrera**: Comparar si una estrategia diferente hubiera dado un mejor resultado.
- **Planificación de Carrera**: Predecir el impacto de un cambio de temperatura repentino en la degradación.
- **Herramienta Educativa**: Entender los "trade-offs" entre velocidad de punta (Ssoft) y durabilidad (Hard).