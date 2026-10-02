# candidate_046 · expbench · iclr2024/19281/1

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
Por favor, revise únicamente los insumos disponibles y proponga un enfoque experimental; todavía no desarrolle el diseño final ni ejecute experimentos. El documento track.md indica que esta tarea es solo de diseño: no requiere repositorio ni cómputo. Resuma qué está respaldado por el contexto y qué habría que asumir. En su propuesta, explique cómo aislaría el efecto de incorporar retroalimentación química frente a no incorporarla, y cómo distinguiría mejoras de propiedades de una mera explotación de las métricas. Indique controles previstos, medidas de alineación con distribuciones reales, diversidad estructural y exceso de cadenas de carbono largas, así como una definición operativa de «alucinaciones moleculares». Señale las incertidumbres importantes, especialmente el significado de p-logP, la fuente y límites de la afinidad de unión, los datos de referencia, el generador y los recursos necesarios. Presente estas elecciones como propuestas, no como detalles confirmados del estudio.
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
El contexto proporciona una pregunta científica y exige un diseño con justificación, controles, análisis y viabilidad; no aporta datos, resultados ni una configuración experimental confirmada. La inspección inicial debe limitarse a los insumos, el enfoque propuesto y las incertidumbres.
````

**Objectives Open**

````text
[
  "Revisar los insumos y separar hechos proporcionados de supuestos.",
  "Acordar un enfoque causal y controles para evaluar la retroalimentación química.",
  "Precisar métricas de propiedades, realismo, diversidad y alucinaciones, y las incertidumbres de viabilidad."
]
````

### Event 2 — Actor

**Answer**

````text
## Alcance y respaldo disponible
Revisé únicamente los insumos. `task.json` contiene la pregunta y, como documento incorporado, `track.md`: «Design-only task; repositories and compute are not required». No hay código, datos ni especificaciones del modelo en los archivos visibles. La pregunta plantea evaluar retroalimentación mediante p-logP, QED y afinidad, junto con distribución, diversidad y cadenas de carbono largas; no establece que haya una mejora. No ejecuté experimentos: solo lectura y comprobación de los insumos.

## Enfoque propuesto, pendiente de aprobación
**1. Aislar el efecto de la retroalimentación.** Propondría comparar un generador sin retroalimentación química con el mismo generador que sí la incorpora. Mantendría iguales el checkpoint inicial, datos, objetivos moleculares, restricciones, procedimiento de muestreo y presupuesto de generación; usaría varias semillas y tareas o dianas emparejadas. Si el mecanismo actualiza el modelo, el control debería tener pasos de actualización equivalentes sin señal química informativa. Registraría por separado coste y número de consultas al evaluador. El análisis principal incluiría todas las propuestas anteriores al filtrado, no solo los mejores candidatos.

Como controles adicionales propondría: selección a posteriori con los mismos evaluadores y presupuesto, para distinguir aprendizaje de mera selección; retroalimentación permutada entre moléculas, para comprobar el valor de la señal específica; y ablaciones por propiedad, para detectar si una señal domina a las demás. La implementación exacta dependería de si el bucle opera durante entrenamiento, generación o selección. No daría por supuesto que estos mecanismos son equivalentes.

**2. Separar mejora química de explotación de métricas.** Congelaría las funciones usadas por el bucle y reservaría evaluadores y datos independientes para la evaluación final. Reportaría p-logP, QED y afinidad por separado, sus distribuciones y compromisos, además de cualquier agregado. Compararía las ganancias en las métricas optimizadas con plausibilidad química, cobertura del dominio de referencia y desempeño de validadores no empleados como recompensa. Prevería revisión química ciega de muestras aleatorias y de extremos de puntuación, con criterios establecidos previamente. Un aumento del score acompañado de artefactos, pérdida de cobertura o deterioro en validación independiente no contaría como evidencia suficiente de mejora real. No equipararía automáticamente mayor lipofilia con mejor molécula.

**3. Medir alineación y diversidad.** Propondría dos referencias independientes del entrenamiento: una colección curada de moléculas reales del dominio y, si existe, otra relevante para cada diana. La comparación principal sería entre brazos sometidos al mismo objetivo; describiría también el desplazamiento intencional respecto de la distribución general. Compararía distribuciones de propiedades fisicoquímicas y topológicas, frecuencias de scaffolds y distancias entre representaciones moleculares; como opciones, distancia de Wasserstein para descriptores y MMD o vecinos cercanos para fingerprints. Incluiría diversidad interna por Tanimoto, riqueza y entropía de scaffolds, unicidad, cobertura y novedad frente al entrenamiento. Usaría tamaños de muestra equiparados y examinaría memorización, porque parecerse a moléculas reales no debe reducirse a copiarlas.

Para cadenas largas, propondría medir la longitud de la cadena acíclica contigua de carbonos no aromáticos y la fracción de carbonos que contiene. La definición final distinguiría cadena de componente ramificado. Fijaría el umbral de «ultralarga» a partir de la cola de la referencia antes de evaluar resultados, y reportaría tanto la distribución completa como la frecuencia y el exceso respecto de la referencia. Haría análisis estratificados por tamaño molecular y dominio para no etiquetar lípidos legítimos como artefactos.

**4. Definir operativamente «alucinaciones moleculares».** No usaría el término como sinónimo de novedad, baja afinidad o rareza. Propondría separar: (a) representaciones que no se pueden convertir en un grafo molecular válido o violan reglas de valencia bajo una convención explícita; (b) grafos formalmente válidos con motivos considerados químicamente inverosímiles para el dominio por reglas predefinidas y revisión independiente; y (c) candidatos con scores favorables pero evidencia de artefacto del evaluador, por ejemplo poses inválidas o explotación de su dominio de aplicabilidad. Reportaría estas categorías por separado, con casos inciertos, y la tasa sobre todas las propuestas, evitando ocultar fallos mediante filtrado. Los indicadores de accesibilidad sintética o de fuera de distribución serían señales auxiliares, no pruebas automáticas de imposibilidad.

**5. Criterio orientativo de éxito y controles de análisis.** Propondría exigir mejora en propiedades validada independientemente y reducción de fallos químicos, sin deterioro relevante de diversidad, alineación pertinente ni exceso de cadenas largas. Los márgenes, objetivos de propiedades y medidas primarias se fijarían antes de la evaluación; no los elegiría viendo los resultados. La incertidumbre se estimaría entre ejecuciones y dianas, no tratando cada molécula correlacionada como réplica experimental independiente. Incluiría controles de estandarización molecular, duplicados, separación entrenamiento/evaluación, presupuesto y selección de candidatos.

## Qué requiere aclaración antes del diseño final
1. **p-logP:** ¿significa logP penalizado u otra cantidad? Hacen falta fórmula, componentes, normalización, dirección deseada y tratamiento de tamaños o anillos. No propondría una recompensa concreta sin esta definición.
2. **Afinidad:** ¿qué dianas y qué fuente se contemplan: ensayos, docking o predictor? Deben precisarse unidades, signo, protocolo y dominio de aplicabilidad. Un score de docking o predicción no demuestra afinidad experimental; otro evaluador computacional solo aportaría corroboración limitada.
3. **Referencias:** ¿qué colecciones reales, particiones y moléculas activas están disponibles, con qué sesgos y restricciones de acceso? «Distribución real» requiere un dominio definido; aproximarse a una colección general puede entrar en tensión con optimizar una diana.
4. **Generador y mecanismo:** ¿qué arquitectura, representación molecular, checkpoint, datos de entrenamiento y forma de incorporar la señal están previstos? Esto determina el control causal y la posibilidad de descartar memorización.
5. **Recursos de una implementación futura:** dependerían del generador, número de semillas y dianas y coste del evaluador. La tarea actual no requiere cómputo. El entorno informado carece de datos, GPU, red y dependencias de proyecto; no fijaría tamaños de corrida ni prometería docking, entrenamiento o validación experimental en él.

Estas son elecciones propuestas, no detalles confirmados del estudio. Espero aprobación o aclaraciones antes de desarrollar el diseño final.
````

**Stage**

````text
plan
````

**Evidence**

````text
Observaciones concretas: la lista de `/workspace` mostró solo `task.json`. Su lectura confirmó los campos `question`, `context` y `documents`; `track.md` está incorporado en `documents`, no como archivo separado visible. Una comprobación local con la biblioteca estándar de Python confirmó esa estructura y reprodujo literalmente: «Design-only task; repositories and compute are not required». No se encontraron código, datasets, definiciones de scores, generador ni resultados. La exploración se limitó a inspección de archivos; no constituye ejecución experimental. Los controles propuestos permiten distinguir señal química, selección posterior y explotación del evaluador, mientras que evaluaciones independientes y referencias por dominio evitan identificar una recompensa alta con calidad química demostrada.
````

**Assumptions**

````text
[
  "Para una implementación futura sería posible disponer de un generador reproducible y controlar su checkpoint, muestreo y acceso a señales químicas; esto no está confirmado.",
  "Podrían obtenerse referencias curadas y suficientemente independientes del entrenamiento; su existencia y acceso no están establecidos.",
  "La plausibilidad química y los umbrales de colas podrían definirse con criterios de dominio y revisión independiente antes de evaluar resultados.",
  "La validación experimental de afinidad sería evidencia más fuerte, pero no se presupone disponible ni necesaria para entregar este diseño."
]
````

**Uncertainties**

````text
[
  "Definición y dirección de p-logP y composición exacta de la retroalimentación.",
  "Dianas, procedencia, fiabilidad y límites de la medida de afinidad.",
  "Dominio de referencia real, disponibilidad de datos y posible contaminación respecto del entrenamiento.",
  "Generador y etapa en la que se incorpora la retroalimentación.",
  "Umbrales de plausibilidad, cadenas ultralargas y márgenes aceptables de diversidad y alineación.",
  "Recursos de una eventual ejecución y disponibilidad de evaluación química independiente."
]
````

### Event 3 — Simulator

**Message**

````text
Apruebo el enfoque. Desarrolle ahora el diseño experimental final, con justificación, controles, plan de análisis y viabilidad, sin ejecutar experimentos ni presentar resultados supuestos. Mantenga la comparación emparejada, la evaluación de propuestas antes del filtrado y los controles de selección posterior y señal permutada; distinga controles esenciales de ablaciones opcionales para que el diseño sea viable. No hay más detalles de fuente disponibles: convierta las incertidumbres en elecciones explícitas del protocolo propuesto, no en hechos confirmados ni en requisitos de aclaración que impidan terminar. Elija una implementación concreta del bucle y especifique recompensa, normalización, momento de actualización y presupuestos comparables. Puede adoptar p-logP como logP penalizado bajo una fórmula declarada, señalando que esa interpretación no está confirmada. Proponga criterios para seleccionar dianas y referencias, particiones sin fuga y evaluación independiente de afinidad; mantenga clara la diferencia entre evidencia computacional y afinidad experimental. Defina medidas primarias, denominadores para fallos y duplicados, regla reproducible para cadenas largas, y cómo separar alineación pertinente de memorización o desplazamiento intencional por optimización. Incluya un número orientativo de semillas, dianas y propuestas como planificación, con ajuste mediante precisión o potencia, unidades de réplica, intervalos de incertidumbre y manejo de comparaciones múltiples. Para responder a la pregunta completa, distinga mejora de alineación de mera ausencia de deterioro; establezca una regla conjunta de decisión para propiedades, alucinaciones, alineación y preservación de diversidad, admitiendo resultados mixtos o inconclusos. Los márgenes pueden ser propuestas justificadas o reglas para fijarlos con datos de desarrollo antes de abrir la evaluación final. Cierre con recursos necesarios, límites y una alternativa mínima viable; no hace falta disponer de esos recursos en el entorno actual.
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
El informe propone aislar la retroalimentación mediante brazos emparejados, controlar selección y explotación de métricas, evaluar diversidad y referencias por dominio, y separar categorías de fallos químicos. Reconoce correctamente que no hay datos, modelo ni definición de p-logP confirmados y no afirma ejecución experimental. El enfoque permite elaborar el entregable de diseño con supuestos explícitos.
````

**Objectives Open**

````text
[
  "Entregar un protocolo experimental concreto y reproducible con supuestos identificados.",
  "Especificar controles, métricas y regla de decisión que respondan conjuntamente a propiedades, alucinaciones, alineación y diversidad.",
  "Completar análisis estadístico, viabilidad y límites sin afirmar resultados ejecutados."
]
````

### Event 4 — Actor

**Answer**

````text
# Diseño experimental propuesto

## 1. Alcance y pregunta estimable
El estudio contrastaría si **actualizar un generador con retroalimentación química**, frente al mismo generador sin esa actualización, mejora propiedades verificadas independientemente, reduce fallos moleculares y acerca las moléculas a una referencia real pertinente, preservando diversidad.

Todo lo que sigue es una elección de protocolo propuesta, no una descripción de un estudio existente. No se han ejecutado experimentos. La evidencia inicialmente alcanzable sería **computacional**: ni docking ni un predictor independiente demostrarían afinidad experimental, sintetizabilidad o utilidad terapéutica.

La comparación principal estimaría el efecto de la señal química bajo igual número de propuestas y consultas disponibles. Una comparación adicional distinguiría ese efecto del beneficio de simplemente puntuar y seleccionar moléculas.

## 2. Dianas, datos y particiones

### Selección propuesta
Seleccionar tres dianas de familias diferentes mediante criterios fijados antes de entrenar: estructura de calidad con ligando cocristalizado, sitio de unión definido, suficientes ligandos con mediciones comparables y suficientes inactivos medidos para validar un evaluador independiente. Excluir dianas que requieran protocolos especiales no disponibles, como unión covalente. Publicar todos los candidatos y motivos de exclusión para evitar escoger retrospectivamente las dianas más favorables.

Usar dos referencias:
- **Referencia general:** moléculas experimentales curadas del dominio de pequeñas moléculas tipo fármaco. Describe plausibilidad y cobertura general, no una distribución universal de «toda la química real».
- **Referencia pertinente por diana:** ligandos medidos para la diana; identificar por separado los activos mediante un umbral de actividad definido en desarrollo. Esta sería la referencia principal de alineación dirigida.

Una fuente posible sería una versión congelada de ChEMBL, más estructuras de PDB. Versiones, licencias, identificadores y reglas de inclusión quedarían registradas. No se presupone que los datos estén disponibles en el entorno actual.

### Prevención de fuga
Estandarizar estructuras antes de particionar: componente orgánico principal, convenciones explícitas de carga, tautomería y estereoquímica, y eliminación documentada de registros incompatibles. Identificar duplicados por conectividad normalizada y conservar una evaluación secundaria sensible a estereoquímica.

Crear particiones separadas de entrenamiento, desarrollo y prueba mediante **agrupaciones de scaffolds Bemis–Murcko**, reforzadas con agrupaciones por similitud para reducir análogos casi idénticos entre particiones. Cuando las fechas lo permitan, añadir separación temporal. Fijar el algoritmo y umbral de agrupación en desarrollo. No mezclar indiscriminadamente Ki, Kd e IC50; elegir un tipo de medida o analizarlos en estratos.

El generador no vería ninguna referencia final de prueba. El predictor de afinidad independiente tampoco se entrenaría con ella. Las moléculas usadas para validar finalmente ese predictor serían distintas de sus datos de entrenamiento y desarrollo. Cualquier checkpoint con procedencia desconocida impediría afirmar ausencia de memorización: preferiría entrenar o reajustar un modelo con inventario de datos auditable.

## 3. Implementación concreta de la retroalimentación

### Generador
Propondría un Transformer autorregresivo pequeño que genere SMILES, entrenado por máxima verosimilitud y luego congelado como política inicial \(\pi_0\). Para cada diana, iniciar todas las condiciones desde exactamente el mismo checkpoint. Mantener tokenizador, temperatura, longitud máxima, restricciones de vocabulario y tratamiento de secuencias truncadas idénticos. No imponer un límite especial a cadenas de carbono: eso eliminaría artificialmente un fenómeno que se quiere medir.

### Definición de p-logP
Adoptaría provisionalmente **logP penalizado**:

\[
p\text{-logP}(m)=\mathrm{CrippenLogP}(m)-\mathrm{SA}(m)-\max(0,L_{\mathrm{anillo}}(m)-6).
\]

SA sería una implementación versionada del score de accesibilidad sintética de Ertl–Schuffenhauer, donde valores altos indican mayor dificultad. \(L_{\mathrm{anillo}}\) sería el tamaño máximo entre los anillos obtenidos por el algoritmo SymmSSSR fijado; sería cero si no hay anillos. Esta fórmula y la elección del algoritmo son convenciones propuestas, **no una interpretación confirmada del término de la pregunta**. Mejorar este score no implica mejorar lipofilia terapéutica ni facilidad real de síntesis.

### Recompensa
Calcular tres componentes: p-logP, QED y \(-E_{dock}\), donde \(E_{dock}\) es el score de docking y menor energía estimada se considera favorable. Elegir para la recompensa un motor y protocolo fijo, por ejemplo AutoDock Vina, con preparación de proteína, protonación, generación de conformeros, caja y semillas congeladas.

Transformar cada componente mediante su función de distribución empírica estimada **solo con datos de desarrollo**. Esto produce percentiles entre 0 y 1, evita que una escala numérica domine y satura extremos. Los transformadores no se recalcularían durante el bucle. La recompensa válida sería:

\[
R(m)=\tfrac13\{F_p(p\text{-logP}(m))+F_Q(QED(m))+F_A(-E_{dock}(m))\}.
\]

SMILES inválidos recibirían −1. Un fallo de docking en una estructura válida daría componente de afinidad cero, sin reintentos selectivos ilimitados; conservaría sus otros componentes. Se distinguirían fallos químicos de problemas de infraestructura. Los últimos se reintentarían según una regla común preestablecida.

### Actualización
Utilizar REINFORCE con baseline por lote y una penalización KL respecto de \(\pi_0\): maximizar la recompensa esperada menos \(\beta D_{KL}(\pi\Vert\pi_0)\). Tras cada lote de 128 propuestas, puntuar todas y efectuar una actualización; no seleccionar únicamente las mejores para aprender. Fijar tasa de aprendizaje, \(\beta\), clipping y número de pasos con datos de desarrollo, sin consultar prueba. La regularización limita desplazamientos arbitrarios, pero no se consideraría garantía de diversidad.

## 4. Condiciones y presupuestos

### Controles esenciales
1. **Bucle químico:** actualizaciones con la recompensa descrita.
2. **Sin bucle:** misma política inicial, mantenida congelada. Genera los mismos tamaños de lote; las puntuaciones se calculan, pero quedan ocultas al generador.
3. **Señal permutada:** mismo algoritmo de actualización que el bucle, pero se permutan aleatoriamente las recompensas entre moléculas válidas del lote. Las inválidas conservan la penalización común. Así se controla el valor de la asignación química específica, manteniendo una señal básica de validez y la distribución marginal de recompensas. No es un control de ausencia total de aprendizaje.
4. **Selección posterior:** sobre el conjunto final del control sin bucle, seleccionar el 10 % con mayor recompensa. No requiere un cuarto entrenamiento. Comparar ese subconjunto con el 10 % del bucle seleccionado por exactamente la misma regla, usando evaluadores independientes. Es un control dependiente del conjunto sin bucle y se analizaría como tal, no como réplica adicional.

La comparación causal principal sería bucle frente a sin bucle. La comparación con señal permutada comprobaría la contribución específica de la química. La comparación seleccionada determinaría si el bucle aporta valor práctico más allá de reranking.

### Planificación inicial
Propondría **3 dianas × 5 semillas × 3 condiciones generativas**. Por ejecución: 10 lotes de adaptación de 128 propuestas y, después de congelar la política, 2.000 propuestas finales sin actualización. Total orientativo: 147.600 propuestas, de las cuales 90.000 corresponden a evaluación final. Son cifras de planificación, no un cálculo de potencia ni una promesa de ejecución.

Emparejar semillas, checkpoint y diana entre condiciones. Usar igual número de posiciones de muestreo y presupuesto máximo de consultas de recompensa; contar inválidos como intentos consumidos. Una caché por diana evitaría repetir cálculos deterministas de moléculas idénticas sin conceder propuestas adicionales. Fijar también un límite de cómputo por consulta. El control congelado no tiene que gastar artificialmente el tiempo ahorrado por no actualizarse: reportar horas, memoria y consultas efectivas por separado.

Evaluar todas las propuestas finales **antes del filtrado**. Conservar también toda la trayectoria de adaptación como diagnóstico de aparición de artefactos. No sustituir fallos por nuevos intentos ni detener condiciones al alcanzar cierto número de moléculas buenas.

### Ablaciones opcionales
Si hay recursos: eliminar por turno p-logP, QED o afinidad; variar pesos; quitar la regularización KL; comparar una recompensa con objetivo de lipofilia acotado. Estas ablaciones ayudan a atribuir mecanismos, pero no son necesarias para el contraste principal y no deben multiplicar el coste del protocolo mínimo.

## 5. Evaluación independiente y defensa frente a explotación de métricas

### Afinidad
La recompensa usaría docking. La evaluación independiente principal usaría un predictor entrenado exclusivamente con mediciones experimentales curadas de la diana, con particiones por scaffold y calibración en desarrollo. Se informaría su error, calibración, discriminación y dominio de aplicabilidad en prueba antes de interpretar moléculas generadas. En ausencia de desempeño suficiente preestablecido, el componente de afinidad quedaría **inconcluso**, no validado por el propio docking.

Una molécula fuera del dominio no recibiría una etiqueta segura de alta afinidad. Se reportaría como no respaldada y no contaría como éxito validado. El score del predictor continuaría siendo una predicción computacional basada en datos experimentales, no una medición de esa nueva molécula.

Como corroboración secundaria, evaluar una muestra ciega mediante otro motor o función de scoring y comprobaciones de geometría, choques y plausibilidad de pose. Esa muestra combinaría selección aleatoria estratificada por condición y diana con una muestra separada de extremos de recompensa. Las estimaciones poblacionales usarían solo la muestra probabilística o pesos de inclusión conocidos; los extremos servirían para buscar artefactos. Compartir sesgos entre métodos seguiría siendo posible.

Una extensión experimental, fuera del núcleo computacional, sintetizaría una selección emparejada y ciega de candidatos para medir unión y controles de agregación/interferencia. Solo esta extensión podría demostrar afinidad medida para los candidatos.

### Propiedades y éxito por intento
Reportar componentes originales, percentiles y distribución completa, no solo la recompensa agregada. Definir en desarrollo ventanas aceptables de p-logP y QED, y un umbral de actividad sustentado por datos de la diana. Para p-logP, una ventana evita equiparar maximización ilimitada con mejora química.

La medida primaria de calidad sería el **rendimiento de moléculas distintas respaldadas por intento**: número de estructuras distintas que cumplen ventanas de propiedades, predicción de afinidad con incertidumbre aceptable dentro del dominio y ausencia de fallos químicos definidos abajo, dividido por las 2.000 propuestas finales. Moléculas copiadas exactamente del entrenamiento no contarían como éxitos nuevos; se reportaría también el rendimiento sin exigir novedad.

Para evitar que una tasa compuesta oculte compensaciones, se analizarían además p-logP y QED por separado, proporción con afinidad independiente respaldada y puntuaciones de afinidad entre candidatos evaluables. Estas últimas son análisis condicionales, siempre acompañados de su tasa de cobertura. Ganancias solo en la recompensa, pero no en validación independiente, se interpretarían como posible explotación del evaluador.

## 6. Definición de «alucinaciones moleculares» y denominadores

El término se operacionalizaría sin identificar rareza o novedad con imposibilidad:
- **H1, fallo representacional:** secuencia truncada o no parseable, o grafo que no supera sanitización/valencia bajo las convenciones fijadas.
- **H2, implausibilidad química:** grafo formalmente válido con un motivo que un catálogo predefinido y revisión química independiente consideran incompatible con el dominio o con estabilidad razonable. Alertas de reactividad, SA alto o rareza, por sí solos, no bastan. Conservar una categoría «incierto».
- **H3, artefacto del evaluador:** alta recompensa sustentada por una pose geométricamente inválida, una preparación errónea o un fallo reproducible del evaluador. Desacuerdo entre predictores o estar fuera de distribución no bastan para declarar H3.

La tasa primaria de alucinaciones sería la unión H1∪H2∪H3 por **todas las propuestas finales**, sin contar dos veces categorías solapadas. H1 y reglas automáticas se evaluarían exhaustivamente; la parte que requiere revisión se estimaría mediante muestreo aleatorio estratificado y pesos conocidos. Dos revisores ciegos, adjudicación y acuerdo entre evaluadores apoyarían H2/H3. Reportar análisis de sensibilidad considerando inciertos como fallo y como no fallo, además de las categorías separadas.

Para duplicados, si N es el número total de intentos, V el número de intentos válidos y U el número de estructuras válidas distintas: reportar V/N, U/N y **(V−U)/V**. En las tasas por intento, cada repetición cuenta; en diversidad estructural se usan estructuras únicas y se reporta explícitamente ese cambio de denominador. Los fallos de evaluación técnica se separarían de H1–H3 y no se borrarían del balance de intentos.

## 7. Alineación, diversidad y cadenas largas

### Alineación pertinente
La medida primaria sería MMD entre fingerprints Morgan de radio 2, con kernel de Tanimoto, de propuestas válidas y la referencia activa de prueba por diana. Fijar longitud del fingerprint, estereoquímica y procedimiento de submuestreo en desarrollo. Utilizar tamaños equiparados y preservar multiplicidades en la comparación principal de distribuciones; repetir con estructuras únicas como sensibilidad. Menor distancia indica mayor alineación en esa representación, no equivalencia química completa.

Medidas secundarias: distancias de Wasserstein para masa, logP, TPSA, carga, número de anillos, enlaces rotables y fracción sp3; frecuencias y cobertura de scaffolds; distancias a vecinos de la referencia. Comparar también con la referencia general, pero sin exigir que una optimización dirigida reproduzca su distribución marginal.

Separar tres fenómenos:
1. **Alineación mejorada:** reducción demostrable de distancia hacia la referencia de la diana.
2. **Desplazamiento intencional:** variación de propiedades objetivo esperada al favorecer actividad. Describirla mediante análisis estratificados en bins de tamaño y propiedades definidos en desarrollo; no permitir que este análisis secundario sustituya el contraste primario si faltan estratos comparables.
3. **Memorización:** coincidencias exactas con entrenamiento, similitud máxima a él y concentración en sus scaffolds. Repetir las comparaciones excluyendo copias. Si la alineación mejora solo por copia o por muy pocos scaffolds, no considerarla un éxito completo.

La MMD entre estructuras válidas es condicional: debe interpretarse junto con la tasa de validez y el rendimiento por intento, no como si describiera las propuestas inválidas.

### Diversidad
Medida primaria: diversidad interna media 1−Tanimoto entre moléculas únicas, mediante muestras de tamaño fijo. Añadir número efectivo de scaffolds, exp(entropía de Shannon), riqueza mediante rarefacción, unicidad y cobertura de referencia. Estas medidas complementarias evitan que una media de distancias o la sola novedad oculten colapso estructural.

### Regla reproducible para cadenas de carbono largas
Construir el subgrafo inducido por carbonos **no aromáticos y no pertenecientes a anillos**, conservando enlaces C–C de cualquier orden. Al ser un bosque, obtener la longitud máxima del camino simple, en número de átomos, como diámetro máximo más uno; cero si el subgrafo está vacío. Esto distingue la cadena más larga del tamaño total de un componente ramificado. Registrar además esa longitud dividida por el número de carbonos de la molécula.

Definir «ultralarga» como longitud mayor que el percentil 99 de la referencia de desarrollo pertinente. Congelar el umbral entero antes de evaluar prueba. Reportar frecuencia entre intentos válidos, frecuencia entre estructuras únicas y frecuencia por todos los intentos, además de histogramas y exceso en puntos porcentuales respecto de la referencia de prueba. Analizar por bins de número de carbonos para distinguir crecimiento global de tamaño de alargamiento desproporcionado. La regla detecta una cola estructural; no convierte automáticamente una cadena larga en una alucinación.

## 8. Análisis estadístico y regla conjunta

### Réplicas e incertidumbre
La unidad experimental es una ejecución **semilla–diana**, no cada molécula. Estimar diferencias emparejadas bucle−sin bucle por semilla y diana, y promediar con igual peso por diana. Reportar cada diana, no solo el promedio. Con tres dianas, las conclusiones se limitarían fundamentalmente a esas dianas; un efecto universal requeriría muchas más.

Construir intervalos mediante bootstrap de pares de ejecuciones dentro de cada diana; incorporar un nivel interno para el muestreo de moléculas y la revisión química cuando corresponda. El análisis principal trataría las tres dianas como estratos fijos. Cinco semillas ofrecen precisión limitada; se harían comprobaciones de sensibilidad con métodos emparejados y se evitaría falsa precisión de intervalos basados en miles de moléculas como si fueran independientes.

Realizar un piloto exclusivamente de desarrollo para estimar variación entre semillas, tasa de fallos y precisión del juicio químico. Ajustar semillas, propuestas finales y tamaño de revisión mediante simulación de potencia/anchura de intervalos para los efectos mínimos relevantes. Aumentar semillas si domina variación entre ejecuciones, propuestas si domina error de muestreo y revisión si domina incertidumbre de adjudicación. Fijar el presupuesto final antes de abrir prueba, sin detener por significación.

### Márgenes
Fijar efectos mínimos relevantes y márgenes de no inferioridad en desarrollo, documentando magnitud, justificación y responsable. Como referencias de planificación, podría tolerarse hasta 5 % de pérdida relativa de diversidad interna, hasta 10 % del número efectivo de scaffolds y hasta 1 punto porcentual adicional de cadenas ultralargas. No adoptar esos números automáticamente: contrastarlos con fluctuaciones entre muestras reales, sensibilidad de las métricas y juicio químico; congelarlos después.

Para MMD, fijar una reducción mínima relevante usando variación entre submuestras reales independientes, sin confundir ruido muestral con beneficio. Para rendimiento de calidad y alucinaciones, fijar diferencias absolutas mínimas según prevalencia y utilidad práctica en desarrollo. Si los fallos de base son casi nulos, reconocer que demostrar reducción puede ser inviable; no sustituir silenciosamente reducción por no inferioridad.

### Decisión preespecificada
El apoyo a la **pregunta completa** requeriría simultáneamente:
1. **Propiedades:** superioridad del rendimiento de moléculas distintas respaldadas por intento, mejora de la proporción con afinidad independiente respaldada y ausencia de deterioro relevante de los componentes químicos dentro de sus objetivos predefinidos.
2. **Alucinaciones:** reducción de la tasa primaria H1∪H2∪H3 mayor que el mínimo relevante.
3. **Alineación:** reducción de MMD hacia la referencia pertinente mayor que el mínimo relevante. Que la distancia no empeore solo demostraría preservación, no mejor alineación.
4. **Diversidad y cadenas:** no inferioridad de diversidad interna y número efectivo de scaffolds, sin exceso relevante de cadenas ultralargas ni dependencia de copias del entrenamiento.

Usar pruebas unilaterales e intervalos al 95 % para los umbrales preespecificados. Esta afirmación conjunta se trataría como una prueba de intersección–unión: todos los criterios deben pasar. Para afirmaciones individuales de superioridad y los contrastes con señal permutada y selección posterior, aplicar Holm dentro de una familia registrada de contrastes confirmatorios. El resto sería exploratorio, con estimaciones e intervalos y, si se hacen búsquedas múltiples, control de FDR.

El contraste con señal permutada tendría que favorecer al bucle para atribuir beneficio a la información química específica y no solo al procedimiento de actualización. La superioridad frente a selección posterior sería una conclusión práctica separada: podría existir efecto causal sobre generación sin ventaja sobre reranking.

Posibles conclusiones incluyen apoyo completo, beneficio parcial con compromisos, ausencia de evidencia, o resultado inconcluso por baja precisión o evaluador no fiable. Una ganancia de score con pérdida de diversidad, afinidad no corroborada o alineación solo no inferior no respondería afirmativamente a toda la pregunta.

## 9. Viabilidad, recursos y alternativa mínima

Se necesitarían datos curados con licencia apropiada, trazabilidad del entrenamiento, RDKit y código versionado de SA/QED, motor de docking, predictor independiente, almacenamiento de todos los intentos y scores, tiempo de especialistas para revisión ciega y probablemente una GPU para entrenar y actualizar el generador. El docking podría paralelizarse en CPU. Antes de presupuestar horas, medir en desarrollo tiempo por consulta, fallos de preparación y memoria; el total orientativo de propuestas no equivale a ese número de cálculos exitosos o únicos. Publicar costes por condición y scripts/configuraciones reproducibles.

No hay que disponer de esos recursos para entregar este diseño. El entorno comunicado —sin datasets, red, GPU ni dependencias de proyecto preinstaladas— no respalda una ejecución inmediata.

**Alternativa mínima viable:** una sola diana bien documentada, tres semillas, un generador pequeño auditable, cinco lotes de adaptación de 128 propuestas y 1.000 propuestas finales por condición. Mantener las tres condiciones generativas esenciales, selección posterior derivada del conjunto congelado, evaluación de todos los intentos y validación independiente; omitir las ablaciones. Eliminar corroboración secundaria costosa antes que eliminar el evaluador independiente o los controles causales. Sería un estudio piloto local, probablemente insuficiente para demostrar simultáneamente todos los criterios y sin generalización entre dianas. Si no puede obtenerse un evaluador independiente fiable, el mínimo solo estudiaría cambios de distribución y explotación de scores, no mejora respaldada de afinidad.

### Límites
Los scores dependen de convenciones químicas; las bases reales están sesgadas por lo que se ha sintetizado y medido; los predictores pueden compartir errores con el docking; y «alucinación» requiere reglas auditables pero seguirá teniendo casos inciertos. El protocolo permite identificar estos límites y resultados mixtos, no convertir evidencia computacional en validación experimental.
````

**Stage**

````text
result
````

**Evidence**

````text
La inspección previa, única exploración realizada, mostró solo `task.json` en el directorio visible. Ese archivo contiene la pregunta, el contexto de diseño y `documents.track.md` con el texto exacto «Design-only task; repositories and compute are not required». No proporciona código, generador, fórmula de p-logP, dianas, datos, evaluadores, presupuestos ni resultados. La comprobación con Python solo confirmó la estructura del documento y los archivos visibles; no fue un experimento. El investigador aprobó el enfoque y pidió convertir lo desconocido en elecciones de protocolo explícitas. La comparación emparejada controla checkpoint, muestreo y oportunidades de evaluación; el control permutado identifica el valor de la asociación entre molécula y señal; la selección posterior separa generación de ranking. Los denominadores sobre todos los intentos impiden ocultar fallos o repetición mediante filtrado, y la evaluación independiente con control de dominio limita, sin eliminar, el riesgo de explotación de métricas. La decisión conjunta diferencia mejora efectiva de alineación de simple ausencia de deterioro.
````

**Assumptions**

````text
[
  "Requisito fijo: la entrega es solo de diseño; no se exige repositorio, cómputo ni ejecución. Ninguna cifra del protocolo representa un resultado.",
  "Elección no confirmada: interpretar p-logP como CrippenLogP menos SA y penalización de anillos mayores de seis, bajo implementaciones congeladas.",
  "Elecciones propuestas: Transformer de SMILES, actualización REINFORCE con KL, recompensa de percentiles equiponderados y docking como señal de afinidad.",
  "Se supone factible obtener datos auditables, tres dianas adecuadas, referencias independientes y un predictor de afinidad con validación aceptable; si no, se aplican los límites y alternativa mínima descritos.",
  "Los tamaños de muestra, márgenes orientativos y selección de fuentes son decisiones de planificación que se congelarían tras desarrollo, no detalles sustentados por los insumos.",
  "Se supone acceso futuro a cómputo y revisión química especializada; no se presume su disponibilidad en el entorno actual."
]
````

**Uncertainties**

````text
[
  "La interpretación original de p-logP sigue sin estar confirmada; el estudio respondería bajo la fórmula declarada.",
  "La factibilidad de validar afinidad depende de datos medidos suficientes, consistentes y representativos; una predicción favorable no demuestra unión experimental.",
  "Los márgenes y potencia efectiva requieren datos de desarrollo; cinco semillas y tres dianas no garantizan precisión suficiente.",
  "Las referencias reales tienen sesgos de selección y cobertura; alineación se define respecto de las referencias declaradas, no de toda la química posible.",
  "Las categorías H2/H3 pueden presentar desacuerdo e incertidumbre; su muestreo y adjudicación contribuyen a los intervalos.",
  "El coste real depende del generador, docking y evaluación; no se ha realizado benchmark ni ejecución experimental."
]
````

### Event 5 — Simulator

**Message**

````text
El diseño final satisface la entrega solicitada: incluye fundamento, implementación concreta del bucle, controles causales, evaluación independiente, métricas de alineación y diversidad, definición operativa de fallos, análisis estadístico y viabilidad. Distingue correctamente las elecciones propuestas de los hechos disponibles y la evidencia computacional de la afinidad experimental. La regla conjunta permite responder sin confundir mejoras de puntuación con mejora química integral, y admite resultados mixtos o inconclusos. No se requieren experimentos ejecutados ni revisiones adicionales para esta entrega.
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
El documento presentado especifica recompensa y actualización, comparación emparejada con generador congelado, señal permutada y selección posterior; contempla particiones sin fuga, denominadores por intento, cadenas largas, memorización y evaluación independiente. Incluye réplicas propuestas, incertidumbre, multiplicidad, márgenes fijados en desarrollo, recursos y alternativa mínima. No afirma resultados experimentales; la definición original de p-logP y la disponibilidad futura de datos y recursos permanecen explícitamente como incertidumbres.
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
  "event_log": "runs/openai-astra-top10-trial-1-batch-1/episodes/expbench_iclr2024_19281_1-0aedaf6a9390/candidate_046/attempt-1/output/iclr2024__19281__1/events.jsonl",
  "event_log_sha256": "69aed9ccf24fe272950c7a84c948197c202eda149a2793239d24307c49b16d74",
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
