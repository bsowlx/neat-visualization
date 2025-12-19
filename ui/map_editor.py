import sys
import os
import json
import pygame

from core.car import Car


WINDOW_SIZE = (1000, 700)
TOP_BAR_HEIGHT = 64
BACKGROUND_COLOR = (18, 18, 22)
ROAD_COLOR = (130, 130, 130)
ERASE_COLOR = (0, 0, 0)
UI_PANEL_COLOR = (30, 30, 34)
TEXT_COLOR = (220, 220, 220)
CLEAR_BUTTON_RECT = pygame.Rect(16, 12, 100, 40)
PROCEED_BUTTON_RECT = pygame.Rect(132, 12, 120, 40)
MIN_BRUSH = 30
MAX_BRUSH = 80
INITIAL_BRUSH = 35
ROTATE_STEP_DEG = 12
CAR_SCALE = 0.03


def draw_button(surface, rect, label, font, hovered, active=False):
    base = (50, 50, 56)
    hover = (70, 70, 78)
    active_color = (90, 140, 90)
    color = active_color if active else (hover if hovered else base)
    pygame.draw.rect(surface, color, rect, border_radius=6)
    text_surf = font.render(label, True, TEXT_COLOR)
    surface.blit(text_surf, text_surf.get_rect(center=rect.center))


def save_track(track_surface):
    path = os.path.join(os.getcwd(), "assets")
    os.makedirs(path, exist_ok=True)
    pygame.image.save(track_surface, os.path.join(path, "track.png"))


def save_start_pose(pos, angle_deg):
    path = os.path.join(os.getcwd(), "assets")
    os.makedirs(path, exist_ok=True)
    data = {"x": pos[0], "y": pos[1], "angle_deg": angle_deg}
    with open(os.path.join(path, "start_pose.json"), "w") as f:
        json.dump(data, f)


def is_on_road(point, track_surface):
    x, y = int(point[0]), int(point[1])
    if x < 0 or y < 0 or x >= track_surface.get_width() or y >= track_surface.get_height():
        return False
    r, g, b, *rest = track_surface.get_at((x, y))
    return (r, g, b) == ROAD_COLOR


def main():
    pygame.init()
    pygame.display.set_caption("Map Drawing Editor")
    screen = pygame.display.set_mode(WINDOW_SIZE)
    font = pygame.font.SysFont(None, 24)
    clock = pygame.time.Clock()

    track_surface = pygame.Surface(WINDOW_SIZE)
    track_surface.fill(ERASE_COLOR)

    brush_size = INITIAL_BRUSH
    left_down = False
    right_down = False
    mode = "draw"
    proceeded = False
    car = None
    car_angle = 0

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if mode == "draw":
                    if event.button == 1:
                        if CLEAR_BUTTON_RECT.collidepoint(mouse_pos):
                            track_surface.fill(ERASE_COLOR)
                        elif PROCEED_BUTTON_RECT.collidepoint(mouse_pos):
                            save_track(track_surface)
                            proceeded = True
                            mode = "place"
                            car = Car(os.path.join(os.getcwd(), "assets", "car.png"), scale=CAR_SCALE)
                            car_angle = 0
                        else:
                            left_down = True
                            pygame.draw.circle(track_surface, ROAD_COLOR, event.pos, brush_size)
                    elif event.button == 3:
                        right_down = True
                        pygame.draw.circle(track_surface, ERASE_COLOR, event.pos, brush_size)
                    elif event.button == 4:  # scroll up
                        brush_size = min(MAX_BRUSH, brush_size + 2)
                    elif event.button == 5:  # scroll down
                        brush_size = max(MIN_BRUSH, brush_size - 2)
                else:
                    if event.button == 1:
                        if mouse_pos[1] > TOP_BAR_HEIGHT and is_on_road(mouse_pos, track_surface):
                            save_start_pose(mouse_pos, car_angle)
                            running = False
                    elif event.button == 3:
                        mode = "draw"
                    elif event.button == 4:
                        car_angle = (car_angle + ROTATE_STEP_DEG) % 360
                    elif event.button == 5:
                        car_angle = (car_angle - ROTATE_STEP_DEG) % 360
            elif event.type == pygame.MOUSEBUTTONUP:
                if mode == "draw":
                    if event.button == 1:
                        left_down = False
                    elif event.button == 3:
                        right_down = False
            elif event.type == pygame.MOUSEMOTION:
                if mode == "draw":
                    if mouse_pos[1] > TOP_BAR_HEIGHT:  # avoid drawing over UI bar
                        if left_down:
                            pygame.draw.circle(track_surface, ROAD_COLOR, event.pos, brush_size)
                        elif right_down:
                            pygame.draw.circle(track_surface, ERASE_COLOR, event.pos, brush_size)
            elif event.type == pygame.KEYDOWN:
                if mode == "place":
                    if event.key in (pygame.K_q, pygame.K_a):
                        car_angle = (car_angle + ROTATE_STEP_DEG) % 360
                    elif event.key in (pygame.K_e, pygame.K_d):
                        car_angle = (car_angle - ROTATE_STEP_DEG) % 360
                    elif event.key == pygame.K_r:
                        car_angle = 0

        screen.fill(BACKGROUND_COLOR)
        screen.blit(track_surface, (0, 0))

        # Top bar overlay
        bar = pygame.Surface((WINDOW_SIZE[0], TOP_BAR_HEIGHT))
        bar.set_alpha(235)
        bar.fill(UI_PANEL_COLOR)

        # Buttons and info per mode
        if mode == "draw":
            clear_hover = CLEAR_BUTTON_RECT.collidepoint(mouse_pos)
            proceed_hover = PROCEED_BUTTON_RECT.collidepoint(mouse_pos)
            draw_button(bar, CLEAR_BUTTON_RECT, "Clear", font, clear_hover)
            draw_button(bar, PROCEED_BUTTON_RECT, "Proceed", font, proceed_hover, active=proceeded)

            info = f"Brush: {brush_size}px  LMB draw  RMB erase  Wheel resize"
            info_surf = font.render(info, True, TEXT_COLOR)
            bar.blit(info_surf, (280, 22))
        else:
            info = "Placement: LMB place (on road) | RMB back | Q/E or Wheel rotate | R reset"
            info_surf = font.render(info, True, TEXT_COLOR)
            bar.blit(info_surf, (16, 22))

        screen.blit(bar, (0, 0))

        if mode == "draw":
            # Preview cursor circle (semi-transparent) if in drawing area
            if mouse_pos[1] > TOP_BAR_HEIGHT:
                preview = pygame.Surface((brush_size * 2, brush_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(preview, (200, 200, 200, 60), (brush_size, brush_size), brush_size)
                screen.blit(preview, (mouse_pos[0] - brush_size, mouse_pos[1] - brush_size))
        else:
            if car:
                valid = mouse_pos[1] > TOP_BAR_HEIGHT and is_on_road(mouse_pos, track_surface)
                tint = (60, 200, 60) if valid else (200, 60, 60)
                car.angle = car_angle
                car.draw(screen, mouse_pos, tint=tint)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
