# candidate_046 · expbench · neurips2024/93022/6

[All trial-1 traces](../../README.md)

- Trial: **1**; endpoint: **original**; attempt: **1**.
- Native status: **completed**; normalized native score: **17/100**.
- Recorded protocol: `researcher-review-v2`.
- Actor, simulator, and judge: **GPT-6 Astra, low reasoning**.
- Scope: chronological shared messages and handoff fields. Private tool logs, system prompts, evaluator references, and raw API requests are not included.
- A repaired endpoint belongs to the same trial; it is not an independent repeat. Zero scores and missing scientific submissions are retained.

## Shared conversation

### Event 1 — Simulator

**Message**

````text
Por favor, revise primero los insumos disponibles y proponga un enfoque, sin elaborar aún el diseño final ni ejecutar experimentos. La comparación de interés es SiT con su atención temporal original (neurips2024/93022/6:setup_4) frente a SiT con un operador Hyena no causal (neurips2024/93022/6:setup_5). No se requiere repositorio ni cómputo. Indique qué detalles están documentados y cuáles serían supuestos, especialmente la variante de SiT, la representación de las trayectorias y la implementación no causal. Proponga brevemente cómo definir trayectorias extremadamente largas, consistencia y dinámica multiescala; qué sistemas de prueba y controles permitirían aislar el efecto del reemplazo; y cómo evaluaría calidad, extrapolación de longitud y viabilidad. Señale las incertidumbres que podrían cambiar el diseño y distinga sus propuestas de los requisitos confirmados.
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
El encargo exige únicamente un diseño experimental. Los insumos confirman la comparación entre atención temporal original y Hyena no causal, pero no especifican datos, variante arquitectónica ni presupuesto; todavía no hay informe del agente.
````

**Objectives Open**

````text
[
  "Inspeccionar los insumos y delimitar hechos frente a supuestos.",
  "Revisar un enfoque propuesto con controles, criterios de evaluación y viabilidad antes de autorizar el diseño final."
]
````

### Event 2 — Actor

**Answer**

````text
### Insumos y alcance confirmado
Revisé los insumos: solo está disponible `task.json`, que plantea la pregunta y declara que el trabajo es de diseño; no exige repositorio ni cómputo. Los identificadores `neurips2024/93022/6:setup_4` y `setup_5` están en su solicitud, pero no sus descripciones completas. No ejecuté experimentos.

La comparación confirmada por su solicitud es **SiT con atención temporal original frente a SiT con un operador Hyena no causal**. No están documentados localmente la variante de SiT, la representación de las trayectorias, ni la construcción concreta del operador no causal. No asumiría que el acrónimo identifica inequívocamente una arquitectura ni importaría detalles de otra publicación.

### Enfoque propuesto, pendiente de aprobación
1. **Fijar primero el contrato arquitectónico.** Identificar SiT, localizar los bloques de atención temporal que se reemplazan y conservar el resto: codificador/decodificador, atención espacial si existe, condicionamiento, objetivo generativo y procedimiento de muestreo. Como opción provisional, usar estados físicos multivariados con un token por instante; si las fuentes usan campos espaciales, partículas o latentes, respetar esa representación y definir sobre qué eje actúa Hyena.
2. **Precisar la no causalidad.** Si las fuentes no especifican la implementación, propondría filtros con soporte temporal hacia pasado y futuro, convolución lineal con padding explícito y recorte, evitando convolución circular accidental. La generación sería conjunta sobre la trayectoria, no un predictor causal disfrazado. Quedan por fijar la parametrización del filtro, sus compuertas y su extensión a longitudes nuevas. Verificaciones futuras con impulsos y perturbaciones a ambos lados comprobarían soporte y bordes; la no causalidad por sí sola no implica acceder a datos de prueba durante generación.
3. **Definir operacionalmente el objetivo.** Llamaría «extremadamente largas» a trayectorias largas tanto respecto de la longitud máxima de entrenamiento como de las escalas físicas. Propondría probar L, 2L, 4L y 8L sin reentrenar y exigir que los horizontes mayores cubran muchas escalas lentas —por ejemplo, al menos diez tiempos característicos lentos, a confirmar según sistema—. Los multiplicadores son propuestas, no requisitos documentados. Si esto excede la viabilidad, se declararía esa limitación y no se rebautizaría una secuencia corta como extremadamente larga.
4. **Medir consistencia y multiescala por separado.** Consistencia: ausencia de discontinuidades y deriva espuria, cumplimiento de restricciones físicas y estabilidad de estadísticas entre ventanas iniciales y tardías, cuando se espera estacionariedad. Dinámica multiescala: autocorrelaciones, espectros o wavelets, estadísticas por escala y acoplamiento entre variables rápidas y lentas. En sistemas caóticos priorizaría fidelidad estadística y dinámica sobre coincidencia punto a punto a largo plazo. Los umbrales se predefinirían usando variabilidad entre trayectorias de referencia, no a partir del resultado favorable de un modelo.
5. **Elegir un pequeño banco interpretable.** Como candidatos: un proceso estocástico con dos tiempos de relajación conocidos, un sistema caótico acoplado rápido–lento como Lorenz–96 de dos escalas y, si la representación fuente lo permite, un sistema espacial como Kuramoto–Sivashinsky. El primero calibra recuperación de escalas; el segundo prueba interacción multiescala; el tercero comprueba generalidad espacial. Son opciones de diseño, no los sistemas atribuidos a los setups.
6. **Aislar el reemplazo.** Comparación primaria con el mismo protocolo y cambio únicamente del mezclador temporal; mismos datos, particiones por trayectorias o condiciones iniciales independientes, longitud de entrenamiento, muestreo y presupuesto de ajuste. Registrar parámetros y coste, sin afirmar que ambos quedan automáticamente igualados. Una comparación secundaria emparejada por capacidad y otra bajo presupuesto computacional común separarían ventajas de arquitectura, tamaño y recursos. Usaría varias semillas y estimaría incertidumbre entre trayectorias independientes, no tratando ventanas correlacionadas como réplicas. Una ablación causal de Hyena ayudaría a atribuir el efecto de bidireccionalidad, siempre que sea compatible con el objetivo; no sustituiría al contraste principal.
7. **Evaluar calidad, extrapolación y viabilidad conjuntamente.** Calidad: distribuciones de estados, incrementos y observables físicos; consistencia y multiescala según lo anterior. Extrapolación: degradación frente a longitud, sin adaptación de pesos y explicitando cambios permitidos de filtros o posiciones. Viabilidad: memoria pico, tiempo y coste total de generar una trayectoria —no solo del operador—, bajo hardware, precisión y muestreo especificados. Distinguir generación conjunta de generación por ventanas; si se permite esta última, mantenerla como protocolo separado para ambos modelos y medir artefactos de unión. Un límite de memoria sería evidencia de viabilidad limitada, no una puntuación inventada de mala calidad.

La conclusión propuesta requeriría **mejor escalabilidad con calidad y consistencia preservadas**, junto con recuperación de las escalas lentas y sus interacciones. Ser más rápido o producir más tokens no bastaría; tampoco una visualización aislada. El alcance de cualquier conclusión quedaría restringido a los sistemas y horizontes evaluados.

### Aclaraciones que podrían cambiar el diseño
Solicitaría al investigador, agrupadas en cuatro consultas sobre las fuentes:
- **setup_4:** ¿Qué variante exacta de SiT, objetivo de entrenamiento, esquema de generación y bloques de atención temporal se documentan?
- **Ambos setups:** ¿Qué representa una trayectoria, cómo se tokeniza, qué condicionamiento usa y cuáles son los sistemas, pasos temporales y longitudes previstos?
- **setup_5:** ¿Cómo se implementa Hyena no causal: filtros, soporte bidireccional, orden/compuertas, bordes y mecanismo para extender la longitud?
- **Ambos setups:** ¿Hay protocolos prescritos de comparación, definiciones de consistencia o multiescala, o exigencia de generación conjunta frente a ventanas?

Con esas respuestas ajustaría las opciones anteriores y, solo tras aprobación explícita, desarrollaría el diseño completo.
````

**Stage**

````text
plan
````

**Evidence**

````text
`inspect_repository('.')` mostró únicamente `task.json`; su lectura confirmó la pregunta y la entrada documental «Design-only task; repositories and compute are not required». Una comprobación exploratoria `find . -maxdepth 2 -type f -print` confirmó que no había otros archivos disponibles. No hay código, datasets ni texto local de setup_4/setup_5 que permita verificar arquitectura o detalles de implementación. Estas comprobaciones fueron únicamente de insumos, no experimentos.
````

**Assumptions**

````text
[
  "La representación provisional de un token por estado temporal es una propuesta sustituible por lo documentado en las fuentes.",
  "Los sistemas de prueba, multiplicadores de longitud y criterio ilustrativo de diez escalas lentas son propuestas, no requisitos confirmados.",
  "Se propone mantener idéntico el contexto generativo y modificar solo el mezclador temporal; su factibilidad depende de la arquitectura fuente.",
  "La convolución bidireccional lineal es una posible operacionalización de Hyena no causal, no una descripción verificada de setup_5."
]
````

**Uncertainties**

````text
[
  "Identidad exacta de SiT y ubicación/estructura de su atención temporal.",
  "Representación, condicionamiento y protocolo de generación de trayectorias.",
  "Parametrización no causal de Hyena y tratamiento de bordes y longitudes no vistas.",
  "Escalas físicas y observables relevantes de los sistemas que establezcan las fuentes.",
  "Compatibilidad de extrapolación sin reentrenamiento con posiciones/filtros de ambos modelos y viabilidad de generación conjunta."
]
````

### Event 3 — Simulator

**Message**

````text
Apruebo el enfoque. Desarrolle ahora el diseño experimental final, sin ejecutar experimentos. Los únicos detalles confirmados son SiT con atención temporal original (neurips2024/93022/6:setup_4) y su reemplazo por Hyena no causal (neurips2024/93022/6:setup_5); no hay información adicional para responder las cuatro consultas. Mantenga lo desconocido como desconocido y presente una configuración operativa propuesta, no atribuida a las fuentes, con las dependencias arquitectónicas claramente señaladas.

Use como núcleo el sistema estocástico de dos escalas y Lorenz–96 de dos escalas; el sistema espacial puede quedar como extensión opcional. Concrete datos y particiones independientes, escalas y horizontes físicos, entrenamiento, generación, semillas, controles y métricas. Especifique cómo se conservan el objetivo y el muestreo de SiT y cómo se implementaría el mezclador Hyena con compuertas, soporte bidireccional, bordes y extensión de filtros. Distinga extrapolación sin reentrenamiento de capacidad para entrenar y generar a mayor longitud: son preguntas relacionadas, pero diferentes.

Incluya criterios de decisión predefinidos para fidelidad absoluta frente a referencias, preservación de calidad respecto de atención y escalabilidad. Explique cómo calibrar márgenes con referencias independientes antes de evaluar modelos y cómo estimar incertidumbre sin contar ventanas correlacionadas como réplicas. La recuperación de estadísticas marginales no debe sustituir la evaluación de dinámica lenta y acoplamiento rápido–lento. Distinga un resultado favorable para ambos modelos, una ventaja exclusiva de eficiencia, un deterioro dinámico y un resultado inconcluso por recursos.

Entregue un diseño autosuficiente con justificación, controles, plan de análisis y viabilidad por etapas. Los recursos y tamaños que proponga deben identificarse como provisionales; no se necesitan mediciones reales ni estimaciones de rendimiento presentadas como hechos.
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
El plan presentado aísla el reemplazo temporal, reconoce la falta de especificaciones fuente, propone referencias multiescala y separa calidad de coste. Es adecuado para avanzar a un diseño, siempre que concrete decisiones operativas y mantenga explícitos los supuestos; no se han reportado experimentos.
````

**Objectives Open**

````text
[
  "Diseño final operativo con supuestos arquitectónicos explícitos",
  "Controles de atribución, protocolos de longitud y evaluación multiescala",
  "Criterios de decisión, incertidumbre y viabilidad sin ejecución"
]
````

### Event 4 — Actor

**Answer**

````text
# Diseño experimental: atención temporal de SiT frente a Hyena no causal

## 1. Alcance, requisitos y límites de atribución

**Confirmado:** comparar SiT con su atención temporal original (`neurips2024/93022/6:setup_4`) y el reemplazo de esa atención por Hyena no causal (`neurips2024/93022/6:setup_5`). El trabajo es exclusivamente de diseño. No se han ejecutado experimentos.

**Desconocido:** variante de SiT, objetivo de entrenamiento, representación, condicionamiento, bloques temporales, codificación posicional, sampler y arquitectura específica de Hyena. Los identificadores no permiten reconstruir esos detalles y no se les atribuye ninguna de las elecciones siguientes.

Todo lo que sigue constituye una **configuración operativa propuesta**. Permite preparar un estudio controlado, pero su ejecución como comparación fiel de esos setups requiere seleccionar y documentar una implementación concreta de SiT. Si no se consigue identificarla, el estudio solo podrá describirse como una comparación en una implementación SiT elegida por los investigadores, no como reproducción de los setups.

### Hipótesis separadas

- **H1, fidelidad:** ambas arquitecturas reproducen trayectorias válidas, incluyendo dinámica lenta y acoplamiento rápido–lento.
- **H2, extrapolación:** entrenadas a longitud L, conservan esa fidelidad al generar 2L, 4L y 8L sin actualizar pesos.
- **H3, capacidad a mayor longitud:** entrenar y generar directamente a longitudes mayores es viable, con calidad adecuada.
- **H4, eficiencia:** Hyena mejora memoria o coste a calidad comparable. H4 no implica H1–H3.

## 2. Sistemas y referencias físicas

### A. Sistema estocástico lineal de dos escalas

Usar el proceso estacionario acoplado

\[
dS=-S\,dt/20+\sqrt{2/20}\,dW_S,
\qquad
dF=-(F-S)\,dt+\sqrt{2}\,dW_F,
\]

con ruidos independientes. S es lento, F relaja hacia S rápidamente. Las escalas de los modos son 20 y 1 unidades físicas. El acoplamiento permite distinguir un modelo con marginales correctas de uno con dependencia temporal o entre variables incorrecta.

- Representación: estado completo `(S,F)`; muestreo cada Δt=0,1.
- Simulación de referencia: transición gaussiana exacta mediante exponencial de la matriz de deriva y covarianza integrada; estado inicial extraído de la distribución estacionaria conjunta, no de marginales independientes.
- Referencias analíticas: covarianzas, correlaciones cruzadas y espectros, además de muestras independientes.
- L=1024 pasos: horizonte nominal 102,4; 8L: 819,2, aproximadamente 41 escalas lentas y 819 rápidas. Se distingue horizonte NΔt de la separación entre primera y última observación, `(N−1)Δt`.

### B. Lorenz–96 de dos escalas

Configuración propuesta: K=8 variables lentas, J=8 rápidas por lenta, F=10, c=b=10 y h=1:

\[
\dot X_k=X_{k-1}(X_{k+1}-X_{k-2})-X_k+F-\frac{hc}{b}\sum_jY_{j,k},
\]
\[
\dot Y_{j,k}=cbY_{j+1,k}(Y_{j-1,k}-Y_{j+2,k})-cY_{j,k}+\frac{hc}{b}X_k.
\]

Usar índices periódicos en k y, como convención operativa explícita, anillos periódicos en j dentro de cada k. Esta convención debe quedar congelada: no mezclarla con implementaciones que conectan los anillos rápidos entre celdas.

- Representación: estado completo de 72 componentes; no ocultar las variables rápidas.
- Referencia numérica: RK4, paso inicial propuesto 0,001 unidades; comprobar convergencia estadística con 0,0005 y 0,00025. El paso definitivo se acepta solo si el error numérico queda por debajo de un cuarto de los márgenes de fidelidad definidos más adelante. La divergencia de trayectorias caóticas no se usa como prueba de fallo del integrador.
- Piloto exclusivamente de referencias: determinar relajación del transitorio y estimar escalas de autocorrelación/envolvente de X, Y, energía lenta y forzamiento rápido agregado. Fijar τ_lenta como la mayor escala robustamente estimada de los observables lentos y τ_rápida a partir de los rápidos; no confundir c con una medición exacta de esas escalas.
- Elegir Δt que resuelva τ_rápida con al menos diez muestras y las frecuencias relevantes según un análisis de aliasing. Elegir L como potencia de dos, inicialmente 1024, aumentando si fuera necesario para que LΔt≥2τ_lenta. Así, 8L cubre al menos 16 escalas lentas.
- Si las escalas no pueden estimarse con precisión, prolongar las referencias antes de congelar Δt y L. Si ese L es inviable, la pregunta sobre ese régimen queda sin resolver; no reducir silenciosamente la resolución física.

**Definición preestablecida de extremadamente largo:** longitud ≥8L respecto al entrenamiento y duración ≥10τ_lenta. Son dos requisitos simultáneos. También se reportan resultados intermedios, sin etiquetarlos automáticamente como extremos.

**Extensión opcional:** Kuramoto–Sivashinsky, solo después del núcleo y si el backbone admite una representación espacial apropiada. No es necesaria para contestar la pregunta delimitada a estos dos sistemas.

## 3. Datos, particiones y prevención de fugas

Tamaños iniciales propuestos, revisables solo durante la etapa de referencias y factibilidad, antes de evaluar modelos:

| Partición | Trayectorias independientes por sistema | Uso |
|---|---:|---|
| Entrenamiento | 4096 de longitud L | Ajustar pesos y normalización |
| Validación | 512 de longitud L | Seleccionar hiperparámetros y checkpoints |
| Calibración de referencia | 2048 de longitud 8L | Escalas, márgenes, bandas y potencia |
| Prueba de referencia | 1024 de longitud 8L | Evaluación final bloqueada |
| Reserva de entrenamiento largo | 4096 de longitud 8L | H3, sin usar datos de calibración/prueba |

- OU: semillas y estados estacionarios independientes por trayectoria.
- Lorenz–96: condiciones iniciales y simulaciones independientes; descarte de transitorio de al menos 50τ_lenta, ampliado si estadísticas de lotes aún derivan. Muestrear una sola trayectoria retenida por simulación. Declarar que las conclusiones corresponden al régimen invariante alcanzado y verificar sensibilidad a la distribución inicial si aparecen regímenes distintos.
- No dividir una simulación larga en ventanas asignadas a entrenamiento y prueba. Los recortes dentro de una trayectoria permanecen en su partición y no cuentan como muestras independientes.
- Normalizar cada componente con estadísticas solo del entrenamiento; conservar la transformación inversa para métricas físicas. No normalizar por ventana: borraría variabilidad lenta y deriva.
- Para H3, todos los modelos usan las mismas trayectorias de la reserva, con prefijos adecuados. Igualar número de tokens observados en la comparación principal de entrenamiento a distintas longitudes y reportar también número de secuencias.

## 4. Contrato de implementación de SiT

Antes de entrenar, registrar un manifiesto: versión del backbone, entrada/salida, bloques sustituidos, posiciones temporales, condicionamiento, distribución del tiempo generativo, objetivo y ponderaciones, parametrización de la predicción, optimizador, sampler, tolerancias/pasos y guidance si existe.

**Conservación estricta del objetivo y muestreo:** no cambiar entre brazos la corrupción o interpolación de datos, la distribución del tiempo generativo, el target, las ponderaciones de pérdida, ni la conversión de predicción a trayectoria. Mantener idénticos sampler, número de evaluaciones, tolerancias y condicionamiento. Usar semillas pareadas para el ruido inicial del sampler y su aleatoriedad. El tiempo físico de la trayectoria es un eje distinto del tiempo generativo de SiT.

No es posible escribir la pérdida concreta de SiT con los insumos disponibles. Inventarla y denominarla «original» invalidaría el contraste. Este manifiesto es una dependencia arquitectónica obligatoria, no un grado de libertad para favorecer un brazo.

### Representación y tamaño provisionales

- Un token por instante, con proyección lineal del estado físico a ancho d=256 y proyección final al estado original; profundidad provisional de ocho bloques y MLP de expansión cuatro, si la variante elegida lo permite.
- Mantener la organización residual, normalización y condicionamiento del backbone. Si SiT exige tokens espaciales o bloques espacio–tiempo, conservarlos y aplicar el reemplazo únicamente sobre el eje temporal; entonces la propuesta de tokenización anterior se sustituye y se documenta antes de entrenar.
- En el brazo atención, conservar su número de cabezas y cualquier máscara original. No suponer causalidad o bidireccionalidad no documentada.
- Conservar posiciones originales si existen. Si usan embeddings aprendidos de longitud fija, la extrapolación sin reentrenamiento puede no estar definida. Una regla de interpolación/extrapolación congelada puede estudiarse como protocolo separado, aplicada y declarada por brazo; no equivale a extrapolación nativa ni a un cambio exclusivo del mezclador.

## 5. Mezclador Hyena no causal propuesto

Esta es una realización operativa, no una reconstrucción de setup_5:

1. Proyectar la entrada normalizada u en valor v y dos ramas de compuerta g₁, g₂; usar activación SiLU en las compuertas. Una convolución local opcional de ancho tres se fija simétricamente y con padding no causal; no variar esta elección entre longitudes.
2. Operador de orden dos, por canal:
   `z₀=v; zᵣ=gᵣ ⊙ (hᵣ * zᵣ₋₁), r=1,2`, seguido de proyección de salida. Conservar la envoltura residual y el condicionamiento de SiT.
3. Cada hᵣ contiene una parte para desfases negativos, otra para positivos y un término central único. Definir `(h*z)t=Σs h(t−s)zs`; permitir ambos signos. No imponer simetría de coeficientes, porque podría borrar direccionalidad física.
4. Generar filtros con una pequeña red implícita a partir del desfase físico firmado y características sinusoidales de frecuencias fijas. Usar envolventes exponenciales por canal con tasas positivas aprendidas, sin truncar artificialmente en L. Registrar amplitudes y masa de las colas. Las frecuencias y transformaciones del desfase quedan congeladas; no usar `desfase/longitud solicitada`, que modificaría los coeficientes ya aprendidos al cambiar N.
5. A longitud N, evaluar esa misma red en los desfases `−(N−1)…N−1`, sin ajustar pesos. Es una extensión definida del filtro, pero no una garantía de buena extrapolación: los desfases grandes no recibieron entrenamiento.
6. Convolución lineal mediante FFT con padding suficiente para evitar aliasing circular —para señal de N y filtro de 2N−1, longitud FFT al menos 3N−2— y recorte alineado. Fuera de la secuencia se usa cero. No envolver final con principio ni dar datos externos al bloque. La FFT es un algoritmo de cálculo, no una condición periódica física.

Pruebas unitarias propuestas antes de entrenar: igualdad con convolución directa en secuencias pequeñas; respuesta a impulsos en centro y extremos; ausencia de envolvimiento circular; sensibilidad a perturbaciones a ambos lados; gradientes finitos; invariancia de coeficientes de un mismo desfase al cambiar N. Reportar métricas en bordes e interior por separado, sin excluir los bordes del criterio global.

La generación primaria es conjunta sobre todos los tokens. El operador no causal ve estados internos de la muestra, no el futuro verdadero de una referencia. La generación por ventanas queda fuera del contraste principal; si se añade, ambos brazos usan idéntico solapamiento y se evalúan uniones.

## 6. Entrenamiento, controles y semillas

### Contraste principal

- A: SiT con atención temporal original.
- B: mismo SiT, sustituyendo todos y solo los bloques de atención temporal designados por el mezclador anterior.
- Mantener profundidad, ancho, datos, objetivo, sampler, tokens por actualización y exposición total. Registrar diferencias de parámetros y FLOPs, sin afirmar que quedan igualados.
- Propuesta inicial: AdamW, 100 000 actualizaciones, batch efectivo de 32 secuencias a L, warmup del 5 %, decaimiento coseno y clipping de norma 1. Estos valores se subordinan al manifiesto si el backbone requiere otro protocolo.
- Hiperparámetros: mismo presupuesto de búsqueda, seis configuraciones por brazo con dos semillas exploratorias; por ejemplo, tres tasas de aprendizaje por dos valores de weight decay. Selección únicamente con validación a L, nunca con resultados de extrapolación. Fijar el procedimiento de selección antes de lanzarlo.
- Cinco semillas finales pareadas de entrenamiento. Por semilla y longitud, generar 1024 trayectorias independientes; no elegir muestras visualmente ni descartar fallos.

### Controles secundarios

1. **Capacidad emparejada:** ajustar ancho del mezclador para parámetros totales dentro de aproximadamente ±5 %, sin alterar la representación; si no es posible, reportar el desajuste. Separa reemplazo directo de efecto de capacidad.
2. **Presupuesto computacional común:** curvas de calidad frente a tiempo de entrenamiento y frente a coste de generación. No confundir este control con igualdad de actualizaciones.
3. **Hyena causal:** mismo orden y compuertas, suprimiendo soporte futuro, si el objetivo permite entrenarlo sin otros cambios. Es una ablación de bidireccionalidad, no el contraste principal.
4. **Controles de métricas:** referencias con orden temporal barajado, bloques lentos permutados y rápidos reasignados entre trayectorias. Conservan parcialmente marginales pero destruyen dinámica o acoplamiento; deben ser detectados antes de aceptar la batería de métricas.

## 7. Dos protocolos de longitud distintos

### E: extrapolación sin reentrenamiento

Entrenar solo a L. Congelar todos los pesos y reglas de posiciones/filtros. Generar L, 2L, 4L y 8L de forma conjunta, con el mismo sampler. No fine-tuning, ni ajuste con validación a las longitudes objetivo. Reportar cambios puramente algorítmicos necesarios para admitir N, como tamaño de FFT.

### T: entrenamiento y generación a mayor longitud

Entrenar desde cero modelos específicos a 2L, 4L y, si resulta viable, 8L. Comparar A/B dentro de cada longitud bajo exposición igualada y, por separado, presupuesto computacional común. Usar acumulación de gradientes si cambia el batch físico. Este protocolo pregunta si Hyena hace accesible el aprendizaje de dependencias largas; no rescata una extrapolación fallida en E.

Si se añade una curva con exposición creciente al aumentar N, etiquetarla como análisis adicional: podría mejorar por más datos y no por arquitectura.

## 8. Métricas: no basta con acertar marginales

Medir en unidades físicas o normalizaciones congeladas con referencias. Evitar una puntuación única que compense pérdida de dinámica con buenas marginales.

| Familia | Métricas primarias propuestas |
|---|---|
| Estados | Distancias Wasserstein de componentes y observables; covarianzas y colas; energía de Lorenz–96 |
| Consistencia | Incidencia de valores no finitos, excursiones extremas frente a referencia, deriva de medias/varianzas entre segmentos, incrementos anómalos y artefactos de borde |
| Dinámica rápida y lenta | Curvas de autocorrelación, tiempos de relajación, potencia en bandas físicas congeladas, distribución de incrementos a retardos rápidos y lentos |
| Multiescala | Energía wavelet por banda y distribución de promedios en bloques de duración τ_rápida, τ_lenta y varias τ_lenta |
| Acoplamiento | Correlaciones cruzadas con retardo, coherencia y fase por banda; estadísticas condicionales rápidas dado el estado lento |
| Balance físico | Residuos integrados de las ecuaciones de Lorenz–96 y balance de transferencia entre X y Y; en OU, media/covarianza de innovaciones y ausencia de correlación serial indebida |

Para OU, contrastar especialmente correlaciones S–F y covarianzas de transición con valores analíticos. Para Lorenz–96, usar Xₖ y el forzamiento rápido agregado `(hc/b)ΣjYj,k`, además de energía rápida local; comprobar medias condicionales y covarianzas a retardos. Los residuos se calibran sobre referencias muestreadas al mismo Δt para no confundir discretización observacional con error generativo. No aplicar restricciones deterministas a trayectorias estocásticas.

Predefinir retardos hasta al menos 2τ_lenta cuando el horizonte lo permita y bandas a partir de referencias, nunca del espectro del modelo. Si L no permite estimar una escala lenta, marcar esa métrica como no identificable a L; no contar su ausencia como éxito. No usar error punto a punto a largo plazo como criterio primario en caos o generación incondicional.

## 9. Calibración, márgenes e incertidumbre

### Calibración anterior a la evaluación de modelos

1. Dividir la partición de calibración en lotes independientes con el tamaño de evaluación previsto, usando remuestreo de trayectorias completas para caracterizar la variabilidad referencia–referencia. No reutilizarla como prueba final.
2. Convertir cada comparación primaria en discrepancia no negativa Dⱼ. Para curvas, usar una norma o máximo sobre retardos/bandas predefinidos. Estimar el percentil 95 de discrepancias entre referencias, qⱼ.
3. Propuesta predefinida de tolerancia absoluta: `Aⱼ=2qⱼ`; margen de no inferioridad frente a atención: `Mⱼ=qⱼ`. Son tolerancias operativas de resolución estadística, no leyes físicas.
4. Impedir que referencias ruidosas legitimen modelos malos: exigir precisión suficiente antes de congelar márgenes. Techos científicos provisionales: 0,10 en discrepancias de correlación/coherencia de magnitud; 10 % de error relativo en tiempos de relajación y energías de banda con potencia relevante; y 0,10 desviaciones estándar de referencia en discrepancias de localización o Wasserstein normalizada. Cerca de cero usar escala absoluta congelada, no porcentajes inestables. Para residuos y otras métricas, fijar un techo mediante referencias refinadas y perturbaciones controladas, antes de acceder a modelos.
5. Si `2qⱼ` excede su techo, aumentar referencias o duración y recalibrar. Si no puede alcanzarse precisión, esa dimensión queda inconclusa. No ensanchar el margen para producir aprobación.
6. Congelar métricas, bandas, márgenes, techo de fallos y plan estadístico. Valores no finitos se consideran fallos; las excursiones físicas se comparan con su tasa de referencia y su intervalo de confianza, no con un umbral visual arbitrario.

Las perturbaciones de control deben demostrar que el ensayo rechaza desacoplamiento y pérdida de dinámica lenta aun conservando marginales. Si no lo hace, revisar la batería antes de evaluar modelos y registrar el cambio.

### Inferencia

- Unidad de réplica: trayectoria independiente para muestreo y semilla de entrenamiento para variación del modelo. Ventanas, instantes y componentes de una misma trayectoria no son réplicas independientes.
- Bootstrap jerárquico: remuestrear semillas de entrenamiento y trayectorias completas dentro de ellas; remuestrear también las trayectorias de referencia. Para A–B preservar el apareamiento de semillas/datos y ruido generativo cuando exista.
- Construir intervalos simultáneos del 95 % para familias primarias y longitudes mediante bootstrap del estadístico máximo; si su estabilidad con cinco semillas es insuficiente, ampliar semillas o declarar incertidumbre. Publicar además cada semilla y su distribución, no solo una media agrupada.
- Como chequeo de robustez, exigir que al menos cuatro de cinco semillas tengan estimaciones puntuales dentro de márgenes y que ninguna presente un fallo catastrófico no explicado. Esto no sustituye los intervalos jerárquicos.

**Fidelidad absoluta:** el límite superior simultáneo de Dⱼ(modelo, referencia de prueba) debe ser ≤Aⱼ para todas las familias primarias identificables, incluyendo dinámica lenta y acoplamiento. Pasar solo marginales no cuenta.

**Preservación frente a atención:** el límite superior simultáneo de `Dⱼ(Hyena)−Dⱼ(atención)` debe ser ≤Mⱼ. Exigir también fidelidad absoluta: ser no inferior a una atención incorrecta no demuestra éxito.

Un intervalo que cruce el umbral implica evidencia insuficiente, no aceptación automática ni prueba de deterioro. Evidencia de deterioro requiere que el límite inferior supere el margen relevante.

## 10. Viabilidad y eficiencia

Recursos provisionales: primera implementación en un acelerador de 24–48 GB; longitudes mayores en uno de 80 GB si está disponible. No hay una estimación factual de que estos recursos basten. Comparar siempre ambos brazos sobre el mismo hardware, precisión y política de ejecución.

Registrar por longitud:

- parámetros, memoria pico total, tamaño físico de batch y acumulación;
- tiempo de entrenamiento por actualización y por token;
- coste total de generar una trayectoria con el sampler completo, sus evaluaciones y la construcción de filtros incluidas;
- latencia batch=1 y throughput a batch común, además del máximo factible de cada brazo;
- máxima longitud que cabe y máxima longitud que satisface calidad; no son lo mismo.

Mediciones futuras: calentamiento, sincronización del acelerador y al menos 20 repeticiones temporizadas en varios lanzamientos; reportar dispersión. Usar atención exacta optimizada y FFT eficiente, evitando comparar una implementación ingenua con otra optimizada. Checkpointing, precisión mixta y kernels deben documentarse y estar disponibles equitativamente; informar si se activan solo por necesidad de memoria.

Criterio provisional de ventaja práctica: a calidad preservada y longitud común, reducción de al menos 20 % en memoria pico o coste total, con intervalo de confianza que sostenga la reducción en tiempo cuando corresponda, sin empeorar el otro recurso más de 10 %. Reportar por separado ventajas que no satisfagan ese compromiso. Una longitud máxima al menos doble con fidelidad aceptable es evidencia adicional de capacidad, pero no permite inventar calidad para el brazo que no pudo ejecutarse.

### Ejecución futura por etapas

1. **Contrato y referencias:** resolver la implementación elegida, simular referencias, verificar integrador, escalas, calibración y sensibilidad de métricas.
2. **Corrección mínima:** pruebas de operador, objetivos y sampler; verificar que el reemplazo es el único cambio principal.
3. **Piloto de factibilidad:** pequeños batches y secuencias, sin inferencias sobre la hipótesis. Congelar recursos, tamaños y presupuestos definitivos. Registrar cualquier desviación del plan.
4. **Estudio E:** entrenamiento a L y evaluación bloqueada de extrapolación.
5. **Estudio T:** entrenamientos largos escalonados; detener aumentos al alcanzar el presupuesto registrado, sin ocultar fallos.
6. **Controles secundarios y extensión espacial:** solo tras el contraste principal o cuando sean necesarios para interpretar un efecto.

Si el presupuesto no permite cinco semillas o referencias suficientes, reducir el alcance declarado o ampliar recursos; no presentar una estimación exploratoria como prueba confirmatoria.

## 11. Interpretación predefinida

- **Favorable para ambos:** A y B pasan fidelidad, dinámica y consistencia a 8L. Hyena permite trayectorias largas en esta implementación, pero no se demuestra que el reemplazo sea necesario ni superior.
- **Ventaja dinámica de Hyena:** B pasa los criterios absolutos, y A falla con evidencia estadística o B mejora métricas dinámicas predefinidas por un margen relevante. Atribuir el efecto al reemplazo queda más sólido si se mantiene en controles de capacidad y presupuesto.
- **Ventaja exclusiva de eficiencia:** calidad y extrapolación son equivalentes dentro de márgenes, pero B cumple el criterio de recursos. Concluir eficiencia, no mejor captura de dinámica multiescala.
- **Deterioro dinámico:** B pierde escalas lentas, correlaciones cruzadas o balances aunque conserve marginales o gane velocidad. Esto refuta la versión fuerte de la afirmación en el régimen probado.
- **Capacidad sin extrapolación:** E falla y T pasa. Hyena puede facilitar entrenar secuencias largas, pero no se demuestra generación extrapolada desde entrenamiento corto.
- **Inconcluso por recursos:** atención o Hyena no pueden entrenarse/generar bajo el presupuesto. Informar el límite; si B sí pasa fidelidad, se puede afirmar viabilidad de B bajo ese presupuesto, pero no superioridad de calidad frente a un A no evaluado.
- **Inconcluso estadístico o arquitectónico:** intervalos cruzan márgenes, referencias insuficientes o contrato de SiT no establecido. No convertir ausencia de evidencia en equivalencia.

La conclusión final debe separar sistema, longitud, protocolo E/T, calidad y recursos. Ningún resultado en estos dos sistemas justificaría por sí solo una afirmación universal sobre trayectorias físicas o todas las variantes de SiT.
````

**Stage**

````text
result
````

**Evidence**

````text
Observaciones efectivas del entorno: `inspect_repository('.')` mostró únicamente `task.json`; su lectura confirmó la pregunta y la declaración «Design-only task; repositories and compute are not required». `find . -maxdepth 2 -type f -print` confirmó la ausencia de otros archivos locales. No hay implementación, datasets ni descripciones de setup_4/setup_5 que respalden detalles arquitectónicos. El investigador aprobó el enfoque y confirmó expresamente que no existe información adicional sobre esas configuraciones. Por ello se conserva el contraste como requisito y se etiqueta toda implementación, sistema parametrizado, tamaño y recurso como propuesta. La elección del proceso lineal permite referencias exactas y prueba de acoplamiento; Lorenz–96 añade caos y transferencia rápido–lento. La separación E/T evita confundir extrapolación con entrenamiento largo. Los controles de referencias perturbadas y las métricas dinámicas evitan aceptar marginales correctas como prueba de dinámica correcta. No se entrenó, simuló ni midió rendimiento; las comprobaciones ejecutadas fueron solo de archivos.
````

**Assumptions**

````text
[
  "La configuración de token por instante y tamaños del backbone es operativa y provisional; depende de que la variante SiT elegida admita ese contrato.",
  "Objetivo, muestreo, posiciones y atención originales siguen desconocidos; su manifiesto debe fijarse antes de una ejecución atribuible a los setups.",
  "La realización Hyena de orden dos, compuertas SiLU, filtros implícitos bidireccionales y padding cero es propuesta, no fuente documentada.",
  "Los parámetros físicos, particiones, semillas, presupuestos, márgenes y recursos son decisiones propuestas que se congelarían tras calibración de referencias y factibilidad, antes de evaluar modelos.",
  "La comparación primaria supone generación conjunta de estados completos en un régimen estacionario; cualquier condicionamiento obligatorio del SiT seleccionado debe mantenerse idéntico y declararse.",
  "Los umbrales prácticos de eficiencia y los techos científicos son criterios operativos explícitos, no resultados ni propiedades garantizadas de las arquitecturas."
]
````

**Uncertainties**

````text
[
  "No se puede garantizar compatibilidad del mezclador o de la tokenización sin conocer el backbone SiT concreto.",
  "La codificación posicional de atención podría impedir extrapolación nativa; una adaptación cambiaría el alcance del contraste.",
  "Los filtros implícitos pueden extenderse matemáticamente sin recuperar dependencias fuera del soporte entrenado.",
  "Las escalas efectivas y la distribución estacionaria de Lorenz–96 requieren verificación mediante referencias independientes.",
  "La precisión inferencial con cinco semillas y los tamaños propuestos puede ser insuficiente para algunos observables lentos.",
  "La memoria, el coste real y las longitudes factibles no se conocen; hardware propuesto y complejidad teórica no sustituyen mediciones futuras."
]
````

### Event 5 — Simulator

**Message**

````text
El diseño final satisface el encargo: incluye justificación, controles, análisis estadístico y viabilidad por etapas, sin afirmar ejecución experimental. Mantiene explícitos los detalles desconocidos de SiT y distingue las elecciones propuestas de los requisitos confirmados. Se da por concluida la tarea de diseño; la respuesta empírica sigue abierta y cualquier ejecución futura deberá fijar el contrato arquitectónico descrito.
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
El entregable compara atención temporal original y Hyena no causal, define horizontes físicos y relativos, separa extrapolación de entrenamiento largo, incluye referencias independientes y pruebas de dinámica lenta y acoplamiento, y establece criterios de fidelidad, no inferioridad y eficiencia. También contempla incertidumbre jerárquica, límites de recursos e interpretaciones alternativas. Las inspecciones de archivos se reportan como tales, no como experimentos. No se identifica una omisión que impida aceptar el entregable de diseño solicitado.
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
  "event_log": "runs/openai-astra-top10-trial-1-batch-1/episodes/expbench_neurips2024_93022_6-b010093c1df2/candidate_046/attempt-1/output/neurips2024__93022__6/events.jsonl",
  "event_log_sha256": "7e609a363855bb2e96c72f7c39743e8fce04f8353836a6b3fb1243d30735659f",
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
