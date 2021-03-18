
#importando as bibliotecas
import cv2
import numpy as np
import imutils

#Implementando um detector de movimento básico

class SingleMotionDetector:
	def __init__(self, acumMedia = 0.5):
        #armazenar a media acumulada
		self.acumMedia = acumMedia
        #quanto maior for a média acumulada, menos o background será levado em conta
        #quando for feito a média ponderada
        #Foi considerado o valor inicial como 0.5, pois, com esse valor, tanto o fundo (background) quanto
        #a camada mais a frente (foreground) terão a mesma "importancia" na média ponderada.
		#inicializar a variavel de backgroung
		self.background = None
	
	def update(self, frame): #recebe uma imagem e calcula a média ponderada
		if self.background is None: # se não houver backgroung, deverá ser inicializado como a imagem recebida na função
			self.background = frame.copy().astype("float")
			return #encerra a função

		#caso exista um background, executará esta parte da função:
        #calcula a média ponderada do backgroun com o frame, atualizando o background.
		cv2.accumulateWeighted(frame, self.background, self.acumMedia)

    
	def detect(self, frame, lVal=25): #detecta o movimento
        #calcula a diferença do background do o frame passado para a função para limitar a imagem resultada da diferença
		diferenca = cv2.absdiff(self.background.astype("uint8"), frame)
		limite = cv2.threshold(diferenca, lVal, 255, cv2.THRESH_BINARY)[1]
        #a variavel "lVal" é usada para demarcar o limite na função "threshold"
        
        #qualquer pixel que tenha uma diferença maior do que o "lVal", será alterado para branco.
        #se a diferença for menor ou igual ao "lVal", será alterado para preto.

        #aqui, faremos apenas um tratamento de imagem, removendo os ruidos.
		limite = cv2.erode(limite, None, iterations=2)
		limite= cv2.dilate(limite, None, iterations=2)

        #Agora, acharemos os contornos na imagem que foi limitada e inicializar os 
        #valores de minimo e máximo que correspondem às arestas dessa região. Esses valores serão as variáveis
        #que irão nos indicar onde está ocorrendo o movimento
       
		contornos = cv2.findContours(limite.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		contornos = imutils.grab_contours(contornos)
		(minX, minY) = (np.inf, np.inf)
		(maxX, maxY) = (-np.inf, -np.inf)

        
        #Por fim, precisamos indicar os valores para essas variáveis

        #se nenhum contorno for achado, irá retornar None
		if len(contornos) == 0:
			return None
		#Caso contrário, passaremos em um loop por cada contorno
		for cont in contornos:
            #calculando a região limitada pelos contornos e a usando para atualizar os
            #valores minimos e maximos da região
			(x, y, w, h) = cv2.boundingRect(cont)
			(minX, minY) = (min(minX, x), min(minY, y))
			(maxX, maxY) = (max(maxX, x + w), max(maxY, y + h))
		
        #então, retorna uma tupla da imagem que foi limitada com os valores da região
		return (limite, (minX, minY, maxX, maxY))
