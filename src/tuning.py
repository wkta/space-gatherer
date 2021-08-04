import glvars


def handle_diff_increase():

    def add_bomb(increm=1):
        glvars.nb_bombs += increm
        # print('bombs: ', end='')
        # print(glvars.nb_bombs)

    def boost_speed(increm=1):
        glvars.simu_avatar_speed += increm
        # print('av speed: ', end='')
        # print(glvars.simu_avatar_speed)

    glvars.difficulty += 1
    # print('  (DEBUG - new DIFF. level is ' + str(glvars.difficulty) + ')')

    if glvars.difficulty == 2:
        boost_speed()  # S
    elif glvars.difficulty == 3:
        add_bomb()  # BB
    elif glvars.difficulty == 4:
        boost_speed()  # S
    elif glvars.difficulty == 5:
        add_bomb(2)  # B

    elif glvars.difficulty == 6:   # frow now on, speed will go 1+2+3 then rewards are boosted
        boost_speed()
    elif glvars.difficulty == 7:
        boost_speed(2)
    elif glvars.difficulty == 8:
        boost_speed(3)
        glvars.booster_flag = True
        glvars.nugget_reward = 175

    elif glvars.difficulty == 16:
        add_bomb()

    elif glvars.difficulty == 32:
        add_bomb()
