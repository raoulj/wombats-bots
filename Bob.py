import random
global random

log = {}
width = 7
height = 7
bored = 0
path = []
targetCoords = []
targetTile = 0
currState = 0
frontier = []
searched = []
fromTile = []
shotDamage = 10

global getArena
def getArena():
    return currState['arena']


global getTile
def getTile(x, y):
    return getArena()[y][x] # TODO: reversed, investigate


global getPlayerTile
def getPlayerTile():
    return getTile(getCoords()[0], getCoords()[1])


global getCoords
def getCoords():
    return currState['local-coords']


global getType
def getType(tile):
    return tile['contents']['type']


global isPoison
def isPoison(tile):
    return getType(tile) == 'poison'


global isWall
def isWall(tile):
    return isWoodWall(tile) or getType(tile) == 'steel-barrier'


global isWoodWall
def isWoodWall(tile):
    return getType(tile) == 'wood-barrier'


global isOtherWombat
def isOtherWombat(x, y, tile):
    return getType(tile) == 'wombat' and [x, y] != getCoords()


global getHp
def getHp(tile):
    if 'contents' in tile.keys():
        if 'hp' in tile['contents'].keys():
            return tile['contents']['hp']
    return 0


global isFog
def isFog(tile):
    return getType(tile) == 'fog'


global isSmoke
def isSmoke(tile):
    return getType(tile) == 'smoke'


global isZakano
def isZakano(tile):
    return getType(tile) == 'zakano'


global isFood
def isFood(tile):
    return getType(tile) == 'food'


global isEnemy
def isEnemy(x, y, tile):
    return isOtherWombat(x, y, tile) or isWoodWall(tile) or isZakano(tile)


global getValue
def getValue(x, y, tile):

    global shotDamage

    if isFood(tile):
        if getHp(getPlayerTile()) < shotDamage * 2:   # always get food if < 2 shots hp
            return 16
        return 5
    elif isZakano(tile):
        if getHp(tile) <= shotDamage:
            return 10
        elif getHp(tile) <= shotDamage * 2:
            return 4
        return 2
    elif isOtherWombat(x, y, tile):
        if getHp(tile) <= shotDamage:
            return 15
        elif getHp(tile) <= shotDamage * 2:
            return 7
        return 3
    elif isWoodWall(tile):
        return 1.5
    return 0


global getOrientationVector
def getOrientationVector():
    orientation = getTile(getCoords()[0], getCoords()[1])['contents']['orientation']
    if orientation == 'n':
        return [0, -1]
    if orientation == 'w':
        return [-1, 0]
    if orientation == 's':
        return [0, 1]
    if orientation == 'e':
        return [1, 0]


global getTurnToVectorDirection
def getTurnToVectorDirection(vector):
    orientationVector = getOrientationVector()
    sumVector = [vector[0] + orientationVector[0], vector[1] + orientationVector[1]]
    if sumVector == [0,0]:
        return "about-face"
    prod = sumVector[0] * sumVector[1]
    if orientationVector[0] == 0:
        # north/south facing
        if prod == -1:
            return "right"
        return "left"

    # east/west facing
    if prod == -1:
        return "left"
    return "right"


global turn
def turn(direction):
    return {'action': 'turn', 'metadata': {'direction': direction}}


global moveForward
def moveForward():
    return {'action': 'move', 'metadata': {}}


global shoot
def shoot():
    return {'action': 'shoot', 'metadata': {}}


# build path to coordinate backwards
# inserts at 0 so result is in order
global pathToTile
def pathToTile(x, y):
    buildPath = []
    currInPath = [x, y]
    while currInPath != getCoords():
        currVector = fromTile[currInPath[0]][currInPath[1]]
        currVector = [currVector[0], currVector[1]]
        currInPath[0] = currInPath[0] + currVector[0]
        currInPath[1] = currInPath[1] + currVector[1]
        currVector[0] *= -1
        currVector[1] *= -1
        buildPath.insert(0, currVector)
    return buildPath


# figure out how many turns the path takes
global getPathTime
def getPathTime(path, tileCoords, currDirection):
    totalTime = 0
    for i in range(0, len(path)):
        totalTime += 1
        if currDirection != path[i]:
            totalTime += 1  # add turn for turning
            currDirection = path[i]
    if isEnemy(tileCoords[0], tileCoords[1], getTile(tileCoords[0], tileCoords[1])):
        # add turn for shooting
        totalTime += 1
    return totalTime


# figure out the ratio of value over time used
global getValueTimeRatio
def getValueTimeRatio(x, y, tile):
    tileValue = getValue(x, y, tile)
    path = pathToTile(x, y)
    pathTime = getPathTime(path, [x, y], getOrientationVector())
    if pathTime == 0:
        return 0
    return tileValue / float(pathTime)


global search
def search(x, y, maxTile, maxEv):

    def valid(coord):
        global frontier
        global searched
        tile = getTile(coord[0], coord[1])
        return coord not in searched and coord not in frontier and not \
            isFog(tile) and not isWall(tile) and not isPoison(tile)

    def tryAdd(dx, dy, backVector):
        if valid([dx, dy]):
            global frontier
            global fromTile
            frontier.append([dx, dy])
            fromTile[dx][dy] = backVector

    searchTile = getTile(x, y)
    searchTileEv = getValueTimeRatio(x, y, searchTile)

    if searchTileEv > maxEv or maxTile == []:
        maxEv = searchTileEv
        maxTile = [x,y]

    global frontier
    global searched
    global width
    global height
    searched.append([x, y])

    if x > 0:
        tryAdd(x-1, y, [1, 0])
    if x < width - 1:
        tryAdd(x+1, y, [-1, 0])
    if y > 0:
        tryAdd(x, y-1, [0, 1])
    if y < height - 1:
        tryAdd(x, y+1, [0, -1])

    if len(frontier) == 0:
        return maxTile

    nextTile = frontier.pop(0)
    return search(nextTile[0], nextTile[1], maxTile, maxEv)

def wombat(state, time_left):
    global bored
    global path
    global targetCoords
    global targetTile
    global width
    global height
    global currState
    global fromTile
    global searched
    global frontier
    global command
    global log
    global shotDamage

    # TODO: investigate/replace
    currState = state
    for i in range(width):
        fromTile.append([])
        for j in range(height):
            fromTile[i].append([0,0])

    # restore saved state if existent
    if 'saved-state' in state and state['saved-state']:
        savedState = state['saved-state']
        path = savedState['path']
        targetCoords = savedState['targetCoords']
        targetTile = savedState['targetTile']
        bored = savedState['bored']
    else:
        path = []
        targetCoords = []
        targetTile = 0

    frontier = []
    searched = []

    #Calculate ev of our stored target using the remainder of our saved path
    currTargetTile = 0
    targetEv = 0
    if len(targetCoords) > 1 and len(path) > 0:
        currTargetTile = getTile(targetCoords[0], targetCoords[1])
        targetEv = getValue(targetCoords[0], targetCoords[1], targetTile) \
                   / float(getPathTime(path, targetCoords, getOrientationVector()))

    #Perform search and calculate ev of max value target
    newTargetCoords = search(getCoords()[0], getCoords()[1], [], 0)
    newTargetTile = getTile(newTargetCoords[0], newTargetCoords[1])
    newTargetEv = getValueTimeRatio(newTargetCoords[0], newTargetCoords[1], newTargetTile)

    log['targetEv'] = targetEv
    log['newSearchEv'] = newTargetEv

    # if no path and see something more valuable, or target is no longer valid
    # fog and smoke count as valid since target is likely still there
    if len(path) == 0 or len(targetCoords) < 2 or newTargetEv > targetEv or \
            (getType(currTargetTile) != getType(targetTile) and not
            isSmoke(currTargetTile) and not isFog(currTargetTile)):
        targetCoords = newTargetCoords
        targetTile = newTargetTile
        if targetCoords != getCoords() and len(targetCoords) > 1:
            path = pathToTile(targetCoords[0], targetCoords[1])

    if len(targetCoords) > 1:
        log['targetHp'] = getHp(targetTile)
        log['targetValue'] = getValue(targetCoords[0], targetCoords[1], targetTile)

    # if something right in front, shoot
    shooting = False
    for i in range (1,5):
        dx = getCoords()[0] + i * getOrientationVector()[0]
        dy = getCoords()[1] + i * getOrientationVector()[1]

        if dx > width -1 or dx < 0 or dy > height -1 or dy < 0:
            break
        sightTile = getTile(getCoords()[0] + i * getOrientationVector()[0], getCoords()[1] + i * getOrientationVector()[1])

        # shoot if entity in front, only shoot at wall if nothing else to do
        if isEnemy(dx, dy, sightTile) and not (len(path) > 0 and isWall(sightTile)):
            command = shoot()
            shooting = True
            break

    if not shooting:
        move = [0,0]
        if len(path) == 0:  # no path, move forward for a while
            bored +=1
            if bored > random.randrange(8, 12, 1): # randomize max boredom to prevent loops
                bored = 0
                command = turn('right')
            else:
                command = moveForward()
        else:   # follow path
            bored = 0
            move = path[0]
            if getOrientationVector() == move:
                command = moveForward()
                path.pop(0)
            else:
                command = turn(getTurnToVectorDirection(move))

    # if about to move into a wall or poison, turn right. should only happen when no path
    frontTile = getTile(getCoords()[0] + getOrientationVector()[0], getCoords()[1] + getOrientationVector()[1])
    if command['action'] == 'move':
        if isPoison(frontTile) or isWall(frontTile):
            command = turn('right')

    return {
        'command': command,
        'state': {'path': path, 'targetCoords': targetCoords, 'targetTile': targetTile, 'bored': bored, 'log': log, 'timeLeft': time_left()}
    }
