import sys
import os
import json
import pickle
import math
import pygame
import neat
from core.car import Car
from ui.visualizer import draw_network

class DemoRunner:
    def __init__(self):
        pygame.init()
        self.load_track()
        self.screen = pygame.display.set_mode(self.track_surface.get_size())
        pygame.display.set_caption("Turing Test: Human vs AI")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
    def load_track(self):
        track_path = os.path.join(os.getcwd(), "assets", "track.png")
        if not os.path.exists(track_path):
            print("Error: No track found! Run ui/map_editor.py first.")
            sys.exit(1)
        self.track_surface = pygame.image.load(track_path)
        
        pose_path = os.path.join(os.getcwd(), "assets", "start_pose.json")
        if not os.path.exists(pose_path):
            print("Warning: start_pose.json not found. Using default.")
            sys.exit(1)
        else:
            with open(pose_path, "r") as f:
                self.start_pose = json.load(f)

    def run(self):
        # Load Config
        config_path = os.path.join(os.getcwd(), "config", "neat-car.cfg")
        config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                             neat.DefaultSpeciesSet, neat.DefaultStagnation,
                             config_path)

        # Load Best Genome
        genome_path = "best_genome.pkl"
        if not os.path.exists(genome_path):
            print("Error: best_genome.pkl not found. Train the AI first!")
            return

        with open(genome_path, "rb") as f:
            genome = pickle.load(f)

        # Create Network and AI Car
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        ai_car = Car(x=self.start_pose["x"], y=self.start_pose["y"], scale=0.03)
        ai_car.angle = self.start_pose["angle_deg"]
        
        # Create Player Car
        player_car = Car(x=self.start_pose["x"], y=self.start_pose["y"], scale=0.03, image_path=os.path.join(os.getcwd(), "assets", "car.png"))
        player_car.angle = self.start_pose["angle_deg"]
        player_car.speed = 0
        
        running = True
        while running:
            # Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        # Reset both cars
                        ai_car = Car(x=self.start_pose["x"], y=self.start_pose["y"], scale=0.03)
                        ai_car.angle = self.start_pose["angle_deg"]
                        player_car = Car(x=self.start_pose["x"], y=self.start_pose["y"], scale=0.03, image_path=os.path.join(os.getcwd(), "assets", "car_player.png"))
                        player_car.angle = self.start_pose["angle_deg"]
                        player_car.speed = 0

            # Player Input
            keys = pygame.key.get_pressed()
            player_outputs = [
                1.0 if keys[pygame.K_LEFT] else 0.0,
                1.0 if keys[pygame.K_RIGHT] else 0.0,
                1.0 if keys[pygame.K_UP] else 0.0,
                1.0 if keys[pygame.K_DOWN] else 0.0
            ]
            
            if player_car.is_alive:
                player_car.apply_ai_control(player_outputs)
                player_car.update(self.track_surface)

            # AI Logic
            if ai_car.is_alive:
                inputs = [d / Car.MAX_SENSOR_DISTANCE for d in ai_car.sensor_distances]
                inputs.append(ai_car.speed / 10.0)
                outputs = net.activate(inputs)
                ai_car.apply_ai_control(outputs)
                ai_car.update(self.track_surface)

            # Drawing
            self.screen.blit(self.track_surface, (0, 0))
            
            if ai_car.is_alive:
                ai_car.draw(self.screen, draw_sensors=False)
                # Draw label
                label = self.font_small.render("AI", True, (255, 100, 100))
                self.screen.blit(label, (ai_car.x - 10, ai_car.y - 40))
            
            if player_car.is_alive:
                player_car.draw(self.screen, draw_sensors=False)
                # Draw label
                label = self.font_small.render("YOU", True, (100, 255, 100))
                self.screen.blit(label, (player_car.x - 15, player_car.y - 40))
            
            # UI Overlay
            overlay_text = [
                "TURING TEST: Human vs AI",
                f"AI Speed: {ai_car.speed:.1f}",
                f"Player Speed: {player_car.speed:.1f}",
                "Controls: Arrow Keys",
                "Press 'R' to Reset",
                "Press 'ESC' to Quit"
            ]
            
            # Status
            if not ai_car.is_alive and not player_car.is_alive:
                msg = "BOTH CRASHED"
                col = (255, 255, 255)
            elif not ai_car.is_alive:
                msg = "YOU WIN!"
                col = (0, 255, 0)
            elif not player_car.is_alive:
                msg = "AI WINS!"
                col = (255, 0, 0)
            else:
                msg = None
            
            if msg:
                text = self.font.render(msg, True, col)
                self.screen.blit(text, (self.screen.get_width()//2 - text.get_width()//2, 50))
            
            for i, line in enumerate(overlay_text):
                text = self.font_small.render(line, True, (255, 255, 255))
                pygame.draw.rect(self.screen, (0, 0, 0, 150), (10, 10 + i*30, text.get_width()+10, 25))
                self.screen.blit(text, (15, 15 + i*30))

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    DemoRunner().run()
