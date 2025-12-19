import sys
import os
import json
import pygame
import neat
from core.car import Car
from ui.visualizer import draw_network

FPS = 0

class NEATSimulation:
    def __init__(self):
        pygame.init()
        self.load_track()
        self.screen = pygame.display.set_mode(self.track_surface.get_size())
        pygame.display.set_caption("NEAT Car Racing - AI Training")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 20)
        self.cars = []
        self.nets = []
        self.genomes = []
        
        self.generation = 0
        self.max_fitness = 0
        
    def wait_for_start(self):
        waiting = True
        while waiting:
            self.screen.fill((0, 0, 0))
            # Draw track background for context
            self.screen.blit(self.track_surface, (0, 0))
            
            # Draw overlay
            overlay = pygame.Surface(self.screen.get_size())
            overlay.fill((0, 0, 0))
            overlay.set_alpha(150)
            self.screen.blit(overlay, (0, 0))
            
            text = self.font.render("Press SPACE to start training", True, (255, 255, 255))
            rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
            self.screen.blit(text, rect)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        waiting = False
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
            self.clock.tick(30)

    def load_track(self):
        track_path = os.path.join(os.getcwd(), "assets", "track.png")
        if not os.path.exists(track_path):
            print("Error: No track found! Run ui/map_editor.py first.")
            sys.exit(1)
        self.track_surface = pygame.image.load(track_path)
        
        pose_path = os.path.join(os.getcwd(), "assets", "start_pose.json")
        if not os.path.exists(pose_path):
            self.start_pose = {"x": 500, "y": 350, "angle_deg": 0}
        else:
            with open(pose_path, "r") as f:
                self.start_pose = json.load(f)
    
    def eval_genomes(self, genomes, config):
        self.generation += 1
        self.cars = []
        self.nets = []
        self.genomes = []
        self.config = config
        
        for genome_id, genome in genomes:
            car = Car(x=self.start_pose["x"], y=self.start_pose["y"], scale=0.03)
            car.angle = self.start_pose["angle_deg"]
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            genome.fitness = 0
            
            self.cars.append(car)
            self.nets.append(net)
            self.genomes.append(genome)
        
        self.run_generation()

        # Save best genome if it beats the record
        if self.genomes:
            current_best = max(self.genomes, key=lambda g: g.fitness)
            if current_best.fitness >= self.max_fitness:
                import pickle
                with open("best_genome.pkl", "wb") as f:
                    pickle.dump(current_best, f)
                print(f"  > Saved new best genome (Fitness: {current_best.fitness:.1f})")
    
    def run_generation(self):
        running = True
        frame_count = 0
        max_frames = 1000
        
        start_positions = [(c.x, c.y) for c in self.cars]
        car_history = [[] for _ in self.cars]
        
        while running and frame_count < max_frames:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
            
            alive_count = 0
            for i, car in enumerate(self.cars):
                if car.is_alive:
                    alive_count += 1
                    
                    inputs = [d / Car.MAX_SENSOR_DISTANCE for d in car.sensor_distances]
                    inputs.append(car.speed / 10.0)
                    
                    outputs = self.nets[i].activate(tuple(inputs))
                    car.apply_ai_control(outputs)
                    car.update(self.track_surface)
                    
                    self.genomes[i].fitness = car.distance_traveled * 0.1
                    
                    # Kill if stopped
                    if frame_count > 50 and car.speed < 0.5:
                        car.is_alive = False
                        self.genomes[i].fitness -= 5

                    # Kill if stagnated
                    if frame_count == 100:
                        dx = car.x - start_positions[i][0]
                        dy = car.y - start_positions[i][1]
                        if (dx**2 + dy**2)**0.5 < 50:
                            car.is_alive = False
                            self.genomes[i].fitness -= 10

                    # Kill if spinning (Donut Detector)
                    if frame_count % 60 == 0:
                        history = car_history[i]
                        history.append((car.x, car.y))
                        if len(history) > 2:
                            prev_x, prev_y = history[-3]
                            if ((car.x - prev_x)**2 + (car.y - prev_y)**2)**0.5 < 50:
                                car.is_alive = False
                                self.genomes[i].fitness -= 5
                    
                    if self.genomes[i].fitness > self.max_fitness:
                        self.max_fitness = self.genomes[i].fitness
            
            if alive_count == 0:
                running = False
            
            self.screen.blit(self.track_surface, (0, 0))
            
            for car in self.cars:
                if car.is_alive:
                    car.draw(self.screen, draw_sensors=True)
            
            info = [
                f"Generation: {self.generation}",
                f"Alive: {alive_count}/{len(self.cars)}",
                f"Frame: {frame_count}/{max_frames}",
                f"Max Fitness: {self.max_fitness:.1f}"
            ]
            
            for i, text in enumerate(info):
                surf = self.font.render(text, True, (255, 255, 255))
                self.screen.blit(surf, (10, 10 + i * 35))
            
            if self.genomes:
                best_genome = max(self.genomes, key=lambda g: g.fitness)
                draw_network(self.screen, self.config, best_genome, (self.screen.get_width() - 310, 10), (300, 200))

            pygame.display.flip()
            self.clock.tick(FPS)
            frame_count += 1

def run_neat(config_path):
    config = neat.Config(
        neat.DefaultGenome, neat.DefaultReproduction,
        neat.DefaultSpeciesSet, neat.DefaultStagnation,
        config_path
    )
    
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())
    
    simulation = NEATSimulation()
    simulation.wait_for_start()
    
    winner = population.run(simulation.eval_genomes, 50)
    
    print("\n✓ Training completed!")
    import pickle
    with open("best_genome.pkl", "wb") as f:
        pickle.dump(winner, f)
    print("Best genome saved to best_genome.pkl")


def main():
    config_path = os.path.join(os.getcwd(), "config", "neat-car.cfg")
    if not os.path.exists(config_path):
        print(f"Error: Config file not found at {config_path}")
        return 1
    
    run_neat(config_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
