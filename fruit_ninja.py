import pygame
import os
import random
import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils  # mediapipe 繪圖方法
mp_drawing_styles = mp.solutions.drawing_styles  # mediapipe 繪圖樣式
mp_hands = mp.solutions.hands  # mediapipe 偵測手掌方法

player_lives = 3
score = 0
fruits = ['melon', 'orange', 'pomegranate', 'guava', 'bomb']

# initialize pygame and create window
WIDTH = 800
HEIGHT = 500
FPS = 30
pygame.init()
pygame.display.set_caption('Fruit-Ninja Game with OPENCV')
gameDisplay = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

background = pygame.image.load('back.jpg')
font = pygame.font.Font(os.path.join(os.getcwd(), 'comic.ttf'), 42)
score_text = font.render('Score : ' + str(score), True, (255, 255, 255))
lives_icon = pygame.image.load('images/white_lives.png')

font_name = pygame.font.match_font('comic.ttf')

explode = pygame.mixer.Sound('sound/explode.wav')
smurf = pygame.mixer.Sound('sound/smurf.wav')


def generate_random_fruits(fruit):
    fruit_path = "images/" + fruit + ".png"
    data[fruit] = {
        'img': pygame.image.load(fruit_path),
        'x': random.randint(100, 500),
        'y': 800,
        'speed_x': random.randint(-10, 10),
        'speed_y': random.randint(-65, -35),
        'throw': (random.random() >= 0.75) and True or False,
        'acceleration': 0,
        'hit': False,
    }


def decrease_live(x, y):
    gameDisplay.blit(pygame.image.load("images/red_lives.png"), (x, y))


#
def draw_text(text, size, x, y):
    fonts = pygame.font.Font(font_name, size)
    text_surface = fonts.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    gameDisplay.blit(text_surface, text_rect)


# 畫生命
def draw_lives(x, y, lives, image):
    for i in range(lives):
        img = pygame.image.load(image)
        img_rect = img.get_rect()
        img_rect.x = int(x + 35 * i)
        img_rect.y = y
        gameDisplay.blit(img, img_rect)


def handle_gameover(first_round):
    global player_lives, score
    gameDisplay.blit(background, (0, 0))
    draw_text("TEAM WORK", 90, WIDTH / 2, HEIGHT / 4)
    if not first_round:
        draw_text("Score : " + str(score), 50, WIDTH / 2, HEIGHT / 2)

    draw_text("Press a key to begin!", 64, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False
    player_lives = 3  # reset player live
    score = 0


def handle_hit(value, key, game_over, current_position):
    global score, player_lives, score_text
    value['x'] += value['speed_x']
    value['y'] += value['speed_y']
    value['speed_y'] += (1 * value['acceleration'])
    value['acceleration'] += 0.3

    if value['y'] <= 800:
        gameDisplay.blit(value['img'], (value['x'], value['y']))
    else:
        generate_random_fruits(key)

    if not value['hit'] and value['x'] < current_position[0] < value['x'] + 90 \
            and value['y'] < current_position[1] < value['y'] + 90:
        if key == 'bomb':
            explode.play()
            player_lives -= 1
            if player_lives == 0:
                handle_gameover(game_over)
                game_over = True
            elif player_lives == 1:
                decrease_live(725, 15)
            elif player_lives == 2:
                decrease_live(760, 15)

            half_fruit_path = "images/explosion.png"
        else:
            smurf.play()
            half_fruit_path = "images/" + "half_" + key + ".png"

        value['img'] = pygame.image.load(half_fruit_path)
        value['speed_x'] += 10
        if key != 'bomb':
            score += 1
        score_text = font.render('Score : ' + str(score), True, (255, 255, 255))
        value['hit'] = True


def draw_point(pos):
    global gameDisplay, BLUE
    pygame.draw.circle(gameDisplay, RED, pos, 18, 5)


def run_game():
    cap = cv2.VideoCapture(1)
    # , cv2.CAP_DSHOW
    with mp_hands.Hands(
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5, max_num_hands=1) as hands:

        global score, score_text, player_lives
        first_round = True
        game_over = True  # terminates the game While loop if more than 3-Bombs are cut
        game_running = True  # used to manage the game loop
        while game_running:
            if game_over:
                if first_round:
                    handle_gameover(first_round)
                    first_round = False
                game_over = False
                draw_lives(690, 5, player_lives, 'images/red_lives.png')

            for event in pygame.event.get():
                # checking for closing window
                if event.type == pygame.QUIT:
                    game_running = False

            gameDisplay.blit(background, (0, 0))
            gameDisplay.blit(score_text, (0, 0))
            draw_lives(690, 5, player_lives, 'images/red_lives.png')

            ret, img = cap.read()
            if not ret:
                print("Cannot receive frame")
            img = cv2.resize(img, (800, 500))
            img2 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = hands.process(img2)  # 偵測手掌
            x = 0
            y = 0
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    x = hand_landmarks.landmark[7].x * WIDTH
                    y = hand_landmarks.landmark[7].y * HEIGHT
                    mp_drawing.draw_landmarks(
                        img,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style())

            img = cv2.flip(img, 1)
            cv2.imshow('cam', img)
            x = 800 - x
            current_position = (x, y)  # gets the current coordinate (x, y) in pixels of the mouse
            draw_point(current_position)

            for key, value in data.items():
                if value['throw']:
                    handle_hit(value, key, game_over, current_position)
                else:
                    generate_random_fruits(key)

            pygame.display.update()
            clock.tick(FPS)
    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()


data = {}
for fruit in fruits:
    generate_random_fruits(fruit)

run_game()
