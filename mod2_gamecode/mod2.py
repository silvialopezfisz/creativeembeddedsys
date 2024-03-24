import pygame
import serial
import random

# Define serial port and baud rate (BAUD RATE must match the arduino code rate)
SERIAL_PORT = '/dev/tty.usbserial-56230321211'  # Arduino serial port
BAUD_RATE = 115200

# Initialize serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fishing Game")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREY = (128, 128, 128)
YELLOW = (255, 195, 0)
GREEN = (0, 255, 0)
BLUE_WATER = (100, 149, 237)
BLUE_SKY = (167, 199, 231)

# game states
START_SCREEN = 0
FISHING_SCREEN = 1
GAME_OVER_SCREEN = 2

# game stuff (intializing, variables)
game_state = START_SCREEN
game_start_time = 0  
game_duration = 30
points = 0
font = pygame.font.SysFont("Courier", 32)
HORIZON_Y = SCREEN_HEIGHT // 4

# fish stuff
fish_size = 50
fish_speeds = [10, 15, 20] 
fish_list = []
hooked_fish = None


# Load images (fish, rod, title screen)
greyfish_image = pygame.image.load("gamemedia/greyfish.png")
yellowfish_image = pygame.image.load("gamemedia/yellowfish.png")
greenfish_image = pygame.image.load("gamemedia/greenfish.png")
startwater_image = pygame.image.load("gamemedia/startwater.jpg")
fishing_rod_image = pygame.image.load("gamemedia/fishingrod.png")
pescalo_image = pygame.image.load("gamemedia/pescalo.png")


def create_fish():
    # fish start on right side, move left
    fish_speed = random.choice(fish_speeds)
    fish_x = SCREEN_WIDTH  
    fish_y = random.randint(HORIZON_Y + 20, SCREEN_HEIGHT - fish_size)  # Randomize y-coordinate of spawnning fishies

    # color and points based on fish's speed
    if fish_speed == fish_speeds[0]:  # grey slowest
        color = GREY
        points_value = 1
    elif fish_speed == fish_speeds[1]:  # yellow faster
        color = YELLOW
        points_value = 2
    else:  # green fastest 
        color = GREEN
        points_value = 3

    return {'x': fish_x, 'y': fish_y, 'speed': fish_speed, 'color': color, 'points': points_value}

def draw_fish(fish):
    if fish['color'] == GREY:
        screen.blit(greyfish_image, (fish['x'], fish['y']))
    elif fish['color'] == YELLOW:
        screen.blit(yellowfish_image, (fish['x'], fish['y']))
    elif fish['color'] == GREEN:
        screen.blit(greenfish_image, (fish['x'], fish['y']))
    else:
        pygame.draw.rect(screen, fish['color'], (fish['x'], fish['y'], fish_size, fish_size))

# this is JUST for the fishing rod image, not the fishing line!!!
def draw_fishing_rod():
    screen.blit(fishing_rod_image, (50, HORIZON_Y - 115 ))  

def draw_timer():
    if game_state == FISHING_SCREEN:
        current_time = pygame.time.get_ticks() // 1000
        time_left = max(0, game_duration - (current_time - game_start_time))
        timer_text = font.render("Time left: {}".format(time_left), True, BLACK)
        timer_rect = timer_text.get_rect(topright=(SCREEN_WIDTH - 20, 40))
        screen.blit(timer_text, timer_rect)

def move_fish(fish):
    fish['x'] -= fish['speed']  

#  check if the fishing line is touching a fish
def check_hooked_fish():
    global hooked_fish
    for fish in fish_list:
        if (buttonVal == 0 and  # Check if the button is pressed
            fishing_line_x >= fish['x'] and fishing_line_x <= fish['x'] + fish_size and
            fishing_line_y >= fish['y'] and fishing_line_y <= fish['y'] + fish_size):
            hooked_fish = fish
            hooked_fish['speed'] = 0  # Stop fish movement on the x-axis
            hooked_fish['x'] = fishing_line_x - 25  # Set fish x-coordinate to fishing line x-coordinate
            hooked_fish['y'] = fishing_line_y  # Set fish y-coordinate to fishing line y-coordinate
            break
        elif buttonVal == 0 and hooked_fish:
            hooked_fish['speed'] = random.choice(fish_speeds)  # Reset fish's speed
            hooked_fish = None  # Remove fish from hooked state

# check if hit horizon and if fish is hooked == get points
def reel_in_fish():
    global hooked_fish, points
    if fishing_line_y <= HORIZON_Y:
        if hooked_fish:
            points += hooked_fish['points']  # Increment points based on the points value of the caught fish
            fish_list.remove(hooked_fish)
            hooked_fish = None


#  Debounce variables
last_button_state = 1  # with button not initially pressed
debounce_counter = 0
debounce_delay = 50  


# GAME LOOP ! 
running = True
while running:
    current_time = pygame.time.get_ticks() // 1000
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # read serial input from button and potentiometer and parse variables
    serial_input = ser.readline().decode().strip()

    values = serial_input.split(",")
    potVal = int(values[0].strip())
    buttonVal = int(values[1].strip())

    screen.fill(WHITE)

    # Implement debounce 
    if buttonVal != last_button_state:
        debounce_counter += 1
        if debounce_counter >= debounce_delay:
            debounce_counter = 0
            last_button_state = buttonVal

            if game_state == FISHING_SCREEN:
                check_hooked_fish()
                reel_in_fish()

    if game_state == START_SCREEN:
        #starting image and PESCALO title png
        screen.blit(startwater_image, (0, 0))
        screen.blit(pescalo_image, ((SCREEN_WIDTH // 2)-175, (SCREEN_HEIGHT // 2)-150))

        rectangle_width = 150
        rectangle_height = 75
        
        # Start button
        start_rect = pygame.Rect(0, 0, rectangle_width, rectangle_height)
        start_rect.center = (SCREEN_WIDTH // 2, (SCREEN_HEIGHT // 2) +20)
        pygame.draw.rect(screen, (255, 87, 51), start_rect, border_radius=50)
        start_text = font.render("Start", True, WHITE)

        text_rect = start_text.get_rect(center=start_rect.center)
        screen.blit(start_text, text_rect.topleft)

        # welcome message
        message = (" Welcome to PESCALO! Ready to start fishing? \n Use the button to catch fish and use potentiometer to control \n your fishing line. Fish must come all the way back up to be caught.\n 1 pt for grey fish, 2pts for yellow fish, 3pts for green fish. \n READY? SET? FISH! " )
        instruct_font = pygame.font.SysFont("Courier", 19, bold=True)
        message_text = instruct_font.render(message, True, BLACK)
        outer_rect = pygame.Rect(0, 0, SCREEN_WIDTH - 40, 150)  
        outer_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)  
        inner_rect = outer_rect.inflate(-10, -10)  

        # Instructions rectangle and border
        pygame.draw.rect(screen, BLUE_SKY, outer_rect)
        pygame.draw.rect(screen, BLUE_WATER, inner_rect)

        # adjust text so it wraps
        text_x = inner_rect.x + 10  # left padding
        text_y = inner_rect.y + 10  # top padding 
        line_spacing = 5 
        for idx, line in enumerate(message.split('\n')):
            line_rendered = instruct_font.render(line, True, WHITE if idx not in (0, 4) else (240, 180, 0))
            line_rect = line_rendered.get_rect(center=(SCREEN_WIDTH // 2, text_y))
            screen.blit(line_rendered, line_rect)
            text_y += line_rendered.get_height() + line_spacing

        # if start button pressed, start game
        if buttonVal == 0:
            game_state = FISHING_SCREEN
            game_start_time = pygame.time.get_ticks() // 1000  
            points = 0 #reset points to 0


    elif game_state == FISHING_SCREEN:

        screen.fill(BLUE_SKY)
        draw_fishing_rod()
        draw_timer()

        #Horizon line, blue water rectangle
        pygame.draw.line(screen, (96, 130, 182), (0, HORIZON_Y), (SCREEN_WIDTH, HORIZON_Y), 2)
        pygame.draw.rect(screen, BLUE_WATER, (0, HORIZON_Y + 1, SCREEN_WIDTH, SCREEN_HEIGHT - HORIZON_Y - 1))

        # Calculate fishing line_y position : 
        # fishing_line_y = find what percentage the potentiometer is at, and then multiply that by the playable screen (blue ocean block)
        fishing_line_x = SCREEN_WIDTH // 6  
        fishing_line_y = SCREEN_HEIGHT - (SCREEN_HEIGHT - HORIZON_Y) * potVal// 4095

        pygame.draw.line(screen, BLACK, (fishing_line_x, HORIZON_Y), (fishing_line_x, fishing_line_y), 2)

        # check if fish @ horizon line (to count point)
        reel_in_fish()

        # check if fish is "hooked"/ stuck to fishing line
        check_hooked_fish()

        # move and draw fish
        for fish in fish_list:
            if fish is hooked_fish: #if fish is hooked, should be glued to fishing line y
                fish['y'] = fishing_line_y  
            else:
                move_fish(fish)
            draw_fish(fish)

        # randomize spawning new fish
        if random.randint(0, 100) < 25: 
            fish_list.append(create_fish())
        # get rid of fish that hit left border
        fish_list = [fish for fish in fish_list if fish['x'] > -fish_size]

        points_text = font.render("Points: {}".format(points), True, BLACK)
        points_rect = points_text.get_rect(topright=(SCREEN_WIDTH - 20, 20))
        screen.blit(points_text, points_rect)

        # if game timer is up, raise GAME OVER alert
        if current_time - game_start_time >= game_duration:
            game_state = GAME_OVER_SCREEN

            #  "GAME OVER!" on screen
            game_over_rect = pygame.Rect(SCREEN_WIDTH // 3, SCREEN_HEIGHT // 3, SCREEN_WIDTH // 3, SCREEN_HEIGHT // 3)
            pygame.draw.rect(screen, (210, 43, 43), game_over_rect)
            game_over_text = font.render("GAME OVER!", True, WHITE)
            game_over_text = pygame.font.SysFont("Courier", 32).render("GAME OVER!", True, WHITE)
            game_over_text_rect = game_over_text.get_rect(center=game_over_rect.center)
            screen.blit(game_over_text, game_over_text_rect)

            pygame.display.flip()

            # im waiting a few seconds before going to the start screen 
            # Added this because I used to double press the button on accident and skip the game over screen
            pygame.time.wait(2000)  


    elif game_state == GAME_OVER_SCREEN:
        screen.blit(startwater_image, (0, 0))

        # End screen: game over, points, and HOME button

        game_over_text = font.render("Game Over!", True, WHITE)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        pygame.draw.rect(screen, BLUE_WATER, game_over_rect)
        screen.blit(game_over_text, game_over_rect.topleft)

        score_text = font.render("Your score: {}".format(points), True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        pygame.draw.rect(screen, BLUE_WATER, score_rect)
        screen.blit(score_text, score_rect.topleft)

        home_text = font.render("Home", True, WHITE)
        home_rect = home_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150))
        home_rect.width = home_text.get_width() + 20  # Add some padding to the width
        home_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150)
        pygame.draw.rect(screen, (255, 87, 51), home_rect, border_radius=50)
        text_rect = home_text.get_rect(center=home_rect.center)
        screen.blit(home_text, text_rect.topleft)


        # if button press = go back to start screen
        if buttonVal == 0:
            game_state = START_SCREEN

    pygame.display.flip()

ser.close()

pygame.quit()
