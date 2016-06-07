__author__ = 'Wilson Junior'

from pybrain.tools.shortcuts import buildNetwork as build
from pybrain.supervised import BackpropTrainer as bpt
from pybrain.datasets import SupervisedDataSet as sds
from matplotlib import pyplot as plt
from scipy import rand
from numpy import sin

rede_neural = build(2,5,1);

dados = sds(2,1);
dados.addSample([0,0],0);
dados.addSample([0,1],1);
dados.addSample([1,0],1);
dados.addSample([1,1],1);

treinamento = bpt(rede_neural,dados,learningrate=0.2);

erro = [];
for epocas in range(0,1000):
    erro.append(treinamento.train());

dados2 = sds(2,1);
x = rand();
dados2.addSample([x,-x],sin(x));

treinamento.testOnData(dados2,verbose=True);

plt.plot(erro,'s--');
plt.show();

