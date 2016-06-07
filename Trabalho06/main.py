
import scipy.ndimage as nd
import scipy.misc as ms
import pytesser.pytesser as pyt
import wilsonpdi
import Som
import os

# CLASSE PRINCIPAL QUE EXECUTA O PROCESSO

class executar:

    # ASSIM QUE INICIALIZADA A CLASSE, O PROCESSO E EXECUTADO
    def __init__(self,caminho):
        imagem = nd.imread(caminho,1);

        x,y = imagem.shape;
        limiar = 180;

        # REALIZANDO UM PROCESSAMENTO NA IMAGEM # SEGMENTACAO
        pdi = wilsonpdi.wilsonpdi(limiar);


        for i in range(0,x):
            for j in range(0,y):
               imagem[i,j] = pdi.segmentacao_inspecao(imagem[i,j]);

        # SALVANDO A IMAGEM SEGMENTADA
        img = ms.toimage(imagem);
        #img.save("imagens/imagem02-segmentada.jpg");

        # BUSCANDO O TEXTO CONTIDO NA IMAGEM
        texto = pyt.image_to_string(img);
        print(texto);

        # SEPARANDO PALAVRAS CONTIDAS NO TEXTO RECEBIDO
        palavra = "";
        conjunto = [];
        tamanho = len(texto);
        for i in range(0,tamanho):
            letra = str(texto[i]);
            if(len(letra)==0 or letra.__eq__('.') or letra.__eq__(',') or letra.__eq__('-') or letra.__eq__(' ') or letra.__eq__('\n') or letra.__eq__(')') or letra.__eq__('(')):
                print(palavra);
                conjunto.append(palavra);
                palavra = "";
            else:
                palavra = palavra + letra;
                print("nao e palavra");

        # GARANTINDO QUE AS PALAVRAS ENCONTRADAS NAO SEJAM NULAS
        for k in conjunto:
            if not k:
                conjunto.remove(k);

        print(conjunto);

        # REPRODUZINDO AUDIO DE ACORDO COM A PALAVRA ENCONTRADA
        for z in conjunto:
            if(os.path.isfile("sons/"+str(z)+".wav")):
                audio = Som.Som("sons/"+str(z)+".wav");
                audio.play();




