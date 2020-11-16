from defines import *
from level1 import Seeker, Hider
from game import Game
from gui_module import Gui
import timeit

if __name__ == "__main__":

    t = timeit.default_timer()

    gui = Gui()
    game = Game(gui)
    game.read_input("1.1")
    hider = Hider(game.getMap(), game.getSize(), game.getRangeHider(), game.getHiderLocation(), gui)
    seeker = Seeker(game.getMap(), game.getSize(), game.getRangeSeeker(), game.getSeekerLocation(), gui)
    
    t = timeit.default_timer() - t

    print(t)

    game.printMap()
    print('HIDER:')
    print(hider.getLocation(0))
    print('SEEKER:')
    print(seeker.getLocation(0))

    # print(seeker.heuristic)

    seeker.cell.append([1, 16])

    print(seeker.isInsideRange(1, 0, 17))

    for turn in range(300):
        seeker.next_move()
        hider.next_move()

        if hider.isAnnouce():
            gui.display_announce(hider.getAnnouce())
            seeker.updateAnnouce(hider.getAnnouce())
    gui.visualize()
        
