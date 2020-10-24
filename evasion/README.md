# Evasion Problem
H (the Hunter) wants to catch P (the prey). P wants to evade H as long as possible. You will play both roles (i.e. in the competition, once you will be the hunter and once the prey).

The game is played on a 300 by 300 square. Both P and H bounce off the sides and bounce off any walls created by H. Bouncing is explained below.

P is initially at point ```(230, 200)``` and H at position ```(0,0)```. In a time step, H moves one unit (always diagonally or counter-diagonally based on its bounce history -- the hunter changes direction only when it encounters a wall). P moves only every other time step. P moves one unit in its current direction unless it hits a wall or it decides to move one unit in some other direction or it chooses not to move. A move of P can be in any direction -- vertical, horizontal, diagonal or counter-diagonal. When both P and H move, they move simultaneously. So, it goes like this:
Timestep 1: Hunter moves \
Timestep 2: Hunter and Prey move \
Timestep 3: Hunter moves \
Timestep 4: Hunter and Prey move

H may create a wall not more frequently than every N time steps (where N is a parameter). When H creates a wall, the wall must touch the point where H was before H moved. The wall must be vertical or horizontal or diagonal or counter-diagonal and must touch neither H nor P nor go through another wall (though it may touch another wall). That is, a wall that would hit P if built is not built. The diagonal and counter-diagonal wall are two units thick, so they occupy for example (i,j), (i,j+1), (i+1,j+1), (i+1,j+2). After creating a wall, H must wait at least N time steps before attempting to create another wall. It may be of any length. If H tries to create a wall that violates any of these rules, the system will generate a message on the screen, will not build the wall, but will not otherwise penalize H.

H may destroy any wall regardless of where H is. At any given time the maximum number of walls there can be is M. (N and M will be specified the time of the competition.) H may destroy walls at will -- without waiting. In every time step, all creation or destruction of walls occurs before any player moves in that time step.

H catches P if H is within four units of P (based on Euclidean distance) and there is no wall between them. H's score is the number of time units it takes to catch P. Less is better.

Technical note about bouncing on vertical and horizontal walls: The walls are one unit thick, and centered at integer coordinate. For any integer coordinate that is within a wall, the wall extends (at least) .5 units above, below, left, and right of it. So, if there is a wall from ```(10,200)``` to ```(300,200)``` and a player begins at ```(100, 199)``` moving +1 in x and +1 in y, it will reflect to ```(101, 199)``` at the end of the time step. Neither player will bounce off the narrow side of a wall (except the special case described below). So, a player who begins at ```(9, 200)``` moving +1 in x and +1 in y, it will not reflect and will simply move to ```(10, 201)```, still moving +1 in x and +1 in y. A player who hits a corner of a wall will bounce off as if they hit the middle of the wall. So, a player who begins at ```(9, 199)``` moving +1 in x and +1 in y will reflect and end up at ```(10, 199)``` moving +1 in x and -1 in y.

Note the following cases:

* The hunter builds a wall, let's say horizontally and to the left and right of him, but also bounces off a horizontal wall. In this case, the wall is simply not built because it would "squish" the hunter between walls.
* The prey tries to move directly into the narrow side of the wall. For example, if the prey tries to move left into a horizontal wall, it will bounce bak to its original position.
* There are two parallel walls, again let's say horizontally, with one centered 1 unit above the other and both ending, let's say on the right, at the same x-coordinate. For example, if one horizontal wall ends at ```(40, 40)``` and another horizontal wall ends at ```(40, 41)```. Then if the Hunter is at ```(41, 41)``` moving -1 in x and -1 in y, it will bounce off as if it hit a vertical wall, and end up at ```(41, 40)``` moving +1 in x and -1 in y.

```
Constraints
-----------
2 <= M (max number of walls at any time) <= 10
1 <= N (number of steps between creation of walls) <= 50
```

```
Super-technical: An algorithm for bouncing

The hunter bounce behavior is as follows (* = wall or arena boundary, arrow = hunter moving in the direction it points):

First the pixels adjacent to both the hunter and the one being hit are considered...

+-+-+    +-+-+
|*| |    |*|↗|
+-+-+ -> +-+-+
|*|↖|    |*| |
+-+-+    +-+-+

+-+-+    +-+-+
|*|*|    |*|*|
+-+-+ -> +-+-+
| |↖|    |↙| |
+-+-+    +-+-+

+-+-+    +-+-+
|*|*|    |*|*|
+-+-+ -> +-+-+
|*|↖|    |*|↘|
+-+-+    +-+-+


+-+-+
|*| |
+-+-+  = search is expanded, now including the other pixels adjacent to the one being hit...
| |↖|
+-+-+


  +-+        +-+
  | |        | |
+-+-+-+    +-+-+-+
|*|*| | -> |*|*| |
+-+-+-+    +-+-+-+
  | |↖|      |↙| |
  +-+-+      +-+-+

  +-+        +-+
  |*|        |*|
+-+-+-+    +-+-+-+
| |*| | -> | |*|↗|
+-+-+-+    +-+-+-+
  | |↖|      | | |
  +-+-+      +-+-+

  +-+        +-+
  |*|        |*|
+-+-+-+    +-+-+-+
|*|*| | -> |*|*| |
+-+-+-+    +-+-+-+
  | |↖|      | |↘|
  +-+-+      +-+-+

  +-+        +-+
  | |        | |
+-+-+-+    +-+-+-+
| |*| | -> | |*| |
+-+-+-+    +-+-+-+
  | |↖|      | |↘|
  +-+-+      +-+-+

```
(The same calculations are mirrored about the relevant axes for the other three directions in which the hunter can be traveling.)

## Approaches
1. 

## References
1. [Architecture](https://github.com/mipademiao/hps-evasionArchitecture)
2. [Sample Game](https://cims.nyu.edu/drecco2016/games/Evasion/views/index.html)

