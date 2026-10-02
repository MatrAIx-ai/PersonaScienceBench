# candidate_046 · expbench · neurips2024/94328/4

[All trial-1 traces](../../README.md)

- Trial: **1**; endpoint: **original**; attempt: **1**.
- Native status: **completed**; normalized native score: **33/100**.
- Recorded protocol: `researcher-review-v2`.
- Actor, simulator, and judge: **GPT-6 Astra, low reasoning**.
- Scope: chronological shared messages and handoff fields. Private tool logs, system prompts, evaluator references, and raw API requests are not included.
- A repaired endpoint belongs to the same trial; it is not an independent repeat. Zero scores and missing scientific submissions are retained.

## Shared conversation

### Event 1 — Simulator

**Message**

````text
Por favor, revise los insumos disponibles y proponga un enfoque, sin elaborar todavía el diseño final ni ejecutar experimentos. Esta tarea es solo de diseño: no requiere repositorio ni cómputo. Los requisitos confirmados son cuantizar únicamente los pesos y estudiar 4, 3 y 2 bits (neurips2024/94328/4:setup_5, setup_7 y setup_11). RTN es el referente de redondeo sin calibración y GPTQ utiliza una aproximación del Hessiano (neurips2024/94328/4:setup_16 y setup_17). Proponga cómo aislar el efecto de la transformación Hadamard de QuaRot frente a ambos métodos, qué controles, métricas de calidad y estabilidad, y análisis serían apropiados. Indique qué detalles están respaldados por los insumos y cuáles serían decisiones propuestas: modelos, datos, alcance de la transformación, granularidad de cuantización, calibración y recursos. Señale las incertidumbres que puedan cambiar la interpretación o viabilidad; no presuponga que los referentes fallarán ni que QuaRot mejorará los resultados.
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
El encargo exige un diseño experimental, no ejecución. Los insumos fijan cuantización solo de pesos a 2–4 bits y describen RTN y GPTQ, pero no especifican modelos, datos, presupuesto ni resultados esperados.
````

**Objectives Open**

````text
[
  "Revisar los insumos y distinguir requisitos confirmados de supuestos.",
  "Proponer un enfoque controlado para atribuir cambios de calidad y estabilidad a Hadamard.",
  "Identificar incertidumbres relevantes antes de autorizar el diseño final."
]
````

### Event 2 — Actor

**Answer**

````text
Propongo un enfoque factorial pareado, todavía no un diseño final, para comprobar si Hadamard ayuda, no ayuda o perjudica la cuantización solo de pesos.

**Respaldado por los insumos.** Según las confirmaciones aportadas: cuantizar únicamente pesos a 4, 3 y 2 bits (setup_5, setup_7, setup_11); RTN es redondeo sin calibración y GPTQ utiliza una aproximación del Hessiano (setup_16, setup_17). No se han aportado los textos completos de esas fuentes. Modelos, datos, granularidad, calibración y recursos concretos no están establecidos por los insumos inspeccionados.

**Comparación central propuesta.** Para cada modelo y precisión, comparar RTN y GPTQ, cada uno sin transformación y con la misma transformación Hadamard de QuaRot. QuaRot se trataría como transformación previa, no como un tercer cuantizador: los contrastes principales serían Hadamard+RTN frente a RTN y Hadamard+GPTQ frente a GPTQ. Mantener el mismo checkpoint, datos de evaluación, formato y presupuesto efectivo de cuantización, agrupamiento, precisión numérica y reglas de ajuste. No cuantizar activaciones ni caché KV. Examinar separadamente el efecto de Hadamard dentro de cada método y su interacción con método y número de bits.

**Controles propuestos.** Incluir el modelo original en alta precisión y su versión transformada sin cuantización, para comprobar equivalencia funcional dentro de tolerancias numéricas. Fijar las matrices cuantizadas y las exclusiones, y documentar qué rotaciones se fusionan con pesos y cuáles requieren operaciones en ejecución. Evitar atribuir a Hadamard diferencias de clipping, búsqueda de escalas, permutaciones, preprocesamiento o excepciones de capas. Usar una política común de parámetros del cuantizador dentro de cada contraste; cualquier ajuste específico por condición requeriría un análisis separado con presupuesto de ajuste comparable. RTN seguiría sin calibración. Para GPTQ, reutilizar exactamente los textos, cantidad de tokens y semillas de calibración, pero recolectar las estadísticas en las coordenadas correspondientes a cada modelo, no reutilizar sin más el Hessiano del modelo original.

**Calidad y estabilidad propuestas.** Priorizar pérdida media por token y perplejidad en texto retenido; complementar con exactitud en unas pocas tareas de comprensión o razonamiento con protocolo idéntico. Informar tanto calidad absoluta como degradación respecto a alta precisión y diferencias pareadas con/sin Hadamard. Distinguir estabilidad numérica —NaN, Inf, errores de ejecución—, estabilidad de calidad —degradación extrema según umbrales predefinidos— y variabilidad entre semillas o muestras de calibración. No repetir RTN determinista como si aportara réplicas independientes; separar variación de rotación, cuando sea aleatoria, de variación de calibración de GPTQ. Registrar todas las condiciones, incluidas ejecuciones fallidas, sin asumir que los referentes colapsarán.

**Análisis propuestos.** Mostrar resultados desagregados por modelo, método y bits, además de resúmenes; estimar diferencias pareadas e intervalos de incertidumbre con unidades de remuestreo adecuadas, por ejemplo documentos y no tokens tratados como independientes. Usar como diagnósticos secundarios la concentración o valores extremos de pesos, error de reconstrucción por capa y discrepancias de salidas frente al modelo de alta precisión. Estos diagnósticos apoyarían una interpretación del mecanismo, pero no demostrarían por sí solos mejora de calidad. Si se pretende atribuir el efecto a la estructura Hadamard y no a cualquier rotación ortogonal, considerar un control ortogonal alternativo en un subconjunto: sería una extensión, no requisito del contraste principal.

**Decisiones que propongo acordar antes del diseño final.**
- Modelos: una familia y tamaño manejable para verificar el protocolo, y otro tamaño o familia para comprobar generalización si los recursos lo permiten. No hay checkpoints respaldados por las fuentes disponibles.
- Datos: corpus separado para calibración GPTQ y evaluación de perplejidad, más tareas breves; fijar tokenización, longitud de contexto, particiones y ausencia de solapamiento.
- Transformación: especificar si se reproduce toda la transformación funcionalmente equivalente de QuaRot o un subconjunto; esto cambia el alcance de la conclusión.
- Cuantización: fijar cuantizador uniforme, simetría, tamaño y eje de grupos, clipping, precisión de escalas y pesos excluidos; reportar bits efectivos incluyendo metadatos. Son elecciones propuestas, no hechos documentados aquí.
- Calibración: fijar corpus, tokens, longitudes y réplicas para GPTQ; no introducir calibración oculta en RTN.
- Recursos: para un experimento futuro, estimar memoria, tiempo y disponibilidad de kernels tras elegir modelos. La simulación de cuantización puede evaluar calidad, pero no demostrar velocidad ni memoria de un despliegue real de 2–4 bits.

La aclaración más importante sería obtener el alcance exacto de Hadamard y los detalles de cuantización/calibración de las fuentes si se busca una reproducción fiel. Si no están disponibles, pueden fijarse explícitamente como decisiones metodológicas. Solicito aprobación de este enfoque antes de desarrollar el diseño completo; no he ejecutado experimentos.
````

**Stage**

````text
plan
````

**Evidence**

````text
La inspección de /workspace encontró únicamente task.json; una enumeración de archivos a profundidad 2 confirmó que no había código, datos ni documentos fuente adicionales visibles. task.json contiene la pregunta, el contexto de diseño y una nota que indica que no se requieren repositorio ni cómputo. Las restricciones de pesos únicamente, 2–4 bits y las descripciones de RTN y GPTQ provienen de la solicitud del investigador con sus identificadores de fuente, no de textos originales consultados. Solo se realizaron lecturas y enumeración de archivos. El entorno declarado carece de GPU, datasets y red; no es evidencia de resultados experimentales ni limita la elaboración conceptual del diseño.
````

**Assumptions**

````text
[
  "Se permite proponer posteriormente una implementación o simulación fiel de cuantización para estudiar calidad, sin exigir mediciones de despliegue.",
  "Activaciones y caché KV permanecerán en la misma precisión no cuantizada en todas las condiciones; la precisión concreta aún debe fijarse.",
  "Las comparaciones futuras podrán usar checkpoints y datos idénticos dentro de cada contraste pareado."
]
````

**Uncertainties**

````text
[
  "No están disponibles los textos originales de los cinco temas citados, por lo que no se pueden atribuir a ellos detalles adicionales.",
  "El alcance y las compensaciones de la transformación Hadamard pueden condicionar equivalencia funcional, implementación y atribución del efecto.",
  "Granularidad, clipping, pesos excluidos y calibración GPTQ pueden cambiar significativamente los resultados, especialmente a 2 bits.",
  "La disponibilidad futura de modelos, hardware y kernels determinará el tamaño viable del estudio y si podrán medirse costes reales.",
  "Una mejora en unos modelos o tareas no establecería que los referentes fallen de forma general ni que Hadamard estabilice universalmente la cuantización."
]
````

### Event 3 — Simulator

**Message**

````text
Apruebo el enfoque factorial pareado. Desarrolle ahora el diseño final con justificación, controles, plan de análisis y viabilidad, sin ejecutar experimentos ni presentar resultados supuestos. Mantenga como requisitos la cuantización solo de pesos a 4, 3 y 2 bits; activaciones y caché KV no se cuantizan. La comparación central será con/sin Hadamard dentro de RTN y de GPTQ, con controles en alta precisión.

Fije opciones concretas y reproducibles para checkpoints, datos y particiones, contexto, matrices incluidas y excluidas, formato de cuantización, agrupamiento, escalas, clipping, parámetros GPTQ, calibración y semillas. Identifique estas opciones como decisiones propuestas, no como detalles confirmados de las fuentes. No hace falta buscar fuentes adicionales para continuar.

Precise especialmente el alcance de la transformación: dónde se aplican y compensan las rotaciones, cómo se preserva la función ante normalizaciones y no linealidades, qué operaciones se fusionan y cuáles permanecen en ejecución, y cómo se tratan dimensiones incompatibles. Evite describir QuaRot como una rotación arbitraria de cada matriz; si propone un subconjunto, limite expresamente la atribución. Defina la prueba de equivalencia en alta precisión y el criterio para detener una comparación inválida.

Incluya métricas y umbrales operativos propuestos de mejora, degradación extrema y estabilidad; contrastes pareados e incertidumbre separando documentos, semillas de rotación y calibración. Los errores de infraestructura deben distinguirse de fallos numéricos o de calidad. Añada diagnósticos del mecanismo en coordenadas comparables, sin confundir menor error de pesos con mejor desempeño. El control ortogonal alternativo puede quedar como extensión opcional.

Presente una matriz experimental y un alcance mínimo viable, con extensiones para generalización y una estimación prudente de recursos futuros. La simulación sirve para estudiar calidad, no para acreditar aceleración o memoria real de despliegue. Concluya con criterios para interpretar mejora, ausencia de efecto o perjuicio, sin presuponer que RTN/GPTQ fallen ni que QuaRot los rescate.
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
El plan reportado cubre los requisitos de pesos únicamente y 2–4 bits, aísla Hadamard mediante contrastes dentro de cada cuantizador e incluye equivalencia funcional, calibración GPTQ en las coordenadas correctas y análisis pareado. Las decisiones aún abiertas son metodológicas y pueden fijarse explícitamente en el diseño; no se requiere ejecución ni una reproducción de detalles fuente no disponibles.
````

**Objectives Open**

````text
[
  "Concretar un diseño experimental reproducible con alcance preciso de Hadamard y controles de equivalencia.",
  "Fijar métricas, umbrales, replicación y análisis de calidad y estabilidad a 2–4 bits.",
  "Entregar justificación, viabilidad y límites de interpretación sin afirmar resultados experimentales."
]
````

### Event 4 — Actor

**Answer**

````text
## 1. Objetivo y alcance de la atribución

Evaluar si añadir una transformación Hadamard mejora, no altera o perjudica la calidad y estabilidad de modelos con pesos a 4, 3 y 2 bits, dentro de RTN y dentro de GPTQ.

**Requisitos confirmados:** cuantización únicamente de pesos; activaciones y caché KV sin cuantizar; RTN sin calibración; GPTQ con aproximación del Hessiano; contrastes pareados y controles en alta precisión.

**Todo lo que sigue sobre modelos, datos, transformación concreta y parámetros es una decisión propuesta**, no una configuración atribuida a los documentos citados. Propongo estudiar el **subconjunto de rotación Hadamard del flujo residual de QuaRot**, no reproducir todo QuaRot. No se incluyen rotaciones internas de valores de atención ni Hadamard online de la dimensión intermedia del MLP. Esta elección permite una transformación exactamente compensable sin atravesar no linealidades ni añadir kernels especiales. Las conclusiones deberán decir «Hadamard residual» y no adjudicar el resultado al paquete completo de QuaRot.

## 2. Modelos y entradas reproducibles

**Principal:** `TinyLlama/TinyLlama-1.1B-Chat-v1.0`, con su tokenizador, sin plantilla de chat para evaluar texto continuo. Su dimensión residual esperada es 2048; comprobarla en la configuración descargada antes de transformar. No entrenar ni ajustar pesos.

**Extensión de escala:** `meta-llama/Llama-2-7b-hf`, condicionada a acceso autorizado y recursos. La arquitectura con RMSNorm y dimensión residual 4096 permite el mismo procedimiento; no se mezclarán sus resultados con los del modelo principal como réplicas independientes idénticas.

**Congelación:** antes de generar artefactos, resolver una sola vez las revisiones de los checkpoints, tokenizadores y datasets; registrar sus commit SHA, hashes de archivos, versiones de bibliotecas y código. No proporcionar SHA inventados: el manifiesto bloqueado es un prerrequisito de ejecución, y no se permitirá resolver `main` de nuevo entre condiciones.

**Texto:** `Salesforce/wikitext`, configuración `wikitext-103-raw-v1`.
- `train`: exclusivamente calibración GPTQ.
- `validation`: solo comprobaciones de implementación/equivalencia; no optimizar hiperparámetros.
- `test`: evaluación final completa.
- Reconstruir artículos usando cabeceras de nivel superior —líneas que, tras eliminar espacios exteriores, empiezan por `= ` y terminan por ` =`, excluyendo `==`—; conservar subsecciones y saltos internos, descartar documentos vacíos y el preámbulo anterior a la primera cabecera. Guardar los textos reconstruidos y sus hashes para eliminar dependencia del parser.
- Antes de seleccionar calibración, excluir artículos de entrenamiento cuyo texto normalizado tenga el mismo hash que algún artículo de validación o prueba. Esta comprobación no garantiza ausencia de contaminación del preentrenamiento.

**Contexto:** 2048 tokens incluyendo un BOS, sin plantilla de chat ni EOS añadido. Dividir cada documento tokenizado en fragmentos consecutivos de hasta 2047 tokens; anteponer BOS a cada fragmento y evaluar todos sus tokens reales, nunca padding. No cruzar límites de documentos. Usar exactamente los mismos fragmentos para todas las condiciones. Esta perplejidad queda definida por este protocolo, no se presentará como idéntica a la de otros protocolos publicados.

**Tarea secundaria opcional:** `google/boolq`, partición `validation` completa. Prompt fijo: `Passage: {passage}\nQuestion: {question}\nAnswer:`; elegir entre continuaciones ` yes` y ` no` por suma de log-probabilidades. Truncar el pasaje por la derecha si es necesario para dejar cabida a pregunta y respuestas en 2048 tokens. Reportar exactitud y diferencias pareadas; no usarlo para elegir parámetros.

## 3. Transformación: definición, compensación y límites

Usar vectores fila. Una proyección lineal escribe `x W`; cuando el almacenamiento use la convención transpuesta, transformar correspondientemente.

Definir `Q = D H`, con `H` Hadamard normalizada de dimensión residual d y `D` diagonal de signos Rademacher. Generar signos con NumPy PCG64, semillas 11, 23 y 37, y guardar tanto signos como hashes. Se cumple `QᵀQ = I`. Se usa **la misma Q en todo el flujo residual de un modelo**, no una rotación independiente por matriz.

1. **Plegar las ganancias de RMSNorm:** para cada RMSNorm previo a atención o MLP, absorber su vector gamma en las filas de todas las proyecciones consumidoras: Q/K/V o gate/up, respectivamente. Absorber la ganancia final en la cabeza de lenguaje. Sustituir gamma por unos. Hacer este preprocesamiento idénticamente en las ramas identidad y Hadamard. RMSNorm sin ganancia satisface `RMS(xQ) = RMS(x)Q`, pues Q conserva la norma y se mantiene el mismo epsilon.
2. **Embedding:** transformar `E → EQ`, de modo que el estado residual sea `xQ`.
3. **Entrada a atención:** transformar `Wq, Wk, Wv → QᵀWq, QᵀWk, QᵀWv`. Sus salidas quedan en las coordenadas originales. Por tanto RoPE, productos QK, softmax, agrupamiento de cabezas y caché KV no cambian de base y no necesitan compensaciones adicionales.
4. **Salida de atención:** transformar `Wo → WoQ`. La salida vuelve a la base residual rotada antes de sumarse al residual.
5. **MLP:** transformar `Wgate, Wup → QᵀWgate, QᵀWup`; sus preactivaciones permanecen iguales. SiLU y producto elemento a elemento se ejecutan en la base original. Transformar `Wdown → WdownQ` para devolver la salida a la base residual rotada.
6. **Cabeza:** tras RMSNorm final sin ganancia, `Whead → QᵀWhead`; los logits vuelven a ser los originales.

No se conmuta una rotación a través de SiLU, softmax ni RoPE. La invariancia proviene de preservar sus entradas, no de asumir que esas funciones son invariantes a rotaciones. Los checkpoints elegidos deben verificarse sin sesgos en estas proyecciones; si aparece un sesgo, detener este protocolo hasta especificar y probar su compensación. Si embedding y cabeza comparten almacenamiento, se materializarán copias separadas y se documentará; no conservar un alias incompatible silenciosamente.

**Fusión:** todas estas operaciones se materializan offline en pesos, embeddings y cabeza, antes de cuantizar. En ejecución no quedan Hadamard online para este subconjunto. Embeddings y cabeza se transforman pero **no se cuantizan**.

**Dimensiones:** solo se rota el eje residual; las dimensiones intermedias del MLP o las salidas K/V no necesitan ser potencias de dos. Los dos modelos propuestos tienen dimensión residual compatible. Ante una dimensión residual no compatible, excluir ese modelo del protocolo principal; no rellenar, truncar ni sustituir por bloques silenciosamente. Una Hadamard por bloques sería una extensión distinta con su propio control de equivalencia.

## 4. Control de equivalencia y puerta de validez

Conservar tres controles no cuantizados: original, identidad con ganancias plegadas y Hadamard con ganancias plegadas. Construir transformaciones en FP32 y realizar la prueba en FP32 sin TF32, con evaluación determinista.

Usar ocho fragmentos de validación: cuatro de hasta 128 tokens y cuatro de 2048, seleccionados por orden del dataset. Comparar original frente a identidad e identidad frente a cada Hadamard, incluyendo inferencia teacher-forced y una prueba de 32 pasos con caché KV que alimenta los mismos tokens.

**Tolerancias propuestas:** discrepancia relativa L2 de logits ≤ 10⁻⁴; diferencia absoluta máxima de logits ≤ 10⁻²; diferencia de pérdida media ≤ 10⁻⁴ nats/token; ningún valor no finito. Registrar también discrepancias capa a capa, llevando estados residuales rotados a la base original con Qᵀ. Antes de cuantizar, aplicar igualmente una comprobación BF16: diferencia de pérdida ≤ 0,01 nats/token respecto al control identidad BF16 y ausencia de valores no finitos.

Si falla cualquier puerta, **detener las comparaciones afectadas**: investigar implementación o precisión y registrar una enmienda antes de evaluar modelos cuantizados. No interpretar un cambio de función como efecto favorable o adverso de la cuantización. Las tolerancias son operativas propuestas, no teoremas universales sobre redondeo.

## 5. Cuantización y calibración

**Matrices incluidas:** todas las proyecciones lineales de atención `q_proj`, `k_proj`, `v_proj`, `o_proj` y de MLP `gate_proj`, `up_proj`, `down_proj`, en todas las capas.

**Excluidas:** embeddings, cabeza de lenguaje, parámetros de normalización y cualquier parámetro no listado. Activaciones, KV y multiplicaciones de evaluación en BF16; pérdidas y agregación de métricas en FP32 o FP64. Los controles de calidad no cuantizados usarán BF16 con las mismas reglas de evaluación.

**Formato:** entero uniforme simétrico con cero representable, sin zero-point aprendido. Para b bits usar códigos `[-2^(b−1), 2^(b−1)−1]`. Grupos contiguos de 128 pesos a lo largo del eje de entrada de cada fila de salida, sin grupos entre filas; el último grupo, si existe, puede ser menor. Escala `s = max(abs(w))/(2^(b−1)−1)`, almacenada en FP16; reconstrucción `s·q`. El extremo negativo extra del código puede utilizarse en GPTQ si las correcciones lo requieren. Un grupo exactamente nulo produce ceros y escala 1.

RTN calcula `q = clip(round_even(w/s), qmin, qmax)`. No hay búsqueda de clipping ni estadísticas de activación: el rango viene exclusivamente del máximo absoluto del grupo. Saturación fuera de rango según los límites anteriores. No cambiar el formato a 2 bits para favorecerlo. Si una escala no nula redondea a cero o a un valor no finito en FP16, registrar fallo de representación numérica, no introducir una escala alternativa silenciosa.

**GPTQ:** mismos grupos, rangos y escalas, calculados a partir de los pesos antes de la compensación y luego congelados. Hessiano aproximado `2XXᵀ/N` en FP32; amortiguación diagonal de 0,01 por la media de la diagonal; bloques de procesamiento de 128 columnas; orden natural, sin activation-order ni permutación de columnas; sin búsqueda de clipping ni reajuste de escalas. Columnas con diagonal exactamente cero se tratan con diagonal 1 y pesos de esa columna puestos a cero, registrando su cantidad. Si Cholesky falla tras la amortiguación, registrar fallo numérico sin aumentar automáticamente damping.

Procesar bloques Transformer en orden. En cada bloque: cuantizar conjuntamente q/k/v usando la misma entrada; luego o con sus activaciones actualizadas; después gate/up conjuntamente y finalmente down. Propagar la salida del bloque cuantizado al siguiente. Recolectar estadísticas propias en las coordenadas de cada condición; no reutilizar directamente el Hessiano identidad en Hadamard. Guardar la implementación exacta de estas decisiones: es una variante explícitamente fijada de GPTQ, no una afirmación de que todos sus programas usan esta configuración.

**Calibración GPTQ:** 128 ventanas de 2048 tokens por réplica. Seleccionar sin reemplazo 128 documentos de entrenamiento con al menos 2047 tokens, uniformemente entre documentos elegibles; de cada uno elegir uniformemente un inicio válido para 2047 tokens y añadir BOS. Semillas PCG64 101, 202 y 303. Guardar IDs de documentos, posiciones y tokens. Usar las mismas ventanas en ambas ramas y en todos los bits. Las semillas de calibración y rotación se cruzan, no se emparejan únicamente por índice. RTN no usa ninguna de estas ventanas.

## 6. Matriz experimental y alcance mínimo

Para cada modelo:

| Método | Transformación | Bits | Réplicas por bit |
|---|---|---|---|
| RTN | Identidad | 4, 3, 2 | 1 determinista |
| RTN | Hadamard residual | 4, 3, 2 | 3 rotaciones |
| GPTQ | Identidad | 4, 3, 2 | 3 calibraciones |
| GPTQ | Hadamard residual | 4, 3, 2 | 3 rotaciones × 3 calibraciones |

Total: **48 configuraciones cuantizadas por modelo**, más original, identidad plegada y tres controles Hadamard no cuantizados. La configuración identidad se reutiliza como referente; no se cuentan sus reutilizaciones como réplicas independientes.

**Mínimo viable exploratorio:** modelo principal, rotación 11 y calibración 101: 12 configuraciones cuantizadas más tres controles no cuantizados. Permite estimar efectos condicionados a esas semillas, pero no sustenta afirmaciones sobre estabilidad entre semillas. Priorizar después completar la matriz de 48 antes de ampliar modelos. BoolQ y Llama-2-7B son extensiones; un control ortogonal alternativo emparejado queda opcional para distinguir estructura Hadamard de rotación ortogonal en general.

## 7. Métricas y criterios operativos

**Primaria:** pérdida media por token en prueba. Secundaria derivada: perplejidad. Guardar sumas de pérdida y número de tokens por documento. Si exp(pérdida) desborda, conservar la pérdida finita y no confundir desbordamiento de presentación con fallo del modelo.

Para cada método, bit y pareja de semillas, definir `Δ = NLL_H − NLL_I`; valores negativos favorecen Hadamard. Reportar también NLL de cada condición frente a su correspondiente control no cuantizado, y la diferencia de degradaciones, para separar efectos residuales de aritmética BF16.

**Umbrales propuestos, fijados antes de evaluar:**
- Mejora de calidad material: Δ ≤ −0,02 nats/token, con intervalo del 95 % enteramente por debajo de cero.
- Perjuicio material: Δ ≥ +0,02 y un intervalo enteramente por encima de cero.
- Equivalencia práctica: intervalo completo dentro de [−0,02, +0,02]. Lo demás es pequeño, heterogéneo o inconcluso; no equivale automáticamente a «sin efecto».
- Degradación extrema de una condición: incremento de NLL ≥ ln(2) frente a su control no cuantizado, es decir, al menos duplicación de perplejidad. Es una definición operativa, no prueba de inutilidad universal.
- BoolQ: diferencia material propuesta de 1 punto porcentual; se informa como resultado secundario, sin reemplazar la métrica primaria si discrepan.

**Estabilidad:** distinguir (a) logits/pérdidas no finitos, escalas inválidas o factorización GPTQ fallida; (b) degradación extrema con cómputo válido; (c) variación de calidad entre rotaciones y calibraciones. Etiqueta provisional «estable en las réplicas estudiadas»: ninguna réplica con fallo numérico ni degradación extrema y rango de NLL entre réplicas ≤ 0,05 nats/token. Mostrar los valores continuos y sensibilidad a umbrales de rango 0,02 y 0,10; no tratar esta etiqueta como garantía universal.

OOM, descargas fallidas, procesos interrumpidos y archivos corruptos son **fallos de infraestructura**, separados de los anteriores. Pueden reintentarse con el mismo artefacto y configuración; registrar cambios de hardware. No imputarles mala calidad ni eliminarlos del inventario de ejecuciones.

## 8. Análisis de incertidumbre

1. Presentar todos los contrastes por modelo, método y bits; no ocultar un perjuicio a 2 bits detrás de una media a 4 bits.
2. Bootstrap pareado de documentos, 2000 remuestreos, semilla 9001: remuestrear los mismos documentos en ambas condiciones y recalcular cocientes de sumas para NLL por token. No usar tokens como observaciones independientes.
3. Presentar además cada resultado por semilla. Para GPTQ-Hadamard, remuestrear rotaciones y calibraciones como dos factores cruzados y conservar el emparejamiento con la referencia de la misma calibración; RTN solo tiene factor rotación. Informar por separado incertidumbre documental condicionada a semillas y dispersión entre semillas. Con tres niveles, la inferencia poblacional sobre semillas será débil; un intervalo conjunto cruzado se etiquetará exploratorio.
4. Examinar interacción Hadamard×método y Hadamard×bits mediante diferencias de contrastes, preservando los emparejamientos. Para seis contrastes primarios por modelo, acompañar los intervalos marginales del 95 % con intervalos conservadores del 99,17 % para decisiones simultáneas. No suponer independencia entre bits.
5. Reportar fracciones descriptivas de fallos y degradación extrema, y curvas por semilla. No aplicar un binomial ingenuo a nueve celdas que comparten rotaciones y calibraciones. Los fallos numéricos se muestran como tales; un análisis solo de ejecuciones válidas será explícitamente condicional y no podrá respaldar una mejora global por sí solo.

## 9. Diagnósticos del mecanismo

Medir, antes de cuantizar, máximo/RMS y colas de pesos por grupo y capa, identificando que son estadísticas dependientes de coordenadas. Para comparar error funcional, transportar cada matriz cuantizada de la rama rotada a la base original: por ejemplo, si `W' = QᵀW`, usar `Q W'_quant`; si `W' = WQ`, usar `W'_quant Qᵀ`. Comparar contra los pesos exactos plegados, no contra otra parametrización.

En los fragmentos de validación, medir error relativo de salidas lineales sobre entradas comunes en coordenadas originales, error de estados residuales tras desrotarlos, y KL/logits frente al control correspondiente. Separar errores locales con entradas de referencia de errores acumulados en el modelo cuantizado. Guardar resultados por capa y no solo promedios.

Una menor concentración de pesos o menor error de reconstrucción no prueba mejor calidad; contrastar su asociación con NLL como análisis explicativo, sin afirmaciones causales adicionales ni selección retrospectiva de capas.

## 10. Viabilidad y reglas de conclusión

No se requiere ejecutar nada en el entorno actual, que no dispone de GPU, datasets ni red. Para una ejecución futura, el modelo de 1,1B ocupa aproximadamente 2,2 GB en BF16 solo en pesos; esto excluye activaciones, copias FP32 y Hessianos. Un Hessiano FP32 de dimensión 5632 ronda 127 MB. Procesamiento por capa y offload permitirían plantear el piloto en una GPU de 24 GB con 32–64 GB de RAM, pero no garantizarlo sin perfilar memoria. Para 7B, considerar una GPU de 48–80 GB o estrategias de offload y 64–128 GB de RAM. No almacenar todas las copias densas: guardar códigos/escalas/manifiestos y reconstruir cada condición por turnos.

Presupuestar prudentemente decenas a centenares de GPU-horas para la matriz principal completa y su evaluación, con incertidumbre amplia según kernels y hardware; no es una medición. Tras un futuro piloto de una capa y una condición, estimar por separado transformación, GPTQ y tokens de evaluación y ajustar el alcance, no los umbrales según resultados. Ejecutar el mínimo viable primero y ampliar solo si supera la puerta de validez.

La simulación mediante pesos dequantizados estudia calidad, **no demuestra aceleración, memoria real de despliegue ni eficiencia de kernels de 2–4 bits**. Informar tamaño teórico de códigos, escalas y pesos excluidos por separado del uso medido de memoria.

Concluir mejora solo para los modelos, bits y métodos donde los contrastes la respalden. «Estabilización» requiere menor incidencia de fallos/degradación extrema o menor variación relevante, no solo una media mejor. Si ambas ramas son estables, puede haber mejora de calidad sin rescate alguno. Si los intervalos apoyan equivalencia práctica, concluir ausencia de efecto relevante en ese alcance; si son amplios, concluir incertidumbre. Si empeora, reportar perjuicio. En ningún caso extrapolar este subconjunto residual al QuaRot completo ni asumir de antemano fracaso de RTN/GPTQ.
````

**Stage**

````text
result
````

**Evidence**

````text
La exploración previa encontró únicamente /workspace/task.json, confirmado por listado de archivos; no hay implementación ni textos completos de las fuentes que permitan verificar sus configuraciones. El archivo declara una tarea solo de diseño. Los requisitos sobre pesos, bits y diferencias RTN/GPTQ proceden de las confirmaciones del investigador, quien aprobó explícitamente el enfoque factorial. No se ejecutaron experimentos ni se obtuvieron resultados. La compensación propuesta se fundamenta en ortogonalidad, equivariancia de RMSNorm sin ganancia y preservación explícita de las entradas de no linealidades; la prueba de equivalencia es una condición de validez, no un resultado supuesto. Las cuentas de configuraciones se derivan de 3 bits × (1+3+3+9), y las estimaciones de memoria son cálculos nominales de almacenamiento, no perfiles del entorno.
````

**Assumptions**

````text
[
  "Los checkpoints futuros mantienen la arquitectura RMSNorm y las proyecciones esperadas; se verificará antes de ejecutar.",
  "Se dispondrá de acceso autorizado a los modelos y datasets y de hardware externo adecuado; el acceso a Llama-2 es opcional.",
  "El subconjunto Hadamard residual aprobado como decisión metodológica es suficiente para responder una pregunta limitada sobre esa transformación, no para reproducir todas las rotaciones de QuaRot.",
  "Los manifiestos de revisiones y hashes se completarán y bloquearán antes de ejecutar; no hay revisiones descargadas actualmente.",
  "Las tolerancias y umbrales son decisiones operativas propuestas, sujetas únicamente a enmiendas documentadas antes de observar resultados cuantizados."
]
````

**Uncertainties**

````text
[
  "La utilidad a 2 bits depende del formato simétrico, agrupamiento, escalas y exclusiones elegidos; un resultado no cubrirá todos los cuantizadores posibles.",
  "La equivalencia numérica BF16 y FP32 debe verificarse: no se presupone que todos los kernels cumplan las tolerancias.",
  "Tres semillas por factor ofrecen cobertura limitada; los resultados de estabilidad no describirán probabilidades universales de fallo.",
  "WikiText y un modelo pequeño limitan la generalización a otros dominios, arquitecturas y escalas; la contaminación de preentrenamiento no queda descartada.",
  "El presupuesto futuro de tiempo y memoria depende de la implementación y hardware; las cifras son orientativas y necesitan perfilado antes de comprometer la matriz completa."
]
````

### Event 5 — Simulator

**Message**

````text
El diseño final satisface el alcance acordado: incluye justificación, controles, parámetros reproducibles, análisis de calidad y estabilidad y viabilidad, sin afirmar ejecución ni resultados. Se mantiene explícitamente la limitación al Hadamard residual; las conclusiones no deberán extenderse al paquete completo de QuaRot. No solicito revisiones adicionales.
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
La entrega presenta contrastes pareados RTN/GPTQ con y sin Hadamard a 4, 3 y 2 bits, cuantización solo de pesos, compensaciones algebraicas y puertas de equivalencia, separación de calibración y rotación, criterios de interpretación y tratamiento de fallos. Incluye una matriz de 48 configuraciones por modelo y un piloto de 12, con recursos estimados y límites de generalización. Los detalles no respaldados por fuentes se identifican como decisiones propuestas; las comprobaciones numéricas quedan como requisitos futuros, apropiadamente para una tarea solo de diseño.
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
  "event_log": "runs/openai-astra-top10-trial-1-batch-1/episodes/expbench_neurips2024_94328_4-72cdd1baa00a/candidate_046/attempt-1/output/neurips2024__94328__4/events.jsonl",
  "event_log_sha256": "cc9c0402e7896d6a1fce892e46664e89c3d063cb143b7952e4f878f9e03d110e",
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
