import cv2 #importar o OpenCV


def salvar_frames(video, seg):
    #parametros:
    '''
    video : video recebido que irá ter os frames salvos
    seg: intervalo de segundos que o usuário quer os frames salvos
    '''

    #algumas variaveis...
    Sucess = True #variavel que ira verificar se o video chegou ao fim
    frame_count = 0 #variavel de apoio que ira contar quantas vezes o loop de captura foi executado
    
    #obter o FPS do video para saber de quantos em quantos frames deveremos salvar a imagem
    fps = int(video.get(cv2.CAP_PROP_FPS))
    #como usaremos esse dado para operações inteiras, fiz um casting para inteiro

    #loop de captura do video
    while Sucess: 
        Sucess, frame = video.read() #ira ler cada frame do video e armazenar na variavel "frame"

        #se o frame for lido corretamente
        
        '''
        Se dividirmos o numero do frame atual pelo FPS, obteremos em qual segundo o video está
        Se os segundos forem um multiplo de "seg", deveremos salvar este frame na pasta
        '''
        if frame_count>0 and (frame_count/fps)%seg==0:
            #definindo um nome para o arquivo
            nome_arq = "frame"+str(frame_count)+".png"
            
            #salvando o frame
            cv2.imwrite(nome_arq,frame)

        #caso o video tenha acabado, encerrara o loop

        frame_count+=1 #incrementar

