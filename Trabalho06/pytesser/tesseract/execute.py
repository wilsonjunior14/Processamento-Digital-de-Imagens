__author__ = 'Wilson Junior'

from pytesser.pytesser import image_to_string
import scipy.ndimage as nd
import pylab as py
import scipy.misc as ms


imagem = nd.imread("imagem02.jpg",1);

img_bin = ms.toimage(imagem);

texto = image_to_string(img_bin);

print(texto[1]);