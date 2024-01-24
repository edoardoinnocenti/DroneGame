import pygame
from pygame.locals import *
from PID import PIDController
from stable_baselines3 import SAC

class Drone:
    def __init__(self):
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

        # Define game variables
        self.money_counter = 0
        self.respawn_timer = 3
        self.dead = False

class DronePlayer(Drone):
    def __init__(self):
        self.name = "Edo"
        self.alpha = 200
        super().__init__()
    
    def movement(self):
        # Initialize both thrusters with the mean value
        thruster_left = thruster_right = self.thruster_mean

        # Get the current state of all keyboard buttons
        pressed_keys = pygame.key.get_pressed()

        # Adjust thrusters based on key inputs
        if pressed_keys[K_UP]:
            thruster_left += self.thruster_amplitude
            thruster_right += self.thruster_amplitude
        elif pressed_keys[K_DOWN]:
            thruster_left -= self.thruster_amplitude
            thruster_right -= self.thruster_amplitude

        if pressed_keys[K_RIGHT]:
            thruster_right -= self.rotation_amplitude
        elif pressed_keys[K_LEFT]:
            thruster_left -= self.rotation_amplitude

        return thruster_left, thruster_right
        

class DronePID(Drone):

    def __init__(self):
        self.name = "PID"
        self.alpha = 70
        super().__init__()

        # Define dt
        self.dt = 1/60

        self.dt = 1 / 60
        self.xPID = PIDController(0.2, 0, 0.2, 25, -25)
        self.thetaPID = PIDController(0.02, 0, 0.01, 1, -1)

        self.yPID = PIDController(2.5, 0, 1.5, 100, -100)
        self.y_dPID = PIDController(1, 0, 0, 1, -1)

    def movement(self, state_vector):
        # Initialize both thrusters with the mean value
        thruster_left = thruster_right = self.thruster_mean

        # Parse inputs
        x_err, _ , y_err, y_d, theta, _ = state_vector

        # Evaluate and update angular correction
        theta_corr = self.xPID.update(-x_err, self.dt)
        theta_err = theta_corr - theta
        theta_update = self.thetaPID.update(-theta_err, self.dt)

        # Evaluate and update vertical correction
        y_d_corr = self.yPID.update(y_err, self.dt)
        y_err = y_d_corr - y_d
        y_update = self.y_dPID.update(-y_err, self.dt)

        thruster_left += (y_update * self.thruster_amplitude) + (theta_update * self.rotation_amplitude)
        thruster_right += (y_update * self.thruster_amplitude) - (theta_update * self.rotation_amplitude)

        return thruster_left, thruster_right
    
class DroneSAC(Drone):
    def __init__(self):
        self.name = "SAC"
        self.alpha = 70
        model_path = "model/sac_model.zip"
        self.path = model_path
        super().__init__()

        self.action_value = SAC.load(self.path)

    def act(self, obs):
        action, _ = self.action_value.predict(obs)
        (action0, action1) = (action[0], action[1])

        thruster_left = self.thruster_mean
        thruster_right = self.thruster_mean

        thruster_left += action0 * self.thruster_amplitude
        thruster_right += action0 * self.thruster_amplitude
        thruster_left += action1 * self.rotation_amplitude
        thruster_right -= action1 * self.rotation_amplitude
        return thruster_left, thruster_right
