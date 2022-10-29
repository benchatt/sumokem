#! /usr/bin/python3.8
#sumokem if you gottem
#sumoku generator
import random
import svgwrite
from time import time

BASE = 9; CELL = 90

def adjacents(x,y,xmax,ymax):
    adjs = []
    for xi in range(x-1,x+2):
        for yi in range(y-1,y+2):
            if (xi==x) ^ (yi==y):
                if not (xi < 0 or yi < 0):
                    if not (xi > xmax or yi > ymax):
                        adjs.append((xi,yi))
    return adjs

def pack(omino, ogrid):
    ordercs = [(x,y) for x in range(BASE) for y in range(BASE)]
    coords = []
    for i in range((BASE*2)+1):
        coords.extend([l for l in ordercs if sum(l) == i])
    walk = sorted(coords,key=lambda x: max(x)+(sum(x)/2))
    for w in walk:
        res = ogrid.fit(omino,w[0],w[1])
        if res:
            return res
    return False

class Ogrid:
    def __init__(self,grid):
        self.grid = grid
        self.ominogrid = [[None for x in range(len(grid[0]))] for y in range(len(grid))]
        self.ominoes = []

    def full(self):
        for x in range(len(self.ominogrid)):
            for y in range(len(self.ominogrid[0])):
                if self.ominogrid[x][y] is None:
                    holes = False
                    for a in adjacents(x,y,len(self.ominogrid)-1,len(self.ominogrid[0])-1):
                        if self.ominogrid[a[0]][a[1]] is None:
                            holes = True
                            break
                    if not holes:
                        return None
        for line in self.ominogrid:
            if len([i for i in line if i is not None]) < BASE:
                return False
        return True

    def fit(self,omino,x,y):
        fully = self.full()
        if fully is None:
            return "IMPOSSIBLE"
        elif fully:
            return "FULL"
        for col in range(x,x+omino.dim[0]):
            for row in range(y,y+omino.dim[1]):
                if col >= len(self.ominogrid) or row >= len(self.ominogrid[0]):
                    return False
                if self.ominogrid[row][col] is not None:
                    return False
        for col in range(x,x+omino.dim[0]):
            for row in range(y,y+omino.dim[1]):
                self.ominogrid[row][col] = omino
                omino.value += self.grid[row][col]
        if omino.x is None:
            omino.x = x
            omino.y = y
            self.ominoes.append(omino)
        return True
    
    def difficulty(self):
        invdiff = 0
        for om in self.ominoes:
            z = max(om.dim)
            if (om.value / 2.4 < z) or (om.value / 7.55 > z):
                invdiff += 1
        return (10 - invdiff)

class Omino:
    def __init__(self,id):
        self.generate()
        self.id = id
        self.x = None
        self.y = None
        self.value = 0
    
    def generate(self):
        dims = [[1,2],[1,3],[2,1],[3,1],[1,2],[2,1],[1,2],[2,1],[1,2],[2,1],[1,2],[2,1],[1,2],[2,1],[1,2],[2,1],[1,2],[2,1]]
        self.dim = random.choice(dims)

def formed(grid):
    for row in grid:
        for i in range(1,BASE+1):
            if row.count(i) > 1:
                return False
    for y in range(BASE):
        col = [grid[x][y] for x in range(BASE)]
        for i in range(1,BASE+1):
            if col.count(i) > 1:
                return False
    return True

def newmain():
    possible = True; zeroth = True
    print('Generating sumoku puzzle..',end='',flush=True)
    while not possible or zeroth:
        possible = True
        zeroth = False
        grid = [[0 for x in range(BASE)] for y in range(BASE)]
        for row in range(BASE-1):
            first = True
            while first or not formed(grid):
                first = False
                nums = list(range(1,BASE+1))
                random.shuffle(nums)
                grid[row] = nums
        print('.',end='',flush=True)
        for i in range(BASE):
            if not possible:
                break
            ff = True; ii = 0
            while ff or not formed(grid):
                ff = False
                ii += 1
                grid[BASE-1][i] = random.randint(1,BASE)
                if ii > 50:
                    possible = False
                    [print(' '.join([str(i) for i in r])) for r in grid]
                    print('give up')
                    break
    print('.',end='',flush=True)
    p = None; q = None
    while p != 'FULL' or q > 6 or q < 4:
        p = None
        ogrid = Ogrid(grid)
        i = 0
        while type(p) is not str:
            i+=1
            omino = Omino(i)
            p = pack(omino,ogrid)
        q = ogrid.difficulty()

    print('.',end='',flush=True)
    stamp = hex(int(time()))[2:]
    xpad = 7
    ypad = 7
    mpad = 5
    swidth = 3
    xmax = (len(grid))*CELL
    ymax = (len(grid[0]))*CELL
    droring = svgwrite.Drawing(stamp+'.svg',(xmax+(xpad*2),ymax+(ypad*2)),profile='tiny')
    droring.add(droring.rect(insert=(0, 0), size=('100%', '100%'), rx=None, ry=None, fill='white',stroke='black'))
    for xs in range(xpad,xmax+xpad+1,CELL):
        for ys in range(ypad,ymax+ypad+1,CELL):
            droring.add(droring.line((xs,ys),(xs,ymax),stroke='black',stroke_width=swidth-1))
            droring.add(droring.line((xs,ys),(xmax,ys),stroke='black',stroke_width=swidth-1))

    for om in ogrid.ominoes:
        xa = (om.x*CELL)+mpad+xpad
        dx = (om.dim[0]*CELL)-(mpad*2)
        ya = (om.y*CELL)+mpad+ypad
        dy = (om.dim[1]*CELL)-(mpad*2)
        xt = xa + (2*mpad)
        yt = ya + mpad+(2*ypad)
        droring.add(droring.rect(insert=(xa,ya),size=(dx,dy),rx=5,stroke='black',stroke_width=swidth,fill='white',fill_opacity=0.01))
        droring.add(droring.text(str(om.value),insert=(xt,yt),font_size=(xpad*3),stroke='black'))
    droring.save()
    print('.done.',flush=True)
    print('Your puzzle is saved at '+stamp+'.svg and the answer is at '+stamp+'.txt')
    with open(stamp+'.txt','w') as fh:
        fh.writelines([' '.join([str(it) for it in line])+'\n' for line in ogrid.grid])
    print('ok' if ogrid.grid == grid else 'error')

if __name__ == '__main__':
    newmain()