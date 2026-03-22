import sys
import random
import pygame

# Constantes
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BRICK_COLORS = [
    (200, 50, 50),
    (50, 200, 50),
    (50, 50, 200),
    (200, 200, 50),
]

PADDLE_WIDTH = 100
PADDLE_HEIGHT = 15
PADDLE_SPEED = 7

BALL_RADIUS = 8
BALL_SPEED = 5

BRICK_ROWS = 6
BRICK_COLS = 10
BRICK_WIDTH = SCREEN_WIDTH // BRICK_COLS
BRICK_HEIGHT = 25


class Paddle:
    """Représente la raquette du joueur."""

    def __init__(self) -> None:
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.rect = pygame.Rect(
            (SCREEN_WIDTH - self.width) // 2,
            SCREEN_HEIGHT - 50,
            self.width,
            self.height,
        )
        self.speed = PADDLE_SPEED

    def update(self, keys: pygame.key.ScancodeWrapper) -> None:
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        # Limites écran
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, WHITE, self.rect)


class Ball:
    """Représente la balle."""

    def __init__(self) -> None:
        self.radius = BALL_RADIUS
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.vx = BALL_SPEED * random.choice([-1, 1])
        self.vy = -BALL_SPEED

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            self.radius * 2,
            self.radius * 2,
        )

    def update(self) -> None:
        self.x += self.vx
        self.y += self.vy

        # Collisions avec les bords
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.vx *= -1
        if self.rect.top <= 0:
            self.vy *= -1

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(
            surface, WHITE, (int(self.x), int(self.y)), self.radius)


class Brick:
    """Représente une brique."""

    def __init__(self, x: int, y: int, color: tuple[int, int, int]) -> None:
        self.rect = pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT)
        self.color = color
        self.alive = True

    def draw(self, surface: pygame.Surface) -> None:
        if self.alive:
            pygame.draw.rect(surface, self.color, self.rect)
            pygame.draw.rect(surface, BLACK, self.rect, 1)


def create_bricks() -> list[Brick]:
    bricks: list[Brick] = []
    for row in range(BRICK_ROWS):
        for col in range(BRICK_COLS):
            x_pos = col * BRICK_WIDTH
            y_pos = 60 + row * BRICK_HEIGHT
            color = BRICK_COLORS[row % len(BRICK_COLORS)]
            bricks.append(Brick(x_pos, y_pos, color))
    return bricks


def handle_ball_collisions(
    ball: Ball,
    paddle: Paddle,
    bricks: list[Brick],
    score: int,
) -> int:
    # Collision avec la raquette
    if ball.rect.colliderect(paddle.rect) and ball.vy > 0:
        ball.vy *= -1
        # Effet selon la position d'impact
        offset = (ball.x - paddle.rect.centerx) / (paddle.width / 2)
        ball.vx = BALL_SPEED * offset

    # Collisions avec les briques
    for brick in bricks:
        if brick.alive and ball.rect.colliderect(brick.rect):
            brick.alive = False
            score += 10

            # Déterminer le côté de collision
            if (
                ball.rect.bottom >= brick.rect.top
                and ball.rect.top < brick.rect.top
                and ball.vy > 0
            ):
                ball.vy *= -1
            elif (
                ball.rect.top <= brick.rect.bottom
                and ball.rect.bottom > brick.rect.bottom
                and ball.vy < 0
            ):
                ball.vy *= -1
            else:
                ball.vx *= -1
            break

    return score


def draw_text(
    surface: pygame.Surface,
    text: str,
    size: int,
    x_pos: int,
    y_pos: int,
) -> None:
    font = pygame.font.SysFont("arial", size)
    rendered = font.render(text, True, WHITE)
    rect = rendered.get_rect(center=(x_pos, y_pos))
    surface.blit(rendered, rect)


def countdown(screen: pygame.Surface) -> None:
    for number in ["3", "2", "1"]:
        screen.fill(BLACK)
        draw_text(screen, number, 80, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        pygame.display.flip()
        pygame.time.delay(1000)

def draw_menu(screen: pygame.Surface) -> None:
    screen.fill(BLACK)
    draw_text(screen, "Brick Breaker", 60, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
    draw_text(screen, "Appuie sur ESPACE pour commencer", 32,
              SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    draw_text(screen, "Appuie sur ESC pour quitter", 28, 
              SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)
    pygame.display.flip()

def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Brick Breaker")
    clock = pygame.time.Clock()

    paddle = Paddle()
    ball = Ball()
    bricks = create_bricks()
    score = 0

    running = True
    game_over = False
    win = False
    paused = False
    in_menu = True   # IMPORTANT

    while running:
        clock.tick(FPS)

        # --- ÉVÉNEMENTS ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # --- MENU PRINCIPAL ---
            if in_menu:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        in_menu = False
                    if event.key == pygame.K_ESCAPE:
                        running = False
                continue  # On reste dans le menu

            # --- PAUSE ---
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                    if not paused:
                        countdown(screen)

            # --- RESTART ---
            if (game_over or win) and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paddle = Paddle()
                    ball = Ball()
                    bricks = create_bricks()
                    score = 0
                    game_over = False
                    win = False

        # --- AFFICHAGE DU MENU ---
        if in_menu:
            draw_menu(screen)
            continue

        # --- LOGIQUE DU JEU ---
        keys = pygame.key.get_pressed()

        if not paused and not game_over and not win:
            paddle.update(keys)
            ball.update()
            score = handle_ball_collisions(ball, paddle, bricks, score)

            if ball.rect.top > SCREEN_HEIGHT:
                game_over = True

            if all(not brick.alive for brick in bricks):
                win = True

        # --- RENDU ---
        screen.fill(BLACK)

        for brick in bricks:
            brick.draw(screen)

        paddle.draw(screen)
        ball.draw(screen)

        draw_text(screen, f"Score : {score}", 24, 80, 20)

        if paused:
            draw_text(screen, "PAUSE", 48, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        if game_over:
            draw_text(screen, "Oh bah mince alors! C'est ballot. ESPACE pour rejouer", 28,
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        if win:
            draw_text(screen, "GG l'ami! ESPACE pour rejouer", 28,
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
