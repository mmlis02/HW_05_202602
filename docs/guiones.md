docs/guiones.md
# Guiones de grabación — Entrevistas y llamadas de venta

31 de octubre de 2026

## Cómo usar estos guiones

Son 10 clips de unos 3 minutos cada uno: 5 entrevistas (Task 1) y 5 llamadas a un restaurante (Task 2). Tú y tu hermano se turnan los roles A y B. Todos los datos son inventados.

| Clip | A (entrevistador / vendedor) | B (candidato / cliente) |
| --- | --- | --- |
| E1, E3, E5 | Tú | Tu hermano |
| E2, E4 | Tu hermano | Tú |
| L2, L4 | Tú | Tu hermano |
| L1, L3, L5 | Tu hermano | Tú |

**Reglas al grabar**

- Lean con naturalidad, pero digan los números, nombres de tecnologías y correcciones **exactamente** como están escritos. Las trampas viven ahí.
- La transcripción de referencia es el texto del guión sin las etiquetas "A:" y "B:". Si improvisan o cambian una palabra, corrijan el guión después de grabar para que coincida con el audio.
- Los números están escritos en letras a propósito: así se dicen, y así debe quedar la referencia.
- Si algún clip dura menos de 2 minutos, hablen más pausado. El límite de la tarea es de 2 a 4 minutos.
- Graben con el celular entre los dos, en un cuarto sin eco. Los archivos se llaman `task 1-1` … `task 1-5` (entrevistas E1 a E5) y `task 2-1` … `task 2-5` (llamadas L1 a L5); el mapeo a los clips `e1` … `l5` está en `config.yaml → audios.archivos`.

**Ajustes que debes hacer tú**

- **Género:** los cargos están en masculino ("desarrollador"). Si tú haces de candidato y prefieres la forma femenina, cámbiala en el guión y en la tabla de ground truth.
- **Fecha de grabación:** los clips se grabaron el sábado 31 de octubre de 2026, y la disponibilidad se calcula desde esa fecha.
- **Tu hermano:** la tarea dice que grabas con un compañero de clase. Dilo tal cual en el README, junto con la línea de consentimiento, y si puedes confírmalo con el profesor.
- **Personaliza:** la tarea pide guiones propios. Cambia nombres, empresas o frases donde quieras; solo actualiza el ground truth si tocas un valor.

## Task 1 — Entrevistas

Cada entrevista dice los seis campos, pero ninguno de forma limpia: hay números distractores, rangos, correcciones y fechas relativas. El orden de los campos cambia en cada clip.

### E1 — Desarrollador backend

A = tú · B = tu hermano

**A:** Buenas tardes, gracias por venir. Soy Carlos, del área de talento de Andina Software. Para empezar, cuéntame un poco de ti y de lo que haces actualmente.

**B:** Buenas tardes, gracias por la invitación. Bueno, actualmente trabajo en una fintech pequeña que se llama Crédito Ágil. Ahí estoy como desarrollador backend semi senior. Mi trabajo es básicamente construir y mantener las APIs que usan la app móvil y el portal web.

**A:** ¿Y cuánto tiempo llevas en ese puesto?

**B:** En Crédito Ágil llevo dos años. Antes estuve en una consultora.

**A:** Entonces, en total, ¿cuántos años de experiencia tienes programando?

**B:** Casi cinco años. Bueno, si cuento solo lo formal, con contrato, serían cuatro años y medio. Antes hice algunos trabajos freelance, pero esos no los cuento.

**A:** Perfecto. ¿Con qué tecnologías trabajas en el día a día?

**B:** Principalmente Python, con Django para las APIs. La base de datos es PostgreSQL, y todo lo desplegamos en contenedores con Docker.

**A:** Muy bien. El equipo aquí trabaja bastante con clientes de afuera. ¿Cómo está tu inglés?

**B:** Leo documentación sin problema, eso todos los días. Escribir correos también. Lo que me cuesta un poco más es hablar, sobre todo en reuniones largas. Diría que tengo un nivel intermedio.

**A:** Entendido. Te cuento del puesto: es para el equipo de pagos, son seis personas, trabajamos en sprints de dos semanas y hay dos días presenciales a la semana en la oficina. ¿Eso te acomoda?

**B:** Sí, sin problema. Vivo relativamente cerca, así que dos días presenciales está bien.

**A:** Genial. Hablemos de lo económico. ¿Cuál es tu pretensión salarial?

**B:** Ahora estoy ganando cinco mil ochocientos. Por el cambio y por las responsabilidades del puesto, mi pretensión sería de seis mil quinientos soles mensuales.

**A:** Bien, lo anoto. ¿Y cuándo podrías empezar?

**B:** Tendría que avisar en mi trabajo y entregar un par de cosas pendientes. Creo que en dos semanas podría estar disponible.

**A:** Perfecto. ¿Tienes alguna pregunta para nosotros?

**B:** Sí, quería saber cómo es la revisión de código y si hay guardias fuera de horario.

**A:** Todo pasa por pull requests con al menos una aprobación. Y sí, hay guardias, pero rotan cada seis semanas y se pagan aparte.

**B:** Perfecto, me queda claro.

**A:** Muy bien. Te escribiremos esta semana con los siguientes pasos. Gracias por tu tiempo.

**B:** Gracias a ustedes. Hasta luego.

### E2 — Analista de datos

A = tu hermano · B = tú

**A:** Buenos días, gracias por conectarse. Le explico rápido: es una conversación corta para conocerle mejor. Antes de todo, una pregunta práctica: si avanzamos, ¿desde cuándo podría incorporarse?

**B:** Buenos días. Puedo empezar de inmediato. Terminé mi último contrato el mes pasado, así que no tengo que dar preaviso.

**A:** Excelente, eso nos ayuda mucho. La posición es para un equipo regional, así que buena parte de las reuniones son en inglés. ¿Cómo describiría su nivel?

**B:** Tengo un nivel avanzado. Saqué el certificado C1 hace dos años, y en mi último trabajo presentaba los reportes mensuales en inglés a la gerencia de Chile y Colombia.

**A:** Muy bien. Cuénteme de su experiencia.

**B:** Trabajo como analista de datos desde dos mil veintitrés, o sea, tres años. Empecé en una empresa de seguros, en el área de riesgos, y luego pasé a una cadena de farmacias.

**A:** ¿Y cuál fue su último puesto exactamente?

**B:** Analista de datos senior en Farmacias Bienestar. Bueno, el cargo decía senior, pero en la práctica éramos dos analistas y yo coordinaba con el área comercial.

**A:** ¿Qué herramientas usaba en ese puesto?

**B:** Para los tableros, Power BI. Las consultas las hacía en SQL Server, y para automatizar la limpieza de datos usaba Python con pandas. Al final del año también armamos algunos flujos en Airflow.

**A:** Interesante. ¿Qué proyecto destacaría de ese tiempo?

**B:** Un modelo de reposición de inventario. Antes cada tienda pedía a ojo; con el modelo bajamos los quiebres de stock en casi un quince por ciento en seis meses.

**A:** Muy bien. Por último, el tema salarial. Como es una posición regional, la pagamos en dólares. ¿Cuál sería su expectativa?

**B:** Estaba pensando en algo alrededor de mil ochocientos dólares al mes. Considerando que es regional, lo veo razonable.

**A:** Perfecto, está dentro del rango. ¿Alguna pregunta?

**B:** Sí, ¿el trabajo es remoto?

**A:** Es híbrido: un día a la semana en la oficina y el resto remoto.

**B:** Perfecto, me parece bien.

**A:** Entonces la siguiente etapa es una prueba técnica. Le llegará por correo mañana. Muchas gracias.

**B:** Muchas gracias, quedo pendiente del correo.

### E3 — Jefe de infraestructura

A = tú · B = tu hermano

**A:** Hola, buenas tardes. Gracias por venir hasta la oficina.

**B:** Buenas tardes. Antes de empezar, quería preguntar algo para no hacerles perder tiempo: ¿el rango salarial del aviso es fijo?

**A:** Hay cierta flexibilidad. ¿Cuál sería tu pretensión?

**B:** Estoy entre nueve y diez mil soles. Idealmente, nueve mil quinientos.

**A:** Bien, eso entra en lo que tenemos. Cuéntame qué haces hoy.

**B:** Hoy soy jefe de infraestructura en una empresa de logística, Transportes Pacífico Sur. Manejo un equipo de tres personas.

**A:** ¿Y cuántos años de experiencia tienes en total?

**B:** En infraestructura, ocho. Casi nueve, porque cumplo nueve en marzo, pero digamos ocho.

**A:** ¿Qué stack manejan?

**B:** Todo está en AWS. Los clústeres corren en Kubernetes, la infraestructura la definimos con Terraform, los despliegues van por Jenkins y el monitoreo lo tenemos en Grafana. Antes usábamos Nagios, pero lo apagamos el año pasado.

**A:** Este puesto tiene reuniones con un proveedor en Estados Unidos. ¿Cómo andas de inglés?

**B:** Básico, la verdad. Leo documentación técnica, eso sí, porque todo está en inglés. Pero conversar me cuesta bastante. Estoy llevando clases los sábados.

**A:** Ok, lo tomamos en cuenta. ¿Por qué quieres cambiar de trabajo?

**B:** Porque en mi empresa la infraestructura ya está estable y quiero un reto más grande. Ustedes tienen tráfico de varios países y eso me interesa.

**A:** Tiene sentido. Una pregunta técnica rápida: si un despliegue falla en producción a las dos de la mañana, ¿qué haces primero?

**B:** Primero reviso si el rollback automático funcionó. Si no, hago rollback manual a la versión anterior, confirmo en Grafana que las métricas vuelvan a la normalidad y recién después investigo la causa. Al día siguiente escribimos el postmortem.

**A:** Muy bien. ¿Y cuándo podrías incorporarte?

**B:** Tengo que entregar una migración a fin de mes. A partir del primero de diciembre estaría libre.

**A:** Perfecto. Te contactamos la próxima semana.

**B:** Gracias, quedo atento.

### E4 — Desarrollador frontend

A = tu hermano · B = tú

**A:** Hola, ¿qué tal? Vi tu portafolio antes de la llamada. ¿Con qué estás trabajando ahora?

**B:** Hola, bien, gracias. Ahora todo lo hago en React con TypeScript. El último proyecto lo migramos a Next.js, y los diseños nos llegan en Figma.

**A:** Bacán. ¿Y haces pruebas?

**B:** Sí, pruebas unitarias con Jest. No llegamos al cien por ciento de cobertura, pero los componentes principales están cubiertos.

**A:** ¿Y cuánta experiencia tienes?

**B:** Un año y medio en mi primer trabajo, en una agencia, y otro año en el actual.

**A:** Ok, buena trayectoria. ¿Y en qué puesto estás ahora?

**B:** Soy desarrollador frontend junior en una startup de educación, Aprende Más. Aunque ya llevo un año ahí, todavía figuro como junior.

**A:** Entiendo. Hablemos de expectativas. ¿Cuánto estás buscando?

**B:** Estaba pensando en cuatro mil doscientos… no, perdón, me confundí con lo que gano ahora. Mi pretensión es cuatro mil ochocientos soles.

**A:** Ok, anotado. ¿Y el inglés?

**B:** Intermedio. Entiendo casi todo cuando leo o veo videos, pero hablando me trabo un poco.

**A:** Normal. Aquí el inglés es más para leer documentación. Cuéntame de algún problema difícil que hayas resuelto.

**B:** En la migración a Next.js teníamos páginas que tardaban como seis segundos en cargar. Separé los componentes pesados, cargamos las imágenes de forma diferida y bajamos el tiempo a menos de dos segundos.

**A:** Muy bien. ¿Cuándo podrías empezar?

**B:** En mi contrato tengo un mes de preaviso, así que tendría que avisar y salir en un mes.

**A:** Perfecto. Mañana te mando la prueba técnica: es un proyecto pequeño para hacer en casa, tienes tres días.

**B:** Genial, muchas gracias.

**A:** A ti. Hablamos.

### E5 — Líder de QA

A = tú · B = tu hermano

**A:** Buenas tardes, bienvenido. Como el cliente principal de este equipo es de Canadá, vamos a empezar por ahí: ¿cómo está tu inglés?

**B:** Bien. Viví dos años en Toronto por trabajo, así que lo uso con soltura. Diría que avanzado.

**A:** Perfecto. ¿En qué estás trabajando actualmente?

**B:** Soy líder técnico de QA en una empresa de comercio electrónico. Tengo a cargo a cuatro testers y defino la estrategia de pruebas de la tienda web y de la app.

**A:** ¿Qué herramientas usan?

**B:** Para automatización web, Cypress. Antes usábamos Selenium y todavía mantenemos algunas pruebas viejas ahí. Las pruebas de API las hacemos en Postman, y el seguimiento de defectos está en Jira.

**A:** ¿Y pruebas de carga?

**B:** Algo con JMeter, pero muy puntual, una o dos veces al año antes de las campañas grandes.

**A:** Bien. Hablemos de tiempos. Si todo sale bien, ¿cuándo podrías empezar?

**B:** Ahí tengo una restricción: en diciembre tenemos la campaña de fin de año y no quiero dejar al equipo en medio de eso. Podría empezar la segunda semana de enero, el lunes once.

**A:** Entiendo, es razonable. ¿Cuál es tu expectativa salarial?

**B:** Hoy gano seis mil doscientos. Mi pretensión es de siete mil soles brutos mensuales.

**A:** Ok. ¿Y cuántos años llevas en calidad de software?

**B:** Empecé como tester manual en dos mil veinte, así que van seis años. Los últimos dos como líder.

**A:** Muy bien. Una última pregunta: ¿cómo decides qué automatizar y qué no?

**B:** Automatizo lo que se repite en cada release y lo que más se rompe: el login, el carrito, el pago. Lo que cambia cada semana lo dejo manual hasta que se estabilice.

**A:** Me parece un buen criterio. Te enviaremos la invitación para la entrevista con el gerente.

**B:** Gracias, quedo atento.

## Task 1 — Ground truth

Estos son los valores correctos que tu sistema debe extraer. La disponibilidad absoluta se calcula desde la fecha de grabación, el 2026-10-31.

| Clip | anios_experiencia | ultimo_puesto | tecnologias | pretension_salarial | disponibilidad | nivel_ingles |
| --- | --- | --- | --- | --- | --- | --- |
| E1 | 4.5 | Desarrollador backend semi senior | Python, Django, PostgreSQL, Docker | 6500 PEN | 2026-11-14 ("en dos semanas") | intermedio |
| E2 | 3 | Analista de datos senior | Power BI, SQL Server, Python, pandas, Airflow | 1800 USD | 2026-10-31 ("de inmediato") | avanzado |
| E3 | 8 | Jefe de infraestructura | AWS, Kubernetes, Terraform, Jenkins, Grafana | 9500 PEN | 2026-12-01 ("primero de diciembre") | basico |
| E4 | 2.5 | Desarrollador frontend junior | React, TypeScript, Next.js, Figma, Jest | 4800 PEN | 2026-11-30 ("un mes de preaviso") | intermedio |
| E5 | 6 | Líder técnico de QA | Cypress, Selenium, Postman, Jira, JMeter | 7000 PEN | 2027-01-11 ("el lunes once" de enero) | avanzado |

**Reglas de anotación** (explícalas en el README)

- **tecnologias:** cuentan las que el candidato usa hoy. No cuenta una herramienta que dice haber abandonado (Nagios en E3).
- **pretension_salarial:** es la cifra que pide, no la que gana hoy. Si da un rango y un ideal, vale el ideal.
- **disponibilidad:** se guarda como fecha absoluta a partir de la fecha de grabación.
- **nivel_ingles:** tres clases: basico, intermedio, avanzado.

**Qué hace difícil cada clip**

| Clip | Trampas |
| --- | --- |
| E1 | "casi cinco" antes de "cuatro años y medio"; sueldo actual (5800) antes de la pretensión; "dos semanas" aparece también como duración del sprint |
| E2 | años dichos como "desde dos mil veintitrés"; moneda en dólares; distractores "C1" y "quince por ciento" |
| E3 | rango "entre nueve y diez mil" con ideal; "casi nueve"; Nagios como tecnología abandonada |
| E4 | los 2.5 años nunca se dicen, hay que sumar: debe quedar sin_verificar aunque el valor sea correcto; autocorrección 4200 → 4800 |
| E5 | sueldo actual (6200) antes de la pretensión; año del "lunes once" implícito; Selenium antiguo pero todavía en uso |

**Posición de cada campo en la conversación** (1 = se dice primero)

| Campo | E1 | E2 | E3 | E4 | E5 |
| --- | --- | --- | --- | --- | --- |
| ultimo_puesto | 1 | 4 | 2 | 3 | 2 |
| anios_experiencia | 2 | 3 | 3 | 2 | 6 |
| tecnologias | 3 | 5 | 4 | 1 | 3 |
| nivel_ingles | 4 | 2 | 5 | 5 | 1 |
| pretension_salarial | 5 | 6 | 1 | 4 | 5 |
| disponibilidad | 6 | 1 | 6 | 6 | 4 |

Distribución: nivel_ingles tiene 1 básico, 2 intermedios y 2 avanzados; la moneda es PEN en 4 clips y USD en 1; los años van de 2.5 a 8.

## Task 2 — Carta del restaurante

Dominio elegido: **restaurante**, una pollería inventada llamada La Leña Dorada. Es más fácil de actuar que un plan de telefonía. Tenla impresa al grabar: el vendedor la usa para dictar precios.

| Producto | Tamaño | Precio (S/) |
| --- | --- | --- |
| Pollo a la brasa | Entero | 68 |
| Pollo a la brasa | Medio | 36 |
| Pollo a la brasa | Cuarto | 20 |
| Papas fritas | Familiar | 14 |
| Papas fritas | Personal | 7 |
| Chicha morada | Jarra de 1 litro | 12 |
| Chicha morada | Vaso | 5 |
| Gaseosa | 1.5 litros | 9 |
| Gaseosa | Personal | 4 |
| Ensalada clásica | Único | 10 |
| Anticuchos | Porción de 3 palitos | 18 |
| Mollejitas | Único | 16 |
| Torta de chocolate | Porción | 9 |

**Promociones** (solo una por pedido)

- **Dúo familiar:** S/ 10 de descuento si el pedido incluye un pollo entero y unas papas familiares.
- **Promo app:** S/ 5 de descuento si el cliente da el código LEÑA5.

El delivery es gratis. Métodos de pago: efectivo, Yape, Plin o tarjeta.

**Regla de validación:** la suma de cantidad × precio unitario, menos el descuento de la promoción, debe ser igual a total_dicho.

## Task 2 — Llamadas

El cliente se corrige en las cinco llamadas, y en tres de ellas el vendedor dice un total equivocado a propósito. Digan el total equivocado con total naturalidad: es un error humano, no un chiste.

### L1 — Pedido familiar con Dúo

A (vendedor) = tu hermano · B (cliente) = tú

**A:** La Leña Dorada, buenas noches, le habla Javier. ¿En qué le puedo ayudar?

**B:** Hola, buenas noches. Quería hacer un pedido para delivery.

**A:** Claro que sí. ¿Me dice qué va a pedir?

**B:** Un pollo a la brasa entero, con unas papas familiares.

**A:** Muy bien, un pollo entero de sesenta y ocho soles y una papa familiar de catorce. ¿Algo para tomar?

**B:** Sí, una jarra de chicha morada… no, mejor que sean dos jarras, que somos varios en la casa.

**A:** Perfecto, dos jarras de chicha morada a doce soles cada una. ¿Alguna ensalada, algún postre?

**B:** No, con eso está bien. ¿Tienen alguna promoción?

**A:** Sí, como lleva pollo entero con papas familiares, aplica el dúo familiar: diez soles de descuento.

**B:** Ah, buenísimo. ¿El pollo viene con cremas?

**A:** Sí, viene con mayonesa, ketchup y ají de la casa.

**B:** Que manden bastante ají, por favor.

**A:** Listo, lo anoto. ¿A qué dirección se lo enviamos?

**B:** Calle Los Cedros doscientos cuarenta y cinco, departamento trescientos dos, en Surco.

**A:** Calle Los Cedros doscientos cuarenta y cinco, departamento trescientos dos. ¿Alguna referencia?

**B:** Es un edificio blanco frente a un parque, al costado de una farmacia.

**A:** Perfecto. ¿A nombre de quién y un número de contacto?

**B:** A nombre de Ramírez. El número es nueve ocho siete, seis cinco cuatro, tres dos uno.

**A:** Gracias. ¿Y cómo va a pagar?

**B:** Con Yape.

**A:** Muy bien. Le confirmo el pedido: un pollo entero, una papa familiar y dos jarras de chicha morada, con el descuento del dúo familiar. El total es noventa y seis soles.

**B:** Perfecto. ¿Cuánto demora?

**A:** Entre cuarenta y cincuenta minutos. Le mandamos el número para el Yape por mensaje.

**B:** Listo, gracias.

**A:** Gracias a usted, buenas noches.

### L2 — Dos medios que se vuelven un entero

A (vendedor) = tú · B (cliente) = tu hermano

**A:** La Leña Dorada, buenas tardes. ¿En qué le puedo ayudar?

**B:** Buenas tardes. Quiero pedir dos medios pollos, por favor.

**A:** Dos medios pollos, muy bien. ¿Algo más?

**B:** Espere, espere. Si un medio cuesta treinta y seis, dos medios me salen setenta y dos. ¿Cuánto está el entero?

**A:** El entero está sesenta y ocho.

**B:** Entonces mejor un pollo entero en vez de los dos medios. Sale más barato.

**A:** Claro, le cambio: un pollo entero en vez de los dos medios. ¿Algo más?

**B:** Una porción de anticuchos.

**A:** Una porción de anticuchos, son tres palitos, a dieciocho soles. ¿Algo de tomar?

**B:** Una gaseosa de litro y medio.

**A:** Una gaseosa de litro y medio, nueve soles. ¿Papas?

**B:** No, papas no, gracias. Ah, tengo un código de la aplicación: LEÑA cinco.

**A:** Perfecto, con el código le descontamos cinco soles. ¿Dirección de entrega?

**B:** Avenida Las Gardenias mil quinientos ochenta, en Pueblo Libre. Es una casa de dos pisos con reja negra.

**A:** Avenida Las Gardenias mil quinientos ochenta, casa de dos pisos con reja negra. ¿Cómo va a pagar?

**B:** En efectivo. Pago con un billete de cien.

**A:** Muy bien, el motorizado lleva vuelto. Entonces le confirmo: un pollo entero, una porción de anticuchos y una gaseosa de litro y medio. El total es noventa y cinco soles.

**B:** Noventa y cinco, ok.

**A:** Le llega en unos cuarenta minutos.

**B:** Perfecto, muchas gracias.

**A:** Gracias por su pedido, buenas tardes.

### L3 — Tres combos y una dirección corregida

A (vendedor) = tu hermano · B (cliente) = tú

**A:** La Leña Dorada, buenas noches.

**B:** Hola, buenas noches. Quiero hacer un pedido: somos tres personas y cada uno quiere su combo.

**A:** Claro. ¿Qué le preparo?

**B:** Tres cuartos de pollo, cada uno con su papa personal.

**A:** Tres cuartos de pollo a veinte soles cada uno, y tres papas personales a siete. ¿Bebidas?

**B:** Tres gaseosas personales.

**A:** Tres gaseosas personales, cuatro soles cada una. ¿Algún postre?

**B:** Sí, dos porciones de torta de chocolate. El tercero está a dieta.

**A:** Dos porciones de torta, a nueve soles cada una. ¿Tiene algún código de promoción?

**B:** No, ninguno. ¿El pollo viene con cremas?

**A:** Sí, mayonesa, ketchup, mostaza y ají de la casa.

**B:** Perfecto. ¿Me pueden mandar extra de ají?

**A:** Claro, sin costo. ¿A qué dirección?

**B:** Jirón Los Halcones mil cuarenta y tres, interior cinco… no, perdón, me equivoqué, es mil treinta y cuatro. Jirón Los Halcones mil treinta y cuatro, interior cinco, en Jesús María.

**A:** Mil treinta y cuatro, interior cinco. ¿Forma de pago?

**B:** Con tarjeta. ¿El motorizado lleva POS?

**A:** Sí, lleva POS. Le repito su pedido: tres cuartos de pollo, tres papas personales, tres gaseosas personales y dos porciones de torta de chocolate. Su total es ciento veintiún soles.

**B:** Ok, perfecto.

**A:** Le llega en cuarenta y cinco minutos aproximadamente.

**B:** Gracias, buenas noches.

**A:** Buenas noches.

### L4 — Almuerzo de oficina

A (vendedor) = tú · B (cliente) = tu hermano

**A:** Buenas tardes, La Leña Dorada, área de delivery.

**B:** Hola, buenas. Quiero hacer un pedido para mi oficina.

**A:** Claro, dígame.

**B:** Un medio pollo a la brasa, con ensalada clásica en vez de papas.

**A:** Las guarniciones se piden aparte, así que le anoto un medio pollo de treinta y seis y una ensalada clásica de diez soles.

**B:** Perfecto. También dos porciones de mollejitas.

**A:** Dos mollejitas, a dieciséis cada una.

**B:** Ah no, perdón, solo una de mollejitas. Y agrégame una porción de anticuchos, mejor.

**A:** Entonces una de mollejitas y una de anticuchos. ¿Para tomar?

**B:** Dos vasos de chicha morada.

**A:** Dos vasos de chicha, cinco soles cada uno. ¿Tiene algún código?

**B:** Sí, el de la app: LEÑA cinco.

**A:** Perfecto, cinco soles de descuento. ¿Dirección?

**B:** Calle Las Orquídeas cuatrocientos dieciocho, oficina setecientos dos, en Miraflores. Es un edificio de oficinas; que deje el pedido en recepción.

**A:** Calle Las Orquídeas cuatrocientos dieciocho, oficina setecientos dos, dejar en recepción. ¿Cómo paga?

**B:** Con Plin.

**A:** Muy bien. Le confirmo: un medio pollo, una ensalada clásica, una porción de mollejitas, una porción de anticuchos y dos vasos de chicha morada, con el descuento de la app. El total es ochenta y cinco soles.

**B:** Perfecto. ¿En cuánto llega?

**A:** En treinta y cinco minutos está ahí.

**B:** Gracias, hasta luego.

### L5 — Reunión familiar

A (vendedor) = tu hermano · B (cliente) = tú

**A:** La Leña Dorada, buenas noches. ¿Delivery o recojo en tienda?

**B:** Delivery, por favor. Es para una reunión familiar.

**A:** Perfecto. ¿Qué le enviamos?

**B:** Dos pollos enteros, dos papas familiares y dos gaseosas de litro y medio.

**A:** Dos pollos enteros…

**B:** Espere, déjeme preguntar… Ya, mejor que sea un pollo entero y un medio pollo. Somos menos de lo que pensábamos.

**A:** Bien, un pollo entero y un medio pollo. ¿Las dos papas familiares y las dos gaseosas de litro y medio se mantienen?

**B:** Sí, eso se mantiene.

**A:** Perfecto. Como lleva pollo entero con papas familiares, tiene el dúo familiar: diez soles de descuento.

**B:** Genial. ¿Vienen con cremas?

**A:** Sí, cada pollo trae su mayonesa, ketchup y ají.

**B:** Perfecto.

**A:** ¿Dirección de entrega?

**B:** Avenida Los Laureles dos mil doscientos setenta y uno, bloque C, departamento quinientos cuatro, en San Juan de Lurigancho.

**A:** Dos mil doscientos setenta y uno, bloque C, departamento quinientos cuatro. ¿Forma de pago?

**B:** Yape.

**A:** Muy bien. Le confirmo: un pollo entero, un medio pollo, dos papas familiares y dos gaseosas de litro y medio, con el dúo familiar. El total es ciento treinta y un soles.

**B:** Ciento treinta y uno, perfecto.

**A:** Le llega en una hora aproximadamente, hoy tenemos bastante demanda.

**B:** No hay problema, gracias.

**A:** Gracias a usted, buenas noches.

## Task 2 — Ground truth y trampas

El corpus cumple las tres trampas obligatorias: correcciones en 5 llamadas (pide mínimo 3), totales errados en 3 (pide mínimo 3) y direcciones con dígitos en las 5.

| Clip | items (producto, tamaño, cantidad × precio S/) | promocion | direccion_entrega | metodo_pago | total_dicho | Total correcto |
| --- | --- | --- | --- | --- | --- | --- |
| L1 | Pollo a la brasa entero 1 × 68; Papas fritas familiar 1 × 14; Chicha morada jarra 2 × 12 | Dúo familiar (−10) | Calle Los Cedros 245, departamento 302, Surco | yape | 96 | 96 |
| L2 | Pollo a la brasa entero 1 × 68; Anticuchos porción 1 × 18; Gaseosa 1.5 litros 1 × 9 | Promo app (−5) | Avenida Las Gardenias 1580, Pueblo Libre | efectivo | 95 | 90 |
| L3 | Pollo a la brasa cuarto 3 × 20; Papas fritas personal 3 × 7; Gaseosa personal 3 × 4; Torta de chocolate porción 2 × 9 | null | Jirón Los Halcones 1034, interior 5, Jesús María | tarjeta | 121 | 111 |
| L4 | Pollo a la brasa medio 1 × 36; Ensalada clásica 1 × 10; Mollejitas 1 × 16; Anticuchos porción 1 × 18; Chicha morada vaso 2 × 5 | Promo app (−5) | Calle Las Orquídeas 418, oficina 702, Miraflores | plin | 85 | 85 |
| L5 | Pollo a la brasa entero 1 × 68; Pollo a la brasa medio 1 × 36; Papas fritas familiar 2 × 14; Gaseosa 1.5 litros 2 × 9 | Dúo familiar (−10) | Avenida Los Laureles 2271, bloque C, departamento 504, San Juan de Lurigancho | yape | 131 | 140 |

**Trampas por llamada** (úsalas para puntuar el validador)

| Clip | Corrección del cliente | Total errado | Causa real del error | Distractores numéricos |
| --- | --- | --- | --- | --- |
| L1 | 1 jarra → 2 jarras | No | — | teléfono de 9 dígitos, "cuarenta y cincuenta minutos" |
| L2 | 2 medios pollos → 1 entero | Sí (+5) | Hablante: el vendedor olvidó el descuento | "setenta y dos", billete de cien |
| L3 | Dirección 1043 → 1034 | Sí (+10) | Hablante: el vendedor sumó mal | número viejo de la dirección |
| L4 | 2 mollejitas → 1, y agrega anticuchos | No | — | "treinta y cinco minutos", oficina 702 |
| L5 | 2 enteros → 1 entero + 1 medio | Sí (−9) | Hablante: el vendedor omitió una gaseosa | números de la dirección |

Los tres totales errados son errores del hablante. Los errores del ASR van a aparecer solos cuando degrades el audio en los niveles de teléfono y ruido de la escalera de degradación, así que ahí tendrás casos de los dos tipos para probar tu regla de diagnóstico.

Ejemplo del registro esperado para L1:

```json
{
  "items": [
    {"producto": "pollo a la brasa", "tamano": "entero", "cantidad": 1, "precio_unitario": 68},
    {"producto": "papas fritas", "tamano": "familiar", "cantidad": 1, "precio_unitario": 14},
    {"producto": "chicha morada", "tamano": "jarra", "cantidad": 2, "precio_unitario": 12}
  ],
  "promocion": "duo familiar",
  "descuento": 10,
  "direccion_entrega": "Calle Los Cedros 245, departamento 302, Surco",
  "metodo_pago": "yape",
  "total_dicho": 96
}
```
