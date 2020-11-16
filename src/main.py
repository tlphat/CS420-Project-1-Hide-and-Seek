from defines import *
from level1 import Seeker, Hider
from game import Game
import timeit

if __name__ == "__main__":

    t = timeit.default_timer()

    game = Game()
    game.read_input()
    hider = Hider(game.getMap(), game.getSize(), game.getRangeHider(), game.getHiderLocation())
    seeker = Seeker(game.getMap(), game.getSize(), game.getRangeSeeker(), game.getSeekerLocation())
    
    t = timeit.default_timer() - t

    print(t)

    game.printMap()
    print('HIDER:')
    print(hider.getLocation(0))
    print('SEEKER:')
    print(seeker.getLocation(0))

    for turn in range(20):
        seeker.next_move()
        #hider.next_move()

        # if hider.isAnnouce():
        #     seeker.updateAnnouce(hider.getAnnouce())

        #     print(hider.getAnnouce())
        
