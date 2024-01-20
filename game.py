# Import Libraries
import pygame
from pygame.locals import *
import os
from random import randrange, randint
from math import sin, cos, pi, sqrt

from drones import DronePlayer, DronePID

# Define game constants
screen_fps = 60
screen_width = 800
screen_height = 800

# Define physics constants for the drone
# gravity = 0.08
# drone_arm = 25
# drone_width = 60

# Initialize Pygame
frames = pygame.time.Clock()
pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))

# Initialize drone
drone_animation_speed = 0.3
drone_width = 60
drone_animation = []
drone_image = pygame.image.load("images/drone.png")
drone_image.convert()
drone_animation.append(pygame.transform.scale(drone_image, (drone_width, int(drone_width)))) 

# Initialize money
money_animation_speed = 0.1
money_width = 40
money_animation = []
image = pygame.image.load("images/money.png")
image.convert()
money_animation.append(pygame.transform.scale(image, (money_width, int(money_width))))


# Initialize stars
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

'''
ADD FONTS FOR NAME OVER THE PLAYER, SCORE, ...
FUNTION TO DISPLAY INFORMATION TO BE ADDED
'''

# Initialize game variables
# money_counter = 0
time = 0
step = 0
time_limit = 20
# dead = False
respawn_timer_max = 3
# respawn_timer = 3

# Define how play the drones
drones = [DronePlayer(), DronePID()]

# Generate 100 money targets
money_targets = []
for i in range(100):
    money_targets.append((randrange(200, 600), randrange(200, 600)))

# Game loop
while True:
    pygame.event.get()

    time += 1/60
    step += 1

    # Display background
    screen.fill((0, 0, 67))

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

    for drone_idx, drone in enumerate(drones):
        if drone.dead == False:
            # Initialize accelerations
            drone.x_dd = 0
            drone.y_dd = drone.gravity
            drone.theta_dd = 0

            # Calculate propeller forces
            if drone.name == "PID":
                thruster_left, thruster_right = drone.movement(
                    [
                        money_targets[drone.money_counter][0] - drone.x, # Error on x
                        drone.x_d,
                        money_targets[drone.money_counter][1] - drone.y, # Error on y
                        drone.y_d,
                        drone.theta,
                        drone.theta_d,
                    ]
                )
            elif drone.name == "Edo":
                thruster_left, thruster_right = drone.movement()

            # Calculate accelerations
            drone.x_dd +=  - (thruster_left + thruster_right)*sin( drone.theta*pi/180)/drone.mass
            drone.y_dd += - (thruster_left + thruster_right)*cos( drone.theta*pi/180)/drone.mass
            drone.theta_dd +=  drone.drone_arm*(thruster_right - thruster_left)/drone.mass

            # Calculate speed
            drone.x_d += drone.x_dd
            drone.y_d += drone.y_dd
            drone.theta_d += drone.theta_dd

            # Calculate position
            drone.x += drone.x_d
            drone.y += drone.y_d
            drone.theta += drone.theta_d

            # Calculate distance to target
            dist = sqrt((drone.x - money_targets[drone.money_counter][0])**2 + (drone.y - money_targets[drone.money_counter][1])**2)

            # If the money is taken, respawn another one
            if dist < 50:
                drone.money_counter += 1

            # If to far, die and respawn after timer
            elif dist > 1000:
                drone.dead = True
                drone.respawn_timer = respawn_timer_max

        else:
            if drone.name == "Edo" or drone.name == "PID":
                # Display respawn timer
                respawn_text = respawn_font.render(str(int(drone.respawn_timer) + 1), True, (255, 255, 255))
                respawn_text.set_alpha(124)
                screen.blit(
                    respawn_text,
                    (
                        (screen_width - respawn_text.get_width())/2,
                        (screen_height - respawn_text.get_height())/2,
                    ),
                )
                drone.respawn_timer -= 1/60

            # Respawn the drone
            if drone.respawn_timer < 0:
                drone.dead = False
                # Back to initial conditions
                (drone.theta, drone.theta_d, drone.theta_dd) = (0, 0, 0)
                (drone.x, drone.x_d, drone.x_dd) = (400, 0, 0)
                (drone.y, drone.y_d, drone.y_dd) = (400, 0, 0)

        # Display money animations
        money_sprite = money_animation[int(step * money_animation_speed) % len(money_animation)]
        screen.blit(
            money_sprite,
            (
                money_targets[drone.money_counter][0] - int(money_sprite.get_width() / 2),
                money_targets[drone.money_counter][1] - int(money_sprite.get_width() / 2),
            ),
        )

        # Display drone animation
        drone_sprite = drone_animation[int(step*drone_animation_speed) % len(drone_animation)]
        drone_copy = pygame.transform.rotate(drone_sprite, drone.theta)
        drone_copy.set_alpha(200)
        screen.blit(
            drone_copy,
            (
                drone.x - int(drone_copy.get_width()/2),
                drone.y - int(drone_copy.get_height()/2),
            ),
        )

        '''
        ADD FUNCTION TO DISPLAY NAMES
        '''

        # Update time
        time_text = info_font.render(
        "Time : " + str(int(time_limit - time)), True, (255, 255, 255)
        )
        screen.blit(time_text, (20, 60))

    # End the game
    if time > time_limit:
        break

    pygame.display.update()
    frames.tick(screen_fps)

