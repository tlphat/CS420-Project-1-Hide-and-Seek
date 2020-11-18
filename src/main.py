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

    game.printMap()
    print('HIDER:')
    print(hider.getLocation(0))
    print('SEEKER:')
    print(seeker.getLocation(0))

    check = [0 for i in range(len(hider.cell))]

    # print(seeker.heuristic)

    for turn in range(10000):
        if turn % 2 == 1:
            seeker.next_move()
        else:
            hider.next_move()

        if hider.isAnnouce():
            gui.display_announce(hider.getAnnouce())
            seeker.updateAnnouce(hider.getAnnouce())

        for hide in range(len(hider.cell)):
           if check[hide] == 0 and seeker.isInsideRange(seeker.cell[0][0], seeker.cell[0][1], hider.cell[hide][0], hider.cell[hide][1]):
               check[hide] = 1
               print('I am at: ', seeker.cell[0])
               print('I can see hider at:', hider.cell[hide])
               seeker.updateHider(hider.cell[hide][0], hider.cell[hide][1])
        
        if seeker.hiderFound == len(hider.cell):
            print()
            print()
            print('Seeker win')
            print('Turn: ', turn)
            print("Has found: ", seeker.hiderFound)
            print('Seeker move: ', seeker.move)
            print('Hider move: ', hider.move)
            print(seeker.print_map())
            gui.visualize()
            exit(0)

    print()
    print()
    print('Seeker loose')
    print('Seeker move: ', seeker.move)
    print('Hider move: ', hider.move)
    print("Has found: ", seeker.hiderFound)
    print(seeker.print_map())
    gui.visualize()
        
