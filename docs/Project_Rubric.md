 
Embedded Systems Design II Final Project      	        	             Dr. Kaputa  Tennis Tracker  	                 
        	        	 
1.  	Introduction
This is the final project for Embedded Systems Design II which is the culmination of the curriculum capstone experience for the Computer Engineering Technology program.  This project consists of two phases which are discussed below in detail.  Due to the complex nature of the challenges, groups shall be formed that consist of between four and six individuals.  You are encouraged to divide up the work between team members, however you are expected to understand and be able to discuss at a detailed level each member of your team’s specific design implementation.  The design sub-systems as well as management tasks are listed below although this may not be an exhaustive list.  It is recommended to have at least two team member work on each section to reduce the risk of a single point failure. 
 
o o o o o
system architecture firmware software graphical user interface algorithm development
o o o o o
systems integration system and subsystem verification program management [cost and schedule] risk register
documentation

 
Each topic will be covering in depth during the course however it is the student’s responsibility to ask poignant questions that will help teams achieve the highest possible score for the competitions.
2.  	Project Description
Since 2003, Hawk-Eye has been used to make calls for the	United States Tennis Association [USTA]. Recently it has been determined that under windy conditions the calls are not very accurate.  This is due to the fact that the wind slightly shifts the cameras resulting in increased error.  The USTA has decided to  fund the development of a new FPGA-based tennis ball tracker that can guarantee accurate results every time.  The USTA has agreed to fund several companies up through a preliminary design review [PDR], and critical design review [CDR], and then will ultimately select a single company to design their system.  The USTA expects to see detailed technical and financial analysis as well as a summary of potential risks pertaining to cost, schedule, and tech.  They have also requested that each company put together a fully working demo that makes use of a virtual camera and 3D world.  The selected company will be one that demonstrates the best overall design and that comes in at the most attractive price point.  In short, each company shall develop a tennis ball tracker system that accurately determines ball position within 3D space.
 
 
3.  	Camera Calibration [10 pts]
 
Each camera system is unique and needs to be calibrated before use.  Make use of the Matlab
‘stereoCameraCalibrator‘ app to help determine all parameters of your stereo camera system.  Once these parameters are determined they can be used to minimize tracking errors of the final production system and ensure highly accurate results.   

 
4.  	System Accuracy Analysis Based on Ball Position [static camera] [15 pts]
The customer needs to know how accurate your system is at finding the exact location of the tennis
ball.  Develop a technique to generate accuracy plots for your system.  Note that your system
accuracy might change over x,y,z positions.  Refer to the paper located here for some ideas about how to determine accuracy. Paper link
 

 
      	Grading Rubric                                                                       	 
Description
Points
Accuracy Technique
6
Total Accuracy
6 
GUI Appearance\Functionality
3

 
5.  	System Accuracy Analysis Based on Camera Position [static camera] [15 pts]
The customer needs to know how accurate your system is at finding the exact location of a tennis ball when the camera is shifting.  Develop a
technique to generate accuracy plots for your system as your camera moves around.  The
customer is interested in knowing the maximum error that can be expected on a windy day 


      	Grading Rubric                                                                       	 
Description
Points
Accuracy Technique
6
Total Accuracy
6 
GUI Appearance\Functionality
3

 
6.  	Coefficient of Restitution [10 pts]


 
 
There has been some controversy over the past couple years about the advantages of various types of tennis courts.  The USTA would like you to determine the coefficient of restitution for your court which effectively determines how bouncy it is.  
 
 

 Grading Rubric 	 
Description
Points
Algorithm Development
4
Accuracy
4 
GUI Appearance\Functionality
2

 
7.  	LED Visualizations [10 pts]
In an attempt to create a better experience for fans the
USTA is thinking about adding large LED structures to many of the tennis stadiums.  When a ball is in bounds they want a green LED to stay on constantly and when
the ball is out of bounds they want a red LED to blink at a rate of 10 Hz with a 50% duty cycle.	


 
      	Grading Rubric                                                                       	 
Description
Points
Blink on Bounce
4
Flash on Out
4 
GUI Appearance\Functionality
2

 
 
8.  	Tennis Tracker [45 pts]
 
You will be given a  Unity tennis court and you will be allowed to place 2 cameras anywhere around the court. 
You can use the Mathworks to Unity link to move the
Unity camera and/or ball via a Matlab interface.  An image of the Unity tennis court is shown to the left.  Feel free to use any custom camera resolution, focal length, etc.  The only constraint is that the parameters that you use must exist in the real world.    
Track Serve 
You will be given a function that receives the time and generates the X,Y,Z of the tennis ball.  You will be required to determine if 5 serves are in or out.
Track Volley
You will be given a function that receives the time and generates the X,Y,Z of the tennis ball.  You will be required to determine if 5 volleys are in or out.
Instant Replay
You are to demonstrate a way to show an instant replay of a shot. 

 
  	 
Grading Rubric
Description
Points
GUI Appearance\Functionality
5
Track Serve
15
Track Volley
15
Instant Replay
10

 
 
 
 
 
 
9.  	Grading
The final project grade will be determined based upon the below chart
 
Points
Camera Calibration
10
System Accuracy Analysis based on Ball Motion
15
System Accuracy Analysis based on Camera Motion
15
Coefficient of Restitution
10
LED Visualization
10
Tennis Tracker
45
Promotional Videos 
Not required but highly recommended
Total
100

 
10.  Tips
-  Frontload your work on this project.  Plan to finish at least 1 week ahead of time.
-  See me to bless off your design before you go too far down the wrong path
-  Use version control
-  Meet at least weekly to keep all group members honest
-  Clearly assign roles to all group members and set concrete delivery dates
11.  Key Dates
PDR
During labs on the week of April 1st
CDR
9:00 am – 11:50 am on April 29th and May 1st

 
 
 
 



