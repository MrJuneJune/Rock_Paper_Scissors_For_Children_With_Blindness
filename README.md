# Rock_Paper_Scissors_For_Children_With_Blindness

Program that can identify hand gesture of rock paper, and scissors from video 

Requirement.

- Python 3.6.4
- Opencv 3.4.1
- numpy

Description: 

This script uses opencv2 library to distinguish hand gesture from video by following these steps.

1. capture video and select region of interested area by clicking and dragging.
2. remove background by using createBackgroundSubtractorMOG from opencv2.
3. Outline the hand by masking the hand with background substracted frame.
4. Find countour of the outlined hand and then find convex hull/convex defects.
5. Define hand gesture of rock, paper, scissors using hull and defects.

It defines hand gestures by using the angle between fingers. By using cosine rule, the angle of convex defects can be calculated. If the range of the defects is limited to how wide the finger can spread, then we can use the number of defects to determine gesture of the hand. For example, rock would have zero defects, scissors will have one or two defects and so on.

Examples:


![](/Images/Rock.png)
![](/Images/Scissors.png)
![](/Images/Paper.png)
