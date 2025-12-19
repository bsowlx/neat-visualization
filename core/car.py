import os
import math
import pygame


class Car:
    SENSOR_ANGLES = [-60, -30, 0, 30, 60]
    MAX_SENSOR_DISTANCE = 200
    ROAD_COLOR = (130, 130, 130)
    
    def __init__(self, x: float = 0.0, y: float = 0.0, image_path: str | None = None, scale: float = 1.0):
        self.x = x
        self.y = y
        self.angle = 0.0
        self.speed = 2.0
        self.is_alive = True
        self.image_path = image_path
        self.scale = scale
        self.sensor_distances = [0.0] * len(self.SENSOR_ANGLES)
        self.distance_traveled = 0.0
        self._load_image()

    def _generate_fallback(self) -> pygame.Surface:
        w, h = 48, 24
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(surf, (220, 60, 60), (0, 0, w, h), border_radius=4)
        return surf

    def _load_image(self):
        if self.image_path and os.path.isfile(self.image_path):
            image = pygame.image.load(self.image_path).convert_alpha()
        else:
            default_path = os.path.join(os.getcwd(), "assets", "car.png")
            if os.path.isfile(default_path):
                image = pygame.image.load(default_path).convert_alpha()
            else:
                image = self._generate_fallback()

        if self.scale != 1.0:
            w = int(image.get_width() * self.scale)
            h = int(image.get_height() * self.scale)
            image = pygame.transform.smoothscale(image, (w, h))
        self.base_image = image

    def get_image_and_rect(self, center_pos: tuple[int, int]) -> tuple[pygame.Surface, pygame.Rect]:
        rotated = pygame.transform.rotate(self.base_image, -self.angle)
        rect = rotated.get_rect(center=center_pos)
        return rotated, rect

    def get_corners(self):
        """Get the four corner positions of the car for collision detection"""
        img_width = self.base_image.get_width()
        img_height = self.base_image.get_height()
        
        #shrink the hitbox
        shrink_factor = 0.4
        half_w = (img_width / 2) * shrink_factor
        half_h = (img_height / 2) * shrink_factor
        
        angle_rad = math.radians(self.angle)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        
        corners = [
            (-half_w, -half_h),
            (half_w, -half_h),
            (half_w, half_h),
            (-half_w, half_h)
        ]
        
        rotated_corners = []
        for cx, cy in corners:
            rx = cx * cos_a - cy * sin_a + self.x
            ry = cx * sin_a + cy * cos_a + self.y
            rotated_corners.append((rx, ry))
        
        return rotated_corners
    
    def cast_sensor(self, sensor_angle: float, track_surface: pygame.Surface) -> float:
        """Cast a ray from the car in the sensor direction and return distance to wall"""
        absolute_angle = self.angle + sensor_angle
        angle_rad = math.radians(absolute_angle)
        
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        
        for distance in range(1, self.MAX_SENSOR_DISTANCE):
            x = self.x + cos_a * distance
            y = self.y + sin_a * distance
            
            ix, iy = int(x), int(y)
            
            if ix < 0 or iy < 0 or ix >= track_surface.get_width() or iy >= track_surface.get_height():
                return distance
            
            r, g, b, *_ = track_surface.get_at((ix, iy))
            if (r, g, b) != self.ROAD_COLOR:
                return distance
        
        return self.MAX_SENSOR_DISTANCE
    
    def check_collision(self, track_surface: pygame.Surface):
        """Check if any corner of the car is off the road"""
        corners = self.get_corners()
        
        for cx, cy in corners:
            ix, iy = int(cx), int(cy)
            
            if ix < 0 or iy < 0 or ix >= track_surface.get_width() or iy >= track_surface.get_height():
                self.is_alive = False
                return
            
            r, g, b, *_ = track_surface.get_at((ix, iy))
            if (r, g, b) != self.ROAD_COLOR:
                self.is_alive = False
                return
    
    def update(self, track_surface: pygame.Surface | None = None):
        if self.is_alive:
            angle_rad = math.radians(self.angle)
            self.x += math.cos(angle_rad) * self.speed
            self.y += math.sin(angle_rad) * self.speed
            self.distance_traveled += abs(self.speed)
            
            if track_surface:
                for i, sensor_angle in enumerate(self.SENSOR_ANGLES):
                    self.sensor_distances[i] = self.cast_sensor(sensor_angle, track_surface)
                
                self.check_collision(track_surface)
    
    def apply_ai_control(self, outputs: tuple[float, ...]):
        if not self.is_alive:
            return
        
        # Steering
        if outputs[0] > 0.5: self.angle -= 3
        if outputs[1] > 0.5: self.angle += 3
        self.angle %= 360
        
        # Speed control
        if outputs[2] > 0.5: self.speed = min(self.speed + 0.2, 8.0)
        if outputs[3] > 0.5: self.speed = max(self.speed - 0.2, 0.0)
            
        # Friction
        if outputs[2] <= 0.5 and outputs[3] <= 0.5:
            self.speed = max(self.speed - 0.02, 0)
    
    def steer(self, direction: str):
        if self.is_alive and abs(self.speed) > 0.5:
            if direction == 'left':
                self.angle -= 3
            elif direction == 'right':
                self.angle += 3
            self.angle %= 360
    
    def draw(self, surface: pygame.Surface, center_pos: tuple[int, int] | None = None, tint: tuple[int, int, int] | None = None, draw_sensors: bool = False):
        if not self.is_alive:
            return
        
        if center_pos is None:
            center_pos = (int(self.x), int(self.y))
        
        if draw_sensors:
            for i, sensor_angle in enumerate(self.SENSOR_ANGLES):
                absolute_angle = self.angle + sensor_angle
                angle_rad = math.radians(absolute_angle)
                distance = self.sensor_distances[i]
                
                end_x = self.x + math.cos(angle_rad) * distance
                end_y = self.y + math.sin(angle_rad) * distance
                
                color = (0, 255, 0) if distance > 50 else (255, 255, 0) if distance > 20 else (255, 0, 0)
                pygame.draw.line(surface, color, (int(self.x), int(self.y)), (int(end_x), int(end_y)), 2)
                pygame.draw.circle(surface, color, (int(end_x), int(end_y)), 3)
        
        img, rect = self.get_image_and_rect(center_pos)
        if tint:
            overlay = pygame.Surface(img.get_size(), pygame.SRCALPHA)
            overlay.fill((*tint, 80))
            img = img.copy()
            img.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        surface.blit(img, rect)
