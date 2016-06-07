from pybrain.tools.validation import ModuleValidator

__author__ = 'Wilson Junior'

from pybrain.tools.shortcuts import buildNetwork as build
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised import BackpropTrainer as bpt
import matplotlib.pyplot as plt
from pybrain.structure import SigmoidLayer;
import scipy as sc


rede = build(2,2,1,bias=True,hiddenclass=SigmoidLayer);

dados = SupervisedDataSet(2,1);
dados.addSample([0,0],[0]);
dados.addSample([0,1],[1]);
dados.addSample([1,0],[10]);
dados.addSample([1,1],[0]);

treinamento = bpt(rede,dados,learningrate=sc.rand());

for epocas in range(0,10000):
   treinamento.trainOnDataset(dados);

dados2 = dados;

#treinamento.testOnData(dados2,verbose=True);
saida = treinamento.testOnData(dados2,verbose=True);
