import neat
import pygame
from render.neural_network.node import Node, Connection, NodeType
from render.colors import Color

class NN:
    INPUT_NEURONS = 6 # 5 Sensors + Speed
    OUTPUT_NEURONS = 4

    def __init__(self, config: neat.Config, genome: neat.DefaultGenome, pos: tuple):
        self.nodes = []
        self.genome = genome
        self.pos = (int(pos[0]+Node.RADIUS), int(pos[1]))
        
        input_names = ["-60°", "-30°", "0°", "+30°", "+60°", "Speed"]
        output_names = ["Left", "Right", "Accel", "Brake"]
        
        hidden_nodes = [n for n in genome.nodes.keys() if n not in config.genome_config.input_keys and n not in config.genome_config.output_keys]
        node_map = {} # Map ID to Node object

        # Input Nodes
        h_input = (NN.INPUT_NEURONS-1)*(Node.RADIUS*2 + Node.SPACING)
        for i, input_key in enumerate(config.genome_config.input_keys):
            # Ensure we don't go out of bounds if config has more inputs than names
            label = input_names[i] if i < len(input_names) else f"In {i}"
            
            n = Node(input_key, pos[0], pos[1]+int(-h_input/2 + i*(Node.RADIUS*2 + Node.SPACING)), 
                     NodeType.INPUT, 
                     [Color.GREEN_PALE, Color.GREEN, Color.DARK_GREEN_PALE, Color.DARK_GREEN], 
                     label, i)
            self.nodes.append(n)
            node_map[input_key] = n

        # Output Nodes
        h_output = (NN.OUTPUT_NEURONS-1)*(Node.RADIUS*2 + Node.SPACING)
        for i, out_key in enumerate(config.genome_config.output_keys):
            label = output_names[i] if i < len(output_names) else f"Out {i}"
            
            n = Node(out_key, pos[0] + 2*(Node.LAYER_SPACING+2*Node.RADIUS), 
                     pos[1]+int(-h_output/2 + i*(Node.RADIUS*2 + Node.SPACING)), 
                     NodeType.OUTPUT, 
                     [Color.RED_PALE, Color.RED, Color.DARK_RED_PALE, Color.DARK_RED], 
                     label, i)
            self.nodes.append(n)
            node_map[out_key] = n

        # Hidden Nodes
        if hidden_nodes:
            h_hidden = (len(hidden_nodes)-1)*(Node.RADIUS*2 + Node.SPACING)
            for i, m in enumerate(hidden_nodes):
                n = Node(m, self.pos[0] + (Node.LAYER_SPACING+2*Node.RADIUS), 
                         self.pos[1]+int(-h_hidden/2 + i*(Node.RADIUS*2 + Node.SPACING)), 
                         NodeType.HIDDEN, 
                         [Color.BLUE_PALE, Color.DARK_BLUE, Color.BLUE_PALE, Color.DARK_BLUE])
                self.nodes.append(n)
                node_map[m] = n

        # Connections
        self.connections = []
        for c in genome.connections.values():
            if c.enabled:
                input_key, output_key = c.key
                
                if input_key in node_map and output_key in node_map:
                    self.connections.append(Connection(node_map[input_key], node_map[output_key], c.weight))

    def draw(self, screen: pygame.Surface):
        # Draw background for network
        # Calculate bounds
        min_x = min(n.x for n in self.nodes) - Node.RADIUS - 60
        max_x = max(n.x for n in self.nodes) + Node.RADIUS + 60
        min_y = min(n.y for n in self.nodes) - Node.RADIUS - 20
        max_y = max(n.y for n in self.nodes) + Node.RADIUS + 20
        
        width = max_x - min_x
        height = max_y - min_y
        
        # Draw white panel
        panel = pygame.Surface((width, height), pygame.SRCALPHA)
        panel.fill((255, 255, 255, 230)) # White with slight transparency
        pygame.draw.rect(panel, (200, 200, 200), (0, 0, width, height), 2) # Border
        screen.blit(panel, (min_x, min_y))

        for c in self.connections:
            c.draw(screen)
        for node in self.nodes:
            node.draw(screen)
