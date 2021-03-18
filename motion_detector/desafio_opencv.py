#https://www.pyimagesearch.com/2019/09/02/opencv-stream-video-to-web-browser-html-page/

#importando as bibliotecas
import numpy as np
import imutils
import cv2
from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template
import threading
import argparse
import datetime
import imutils
import time

import detector


#Combinando OpenCV com Flask - - - - -

#inicializar a variavel outputFrame e uma "lock", que garantirá trocas thread-safe
outputFrame = None
lock = threading.Lock()

#criando uma instancia flask
app = Flask(__name__)

#inicializar a stream de video
#video = VideoStream(src=0).start() -> acessa a webcam
#time.sleep(2.0)

#mudando para o video de um link
video = cv2.VideoCapture()
video.open("rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov")


@app.route("/")
def index():
	#retornar o template "index.html"
	return render_template("/tela_principal.html")


def detect_motion(frameCount): #"frameCount" é a quantidade mínima de frames para o background na SingleMotionDetector
	#chamar algumas variaveis globais
	global video, outputFrame, lock
	#inicializar o detector de movimento e o numero total de frames lidos ate o momento
	movdec = detector.SingleMotionDetector(acumMedia=0.1)
	total = 0

	Sucess = True #variavel que irá indicar quando o video terminar
	
	#loop que passará pelos frames do video
	while Sucess:
		#receber o proximo frame, redimensionar (para ocupar menos espaço na memória),
		#converter pra escala de cinza e embaçar (para reduzir o ruido)
		Sucess, frame = video.read()
		frame = imutils.resize(frame, width=400) #frame = cv2.resize(frame,(400,400))
		frame_cinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		frame_cinza = cv2.GaussianBlur(frame_cinza, (7, 7), 0)

		#escrever a hora e a data no frame
		hora_data = datetime.datetime.now()
		cv2.putText(frame, hora_data.strftime("%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
        
		#se o numero total de frames chegar a um numero suficiente, ou seja, maior do que o minimo,
		#entao, devemos continuar a processar o frame
		if total > frameCount:
			#detectar movimendo no frame
			mov = movdec.detect(frame_cinza)

			#conferir se foi achado algum movimento
			if mov is not None:
				#relacionar os valores da tupla retornada em "mov"
				#e desenhar um retangulo em volta da area onde foi detectado o movimento
				(limite, (minX, minY, maxX, maxY)) = mov
				cv2.rectangle(frame, (minX, minY), (maxX, maxY), (0, 0, 255), 2)
		
		#atualizar o background e incrementar o numero total de frames
		movdec.update(frame_cinza)
		total += 1

		#travar a thread, definir o "outputFrame" e destravar
		with lock:
			outputFrame = frame.copy()

def generate():
	#chamar algumas variaveis globais
	global outputFrame, lock

	#passar pelos frames 
	while True:
		#travar a thread
		with lock:
			#verificar de o frame do output existe. Se não existir, ira recomeçar o loop
			if outputFrame is None:
				continue

			#converter o frame para JPEG
			(flag, frame_jpeg) = cv2.imencode(".jpg", outputFrame)
			
			#certificar que a operação ocorreu corretamente
			if not flag:
				continue

		# retorna o frame do output em byte
		yield(b'--frame\r\n' b'Content-Type: frame/jpeg\r\n\r\n' + bytearray(frame_jpeg) + b'\r\n')

@app.route("/video_feed")
def video_feed():
	#retorna a Response gerada durante a mídia em formato mime
	return Response(generate(), mimetype = "multipart/x-mixed-replace; boundary=frame")


#verifica se essa é a main na execução
if __name__ == '__main__':
	#definir os argumentos do programa
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--ip", type=str, required=True, help="endereco ip do dispositivo")
	ap.add_argument("-o", "--port", type=int, required=True, help="numero da porta efemera do servidor (1024 a 65535)")
	ap.add_argument("-f", "--frame-count", type=int, default=32, help="numero de frames usardos na construcao do background")
	args = vars(ap.parse_args())
	
	#iniciar uma thread que irá executar a detecção de movimento
	thread = threading.Thread(target=detect_motion, args=(args["frame_count"],))
	thread.daemon = True
	thread.start()

	#iniciar o flask
	app.run(host=args["ip"], port=args["port"], debug=True, threaded=True, use_reloader=False)

#parar o video (não funciona para VideoCapture())
#video.stop()

