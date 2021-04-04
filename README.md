# CS420-Project-1-Hide-and-Seek

In this project, we aim to implement intelligent agents who are involved in the game called Hide and Seek, using basic searching and optimization techniques.

* There are 4 levels:
Level 1: 1 seeker - 1 hider. Hider can not move
Level 2: 1 seeker - many hider. Hider can not move
Level 3: 1 seeker - many hider. Hider can move
Level 4: 1 seeker - many hider. Hider can move, agent can move obstabcle

* Code Structure:
|
|--- asset: image of agent for front end
|
|--- level123: code for level 1 - 2 -3
|
|--- level4: code forlevel 4
|
|--- map: data of map

* Map structure:

We design map for each level with format x.y.txt
x: level
y: index (1..)
eg: 1.2.txt - 2.4.txt

* How to run:

- For level 1-2-3 go to folder level123, run this command in terminal:

python3 main.py -l x -m y
-l: level
-m: map
eg: python3 main.py -l 3 -m 3.4


- For level 4 go to folder level4, run this command in terminal:

python3 main.py -m y
-m: map
eg: python3 main.py -m 4.1
