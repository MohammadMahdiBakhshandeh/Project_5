import pygame
import math
import random


WIDTH = 1200
HEIGHT = 700

FPS = 60
DT = 1 / FPS

WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
BLUE = (50, 120, 255)
RED = (220, 60, 60)
GREEN = (0, 180, 0)


class Cart:

    def __init__(self):

        self.x = WIDTH // 2
        self.v = 0

        self.width = 140
        self.height = 50

    def update(self, force):

        self.v += force * DT

        self.v *= 0.98

        self.x += self.v

        if self.x < 100:
            self.x = 100
            self.v = 0

        if self.x > WIDTH - 100:
            self.x = WIDTH - 100
            self.v = 0



class Pendulum:

    def __init__(self):

        self.length = 180

        self.angle = random.uniform(-0.05, 0.05)

        self.angular_velocity = 0

    def update(self, force):

        g = 9.81

        theta_acc = (
            (g / self.length) * math.sin(self.angle)
            - force * 0.0006
        )

        self.angular_velocity += theta_acc

        self.angular_velocity *= 0.995

        self.angle += self.angular_velocity

    def sensor_angle(self):

        noise = random.gauss(0, 0.015)

        return self.angle + noise



class Controller:

    def __init__(self):

        self.kp = 180
        self.ki = 0
        self.kd = 35

        self.integral = 0
        self.prev_error = 0

    def compute(self, angle):

        error = -angle

        self.integral += error * DT

        derivative = (
            error - self.prev_error
        ) / DT

        self.prev_error = error

        output = (
            self.kp * error
            + self.ki * self.integral
            + self.kd * derivative
        )

        return max(min(output, 50), -50)



class Simulation:

    def __init__(self):

        pygame.init()

        self.screen = pygame.display.set_mode(
            (WIDTH, HEIGHT)
        )

        pygame.display.set_caption(
            "Inverse Pendulum"
        )

        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont(
            "arial", 24
        )

        self.cart = Cart()

        self.pendulum = Pendulum()

        self.controller = Controller()

        self.running = True

        self.auto_mode = True

    def draw(self):

        self.screen.fill(WHITE)

        pygame.draw.line(
            self.screen,
            BLACK,
            (0, HEIGHT - 120),
            (WIDTH, HEIGHT - 120),
            4
        )

        cart_y = HEIGHT - 170

        pygame.draw.rect(
            self.screen,
            BLUE,
            (
                self.cart.x - self.cart.width // 2,
                cart_y,
                self.cart.width,
                self.cart.height
            ),
            border_radius=10
        )

        pygame.draw.circle(
            self.screen,
            BLACK,
            (
                int(self.cart.x - 45),
                cart_y + 60
            ),
            18
        )

        pygame.draw.circle(
            self.screen,
            BLACK,
            (
                int(self.cart.x + 45),
                cart_y + 60
            ),
            18
        )

        pivot_x = self.cart.x
        pivot_y = cart_y

        end_x = (
            pivot_x +
            self.pendulum.length *
            math.sin(self.pendulum.angle)
        )

        end_y = (
            pivot_y -
            self.pendulum.length *
            math.cos(self.pendulum.angle)
        )

        pygame.draw.line(
            self.screen,
            BLACK,
            (pivot_x, pivot_y),
            (end_x, end_y),
            8
        )

        pygame.draw.circle(
            self.screen,
            RED,
            (int(end_x), int(end_y)),
            18
        )

        angle_deg = math.degrees(
            self.pendulum.angle
        )

        mode = (
            "AUTO PID"
            if self.auto_mode
            else "MANUAL"
        )

        texts = [

            f"Angle : {angle_deg:.2f}",

            f"Mode : {mode}",

            f"Kp={self.controller.kp}",

            f"Kd={self.controller.kd}",

            "SPACE : Change Mode",

            "LEFT/RIGHT : Manual Control",

            "Q/A : Kp +/-",

            "W/S : Kd +/-"

        ]

        for i, t in enumerate(texts):

            txt = self.font.render(
                t,
                True,
                BLACK
            )

            self.screen.blit(
                txt,
                (20, 20 + i * 30)
            )

        pygame.display.flip()

    def run(self):

        while self.running:

            self.clock.tick(FPS)

            force = 0

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_SPACE:
                        self.auto_mode = \
                            not self.auto_mode

                    if event.key == pygame.K_q:
                        self.controller.kp += 10

                    if event.key == pygame.K_a:
                        self.controller.kp -= 10

                    if event.key == pygame.K_w:
                        self.controller.kd += 5

                    if event.key == pygame.K_s:
                        self.controller.kd -= 5

            keys = pygame.key.get_pressed()

            if self.auto_mode:

                measured_angle = (
                    self.pendulum.sensor_angle()
                )

                force = (
                    self.controller.compute(
                        measured_angle
                    )
                )

            else:

                if keys[pygame.K_LEFT]:
                    force = -20

                if keys[pygame.K_RIGHT]:
                    force = 20

            self.cart.update(force)

            self.pendulum.update(force)

            # جلوگیری از سقوط

            if abs(self.pendulum.angle) > 0.5:

                self.pendulum.angle = \
                    random.uniform(
                        -0.05,
                        0.05
                    )

                self.pendulum.angular_velocity = 0

            self.draw()

        pygame.quit()



if __name__ == "__main__":

    sim = Simulation()

    sim.run()