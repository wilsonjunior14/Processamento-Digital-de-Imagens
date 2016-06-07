__author__ = 'Wilson Junior'


class wilsonpdi:
    limiar=0;

    def __init__(self,l):
        self.limiar = l;

    def segmentacao_inspecao(self,valor_entrada):
        if(valor_entrada > self.limiar):
            return 255;
        else:
            return 0;


