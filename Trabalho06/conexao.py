__author__ = 'Wilson Junior'

import MySQLdb as mysql
import os

class Persistencia:

    Conexao = "";
    Cursor = "";

    def __init__(self):
        self.Conexao = mysql.connect(host='localhost',db='belezainovada',user='root',passwd='wilson');
        self.Cursor = self.Conexao.cursor();


    def getBancos(self):
        self.Cursor.execute('select * from Servico');
        return self.Cursor.fetchall();

    def encerra_conexao(self):
        self.Conexao.close();


pers = Persistencia();
print(pers.getBancos())