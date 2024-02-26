import zmq

context = zmq.Context()

test = {"labels": {"labelA": .2, "labelB": .4, "labelC": .4},
        "options": {"optionA": {"labelA": 5, "labelB": 10, "labelC": 8},
                    "optionB": {"labelA": 10, "labelB": 5, "labelC": 4}}}

port = 5555

#  Socket to talk to server
print("Connecting to hello world server…")
socket = context.socket(zmq.REQ)
socket.connect(f"tcp://localhost:{port}")

#  Do 10 requests, waiting each time for a response
print(f"Sending request to port {port}")
socket.send_json(test)


#  Get the reply.
message = socket.recv()
print(f"Received reply request [ {message} ]")