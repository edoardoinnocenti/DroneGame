import numpy as np
from math import sin, cos, pi, sqrt
from random import randrange
import pygame
from pygame.locals import *
import gym
from gym import spaces

class DroneEnv(gym.Env):
    def __init__(self, frame_rendering, mouse_pointer):
        super(DroneEnv, self).__init__()

        self.action_space = spaces.Box(low=-1, high=1, shape=(2,))
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(7,))

        self.frame_rendering = frame_rendering
        self.pointer = mouse_pointer

        # Define game constants
        self.screen_fps = 60
        self.screen_width = 800
        self.screen_height = 800

        # Create the game enviroment
        pygame.init()
        self.frames = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

        self.drone = pygame.image.load("images/drone_.png")
        self.drone.convert()

        self.money = pygame.image.load("images/money_.png")
        self.money.convert()

        pygame.font.init()
        self.font = pygame.font.Font("fonts/Roboto-Regular.ttf", 20)

        # Initialize drone variables
        self.thruster_amplitude = 0.04
        self.rotation_amplitude = 0.003
        self.thruster_mean = 0.04
        self.mass = 1
        self.gravity = 0.08
        self.drone_arm = 25
        self.drone_width = 60

        # Initialize positions, speeds and accelerations
        (self.x, self.x_d, self.x_dd) = (400, 0, 0)
        (self.y, self.y_d, self.y_dd) = (400, 0, 0)
        (self.theta, self.theta_d, self.theta_dd) = (0, 0, 0)
        self.xt = randrange(200, 600)
        self.yt = randrange(200, 600)

        # Initialize game variables
        self.money_counter = 0
        self.reward = 0
        self.time = 0
        self.time_limit = 20
        if self.pointer is True:
            self.time_limit = 1000

    def reset(self):
        # Reset variables
        (self.x, self.x_d, self.x_dd) = (400, 0, 0)
        (self.y, self.y_d, self.y_dd) = (400, 0, 0)
        (self.theta, self.theta_d, self.theta_dd) = (0, 0, 0)
        self.xt = randrange(200, 600)
        self.yt = randrange(200, 600)

        self.money_counter = 0
        self.reward = 0
        self.time = 0

        return self.get_obs()

    def get_obs(self) -> np.ndarray:

        theta = self.theta / 180 * pi
        speed = sqrt(self.x_d**2 + self.y_d**2)
        theta_d = self.theta_d
        distance = (
            sqrt((self.xt - self.x) ** 2 + (self.yt - self.y) ** 2) / 500
        )
        psi = np.arctan2(self.yt - self.y, self.xt - self.x)
        eta = np.arctan2( self.yt - self.y, self.xt - self.x) - np.arctan2(self.y_d, self.x_d)
        return np.array(
            [
                theta,
                speed,
                theta_d,
                distance,
                psi,
                eta,
                distance,
            ]
        ).astype(np.float32)
    
    def step(self, action):
        # Game loop
        self.reward = 0.0
        (action0, action1) = (action[0], action[1])

        # Act every 5 frames
        for _ in range(5):
            self.time += 1 / 60

            if self.pointer is True:
                self.xt, self.yt = pygame.mouse.get_pos()

            # Initialize accelerations
            self.x_dd = 0
            self.y_dd = self.gravity
            self.theta_dd = 0
            thruster_left = self.thruster_mean
            thruster_right = self.thruster_mean

            thruster_left += action0 * self.thruster_amplitude
            thruster_right += action0 * self.thruster_amplitude
            thruster_left += action1 * self.rotation_amplitude
            thruster_right -= action1 * self.rotation_amplitude

            # Calculating accelerations with Newton's laws of motions
            self.x_dd += (
                -(thruster_left + thruster_right) * sin(self.theta * pi / 180) / self.mass
            )
            self.y_dd += (
                -(thruster_left + thruster_right) * cos(self.theta * pi / 180) / self.mass
            )
            self.theta_dd += self.drone_arm * (thruster_right - thruster_left) / self.mass

            self.x_d += self.x_dd
            self.y_d += self.y_dd
            self.theta_d += self.theta_dd
            self.x += self.x_d
            self.y += self.y_d
            self.theta += self.theta_d

            dist = sqrt((self.x - self.xt) ** 2 + (self.y - self.yt) ** 2)

            # Reward per step survived
            self.reward += 1 / 60
            # Penalty according to the distance to target
            self.reward -= dist / (100 * 60)

            if dist < 1:
                # Reward if close to target
                self.xt = randrange(200, 600)
                self.yt = randrange(200, 600)
                self.reward += 100

            # If out of time
            if self.time > self.time_limit:
                done = True
                break

            # If too far from target (crash)
            elif dist > 1000:
                self.reward -= 1000
                done = True
                break

            else:
                done = False

            if self.frame_rendering is True:
                self.render("yes")

        info = {}

        return (
            self.get_obs(),
            self.reward,
            done,
            info,
        )
    
    def render(self, mode):
        # Pygame rendering
        pygame.event.get()
        self.screen.fill(0)
        self.screen.blit(
            self.money,
            (
                self.xt - int(self.money.get_width() / 2),
                self.yt - int(self.money.get_height() / 2),
            ),
        )
        drone_copy = pygame.transform.rotate(self.drone, self.theta)
        self.screen.blit(
            drone_copy,
            (
                self.x - int(drone_copy.get_width() / 2),
                self.y - int(drone_copy.get_height() / 2),
            ),
        )

        textsurface = self.font.render(
            "Collected: " + str(self.money_counter), False, (255, 255, 255)
        )
        self.screen.blit(textsurface, (20, 20))
        textsurface3 = self.font.render(
            "Time: " + str(int(self.time)), False, (255, 255, 255)
        )
        self.screen.blit(textsurface3, (20, 50))

        pygame.display.update()
        self.frames.tick(self.screen_fps)

    def close(self):
        pass
