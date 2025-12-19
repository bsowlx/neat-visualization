import pygame
from render.colors import Color

class NodeType:
    INPUT = 0
    HIDDEN = 1
    OUTPUT = 2

class Node:
    RADIUS = 15
    SPACING = 5
    LAYER_SPACING = 80
    CONNECTION_WIDTH = 2
    FONT = None  # Initialized later

    def __init__(self, id: int, x: int, y: int, type: int, colors: list, label: str = "", index: int = 0):
        self.id = id
        self.x = x
        self.y = y
        self.type = type
        self.colors = colors
        self.label = label
        self.index = index
        self.inputs = [0, 0, 0, 0, 0, 0] # 6 inputs now (5 sensors + speed)
        self.output = None
        
        if Node.FONT is None:
            Node.FONT = pygame.font.SysFont("comicsans", 15)

    def draw(self, screen: pygame.Surface):
        color_scheme = self.get_color()

        pygame.draw.circle(screen, color_scheme[0], (self.x, self.y), Node.RADIUS)
        pygame.draw.circle(screen, color_scheme[1], (self.x, self.y), Node.RADIUS - 2)

        if self.type != NodeType.HIDDEN:
            text = Node.FONT.render(self.label, 1, Color.BLACK)
            # Adjust text position based on type
            if self.type == NodeType.INPUT:
                text_x = self.x - Node.RADIUS - 5 - text.get_width()
            else:
                text_x = self.x + Node.RADIUS + 5
                
            screen.blit(text, (text_x, self.y - text.get_height()/2))

    def get_color(self):
        # Simplified color logic for now to avoid index errors
        # Just return the primary colors passed in
        if self.type == NodeType.INPUT:
            return [self.colors[1], self.colors[0]] # Darker border, lighter center
        elif self.type == NodeType.OUTPUT:
            return [self.colors[1], self.colors[0]]
        else:
            return [self.colors[1], self.colors[0]]

class Connection:
    def __init__(self, input_node, output_node, wt):
        self.input = input_node
        self.output = output_node
        self.wt = wt

    def draw(self, screen):
        color = Color.GREEN if self.wt >= 0 else Color.RED
        width = max(1, int(abs(self.wt * Node.CONNECTION_WIDTH)))
        pygame.draw.line(screen, color, (self.input.x + Node.RADIUS, self.input.y), 
                         (self.output.x - Node.RADIUS, self.output.y), width)
