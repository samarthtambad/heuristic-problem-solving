# Hidden Tunnel
There is a grid of size n by n, where n will be given the day of the competition. One player, called T for tunneler, has placed a tunnel from the bottom, beginning anywhere along the horizontal line marked Start in the south, and ending anywhere along the horizontal side End in the north. The tunnel follows the path of the roads somehow but may wind around. It is also a simple path (no dead ends and no loops along the way). Further, at any intersection, there cannot be more than two streets having parts of the tunnel underneath that intersection.

The second player, called D for detector, wants to probe a minimum number of times and yet be able to find the exact route of the tunnel.

Suppose a probe reports whether a tunnel ran under an intersection or not and which street(s) (up to two streets) next to the intersection the tunnel runs under. Thus, it is a directional probe.

The tunnel is at most k blocks (a parameter I will give on the day of the competition) long and begins at Start and ends at End.

The game will be played in p phases (another parameter given at the day of the competition). In each phase, D will place some number of probes at intersections and will recive their reports. By the end of the last phase, D must guess the tunnel.

The score of D is the number of probes D used assuming D found the path. If D does not find the path, then the score is infinity. D's goal is to get as low a score as possible.

Each competition will consist of two games where each team plays the role of T once and D once. Whichever team receives the lowest score as D wins.

```
Constraints
-----------

```

## Approaches
1. 

## References
1. [Architecture]()
2. [Sample Game](https://cims.nyu.edu/drecco2016/games/DigThat/iframe.html)