class PIDController:
    
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral_error = 0
        self.previous_error = 0

    def update(self, error, dt):

        # Calculate error
        error = error - self.previous_error

        # Proportional term
        kp_term = self.kp * error

        # Integral term
        self.integral_error += error * dt
        ki_term = self.ki * self.integral_error

        # Derivative term
        derivative_error = (error - self.previous_error) / dt
        kd_term = self.kd * derivative_error

        # Total output
        output = kp_term + ki_term + kd_term

        # Save error for next iteration
        self.previous_error = error

        return output