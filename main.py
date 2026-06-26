import pygame
import random
import sys

# ===========================
# 定数定義
# ===========================
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

COLS = 10
ROWS = 20
CELL_SIZE = 30

FIELD_LEFT = (SCREEN_WIDTH - COLS * CELL_SIZE) // 2
FIELD_TOP = (SCREEN_HEIGHT - ROWS * CELL_SIZE) // 2

FPS = 60
FALL_INTERVAL = 500  # ミリ秒（0.5秒ごとに1マス落下）

# 色定義
BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
GRAY   = (128, 128, 128)
CYAN   = (0,   255, 255)
YELLOW = (255, 255, 0)
PURPLE = (160, 0,   255)

# ===========================
# ブロック定義
# ===========================
SHAPES = {
    "I": {
        "shape": [
            [1, 1, 1, 1]
        ],
        "color": CYAN,
    },
    "O": {
        "shape": [
            [1, 1],
            [1, 1]
        ],
        "color": YELLOW,
    },
    "T": {
        "shape": [
            [0, 1, 0],
            [1, 1, 1]
        ],
        "color": PURPLE,
    },
}

SHAPE_KEYS = list(SHAPES.keys())


# ===========================
# フィールド管理
# ===========================
def create_board():
    """空のフィールドを生成する"""
    return [[0 for _ in range(COLS)] for _ in range(ROWS)]


# ===========================
# ブロック生成
# ===========================
def new_piece():
    """ランダムにブロックを生成し、初期位置（上部中央）に配置する"""
    key = random.choice(SHAPE_KEYS)
    shape = [row[:] for row in SHAPES[key]["shape"]]
    color = SHAPES[key]["color"]
    x = COLS // 2 - len(shape[0]) // 2
    y = 0
    return {"shape": shape, "color": color, "x": x, "y": y}


# ===========================
# 衝突判定
# ===========================
def is_valid_position(board, piece, offset_x=0, offset_y=0):
    """
    ブロックが指定オフセット移動後に有効な位置にあるか判定する。
    フィールド外・既存ブロックとの重なりを検出する。
    """
    shape = piece["shape"]
    px = piece["x"] + offset_x
    py = piece["y"] + offset_y

    for row_idx, row in enumerate(shape):
        for col_idx, cell in enumerate(row):
            if cell == 0:
                continue
            nx = px + col_idx
            ny = py + row_idx
            # フィールド外チェック
            if nx < 0 or nx >= COLS or ny < 0 or ny >= ROWS:
                return False
            # 既存ブロックとの重なりチェック
            if board[ny][nx] != 0:
                return False
    return True


# ===========================
# 回転処理
# ===========================
def rotate_shape(shape):
    """行列の転置＋各行を反転して時計回り90度回転する"""
    transposed = [list(row) for row in zip(*shape)]
    rotated = [row[::-1] for row in transposed]
    return rotated


# ===========================
# ブロック固定
# ===========================
def lock_piece(board, piece):
    """現在のブロックをフィールドに固定する"""
    shape = piece["shape"]
    color = piece["color"]
    for row_idx, row in enumerate(shape):
        for col_idx, cell in enumerate(row):
            if cell:
                bx = piece["x"] + col_idx
                by = piece["y"] + row_idx
                board[by][bx] = color


# ===========================
# ライン削除
# ===========================
def clear_lines(board):
    """
    横一列が全て埋まった行を削除し、上の行を下へシフトする。
    削除した行数を返す。
    """
    new_board = [row for row in board if any(cell == 0 for cell in row)]
    cleared = ROWS - len(new_board)
    # 削除した行数分、上部に空行を追加
    for _ in range(cleared):
        new_board.insert(0, [0 for _ in range(COLS)])
    # board をインプレースで更新
    for i in range(ROWS):
        board[i] = new_board[i]
    return cleared


# ===========================
# 描画処理
# ===========================
def draw_board(surface, board):
    """フィールドに固定されたブロックを描画する"""
    for row_idx, row in enumerate(board):
        for col_idx, cell in enumerate(row):
            x = FIELD_LEFT + col_idx * CELL_SIZE
            y = FIELD_TOP + row_idx * CELL_SIZE
            if cell != 0:
                pygame.draw.rect(surface, cell, (x, y, CELL_SIZE - 1, CELL_SIZE - 1))
            else:
                pygame.draw.rect(surface, GRAY, (x, y, CELL_SIZE - 1, CELL_SIZE - 1), 1)


def draw_piece(surface, piece):
    """落下中のブロックを描画する"""
    shape = piece["shape"]
    color = piece["color"]
    for row_idx, row in enumerate(shape):
        for col_idx, cell in enumerate(row):
            if cell:
                x = FIELD_LEFT + (piece["x"] + col_idx) * CELL_SIZE
                y = FIELD_TOP + (piece["y"] + row_idx) * CELL_SIZE
                pygame.draw.rect(surface, color, (x, y, CELL_SIZE - 1, CELL_SIZE - 1))


def draw_game_over(surface):
    """ゲームオーバー画面を描画する"""
    font_large = pygame.font.SysFont(None, 60)
    font_small = pygame.font.SysFont(None, 36)
    text1 = font_large.render("GAME OVER", True, WHITE)
    text2 = font_small.render("Close window to exit", True, GRAY)
    surface.blit(text1, (SCREEN_WIDTH // 2 - text1.get_width() // 2,
                          SCREEN_HEIGHT // 2 - text1.get_height()))
    surface.blit(text2, (SCREEN_WIDTH // 2 - text2.get_width() // 2,
                          SCREEN_HEIGHT // 2 + 10))


# ===========================
# メイン処理
# ===========================
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("テトリス（簡易版）")
    clock = pygame.time.Clock()

    board = create_board()
    current_piece = new_piece()
    game_over = False

    fall_timer = 0  # 落下タイマー（ミリ秒）

    while True:
        dt = clock.tick(FPS)  # 前フレームからの経過時間（ミリ秒）

        # ===== イベント処理 =====
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if not game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if is_valid_position(board, current_piece, offset_x=-1):
                        current_piece["x"] -= 1

                elif event.key == pygame.K_RIGHT:
                    if is_valid_position(board, current_piece, offset_x=1):
                        current_piece["x"] += 1

                elif event.key == pygame.K_DOWN:
                    if is_valid_position(board, current_piece, offset_y=1):
                        current_piece["y"] += 1

                elif event.key == pygame.K_UP:
                    rotated = rotate_shape(current_piece["shape"])
                    original_shape = current_piece["shape"]
                    current_piece["shape"] = rotated
                    if not is_valid_position(board, current_piece):
                        # 回転後に衝突する場合は元に戻す
                        current_piece["shape"] = original_shape

        # ===== 落下処理 =====
        if not game_over:
            fall_timer += dt
            if fall_timer >= FALL_INTERVAL:
                fall_timer = 0
                if is_valid_position(board, current_piece, offset_y=1):
                    current_piece["y"] += 1
                else:
                    # 固定処理
                    lock_piece(board, current_piece)
                    # ライン削除
                    clear_lines(board)
                    # 新しいブロック生成
                    current_piece = new_piece()
                    # ゲームオーバー判定
                    if not is_valid_position(board, current_piece):
                        game_over = True

        # ===== 描画処理 =====
        screen.fill(BLACK)
        draw_board(screen, board)
        if not game_over:
            draw_piece(screen, current_piece)
        else:
            draw_game_over(screen)
        pygame.display.flip()


if __name__ == "__main__":
    main()
