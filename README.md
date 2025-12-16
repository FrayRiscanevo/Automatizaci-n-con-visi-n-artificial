📌 Descripción del proyecto

Este proyecto implementa un sistema de automatización robótica con visión artificial en lazo cerrado, donde un manipulador industrial ABB ajusta dinámicamente su posición a partir de información visual obtenida en tiempo real. La solución integra Python, OpenCV, marcadores ArUco y programación RAPID, permitiendo que el robot reaccione automáticamente a la posición y orientación de un objeto detectado por una cámara.

El sistema fue desarrollado y validado en un entorno de simulación utilizando ABB RobotStudio con controlador IRC5, estableciendo una comunicación TCP/IP tipo socket entre el PC y el robot. A través de esta arquitectura, las coordenadas calculadas desde visión artificial (X, Y, Z) son enviadas al controlador ABB, donde se actualizan los robtargets y se ejecuta el movimiento del robot de forma automática.

⚙️ Arquitectura general

El proyecto está estructurado en tres bloques principales:

PC (Python + OpenCV):
Captura de imágenes, detección de marcadores ArUco, cálculo de posición y orientación (tvec, rvec) y lógica de control.

Comunicación TCP/IP (Sockets):
Envío de datos de posición desde Python hacia el robot mediante una arquitectura cliente-servidor.

Robot ABB (RAPID / RobotStudio):
Recepción de coordenadas, cálculo de offsets, actualización de targets y ejecución del movimiento del TCP hacia la posición detectada.

Esta arquitectura permite una integración flexible entre visión artificial y control robótico, simulando un entorno industrial real.

🔄 Flujo de funcionamiento

Captura:
La cámara adquiere una imagen del entorno donde se encuentra el objeto con marcador ArUco.

Procesamiento:
OpenCV detecta el marcador y calcula su pose (posición y orientación).

Envío de datos:
Python formatea las coordenadas y las envía al robot mediante un socket TCP/IP.

Alineación y movimiento:
El robot recibe los datos, calcula el offset necesario y mueve su TCP a la posición objetivo.

🧪 Metodología y pruebas realizadas

El desarrollo se realizó de forma incremental:

Verificación del funcionamiento de la cámara y detección de distancia y pose.

Pruebas de comunicación enviando datos de prueba desde Python al robot.

Creación y validación de un programa RAPID para movimientos manuales.

Integración total del sistema, logrando movimiento automático del robot a partir de la información visual.

⚠️ Desafíos abordados

Calibración precisa de la cámara para reducir errores de distorsión.

Latencia en la comunicación TCP/IP, que puede afectar el tiempo de respuesta.

Condiciones de iluminación y reflejos, que influyen en la detección confiable de los marcadores ArUco.

🚀 Aplicaciones potenciales

Automatización con cobots para manipulación de objetos.

Sistemas de seguimiento visual con cámara en tiempo real.

Ensamble y montaje de componentes con alta precisión.

Inspección visual industrial y control de calidad.

✅ Conclusión

El proyecto demuestra la viabilidad de integrar visión artificial y control robótico para lograr sistemas de automatización más precisos, adaptables y eficientes. La combinación de Python, OpenCV y RobotStudio permite reducir tiempos de configuración, mejorar la exactitud del movimiento y sentar bases para aplicaciones industriales más avanzadas.
