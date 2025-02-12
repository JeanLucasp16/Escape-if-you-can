import pygame
import random
import os
import time

# Inicialização do Pygame
pygame.init()

# Configurações da tela
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 450
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
obstacle_images = {
    1: [
        pygame.transform.scale(pygame.image.load(os.path.join("assets", "obstacle.png")), (50, 50)),
        pygame.transform.scale(pygame.image.load(os.path.join("assets", "knife.png")), (50, 50))
    ],
    2: [
        pygame.transform.scale(pygame.image.load(os.path.join("assets", "ball.png")), (50, 50)),
        pygame.transform.scale(pygame.image.load(os.path.join("assets", "cactus.png")), (50, 50))
    ]
}
backgrounds = {
    1: pygame.transform.scale(pygame.image.load(os.path.join("assets", "background.png")),
                              (SCREEN_WIDTH, SCREEN_HEIGHT)),
    2: pygame.transform.scale(pygame.image.load(os.path.join("assets", "level2.png")), (SCREEN_WIDTH, SCREEN_HEIGHT))
}
menu_background = pygame.transform.scale(pygame.image.load(os.path.join("assets", "backgroundFT.png")),
                                         (SCREEN_WIDTH, SCREEN_HEIGHT))

# Músicas e efeitos sonoros
pygame.mixer.music.load(os.path.join("assets", "menumusic.mp3"))
game_music = os.path.join("assets", "gamemusic.mp3")
collision_sound = pygame.mixer.Sound(os.path.join("assets", "collision.mp3"))

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
        self.image = pygame.transform.scale(player_image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.health = 100
        self.invincible = False

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT]:
            self.rect.x += 5

        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)

    def take_damage(self):
        if not self.invincible:
            self.health -= 25
            self.invincible = True
            pygame.time.set_timer(pygame.USEREVENT + 2, 1000)  # 1s de invencibilidade


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, speed, image):
        super().__init__()
        self.image = image
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

    if rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, RED, rect)
        if clicked:
            action = True
    else:
        pygame.draw.rect(screen, RED, rect, 2)

    font = pygame.font.SysFont(None, 50)
    text_surf = font.render(text, True, WHITE)
    screen.blit(text_surf, text_surf.get_rect(center=rect.center))
    return action


def show_main_menu():
    pygame.mixer.music.play(-1)
    while True:
        screen.blit(menu_background, (0, 0))

        title_font = pygame.font.SysFont(None, 100)
        title_text = title_font.render("Space Panda", True, WHITE)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))

        new_game_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 300, 200, 50)
        score_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 380, 200, 50)

        if draw_button("New Game", new_game_rect):
            pygame.mixer.music.stop()
            return 'new_game'
        if draw_button("High Scores", score_rect):
            show_high_scores()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return 'quit'

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


def show_level_transition(level):
    screen.fill(BLACK)
    show_text(f"LEVEL {level}", YELLOW)
    pygame.display.flip()
    time.sleep(2)


def show_end_screen(message, color, score):
    screen.fill(BLACK)
    show_text(message, color)
    show_text(f"Pontuação Total: {score}", WHITE, 100, 50)
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


def save_score(score):
    global high_scores
    high_scores.append(score)
    high_scores.sort(reverse=True)
    high_scores = high_scores[:3]  # Mantém apenas os 3 melhores scores


# =============================================
# Função Principal do Jogo - CORRIGIDA
# =============================================
def game_loop(level, total_score=0):
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
    double_obstacles = False
    extra_obstacle_added = False

    while running:
        elapsed_time = time.time() - start_time

        if elapsed_time >= level_duration:
            pygame.mixer.music.stop()
            return 'win', int(score + total_score)

        # Lógica específica do Level 2
        if level == 2:
            if elapsed_time >= 15 and not extra_obstacle_added:
                pygame.time.set_timer(spawn_obstacle_event, 500)
                extra_obstacle_added = True
                obstacle_speed += 3  # Aumenta velocidade adicional

        obstacle_speed = 5 + (elapsed_time // 5)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                return 'quit', 0

            if event.type == spawn_obstacle_event:
                # Spawn de obstáculos baseado no nível
                img1 = obstacle_images[level][0]
                img2 = obstacle_images[level][1]

                all_sprites.add(Obstacle(obstacle_speed, img1))
                all_sprites.add(Obstacle(obstacle_speed, img2))

            if event.type == pygame.USEREVENT + 2:
                player.invincible = False

        all_sprites.update()

        # Verificar colisões
        collisions = pygame.sprite.spritecollide(player, obstacles, True)
        if collisions:
            collision_sound.play()  # Toca o som de colisão
            player.take_damage()  # Reduz a vida do jogador

            if player.health <= 0:
                pygame.mixer.music.stop()
                return 'lose', int(score + total_score)

        score = int(elapsed_time * 10)

        screen.blit(backgrounds[level], (0, 0))
        all_sprites.draw(screen)

        font = pygame.font.SysFont(None, 55)
        texts = [
            f"Tempo: {int(level_duration - elapsed_time)}",
            f"Pontuação: {score + total_score}",
            f"Vida: {player.health}%",
            f"Level: {level}"
        ]

        for i, text in enumerate(texts):
            screen.blit(font.render(text, True, WHITE), (10, 10 + i * 50))

        pygame.display.flip()
        clock.tick(60)

    return 'quit', 0


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
            show_level_transition(1)
            result, score = game_loop(1)

            if result == 'win':
                show_level_transition(2)
                result, total_score = game_loop(2, score)

            if result in ['quit', 'lose']:
                save_score(total_score)  # Salva a pontuação
                show_end_screen("GAME OVER" if result == 'lose' else "VITÓRIA!", RED, total_score)

            if result == 'quit':
                break

    pygame.quit()


if __name__ == "__main__":
    main()