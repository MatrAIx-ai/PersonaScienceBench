# candidate_046 · expbench · neurips2024/93638/3

[All trial-1 traces](../../README.md)

- Trial: **1**; endpoint: **original**; attempt: **1**.
- Native status: **completed**; normalized native score: **57/100**.
- Recorded protocol: `researcher-review-v2`.
- Actor, simulator, and judge: **GPT-6 Astra, low reasoning**.
- Scope: chronological shared messages and handoff fields. Private tool logs, system prompts, evaluator references, and raw API requests are not included.
- A repaired endpoint belongs to the same trial; it is not an independent repeat. Zero scores and missing scientific submissions are retained.

## Shared conversation

### Event 1 — Simulator

**Message**

````text
Por favor, revise primero los insumos disponibles y presente solamente una propuesta de enfoque, no el diseño completo todavía. El objetivo es comparar las mejoras de razonamiento de SPAG —imitación de GPT-4 seguida de autojuego en Taboo adversarial— con 20-Question y Guess-My-City no adversariales. No hace falta ejecutar experimentos ni disponer de repositorio o cómputo. Distinga los detalles respaldados por los insumos de los supuestos pendientes, especialmente reglas, recompensas y procedimiento de entrenamiento. Proponga cómo separar el efecto de la adversarialidad de las diferencias entre juegos, de la imitación inicial y del presupuesto de entrenamiento; indique qué controles, evaluación externa de razonamiento y análisis estadístico consideraría. Señale las incertidumbres que cambiarían de manera importante el diseño y su viabilidad. No presuponga cuál será el resultado.
````

**Interaction**

````text
initial_request
````

**Phase**

````text
initial_inspection
````

**Action**

````text
continue
````

**Approve Approach**

````text
false
````

**Evidence**

````text
El encargo exige únicamente un diseño experimental; identifica los tres juegos y la secuencia general de SPAG, pero no aporta datos, recursos de entrenamiento ni especificaciones completas de los juegos.
````

**Objectives Open**

````text
[
  "Inspeccionar los insumos y separar hechos documentados de supuestos.",
  "Revisar una propuesta de comparación justa y de identificación del efecto adversarial.",
  "Identificar incertidumbres relevantes antes de autorizar el diseño completo."
]
````

### Event 2 — Actor

**Answer**

````text
## Propuesta de enfoque — pendiente de aprobación

**Objetivo.** Comparar la mejora de razonamiento externo de SPAG con alternativas no adversariales, sin anticipar qué método ganará. Separaría dos preguntas: (1) qué paquete de entrenamiento produce mayor mejora con recursos comparables; (2) qué parte de esa mejora puede atribuirse específicamente a la adversarialidad. Comparar solamente Taboo contra otros juegos no identifica la segunda.

### 1. Qué está respaldado y qué falta
Los insumos describen SPAG como imitación de GPT-4 seguida de autojuego en Taboo adversarial, y proponen 20-Question y Guess-My-City como comparadores no adversariales. No proporcionan reglas operativas, definición de adversarialidad, recompensas, algoritmo de actualización ni datos originales. Por tanto, no asumiría, por ejemplo, que Taboo tiene las reglas del juego comercial, que los otros juegos son cooperativos en un sentido técnico, ni que el autojuego utiliza un algoritmo concreto de aprendizaje por refuerzo.

### 2. Comparaciones que propondría
- **Comparación de paquetes:** partir del mismo modelo base y comparar los tres procedimientos con sus reglas documentadas. Mantener identificable una condición SPAG fiel a la fuente, separada de las modificaciones experimentales.
- **Efecto de la adversarialidad:** añadir variantes adversarial y no adversarial dentro de una misma estructura de juego, conservando información disponible, tareas, vocabulario, límites de turnos y distribución de dificultad. Cambiar objetivos/incentivos de manera explícita. Idealmente se cruzarían juego y adversarialidad; si las reglas no permiten variantes coherentes, priorizaría un contraste interno en Taboo y restringiría la conclusión causal a ese entorno. No presentaría una variante nueva como implementación original.
- **Efecto de la imitación inicial:** incluir modelo base, imitación sin autojuego e imitación más autojuego. Para una comparación limpia, las ramas principales de autojuego partirían del mismo checkpoint de imitación. Si la imitación original es específica de Taboo, este control podría favorecerlo: consideraría entonces una inicialización equilibrada entre juegos y, por separado, imitaciones específicas igualadas en presupuesto. Una rama de autojuego sin imitación permitiría estudiar su interacción con la adversarialidad, si es viable.
- **Efecto del presupuesto:** comparar con un presupuesto de recursos predefinido y reportar por separado tokens generados, tokens de actualización, actualizaciones y coste de generación docente. El número de episodios por sí solo no basta. Consideraría curvas de mejora frente al coste y una comprobación adicional con exposición de entrenamiento comparable: igualar todos los recursos simultáneamente puede no ser posible.

### 3. Controles y mediciones
Mantendría constantes arquitectura, checkpoint base, configuración de evaluación y criterio de selección de modelos; igualaría el esfuerzo de ajuste de hiperparámetros. Separaría secretos, entidades y plantillas de entrenamiento de las pruebas de juego y examinaría contaminación de las evaluaciones externas. Controlaría longitud de diálogo, oportunidades de acción, rol entrenado y régimen de actualización del oponente en la medida permitida por cada juego. Las variantes nuevas necesitarían comprobarse primero por validez de reglas, incentivos y dificultad; estas comprobaciones no serían evidencia de mejora de razonamiento.

La variable principal sería la **mejora frente al checkpoint anterior al autojuego en una batería externa congelada**, con dominios matemático, lógico y multietapa, preferentemente de corrección verificable. También mediría la mejora total desde el modelo base. Seleccionaría benchmarks concretos después de conocer el modelo y los datos, evitando solapamientos y efectos techo. Usaría el mismo presupuesto de inferencia, prompts y procedimiento de puntuación para todas las ramas. Éxito dentro del juego, generalización a secretos nuevos y explotación de recompensas serían diagnósticos secundarios, no sustitutos de razonamiento externo.

### 4. Análisis previsto
Preespecificaría un agregado principal y los contrastes SPAG frente a cada comparador, junto con el contraste interno de adversarialidad. Usaría varias semillas de entrenamiento, preferentemente emparejadas por inicialización y particiones. Estimaría diferencias de mejora e intervalos de confianza teniendo en cuenta tanto la variación entre ejecuciones como entre ítems; no trataría miles de respuestas de una única ejecución como réplicas independientes de entrenamiento. Si se realiza el cruce, estimaría interacciones juego × adversarialidad y, si procede, imitación × adversarialidad. Prevería corrección por comparaciones múltiples y un umbral de relevancia práctica. El número de semillas requeriría un análisis de potencia o sensibilidad basado en varianza disponible; no fijaría una cifra supuestamente suficiente sin esa información.

### 5. Aclaraciones prioritarias antes del diseño completo
Solicitaría al investigador los extractos relevantes de los temas `neurips2024/93638/3:setup_2`, `setup_32` y `setup_33`, sin presuponer qué contiene cada uno:
1. ¿Cuáles son las reglas, información privada, roles, acciones permitidas, terminación y restricciones de lenguaje de cada juego?
2. ¿Qué recompensas recibe cada rol, cómo se verifica el éxito y qué significa exactamente «no adversarial» en los comparadores?
3. ¿Cómo se construye la imitación de GPT-4: prompts, juegos cubiertos, volumen, filtrado y roles imitados?
4. ¿Cuál es el procedimiento de autojuego y actualización: algoritmo, selección de episodios, actualización de roles, oponentes y tratamiento de recompensas?
5. ¿Qué modelo, datos, presupuestos y evaluaciones originales deben preservarse para considerar una condición una reproducción fiel?

Estas respuestas pueden cambiar si es posible manipular adversarialidad sin alterar simultáneamente información o dificultad, si conviene una inicialización común y cuántas ramas son viables. Si no se obtienen, se podría diseñar una prueba de mecanismos bajo reglas explícitas, pero no atribuirle fidelidad al SPAG original. La propuesta no requiere ejecutar entrenamientos ahora; quedaría a la espera de aprobación para concretar el diseño.
````

**Stage**

````text
plan
````

**Evidence**

````text
Se inspeccionó /workspace y se leyó task.json. Una comprobación con find /workspace -maxdepth 2 -type f -print identificó únicamente /workspace/task.json. Ese archivo contiene la pregunta, la posibilidad de aclarar detalles por tema y una entrada documents.track.md que indica que la tarea es solo de diseño y no requiere repositorio ni cómputo; no se encontró un archivo track.md independiente. No hay implementaciones, reglas detalladas ni resultados de experimentos entre los archivos observados. El mensaje del investigador informa además que no hay datasets, GPU ni red. Las comprobaciones fueron exclusivamente de inspección, no experimentos.
````

**Assumptions**

````text
[
  "La evaluación externa podrá elegirse y congelarse antes de ajustar los métodos; los benchmarks específicos todavía no están determinados.",
  "Un checkpoint inicial compartido y variantes internas de juego son opciones experimentales propuestas, no detalles documentados de SPAG.",
  "La viabilidad de un factorial completo dependerá de reglas e incentivos aún no suministrados y del presupuesto de una futura ejecución."
]
````

**Uncertainties**

````text
[
  "No están documentadas las reglas y recompensas de los tres juegos ni qué componente operacional define su adversarialidad.",
  "No se conocen el algoritmo de entrenamiento, la composición de la imitación, el filtrado de episodios ni la dinámica de oponentes.",
  "Cambiar objetivos puede alterar dificultad, distribución de trayectorias y señal de aprendizaje; habría que distinguir mecanismos del tratamiento de confusores evitables.",
  "Se desconocen modelo, contaminación potencial, varianza entre semillas y recursos futuros; no es posible justificar todavía benchmarks definitivos, potencia o número de ejecuciones."
]
````

### Event 3 — Simulator

**Message**

````text
Apruebo el enfoque. Prepare ahora el diseño final con justificación, brazos y controles, protocolo de entrenamiento propuesto, evaluación, análisis y viabilidad; no ejecute experimentos. Mantenga la distinción entre comparar paquetes y atribuir un efecto a la adversarialidad.

Los únicos extractos disponibles son: neurips2024/93638/3:setup_2 exige investigar si SPAG con Taboo adversarial mejora más el razonamiento que 20-Question y Guess-My-City; neurips2024/93638/3:setup_32 especifica el entorno adversarial SPAG; neurips2024/93638/3:setup_33 especifica esos dos comparadores no adversariales. No aportan reglas ni detalles de entrenamiento adicionales. Por ello no espere nuevas aclaraciones ni presente una reproducción fiel como garantizada: identifique qué deberá verificarse contra la fuente y marque las decisiones operativas como propuestas.

Priorice un diseño mínimo informativo con los tres juegos, base, imitación sin autojuego y un contraste interno de Taboo que cambie los incentivos conservando las reglas e información en lo posible. Separe claramente una inicialización común equilibrada para aislar el autojuego de la comparación de paquetes con imitaciones específicas. El factorial completo y el autojuego sin imitación pueden quedar como extensiones. Explique cómo una variante no adversarial evita soluciones triviales o revelación del secreto; no intente igualar a posteriori las trayectorias o la dificultad producidas por el propio tratamiento.

Concrete reglas y recompensas propuestas, unidad de asignación, roles entrenados, control principal de recursos y manejo de fallos. Proponga una batería externa concreta, agregado y contrastes preespecificados, intervalos y corrección múltiple, umbral práctico y una estrategia de potencia o sensibilidad sin inventar varianzas. Distinga superioridad frente a ambos comparadores de resultados mixtos o inconclusos. Incluya recursos necesarios para una futura ejecución, sin afirmar disponibilidad ni resultados.
````

**Interaction**

````text
next_task
````

**Phase**

````text
approach_review
````

**Action**

````text
continue
````

**Approve Approach**

````text
true
````

**Evidence**

````text
La propuesta reconoce correctamente que comparar juegos distintos no identifica por sí solo el efecto de la adversarialidad. Incluye controles de imitación y presupuesto, evaluación externa y replicación por semillas. La inspección reportada no encontró reglas ni implementaciones; los extractos disponibles tampoco resuelven esos detalles. Es suficiente para autorizar un diseño explícito bajo supuestos, no una ejecución ni una reproducción verificada.
````

**Objectives Open**

````text
[
  "Concretar el diseño mínimo y sus controles para comparar SPAG con ambos juegos.",
  "Definir una manipulación interna interpretable de adversarialidad y delimitar la fidelidad a la fuente.",
  "Especificar evaluación, inferencia estadística, criterios de decisión y viabilidad futura."
]
````

### Event 4 — Actor

**Answer**

````text
# Diseño final propuesto

**Alcance:** experimento futuro, no ejecutado. Permitirá comparar tres paquetes de entrenamiento y, por separado, estimar el efecto de cambiar los incentivos dentro de una implementación de Taboo. **No se garantiza una reproducción fiel de SPAG:** los extractos disponibles identifican los métodos, pero no sus reglas ni su algoritmo.

## 1. Requisitos respaldados y decisiones propuestas

**Respaldado por los insumos:** SPAG combina imitación de GPT-4 y autojuego en Taboo adversarial; los comparadores son 20-Question y Guess-My-City no adversariales. Los tres temas suministrados no añaden reglas, recompensas o instrucciones de entrenamiento.

**Propuesto aquí:** todas las reglas operativas, representación de acciones, recompensas, optimizador, presupuesto y evaluación siguientes. Antes de ejecutar deberá cotejarse con la fuente la semántica de Taboo, la información de cada rol, la construcción de demostraciones, las recompensas, el filtrado y la actualización de políticas. Si difieren, los resultados deberán describirse como una prueba con una operacionalización de estos juegos, no como reproducción de SPAG. Las decisiones se congelarán antes del entrenamiento y de examinar resultados externos.

## 2. Preguntas y brazos mínimos

Usar un único modelo base B, con idéntico tokenizer, tamaño, contexto y política de inferencia. I denota imitación supervisada; S, autojuego.

| Bloque | Brazos | Qué identifica |
|---|---|---|
| Referencia | B | Capacidad inicial |
| Inicialización común | I_bal: imitación equilibrada de los tres juegos | Efecto de imitación común |
| Autojuego desde I_bal | S_TA, S_TN, S_20, S_City | Comparación de autojuego con igual punto de partida |
| Paquetes específicos | I_T, I_20, I_City, cada uno sin autojuego y con su autojuego correspondiente | Mejora total de cada paquete y contribución incremental de su autojuego |

Son **12 condiciones**, contando B y reutilizando cada checkpoint de imitación como control sin entrenamiento adicional. I_T alimenta Taboo adversarial; la variante Taboo no adversarial solo necesita el bloque común.

- **Contraste causal central:** S_TA − S_TN, dentro de Taboo y desde I_bal.
- **Comparadores comunes:** S_TA − S_20 y S_TA − S_City. Eliminan diferencias de inicialización, pero todavía combinan diferencias de juego e incentivos.
- **Comparación de paquetes:** I_T+S_TA frente a I_20+S_20 e I_City+S_City, igualando el coste total. No atribuye sus diferencias exclusivamente a adversarialidad.
- Comparar cada rama de autojuego con su propio checkpoint de imitación separa mejora durante autojuego de mejora durante imitación.

I_bal tendrá un tercio de su presupuesto de demostraciones por juego, con ambos roles equilibrados. Incluirá demostraciones Taboo válidas bajo ambos incentivos, identificadas por instrucciones de rol. Todas sus ramas recibirán exactamente el mismo checkpoint. Las imitaciones específicas tendrán el mismo presupuesto total entre sí, dedicado al juego correspondiente. Este bloque representa especialización, no un aislamiento de autojuego.

El factorial juego × incentivos y el autojuego sin imitación quedan como extensiones, no requisitos mínimos.

## 3. Juegos e incentivos: operacionalización verificable

Para evitar que recompensas y verificación dependan de un juez lingüístico opaco, propongo inicialmente **mundos finitos de candidatos y hechos comprobables**, con acciones estructuradas representadas en lenguaje. Esto reduce naturalidad y limita la generalización a diálogo libre, pero hace viable auditar incentivos y separar tratamientos. Las tres tareas usan bancos de hechos, sin acceso a herramientas externas.

### Taboo propuesto

- Un describidor conoce el objetivo secreto; un adivinador conoce la lista de candidatos, pero no el objetivo. Ambos conocen las reglas. La lista y los hechos públicos permiten razonamiento por eliminación.
- Durante cuatro rondas, el describidor selecciona una pista verdadera de un catálogo de atributos públicos; el adivinador responde con una hipótesis. Al terminar, su última hipótesis determina éxito. No hay revelación de acierto durante las rondas, para mantener la misma oportunidad de interacción.
- El catálogo impide usar el nombre objetivo, alias, traducciones, fragmentos identificativos o texto libre. Las pistas se renderizan en formato canónico sin canales de puntuación, IDs u ordenamiento arbitrario que codifiquen el secreto.
- En cada ronda, la pista debe ser nueva y eliminar al menos un candidato todavía compatible. Los casos se seleccionan **antes de asignar el tratamiento** para que existan secuencias legales completas y una solución informativa en cuatro pistas. La ausencia de secuencia legal es un error del generador, no una victoria del agente.
- **TA, adversarial:** recompensa terminal del adivinador +1 si acierta y −1 si falla; describidor recibe el negativo.
- **TN, no adversarial:** ambos reciben +1 si el adivinador acierta y −1 si falla.

Solo cambia la relación entre recompensas y las instrucciones necesarias para comunicar los objetivos. Se conservan secretos, información, acciones legales, límites y verificador. El describidor adversarial no puede mentir, omitir su turno o emitir pistas totalmente vacías; el cooperativo no puede simplemente decir el secreto. Una pista legal especialmente informativa es cooperación permitida, no un fallo. Se comprobará previamente que no todo objetivo tiene una pista única que lo resuelva inmediatamente y que la tarea no es trivial para políticas simples. Esto se hace sobre la distribución generadora, no seleccionando retrospectivamente episodios según el rendimiento de cada tratamiento.

Esta es una **variante experimental de Taboo con pistas restringidas**. Si el Taboo de SPAG usa otros roles o un mecanismo de inducción de palabras prohibidas, no mide exactamente ese mecanismo. Sin reglas originales no puede salvarse esa limitación por nomenclatura.

### 20-Question propuesto

- Un respondedor conoce un objeto secreto; un interrogador conoce los candidatos y el vocabulario de predicados.
- Hasta 20 preguntas binarias sobre atributos; un único intento final de identificación. Preguntas y respuestas usan un esquema canónico. El respondedor debe contestar conforme a la tabla de hechos, sin comentarios o pistas extra.
- Recompensa compartida +1 por identificación correcta, −1 en caso contrario. Sin recompensa por rapidez en el análisis principal.

### Guess-My-City propuesto

- Igual estructura de interrogador/respondedor, con una ciudad secreta y predicados geográficos predefinidos, por ejemplo continente, país, condición costera y rangos de población con fecha fija.
- Hasta 20 preguntas y una respuesta final; recompensa compartida +1/−1. Las respuestas se verifican contra una tabla versionada, no contra conocimiento cambiante del modelo.

En estos dos juegos se entrenarán ambos roles, aunque responder hechos verificables tenga menos demanda estratégica. Esta asimetría se declarará como propiedad de los juegos, no se ocultará como igualdad de dificultad. Preguntas de identificación directa y otras acciones que trivialicen la búsqueda se excluirán mediante un esquema congelado.

## 4. Entrenamiento y asignación

**Unidad experimental:** una ejecución de entrenamiento con semilla independiente, no un episodio ni una pregunta del benchmark. Para cada semilla se generan los checkpoints de imitación y se bifurca I_bal a sus cuatro condiciones. Se aleatoriza la correspondencia entre ramas, flujos de aleatoriedad y orden de ejecución. Las comparaciones emparejadas usan el mismo bloque de semilla.

**Imitación propuesta:** generar demostraciones con una versión registrada de GPT-4, sus prompts y parámetros archivados. Supervisar los mensajes de ambos roles, sin incluir información secreta en el contexto del rol que no debe verla. Validar automáticamente hechos y legalidad; mantener tasas y costes de rechazo. Aplicar pérdida de entropía cruzada solo a respuestas objetivo. Equilibrar roles por tokens supervisados, no únicamente por número de conversaciones.

**Autojuego propuesto:** PPO con recompensa terminal, penalización KL respecto al checkpoint de imitación correspondiente, y una cabeza de valor. Cada condición tendrá una política compartida entre roles, distinguida por instrucciones; minibatches equilibrados por rol. En cada iteración se generan episodios con una copia congelada de la política vigente, se calculan retornos por rol y luego se actualiza la política. No habrá rivales de otras condiciones ni selección oportunista de oponentes. Actualizar ambos roles puede generar interferencia; por eso se conservará idéntico este mecanismo en TA y TN.

El optimizador, límites de contexto, longitud máxima de mensajes, coeficiente KL y calendario se fijarán con un piloto de estabilidad separado de los benchmarks finales. Se usará el mismo esfuerzo de ajuste por condición. No se seleccionarán checkpoints por rendimiento externo: el principal será el checkpoint del presupuesto final, con puntos intermedios predefinidos para curvas de aprendizaje.

### Recursos y fallos

- **Control principal:** presupuesto de cómputo de entrenamiento definido antes de ejecutar, contabilizando generación de rollouts y actualizaciones por separado. Con arquitectura y hardware fijos puede instrumentarse mediante FLOPs estimados/calibrados y verificarse con tiempo de acelerador. No basta igualar episodios.
- En el bloque común, todas las ramas tienen igual presupuesto posterior a I_bal. En paquetes, se igualan tanto presupuesto de imitación como presupuesto posterior; además se contabiliza por separado el coste docente, incluyendo intentos rechazados. Una misma cantidad de cómputo del alumno no garantiza igual gasto en API docente.
- No será posible igualar simultáneamente cómputo, episodios, tokens y actualizaciones. Se reportarán todos; una sensibilidad secundaria igualará tokens de actualización si hay recursos.
- La generación usa un esquema de acciones con verificación posterior. Una acción ilegal termina el episodio: infractor −1, otro rol 0; no se elimina silenciosamente ni se permite que la infracción cuente como victoria. Este tratamiento es idéntico entre incentivos. Los rollouts fallidos consumen presupuesto.
- Errores de infraestructura se reanudan desde checkpoint con registros preservados. NaN u otros fallos de optimización se registran como fallos de ejecución; no se sustituyen por semillas favorables. Se informa tasa de finalización y se separa la comparación de calidad entre ejecuciones válidas de la viabilidad global. Una asimetría sustancial de fallos impide una afirmación simple de superioridad.

No se emparejarán a posteriori trayectorias, dificultad realizada ni tasas de éxito: pueden ser consecuencias legítimas del tratamiento. Solo se comparten distribuciones y restricciones fijadas previamente.

## 5. Evaluación externa

Batería propuesta, con versiones, particiones y prompts congelados:

1. **GSM8K**, test oficial: razonamiento matemático verbal.
2. **MATH-500**: matemática de varios pasos.
3. **BBH**, tareas `logical_deduction` de 3, 5 y 7 objetos: deducción lógica; promedio interno de sus tres tamaños.
4. **BBH**, tareas `tracking_shuffled_objects` de 3, 5 y 7 objetos: seguimiento multietapa; promedio interno de tamaños.

**Resultado principal A:** media no ponderada de esas cuatro puntuaciones porcentuales. Así, el tamaño de un conjunto no determina su peso. Reportar también cada componente; estos conjuntos no representan toda forma de razonamiento.

Usar puntuación verificable de respuesta final, normalización matemática versionada, decodificación determinista, mismo contexto y límite de tokens, sin herramientas ni muestreo selectivo. Prompts fijos con razonamiento permitido y respuesta final extraíble; respuestas no parseables cuentan como incorrectas. Medir longitud y truncamientos para detectar artefactos del presupuesto de inferencia.

Evaluar B, todos los checkpoints de imitación y finales. Para autojuego, ΔA = A_final − A_imitación; para paquetes, A_final − A_B. Al compartir referencia, las diferencias de mejoras dentro de cada bloque coinciden con las diferencias de puntuación final.

Auditar solapamiento con las demostraciones y hechos de los juegos. El preentrenamiento del modelo y de GPT-4 puede contener benchmarks: no se puede garantizar ausencia de contaminación. Añadir como sensibilidad una prueba procedimental inédita de deducción y seguimiento, con generador y semillas de evaluación sellados antes del entrenamiento. No reemplazar a posteriori el agregado por esta prueba.

Evaluación de juego secundaria: objetivos nuevos, combinaciones de atributos retenidas, oponentes fijos de referencia, éxito, legalidad y comportamiento por rol. Sirve para comprobar que el entrenamiento funciona, no para concluir transferencia externa.

## 6. Análisis preespecificado

Cinco contrastes confirmatorios sobre A, todos en puntos porcentuales:

1. S_TA − S_TN desde I_bal.
2–3. S_TA frente a S_20 y S_City desde I_bal.
4–5. Paquete específico Taboo frente a cada paquete específico no adversarial.

**Umbral práctico propuesto:** δ = 2 puntos del agregado, decidido antes de ver resultados. Es una elección de relevancia, no una magnitud derivada de datos existentes; se mostrarán sensibilidades descriptivas a 1 y 3 puntos.

Para cada contraste, calcular diferencias emparejadas entre semillas. Informar medias, dispersión entre semillas y un intervalo del 95% sobre la diferencia media; con pocas semillas, usar el intervalo t emparejado y declarar su dependencia de supuestos. Añadir una sensibilidad mediante remuestreo jerárquico que conserve emparejamiento entre métodos y remuestree semillas e ítems dentro de cada componente. El intervalo principal considera la batería fija; el remuestreo de ítems evalúa sensibilidad a su composición, sin convertir unos pocos benchmarks en una muestra de todo el razonamiento.

Controlar error familiar de los cinco contrastes mediante Holm a α = 0,05. Para hacer transparente la decisión por intervalos, informar también límites simultáneos conservadores mediante Bonferroni. Superioridad práctica requiere evidencia ajustada de diferencia mayor que δ; significación por encima de cero sin superar δ no basta. Las mejoras contra base e imitación y los componentes individuales serán estimaciones secundarias, claramente etiquetadas.

**Potencia:** no hay varianza conocida y no se afirmará que un número arbitrario de semillas basta. Presupuestar inicialmente un piloto de estabilidad y varianza, por ejemplo cuatro bloques independientes, excluidos de la prueba confirmatoria. Con la desviación de diferencias emparejadas s_d, calcular el número necesario para 80% o 90% de potencia, usando α conservador para cinco pruebas y un efecto alternativo mayor que δ. La aproximación n ≈ [(z_(1−α/5)+z_(potencia))·s_d/(d_alt−δ)]² se refinará con distribución t o simulación. Mostrar una tabla de sensibilidad para distintos s_d y d_alt, sin atribuirles valores observados ficticios. Si el presupuesto impone n, informar el efecto mínimo detectable y reconocer evidencia inconclusa cuando corresponda.

### Interpretación de resultados posibles

- **Superioridad frente a ambos comparadores:** requiere superar el criterio ajustado frente a los dos dentro del mismo bloque; no basta un promedio de ambos o una victoria aislada.
- **Paquetes superiores, contraste interno nulo o impreciso:** no sustenta atribución a adversarialidad.
- **Contraste interno favorable:** respalda el efecto de incentivos opuestos en este Taboo restringido, no universalmente en cualquier juego.
- **Resultados mixtos:** superioridad frente a un comparador y no al otro se describe como tal.
- **Intervalos amplios:** inconclusión, no equivalencia. Ausencia de significación no demuestra ausencia de efecto.
- Una afirmación fuerte sobre SPAG requeriría además verificar fidelidad a su procedimiento original.

## 7. Viabilidad y entregables

La ejecución futura necesita: pesos y licencia de un modelo ajustable; acceso autorizado a GPT-4 o demostraciones archivadas; tablas de hechos y generadores de juegos; implementaciones de SFT/PPO, verificadores y evaluación; almacenamiento de rollouts/checkpoints; y aceleradores adecuados al modelo, contexto y paralelismo. No se afirma que estén disponibles. Las necesidades exactas de memoria y horas solo podrán estimarse tras fijar modelo y medir rendimiento en un piloto.

Para reducir coste, reutilizar checkpoints de imitación, precomputar hechos legales y comenzar por el bloque común. Si solo ese bloque puede completarse, informar sobre autojuego e incentivos, dejando sin respuesta la comparación completa de paquetes. El diseño requiere múltiples ejecuciones independientes; muchos episodios de una sola ejecución no compensan su ausencia.

Entregables: especificación versionada de juegos y recompensas; manifiesto de brazos/semillas; presupuesto y reglas de fallos; datos y prompts docentes auditables; preregistro de evaluación/análisis; y, solo tras una futura ejecución, estimaciones con incertidumbre y limitaciones. Este documento no contiene resultados experimentales.
````

**Stage**

````text
result
````

**Evidence**

````text
La inspección previa de /workspace encontró únicamente task.json; find confirmó que no había archivos fuente adicionales a profundidad dos. task.json contiene la pregunta y una referencia textual a una tarea de solo diseño, sin implementaciones, datos, reglas o resultados. El investigador aprobó el enfoque y aclaró que setup_2 exige la comparación, setup_32 identifica SPAG adversarial y setup_33 identifica 20-Question y Guess-My-City no adversariales; ninguno aporta detalles adicionales. Por ello las reglas y PPO se presentan como propuestas, no como observaciones de la fuente. La inicialización compartida controla imitación; el contraste interno mantiene estructura e información y modifica incentivos; las imitaciones específicas responden por separado a la pregunta de paquetes. La evaluación externa evita confundir éxito en el juego con transferencia de razonamiento. No se ejecutó entrenamiento ni evaluación experimental.
````

**Assumptions**

````text
[
  "Se podrá obtener legalmente un modelo ajustable y demostraciones de GPT-4 para una ejecución futura; no se presupone disponibilidad actual.",
  "Los mundos finitos y acciones estructuradas son una operacionalización nueva destinada a verificación y control, no reglas confirmadas de SPAG.",
  "PPO, política compartida entre roles, recompensas terminales, límites de turnos y presupuesto por cómputo son decisiones propuestas sujetas a congelación antes de ejecutar.",
  "El umbral de dos puntos del agregado representa una elección práctica propuesta, no una estimación empírica.",
  "La inferencia principal se refiere a la batería fijada y a las implementaciones estudiadas; no garantiza generalización a toda capacidad de razonamiento."
]
````

**Uncertainties**

````text
[
  "Sin acceso a reglas originales, el Taboo experimental puede diferir sustancialmente del mecanismo de SPAG; una reproducción fiel sigue sin estar garantizada.",
  "La representación restringida facilita verificación, pero puede reducir transferencia al lenguaje natural y hacer algunos roles poco estratégicos.",
  "La potencia y coste dependen del modelo, rendimiento de hardware y variación entre semillas, actualmente desconocidos.",
  "Los benchmarks públicos pueden estar contaminados por preentrenamiento; una auditoría y evaluación procedimental complementaria mitigan pero no eliminan esa limitación.",
  "Cambiar incentivos puede cambiar trayectorias, dificultad realizada y estabilidad del autojuego: son posibles mecanismos del tratamiento, no variables para igualar retrospectivamente."
]
````

### Event 5 — Simulator

**Message**

````text
El diseño final satisface el encargo de diseño experimental: incluye justificación, controles, evaluación externa, análisis y viabilidad, sin afirmar ejecución. Queda explícito que las reglas restringidas de Taboo y el entrenamiento propuesto no constituyen una reproducción verificada de SPAG. Por tanto, una futura conclusión específica sobre SPAG dependerá de cotejar su procedimiento original; con la operacionalización actual, las conclusiones se limitarán a los paquetes y al contraste de incentivos definidos. No solicito más revisiones.
````

**Interaction**

````text
conclude
````

**Phase**

````text
result_review
````

**Action**

````text
stop
````

**Approve Approach**

````text
false
````

**Evidence**

````text
La entrega distingue comparación de paquetes, autojuego desde una imitación común y contraste interno de incentivos. Define brazos, recompensas, unidad experimental, presupuesto, manejo de fallos, batería externa, cinco contrastes con control múltiple y estrategia de potencia sin inventar varianzas. Declara las limitaciones de fidelidad, contaminación y recursos, y no presenta resultados experimentales. Esto cubre el contrato de diseño, para el que no se requiere ejecución.
````

**Objectives Open**

````text
[]
````

## Provenance

````text
{
  "source_run": "runs/openai-astra-top10-trial-1-batch-1",
  "repair_run": "runs/repair-1-openai-astra-top10-trial-1-batch-1",
  "event_log": "runs/openai-astra-top10-trial-1-batch-1/episodes/expbench_neurips2024_93638_3-a0d336b66a08/candidate_046/attempt-1/output/neurips2024__93638__3/events.jsonl",
  "event_log_sha256": "0741497bedd1360517c86163e1434eecd0ba4fd378c011b6625b99a33d3064f6",
  "models": {
    "actor": {
      "model": "gpt-6-astra",
      "provider": "openai",
      "reasoning_effort": "low"
    },
    "researcher": {
      "model": "gpt-6-astra",
      "provider": "openai",
      "reasoning_effort": "low"
    },
    "judge": {
      "model": "gpt-6-astra",
      "provider": "openai",
      "reasoning_effort": "low"
    }
  }
}
````
