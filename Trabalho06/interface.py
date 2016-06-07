__author__ = 'Wilson Junior'
from Tkinter import *
import main
import tkFileDialog
import tkMessageBox
import os


class Interface:



    def __init__(self,obj):
        #ARQUIVO
        self.arquivo = "";

        # FRAME TOP
        self.frame = Frame();
        self.frame.pack();

        # FRAME CENTRO 1
        self.framecentro1 = Frame();
        self.framecentro1.pack();

        # FRAME BOTTOM
        self.framebottom = Frame();
        self.framebottom.pack();

        self.titulo = Label(self.frame,text='Processamento Digital de Imagens',foreground='red');
        self.titulo.pack(side=TOP);

        self.subtitulo = Label(self.frame,text='Reconhecimento Optico de Caracteres',foreground='red');
        self.subtitulo.pack();

        self.labelnome = Label(self.framecentro1,text='Caminho da imagem .:',foreground='white',background='black');
        self.labelnome.pack(side=LEFT);

        self.btimagem = Button(self.framecentro1,text='Carregar Imagem',foreground='white',background='black');
        self.btimagem['command'] = self.carrega_imagem;
        self.btimagem.pack();

        self.btprocessa = Button(self.framebottom,text='Processar Imagem',background='gray',foreground='black');
        self.btprocessa['command'] = self.processa_imagem;
        self.btprocessa.pack(side=TOP);

        self.footer = Label(self.framebottom,text='Engenharia da Computacao, UFC Sobral \n Wilson Junior');
        self.footer.pack();


    def processa_imagem(self):
        if(os.path.isfile(self.arquivo)):
            main.executar(self.arquivo);
        else:
            tkMessageBox.showerror("ARQUIVO INVALIDO !","ERRO");

    def carrega_imagem(self):
        self.arquivo = tkFileDialog.askopenfilename();
        print(self.arquivo);


interface = Tk();
inter = Interface(interface);
interface.mainloop();