# Optimal Touring

You want to visit up to n sites over k days. Each site has certain visiting hours. You have fixed a time you want to spend at each site which must all happen in one day. The time to go from site to site in minutes is the sum of street and avenue differences between them. On each day, you can start at any site you like (as if you teleported from the previous place you visited and slept on the street).

No more than 10 days and 200 sites.

You will be told the statistics of the sites and the number of days on the day of the contest.

The format will be
site, x location, y location, desiredtime, value
site, day, beginhour, endhour

Here is a sample input.
```
site avenue street desiredtime value
1 99 54 118 70.8
2 58 115 218 130.8
3 71 159 73 43.8
4 52 142 65 39
5 20 86 55 33
6 81 64 59 35.4
7 56 190 185 111
8 77 183 145 87
9 76 52 165 99
```

You want to achieve the maximum possible value summed over all sites within the time constraints. Visiting a site twice or more times gives no more value than visiting it once.

Note that a pure greedy strategy wouldn't be so good. Such a strategy might have you visit a site and and then visit the next nearest site. That might lead to large number of sites being found the first day (e.g. a central circle), but then later days might not have sites close to one another.

Your output should simply give a sequence of sites in the order of visit per day, one line per day.

## Important
1. What time duration should I start the visit at a site
2. Given a time, which sites could be visited at that time?



## Approaches
1. ```Minimum Spanning Tree (MST) + 2OPT``` - using MST to generate an initial tour. Keep swapping two edges as long as it improves the result.
2. ```Clustering``` - approaches using clustering performed better.
3. ```Simulated annealing + DP``` -  this strategy won the contest.

## References
1. http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.104.9895&rep=rep1&type=pdf#:~:text=The%20traveling%20salesman%20problem%20