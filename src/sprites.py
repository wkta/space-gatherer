import random

import pygame

import glvars
import tuning


class Bomb(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        temp = pygame.image.load(glvars.ASSETS[4])
        self.image = pygame.transform.scale2x(temp)

        self.rect = self.image.get_rect()
        self.dx = None
        self.increm_yspeed = None
        self.reset()

    def reset(self):
        self.rect.bottom = 0
        self.rect.centerx = random.randrange(0, glvars.screen.get_width())

        if random.random() > 0.5:
            self.dx = random.randint(-3, -1)
        else:
            self.dx = random.randint(1, 2)
        self.increm_yspeed = random.randint(1, 5)

    def update(self):
        self.rect.centerx += self.dx
        self.rect.centery += glvars.simu_avatar_speed + self.increm_yspeed

        if self.rect.top > glvars.screen.get_height():
            self.reset()


class Nugget(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()

        self.image = pygame.image.load(glvars.ASSETS[3])
        self.rect = self.image.get_rect()

        self.reset()
        glvars.nuggets_out -= 1  # first reset doesnt count

    def update(self):
        self.rect.centery += glvars.simu_avatar_speed
        if self.rect.top > glvars.screen.get_height():
            self.reset()

    def reset(self):
        self.rect.centery = 0
        self.rect.centerx = random.randrange(0, glvars.screen.get_width())

        glvars.nuggets_out += 1
        if glvars.nuggets_out == glvars.STEP_FOR_DIFF_INCREM:
            tuning.handle_diff_increase()
            glvars.nuggets_out = 0


class ScoreBoard(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.maxlives = 5
        self.lives = self.maxlives
        self.score = 0
        self.font = pygame.font.SysFont(None, 50)

        self.text = ""

    def update(self):
        self.text = "HP: {}/{}  |  Cash: {:,}$".format(self.lives, self.maxlives, self.score)

        self.image = self.font.render(self.text, True, (255, 255, 0))
        self.rect = self.image.get_rect()


class SpaceBg(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(glvars.ASSETS[0])
        self.image = self.image.convert()  # ?
        self.rect = self.image.get_rect()
        self.reset()

    def update(self):
        self.rect.bottom += glvars.simu_avatar_speed
        if self.rect.top >= 0:
            self.reset()

    def reset(self):
        self.rect.bottom = glvars.screen.get_height()


class Spacecraft(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(glvars.ASSETS[1])
        self.rect = self.image.get_rect()

        self.consty = 404
        self.rect.center = (glvars.screen.get_width()//2, self.consty)  # init position
        self._low_speed = True

        if not pygame.mixer:
            print("problem with sounds!")
        else:
            pygame.mixer.init()

            self._snd_slow_engin = pygame.mixer.Sound(glvars.ASSETS[-1])
            self._snd_slow_engin.set_volume(0.44)
            
            self._snd_fast_engin = pygame.mixer.Sound(glvars.ASSETS[-4])
            self._snd_fast_engin.set_volume(1.22)

            self.snd_boom = pygame.mixer.Sound(glvars.ASSETS[-2])
            self.snd_boom.set_volume(0.55)

            self.snd_yay = pygame.mixer.Sound(glvars.ASSETS[-3])
            self.snd_yay.set_volume(0.8)

            self.engine_sound = self._snd_slow_engin
            self.engine_sound.play(-1)



        self.trail_img = pygame.image.load(glvars.ASSETS[2])
        self.big_trail_img = pygame.image.load(glvars.ASSETS[5])

        self.trail_sz = self.trail_img.get_size()
        self._k = 1

        # queued delta_x
        self._q_deltax = 0

    def draw_trail(self, surf):
        tx, ty = self.rect.bottomleft

        if self._k == 0:
            decalx, decaly = -1, -1
        elif self._k == 1:
            decalx, decaly = 1, -1
        elif self._k == 2:
            decalx, decaly = -1, 1
        else:
            decalx, decaly = 1, 1

        if glvars.booster_flag:
            surf.blit(self.big_trail_img, (decalx + tx, -11 + decaly + ty))
        else:
            surf.blit(self.trail_img, (decalx + tx, -11 + decaly + ty))

    def update(self):
        if glvars.booster_flag and self._low_speed:
            self._low_speed = False
            self._snd_slow_engin.stop()
            self.engine_sound = self._snd_fast_engin
            self.engine_sound.play(-1)

        posx, posy = pygame.mouse.get_pos()

        curr_var = abs(self.rect.centerx - posx)
        if self.rect.centerx < posx:
            effective_delta = min(glvars.STEERING_LIMIT, curr_var)
        else:
            effective_delta = -1 * min(glvars.STEERING_LIMIT, curr_var)

        self.rect.center = (self.rect.centerx + effective_delta, self.consty)

        # update the trail effect
        self._k = (self._k + 1) % 4
