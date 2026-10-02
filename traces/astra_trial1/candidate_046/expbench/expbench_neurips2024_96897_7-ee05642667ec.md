# candidate_046 · expbench · neurips2024/96897/7

[All trial-1 traces](../../README.md)

- Trial: **1**; endpoint: **original**; attempt: **1**.
- Native status: **completed**; normalized native score: **50/100**.
- Recorded protocol: `researcher-review-v2`.
- Actor, simulator, and judge: **GPT-6 Astra, low reasoning**.
- Scope: chronological shared messages and handoff fields. Private tool logs, system prompts, evaluator references, and raw API requests are not included.
- A repaired endpoint belongs to the same trial; it is not an independent repeat. Zero scores and missing scientific submissions are retained.

## Shared conversation

### Event 1 — Simulator

**Message**

````text
Por favor, revise únicamente los insumos disponibles y proponga un enfoque para diseñar la comparación de BAdam frente a LoRA al ajustar Llama 3-70B con MathInstruct y evaluar matemáticas zero-shot. No desarrolle todavía el diseño final ni ejecute experimentos. No es necesario disponer de repositorios ni cómputo. En su propuesta, distinga los datos confirmados de las decisiones sugeridas y señale las incertidumbres importantes: variante del modelo, definición de zero-shot, benchmarks y contaminación de datos, criterio de comparación justa, selección de hiperparámetros, variación entre semillas y recursos necesarios. Indique cómo abordaría los controles, el análisis estadístico y la viabilidad, sin anticipar qué método ganará.
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
El encargo exige solo un diseño experimental con justificación, controles, análisis y viabilidad. Los insumos no especifican benchmarks, presupuesto ni resultado esperado; track.md aclara que no hacen falta repositorios ni cómputo.
````

**Objectives Open**

````text
[
  "Revisar los insumos y sus limitaciones.",
  "Acordar un enfoque de comparación y sus supuestos antes de elaborar el diseño final."
]
````

### Event 2 — Actor

**Answer**

````text
## Alcance y datos confirmados
La pregunta es si BAdam supera a LoRA al ajustar Llama 3-70B sobre MathInstruct y evaluar matemáticas zero-shot. Se solicita únicamente diseñar el experimento, no ejecutarlo. Los insumos no especifican checkpoints, versiones de datos, benchmarks, hiperparámetros ni recursos de entrenamiento. No permiten anticipar un ganador.

## Enfoque propuesto — sujeto a aprobación
1. **Precisar modelo y métodos.** Fijar el checkpoint y revisión exactos de Llama 3-70B: base o Instruct es una decisión pendiente con consecuencias para el punto de partida y el formato de entrada. Usar el mismo checkpoint y tokenizer en ambos brazos. Documentar qué implementación de BAdam se emplearía, sus bloques y política de actualización, y qué implementación de LoRA, rango y módulos adaptados. No sustituir LoRA por QLoRA sin convertirlo en una condición explícita.
2. **Definir zero-shot y resultados.** Propongo entender zero-shot como ausencia de ejemplos resueltos en el prompt de evaluación, no ausencia de entrenamiento matemático. Decidir y mantener constantes las instrucciones para razonar, la plantilla, el número de respuestas generadas, la decodificación y los límites de tokens. Como candidatos, considerar GSM8K y MATH, con versiones y particiones aún por confirmar. La selección debe depender de la auditoría de contaminación, no de los resultados de los métodos. Predefinir una métrica primaria —por ejemplo, media macro de exactitud por benchmark— y reportar también cada benchmark; documentar la normalización y comprobación de respuestas matemáticas.
3. **Auditar MathInstruct y las evaluaciones.** Fijar versión, composición, licencias y particiones de MathInstruct. Examinar procedencia y solapamientos exactos y aproximados de problemas y soluciones, incluidos duplicados reformulados. Proponer una variante filtrada común a ambos métodos y una evaluación sobre ítems sin solapamiento detectado; registrar cuánto cambia la mezcla de entrenamiento. No asumir que estos benchmarks son independientes de MathInstruct. La contaminación del preentrenamiento podría no ser verificable: se declararía como limitación, sin presentar «sin solapamiento detectado» como «nunca visto».
4. **Elegir qué significa comparación justa.** Recomiendo como análisis principal igual exposición a datos —mismos ejemplos, tokens útiles, orden emparejado por semilla, longitud de contexto, tratamiento de truncado y batch efectivo—, permitiendo configuraciones específicas de cada método. Esto compara calidad bajo igual exposición, pero no igual coste. Como análisis complementario, proponer calidad bajo un presupuesto común de recursos, si resulta viable. Igualar tiempo o GPU-horas puede implicar distinta exposición; no tratar estos criterios como equivalentes ni igualar artificialmente el número de parámetros entrenables.
5. **Controlar ajuste y selección.** Mantener comunes preprocesamiento, objetivo y máscara de pérdida, precisión cuando sea factible, protocolo de evaluación y regla de selección de checkpoints. Añadir el modelo sin ajuste como control de referencia. Seleccionar hiperparámetros exclusivamente con validación separada, descontaminada respecto de las pruebas. Dar a ambos métodos presupuestos de búsqueda comparables y declarados: tasa de aprendizaje y scheduler, además de rango/escala/módulos/dropout para LoRA y partición/orden/frecuencia de cambio de bloques para BAdam. No imponer la misma tasa de aprendizaje como supuesto de justicia. Registrar también el coste de búsqueda, no solo el entrenamiento elegido.
6. **Incorporar incertidumbre estadística.** Proponer al menos tres semillas finales emparejadas, idealmente cinco si el presupuesto lo permite, separadas de la selección de hiperparámetros. Reportar variabilidad entre entrenamientos y diferencias absolutas de exactitud BAdam−LoRA, además de resultados por benchmark. Consideraría un bootstrap jerárquico emparejado que remuestree semillas e ítems dentro de cada benchmark, con intervalos de confianza y advertencia sobre la escasa precisión con pocas semillas. No tratar todas las predicciones como réplicas de entrenamiento independientes. Predefinir un umbral de relevancia práctica y una regla para concluir superioridad o resultado inconcluso; controlar multiplicidad si se hacen afirmaciones confirmatorias para varios benchmarks. Un intervalo que incluya cero no demostraría equivalencia.
7. **Evaluar viabilidad antes de comprometer recursos.** El diseño final estimaría por método memoria de pesos, gradientes, estados del optimizador, activaciones y buffers, junto con almacenamiento de checkpoints, evaluación y multiplicación por búsquedas y semillas. No asumir que el ahorro de estados de BAdam o los adaptadores de LoRA eliminan el coste de mantener los pesos del modelo. Propondría, para una eventual ejecución aprobada, pruebas mínimas de carga, paso de entrenamiento, extracción de respuestas y medición de memoria/rendimiento antes de una campaña completa. El hardware y la estrategia distribuida quedarían condicionados a esas estimaciones, sin afirmar ahora un número de GPU suficiente.

## Decisiones prioritarias para el diseño posterior
Confirmar base frente a Instruct; definición operativa de zero-shot; benchmarks/versiones y política de contaminación; prioridad entre igual exposición e igual presupuesto; presupuesto de búsqueda y semillas; hardware disponible. En ausencia de aclaraciones, presentaría valores propuestos como supuestos explícitos, nunca como detalles respaldados por los insumos.

Este es únicamente un enfoque preliminar. Esperaría aprobación explícita antes de desarrollar el diseño completo.
````

**Stage**

````text
plan
````

**Evidence**

````text
Se inspeccionó /workspace y se leyó task.json. El único archivo visible es task.json; contiene la pregunta repetida y el contexto de diseño, más un documento incrustado track.md cuyo texto es «Design-only task; repositories and compute are not required.». Una comprobación local con Python confirmó los archivos y ese metadato; no ejecutó entrenamiento ni evaluación. No hay código de BAdam/LoRA, configuraciones, checkpoints ni datos que inspeccionar. El entorno suministrado declara red deshabilitada, ausencia de datasets y GPU, y dependencias de proyecto no preinstaladas. Estos hechos justifican proponer decisiones y verificaciones futuras en lugar de atribuir una configuración concreta a una fuente o afirmar resultados.
````

**Assumptions**

````text
[
  "Las recomendaciones de benchmarks, número de semillas, métrica agregada y criterio principal de igualdad de exposición son propuestas, no requisitos confirmados.",
  "El futuro diseño podría usar un mismo checkpoint inicial y un corpus de entrenamiento auditado común a ambos métodos.",
  "El acceso futuro a pesos, datos y recursos de cómputo tendría que confirmarse para ejecutar; no es necesario para completar este encargo de diseño."
]
````

**Uncertainties**

````text
[
  "Variante y revisión exactas de Llama 3-70B, tokenizer y plantilla.",
  "Versiones e implementaciones concretas de BAdam y LoRA y sus restricciones distribuidas.",
  "Versión/composición de MathInstruct y magnitud de solapamientos con benchmarks; contaminación de preentrenamiento posiblemente no verificable.",
  "Definición de zero-shot, benchmarks elegibles y reglas de puntuación.",
  "Criterio principal de comparación justa, presupuesto de búsqueda y umbral de relevancia práctica.",
  "Variabilidad entre semillas y precisión estadística alcanzable.",
  "Memoria, rendimiento, almacenamiento y hardware necesarios, aún sin mediciones."
]
````

### Event 3 — Simulator

**Message**

````text
Apruebo el enfoque. Desarrolle ahora el diseño experimental final, sin ejecutar experimentos ni anticipar un ganador. Adopte como decisiones propuestas Llama 3-70B base, zero-shot sin ejemplos resueltos en el prompt e igual exposición a datos como comparación principal; mantenga igual presupuesto de cómputo como análisis complementario opcional. Explique que estas elecciones no proceden de una configuración confirmada. Convierta el esquema en un protocolo concreto: brazos y control sin ajuste; particiones y filtrado de MathInstruct; benchmarks, prompts y puntuación; configuraciones y búsqueda equilibrada de hiperparámetros; semillas, métrica primaria, umbral práctico y reglas de conclusión. Especifique cómo distinguirá el efecto sobre MathInstruct filtrado de una afirmación sobre el corpus original, y cómo evitará usar pruebas para seleccionar configuraciones. En BAdam, detalle la variante propuesta, bloques, rotación y tratamiento de estados del optimizador; en LoRA, módulos, rango y escala. Puede dejar revisiones exactas pendientes de fijar antes de una ejecución, pero no deje las decisiones metodológicas centrales como una lista abierta. Incluya un análisis emparejado que respete la variación entre semillas y entre problemas, las limitaciones con pocas semillas y estimaciones razonadas de memoria y coste, sin prometer hardware suficiente sin verificación. Entregue un diseño autosuficiente con justificación, controles, análisis y viabilidad; no se requieren datos, código ni mediciones reales.
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
La propuesta distingue hechos disponibles de supuestos y cubre controles, contaminación, igualdad de exposición, selección independiente de pruebas, incertidumbre y viabilidad. El informe de inspección declara que no hay datos ni implementaciones disponibles; el encargo exige únicamente diseño. No hay una incertidumbre que impida autorizar su desarrollo con supuestos explícitos.
````

**Objectives Open**

````text
[
  "Entregar un protocolo final concreto para comparar BAdam y LoRA en Llama 3-70B con MathInstruct.",
  "Precisar controles, evaluación zero-shot y manejo de contaminación.",
  "Fijar búsqueda, análisis estadístico y criterios de conclusión.",
  "Justificar viabilidad y límites de interpretación sin afirmar ejecución."
]
````

### Event 4 — Actor

**Answer**

````text
# Protocolo experimental: BAdam frente a LoRA

## 1. Alcance, decisiones y estimando

**Requisitos confirmados:** diseñar una comparación de BAdam y LoRA al ajustar Llama 3-70B con MathInstruct y evaluar matemáticas zero-shot. No se ha ejecutado ningún experimento.

**Decisiones adoptadas para este protocolo, no configuración confirmada por los insumos:** usar Llama 3-70B **base**, definir zero-shot como **cero ejemplos resueltos en el prompt**, y comparar principalmente con **igual exposición a datos**. Las revisiones exactas del modelo, tokenizer, datasets y software se fijarán mediante identificadores y hashes antes de ejecutar.

El estimando principal será la diferencia de calidad entre dos procedimientos de ajuste, cada uno seleccionado con su búsqueda predefinida, al entrenarse sobre una misma versión **filtrada** de MathInstruct. No será una comparación a igual número de parámetros entrenables, ni necesariamente a igual cómputo. Las conclusiones se limitarán a estas implementaciones, presupuesto de búsqueda y condiciones.

## 2. Brazos y controles

- **BAdam:** ajuste por bloques con AdamW, según la variante operativa de la sección 5.
- **LoRA:** adaptadores sobre un backbone congelado, según la sección 5.
- **Control sin ajuste:** checkpoint base original, evaluado con exactamente el mismo prompt, decodificación y puntuación.

Los dos brazos entrenados compartirán checkpoint inicial, tokenizer, corpus, orden de ejemplos emparejado por semilla, objetivo, presupuesto de tokens, batch efectivo y política de longitud. No se añadirá un brazo de ajuste completo: no es necesario para responder la pregunta principal y tendría otro coste.

## 3. Datos, particiones y contaminación

### Construcción de la versión primaria

1. Congelar y conservar una copia inmutable de MathInstruct. Registrar fuentes, tamaños, formatos de solución, licencias y hashes. No atribuirle una composición concreta antes de inspeccionarla.
2. Separar en campos el enunciado, la solución y la respuesta final. Excluir registros vacíos, corruptos o sin supervisión textual utilizable con reglas independientes del método. Conservar las distintas fuentes y estilos válidos; no seleccionar solo las fuentes que favorezcan un brazo.
3. Construir familias de duplicados mediante igualdad tras normalización Unicode, espacios y formato, seguida de detección aproximada. Como regla inicial reproducible, usar Jaccard de shingles de cinco tokens ≥0,8 para generar candidatos, incluyendo una vista de enunciados con números sustituidos por marcadores. Los candidatos aproximados requieren revisión del enunciado completo y no se eliminan por compartir únicamente una respuesta numérica. Agrupar componentes conectados confirmados; conservar un representante determinista de cada duplicado.
4. Auditar MathInstruct contra los splits oficiales de entrenamiento y prueba de GSM8K y MATH. Eliminar de MathInstruct las familias que reproduzcan problemas de esos benchmarks, incluidas soluciones copiadas y reformulaciones verificadas. Usar metadatos de procedencia para retirar familias derivadas conocidas aunque no superen el umbral textual. Si la procedencia de una fuente impide separar con confianza los problemas derivados, excluir la fuente afectada del corpus primario y documentarlo.
5. Una persona o proceso de auditoría separado podrá acceder al contenido de las pruebas **solo para descontaminación**, nunca para ajustar prompts, modelos o hiperparámetros. Congelar sus decisiones antes de entrenar y guardar un manifiesto de exclusiones. Revisar una muestra determinista de pares descartados y no descartados para detectar fallos evidentes; la revisión no demuestra ausencia total de contaminación.
6. Partir las familias restantes mediante hash y semilla fija: **95% entrenamiento, 5% validación**, estratificando por fuente cuando sea posible. Ninguna familia cruzará particiones. Para la búsqueda, usar hasta 2.000 ejemplos de validación, seleccionados determinísticamente y estratificados entre los que tengan respuesta final verificable. Reservar toda la validación para calcular pérdida si hace falta el desempate descrito abajo.

Publicar recuentos antes y después de cada operación, por fuente, longitud y tipo de solución. Si no existe suficiente validación con respuesta verificable, detener y corregir el protocolo antes de cualquier entrenamiento o acceso a resultados de prueba; no improvisar una métrica tras conocerlos.

### Qué permite afirmar el filtrado

El resultado principal responderá a la pregunta para **MathInstruct filtrado con este procedimiento**. El filtrado puede cambiar volumen, dificultad y mezcla de fuentes; por tanto, no permite afirmar directamente qué ocurriría con el corpus original.

Una extensión, identificada como secundaria, repetiría ambos brazos sobre una versión original con solo saneamiento técnico, manteniendo familias duplicadas dentro de una única partición. Utilizaría configuraciones seleccionadas sin consultar pruebas y reportaría por separado ítems de evaluación con y sin solapamiento detectado. Sería una evaluación del régimen original potencialmente contaminado, no evidencia limpia de generalización. Para atribuir cambios específicamente al filtrado y no al volumen, haría falta además un control no filtrado submuestreado para igualar tamaño y mezcla por fuente. Esta extensión no es requisito para concluir sobre el corpus filtrado.

La contaminación del preentrenamiento de Llama puede ser desconocida. “Sin solapamiento detectado con MathInstruct” no significa “nunca visto por el modelo”.

## 4. Evaluación zero-shot

### Benchmarks y prompt

Usar los **splits oficiales completos de prueba de GSM8K y MATH**, con sus revisiones congeladas. No sustituirlos por subconjuntos ni elegirlos después de observar resultados. La auditoría anterior debe completarse antes; si no permite sostener la separación de datos, se informará que la evaluación limpia no quedó establecida.

Para todos los brazos, sin plantilla de chat ni mensaje de sistema, usar esta plantilla textual:

`Solve the following math problem. Show your reasoning and put your final answer in \\boxed{...}.\n\nProblem:\n{problem}\n\nSolution:\n`

No contiene demostraciones. Pedir razonamiento no transforma el protocolo en few-shot. Tampoco implica ausencia de entrenamiento previo en matemáticas.

- Decodificación greedy; una respuesta por problema, sin votación ni self-consistency.
- Sin herramientas, ejecución de código, recuperación de información ni feedback del verificador al modelo.
- Entrada máxima de 2.048 tokens y hasta 2.048 tokens nuevos, dentro del contexto de 4.096 adoptado para este protocolo.
- Parada por EOS o presupuesto agotado. No truncar silenciosamente enunciados: un problema que exceda el límite de entrada se registra como fallo con puntuación cero, para todos los brazos; comprobar esta condición antes de evaluar.

### Puntuación

La exactitud por benchmark será la proporción de respuestas finales correctas. El extractor tomará la última expresión `\\boxed{...}` bien formada, sin fallback a números arbitrarios del razonamiento. Ausencia de respuesta extraíble contará como incorrecta.

- GSM8K: comparación numérica exacta tras normalizar separadores, signos y fracciones.
- MATH: normalización matemática y comprobador simbólico congelado, con timeout, sin aceptar equivalencia cuando la evaluación simbólica falle o cambie dominios de forma no justificada.

Validar el extractor y el comprobador con ejemplos sintéticos y datos de desarrollo, incluidos signos, fracciones, conjuntos y expresiones equivalentes, antes de abrir resultados de prueba. Guardar texto, respuesta extraída, puntuación y causa de error. Una revisión humana ciega de errores puede diagnosticar problemas, pero no cambiar selectivamente las puntuaciones. Si hay un bug sustantivo, versionar la corrección y reevaluar todos los brazos.

**Métrica primaria:** media macro de las exactitudes de GSM8K y MATH, expresada en puntos porcentuales: `100 × (acc_GSM8K + acc_MATH)/2`. Así, MATH no domina simplemente por tener más problemas. Reportar además exactitud por benchmark, niveles/áreas de MATH, fallos de formato y agotamiento del presupuesto como análisis secundarios.

## 5. Entrenamiento y configuraciones

### Elementos comunes

- Pesos y operaciones principales en BF16; acumuladores/estados numéricamente sensibles en FP32. Sin cuantización: LoRA no será QLoRA.
- Contexto de 4.096 tokens. Renderizar los ejemplos con la misma estructura pregunta/solución; enmascarar la pérdida sobre el prompt y calcular entropía cruzada solo sobre la solución.
- Añadir la respuesta final en formato boxed cuando un parser determinista pueda identificarla con confianza; en otro caso conservar la solución original. No generar etiquetas con otro modelo. Esta transformación se comparte entre brazos y queda registrada.
- Excluir del entrenamiento primario las secuencias que excedan 4.096 tokens después de formatearlas, en lugar de truncar soluciones; informar el sesgo y porcentaje excluido. Esta es otra razón para hablar de un corpus operacional filtrado.
- **Dos recorridos completos** del entrenamiento; los mismos tokens y ejemplos en cada brazo. Batch efectivo de **8.192 tokens no padding**, con acumulación y máscara por ejemplo que impida atención cruzada si se usa packing. El último batch puede ser menor; registrar por separado tokens de prompt y tokens supervisados.
- Warmup lineal durante el 3% de pasos, seguido de decay coseno hasta el 10% de la tasa máxima. AdamW con β=(0,9; 0,999), ε=10⁻⁸ y clipping de norma global a 1 sobre los parámetros activos. Checkpoint final de los dos recorridos: no elegir el “mejor paso” con pruebas.

### BAdam propuesto

Se propone **BAdam por capas, actualización de un bloque a la vez y reinicio de estados al cambiar de bloque**. Es una especificación a verificar contra la implementación elegida, no una afirmación sobre una configuración publicada.

- Un bloque por capa Transformer, incluyendo atención, MLP y sus normalizaciones; embedding como bloque separado; normalización final y cabeza de salida como último bloque. Para una arquitectura de 80 capas y pesos de entrada/salida no ligados, serían **82 bloques**. Confirmar la arquitectura; los tensores compartidos, si existieran, se asignan una sola vez.
- En cada paso solo el bloque activo recibe gradientes y actualizaciones. Los otros pesos permanecen congelados, aunque pueda ser necesario propagar gradientes a través de operaciones posteriores al bloque activo.
- Orden cíclico fijo: embedding, capas desde la entrada hasta la salida, bloque final. Continuar el ciclo entre épocas, sin reiniciarlo. No aleatorizar el orden en esta variante.
- Cada activación dura `K` pasos del optimizador. Inicializar momentos Adam de ese bloque a cero al activarlo, contar localmente los pasos para la corrección de sesgo y descartar los momentos al desactivarlo. Conservar los pesos actualizados. No almacenar momentos persistentes de todos los bloques en CPU. Aplicar weight decay únicamente cuando el bloque esté activo.
- Usar el scheduler global común, sin reiniciar warmup en cada bloque.

**Búsqueda BAdam, 12 configuraciones:** tasa máxima ∈ {1×10⁻⁵, 2×10⁻⁵, 5×10⁻⁵}; `K` ∈ {1, 5}; weight decay ∈ {0, 0,1}. Con `K=1` los momentos no se acumulan entre visitas: es una consecuencia explícita de esta variante, no un detalle oculto. Registrar el número de actualizaciones por bloque. Antes de lanzar, verificar que el número de pasos alcanza al menos una rotación completa para `K=5`; de no alcanzarlo, el protocolo requiere revisión previa, no una reinterpretación posterior.

Pruebas unitarias futuras deberán verificar pesos congelados, cobertura de bloques, reinicio de estados y ausencia de copia accidental de estados de todo el modelo. Si una biblioteca tiene otros valores por defecto, se configura o modifica para satisfacer esta definición; cualquier desviación cambia el brazo y debe declararse.

### LoRA propuesto

- Backbone congelado, embeddings, normalizaciones y cabeza sin adaptar.
- Adaptadores en todas las proyecciones `q`, `k`, `v`, `o`, `gate`, `up` y `down` de todas las capas.
- Parametrización estándar `W + (alpha/r)BA`, inicialización aleatoria de A y B a cero, sin bias entrenable, sin rsLoRA ni DoRA.
- Rango `r` ∈ {16, 64}; **alpha=2r**, de modo que alpha/r=2 en ambos rangos.
- AdamW sobre los adaptadores, momentos persistentes durante todo el entrenamiento; weight decay=0.

**Búsqueda LoRA, 12 configuraciones:** tasa máxima ∈ {5×10⁻⁵, 1×10⁻⁴, 2×10⁻⁴}; rango ∈ {16, 64}; dropout ∈ {0, 0,05}.

Las tasas no se igualan artificialmente: el tipo de parámetros actualizado es distinto. Las rejillas son propuestas plausibles, no óptimos conocidos.

## 6. Búsqueda equilibrada y separación de pruebas

Para cada método:

1. Entrenar las 12 configuraciones con una semilla de búsqueda común y los dos recorridos completos.
2. Ordenarlas por exactitud en los mismos ejemplos de validación, con el prompt y parser congelados. Desempatar por menor pérdida media de validación y luego por identificador lexicográfico de configuración.
3. Reevaluar las dos primeras mediante **dos nuevas semillas de entrenamiento** cada una, también con exposición completa. Elegir por la media de exactitud de validación de sus tres entrenamientos, con los mismos desempates.
4. Congelar la configuración elegida. Entrenarla con **cinco semillas finales nuevas**, por ejemplo 101–105, separadas de las semillas de búsqueda 11–13. Emparejar orden y aleatoriedad compartida de datos entre métodos; las inicializaciones propias de LoRA se registran adicionalmente.

Son **16 entrenamientos de búsqueda y 5 finales por método: 42 en total**. Este equilibrio es de oportunidades de búsqueda y exposición, no de GPU-horas. Registrar coste de búsqueda separado del coste del ajuste final. No ampliar la rejilla porque la prueba resulte decepcionante. Un óptimo en el borde de la rejilla se reportará como limitación; cualquier ampliación posterior será un estudio nuevo.

El control base y los checkpoints finales se evalúan en pruebas después de congelar configuraciones y análisis. Los resultados de prueba no intervienen en la búsqueda ni en la selección de prompts, parser o checkpoints.

## 7. Análisis estadístico y reglas de conclusión

Para cada semilla final `s`, calcular la diferencia emparejada `d_s = macroacc_BAdam,s − macroacc_LoRA,s`. La estimación principal será la media de las cinco diferencias. Mostrar todos los valores, media, desviación entre semillas y diferencias por benchmark, no solo el mejor entrenamiento.

**Intervalo principal:** bootstrap emparejado de dos factores, con 10.000 réplicas y semilla de análisis congelada. En cada réplica:

- remuestrear con reemplazo los cinco pares de semillas;
- remuestrear con reemplazo los problemas dentro de cada benchmark, usando los mismos problemas remuestreados para todos los pares de semillas y ambos métodos;
- si la auditoría identifica familias de problemas casi duplicados dentro de una prueba, remuestrear familias como clusters y conservar sus miembros;
- recalcular la diferencia macro media y obtener los percentiles 2,5 y 97,5.

Este procedimiento respeta que las semillas comparten problemas y que cada problema tiene resultados de varios entrenamientos; no trata todas las predicciones como réplicas independientes. Añadir como sensibilidad un intervalo t emparejado sobre los cinco `d_s`, condicionado a los conjuntos de prueba fijos, y mostrar si las conclusiones son frágiles. El bootstrap de problemas interpreta las pruebas como muestra de tareas similares; el análisis condicionado evita confundir esa interpretación con una certeza sobre todo el dominio matemático.

**Umbral práctico predefinido: 1,0 punto porcentual de media macro.** Si `[L,U]` es el intervalo principal:

- `L > +1`: evidencia de ventaja práctica de BAdam bajo este protocolo.
- `U < −1`: evidencia de ventaja práctica de LoRA.
- `[L,U]` completamente dentro de `[-1,+1]`: resultados compatibles con diferencias pequeñas según este criterio operacional, sin afirmar equivalencia universal.
- En cualquier otro caso: resultado no concluyente sobre superioridad práctica. Un intervalo por encima de cero pero que cruce +1 indicará diferencia direccional sin establecer el umbral práctico.

Habrá una única conclusión confirmatoria primaria. Los resultados por benchmark y subgrupo serán descriptivos; no se usarán para reemplazar una conclusión primaria desfavorable. Si se desean pruebas confirmatorias adicionales por benchmark, se declararán antes y corregirán por Holm.

Cinco semillas dan información limitada sobre colas, varianza y cobertura de intervalos; no se promete potencia para detectar un punto. Los intervalos tampoco incorporan plenamente la incertidumbre de repetir toda la búsqueda de hiperparámetros: la inferencia queda condicionada a las configuraciones seleccionadas. No se añadirán semillas mirando si el resultado alcanza significación. Una reducción de recursos a tres semillas debe acordarse antes de consultar pruebas y marcarse como evidencia de menor precisión.

## 8. Viabilidad, memoria y coste

### Memoria: estimaciones de orden de magnitud, no mediciones

Con 70.000 millones de parámetros, solo los pesos BF16 requieren aproximadamente **140 GB decimales** —unos 130 GiB—, antes de activaciones, buffers y fragmentación. Ninguno de estos métodos elimina ese requisito si los pesos permanecen residentes.

- **BAdam:** una capa de aproximadamente 0,85–0,9 mil millones de parámetros requiere unos 12–13 GB adicionales si se cuentan gradiente BF16, copia maestra FP32 y dos momentos FP32: 14 bytes por parámetro activo. Un bloque de embeddings/cabeza de aproximadamente mil millones puede llevar esa cifra a unos 15 GB. El mínimo agregado orientativo sería 152–155 GB, antes de activaciones y buffers. Retener momentos de todos los bloques cambiaría radicalmente esta estimación y violaría la variante propuesta.
- **LoRA:** suponiendo 80 capas, dimensión oculta 8.192, MLP 28.672 y proyecciones K/V reducidas por GQA, adaptar las siete proyecciones añade aproximadamente 207 millones de parámetros con rango 16 y 828 millones con rango 64. A 16 bytes por parámetro adaptador —peso, gradiente, copia maestra y momentos— son aproximadamente 3,3 y 13,3 GB adicionales. El mínimo agregado sería unos 143–153 GB más activaciones/buffers.

Estas dimensiones se verificarán en la configuración real. Las copias maestras y tipos de gradiente dependen de la implementación; publicar el desglose real en lugar de asumir que todas las bibliotecas usan la misma contabilidad.

Sharding de pesos, checkpointing de activaciones y microbatches pequeños probablemente sean necesarios. Dos GPU de 80 GB dejarían muy poco margen agregado y no se consideran suficientes por esta cuenta. Un nodo con varias GPU de 80 GB —por ejemplo 4–8— es un **candidato para verificar**, no una garantía. Pesos reunidos temporalmente, comunicación, buffers, activaciones y congelación dinámica pueden invalidar estimaciones simples. La congelación de pesos no elimina automáticamente la retropropagación por capas congeladas.

### Tiempo y presupuesto

Medir primero el número real `D` de tokens por recorrido y usar `T=2D`. Como ilustración exclusivamente presupuestaria, si quedaran 200.000 registros con 500–1.000 tokens de media, cada entrenamiento consumiría 200–400 millones de tokens tras dos recorridos. No se afirma que esos sean los tamaños observados de MathInstruct filtrado.

Un cálculo grueso de 4–6 FLOP por parámetro y token daría, para ese escenario, aproximadamente **5,6×10¹⁹ a 1,68×10²⁰ FLOP por entrenamiento**. A 100–300 TFLOP/s efectivos por GPU equivaldría a aproximadamente 52–467 GPU-horas por entrenamiento; 42 entrenamientos representarían unas 2.200–19.600 GPU-horas, antes de evaluación y contingencias. Son cotas orientativas basadas en throughput supuesto, no predicciones: BAdam, LoRA, recomputación y comunicación pueden apartarse sustancialmente de esta aproximación.

Contabilizar además generación sobre todos los problemas y validaciones, transferencia de datos, auditoría, almacenamiento y fallos. Un checkpoint BAdam completo ronda el tamaño del modelo, mientras que un checkpoint LoRA puede guardar solo adaptadores; usar retención limitada e incluir estados y metadatos necesarios para reanudar. No estimar el coste de BAdam solo por el tamaño del bloque activo.

Antes de una ejecución completa, serían necesarias verificaciones futuras de carga, un paso de cada brazo, cobertura de una rotación, equivalencia del batch, memoria pico, tiempo por token y puntuación. Estas son condiciones de viabilidad propuestas, **no pruebas realizadas**. Si la campaña no cabe en el presupuesto, revisarla antes de consultar resultados; un estudio reducido no debe presentarse como si hubiera satisfecho este protocolo.

## 9. Análisis complementario opcional a igual cómputo

Ejecutarlo solo con presupuesto adicional preasignado. Utilizar el mismo tipo y número de GPU, y fijar un límite idéntico de GPU-horas de entrenamiento a partir del perfil de rendimiento, sin acceso a puntuaciones de prueba. Igualar también el presupuesto total de búsqueda por método en GPU-horas. Seleccionar y evaluar checkpoints al alcanzar el límite, reportando tokens efectivamente vistos. Mantener el resto de condiciones.

Respondería a una pregunta distinta: calidad alcanzada con ese hardware y presupuesto, no con igual exposición. No mezclarlo con el análisis principal ni interpretar una comparación de tiempos entre sistemas diferentes como eficiencia intrínseca del método.

## 10. Entregables y límites de interpretación

Conservar manifiestos de datos y exclusiones, revisiones, configuraciones completas, hashes, semillas, logs por bloque, todos los resultados de búsqueda, predicciones y código de puntuación/análisis. Publicar calidad, incertidumbre, coste y fallos, incluso si no hay diferencia concluyente.

Este protocolo no anticipa un ganador. Una conclusión positiva sería sobre la variante concreta de BAdam, el LoRA seleccionado, Llama 3-70B base y MathInstruct filtrado bajo igual exposición; no demostraría superioridad universal, ausencia de contaminación del preentrenamiento ni una ventaja bajo igual cómputo.
````

**Stage**

````text
result
````

**Evidence**

````text
En la exploración previa se inspeccionó /workspace y se leyó task.json. El único archivo visible fue task.json; contenía la pregunta repetida, el contexto de diseño y el documento incrustado track.md: «Design-only task; repositories and compute are not required.». Una comprobación local con Python confirmó esos metadatos sin entrenar ni evaluar. No se encontraron código, configuraciones, checkpoints ni datos para verificar detalles de implementación. El entorno suministrado declara red deshabilitada, ausencia de GPU y datasets, y dependencias de proyecto no preinstaladas. El investigador aprobó después el enfoque y solicitó adoptar como propuestas modelo base, zero-shot sin demostraciones e igualdad de exposición. Las rejillas, bloques, prompts, umbral, presupuesto y reglas estadísticas de esta entrega son decisiones explícitas de diseño. Las cifras de memoria proceden de contabilidad de bytes por parámetro y dimensiones arquitectónicas que deben verificarse; las cifras de cómputo son escenarios algebraicos, no observaciones. La separación entre auditoría, validación y pruebas evita usar resultados de prueba para elegir configuraciones; el emparejamiento y el remuestreo de semillas y problemas evitan tratar predicciones correlacionadas como entrenamientos independientes.
````

**Assumptions**

````text
[
  "Se podrá acceder legalmente al checkpoint base de Llama 3-70B, al tokenizer y a las revisiones de MathInstruct, GSM8K y MATH necesarias para una futura ejecución.",
  "La arquitectura numérica usada para ilustrar memoria —80 capas y dimensiones indicadas— deberá confirmarse mediante la configuración exacta; no se verificó con pesos disponibles.",
  "La implementación elegida permitirá congelación dinámica por bloques, reinicio explícito de estados, precisión y sharding conforme al protocolo; los valores por defecto de una biblioteca no sustituyen esa verificación.",
  "Existirá suficiente entrenamiento filtrado para cubrir la rotación de bloques y suficiente validación con respuestas verificables; el protocolo incluye condiciones de parada previa si no se cumple.",
  "El umbral práctico de un punto, las rejillas, cinco semillas y los dos recorridos son decisiones metodológicas propuestas y aprobables, no datos de una configuración fuente.",
  "La campaña completa y la extensión a igual cómputo dependen de recursos futuros; ninguna ejecución es necesaria para cumplir esta tarea de diseño."
]
````

**Uncertainties**

````text
[
  "Revisiones exactas, procedencia detallada y proporción de registros excluidos, largos o sin respuesta verificable.",
  "Contaminación semántica no detectada y contaminación del preentrenamiento, que podrían seguir sin identificarse después de la auditoría.",
  "Correspondencia entre la variante operativa de BAdam propuesta y una biblioteca concreta; cualquier divergencia deberá resolverse antes de entrenar.",
  "Sensibilidad a hiperparámetros fuera de las rejillas y variación del propio procedimiento de selección, no capturada plenamente por cinco semillas finales.",
  "Precisión y cobertura de los intervalos con solo cinco semillas y capacidad para detectar el umbral práctico.",
  "Memoria pico, throughput, escalado distribuido y coste de evaluación reales; no se ha verificado suficiencia de ningún hardware.",
  "Resultados sobre MathInstruct original y bajo igualdad de cómputo, que no se deducen del análisis primario filtrado."
]
````

### Event 5 — Simulator

**Message**

````text
El diseño final satisface el encargo: incluye justificación, controles, protocolo de entrenamiento y evaluación, análisis estadístico y viabilidad. Quedan explícitos el alcance sobre MathInstruct filtrado, las decisiones propuestas y las verificaciones necesarias antes de una ejecución. No se requiere trabajo adicional ni ejecutar experimentos. La comparación empírica sigue pendiente; el diseño no establece un ganador.
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
La entrega especifica los dos brazos y el control base, igualdad de exposición, auditoría de contaminación, búsqueda separada de las pruebas, cinco semillas finales emparejadas, métrica primaria y umbral práctico. Incluye remuestreo de semillas y problemas, limitaciones inferenciales y estimaciones de memoria y coste claramente presentadas como escenarios no medidos. Las revisiones de software y datos y la compatibilidad de la implementación quedan como verificaciones previas, aceptables para una tarea exclusivamente de diseño.
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
  "event_log": "runs/openai-astra-top10-trial-1-batch-1/episodes/expbench_neurips2024_96897_7-ee05642667ec/candidate_046/attempt-1/output/neurips2024__96897__7/events.jsonl",
  "event_log_sha256": "fb93cba1cfb745cb5aef415c778ab7eb28249526cbfddb55e11762c31327e012",
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
