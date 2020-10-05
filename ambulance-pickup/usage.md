# Ambulance Pickup Problem Architecture
### Team Marshmallow (Nellie Spektor and Nehemiah Dureus)
ns104@nyu.edu

### Rules
- It takes a minute to go one block either north-south or east-west. 
- Each hospital has an (x,y) location that you can determine when you see the distribution of victims. 
- The ambulances need not return to the hospital where they begin. They will automatically return to the closest hospital to the last person's pick up spot 
- Each ambulance can carry up to 4 people. 
- It takes 1 minute to load a person and 1 minute to unload up to four people. 
- Each person will have a rescue time which is the number of minutes from the start when the person should be unloaded in the hospital to survive.

[link to problem description](https://cs.nyu.edu/courses/fall20/CSCI-GA.2965-001/ambulance.html)

## How do I interact with the architecture?
Your code should output a result file that follows the format shown below. Please look at the `sample_result` files in this repo for some examples.
```
Hospital: <x>, <y>, <num_ambulances> 
Hospital: <x>, <y>, <num_ambulances> 

Ambulance: <hospital_id>: (<hospital_x>,<hospital_y>) <person_id>: (<person_x>,<person_y>,<person_rescue_time>), <person_id>: (<person_x>,<person_y>,<person_rescue_time>), <person_id>: (<person_x>,<person_y>,<person_rescue_time>)
Ambulance: <hospital_id>: (<hospital_x>,<hospital_y>) <person_id>: (<person_x>,<person_y>,<person_rescue_time>), <person_id>: (<person_x>,<person_y>,<person_rescue_time>), <person_id>: (<person_x>,<person_y>,<person_rescue_time>), <person_id>: (<person_x>,<person_y>,<person_rescue_time>)
Ambulance: <hospital_id>: (<hospital_x>,<hospital_y>) <person_id>: (<person_x>,<person_y>,<person_rescue_time>), <person_id>: (<person_x>,<person_y>,<person_rescue_time>)
```

You can run the validator with python 3:
`python3 validator.py sample_data sample_result`
Running this line should result in a total score of 26 and output showing who was rescued. 
You can also try out running with `sample_wrong_result` to see the various kinds of error messages the validator produces.

## How do I send in the code?
Please send me (ns104@nyu.edu) a zip file by 12pm on Monday with your code and a shell script that compiles and runs your code.
Your solution should expect a command line argument with the name of the data file and should output a result file with your solution.

I should be able to run: 

```python3 run.py your_shell_script.sh input_data``` 

and have your code generate a result file called: `result` which I will then pass into `validator.py` to determine your score: 

```python3 validator.py input_data result``` 
