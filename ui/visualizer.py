import pygame
from render.neural_network.nn import NN

def draw_network(surface, config, genome, pos, size):
    adjusted_pos = (pos[0] + 10, pos[1] + 110)
    nn = NN(config, genome, adjusted_pos)
    
    # Draw
    nn.draw(surface)

