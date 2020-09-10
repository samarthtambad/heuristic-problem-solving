# Expanding Nim

## Problem Statement
You and your opponent are presented with some number of stones that I will announce the day of the competition. The winner removes the last stone(s). The first player can take up to three (1, 2, or 3). At any later point in play, call the maximum that any previous player has taken currentmax . Initially currentmax has the value 0. At any later turn, a player may take (i) 1, 2, or 3 if a reset has been imposed by the other player in the immediately preceding turn (ii) up to a maximum of 3 and 1 + currentmax, otherwise.

To see how this changes the strategy from normal nim, suppose there are 8 stones to begin with. In normal Nim, the second player can force a win. Suppose the first player removes 1, 2, or 3 stones. The second player removes 3, 2, or 1 respectively, leaving the first player with four stones. If the first player removes 1, 2, or 3 stones at this point, the second player can remove the rest. However, in expanding nim, if the first player removes one stone and the second player removes three, the first player can win by removing all four that remain.

Here is another example just to show you the mechanics: if the first player removes 3, the second player can remove up to 4, in which case the first player can remove any number of stones up to and including 5.
In our tornament, two teams will play expanding nim with a reset option against each other. I will provide the initial set of stones (under 1,000). Each team will play once as the first player and once as the second player. The team may use the reset option at most four times in each game. The reset option permits a team after making its move to force the maximum number of stones that can be removed in the next turn for the other team (and in the next turn only) to be three again. After that turn play continues using the currentmax until and if some team exercises its reset option.

Hint: dynamic programming is a good idea, but you must keep track of which player's turn it is, how many stones are left, and what the currentmax is, and who has used the reset option and how often.

```
Starting state:
N           = number of stones (max 1000)
CurrentMax  = 0
Resets      = 4

Max Number of stones removable = 
            3 if reset option is used by opponent
            max(3, 1+currentmax) otherwise
```

## Approaches
