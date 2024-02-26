<!-- Add a README to your GitHub (or update it if you already have one) that contains your communication contract. (Once you define it, don't change it! Your partner is relying on you.) README must contain...

    Clear instructions for how to programmatically REQUEST data from the microservice you implemented. Include an example call.
    Clear instructions for how to programmatically RECEIVE data from the microservice you implemented.
    UML sequence diagram showing how requesting and receiving data works. Make it detailed enough that your partner (and your grader) will understand -->

<!-- What do you mean by "communication contract"?

"Communication contract" is simply a label for your answers to part 2. The hope is that, once you write the contract, you won't change it.

Can we prove that the basis of the service works by demonstrating local send/receive of data and then work with our partner after to establish and troubleshoot any network connectivity issues?

Yes! You don't have to integrate with teammates' software until next Sprint. However, your communication contract needs to finalized NOW.

For the UML sequence diagram, what are you looking for?

We're looking for a pretty basic UML sequence diagram that covers the calls and functions necessary for doing requests and responses. Below is a very basic example with a text file as a communication pipe. Names of functions aren't included for the requesting program because, in general, you won't know that information. Function names ARE included for the microservice. The yellow boxes are notes. -->

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

    3. 