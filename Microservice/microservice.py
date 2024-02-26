import zmq
import json

def weighted_sum(test):
    try:
        return {option: sum([test["labels"][label] * test["options"][option][label] for label in test["labels"]]) for option in test["options"]}
    except:
        return "Error: An error occurred while calculating the weighted sum"
    # returns a dictionary of the weighted sum of each option

port = 5555 # the port number

context = zmq.Context() # create a new context
socket = context.socket(zmq.REP) # create a new reply socket
socket.bind(f"tcp://*:{port}") # bind the socket to the port

print(f"Ready to recieve requests on port {port}…")

# example = {"labels": {"labelA": .2, "labelB": .4, "labelC": .4},
#         "options": {"optionA": {"labelA": 5, "labelB": 10, "labelC": 8},
#                     "optionB": {"labelA": 10, "labelB": 5, "labelC": 3}}}

while True:
    message = json.loads(socket.recv().decode("utf-8"))
    print(f"Recieved request: {message}")
    valid = True

    # check if the message is valid
    if "labels" not in message:
        socket.send_string("Error: 'labels' not in message")
        # if the message does not contain a "labels" key, send an error message

    elif "options" not in message:
        socket.send_string("Error: 'options' not in message")
        # if the message does not contain an "options" key, send an error message

    elif not isinstance(message["labels"], dict):
        socket.send_string("Error: 'labels' is not a dictionary")
        # if the "labels" key is not a dictionary, send an error message

    elif not isinstance(message["options"], dict):
        socket.send_string("Error: 'options' is not a dictionary")
        # if the "options" key is not a dictionary, send an error message

    elif len(message["labels"]) == 0:
        socket.send_string("Error: 'labels' is empty")
        # if the "labels" dictionary is empty, send an error message
    
    elif len(message["options"]) == 0:
        socket.send_string("Error: 'options' is empty")
        # if the "options" dictionary is empty, send an error message

    else:
        label_count = len(message["labels"])
        # get the number of labels

        for option in message["options"]:
            if len(message["options"][option]) != label_count:
                socket.send_string(f"Error: 'options' value '{option}' does not contain the same number of labels as 'labels'")
                valid = False
                break
                # if the number of labels in the "options" dictionary is not the same as the number of labels in the "labels" dictionary, send an error message
            elif not all(isinstance(message["options"][option][label], (int, float)) for label in message["options"][option]):
                socket.send_string(f"Error: 'options' value '{option}' contains a non-numeric value")
                valid = False
                break
                # if the value of any label in the "options" dictionary is not an int or a float, send an error message

        if valid:
            socket.send_json(weighted_sum(message))
            # send the weighted sum of the options if the message is valid
