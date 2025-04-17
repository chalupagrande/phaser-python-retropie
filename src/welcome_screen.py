import pygame
from colors import *

class WelcomeScreen:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.font = pygame.font.SysFont(None, 36)
        self.title_font = pygame.font.SysFont(None, 72)
        self.running = True
        self.selected_option = 0  # 0 = Start Game, 1 = Options
        self.result = None  # 'start' or 'options'
        
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
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    self.selected_option = 1 - self.selected_option  # Toggle between 0 and 1
                    
                # Selection
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if self.selected_option == 0:
                        self.result = 'start'
                    else:
                        self.result = 'options'
                    self.running = False
    
    def draw(self):
        # Clear screen
        self.screen.fill(BLACK)
        
        # Draw title
        title_surface = self.title_font.render("TILE STRATEGY GAME", True, WHITE)
        title_rect = title_surface.get_rect(center=(self.width // 2, self.height // 3))
        self.screen.blit(title_surface, title_rect)
        
        # Draw options
        start_color = YELLOW if self.selected_option == 0 else WHITE
        options_color = YELLOW if self.selected_option == 1 else WHITE
        
        start_text = self.font.render("START GAME", True, start_color)
        start_rect = start_text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(start_text, start_rect)
        
        if self.selected_option == 0:
            pygame.draw.rect(self.screen, RED, 
                           (start_rect.left - 10, start_rect.top - 5, 
                            start_rect.width + 20, start_rect.height + 10), 3)
        
        options_text = self.font.render("OPTIONS", True, options_color)
        options_rect = options_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
        self.screen.blit(options_text, options_rect)
        
        if self.selected_option == 1:
            pygame.draw.rect(self.screen, RED, 
                           (options_rect.left - 10, options_rect.top - 5, 
                            options_rect.width + 20, options_rect.height + 10), 3)
        
        # Draw instructions
        instructions = self.font.render("Use UP/DOWN to navigate, ENTER to select", True, LIGHT_GRAY)
        instructions_rect = instructions.get_rect(center=(self.width // 2, self.height * 3 // 4))
        self.screen.blit(instructions, instructions_rect)
        
        # Update display
        pygame.display.flip()
        
    def run(self):
        while self.running:
            self.handle_input()
            self.draw()
            pygame.time.delay(30)
            
        return self.result
