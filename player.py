from multiprocessing.connection import Client
import traceback
import pygame
import sys, os

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255,255,0)
GREEN = (0,255,0)
X = 0
Y = 1
SIZE = (700, 525)

GOALKEEPER = 0
SHOOTER = 1

class Player():
	def __init__(self, tipo):
		self.size = size
		self.pos = None # Una se fija
		self.tipo = tipo
		
	def get_pos(self):
	
	def get_size(self):
	
	def set_pos(self):
	
	def __str__(self):
	
class Ball(): # solo se mueve en linea recta
	def __init__(self):
	
	def get_pos(self):
	
	def set_pos(self):
	
	def __str__(self):
