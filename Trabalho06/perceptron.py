__author__ = 'Wilson Junior'

import numpy as np
import scipy as sc
import matplotlib.pyplot as plt


entrada = [(0,0),(0,1),(1,0),(1,1)];
entrada = np.matrix(entrada);

desejado = [0,0,0,1];
desejado = np.matrix(desejado);

w1 = sc.rand();
w2 = sc.rand();
bias = sc.rand();
taxa_aprendizagem = 0.2;
e = [];

for k in range(0,100):
    for i in range(0,4):
        y = (entrada[i,0]*w1 + entrada[i,1]*w2) + bias;
        if(y>0):
            y = 1;
        else:
            y = 0;
        erro = desejado[0,i] - y;
        e.append(erro);
        bias = bias + taxa_aprendizagem*erro;
        w1 = w1 + entrada[i,0]*taxa_aprendizagem*erro;
        w2 = w2 + entrada[i,1]*taxa_aprendizagem*erro;
        print(erro);

print("Valor de w1 = "+str(w1)+"");
print("Valor de w2 = "+str(w2)+"");
print("Bias = "+str(bias));
print(e)

plt.plot(e);
plt.show();