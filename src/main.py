from defines import *
from level1 import Seeker, Hider
from game import Game

if __name__ == "__main__":
    game = Game()
    game.read_input()
    hider = Hider(game.getMap(), game.getSize(), game.getRangeHider(), game.getHiderLocation())
    seeker = Seeker(game.getMap(), game.getSize(), game.getRangeSeeker(), game.getSeekerLocation())

    for i in range(20):
        seeker.next_move()
        hider.next_move()

        if hider.isAnnouce():
            seeker.updateAnnouce(hider.getAnnouce()[0], hider.getAnnouce()[1])

            print(hider.getAnnouce())
        
