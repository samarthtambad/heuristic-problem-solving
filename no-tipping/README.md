# No Tipping Game

Given a uniform, flat board (made of a titanium alloy) 60 meters long and weighing 3 kilograms, consider it ranging from -30 meters to 30 meters. So the center of gravity is at 0. We place two supports of equal heights at positions -3 and -1 and a 3 kilogram block at position -4.

The No Tipping game is a two person game that works as follows: the two players each start with k blocks having weights 1 kg through k kg where 2k is less than 50. The first player places one block anywhere on the board, then the second player places one block anywhere on the board, and play alternates with each player placing one block until the second player places his or her last block. (The only allowable positions are on meter markers. No player may place one block above another one, so each position will have at most one block.) If after any ply, the placement of a block causes the board to tip, then the player who did that ply loses. Suppose that the board hasn't tipped by the time the last block is placed. Then the players remove one block at a time in turns. At each ply, each player may remove a block placed by any player or the initial block. If the board tips following a removal, then the player who removed the last block loses.

As the game proceeds, the net torque around each support is calculated and displayed. The blocks, whether on the board or in the possession of the players, are displayed with their weight values. The torque is computed by weight times the distance to each support. Clockwise is negative torque and counterclockwise is positive torque. You want the net torque on the left support to be negative and the net torque on the right support to be positive.

## Approaches
1. 

## References
1. [Architecture](https://github.com/Heuristic-Problem-Solving/NoTippingGameArchitecture)
2. 