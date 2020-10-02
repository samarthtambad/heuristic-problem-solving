# Ambulance Pickup Problem

The ambulance planning real-time problem is to rescue as many people as possible following a disaster. The problem statement identifies the locations of people and the time they have to live. You can also establish mobile hospitals at the beginning of the problem. The problem is to get as many people to the hospitals on time as possible.

In our case, the graph is the Manhattan grid with every street going both ways. It takes a minute to go one block either north-south or east-west. Each hospital has an (x,y) location that you can determine when you see the distribution of victims. The ambulances need not return to the hospital where they begin. Each ambulance can carry up to four people. It takes one minute to load a person and one minute to unload up to four people. Each person will have a rescue time which is the number of minutes from now when the person should be unloaded in the hospital to survive. By the way, this problem is very similar to the vehicle routing problem about which there is an enormous literature and nice code like "jsprit" which was used in 2015 to great effect. If anyone wants to take a break from programming, he/she may volunteer to look up that literature and propose some good heuristics.

So the data will be in the form:
person(xloc, yloc, rescuetime)

Here is a [typical scenario from Dr. Dobb's journal, except that the hospitals had fixed locations](https://cs.nyu.edu/courses/fall20/CSCI-GA.2965-001/ambustory.html),

In our case, there will be 5 hospitals and 300 victims. [Here is some typical data with only 50 victims (and again fixed hospitals)](https://cs.nyu.edu/courses/fall20/CSCI-GA.2965-001/ambudata.html) . You will have the usual 2 minutes of user time.

[Here is data and the best solution we could find (from Tyler Neylon) but not in the format we want](https://cs.nyu.edu/courses/fall20/CSCI-GA.2965-001/ambusol.html).

Here is the [data from 2007 having 300 people and five hospitals (having fixed hospitals)](https://cs.nyu.edu/courses/fall20/CSCI-GA.2965-001/ambuprob07). Here is the winning [strategy used by Arefin Huq but each ambulance could take only two people and had to return to the home hospital](https://cs.nyu.edu/courses/fall20/CSCI-GA.2965-001/arefinambulance). He was able to rescue [118 people](https://cs.nyu.edu/courses/fall20/CSCI-GA.2965-001/arefinsave), 20 more than the next best solution.

Here is the [data from 2015 having 300 people and five hospitals](https://cs.nyu.edu/courses/fall20/CSCI-GA.2965-001/amb.2015). [Here is a validator written by Yusuke Shinyama](https://cs.nyu.edu/courses/fall20/CSCI-GA.2965-001/validator.tar.gz). This tar.gz file includes README, sample_data, sample_result, and sample_wrong_result (which causes a validation error) files.

## Approaches
1. 

## References
1. 