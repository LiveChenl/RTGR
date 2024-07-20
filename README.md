# Multithreaded Socket Communication for Gesture Recognition
This project is based on TCP-connected Socket communication. The detailed introduction is as follows:

1.Client-side Multithreaded Video Stream Capture and Upload:
The client uses multiple threads to capture video streams from the camera.
The video streams are uploaded to the server via a TCP connection.
Simultaneously, the client receives the processed video stream from the server.

2.Server-side Multithreaded Video Stream Reception and Processing:
The server uses multiple threads to receive video streams from the client.
A pre-trained gesture recognition model is used to detect gestures in the video data.
After obtaining the detection results, the server sends them back to the client.

3.Server Sending Detection Results to Client:
The server sends the detection results back to the Windows client via a TCP connection.
The client receives and displays the detection results.

# Usage
1.Deploy Server Code:

Deploy the code from the server files to the server.

2.Deploy Client Code:

Deploy the remaining code to the client.

3.Run Code and Test Communication:

First, run the server code on the server to ensure the server starts successfully.
Then, run the client code on the client device to ensure the client can successfully connect and communicate with the server.
Perform the necessary detection and operations.

4.Interrupt Communication and Shut Down Server and Client:

After the detection is complete, press the ESC key to interrupt the communication.
