# Import Libraries
import pygame
from pygame.locals import *
import os
from random import randrange, randint
from math import sin, cos, pi, sqrt

# Define game constants
screen_fps = 60
screen_width = 800
screen_height = 800

# Define physics constants for the drone
gravity = 0.08
thruster_amplitude = 0.03
rotation_amplitude = 0.002
thruster_mean = 0.04
mass = 1
drone_arm = 25
drone_width = 60

# Initialize Pygame
frames = pygame.time.Clock()
pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))

# Initialize drone
drone_animation_speed = 0.3
drone = []
drone_image = pygame.image.load("images/drone.png")
drone_image.convert()
drone.append(pygame.transform.scale(drone_image, (drone_width, int(drone_width)))) 

# Initialize money
money_width = 40
money_animation_speed = 0.1
money = []
image = pygame.image.load("images/money.png")
image.convert()
money.append(pygame.transform.scale(image, (money_width, int(money_width))))

# Display stars
star_images = []
for n_star in range(1, 5):
    star_path = os.path.join("images/star_" + str(n_star) + ".png")
    star_images.append(pygame.image.load(star_path))
    star_images.append(pygame.image.load(star_path))
star_positions = []
star_bool = True

# Loading fonts
pygame.font.init()
info_font = pygame.font.Font("fonts/Roboto-Regular.ttf", 26)
respawn_font = pygame.font.Font("fonts/Roboto-Bold.ttf", 90)

# Initialize positions, speeds and accelerations
(theta, theta_d, theta_dd) = (0, 0, 0)
(x, x_d, x_dd) = (400, 0, 0)
(y, y_d, y_dd) = (400, 0, 0)
x_money = randrange(200, 600)
y_money = randrange(200, 600)

# Initialize game variables
money_counter = 0
time = 0
step = 0
time_limit = 100
dead = False
respawn_timer_max = 3
respawn_timer = 3

# Game loop
while True:
    pygame.event.get()

    # Display background
    screen.fill((0, 0, 67))
    time += 1 / 60
    step += 1

    # Display moon
    moon_image = pygame.image.load("images/moon.png")
    screen.blit(moon_image, (540, 0))

    # Display stars
    star_count = 0
    for star_image in star_images:
        if star_bool == True:
            star_image_rect = star_image.get_rect()
            random_position = (randint(0, screen_width - star_image_rect.width), randint(0, screen_height - star_image_rect.height))
            star_positions.append(random_position)
        screen.blit(star_image, star_positions[star_count])
        star_count += 1

    star_bool = False

    if dead == False:
        # Initialize accelerations
        x_dd = 0
        y_dd = gravity
        theta_dd = 0

        # Calculate propeller force based on keys inputs
        thruster_left = thruster_mean
        thruster_right = thruster_mean
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_UP]:
            thruster_left += thruster_amplitude
            thruster_right += thruster_amplitude
        if pressed_keys[K_DOWN]:
            thruster_left -= thruster_amplitude
            thruster_right -= thruster_amplitude
        if pressed_keys[K_RIGHT]:
            thruster_right -= rotation_amplitude
        if pressed_keys[K_LEFT]:
            thruster_left -= rotation_amplitude

        # Calculate accelerations
        x_dd +=  - (thruster_left + thruster_right)*sin(theta*pi/180)/mass
        y_dd += - (thruster_left + thruster_right)*cos(theta*pi/180)/mass
        theta_dd += drone_arm*(thruster_right - thruster_left)/mass

        # Calculate speed
        x_d += x_dd
        y_d += y_dd
        theta_d += theta_dd

        # Calculate position
        x += x_d
        y += y_d
        theta += theta_d

        # Calculate distance to target
        dist = sqrt((x - x_money)**2 + (y - y_money)**2)

        # If the money is taken, respawn another one
        if dist < 50:
            x_money = randrange(200, 600)
            y_money = randrange(200, 600)
            money_counter += 1

        # If to far, die and respawn after timer
        elif dist > 1000:
            dead = True
            respawn_timer = respawn_timer_max
    else:
        # Display respawn timer
        respawn_text = respawn_font.render(
            str(int(respawn_timer) + 1), True, (255, 255, 255)
        )
        respawn_text.set_alpha(124)
        screen.blit(
            respawn_text,
            (
                (screen_width - respawn_text.get_width())/2,
                (screen_height/2 - respawn_text.get_height())/2,
            ),
        )
        respawn_timer -= 1/60

        # Respawn the drone
        if respawn_timer < 0:
            dead = False
            # Back to initial conditions
            (theta, theta_d, theta_dd) = (0, 0, 0)
            (x, x_d, x_dd) = (400, 0, 0)
            (y, y_d, y_dd) = (400, 0, 0)

    # End the game
    if time > time_limit:
        break

    # Display drone and money
    money_sprite = money[int(step * money_animation_speed) % len(money)]
    screen.blit(
        money_sprite,
        (
            x_money - int(money_sprite.get_width() / 2),
            y_money - int(money_sprite.get_height() / 2),
        ),
    )

    drone_sprite = drone[int(step*drone_animation_speed) % len(drone)]
    drone_copy = pygame.transform.rotate(drone_sprite, theta)
    screen.blit(
        drone_copy,
        (
            x - int(drone_copy.get_width()/2),
            y - int(drone_copy.get_height()/2),
        ),
    )

    # Update collected money and time
    money_collected = info_font.render(
        "Money : " + str(money_counter), True, (255, 255, 255)
    )
    screen.blit(money_collected, (20, 20))
    time_text = info_font.render(
        "Time : " + str(int(time_limit - time)), True, (255, 255, 255)
    )
    screen.blit(time_text, (20, 60))

    pygame.display.update()
    frames.tick(screen_fps)

print("Score : " + str(money_counter))