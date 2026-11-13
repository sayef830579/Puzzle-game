import pygame
import sys
import random
from pygame.locals import *

win_width = 1420
win_height = 880
FPS = 80
BLANK = None

# background up color
BG_TOP = (30, 41, 59)
BG_BOTTOM = (15, 23, 42)

TILE_COLOR = (99, 102, 241)
TILE_COLOR_LIGHT = (129, 140, 248)
TILE_SHADOW = (30, 27, 75)
TILE_RADIUS = 14

TEXT_COLOR = (255, 255, 255)
BORDER_COLOR = (245, 158, 11)
BOARD_PANEL_COLOR = (51, 65, 85)

BASICFONTSIZE = 26
BIGFONTSIZE = 46
SMALLFONTSIZE = 18

MESSAGE_BG = (30, 41, 59)
MESSAGE_TEXT = (74, 222, 128)

BUTTON_COLOR = (99, 102, 241)
BUTTON_HOVER_COLOR = (129, 140, 248)
BUTTON_TEXT_COLOR = (255, 255, 255)
BUTTON_RADIUS = 12
SIDEBAR_COLOR = (51, 65, 85)
SIDEBAR_RADIUS = 18

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

LEVELS = {
    'Easy  (3 x 3)':   (3, 3, 190, 25,  (74, 222, 128)),   # green-400
    'Normal (4 x 4)':  (4, 4, 130, 60,  (99, 102, 241)),   # indigo-500
    'Hard  (5 x 5)':   (5, 5, 100, 120, (248, 113, 113)),  # red-400
}

# defoult bord size
w_of_board = 4
h_of_board = 4
block_size = 130
XMARGIN = 0
YMARGIN = 0
CURRENT_ACCENT = TILE_COLOR

# fetures(Reset,New game, Auto solve,level change)
SIDEBAR_WIDTH = 260
SIDEBAR_X = win_width - SIDEBAR_WIDTH - 40
SIDEBAR_Y = 40
SIDEBAR_HEIGHT = win_height - 80
BUTTON_W = SIDEBAR_WIDTH - 60
BUTTON_H = 60

# Stay board center
def recalc_board_dimensions():
    """Recalculate XMARGIN / YMARGIN whenever w_of_board / h_of_board / block_size change."""
    global XMARGIN, YMARGIN
    # leave room on the right for the sidebar panel
    play_area_width = SIDEBAR_X - 40
    XMARGIN = int((play_area_width - (block_size * w_of_board + (w_of_board - 1))) / 2)
    YMARGIN = int((win_height - (block_size * h_of_board + (h_of_board - 1))) / 2)

# drow beautifull background
def draw_gradient_background(surface, top_color, bottom_color):
    """Simple vertical gradient fill so the background doesn't look flat."""
    height = surface.get_height()
    width = surface.get_width()
    for y in range(height):
        ratio = y / height
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (width, y))

# draw beautifull button
def draw_rounded_button(surface, rect, base_color, hover_color, text, font, mouse_pos, text_color=BUTTON_TEXT_COLOR, radius=BUTTON_RADIUS):
    """Draws a rounded rectangle button that lights up when hovered."""
    is_hovered = rect.collidepoint(mouse_pos)
    color = hover_color if is_hovered else base_color

    # subtle shadow beneath the button
    shadow_rect = rect.move(0, 4)
    pygame.draw.rect(surface, (0, 0, 0), shadow_rect, border_radius=radius)

    pygame.draw.rect(surface, color, rect, border_radius=radius)

    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)
    return is_hovered


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, BIGFONT, SMALLFONT
    global w_of_board, h_of_board, block_size, CURRENT_ACCENT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((win_width, win_height), pygame.RESIZABLE)
    pygame.display.set_caption('Slide Puzzle - CopyAssignment')

    BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)
    BIGFONT = pygame.font.Font('freesansbold.ttf', BIGFONTSIZE)
    SMALLFONT = pygame.font.Font('freesansbold.ttf', SMALLFONTSIZE)

    while True:
        # ---- 1) let the player pick a difficulty level ----
        level_name = level_select_screen()
        w_of_board, h_of_board, block_size, shuffle_moves, CURRENT_ACCENT = LEVELS[level_name]
        recalc_board_dimensions()

        # ---- 2) start playing that level ----
        play_level(shuffle_moves)
        # returning from play_level (via Menu button) loops back to level select


def play_level(shuffle_moves):
    mainBoard, solutionSeq = generateNewPuzzle(shuffle_moves)
    SOLVEDBOARD = start_playing()
    allMoves = []

    # sidebar buttons (rebuilt here since they don't depend on board size)
    reset_rect = pygame.Rect(SIDEBAR_X + 30, 220, BUTTON_W, BUTTON_H)
    new_rect = pygame.Rect(SIDEBAR_X + 30, 220 + (BUTTON_H + 20), BUTTON_W, BUTTON_H)
    solve_rect = pygame.Rect(SIDEBAR_X + 30, 220 + 2 * (BUTTON_H + 20), BUTTON_W, BUTTON_H)
    menu_rect = pygame.Rect(SIDEBAR_X + 30, 220 + 3 * (BUTTON_H + 20), BUTTON_W, BUTTON_H)

    while True:
        slideTo = None
        msg = 'Click a block or press arrow keys to slide'

        if mainBoard == SOLVEDBOARD:
            msg = 'Solved!'

        drawBoard(mainBoard, msg, reset_rect, new_rect, solve_rect, menu_rect)
        check_exit_req()

        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                spotx, spoty = getSpotClicked(mainBoard, event.pos[0], event.pos[1])

                if (spotx, spoty) == (None, None):
                    if reset_rect.collidepoint(event.pos):
                        rst_animation(mainBoard, allMoves, reset_rect, new_rect, solve_rect, menu_rect)
                        allMoves = []
                    elif new_rect.collidepoint(event.pos):
                        mainBoard, solutionSeq = generateNewPuzzle(shuffle_moves)
                        allMoves = []
                    elif solve_rect.collidepoint(event.pos):
                        rst_animation(mainBoard, solutionSeq + allMoves, reset_rect, new_rect, solve_rect, menu_rect)
                        allMoves = []
                    elif menu_rect.collidepoint(event.pos):
                        return 'menu'  # go back to level select screen
                else:
                    blankx, blanky = getBlankPosition(mainBoard)

                    if spotx == blankx + 1 and spoty == blanky:
                        slideTo = LEFT
                    elif spotx == blankx - 1 and spoty == blanky:
                        slideTo = RIGHT
                    elif spotx == blankx and spoty == blanky + 1:
                        slideTo = UP
                    elif spotx == blankx and spoty == blanky - 1:
                        slideTo = DOWN

            elif event.type == KEYUP:
                if event.key in (K_LEFT, K_a) and isValidMove(mainBoard, LEFT):
                    slideTo = LEFT
                elif event.key in (K_RIGHT, K_d) and isValidMove(mainBoard, RIGHT):
                    slideTo = RIGHT
                elif event.key in (K_UP, K_w) and isValidMove(mainBoard, UP):
                    slideTo = UP
                elif event.key in (K_DOWN, K_s) and isValidMove(mainBoard, DOWN):
                    slideTo = DOWN

        if slideTo:
            sliding_animation(mainBoard, slideTo, msg, 8, reset_rect, new_rect, solve_rect, menu_rect)
            take_turn(mainBoard, slideTo)
            allMoves.append(slideTo)

        pygame.display.update()
        FPSCLOCK.tick(FPS)

# level select show screen
def level_select_screen():
    """Show Easy / Normal / Hard buttons and wait for the player to pick one."""
    names = list(LEVELS.keys())

    button_w, button_h = 420, 90
    gap = 26
    total_h = len(names) * button_h + (len(names) - 1) * gap
    start_y = (win_height - total_h) // 2 + 30
    start_x = (win_width - button_w) // 2

    button_rects = []
    for i, name in enumerate(names):
        rect = pygame.Rect(start_x, start_y + i * (button_h + gap), button_w, button_h)
        button_rects.append(rect)

    title_surf = BIGFONT.render('Slide Puzzle', True, TEXT_COLOR)
    title_rect = title_surf.get_rect(center=(win_width // 2, start_y - 140))

    subtitle_surf = SMALLFONT.render('Choose your difficulty to begin', True, (148, 163, 184))
    subtitle_rect = subtitle_surf.get_rect(center=(win_width // 2, start_y - 90))

    while True:
        check_exit_req()
        draw_gradient_background(DISPLAYSURF, BG_TOP, BG_BOTTOM)
        DISPLAYSURF.blit(title_surf, title_rect)
        DISPLAYSURF.blit(subtitle_surf, subtitle_rect)

        mouse_pos = pygame.mouse.get_pos()

        for rect, name in zip(button_rects, names):
            accent = LEVELS[name][4]
            hover_color = tuple(min(255, c + 30) for c in accent)
            draw_rounded_button(DISPLAYSURF, rect, accent, hover_color, name, BASICFONT, mouse_pos, radius=18)

        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                for rect, name in zip(button_rects, names):
                    if rect.collidepoint(event.pos):
                        return name

        pygame.display.update()
        FPSCLOCK.tick(FPS)

# off game
def terminate():
    pygame.quit()
    sys.exit()


def check_exit_req():
    for event in pygame.event.get(QUIT):
        terminate()

    for event in pygame.event.get(KEYUP):
        if event.key == K_ESCAPE:
            terminate()
        pygame.event.post(event)

# Auto solved
def start_playing():
    counter = 1
    board = []

    for x in range(w_of_board):
        column = []
        for y in range(h_of_board):
            column.append(counter)
            counter += w_of_board
        board.append(column)
        counter -= w_of_board * (h_of_board - 1) + w_of_board - 1

    board[w_of_board - 1][h_of_board - 1] = BLANK
    return board

# search blank tile
def getBlankPosition(board):
    for x in range(w_of_board):
        for y in range(h_of_board):
            if board[x][y] == BLANK:
                return (x, y)

# swap tile
def take_turn(board, move):
    blankx, blanky = getBlankPosition(board)
    if move == UP:
        board[blankx][blanky], board[blankx][blanky + 1] = board[blankx][blanky + 1], board[blankx][blanky]
    elif move == DOWN:
        board[blankx][blanky], board[blankx][blanky - 1] = board[blankx][blanky - 1], board[blankx][blanky]
    elif move == LEFT:
        board[blankx][blanky], board[blankx + 1][blanky] = board[blankx + 1][blanky], board[blankx][blanky]
    elif move == RIGHT:
        board[blankx][blanky], board[blankx - 1][blanky] = board[blankx - 1][blanky], board[blankx][blanky]


def isValidMove(board, move):
    blankx, blanky = getBlankPosition(board)
    return (move == UP and blanky != len(board[0]) - 1) or \
           (move == DOWN and blanky != 0) or \
           (move == LEFT and blankx != len(board) - 1) or \
           (move == RIGHT and blankx != 0)


def random_moves(board, lastMove=None):
    validMoves = [UP, DOWN, LEFT, RIGHT]

    if lastMove == UP or not isValidMove(board, DOWN):
        validMoves.remove(DOWN)
    if lastMove == DOWN or not isValidMove(board, UP):
        validMoves.remove(UP)
    if lastMove == LEFT or not isValidMove(board, RIGHT):
        validMoves.remove(RIGHT)
    if lastMove == RIGHT or not isValidMove(board, LEFT):
        validMoves.remove(LEFT)

    return random.choice(validMoves)

# tile posision count(X,Y)
def getLeftTopOfTile(block_x, block_y):
    left = XMARGIN + (block_x * block_size) + (block_x - 1)
    top = YMARGIN + (block_y * block_size) + (block_y - 1)
    return (left, top)

# detect mouse click which tile
def getSpotClicked(board, x, y):
    for block_x in range(len(board)):
        for block_y in range(len(board[0])):
            left, top = getLeftTopOfTile(block_x, block_y)
            tileRect = pygame.Rect(left, top, block_size, block_size)
            if tileRect.collidepoint(x, y):
                return (block_x, block_y)
    return (None, None)

# drow puzzle tile
def draw_block(block_x, block_y, number, adjx=0, adjy=0):
    left, top = getLeftTopOfTile(block_x, block_y)
    pad = 3  # small gap between tiles so rounded corners are visible

    # drop shadow for a subtle 3D "raised tile" look
    shadow_rect = pygame.Rect(left + adjx + pad, top + adjy + pad + 4, block_size - pad * 2, block_size - pad * 2)
    pygame.draw.rect(DISPLAYSURF, TILE_SHADOW, shadow_rect, border_radius=TILE_RADIUS)

    tile_rect = pygame.Rect(left + adjx + pad, top + adjy + pad, block_size - pad * 2, block_size - pad * 2)
    pygame.draw.rect(DISPLAYSURF, CURRENT_ACCENT, tile_rect, border_radius=TILE_RADIUS)
    # thin lighter top edge highlight for extra depth
    pygame.draw.rect(DISPLAYSURF, TILE_COLOR_LIGHT, tile_rect, width=2, border_radius=TILE_RADIUS)

    number_font = pygame.font.Font('freesansbold.ttf', max(16, int(block_size / 3.2)))
    text_rendering = number_font.render(str(number), True, TEXT_COLOR)
    text_in_rect = text_rendering.get_rect(center=tile_rect.center)
    DISPLAYSURF.blit(text_rendering, text_in_rect)

# Make text surface
def makeText(text, color, bgcolor, top, left, font=None):
    if font is None:
        font = BASICFONT
    text_rendering = font.render(text, True, color)
    text_in_rect = text_rendering.get_rect()
    text_in_rect.topleft = (top, left)
    return (text_rendering, text_in_rect)

# drow full screen(background, board, tile, buttons, message, border)
def drawBoard(board, message, reset_rect, new_rect, solve_rect, menu_rect):
    draw_gradient_background(DISPLAYSURF, BG_TOP, BG_BOTTOM)

    # ---- message pill (top-left, floating badge instead of plain text) ----
    if message:
        msg_font = BASICFONT
        text_surf = msg_font.render(message, True, MESSAGE_TEXT)
        badge_rect = pygame.Rect(0, 0, text_surf.get_width() + 40, text_surf.get_height() + 24)
        badge_rect.topleft = (30, 25)
        pygame.draw.rect(DISPLAYSURF, MESSAGE_BG, badge_rect, border_radius=14)
        pygame.draw.rect(DISPLAYSURF, CURRENT_ACCENT, badge_rect, width=2, border_radius=14)
        text_rect = text_surf.get_rect(center=badge_rect.center)
        DISPLAYSURF.blit(text_surf, text_rect)

    # ---- panel behind the board so the tiles pop out visually ----
    left, top = getLeftTopOfTile(0, 0)
    width = w_of_board * block_size
    height = h_of_board * block_size
    panel_pad = 22
    panel_rect = pygame.Rect(left - panel_pad, top - panel_pad, width + panel_pad * 2, height + panel_pad * 2)
    pygame.draw.rect(DISPLAYSURF, BOARD_PANEL_COLOR, panel_rect, border_radius=20)
    pygame.draw.rect(DISPLAYSURF, BORDER_COLOR, panel_rect, width=3, border_radius=20)

    for block_x in range(len(board)):
        for block_y in range(len(board[0])):
            if board[block_x][block_y]:
                draw_block(block_x, block_y, board[block_x][block_y])

    # ---- sidebar panel with title + buttons ----
    sidebar_rect = pygame.Rect(SIDEBAR_X, SIDEBAR_Y, SIDEBAR_WIDTH, SIDEBAR_HEIGHT)
    pygame.draw.rect(DISPLAYSURF, SIDEBAR_COLOR, sidebar_rect, border_radius=SIDEBAR_RADIUS)
    pygame.draw.rect(DISPLAYSURF, CURRENT_ACCENT, sidebar_rect, width=2, border_radius=SIDEBAR_RADIUS)

    sidebar_title = BASICFONT.render('Slide Puzzle', True, TEXT_COLOR)
    DISPLAYSURF.blit(sidebar_title, sidebar_title.get_rect(center=(SIDEBAR_X + SIDEBAR_WIDTH // 2, SIDEBAR_Y + 50)))

    level_label = SMALLFONT.render(f'{w_of_board} x {h_of_board} board', True, (148, 163, 184))
    DISPLAYSURF.blit(level_label, level_label.get_rect(center=(SIDEBAR_X + SIDEBAR_WIDTH // 2, SIDEBAR_Y + 85)))

    mouse_pos = pygame.mouse.get_pos()
    draw_rounded_button(DISPLAYSURF, reset_rect, BUTTON_COLOR, BUTTON_HOVER_COLOR, 'Reset', BASICFONT, mouse_pos)
    draw_rounded_button(DISPLAYSURF, new_rect, BUTTON_COLOR, BUTTON_HOVER_COLOR, 'New Game', BASICFONT, mouse_pos)
    draw_rounded_button(DISPLAYSURF, solve_rect, BUTTON_COLOR, BUTTON_HOVER_COLOR, 'Solve', BASICFONT, mouse_pos)
    draw_rounded_button(DISPLAYSURF, menu_rect, (100, 116, 139), (148, 163, 184), 'Change Level', BASICFONT, mouse_pos)

# Show tile slide animation
def sliding_animation(board, direction, message, animationSpeed, reset_rect, new_rect, solve_rect, menu_rect):
    blankx, blanky = getBlankPosition(board)

    if direction == UP:
        move_in_xaxis = blankx
        move_in_yaxis = blanky + 1
    elif direction == DOWN:
        move_in_xaxis = blankx
        move_in_yaxis = blanky - 1
    elif direction == LEFT:
        move_in_xaxis = blankx + 1
        move_in_yaxis = blanky
    elif direction == RIGHT:
        move_in_xaxis = blankx - 1
        move_in_yaxis = blanky

    drawBoard(board, message, reset_rect, new_rect, solve_rect, menu_rect)
    baseSurf = DISPLAYSURF.copy()

    take_left, take_top = getLeftTopOfTile(move_in_xaxis, move_in_yaxis)
    pad = 3
    erase_rect = pygame.Rect(take_left + pad, take_top + pad - 6, block_size - pad * 2, block_size - pad * 2 + 12)
    # repaint that spot with the panel color (since board panel sits behind tiles now)
    pygame.draw.rect(baseSurf, BOARD_PANEL_COLOR, erase_rect, border_radius=TILE_RADIUS)

    for i in range(0, block_size, animationSpeed):
        check_exit_req()
        DISPLAYSURF.blit(baseSurf, (0, 0))

        if direction == UP:
            draw_block(move_in_xaxis, move_in_yaxis,
                       board[move_in_xaxis][move_in_yaxis], 0, -i)
        if direction == DOWN:
            draw_block(move_in_xaxis, move_in_yaxis,
                       board[move_in_xaxis][move_in_yaxis], 0, i)
        if direction == LEFT:
            draw_block(move_in_xaxis, move_in_yaxis,
                       board[move_in_xaxis][move_in_yaxis], i, 0)
        if direction == RIGHT:
            draw_block(move_in_xaxis, move_in_yaxis,
                       board[move_in_xaxis][move_in_yaxis], -i, 0)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def generateNewPuzzle(numSlides):
    sequence = []
    board = start_playing()

    # placeholder button rects just so drawBoard can render during shuffle animation
    reset_rect = pygame.Rect(SIDEBAR_X + 30, 220, BUTTON_W, BUTTON_H)
    new_rect = pygame.Rect(SIDEBAR_X + 30, 220 + (BUTTON_H + 20), BUTTON_W, BUTTON_H)
    solve_rect = pygame.Rect(SIDEBAR_X + 30, 220 + 2 * (BUTTON_H + 20), BUTTON_W, BUTTON_H)
    menu_rect = pygame.Rect(SIDEBAR_X + 30, 220 + 3 * (BUTTON_H + 20), BUTTON_W, BUTTON_H)

    drawBoard(board, '', reset_rect, new_rect, solve_rect, menu_rect)
    pygame.display.update()
    pygame.time.wait(500)

    lastMove = None
    for i in range(numSlides):
        move = random_moves(board, lastMove)
        sliding_animation(board, move, 'Generating new puzzle...',
                          int(block_size / 3), reset_rect, new_rect, solve_rect, menu_rect)
        take_turn(board, move)
        sequence.append(move)
        lastMove = move

    return (board, sequence)


def rst_animation(board, allMoves, reset_rect, new_rect, solve_rect, menu_rect):
    reverse_moves = allMoves[:]
    reverse_moves.reverse()

    for move in reverse_moves:
        if move == UP:
            opp_moves = DOWN
        elif move == DOWN:
            opp_moves = UP
        elif move == RIGHT:
            opp_moves = LEFT
        elif move == LEFT:
            opp_moves = RIGHT

        sliding_animation(board, opp_moves, '',
                          int(block_size / 2), reset_rect, new_rect, solve_rect, menu_rect)
        take_turn(board, opp_moves)


if __name__ == '__main__':
    main()
