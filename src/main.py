import pygame
from sprites import Bomb, Nugget, ScoreBoard, SpaceBg, Spacecraft
import glvars


def main_func():
    glvars.ensure_path_ok()
    print(glvars.ASSETS)
    pygame.init()

    glvars.screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption(glvars.CAPTION)

    pygame.mixer.init()
    gl_music = pygame.mixer.Sound(glvars.ASSETS[-5])
    gl_music.set_volume(0.08)
    gl_music.play(-1)

    done_playing = False
    all_scores = [0]

    while not done_playing:
        done_playing = intro_state(max(all_scores))

        if not done_playing:
            glvars.reset_gl_game_vars()
            newscore, abort = game_state()
            all_scores.append(newscore)
            if abort:
                break

    print('GAME OVER.')
    print('Best score: {:,}$'.format(max(all_scores)))
    gl_music.stop()

    pygame.quit()


def intro_state(score):
    my_ship = Spacecraft()
    my_ship.engine_sound.stop()

    space_bg = SpaceBg()

    all_sprites = pygame.sprite.Group(space_bg, my_ship)
    ins_font = pygame.font.SysFont(None, 30)
    instructions = (
        "{} | HIGHSCORE is: {:,}$".format(glvars.CAPTION, score),
        "",
        "Instructions: you're a reckless gatherer hunting for valuable",
        "minerals in the most dangerous part of the Galaxy.",
        "",
        "Fly over small Planetoids to gather minerals, but watch out",
        "for bombs; remainings of the last great space conflict.",
        "Your spaceship would explode if hit by too many explosions.",
        "Good luck!",
        "",
        "Click your ship to start / Press escape to quit"
    )
    nb_ins = len(instructions)
    ins_labels = list()
    for k, ins_txt in enumerate(instructions):
        if k == 0:
            col = (255, 255, 0)
        elif k == nb_ins-1:
            col = (233, 16, 8)
        else:
            col = (111, 111, 90)

        temp_label = ins_font.render(ins_txt, True, col, (0, 0, 0))
        ins_labels.append(temp_label)

    keep_goin = True
    done_playing = False
    clock = pygame.time.Clock()

    while keep_goin:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                done_playing = True
                keep_goin = False
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                keep_goin = False

        # refresh display
        all_sprites.draw(glvars.screen)
        for i in range(len(ins_labels)):
            glvars.screen.blit(ins_labels[i], (28, (1+i)*30))

        pygame.display.flip()
        clock.tick(30)

    return done_playing


def game_state():
    """
    :return: a tuple (score: int, abort: bool)
    """

    li_bombs = []

    my_ship = Spacecraft()
    nugget = Nugget()
    spacebg = SpaceBg()
    scoreboard = ScoreBoard()

    for k in range(glvars.nb_bombs):
        li_bombs.append(Bomb())

    friendly_sprites = pygame.sprite.Group(nugget, my_ship)
    danger_sprites = pygame.sprite.Group(*li_bombs)
    clock = pygame.time.Clock()
    
    game_over = False
    paused = None
    pause_msg = None
    font = pygame.font.SysFont(None, 28)

    def pause_game():
        nonlocal paused, pause_msg
        pause_msg = font.render(
            'Mouse cursor out of screen! Press SPACE to resume the game',
            True,
            (111, 111, 100),
            (0, 0, 0)
        )
        paused = True
        pygame.mouse.set_visible(True)

    def unpause_game():
        nonlocal paused, pause_msg
        pause_msg = None
        paused = False
        pygame.mouse.set_visible(False)

    # -------------------------
    #  GAME LOOP
    # -------------------------
    unpause_game()
    abort = False
    while not game_over:

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                game_over = True
                abort = True

            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                game_over = True

            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
                if paused:
                    unpause_game()

            elif ev.type == pygame.constants.WINDOWLEAVE:
                if not paused:
                    pause_game()

        # - we handle the game logic *************
        if not paused:
            # check if there are enough bombs... If not, we add one
            if len(li_bombs) < glvars.nb_bombs:
                obj = Bomb()
                li_bombs.append(obj)
                danger_sprites.add(obj)

            if pygame.sprite.collide_rect_ratio(0.8)(my_ship, nugget):
                # we manage to gather a nugget
                my_ship.snd_yay.play()
                nugget.reset()
                scoreboard.score += glvars.nugget_reward

            hit_bombs = pygame.sprite.spritecollide(
                my_ship,
                danger_sprites,
                False,  # kill
                pygame.sprite.collide_rect_ratio(glvars.BOMB_RECT_RATIO)
            )
            if hit_bombs:
                my_ship.snd_boom.play()
                for elt in hit_bombs:
                    elt.reset()
                scoreboard.lives -= len(hit_bombs)
                if scoreboard.lives <= 0:
                    game_over = True

            spacebg.update()

            friendly_sprites.update()
            danger_sprites.update()

        scoreboard.update()
        # game logic handling ends here.

        # - draw things & refresh screen *************
        glvars.screen.blit(spacebg.image, spacebg.rect.topleft)
        my_ship.draw_trail(glvars.screen)
        friendly_sprites.draw(glvars.screen)

        danger_sprites.draw(glvars.screen)
        glvars.screen.blit(scoreboard.image, scoreboard.rect.topleft)

        if pause_msg:
            tmp = pause_msg.get_size()
            scr_size = glvars.screen.get_size()
            glvars.screen.blit(pause_msg, ((scr_size[0] - tmp[0])//2, (scr_size[1] - tmp[1])//2))

        pygame.display.flip()

        # cap fps
        clock.tick(glvars.FPS_CAP)
    # game loop has ended

    my_ship.engine_sound.stop()
    print('new score obtained: ', end='')
    print("{:,}$".format(scoreboard.score))
    return scoreboard.score, abort


if __name__ == '__main__':
    main_func()
