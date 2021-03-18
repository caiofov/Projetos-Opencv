#obter frames de um video a cada 5 segundos

import cv2 #importar o OpenCV
import salvar_frames as SF #importar o arquivo da função


video = cv2.VideoCapture("video.mp4")
#Tambem funciona com outros links/diretorios:
#https://file-examples-com.github.io/uploads/2017/04/file_example_MP4_640_3MG.mp4
#rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov


SF.salvar_frames(video,5)






