# Random Lawn Mower Problem

There is one perfectly flexible but unbreakable rope attached to two posts on a large but unkepmt lawn. The posts are a distance 1000 meters apart and the rope is of length 1100 meters. So there is some slack in the rope.

A randomower is a driverless lawnmower that can change directions at any time by an arbitrary angle. Fortunately, it can be clipped to the rope so it won't wander off too far. You are trying to use this random lawnmower to cut at least part of the grass between the posts. We'll call the rope's zero point is at post A and its end point at post B is r. The distance between A and B is d where d < r.

To train your intuition, suppose you wanted to cut the grass to clear a path, i.e. a line segment the width of the lawnmower itself, between the two posts. It's ok if more grass is cut on the sides in addition, but you want to be sure to have a continuous path. The challenge is to do this with the minimum number of attachments.

Warm-up: What is the smallest number of attachments necessary to mow a straight line segment (and, optionally, other grass) from post to post?

Solution: Call the difference r - d, diff. Attach the randomower to the diff meter mark along the rope starting say from post A. Because the rope is diff meters longer than the distance between the posts, the distance along the rope between the attachment point of the randomower and post B is d. Therefore, the randomower can reach post A up to a point diff from point A in the direction of B. Next attach the randomower at the 2*diff meter mark along the rope from post A. So, all together we will need ceiling(d/diff) attachments.

Because of its random movements, the randomower will mow more grass than what is in the line segment. That suggests a game.

Suppose that T1 and T2 play a game in which each wants to use attachments that cuts as much of the lawn as possible. They take turns as follows: T2 makes the first attachment. Then T1 makes two. Then T2 makes two. This goes on until each makes the same number of moves (T2, in the last move, makes one attachment). Each player gets credit for every part of the lawn that is first mowed by randomower due to an attachment by that player.

## Approaches
1. 

## References
1. 