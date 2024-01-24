# Import Libraries
import os
import numpy as np
import pygame
from pygame.locals import *
from random import randrange, randint
from math import sin, cos, pi, sqrt

from drones import DronePlayer, DronePID, DroneSAC

# Define game constants
screen_fps = 60
screen_width = 800
screen_height = 800

# Initialize Pygame
frames = pygame.time.Clock()
pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))

# Initialize drone
drone_animation_speed = 0.3
drone_width = 80
drone_animation = []
drone_image = pygame.image.load("images/drone.png")
drone_image.convert()
drone_animation.append(pygame.transform.scale(drone_image, (drone_width, int(drone_width)))) 

# Initialize money
money_animation_speed = 0.1
money_width = 30
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
respawn_font = pygame.font.Font("fonts/Roboto-Bold.ttf", 80)
name_font = pygame.font.Font("fonts/Roboto-Bold.ttf", 20)
name_hud_font = pygame.font.Font("fonts/Roboto-Bold.ttf", 15)
time_font = pygame.font.Font("fonts/Roboto-Bold.ttf", 30)
score_font = pygame.font.Font("fonts/Roboto-Regular.ttf", 20)
final_font = pygame.font.Font("fonts/Roboto-Regular.ttf", 40)

# Function to display info about a player
def display_info(position):
    name_text = name_font.render(drone.name, True, (255, 255, 255))
    screen.blit(name_text, (position, 20))
    target_text = score_font.render(
        "Score : " + str(drone.money_counter), True, (255, 255, 255)
    )
    screen.blit(target_text, (position, 45))
    if drone.dead == True:
        respawning_text = info_font.render(
            "Respawning...", True, (255, 255, 255)
        )
        screen.blit(respawning_text, (position, 120))

# Initialize game variables
time = 0
step = 0
time_limit = 30000
respawn_timer_max = 0.1

# Define how play the drones
drones = [DronePlayer(), DronePID(), DroneSAC()]

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
    moon_image.set_alpha(180)
    screen.blit(moon_image, (540, 0))

    # Display stars
    star_count = 0
    for star_image in star_images:
        if star_bool == True:
            star_image_rect = star_image.get_rect()
            random_position = (randint(0, screen_width - star_image_rect.width), randint(0, screen_height - star_image_rect.height))
            star_positions.append(random_position)
        screen.blit(star_image, star_positions[star_count])
        star_image.set_alpha(180)
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
            elif drone.name == "SAC":
                theta = drone.theta / 180 * pi
                speed = sqrt(drone.x_d**2 + drone.y_d**2)
                theta_d = drone.theta_d
                distance_to_target = (
                    sqrt(
                        (money_targets[drone.money_counter][0] - drone.x) ** 2
                        + (money_targets[drone.money_counter][1] - drone.y)
                        ** 2
                    )
                    / 500
                )
                psi = np.arctan2(
                    money_targets[drone.money_counter][1] - drone.y,
                    money_targets[drone.money_counter][0] - drone.x,
                )

                eta = np.arctan2(
                    money_targets[drone.money_counter][1] - drone.y,
                    money_targets[drone.money_counter][0] - drone.x,
                ) - np.arctan2(drone.y_d, drone.x_d)
                
                thruster_left, thruster_right = drone.act(
                    np.array(
                        [
                            theta,
                            speed,
                            theta_d,
                            distance_to_target,
                            psi,
                            eta,
                            distance_to_target,
                        ]
                    ).astype(np.float32)
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
            if drone.name == "Edo":
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
        money_sprite.set_alpha(drone.alpha)
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
        drone_copy.set_alpha(drone.alpha)
        screen.blit(
            drone_copy,
            (
                drone.x - int(drone_copy.get_width()/2),
                drone.y - int(drone_copy.get_height()/2),
            ),
        )

        # Display names
        name_hud_text = name_hud_font.render(drone.name, True, (255, 255, 255))
        screen.blit(
            name_hud_text,
            (
                drone.x - int(name_hud_text.get_width() / 2),
                drone.y - 30 - int(name_hud_text.get_height() / 2),
            ),
        )

        # Display player info
        if drone_idx == 0:
            display_info(20)
        elif drone_idx == 1:
            display_info(130)
        elif drone_idx == 2:
            display_info(240)
        elif drone_idx == 3:
            display_info(350)

        # Update time
        time_text = info_font.render(
        "Time : " + str(int(time_limit - time)), True, (255, 255, 255)
        )
        screen.blit(time_text, (20, 80))

    if time > time_limit:
        # Evaluate who wins the game
        final_scores = []
        starting_y_pos = screen_height / 2 - 50 * len(drones) // 2
        y_offset = 50 
        bg_padding = 10 

        for i, drone in enumerate(drones):
            # Prepare the text and position
            drone_score_text = f"{drone.name}'s Score: {drone.money_counter}"
            drone_score = final_font.render(drone_score_text, True, (255, 255, 255))
            drone_score_pos = drone_score.get_rect(center=(screen_width/2, starting_y_pos + i * y_offset))

            # Background rectangle
            bg_rect = pygame.Rect(drone_score_pos.left - bg_padding, drone_score_pos.top - bg_padding, 
                                drone_score_pos.width + 2 * bg_padding, drone_score_pos.height + 2 * bg_padding)
            pygame.draw.rect(screen, (0, 0, 0), bg_rect)

            # Blit text on screen
            screen.blit(drone_score, drone_score_pos)
            final_scores.append(drone.money_counter)

        pygame.display.update()
        pygame.time.wait(1000)

        # Determine the winner
        winner_index = np.argmax(final_scores)
        winner = drones[winner_index].name
        winner_text = final_font.render(f"{winner} wins!", True, (255, 255, 255))
        winner_text_pos = winner_text.get_rect(center=(screen_width/2, starting_y_pos + len(drones) * y_offset))

        # Background for winner text
        winner_bg_rect = pygame.Rect(winner_text_pos.left - bg_padding, winner_text_pos.top - bg_padding, 
                                    winner_text_pos.width + 2 * bg_padding, winner_text_pos.height + 2 * bg_padding)
        pygame.draw.rect(screen, (0, 0, 0), winner_bg_rect)

        # Blit winner text on screen
        screen.blit(winner_text, winner_text_pos)
        pygame.display.update()

        pygame.time.wait(7000) 
        break

    pygame.display.update()
    frames.tick(screen_fps)

pygame.quit()