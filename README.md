# Clamming-Website

## Microservice

The microservice uses ZeroMQ sockets to communicate data. In microservice.py, set the port number in line 11 as desired. Run the file to begin allowing requests.
    1. To request data, create a ZerOMQ socket in the request process, connect to the microservice, and send the request as JSON. It will require the inclusion of "labels" and "options" that are both populated and that the number of labels match between all. Example in python:
        
        import zmq
        context = zmq.Context()
        
        test = {"labels": {"labelA": .2, "labelB": .4, "labelC": .4},
                        "options": {"optionA": {"labelA": 5, "labelB": 10, "labelC": 8},
                                    "optionB": {"labelA": 10, "labelB": 5, "labelC": 4}}}
        
        port = 5555
        
        socket = context.socket(zmq.REQ)
        socket.connect(f"tcp://localhost:{port}")
        
        print(f"Sending request to port {port}")
        socket.send_json(test)
        
  2. To receive data, have a line to recieve from the circuit. The recieved data will be utf-8 encoded. It will either be JSON of the weighted sum of each option or an explanitory error message. Example in Python:

         message = socket.recv()

  3. ULM Sequence Diagram
     ![ULM](https://github.com/DylanMajewski/Clamming-Website/assets/106936591/31d24685-d24f-432b-ac2c-d46ade836fef)
