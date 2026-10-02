# candidate_046 · expbench · neurips2024/94328/9

[All trial-1 traces](../../README.md)

- Trial: **1**; endpoint: **original**; attempt: **1**.
- Native status: **completed**; normalized native score: **38/100**.
- Recorded protocol: `researcher-review-v2`.
- Actor, simulator, and judge: **GPT-6 Astra, low reasoning**.
- Scope: chronological shared messages and handoff fields. Private tool logs, system prompts, evaluator references, and raw API requests are not included.
- A repaired endpoint belongs to the same trial; it is not an independent repeat. Zero scores and missing scientific submissions are retained.

## Shared conversation

### Event 1 — Simulator

**Message**

````text
Por favor, revise únicamente los insumos disponibles y proponga un enfoque; no elabore todavía el diseño final ni ejecute experimentos. El objetivo es diseñar una comparación de QuaRot-RTN y QuaRot-GPTQ en Phi-3-mini-4k-instruct, con INT4, INT6 e INT8, usando perplejidad y exactitud zero-shot. No se requiere repositorio ni cómputo. Resuma qué está respaldado por los insumos y qué sería una elección metodológica. Proponga brevemente la matriz de comparación, controles, evaluaciones y análisis, e identifique las incertidumbres importantes: qué tensores se cuantizan, adaptación de QuaRot a Phi-3, calibración, compatibilidad de INT6 y recursos futuros. Distinga la evidencia sobre este modelo de cualquier afirmación más amplia sobre modelos no LLaMA. Señale los supuestos que debamos acordar antes de desarrollar el diseño.
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
El brief establece una tarea de diseño, sin ejecución, y fija modelo, métodos, precisiones y métricas. No aporta resultados, datos ni presupuesto de ejecución; primero corresponde revisar los insumos y acordar el enfoque.
````

**Objectives Open**

````text
[
  "Inspeccionar los insumos y separar requisitos de supuestos.",
  "Acordar un enfoque de comparación y controles adecuados.",
  "Identificar incertidumbres técnicas y de viabilidad antes del diseño final."
]
````

### Event 2 — Actor

**Answer**

````text
## Alcance y respaldo de los insumos
Los insumos fijan la pregunta: comparar QuaRot-RTN y QuaRot-GPTQ en Phi-3-mini-4k-instruct a 4, 6 y 8 bits mediante perplejidad y exactitud zero-shot. Se solicita únicamente un diseño, sin necesitar repositorio ni cómputo. No he ejecutado experimentos.

El material disponible no aporta resultados, código, configuraciones de cuantización ni detalles de evaluación. Los seis identificadores de temas son referencias para consultar al investigador; sus contenidos no están incluidos. Por tanto, todavía no puede afirmarse que alguna variante funcione mejor, que exista una adaptación validada a Phi-3 o que INT6 tenga soporte operativo. Todo lo que sigue es una propuesta metodológica, no una reproducción respaldada por esas fuentes.

## Enfoque propuesto, pendiente de aprobación
- **Matriz principal:** seis condiciones, RTN y GPTQ × INT4, INT6 e INT8, todas con QuaRot y el mismo checkpoint. La comparación debe fijar primero qué significa el número de bits: solo pesos o pesos y activaciones; la precisión de caché KV también debe declararse explícitamente.
- **Controles esenciales:** modelo original en una precisión flotante acordada y modelo rotado sin cuantizar. El segundo permite detectar errores de adaptación antes de atribuir degradaciones a cuantización. Como extensión opcional, condiciones RTN/GPTQ sin QuaRot permitirían separar el efecto de la rotación del cuantizador; no son imprescindibles para comparar las dos variantes solicitadas.
- **Comparabilidad:** compartir checkpoint y revisión, tokenizer, tensores elegibles y exclusiones, rotaciones y semillas emparejadas, granularidad y esquema de cuantización, reglas de clipping compatibles, precisión de acumulación y evaluación. Registrar las diferencias intrínsecas de GPTQ, especialmente calibración y opciones de optimización, sin ocultarlas bajo una etiqueta común.
- **Evaluaciones candidatas:** perplejidad en WikiText-2 y, si interesa ampliar cobertura, un conjunto de texto adicional acordado; exactitud zero-shot en una batería predefinida, por ejemplo PIQA, HellaSwag, WinoGrande y tareas de ARC. Ni esos conjuntos ni sus protocolos están fijados por los insumos. Acordar versiones, particiones, longitud y segmentación de contexto, máscara de pérdida, formato de prompts, ausencia de ejemplos y elección de accuracy o accuracy normalizada por tarea. Mantenerlos idénticos en todas las condiciones.
- **Análisis:** informar resultados por condición y por tarea, degradación frente al control flotante y diferencia emparejada GPTQ−RTN por bit. Analizar si esa diferencia cambia con la precisión. Si los recursos posteriores lo permiten, repetir calibraciones y semillas y usar intervalos emparejados sobre ejemplos o documentos; no tratar tokens correlacionados como observaciones independientes. No inferir eficiencia de despliegue de una simulación numérica.

## Incertidumbres y acuerdos necesarios
1. **Tensores y precisión:** ¿WbA16, WbAb u otra política? Precisar atención, MLP, embeddings, cabeza de salida, normalizaciones y caché KV, además de escalas, grupos, simetría y acumuladores. Evitar multiplicar escenarios antes de acordar la política principal.
2. **Adaptación a Phi-3:** confirmar variante y revisión exactas e inspeccionar posteriormente la implementación: normalización y fusiones, proyecciones QKV, estructura de atención y MLP, conexiones residuales y ubicación de rotaciones. Verificar equivalencia numérica de la transformación sin cuantización, con tolerancias acordadas, en lugar de asumir que el código para LLaMA se transfiere directamente.
3. **Calibración:** acordar corpus independiente de las evaluaciones, número y longitud de secuencias, semillas y parámetros de GPTQ. RTN no necesita la optimización de GPTQ, pero cualquier calibración de activaciones o clipping que use debe quedar especificada y comparable.
4. **INT6:** distinguir simulación de cuantización de 6 bits de almacenamiento empaquetado y kernels nativos. Si no hay kernels compatibles, proponer evaluación de fidelidad mediante simulación validada, sin afirmaciones de velocidad ni memoria real; documentar redondeo, saturación y niveles representables en los tres anchos.
5. **Recursos futuros:** para ejecutar posteriormente harían falta pesos y datos accesibles, implementación adaptable, dependencias versionadas y un presupuesto de memoria y tiempo por estimar mediante una comprobación pequeña. No se requieren para aprobar este enfoque y no hay base para prometer una GPU o duración concretas.
6. **Fuentes y alcance de la conclusión:** solicitar aclaraciones de los temas suministrados sobre configuración reportada, adaptación, calibración y evaluaciones antes de fijar el diseño. Un estudio en Phi-3-mini-4k-instruct aportaría evidencia sobre ese checkpoint no LLaMA, no sobre todos los modelos no LLaMA; una conclusión más amplia exigiría otros modelos y arquitecturas.

Solicito aprobación del enfoque y acuerdo sobre alcance de cuantización, evaluación simulada o nativa de INT6, protocolos de evaluación y calibración, y carácter opcional de controles sin rotación y repeticiones. No desarrollo todavía el diseño final.
````

**Stage**

````text
plan
````

**Evidence**

````text
La inspección de /workspace y un listado exploratorio con find mostraron únicamente task.json. El archivo contiene la pregunta, la instrucción de diseño sin experimento y una entrada documents.track.md que indica que no se requieren repositorios ni cómputo; no apareció un archivo track.md independiente. No hay código, resultados, pesos, datasets ni textos de los temas referenciados en los archivos inspeccionados. El entorno declarado carece de GPU, red y dependencias de proyecto preinstaladas. Los comandos se limitaron a leer e inventariar los insumos, sin pruebas de modelos ni experimentos.
````

**Assumptions**

````text
[
  "Propuesta pendiente de acuerdo: usar un checkpoint y una política de tensores común para las seis condiciones.",
  "Propuesta pendiente de acuerdo: priorizar fidelidad numérica y permitir simulación validada si no existe soporte nativo de INT6.",
  "Propuesta pendiente de acuerdo: incluir controles flotante original y rotado, dejando las ablaciones sin QuaRot como extensión opcional.",
  "Propuesta pendiente de acuerdo: fijar datasets y protocolos antes de observar resultados y separar calibración de evaluación."
]
````

**Uncertainties**

````text
[
  "Los contenidos de los seis temas de fuentes no están disponibles en los archivos suministrados.",
  "No están especificados los tensores cuantizados, granularidad, clipping, precisión de activaciones o caché KV.",
  "No se ha establecido la validez de la adaptación de QuaRot a esta implementación de Phi-3.",
  "No están fijados corpus y parámetros de calibración, batería zero-shot ni protocolo de perplejidad.",
  "Se desconoce la compatibilidad de INT6 y el presupuesto futuro para una ejecución."
]
````

### Event 3 — Simulator

**Message**

````text
Apruebo el enfoque. Desarrolle ahora el diseño final, sin ejecutar experimentos ni presentar resultados supuestos. Los insumos solo confirman Phi-3-mini-4k-instruct, formato compatible con HuggingFace Transformers, contexto de 4K y comparación QuaRot-RTN/QuaRot-GPTQ en INT4, INT6 e INT8; no hay detalles adicionales de fuentes que debamos esperar.

Como elección metodológica, adoptemos WbAb para las seis condiciones principales, con caché KV flotante fija para aislar esta comparación. Especifique los puntos de cuantización de activaciones y todas las exclusiones, y aclare que esta política no prueba un sistema con KV cuantizada. RTN y GPTQ deben diferir en la cuantización de pesos, manteniendo iguales la rotación y el tratamiento de activaciones. Permita simulación numérica validada en los tres anchos para una comparación homogénea; no derive ventajas de velocidad o memoria de ella.

Incluya controles flotante original y rotado sin cuantizar; conserve la ablación sin rotación como extensión opcional y limite las conclusiones causales sobre el beneficio de QuaRot si se omite. Use WikiText-2 para perplejidad y PIQA, HellaSwag, WinoGrande, ARC-Easy y ARC-Challenge para zero-shot, como elecciones propuestas, no como requisitos de fuente. Fije particiones, puntuación y protocolo reproducible, además de corpus, tamaño, longitud y parámetros de calibración independientes de evaluación. Proponga tres semillas emparejadas, distinguiendo variabilidad de calibración/rotación de incertidumbre de evaluación.

El entregable debe contener matriz experimental, justificación, detalles suficientes de cuantización y GPTQ, adaptación de Phi-3 y pruebas de equivalencia con criterios de aceptación propuestos, análisis emparejado por bit y tarea, plantilla de reporte sin cifras inventadas y viabilidad futura. Los aspectos de arquitectura que requieren inspección posterior deben quedar como verificaciones pendientes con una regla clara para detener o corregir la adaptación. No es necesario fijar recursos o tiempos no conocidos ni ampliar a otras arquitecturas. La conclusión posible será sobre este checkpoint, no sobre todos los modelos no LLaMA.
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
La propuesta cubre las seis condiciones solicitadas, controles de equivalencia, evaluación emparejada y limitaciones de INT6. La inspección reportada no encontró implementación ni resultados; el contrato requiere solo diseño. Las decisiones pendientes pueden fijarse explícitamente como elecciones metodológicas, sin atribuirlas a fuentes ausentes.
````

**Objectives Open**

````text
[
  "Entregar diseño final reproducible con matriz, controles y justificación.",
  "Precisar cuantización, calibración, adaptación y criterios de validación.",
  "Definir evaluación, análisis de incertidumbre y alcance de las conclusiones.",
  "Explicar viabilidad futura sin afirmar ejecución ni resultados."
]
````

### Event 4 — Actor

**Answer**

````text
# Diseño experimental: QuaRot-RTN frente a QuaRot-GPTQ en Phi-3-mini-4k-instruct

## 1. Pregunta, alcance y estatus
Se comparará la pérdida de calidad producida por RTN y GPTQ dentro de una adaptación explícita de QuaRot a **Phi-3-mini-4k-instruct**, usando pesos y activaciones a 4, 6 y 8 bits, con perplejidad y exactitud zero-shot.

**Respaldado por los insumos:** identidad del modelo, formato compatible con HuggingFace Transformers, contexto de 4K y comparación entre QuaRot-RTN y QuaRot-GPTQ en los tres anchos. No se suministraron resultados, implementación ni configuraciones originales de QuaRot para este modelo.

**Acordado metodológicamente:** WbAb, KV flotante, simulación homogénea permitida, controles flotantes original y rotado, batería de evaluación indicada y tres semillas emparejadas. Las especificaciones restantes de este documento son propuestas operativas, no detalles atribuidos a las fuentes.

No se han ejecutado experimentos. Las conclusiones posibles se limitarán a este checkpoint y a esta política de cuantización; no demostrarán generalización a todos los modelos no LLaMA ni calidad de un sistema con KV cuantizada.

## 2. Matriz experimental

| Condición | Pesos elegibles | Entradas de lineales elegibles | KV | Rotación | Réplicas |
|---|---|---|---|---|---|
| F-original | FP32 | FP32 | FP32 | No | Una referencia determinista |
| F-rotado | FP32 | FP32 | FP32 | Sí | Tres semillas |
| QuaRot-RTN-4 | INT4 simulado | INT4 simulado | FP32 | Sí | Tres semillas |
| QuaRot-GPTQ-4 | INT4 simulado | INT4 simulado | FP32 | Sí | Tres semillas |
| QuaRot-RTN-6 | INT6 simulado | INT6 simulado | FP32 | Sí | Tres semillas |
| QuaRot-GPTQ-6 | INT6 simulado | INT6 simulado | FP32 | Sí | Tres semillas |
| QuaRot-RTN-8 | INT8 simulado | INT8 simulado | FP32 | Sí | Tres semillas |
| QuaRot-GPTQ-8 | INT8 simulado | INT8 simulado | FP32 | Sí | Tres semillas |

Son 18 ejecuciones principales, tres controles rotados y una referencia original. FP32 será la aritmética común de la simulación, con TF32 y autocast desactivados. Esta elección favorece el aislamiento de errores de cuantización; no pretende representar el coste de un despliegue FP32 ni optimizar recursos. Los pesos originales se convertirán a FP32 sin recuperar precisión ausente en el checkpoint.

Extensión opcional: RTN/GPTQ sin rotación con idéntica política WbAb, calibración y evaluación. Si se omite, el control rotado solo verificará que la transformación preserva la función: **no permitirá atribuir causalmente una mejora de robustez a QuaRot**.

## 3. Política exacta de cuantización

### Pesos incluidos
Cuantizar todos los pesos de las proyecciones lineales de cada bloque Transformer: Q, K, V, proyección de salida de atención y proyecciones de entrada, compuerta y salida de MLP, según sus nombres reales. Si QKV o gate/up están fusionadas, conservar las correspondencias de filas y documentar las secciones; usar el mismo tratamiento en RTN y GPTQ.

### Activaciones incluidas
Insertar cuantización-desquantización inmediatamente **antes de cada multiplicación por un peso elegible**:
- Entrada a Q/K/V, después de normalización y de las transformaciones de base aplicables. Una entrada compartida se cuantiza una sola vez.
- Entrada a la proyección de salida de atención, después de concatenar las cabezas y de las transformaciones ortogonales correspondientes.
- Entrada a las proyecciones gate/up de la MLP, después de normalización; compartir el tensor cuantizado si comparten entrada.
- Entrada a la proyección down de MLP, después de la no linealidad, producto de compuerta y rotación online de ese espacio.

Las salidas de estas lineales no reciben un cuantizador adicional: permanecen FP32 hasta encontrar otro punto de cuantización definido. La política es idéntica en RTN y GPTQ, aunque las escalas dinámicas puedan diferir porque difieren sus activaciones.

### Exclusiones explícitas
Mantener FP32: embeddings, cabeza de lenguaje, sesgos, parámetros de normalización, acumulaciones de lineales, stream residual y sumas, RoPE, Q y K de salida, logits de atención, softmax, producto atención–V, operaciones de compuerta/no linealidad, rotaciones y sus constantes, escalas de cuantización y caché K/V. No cuantizar por separado Q/K/V después de sus proyecciones. Los valores almacenados en KV ya reflejan el error previo de WbAb, pero **el almacenamiento de KV no se cuantiza**. No se infieren resultados sobre atención enteramente entera.

Un inventario automático deberá enumerar cada módulo incluido/excluido y justificar cualquier módulo no contemplado. Ninguna omisión silenciosa es admisible. Reportar la fracción de parámetros elegibles, además de la etiqueta WbAb.

### Cuantizador común
Para b ∈ {4, 6, 8}, usar un cuantizador simétrico con cero exacto:

qmax = 2^(b−1)−1; s = max(abs(x))/qmax; q = clamp(round_even(x/s), −qmax, qmax); x̂ = s q.

Usar s=1 para grupos completamente nulos. Se excluye deliberadamente el código negativo extremo: 15, 63 y 255 niveles utilizables, respectivamente. Documentar esta convención para evitar confundirla con cuantizadores asimétricos de 16/64/256 niveles.

- Pesos: una escala por canal de salida, a partir del máximo absoluto del peso rotado original; sin agrupación adicional, zero-point, búsqueda de clipping ni reajuste posterior de escalas.
- Activaciones: escala dinámica por token sobre todas las características de entrada de la lineal; sin clipping aprendido ni calibración de rangos.
- Redondeo al par y saturación idénticos en ambos métodos.
- Productos y sumas se simulan desquantizando a FP32. No habrá mezcla de kernels nativos para INT4/INT8 y simulación para INT6.

Así se compara una política precisa, no una supuesta implementación canónica de todos los sistemas denominados W4A4.

## 4. Adaptación de QuaRot y condiciones de validez

Esta será una **adaptación QuaRot de alcance declarado**, no una afirmación de reproducción exacta de un código o resultado no suministrado. El manifiesto deberá describir las transformaciones realmente implementadas.

Propuesta de transformaciones:
1. Rotación ortogonal compartida del espacio residual, absorbida en embeddings, entradas/salidas de subcapas y cabeza de lenguaje. Fusionar escalas de normalización donde lo permita el álgebra; transformar también sesgos existentes.
2. Rotación ortogonal por cabeza del espacio de valores, absorbida en V y compensada en la proyección de salida de atención. No rotar Q/K ni modificar RoPE. Si existe atención de consultas agrupadas, compartir la rotación entre cada cabeza KV y sus cabezas de consulta asociadas.
3. Rotación online después del producto de compuerta de MLP, compensada en el peso down. No desplazar esta rotación a través de la no linealidad.

Para fijar una familia válida incluso con dimensiones no potencia de dos, proponer bloques Hadamard normalizados de tamaño igual a la mayor potencia de dos que divide la dimensión relevante, con permutación y signos aleatorios sembrados. Usar una transformación por espacio compatible; dimensiones de bloque y coste deberán declararse. Esta elección estructurada es metodológica y puede diferir de otras implementaciones de QuaRot. No añadir transformaciones adicionales de mezcla de cabezas sin modificar y registrar el protocolo antes de evaluar.

### Verificaciones pendientes de inspección del checkpoint/código
Comprobar arquitectura y revisión exactas; tipo y posición de normalización; epsilon; sesgos; estructura QKV y MLP fusionada; número y dimensiones de cabezas; GQA/MQA; RoPE y caché; embeddings atados o no; y orden de las operaciones. La compatibilidad HuggingFace no garantiza que un adaptador para LLaMA sea correcto.

La rotación residual propuesta presupone que la normalización admite la transformación ortogonal y la fusión de escalas. No asumir que LayerNorm se comporta como RMSNorm. Si la arquitectura real invalida alguna identidad, **detener la adaptación**, corregir las transformaciones con una demostración algebraica y repetir las pruebas, o declarar que el protocolo no es ejecutable todavía. Si se necesita desatar embeddings/cabeza para preservar la función, registrar el cambio; no atribuirle ahorro de memoria.

### Puertas de aceptación propuestas, antes de cuantizar
- Ortogonalidad: error relativo de Frobenius ||RᵀR−I||F/||I||F ≤ 10^−6 en FP32.
- Pruebas locales de cada transformación, incluidos sesgos y expansión GQA: error relativo L2 ≤ 10^−5 y máximo absoluto ≤ 10^−4·max(1, ||salida referencia||∞).
- Prueba integral F-original frente a F-rotado, para las tres semillas y longitudes 16, 128, 512 y 4096, con texto de validación de adaptación separado de evaluación: error relativo L2 de logits ≤ 10^−4, máximo absoluto ≤ 10^−3·max(1, ||logits referencia||∞) y diferencia de NLL media ≤ 10^−4 nats/token.
- Probar secuencia completa y decodificación incremental con KV flotante. Verificar conservación del tokenizador, atención causal, posiciones y segmentación de cabezas.

Estas tolerancias son umbrales propuestos, no garantías observadas. Un fallo obliga a localizar errores algebraicos, de índices, kernels o precisión; no se relajan los umbrales tras ver las métricas finales. Cualquier revisión deberá justificarse y congelarse antes de la evaluación principal.

## 5. Calibración y definición de GPTQ

### Datos independientes
Usar **128 secuencias de 2048 tokens de la partición de entrenamiento de C4 en inglés**, por semilla, como elección metodológica. Fijar snapshot, subconjunto/shards y hashes en el manifiesto antes de ejecutar. Seleccionar documentos determinísticamente con la semilla, tokenizar con el tokenizer del checkpoint, filtrar documentos demasiado cortos y tomar un segmento contiguo de 2048 tokens por documento. Sin padding, plantilla de chat ni ejemplos de las evaluaciones. Guardar identificadores, offsets y tokens exactos.

Reservar otros 16 documentos, sin solapamiento con calibración, para las pruebas de adaptación. Separación de particiones/corpus no garantiza ausencia de duplicados web: comprobar duplicados exactos de documentos y de textos completos de ítems respecto de la evaluación, sin usar etiquetas para seleccionar datos, y registrar las limitaciones de contaminación residual.

### Semillas emparejadas
Usar semillas maestras 17, 29 y 43; derivar subsemillas separadas para muestreo y rotación. Para cada semilla, compartir rotación y conjunto de calibración entre todos los bits y métodos. RTN no usa el corpus para optimizar pesos; se conserva el emparejamiento y el manifiesto común. En este diseño no se estima por separado el efecto de variar calibración y rotación: en GPTQ se observará su variabilidad conjunta; en RTN, esencialmente la de rotación.

### GPTQ fijado
- Procesar cada matriz elegible en su orden de columnas original, con bloques de 128 columnas; último bloque parcial permitido.
- Para cada bit y semilla, obtener entradas X mediante un pase del modelo rotado con **todos los pesos aún flotantes** y con la política de activaciones WbAb correspondiente habilitada. Así el Hessiano usa las entradas efectivas cuantizadas; no se introduce un esquema secuencial de recalibración con pesos previamente cuantizados.
- Acumular H = XᵀX/N en FP64 por módulo, contando solo tokens reales; usar FP64 para la factorización y FP32 para el peso final desquantizado. No almacenar todos los tokens de todos los módulos simultáneamente.
- Añadir amortiguación λ = 0,01·media(diag(H)). Usar GPTQ estándar con compensación del error hacia las columnas aún no cuantizadas mediante el factor de Cholesky del inverso del Hessiano amortiguado.
- Escalas por fila fijas, iguales a las de RTN para el mismo peso rotado. Sin act-order, true-sequential, MSE clipping, grupos ni ajuste de escalas durante GPTQ.
- Si una columna tiene diagonal exactamente cero, no forzar su peso a cero: desacoplarla en el Hessiano y cuantizarla con RTN. Si todo H es cero, usar RTN para la matriz y registrarlo. Un fallo de factorización no nulo detiene esa condición; no aumentar damping selectivamente sin una revisión declarada del protocolo.

RTN aplica directamente el cuantizador común al mismo peso rotado. La diferencia entre métodos es, por tanto, la selección de pesos cuantizados mediante compensación GPTQ, no otra rotación, clipping o política de activaciones. Las conclusiones serán sobre **esta configuración de GPTQ**, no sobre todos sus hiperparámetros posibles.

## 6. Evaluaciones reproducibles

### Perplejidad
Usar WikiText-2, configuración `wikitext-2-raw-v1`, partición **test**, revisión y hash congelados. Concatenar los registros en su orden con dos saltos de línea; tokenizar sin tokens especiales automáticos. Dividir la secuencia en bloques consecutivos no solapados de hasta 4096 tokens, sin BOS artificial. En cada bloque puntuar posiciones 2…L mediante causal likelihood; incluir el último bloque si contiene al menos dos tokens. No puntuar la primera posición de cada bloque, cuyo contexto se reinicia.

Reportar número exacto de tokens puntuados, NLL total/N y PPL = exp(NLL total/N). No promediar perplejidades por bloque. No ajustar hiperparámetros con test. Este protocolo utiliza hasta 4095 tokens previos y no equivale a una evaluación con ventana deslizante.

### Exactitud zero-shot
Usar un harness de evaluación versionado y congelar también el contenido de sus plantillas, no solo el nombre de la tarea. Las particiones propuestas son:

| Tarea | Partición con etiquetas | Métrica primaria |
|---|---|---|
| PIQA | validation | Accuracy |
| HellaSwag | validation | Accuracy normalizada |
| WinoGrande | validation de winogrande_xl | Accuracy |
| ARC-Easy | test | Accuracy normalizada |
| ARC-Challenge | test | Accuracy normalizada |

Usar cero demostraciones, plantillas de completado del harness, sin plantilla de chat ni system prompt. Para las alternativas, sumar log-probabilidades solo de la continuación de respuesta, incluida su separación textual según la plantilla. Para las tareas normalizadas, dividir por el número de caracteres de la continuación exactamente puntuada; guardar esa cadena y denominador. En WinoGrande usar la regla de likelihood de continuación de su plantilla cloze, no inventar una clasificación generativa por letras. Desempatar por el orden original de opciones.

La implementación debe auditarse contra estas definiciones; si la versión del harness difiere, ajustar el adaptador y congelarlo antes de medir. Guardar prompts renderizados, alternativas, límites de tokenización y puntuaciones por ejemplo. Reportar también accuracy no normalizada en las tareas que la tengan como métrica secundaria, sin seleccionar a posteriori la más favorable.

Ninguna entrada más continuación podrá exceder 4096 tokens: reservar espacio para la alternativa más larga y truncar por la izquierda el contexto común si fuera necesario, manteniendo idéntico contexto para todas las opciones. Registrar cuántos ejemplos se truncaron. Sin muestreo de texto ni temperatura: son decisiones por likelihood. Fijar batch size por tarea y hardware antes de comparar métodos; cualquier reducción por memoria debe aplicarse a todas las condiciones de esa tarea.

Como resumen secundario, promediar sin ponderar las cinco métricas primarias, identificándolo como macro-promedio de métricas heterogéneas, no como una accuracy poblacional única.

## 7. Validación de la simulación
Antes de la evaluación principal:
- Probar escalas nulas, extremos positivos/negativos, empates de redondeo, saturación y valores fuera de rango en los tres bits.
- Verificar códigos enteros, límites permitidos y reconstrucción q·s por grupo.
- Contrastar capas pequeñas con una referencia independiente de operaciones escalares; tolerancia relativa 10^−5 y absoluta 10^−6 para resultados FP32, investigando casos cercanos a cero.
- Verificar que desactivar los cuantizadores recupera F-rotado; comprobar con hooks todos los puntos de activaciones y exclusiones.
- Probar que cambiar b afecta pesos y activaciones en todas las capas elegibles, sin rutas que silenciosamente mantengan FP32.
- Comprobar que RTN y GPTQ comparten escalas originales de pesos, rotaciones, configuración de activaciones y ejemplos de evaluación, y que no hay NaN/Inf.

No es necesario que exista un kernel INT6: la simulación validada proporciona una comparación numérica homogénea. No permite afirmar aceleración, memoria residente reducida, ancho de banda menor ni eficiencia energética.

## 8. Análisis y límites inferenciales
Para cada semilla, bit y tarea, calcular diferencias **GPTQ−RTN**. Una diferencia negativa favorece GPTQ en NLL/PPL; una positiva lo favorece en accuracy. Reportar:
- Resultados absolutos y degradación frente a F-original y al F-rotado emparejado.
- Diferencia emparejada de NLL, diferencia y cociente de PPL; recordar que el cociente de PPL es exp(diferencia de NLL).
- Diferencias de accuracy en puntos porcentuales y conteos de ejemplos que cambian de acierto/error.
- Resultados individuales de las tres semillas, media, desviación estándar y rango. No ocultar el comportamiento por tarea bajo un promedio.
- Contrastes descriptivos entre las diferencias de método a 4, 6 y 8 bits; no asumir monotonicidad con los bits.

**Dos incertidumbres distintas:**
1. Variabilidad de construcción: las tres semillas muestran sensibilidad a rotación/calibración; con tres réplicas no se estiman colas ni se separan sus componentes con fiabilidad.
2. Incertidumbre de evaluación: bootstrap emparejado de 10.000 réplicas, con semilla fija 2026, sobre ejemplos de cada tarea y sobre bloques de WikiText-2. Usar los mismos índices remuestreados para ambos métodos y las tres semillas, promediando la diferencia entre semillas dentro de cada remuestreo. Dar intervalos percentiles del 95% condicionales a esas construcciones. En WikiText-2 remuestrear sumas de NLL y conteos de tokens por bloque y recalcular el cociente; no remuestrear tokens como independientes. La dependencia entre bloques limita la interpretación del intervalo y debe advertirse.

El análisis primario será estimativo, con intervalos por comparación identificados como no simultáneos; no declarar significancia global por seleccionar intervalos favorables entre bits y tareas. Si se desea inferencia confirmatoria posterior, requerirá definir previamente familia de hipótesis y corrección múltiple.

## 9. Plantilla de reporte — sin resultados supuestos

**Manifiesto:** checkpoint/revisión/hashes; tokenizer; código/adaptador/harness; datasets y particiones; entorno y aritmética; semillas; corpus, offsets y tokens de calibración; transformaciones; módulos incluidos/excluidos; cobertura de pesos; cuantizador y GPTQ; pruebas de aceptación y desviaciones del protocolo.

| Condición | Semilla | PPL WT2 | NLL/token | PIQA acc | HellaSwag acc_norm | WinoGrande acc | ARC-E acc_norm | ARC-C acc_norm | Macro |
|---|---|---|---|---|---|---|---|---|---|
| Cada fila de la matriz | Por completar | — | — | — | — | — | — | — | — |

| Bit | Métrica/tarea | GPTQ−RTN por semilla | Media ± DE entre semillas | IC evaluación emparejado | Degradación frente a flotante |
|---|---|---|---|---|---|
| 4 / 6 / 8 | Por completar | — | — | — | — |

Adjuntar tabla de equivalencia, pruebas del cuantizador, fallos o fallback GPTQ, truncamientos y cantidades de ejemplos/tokens. Un fallo técnico debe aparecer como condición no evaluada, nunca como cero ni omitirse silenciosamente. Las celdas se completarán únicamente con mediciones futuras.

## 10. Viabilidad y secuencia futura
1. Obtener checkpoint y snapshots de datos, fijar revisiones y realizar inventario arquitectónico.
2. Implementar/fijar la adaptación y superar las puertas de equivalencia flotante.
3. Validar la simulación y GPTQ en matrices pequeñas y un bloque del modelo.
4. Estimar memoria para pesos, activaciones y Hessianos, y definir carga por capas, batch sizes y almacenamiento de artefactos. No hay base para fijar ahora hardware, duración o coste.
5. Congelar manifiesto y protocolos; construir las condiciones emparejadas y evaluar sin retocar parámetros con los resultados finales.
6. Publicar datos por ejemplo/bloque y análisis emparejado dentro de las licencias aplicables.

El entorno actual no contiene pesos, datos ni implementación y no es un requisito ejecutar aquí. Si FP32 o las rotaciones estructuradas resultan demasiado costosas en el entorno futuro, cualquier cambio de precisión o transformación deberá tratarse como revisión global del protocolo, con nuevas pruebas de equivalencia, no como excepción favorable a una condición.

**Interpretación final admisible:** caracterizar qué método conserva mejor la calidad, y con qué variabilidad, en este checkpoint y esta adaptación QuaRot-WbAb con KV flotante. No extrapolar a otras arquitecturas, QuaRot con otra política de tensores, caché cuantizada o rendimiento nativo de hardware.
````

**Stage**

````text
result
````

**Evidence**

````text
En la exploración previa, inspect_repository y find identificaron únicamente /workspace/task.json. Ese archivo contenía la pregunta y la indicación de que es una tarea de diseño sin necesidad de repositorio ni cómputo, no código ni resultados. No se ejecutaron modelos. La aprobación posterior del investigador confirma Phi-3-mini-4k-instruct, compatibilidad HuggingFace y contexto 4K, y establece WbAb con KV flotante, igualdad de rotación y tratamiento de activaciones, simulación homogénea, los controles, la batería de evaluación y tres semillas emparejadas. No existen fuentes adicionales pendientes según esa aprobación. La elección de cuantizadores dinámicos iguales aísla el método de pesos; los controles flotantes y puertas de equivalencia separan errores de adaptación de errores de cuantización; la simulación común evita confundir soporte de kernels con calidad numérica; la separación de remuestreo de evaluación y semillas evita presentar solo una fuente de incertidumbre como si fuera la total. Ninguna métrica ni prueba de aceptación se presenta como observada.
````

**Assumptions**

````text
[
  "La arquitectura real permitirá una adaptación ortogonal con las identidades descritas; esta es una condición por verificar, no un hecho confirmado por la compatibilidad HuggingFace.",
  "Las revisiones y licencias futuras permitirán acceder al checkpoint y a los corpus y conservar los artefactos reproducibles necesarios.",
  "FP32 común, cuantización simétrica por canal/per-token, rotaciones Hadamard por bloques, GPTQ sin act-order ni true-sequential y el protocolo de calibración son elecciones metodológicas de este diseño, no requisitos atribuidos a las fuentes.",
  "Las particiones, puntuación, semilla de bootstrap y tolerancias propuestas se congelarán antes de evaluar y cualquier cambio se registrará como revisión del protocolo."
]
````

**Uncertainties**

````text
[
  "Falta inspeccionar arquitectura concreta, normalizaciones, fusiones, sesgos, dimensiones y tratamiento de KV; una incompatibilidad detiene la adaptación hasta corregirla.",
  "La adaptación estructurada propuesta no establece equivalencia con todas las implementaciones publicadas bajo el nombre QuaRot.",
  "No se conoce el consumo futuro de memoria/tiempo, ni se requiere soporte nativo INT6 para este estudio numérico.",
  "Tres semillas no separan efectos de calibración y rotación ni caracterizan completamente su distribución.",
  "Los intervalos por bloques de WikiText-2 no eliminan toda dependencia textual; las conclusiones sobre evaluación y contaminación deben conservar estas limitaciones.",
  "Sin ablación sin rotación no se identifica causalmente el beneficio de QuaRot; un solo checkpoint no justifica generalización a todos los modelos no LLaMA."
]
````

### Event 5 — Simulator

**Message**

````text
El diseño final satisface el alcance solicitado: compara QuaRot-RTN y QuaRot-GPTQ a 4, 6 y 8 bits en Phi-3-mini-4k-instruct, con controles, justificación, evaluación, análisis emparejado y viabilidad. Se conserva explícitamente su carácter de diseño, sin resultados empíricos. Las verificaciones arquitectónicas, la equivalencia de las rotaciones y la validación de la simulación quedan correctamente como condiciones previas a una ejecución futura. No solicito revisiones adicionales.
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
El entregable incluye las seis condiciones WbAb con KV flotante, controles original y rotado, política de tensores y cuantizadores, calibración y GPTQ definidos, tres semillas emparejadas, WikiText-2 y las cinco tareas acordadas, criterios de aceptación, intervalos y límites inferenciales, plantilla sin resultados inventados y secuencia de ejecución futura. Declara que la adaptación propuesta no es una reproducción confirmada de una implementación publicada y restringe las conclusiones al checkpoint y política estudiados. No se requiere ejecución para este encargo.
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
  "event_log": "runs/openai-astra-top10-trial-1-batch-1/episodes/expbench_neurips2024_94328_9-f027985e5a4b/candidate_046/attempt-1/output/neurips2024__94328__9/events.jsonl",
  "event_log_sha256": "dfa885964c51e046b0048248def44624a0b0e00d030d0ea3198f414c05a28c41",
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
