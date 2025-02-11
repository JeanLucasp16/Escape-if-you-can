import pygame
import random
import os
import time

# Inicialização do Pygame
pygame.init()

# Configurações da tela
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Esquiva de Obstáculos")

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Carregar assets
player_image = pygame.image.load(os.path.join("assets", "player.png"))
obstacle_image = pygame.image.load(os.path.join("assets", "obstacle.png"))
background_image = pygame.image.load(os.path.join("assets", "background.png"))
menu_background = pygame.image.load(os.path.join("assets", "backgroundFT.png"))

# Redimensionar imagens
player_image = pygame.transform.scale(player_image, (50, 50))
obstacle_image = pygame.transform.scale(obstacle_image, (50, 50))
menu_background = pygame.transform.scale(menu_background, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Músicas e efeitos sonoros
pygame.mixer.music.load(os.path.join("assets", "menumusic.mp3"))  # Música do menu
game_music = os.path.join("assets", "gamemusic.mp3")  # Música do jogo
collision_sound = pygame.mixer.Sound(os.path.join("assets", "collision.mp3"))  # Efeito de colisão

# Clock para controle de FPS
clock = pygame.time.Clock()

# Variáveis globais
high_scores = [0, 0, 0]


# =============================================
# Classes do Jogo
# =============================================
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.health = 100  # Vida inicial
        self.invincible = False  # Estado de invencibilidade

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT]:
            self.rect.x += 5

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def take_damage(self):
        if not self.invincible:
            self.health -= 25
            self.invincible = True
            pygame.time.set_timer(pygame.USEREVENT + 2, 1000)  # 1s de invencibilidade


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = obstacle_image
        self.rect = self.image.get_rect()

        if self.rect.width > SCREEN_WIDTH:
            self.image = pygame.transform.scale(self.image, (SCREEN_WIDTH, self.rect.height))
            self.rect = self.image.get_rect()

        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = -self.rect.height
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


# =============================================
# Funções para Telas e Menus
# =============================================
def draw_button(text, rect):
    mouse_pos = pygame.mouse.get_pos()
    clicked = pygame.mouse.get_pressed()[0]
    action = False

    # Efeito hover
    if rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, YELLOW, rect)
        if clicked:
            action = True
    else:
        pygame.draw.rect(screen, RED, rect, 2)

    # Texto do botão
    font = pygame.font.SysFont(None, 50)
    text_surf = font.render(text, True, RED)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)
    return action


def show_main_menu():
    pygame.mixer.music.play(-1)  # Toca a música do menu em loop
    while True:
        screen.blit(menu_background, (0, 0))

        # Título
        title_font = pygame.font.SysFont(None, 100)
        title_text = title_font.render("Space Panda", True, WHITE)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))

        # Botões
        new_game_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 300, 200, 50)
        score_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 380, 200, 50)

        # Desenha botões e verifica cliques
        new_game_clicked = draw_button("New Game", new_game_rect)
        score_clicked = draw_button("High Scores", score_rect)

        # Processa eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return 'quit'

        # Verifica ações
        if new_game_clicked:
            pygame.mixer.music.stop()  # Para a música do menu
            return 'new_game'
        if score_clicked:
            show_high_scores()

        pygame.display.flip()
        clock.tick(60)


def show_high_scores():
    screen.fill(BLACK)
    show_text("HIGH SCORES", YELLOW, -100)

    # Exibe as pontuações salvas
    font = pygame.font.SysFont(None, 60)
    y = SCREEN_HEIGHT // 2 - 50

    for i, score in enumerate(high_scores):
        text = font.render(f"{i + 1}. {score}", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))
        y += 60

    back_rect = pygame.Rect(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT - 100, 150, 40)
    if draw_button("Back", back_rect):
        return

    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        clock.tick(60)


def show_text(text, color, y_offset=0, font_size=100):
    font = pygame.font.SysFont(None, font_size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + y_offset))
    screen.blit(text_surface, text_rect)


def show_end_screen(message, color, score):
    screen.fill(BLACK)
    show_text(message, color)
    show_text(f"Pontuação: {score}", WHITE, 100, 50)
    show_text("Pressione R para recomeçar ou Q para sair", WHITE, 200, 40)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return 'restart'
                elif event.key == pygame.K_q:
                    return 'quit'


# =============================================
# Função Principal do Jogo
# =============================================
def game_loop():
    pygame.mixer.music.load(game_music)
    pygame.mixer.music.play(-1)

    running = True
    start_time = time.time()
    level_duration = 30
    spawn_obstacle_event = pygame.USEREVENT + 1
    pygame.time.set_timer(spawn_obstacle_event, 1000)

    all_sprites = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)

    obstacle_speed = 5
    score = 0

    while running:
        elapsed_time = time.time() - start_time

        # Condição de vitória
        if elapsed_time >= level_duration:
            pygame.mixer.music.stop()
            return show_end_screen("VITÓRIA!", GREEN, score)

        # Aumento de dificuldade
        obstacle_speed = 5 + (elapsed_time // 5)

        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                return 'quit'

            if event.type == spawn_obstacle_event:
                obstacle = Obstacle(obstacle_speed)
                all_sprites.add(obstacle)
                obstacles.add(obstacle)

            # Resetar invencibilidade
            if event.type == pygame.USEREVENT + 2:
                player.invincible = False

        # Atualizações
        all_sprites.update()

        # Verificar colisões
        collisions = pygame.sprite.spritecollide(player, obstacles, True)
        if collisions:
            collision_sound.play()
            player.take_damage()

            # Condição de derrota
            if player.health <= 0:
                pygame.mixer.music.stop()
                return show_end_screen("GAME OVER", RED, score)

        # Atualizar pontuação
        score = int(elapsed_time * 10)

        # Desenhar elementos
        screen.blit(background_image, (0, 0))
        all_sprites.draw(screen)

        # UI
        font = pygame.font.SysFont(None, 55)
        time_text = font.render(f"Tempo: {int(level_duration - elapsed_time)}", True, WHITE)
        score_text = font.render(f"Pontuação: {score}", True, WHITE)
        health_text = font.render(f"Vida: {player.health}%", True, WHITE)

        screen.blit(time_text, (10, 10))
        screen.blit(score_text, (10, 60))
        screen.blit(health_text, (10, 110))

        pygame.display.flip()
        clock.tick(60)

    return 'quit'


# =============================================
# Loop Principal do Jogo
# =============================================
def main():
    global high_scores

    while True:
        action = show_main_menu()

        if action == 'quit':
            break
        elif action == 'new_game':
            result = game_loop()
            if result == 'quit':
                break

    pygame.quit()


if __name__ == "__main__":
    main()