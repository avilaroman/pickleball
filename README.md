<p align='center'>
  <a href="https://www.artlabs.tech"><img src='https://tucumanpickleballclub.com.ar/wp-content/uploads/2023/03/Mesa-de-trabajo-264.png' width="150" height="170"></a>
</p>

<h1 align='center'>Pikleball Tracker 🎾</h1>
<p align='center'>
  <img src="https://img.shields.io/github/forks/ArtLabss/tennis-tracking.svg">
  <img src="https://img.shields.io/github/stars/ArtLabss/tennis-tracking.svg">
  <img src="https://img.shields.io/github/watchers/ArtLabss/tennis-tracking.svg">
  
  <br>
  
  <img src="https://img.shields.io/github/last-commit/ArtLabss/tennis-tracking.svg">
  <img src="https://img.shields.io/badge/license-Unlicense-blue.svg">
  <img src="https://hits.sh/github.com/ArtLabss/tennis-tracking.svg"/>
  <br>
  <code>con ❤️ por avilaroman</code>
  
</p>

<!-- 
![Forks](https://img.shields.io/github/forks/ArtLabss/tennis-tracking.svg)
![Stars](https://img.shields.io/github/stars/ArtLabss/tennis-tracking.svg)
![Watchers](https://img.shields.io/github/watchers/ArtLabss/tennis-tracking.svg)
![Last Commit](https://img.shields.io/github/last-commit/ArtLabss/tennis-tracking.svg)  
-->

<h3>Objectivos:</h3>
<ul>
  <li>Trackea la pelota </li>
  <li>Detecta lineas de la cancha </li>
  <li>Detecta a los jugadores</li>
</ul>

<p>Para tracker la bola uso <a href='https://nol.cs.nctu.edu.tw:234/open-source/TrackNet'>TrackNet</a> - una deep learning network para trackear objetos a rápidas velocidades. <br >Para los detectores de personas ResNet50.
<h3>Ejemplo usando: <a href="https://github.com/avilaroman/pickleball/tree/main/VideoInput">Ejemplo de videos</a>

</h3>


Input            |  Output
:-------------------------:|:-------------------------:
![input](https://raw.githubusercontent.com/avilaroman/pickleball/refs/heads/main/VideoOutput/pickleball-GIF1.gif)  |  ![output](https://raw.githubusercontent.com/avilaroman/pickleball/refs/heads/main/VideoOutput/pickleball-GIF1.gif)
![input_img1](https://github.com/ArtLabss/tennis-tracking/blob/00cfe10b18db1e6a68800921dfbda010f90a74bb/VideoOutput/ezgif.com-gif-maker(3).gif)  |  ![output_img1](https://github.com/ArtLabss/tennis-tracking/blob/0f684fdeef96a715984dc74b62b961f68ff95edc/VideoOutput/ezgif.com-gif-maker.gif)
![input_img2](https://github.com/ArtLabss/tennis-tracking/blob/579fb3344935bbf4c5d08e27c99ffc6b56bed896/VideoOutput/ezgif.com-gif-maker(1).gif)  |  ![output_img2](https://github.com/ArtLabss/tennis-tracking/blob/579fb3344935bbf4c5d08e27c99ffc6b56bed896/VideoOutput/ezgif.com-gif-maker(2).gif)
![input_img3](https://github.com/ArtLabss/tennis-tracking/blob/06179bdd29d4424f5e19e5600802f853aaa86f22/VideoOutput/monteCarlo_input.gif)  |  ![output_img3](https://github.com/ArtLabss/tennis-tracking/blob/06179bdd29d4424f5e19e5600802f853aaa86f22/VideoOutput/monteCarlo_output.gif)

<h3>Como correrlo:</h3>

<p>Este proyecto requiere compatibilidad <b>GPU</b> para Instalar el Tensorflow, puedes correr: <a href='https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwissLL5-MvxAhXwlYsKHbkBDEUQFnoECAMQAw&url=https%3A%2F%2Fcolab.research.google.com%2Fnotebooks%2F&usg=AOvVaw0eDNVclINNdlOuD-YTYiiB'>Google Colaboratory</a> with <b>Tipo de Runtime</b> cambiado a <b>GPU</b>.</p>

- [ ] Los videos Input tienen que ser rallies del juego y no pueden contener ningun comercial o placa <strong>, o pausa o a Espectadores en el cuadro por que se comienza a fallar la detección.</strong>.
  
<ol>
  <li>
    Clona este repositorio
  </li>
  
  ```git
  git clone https://github.com/avilaroman/pickleball.git
  ```
  
   <li>
     Download el yolov3 Pesa: (237 MB) desde <a href="https://pjreddie.com/media/files/yolov3.weights">aqui</a> y agrega tu <a href="/Yolov3">Yolov3 carpeta</a>.
  </li>
  
  <li>
    Instala los requerimientos usando pip
  </li>
  
  ```python
  pip install -r requirements.txt
  ```
  
   <li>
    Corre los siguientes comandos:
  </li>
  
  ```python
  python3 predict_video.py --input_video_path=VideoInput/video_input3.mp4 --output_video_path=VideoOutput/video_output.mp4 --minimap=0 --bounce=0
  python3 predict_video.py --input_video_path=pickleball.mp4 --output_video_path=pickleball_output.mp4 --minimap=1 --bounce=0 
  ```
  
  <li>Google Colab upload todos los archivos del Google Drive, incluyendo el yolov3 pasan del paso <strong>2.</strong></li>
  
   <li>
    Creaun Google Colaboratory Notebook en el mismo directorio <code>predict_video.py</code>, canbia el Tuntime: <strong>GPU</strong> y conecta it to Google drive
  </li>
  
  ```python
  from google.colab import drive
  drive.mount('/content/drive')
  ```
  
  <li>
    Cambia el directorio de trabajo para uno: en Colab Notebook y <code>predict_video.py</code> es en mi caso,
  </li>
  
  ```python
  import os 
  os.chdir('drive/MyDrive/Colab Notebooks/tennis-tracking')
  ```
  
  <li>
    Instala 2 requerimientos, por que Colab ya tiene el rest
  </li>
  
  ```python
  !pip install filterpy sktime
  ```
  
  <li>
    Adentro del notebook Corre el comando: <code>predict_video.py</code>
  </li>
  
  ```
   !python3 predict_video.py --input_video_path=VideoInput/video.mp4 --output_video_path=VideoOutput/video_output.mp4 --minimap=0 --bounce=0
o tambien:
    !python3 predict_video.py --input_video_path=pickleball.mp4 --output_video_path=pickleball_output.mp4 --minimap=1 --bounce=0
  ```
  
  <p>Despùés de la compilación es Completada, un nuevo video se creará en  <a href="/VideoOutput" target="_blank">la Carpeta: VideoOutput </a> SI el Minimap: <code>--minimap</code> fué seteado <code>0</code>, si: <code>--minimap=1</code> 3 videos seran creados del juego: 1) Video del juego 2) Video del minimap y 3) Combinados los 2 Videos</p>
  <p><i>Si te parece muy dificil o sale un <b>error</b> o tienes alguna pregunta contactame: by em@il:  avilaroman@gmail.com <a href='https://avilaroman.github.com'>Pickleball</a> </i></p>
  CABE DESTACAR QUE ESTE SOFTWARE TAMBIÉN FUNCIONA PARA CASI CUALQUIER DEPORTE DE PALETA PELOTA: Ping Pong / Padel / Squash / Tenis en distintas superficies.
  se debe cambiar las 9 imagenes de reconocimiento de la cancha: Los Sprites en la carpeta <br> 
  /pickleball/court_configurations/

History
This branch is 0 commits ahead of avilaroman/pickleball:main.
This branch is 18 commits ahead of ArtLabss/tennis-tracking:main.
Folders and files
parent directory
..
court_conf_1.png
court_conf_10.png
court_conf_11.png
court_conf_12.png
court_conf_2.png
court_conf_3.png
court_conf_4.png
court_conf_5.png
court_conf_6.png
court_conf_7.png
court_conf_8.png
court_conf_9.png
court_reference.png

y ya se lo adapta para el mejor judgado, pero igual sino igual también anda con un 85%.
</ol>


<h3>Que Hace y lo nuevo?</h3>
<ul>
  <li>Detecta las lineas de la cancha (Mejorada)</li>
  <li>Detección del Jugador (Optimizada en cuadros)</li>
  <li>El algoritmo ahora trabaja practicamente en cualquier color de cancha y pelotas verdes o de otro color</li>
  <li>Algoritmo mas RAPIDO</li>
  <li>Dynamic Mini-Mapa Dinámico con seguimiento de jugadores y pelota, para activarlo usá el argumento: <code>--minimap</code></li>
  </ul>
  
`--minimap=0`            |  `--minimap=1`
:-------------------------:|:-------------------------:
![input_img1](https://github.com/ArtLabss/tennis-tracking/blob/4b5ff2849b71af67023c4160c4f91481a6821bb3/VideoOutput/input6.gif)  |  ![output_img1](https://github.com/ArtLabss/tennis-tracking/blob/3124a8609b30deb557c1563c45febb1fd86c8956/VideoOutput/input3.gif)

<p>
  Para predecir los puntos de rebote en el la Librería del Machine Learning por el tiempo de las series. <a href="https://www.sktime.org/en/stable/index.html">sktime</a> fue usado. Specificamente, <a href="https://github.com/ArtLabss/tennis-tracking/blob/90652b4547311423ea49c4195dde9da9a81f1893/clf.pkl">TimeSeriesForestClassifier</a> fue entrenado en 3 variables:  <code>X</code>, <code>Y</code> coordenadas de la pelota y <code>V</code> para Velocidad (<code>V2-V1/t2-t1</code>). Ejemplo de Data del modelo ya entrenado: - <a href="https://github.com/avilaroan/pickleball/blob/main/bigDF.csv" >df.csv</a>
<p>
<ul>
  <li>Como especificando: <code>--bounce=1</code> Puntos que pican y rebotan pueden ser detectadas y mostradas: </li>
</ul>
<p align="center">
  <kbd>
  <img width=500 src="https://github.com/ArtLabss/tennis-tracking/blob/a6f395716dc5a076bfb2fc49f97db96a2004efed/VideoOutput/9bounces.gif">
  </kbd>
</p>


<p>
  Este Modelo predice: Verdaderos negativos (sin rebotar) con una precisión de hasta un: <strong>98%</strong> Porciento de los Verdaderos Positivos (Rebotadas) con un: <strong>83%</strong>.
</p>


 
<h3>Repositorios de Ayuda / Consulta:</h3>
<ul>
  <li><a href="https://github.com/MaximeBataille/tennis_tracking">Tennis Tracking</a> @MaximeBataille</li>
  <li><a href="https://github.com/avivcaspi/TennisProject">Tennis Project</a> @avivcaspi</li>
  <li><a href="https://nol.cs.nctu.edu.tw:234/open-source/TrackNet/tree/master/Code_Python3">TrackNet</a></li>
</ul>

<h1>EJEMPLO de sintetización descriptiva del video:</h1>
<p>Inicio del Juego (0:00-0:03):

El juego comienza con un saque del equipo de la izquierda (jugador de camiseta amarilla y su compañera).

El jugador de amarillo golpea la pelota, la cual rebota en el suelo y va al lado contrario.

La jugadora del equipo de la derecha intenta devolverla con un golpe, pero la pelota termina saliendo de la cancha.

El punto va para el equipo de la izquierda.

Intercambio de puntos y movimientos (0:03-0:32):

El juego sigue con varios intercambios rápidos, donde ambos equipos intentan colocar la pelota estratégicamente.

Se pueden ver golpes cruzados, voleas cerca de la red y algunos intentos de remate.

Se aprecia un buen nivel de habilidad en la manipulación de la pelota y agilidad en los movimientos de ambos equipos.

En varias ocasiones, se pueden ver golpes con muy poca altura sobre la red, exigiendo movimientos rápidos por parte de los jugadores.

Continuación del juego (0:32-1:01):

Los equipos siguen alternándose puntos y se pueden ver jugadas de gran intensidad.

Se observan algunos saques que resultan en puntos directos.

En un punto, se ve a una jugadora del equipo de la derecha dar un salto para darle a la pelota lo que hace mas dinamico y llamativo el juego.

Ambos equipos muestran la importancia de trabajar en equipo para cubrir bien los espacios.

Los movimientos rápidos de ambos equipos demuestran que es un juego de mucha agilidad.

Fase final del partido (1:01-1:34):

Los jugadores muestran un poco de cansancio pero siguen dando lo mejor de si mismos.

Hay algunos intercambios largos donde la pelota pasa varias veces de un lado al otro de la red antes de que un equipo gane el punto.

Un jugador del equipo de la izquierda da un giro muy vistoso con el que impacta la pelota.

El partido sigue muy igualado con varios puntos de gran calidad por parte de ambos equipos.

Se ven jugadas mas cerradas a la red y se puede apreciar como la habilidad de los jugadores empieza a marcar diferencia.

El juego termina con un punto espectacular donde los jugadores de ambos equipos lucieron sus mejores habilidades.

Consideraciones Adicionales:

Ambiente: El partido se juega de noche, en una cancha iluminada con focos, lo que añade un toque especial a la atmósfera del juego.

Actitud: Los jugadores muestran una actitud de competencia y deportividad, disfrutando del juego y esforzándose al máximo.

</p>

