__author__ = 'Wilson Junior'

import winsound as sound
import time


class Som:
    audio = "";
    delay = "";

    def __init__(self,caminho):
        self.audio = caminho;


    def play(self):
        sound.PlaySound(self.audio,sound.SND_NODEFAULT);


