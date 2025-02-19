import pygame
import random
import os
import time
import json

# Inicialização do Pygame
pygame.init()

# Configurações da tela
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Escape if you can")

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)

# Carregamento de assets
def load_image(path, size=(50, 50)):
    img = pygame.image.load(os.path.join("assets", path))
    if "laser.png" in path or "meteor.png" in path:  # Aumenta o tamanho apenas para imagens do nível 3
        size = (80, 80)  # Aumente conforme necessário
    return pygame.transform.scale(img, size)

player_image = load_image("player.png")
obstacle_images = {
    1: [load_image("obstacle.png"), load_image("knife.png")],
    2: [load_image("ball.png"), load_image("cactus.png")],
    3: [load_image("laser.png"), load_image("meteor.png")]
}
backgrounds = {
    1: load_image("background.png", (SCREEN_WIDTH, SCREEN_HEIGHT)),
    2: load_image("level2.png", (SCREEN_WIDTH, SCREEN_HEIGHT)),
    3: load_image("level3.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
}
menu_background = load_image("backgroundFT.png", (SCREEN_WIDTH, SCREEN_HEIGHT))

# Sons e música
pygame.mixer.music.load(os.path.join("assets", "menumusic.mp3"))
game_music = [os.path.join("assets", f"gamemusic_{i}.mp3") for i in range(1, 4)]  # Músicas diferentes para cada nível
collision_sound = pygame.mixer.Sound(os.path.join("assets", "collision.mp3"))


# Relógio para controle de FPS
clock = pygame.time.Clock()

# Variáveis globais
high_scores = []

# Funções para salvar e carregar scores
def save_scores(scores):
    with open("high_scores.json", "w") as file:
        json.dump(scores, file)

def load_scores():
    global high_scores
    try:
        with open("high_scores.json", "r") as file:
            high_scores = json.load(file)
    except FileNotFoundError:
        high_scores = []

# Carregar scores no início do jogo
load_scores()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.health = 100
        self.invincible = False
        self.invincible_time = 0
        self.speed = 5

    def update(self):
        keys = pygame.key.get_pressed()
        self.rect.x += (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * self.speed
        self.rect.clamp_ip(screen.get_rect())  # Mantém o jogador na tela

    def take_damage(self):
        if not self.invincible:
            self.health -= 25
            self.invincible = True
            self.invincible_time = pygame.time.get_ticks()

    def check_invincibility(self):
        if self.invincible and pygame.time.get_ticks() - self.invincible_time > 1000:
            self.invincible = False

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

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = -self.rect.height
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Funções de UI
def draw_button(text, rect, color=WHITE):
    mouse_pos = pygame.mouse.get_pos()
    clicked = pygame.mouse.get_pressed()[0]
    button_color = RED if rect.collidepoint(mouse_pos) else color
    pygame.draw.rect(screen, button_color, rect)
    font = pygame.font.SysFont(None, 50)
    text_surf = font.render(text, True, BLACK)
    screen.blit(text_surf, text_surf.get_rect(center=rect.center))
    return rect.collidepoint(mouse_pos) and clicked

def show_main_menu():
    pygame.mixer.music.play(-1)
    while True:
        screen.blit(menu_background, (0, 0))
        title_text = pygame.font.SysFont(None, 100).render("Escape if you can", True, WHITE)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))

        if draw_button("New Game", pygame.Rect(SCREEN_WIDTH // 2 - 100, 300, 200, 50)):
            pygame.mixer.music.stop()
            return 'new_game'
        if draw_button("High Scores", pygame.Rect(SCREEN_WIDTH // 2 - 100, 380, 200, 50)):
            return 'high_scores'

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return 'quit'

        pygame.display.flip()
        clock.tick(60)

def show_high_scores():
    while True:
        screen.fill(BLACK)
        show_text("HIGH SCORES", YELLOW, -100)

        font = pygame.font.SysFont(None, 30)
        y = SCREEN_HEIGHT // 2 - 50
        for i, score in enumerate(high_scores[:5]):  # Mostra os 5 melhores scores
            text = font.render(f"{i + 1}. {score['name']}: {score['score']}", True, WHITE)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))
            y += 40

        if draw_button("Back", pygame.Rect(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT - 100, 150, 40)):
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        pygame.display.flip()
        clock.tick(60)

def show_text(text, color, y_offset=0, font_size=50):
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
    show_text(f"Total Score: {score}", WHITE, 100, 30)
    show_text("Press R to restart or Q to quit", WHITE, 200, 30)
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

def get_player_name():
    name = ""
    while True:
        screen.fill(BLACK)
        show_text("Enter your name:", WHITE, -50, 30)
        show_text(name, YELLOW, 50, 30)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return name if name else "Player"
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    name += event.unicode

def save_score(score):
    global high_scores
    name = get_player_name()
    if name:
        high_scores.append({"name": name, "score": score})
        high_scores.sort(key=lambda x: x["score"], reverse=True)
        high_scores = high_scores[:5]  # Mantém apenas os 5 melhores scores
        save_scores(high_scores)

def game_loop(level, total_score=0):
    pygame.mixer.music.load(game_music[level - 1])
    pygame.mixer.music.play(-1)

    all_sprites = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    powerups = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)

    obstacle_speed = 5
    score = 0
    spawn_obstacle_event = pygame.USEREVENT + 1
    spawn_powerup_event = pygame.USEREVENT + 2
    pygame.time.set_timer(spawn_obstacle_event, random.randint(800, 1500))
    pygame.time.set_timer(spawn_powerup_event, random.randint(5000, 10000))

    start_time = pygame.time.get_ticks()
    level_duration = 30000  # 30 segundos

    while True:
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - start_time

        if elapsed_time >= level_duration:
            pygame.mixer.music.stop()
            return 'win', int(score + total_score)

        if level > 1:
            obstacle_speed = 5 + (elapsed_time // 5000)  # Aumenta a velocidade conforme o tempo passa

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                return 'quit', 0
            if event.type == spawn_obstacle_event:
                num_obstacles = random.randint(2, 4) if level == 1 else random.randint(3, 5)
                for _ in range(num_obstacles):
                    img = random.choice(obstacle_images[level])
                    obstacle = Obstacle(obstacle_speed, img)
                    all_sprites.add(obstacle)
                    obstacles.add(obstacle)
                pygame.time.set_timer(spawn_obstacle_event, random.randint(800, 1500) if level == 1 else random.randint(400, 800))
            if event.type == spawn_powerup_event:
                powerup = PowerUp(load_image("powerup.png"))
                all_sprites.add(powerup)
                powerups.add(powerup)
                pygame.time.set_timer(spawn_powerup_event, random.randint(5000, 10000))

        all_sprites.update()
        player.check_invincibility()

        # Verifica colisões
        if pygame.sprite.spritecollide(player, obstacles, dokill=True):
            collision_sound.play()
            player.take_damage()
            if player.health <= 0:
                pygame.mixer.music.stop()
                return 'lose', int(score + total_score)

        if pygame.sprite.spritecollide(player, powerups, dokill=True):
            player.health = min(player.health + 25, 100)  # Cura o jogador

        score = int(elapsed_time / 100)

        screen.blit(backgrounds[level], (0, 0))
        all_sprites.draw(screen)

        # Informações do jogo
        font = pygame.font.SysFont(None, 30)
        texts = [
            f"Time: {int((level_duration - elapsed_time) / 1000)}",
            f"Score: {score + total_score}",
            f"Health: {player.health}%",
            f"Level: {level}"
        ]
        for i, text in enumerate(texts):
            screen.blit(font.render(text, True, WHITE), (10, 10 + i * 30))

        # Desenha barra de saúde
        pygame.draw.rect(screen, RED, (SCREEN_WIDTH - 110, 10, 100, 20))
        pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH - 110, 10, player.health, 20))

        pygame.display.flip()
        clock.tick(60)

def main():
    global high_scores

    while True:
        action = show_main_menu()

        if action == 'quit':
            break
        elif action == 'new_game':
            for level in range(1, 4):  # Três níveis
                show_level_transition(level)
                result, score = game_loop(level, score if level > 1 else 0)

                if result != 'win':
                    break

            if result in ['quit', 'lose', 'win']:
                color = RED if result == 'lose' else GREEN
                message = "GAME OVER" if result == 'lose' else "YOU WIN"
                action = show_end_screen(message, color, score)
                save_score(score)

            if action == 'quit':
                break
        elif action == 'high_scores':
            show_high_scores()

    pygame.quit()

if __name__ == "__main__":
    main()