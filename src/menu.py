import pygame
from colors import *

class MenuItem:
    def __init__(self, text, value, min_value=None, max_value=None, options=None, callback=None):
        self.text = text
        self.value = value
        self.min_value = min_value
        self.max_value = max_value
        self.options = options
        self.callback = callback
        self.selected = False
        self.editing = False
        
    def increase(self):
        if self.options:
            current_index = self.options.index(self.value)
            next_index = (current_index + 1) % len(self.options)
            self.value = self.options[next_index]
        elif self.max_value is not None:
            self.value = min(self.value + 1, self.max_value)
        
        if self.callback:
            self.callback(self.value)
            
    def decrease(self):
        if self.options:
            current_index = self.options.index(self.value)
            prev_index = (current_index - 1) % len(self.options)
            self.value = self.options[prev_index]
        elif self.min_value is not None:
            self.value = max(self.value - 1, self.min_value)
            
        if self.callback:
            self.callback(self.value)
    
    def draw(self, screen, x, y, font):
        color = YELLOW if self.selected else WHITE
        border_color = RED if self.editing else color
        
        # Draw item text
        text_surface = font.render(f"{self.text}: ", True, color)
        screen.blit(text_surface, (x, y))
        
        # Draw value with arrows
        value_text = str(self.value)
        value_surface = font.render(f"< {value_text} >", True, border_color)
        screen.blit(value_surface, (x + 250, y))
        
        return y + 40  # Return next y position

class Menu:
    def __init__(self, screen, options):
        self.screen = screen
        self.options = options
        self.width, self.height = screen.get_size()
        self.font = pygame.font.SysFont(None, 36)
        self.title_font = pygame.font.SysFont(None, 72)
        self.items = []
        self.selected_index = 0
        self.running = True
        self.game_started = False
        
        # Create menu items
        self.create_menu_items()
        
    def create_menu_items(self):
        # Grid size options
        def update_grid_width(value):
            self.options.grid_size = (value, self.options.grid_size[1])
            
        def update_grid_height(value):
            self.options.grid_size = (self.options.grid_size[0], value)
            
        self.items.append(MenuItem("Grid Width", self.options.grid_size[0], 10, 30, callback=update_grid_width))
        self.items.append(MenuItem("Grid Height", self.options.grid_size[1], 8, 20, callback=update_grid_height))
        
        # Cell size
        def update_cell_size(value):
            self.options.cell_size = value
            
        self.items.append(MenuItem("Cell Size", self.options.cell_size, 20, 60, options=[20, 30, 40, 50, 60], callback=update_cell_size))
        
        # Goal size
        def update_goal_size(value):
            self.options.goal_size = value
            
        self.items.append(MenuItem("Goal Size", self.options.goal_size, 2, 5, callback=update_goal_size))
        
        # Tile bank size
        def update_tile_bank_size(value):
            self.options.tile_bank_size = value
            
        self.items.append(MenuItem("Tile Bank Size", self.options.tile_bank_size, 1, 5, callback=update_tile_bank_size))
        
        # Tile replenish time
        def update_replenish_time(value):
            self.options.tile_replenish_time = value
            
        self.items.append(MenuItem("Tile Replenish Time (s)", self.options.tile_replenish_time, 1, 10, callback=update_replenish_time))
        
        # Game duration
        def update_game_duration(value):
            self.options.game_duration = value
            
        self.items.append(MenuItem("Game Duration (s)", self.options.game_duration, 60, 600, options=[60, 120, 180, 300, 600], callback=update_game_duration))
        
        # Ball speed
        def update_ball_speed(value):
            self.options.initial_ball_speed = value
            
        self.items.append(MenuItem("Ball Speed", self.options.initial_ball_speed, 0.1, 0.5, options=[0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5], callback=update_ball_speed))
        
        # Start game option
        self.items.append(MenuItem("START GAME", None))
        
        # Set first item as selected
        self.items[0].selected = True
        
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
                    
                # Navigation
                if event.key == pygame.K_UP:
                    self.items[self.selected_index].selected = False
                    self.selected_index = (self.selected_index - 1) % len(self.items)
                    self.items[self.selected_index].selected = True
                    
                elif event.key == pygame.K_DOWN:
                    self.items[self.selected_index].selected = False
                    self.selected_index = (self.selected_index + 1) % len(self.items)
                    self.items[self.selected_index].selected = True
                    
                # Value adjustment
                elif event.key == pygame.K_LEFT:
                    self.items[self.selected_index].decrease()
                    
                elif event.key == pygame.K_RIGHT:
                    self.items[self.selected_index].increase()
                    
                # Selection
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    # If START GAME is selected
                    if self.selected_index == len(self.items) - 1:
                        self.game_started = True
                        self.running = False
    
    def draw(self):
        # Clear screen
        self.screen.fill(BLACK)
        
        # Draw title
        title_surface = self.title_font.render("GAME OPTIONS", True, WHITE)
        title_rect = title_surface.get_rect(center=(self.width // 2, 50))
        self.screen.blit(title_surface, title_rect)
        
        # Draw instructions
        instructions = self.font.render("Use UP/DOWN to navigate, LEFT/RIGHT to change values", True, LIGHT_GRAY)
        instructions_rect = instructions.get_rect(center=(self.width // 2, 100))
        self.screen.blit(instructions, instructions_rect)
        
        # Draw menu items
        y = 150
        for item in self.items:
            y = item.draw(self.screen, self.width // 2 - 200, y, self.font)
            
        # Draw start game highlight if selected
        if self.selected_index == len(self.items) - 1:
            start_text = self.font.render("START GAME", True, YELLOW)
            text_rect = start_text.get_rect(center=(self.width // 2, y - 40))
            pygame.draw.rect(self.screen, RED, 
                            (text_rect.left - 10, text_rect.top - 5, 
                             text_rect.width + 20, text_rect.height + 10), 3)
        
        # Update display
        pygame.display.flip()
        
    def run(self):
        while self.running:
            self.handle_input()
            self.draw()
            pygame.time.delay(30)
            
        return self.game_started
