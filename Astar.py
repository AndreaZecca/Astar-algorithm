import pygame
import math
from queue import PriorityQueue

WIDTH = 800

WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Path Finding Algorithm Visualization")

COLOR = {
    "RED": (255,0,0), # closed
    "GREEN": (0,255,0), # open
    "BLUE": (0,0,255), # path
    "YELLOW": (255,255,0), # 
    "WHITE": (255,255,255), # free
    "BLACK": (0,0,0), # wall
    "PURPLE": (128,0,128), # end
    "ORANGE": (255,165,0), # start
    "GREY": (128,128,128), #  
    "TURQUOISE": (64,225,208) # end
}


class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = COLOR["WHITE"]
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col
    
    def is_state(self, color):
        return self.color == COLOR[color]

    def reset(self):
        self.color = COLOR["WHITE"]

    def set_state(self, state):
        self.color = COLOR[state]

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_state("BLACK"): # DOWN
            self.neighbors.append(grid[self.row + 1][self.col])    

        if self.row > 0 and not grid[self.row - 1][self.col].is_state("BLACK"): # UP
            self.neighbors.append(grid[self.row - 1][self.col]) 
            
        if self.col > 0 and not grid[self.row][self.col - 1].is_state("BLACK"): # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])  

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_state("BLACK"): # RIGHT
            self.neighbors.append(grid[self.row][self.col + 1]) 
    def __lt__(self, other):
        return False

# Heuristic function (using Manhattan distance)
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0,count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())
    
    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        current = open_set.get()[2]
        open_set_hash.remove(current)
        if current == end:
            reconstruct_path(came_from, end, draw)
            end.set_state("PURPLE")
            return True
        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1
            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.set_state("GREEN")
        draw()

        if current != start:
            current.set_state("RED")
    return False

def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.set_state("BLUE")
        draw()

def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)
    return grid

def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, COLOR["GREY"], (0, i*gap), (width, i*gap))
    for j in range(rows):
        pygame.draw.line(win, COLOR["GREY"], (j*gap, 0), (j*gap, width))
    

def draw(win, grid, rows, width):
    win.fill(COLOR["WHITE"])

    for row in grid:
        for spot in row:
            spot.draw(win)
    
    draw_grid(win, rows, width)
    pygame.display.update()

def get_clicked_pos(pos, rows, width):
    gap = width//rows
    y,x = pos

    row = y//gap
    col = x//gap

    return row, col

def main(win, width):
    rows = 50
    grid = make_grid(rows, width)

    start = None
    end = None

    run = True
    started = False

    while run:
        draw(win, grid, rows, width)
        for event in pygame.event.get():
            if(event.type == pygame.QUIT):
                run = False
            if started:
                continue
            if pygame.mouse.get_pressed()[0]: # LEFT
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, rows, width)
                spot = grid[row][col]
                if not start and spot != end:
                    start = spot
                    start.set_state("ORANGE")
                elif not end and spot != start:
                    end = spot
                    end.set_state("TURQUOISE")
                elif spot != end and spot != start:
                    spot.set_state("BLACK")
            elif pygame.mouse.get_pressed()[2]: # RIGHT
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, rows, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not started:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)
                    algorithm(lambda: draw(win, grid, rows, width), grid, start, end)
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(rows, width)
    pygame.quit()

main(WIN, WIDTH)
