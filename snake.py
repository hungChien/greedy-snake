#coding=utf-8
import os, time, random
from evdev import InputDevice
from select import select

def detectInputKey(time_out):
    """
    a: 30, d: 32, w: 17, s: 31
    left: 105, right: 106, up: 103, down: 108
    """
    dev = InputDevice('/dev/input/event4')
    res = select([dev], [], [], time_out)
    if res == ([], [], []): return
    for event in dev.read():
        if event.value > 0 and event.code != 0:
            if event.code == 30 or event.code == 105:
                return "L"
            elif event.code == 32 or event.code == 106:
                return "R"
            elif event.code == 17 or event.code == 103:
                return "U"
            elif event.code == 31 or event.code == 108:
                return "D"
class Snake():
    def __init__(self, area_shape):
        w, h = area_shape
        self.init_length = 5
        self.body = []
        self.init_head_position = random.randint(2, h-self.init_length-2), random.randint(5, w-self.init_length-5)
        self.body.append(self.init_head_position)
        for i in xrange(1, self.init_length):
            self.body.append((self.init_head_position[0], self.init_head_position[1]+i))
class Game():
    def __init__(self):
        self.area_width = 50
        self.area_height = 15
        self.score = 0
        self.wall_mark = "+"
        self.snake_mark = "*"
        self.head_mark = "@"
        self.goal_mark = "#"
        self.pixels = [" "] * (self.area_width*self.area_height)
        self.snake = Snake((self.area_width, self.area_height))
        self.goal = (10, 30)
        self.cur_direction = "L"
        self.cmd_lst = ['U', 'R', 'D', 'L']
    def initPixels(self):
        for i in xrange(len(self.snake.body)):
            x, y = self.snake.body[i]
            marker = self.head_mark if i==0 else self.snake_mark
            self.pixels[x*self.area_width+y] = marker
        self.pixels[self.goal[0]*self.area_width+self.goal[1]] = self.goal_mark
    def genGoal(self):
        while 1:
            goal = (random.randint(0, self.area_height-1), random.randint(0, self.area_width-1))
            if not goal in self.snake.body: break
        return goal
    def updatePixels(self):
        """direction: U, up; D, down; L, left; R, right
        """
        def comp_new_block(body, direction):
            head = body[0]
            if direction=="U":
                new_block = (head[0]-1, head[1])
            elif direction == "D":
                new_block = (head[0]+1, head[1])
            elif direction == "L":
                new_block = (head[0], head[1]-1)
            elif direction == "R":
                new_block = (head[0], head[1]+1)
            return new_block
        direction = self.cur_direction
        new_block =  comp_new_block(self.snake.body, direction)
        # 碰撞检测
        if new_block[0]<0 or new_block[1]<0 or \
         new_block[0]>=self.area_height or new_block[1] >= self.area_width:
            return "wall collision"
        if new_block in self.snake.body:
            # 头尾相接不算self collision
            if new_block!=self.snake.body[-1]:
                return "self collision"
        # 目标符号
        self.pixels[self.goal[0]*self.area_width+self.goal[1]] = self.goal_mark

        # 改变原来的蛇头符号
        head = self.snake.body[0]
        self.pixels[head[0]*self.area_width+head[1]] = self.snake_mark
        # 是否撞到目标检测
        if new_block == self.goal:
            self.score += 1
            # 改变目标符号
            self.pixels[new_block[0]*self.area_width+new_block[1]] = self.snake_mark
            self.snake.body.insert(0, new_block)
            new_block = comp_new_block(self.snake.body, direction)
            self.goal = self.genGoal()
        # 改变新蛇头的符号
        # 考虑目标出现在墙边的情况
        if not (new_block[0]<0 or new_block[1]<0 or \
                     new_block[0]>=self.area_height or new_block[1] >= self.area_width):
            self.snake.body.insert(0, new_block)
            head = self.snake.body[0]
            self.pixels[head[0]*self.area_width+head[1]] = self.head_mark
        # 去掉蛇尾
        tail = self.snake.body[-1]
        self.pixels[tail[0]*self.area_width+tail[1]] = " "
        self.snake.body.pop(-1)
    def render(self):
        os.system("clear")
        print("Score: %3d" % self.score )
        print(self.wall_mark * (self.area_width + 2))
        for i in xrange(self.area_height):
            print(self.wall_mark + "".join(self.pixels[i*self.area_width:(i+1)*self.area_width]) + self.wall_mark)
        print(self.wall_mark * (self.area_width+2))
        time.sleep(.005) # 防止闪屏
    def compDirection(self, time_out):
        cmd = detectInputKey(time_out)
        if cmd!=None:
            self.cur_direction = cmd
    def spin(self):
        self.initPixels()
        inherent_time = 0.2
        while 1:
            self.render()
            start = time.time()
            self.compDirection(inherent_time)
            elapsed = time.time() - start
            if elapsed < inherent_time:
                time.sleep(inherent_time - elapsed) #保证每两次间的间隔是相同的
            res = self.updatePixels()
            if res!=None:
                print(res)
                print("Game Over.")
                break

def main():
    game = Game()
    game.spin()
        
if __name__ == '__main__':
    main()