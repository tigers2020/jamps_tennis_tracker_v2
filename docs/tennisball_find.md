Introduction
0:00
hello in this video I will teach you how you can build this tennis analysis project from scratch the project detects
0:07
and tracks the players as well as the tennis balls across the whole video we also detect the Court's key points to
0:14
know the player's position relative to the court measure distances and even determine if the ball is in or out we
0:21
will use the output of those models to know how many times a player has shot the ball and how fast he shot it we will
0:28
also be measuring the player's speed and how many meters the player covered in addition we'll be training two
0:34
convolutional neural networks in this project the first one will be YOLO and object detection models to detect the
0:40
fast moving tennis balls to enhance the detection accuracy of the outof the-box models the other one is a CNN that is
0:48
trained to estimate the Court's key points and we'll be using pyto for that
0:53
so whether you're a beginner or an experienced machine learning engineer this project will totally make your
0:59
resume shine let's start the project I have a project set up with one folder called input videos this folder contains
Object detection with YOLO
1:07
one image and one video the image is a screenshot of a tennis match and the
1:12
video is just a small bit of the same tennis match we are going to use those to develop and test our code our first
1:19
task is to detect the players and the tennis ball with an object detector we are going to use a popular object
1:25
detector model called YOLO so the way that we're going to do that is we're going to use a library
1:31
called Ultra litics so um we can just pip install it first we can pip
1:40
install Ultra litics and then run it it run very fast
1:46
on my machine because I have it already uh but it might take a little bit more time on your
1:52
end and then we're going to create a uh a a file that is going to be called YOLO
2:06
inference this file we're going to be playing around with yolo a little bit we're going to see how it works and what
2:12
the output is and uh yeah see how ultral litics work so to import YOLO we're just
2:20
going to do from ultral litics import
2:27
YOLO and uh to import a YOLO model we just do a model equal
2:35
YOLO and then provide what more what model we want so here we want YOLO V8
2:41
which is the um the latest one that we can use right now so we have YOLO V 8X which is extra
2:50
extra large and to run it on um um on um
2:55
on an image we just do model Dot model.
3:01
predict and give it the image path which is going going to be called
3:07
input videos then slash
3:12
image.png which is going to be this one um yeah we can also save it so we
3:20
can have save equal true and yeah that is all for it so we can clear the output
3:28
here and just run it it's going to take a little bit uh time
3:34
um yeah it's it's going to also download the YOLO V8 model because it's not
3:39
readily available on my machine but in the next run it will find it uh in my local directory so it won't download it
3:46
again it will just download it the first time um so it's just going to take a
3:51
little bit time and then uh run it on the image okay now we're done so you're
3:58
going to find uh a new folder that was created it is called runs and then
4:04
detect and then you have predict um if you open predict you're
4:09
going to find the image with the detections there are multiple detections that you can find here which is multiple
4:16
people or players and then you're going to have something like a tennis racket a
4:21
sports ball which is right behind the tennis racket so you can uh actually see it um you have the clock and um you have
4:31
uh you have also the uh the the name of the class which is a person a sports
4:36
ball whatever and then followed by the confidence score the confidence score is
4:42
a a number between zero and one tells you how confident the model is that this
4:47
is um a person for example so the lower the number is the the less the less
4:54
confident the the model is that this is going to be actually what it is and it's
4:59
not going to be a false prediction but yeah this is the output so far it
5:07
looks decent and U yeah the output like the output for one object consists of
5:15
multiple things but let's focus on the three things that we have right now which is the bounding box the class name
5:23
and then the confidence scoree the bounding box here is consistent of
5:28
mainly going to be four values um and it can be in multiple uh ways to represent
5:35
it so we have for example um we can represent it by the X Center and Y
5:40
Center which is the X position and the Y position um of the um of the object
5:46
followed by the width and the height of the uh of the uh of the
5:52
rectangle and we can also represented by the um the far ends of the rectangle
5:58
like the it's called X minimum y minimum then X maximum y maximum those two
6:04
points uh we're going to stick by the X minimum y minimum then X maximum y maximum format um just to stay
6:12
consistent then we have the uh class name here right here and then we have
6:17
the confidence um yeah we can also see those
6:23
uh outputs in a list format in the output format just by creating um a
6:29
variable that stores the output we just didn't store it before um and we can
6:35
just print it print the result and we can also print the
6:41
bounding boxes because there are bounding boxes inside the results so we can have it we can have a look at it
6:48
also so we can have something like this which is for box
6:55
in um results of of 0 do
7:02
boxes then print box uh this is going to print the boxes
7:08
um then we're going to run it again it's going to take a little bit
7:14
time now it's done uh first you're going to find that the runs have another
7:20
folder now which is called predict two uh predict two has the latest prediction
7:25
that we did and it's going to be this exactly the same thing so we won't have to look at
7:32
it so looking at the result we have first the boxes which is a boxes object
7:38
that we're going to look at later um then we have the key points in The Mask which is not important right
7:44
now those are not the for detection uh those are for pose models and for
7:50
segmentation uh we're not going to use it here so don't worry about them um we
7:56
also have the uh names which is um the
8:01
class names for example the ID zero stands for person the id1 stands for
8:07
bicycle and so on and so forth then we have the uh original image
8:13
and this is in pixel so we don't have to worry about it um and yeah this is all
8:20
the main important stuff here then followed by the boxes themselves the Box
8:26
themselves contains uh first of all the class um here it's zero zero you can
8:32
scroll up and see that zero means person so that's the class name uh but here's
8:38
the class ID so you can map it to the class name easily followed by the confidence
8:44
score and then you have the is track which is going to be tracking um tracking uh across frames in
8:53
a video uh we're going to tackle that um when we predict on a video so I can show you and and then we have the bounding
9:01
box themselves you can see different types of formats here um but the one
9:06
that we're going to use is the X yxy which is X minimum y minimum X maximum y maximum and here's the X position uh of
9:15
the minimum one then the Y position then the maximum X and then the maximum
9:23
Y and yeah you're going to find that we have multiple boxes and and that is it
9:31
this is the uh results that we have so in order for us to uh run it on a video
9:39
we can just replace the uh image path with the video path like this input
9:46
video. MP4 then we're going to run
9:54
it and it's going to take a little bit more time because a video consists of
9:59
multiple images uh and in that case it consists of 214 images so it's going to
10:07
run off those those images one at a time um so it's going to take a while so I'll
10:13
be back when it finishes okay so now we're done and we
10:18
have a predict three folder that we can go check out so you can press detect you can have the uh open the predict 3 and
10:26
then you have the output video so let's open it and you're going to find a very similar
10:32
output to the one that we have before and yeah it is just running it again and
10:39
again over each uh frame in the video but the one thing to note is that if you
10:45
look at the sports ball it's being detected very low like the number of
10:51
times it's being detected in the whole video is just maybe 10 um and this is
10:56
going to be very hard for us to analyze the the the motion of the ball and how it
11:03
goes and its speed and things like that so we're going to need to uh fine-tune a
11:10
detector model to detect the ball a little bit better so that for us to um
11:17
utilize this output a little bit better so we can start by training and
11:23
fine-tuning um aolo model on the balls on the tennis balls that are moving very
11:29
past so that we can detect it a little bit better so the way that we're going to do it is that maybe we're going to uh
Train YOLO on tennis balls
11:36
do another uh folder called training and inside this folder we can create a
11:42
notebook so we can call it um
11:48
tennis ball detector detector um training.
11:57
ipynb and then then you're going to have a notebook set up first before like
12:03
jumping in we're going to need to find a data set so that we can utilize and I
12:08
already found a data set on roof flow and roof flow has a data set of very
12:16
similar images to the ones that we are using in our um in our use case where
12:23
the there is an aial um photo of the tennis court
12:29
and then the tennis ball is moving right here and you also have a bounding box on
12:34
it uh by the way Robo flow also can give you the ability to create your own data
12:40
set and it's done with very easily um but yeah we're not going to annotate it
12:47
for us because it's already there and you have 428 images in the training set
12:55
and 578 total images so this is is not a big data set but it's going to be good
13:03
good enough for us uh for our use case um so if you haven't already you
13:08
can just go create yourself a rof flow account and then um I am going to use
13:14
YOLO V5 because it has the it got me the best results in detecting the balls so
13:21
you can just click on it make sure that you have the show download code and um
13:29
yeah you can press continue and it it gives you the code that you're going to use to download the
13:35
uh data set so you just copy it and can come back here
13:41
and basically um like get data
13:48
set and you can paste it right
13:53
here so here the API key is is going to
13:59
be your key I just replaced it with a string so that not to show you my key
14:04
and you can also like it also installs the robo flow so we can install it right
14:11
here and I'm not going to train on this machine I'm going to train in Google collab so I'm just going to add also
14:18
install ultral litics so you can install both and you
14:25
can download your data set right here um so I want to show you the data set um
14:34
that is being downloaded I'm going to run this uh now it's now it's being grun
14:40
uh and it's downloading the uh the data set for us and yeah we're just going to
14:47
wait a little bit for it to finish so now it's done and you're going to find that a new folder has been created which
14:54
is called tennis ball detections -6 if you open it you're going to have have uh
14:59
three folders which is training testing and validation and inside each one you're
15:04
going to find images and labels and if you open the images you're going to find the images that were shown before
15:13
and if you are going to open the labels you're going to find the class
15:20
name which is uh going to be sorry the class ID which is going to be zero
15:25
followed by the bounding boxes that we have so yeah to start training we're going to
15:31
need to Wrangle the data set a little bit uh it's not going to be much uh but the training code requires us to have
15:38
another folder inside this folder that is called the the same name tenis ball
15:44
detection D6 and inside of it we're going to have training testing and
15:50
validation so in order to do this we're just going to we can just do it manually
15:56
right here uh but I'm I do do want to make the code reproducible so I'm going to do it with code and I'm going to
16:04
import something called shuttle that is going to help us move copy and paste
16:09
things around uh using python so the way that we do it is that
16:15
we're going to write uh shuttle Das move then give it the tennis B
16:23
detection then train and we want to move
16:29
it here we want to move it again into another folder like
16:36
this um so that way the the code for the training code won't crash it it just uh
16:43
expects it to have it uh to have it in this type of format so I'm just uh abiding it uh so we can do the same for
16:51
the test and for the
16:57
validation you can run
17:03
it and it's going to finish anytime
17:12
soon okay so if you if you see the results again so you're going to find the tennis ball detections -6 then
17:19
tennis ball detections -6 and then you're going to find the training and testing and validation uh
17:25
folders uh to train the model it's going to be simple with alter litics so the
17:31
way that we're going to do that is that um we're just going to have um write
17:38
YOLO then uh mention that the task is going to be detect which is going to be
17:44
uh detection because it has multiple other things like key Point extraction and uh segmentation so we're going to
17:52
specify that it's U only detection and we can uh specify the mode
17:59
of it which is going to be training we're not going to be detecting and we're going to specify the model itself
18:06
which is going to be YOLO V5 and I'm going to choose a big one which is going
18:11
to be uh this one. PT and I'm going to also specify the
18:20
data set path which is going to be a
18:25
location uh Slash data yaml and data set. location is from Robo
18:33
flow you're going to find it here um uh so it's a data set and the
18:41
data set has a location attribute so that's how you do it and you can also
18:47
specify the epox to be as much as you want I'm going
18:53
to keep it 100 and you can also specify the image size
18:59
um I'm going to specify to be a 640 and you can run it right here um and
19:07
uh yeah you will have the output uh but I'm going to run it on Google cab
19:13
because it has uh free GPU so um I just
19:18
moved it just move the code right here uh the same thing copy pasted it and uh
19:24
run the same thing it run the model it trained it and then it produced another
19:31
folder called runs you open the runs you have the tect you open the tect you have the train and then you have
19:39
multiple um multiple metrics that you can open up and see but the ones that
19:46
we're going to use is the weights uh you're going to have the best weights and the last weights download them both
19:53
like by pressing this download button I already did um and yeah you just
19:59
download them then copy them and then uh paste uh like paste them right here we
20:06
can create a new folder called models and you're going to paste it
20:15
right here so let me uh let me go paste them and come
20:20
back so I pasted them right here and renamed them to YOLO V5 best and YOLO V5
20:27
last uh we're just going to use one of them uh so for me I think the last was
20:33
doing a little bit better than the best so uh but it might not be the case for you so you can play around with both and
20:39
see which one works best for you um and now we can use this model again for the
20:47
inference and see how it goes so for the inference we can uh we
20:56
can use this model by specifying its path so we can just do models SL
21:05
YOLO s YOLO 5-
21:11
last last. PT and we can also specify the confidence to be uh 0.2 I think it's uh
21:21
something very close to 0.2 right now but yeah we can uh run it again on the
21:28
video and we can see the results again this is going to take a
21:35
little bit time to run on all the video so um I'll cut the video and come back
21:41
when it's done so it's done now and we can go back to our um folder to the output folder
21:50
that we have which is going to be runs detect and then you have a predict for
21:58
and you can now see that the ball is being detected way more than we had in
22:03
the past um but you're going to also notice that only the ball is being detected and
22:11
not the players not anything else that is because we only trained on tennis
22:16
balls because that was the data set so unfortunately right here we're going to
22:23
have two passes one with yolo V8 to detect the players and one with yolo V five the trained one to detect the
22:29
tennis balls and yeah but it's going to be doable it's just going to take a
Object Tracking
22:35
little bit more time if we look at the previous YOLO V8 output video we will find that for each
22:42
frame we get a list of bounding boxes and those bounding boxes are not the same between frames as objects move from
22:49
one frame to another we want to have the ability to match the player's bounding boxes to the bounding boxes in the next
22:56
frame because right now we just have the X and Y positions of each we have nothing that explicitly states that this
23:03
is the same object between frames this bounding box matching is called object tracking where we say that
23:11
this bounding box is the same object as this bounding box in the next frame this
23:17
way we can analyze the movement of the same players across the video ultral litics also gives us the ability to
23:25
track instead of predict so we we can do track right
23:31
here and we can return it back to yov V uh 8 and it was Yol V
23:40
8X run it it's going to take a while so again I'm going to cut the video and
23:47
come back later okay so now we're done uh we can
23:52
open it up again we can open the runs detect and this time you're going to find a track it's not going to be
23:59
predict it's going to be a track so if you open it you're going to find that each player has a different ID so this
24:06
is ID 1 and this is id2 and no matter the frame that we are in we can always
24:12
say that this one is the player one and this one is player two and this one are
24:18
persons with other IDs as well um this is going to be very useful
24:24
for us and very helpful for us to all always say or to always detect which is
24:32
which which person is which person with ease um and yeah we can also track the
24:39
balls but since there's only one ball in the field in uh in in most of the times
24:47
then we don't need to track the ball we can just detect it and yeah we only know
24:52
that there's going to be only one so uh no need for a Tracker right here and
24:58
before we proceed while we're training stuff um in the in the final output
25:04
video I showed you that we also are detecting the key points multiple key
25:10
points in the court uh those red key points that you see right here uh those
25:15
multiple key points are going to be helpful for us to detect how much a user
25:21
has um has covered in kilometers and how much um and meters and how muches the
25:28
ball have traveled and it can also detect whether the ball is in or out and
25:35
yeah it is very useful for us to detect those key points um so the way that
Train key point detection with Pytorch
25:40
we're going to do it is that we're going to also find uh a data
25:46
set and I have found a repo that does exactly the same thing which is uh
25:53
detecting multiple key points uh in the same are view of the tennis court and
26:00
they also provided us with a data set and they also have a model for it but
26:06
we're going to train our own so the uh the data set right here they have it so
26:13
you can click on it and uh you can download it easily from um from the uh
26:21
from the drive or we can just uh W get it um
26:29
so the way that I'm did it is that I used WG to download this so um you can
26:37
just copy this uh download WG function uh WG command and we can write it on our
26:46
own so to train this we're going to have
26:54
another um notebook that is called tennis
26:59
court key
27:05
points training.
27:11
ipynb and we can download our data set
27:18
and this is going to download it in a zip format so we will need to unzip it
27:25
so we can write unzip tennis court de data set.
27:35
zip and then we can start uh with our code so we can do a markdown right here
27:44
and say start code uh for this code we're going to use
27:51
pyour so we're going to import pytorch and we're we're going to also
28:00
import um the data set from pytor so data set torch. utils do data
28:12
import import data set and a data
28:22
loader and we can also import um
28:28
the model itself which is from
28:33
torch Vision import models and we can also
28:40
import Transformers transforms uh which is going to help us
28:45
transform our data set a little bit so you can run this and
28:52
yeah uh first we can specify the device that we're going to use so we have
28:58
device equal um and you can see that it autofilled so you can see Tor device
29:06
we're going to set it to Cuda if Cuda is available which is uh GPU else we're
29:11
going to put CPU and let's run it and afterwards
29:18
let's create our own uh torch data
29:24
set so the T the data set is where most
29:29
of our code is going to be here um and the other things is going to be a little bit easier so we can create a class for
29:38
this data set which is called key points data set we can call it whatever
29:45
you want it's going to it's going to inherit from the data set that we uh
29:50
imported in the torch so it's going to inherit a lot of the functions and uh uh things like that
29:58
and we can also plug it in into our um training uh so the first thing is going
30:05
to make an initialized function that is going to take the um image
30:12
directory as well as the data file so before we proceed I wanted to
30:19
show you what data that we got by downloading uh our data set so let me
30:24
move again to collab and you're going to find that I here also use coolab for the
30:32
training so um you when when you download the data set and you extract it
30:38
as well uh you're going to find that you have images it's going to take uh bit time a
30:47
bit of time to download to open those images because we have a lot a lot more than 500 the time um so you're going to
30:55
find the images are pretty similar to what we have and what we saw before so nothing interesting is here but you're
31:02
going to find also a Json file and this Json file has the ground truth positions
31:11
of the uh keypoints so first you're going to find the
31:17
ID uh give it a minute it's just acting up because it's a lot of data so you're
31:23
going to find an ID and um let an ID
31:28
which is the image ID and then the key points KPS is the key points and you're
31:34
going to find 14 of them those 14 are going to be X and Y positions so
31:41
actually in reality the model is predicting 28 um 28 numbers it's not 14
31:49
numbers so you're going to find the X and Y positions of each one and yeah
31:56
that is it so given that we can jump back to the code and create our own uh continue
32:04
creating our own data set so we can um save the image directory here in the uh
32:14
self we can also open up the uh data file which is open data file and we're
32:23
going to read the data so uh it's predicted this wrong but
32:29
we can import Json because it should it's in Json
32:35
format so we can just import it as a dictionary do load and give it
32:44
f and yeah that is it so in the data set you're going to find the dictionary that
32:50
I just showed you on the Google collab and then we're going to uh write
32:58
um a transformation um a transformation function uh this one is going to
33:05
standardize the image into uh the same size and it's going to
33:10
normalize it as well so you can write it as transforms
33:18
equal uh transforms which is what we imported from torch and we can
33:25
compose then we can give it a list of Transformations that we want so the
33:31
first one is to transform it into um a
33:37
pil image do to P image
33:46
because then we're going to resize it to make it um 2 224 by
33:54
224 and then we we are going to uh make this into a
34:00
tensor and lastly we're going to normalize it so that the values can um
34:07
can be easier to train the values of the pixels can be easier to train the next function we want is to
34:15
define the length of the data set so you can have the uh length of it it's just
34:21
the maybe the length of the data that we have the the length of the dictionary that we read
34:28
um and yeah afterwards we're going to create a function that is going to get
34:36
um an item so in the training we are going
34:41
to uh get items one by one or batch by batch uh and then train it on this batch
34:48
and then um wait for the other one to come so the way that we're going to do this is we're going to do a function
34:55
called get item that's is going to to take an index and is going to return back the
35:03
image and the key points so let's start by um getting the
35:09
annotations of it so we can say items. index and
35:16
then um we want to get the image so we
35:21
can write image uh CV2 we're going to read the image and
35:28
read and then um we are going to specify
35:34
the path so the path is going to be
35:40
self. image directory then
35:46
slash then it's going to be item do ID because if you remember we
35:53
have the the ID is going to be the same name name as the image and it's followed by
36:02
PNG now this will read in the image but we don't have the CV2 imported so we can
36:10
import it using here Port
36:16
CV2 and then we want to get the height and the width of the image so we can do
36:23
that easily by that and we just can call the shape
36:33
function um and CB2 reads the image in a
36:39
BGR format but we want it to be in an RGB format so we can have it like
36:46
this CV2 do CVT color from RGB to
36:55
BGR um afterwards we want to transform the image by the Transformations that we
37:02
defined above so we can have this self dot transforms and given the
37:11
image um then we want to have the key points so the key points are going to be
37:21
item and we saw that it is in the KPS um
37:28
key and yeah uh this one is going to
37:33
be um a list but uh for in order for us
37:38
to to to train it we need to make it into a numpy
37:43
array um so we can import numpy at the beginning then go back here and write
37:53
np. array and and have it like this and also we
38:03
noticed that it was a 2d array so we want it to have it only 1D so the way
38:09
that we do it is we make it um flatten and flatten is just going to convert it
38:16
from 1D to 2D and at the end we just want it to be
38:22
a float um so it's an array of floats so we can
38:30
just specify the type as np. FL
38:37
32 um now now the key points we regarding that the image has the
38:44
original um size and it's not 224 by
38:49
224 so we would need to map the key points to actually show this like to
38:55
actually be m map to the same um to the same um positions after the resize so
39:04
the way that we're going to do that is we're going to do like very simple cross multiplication where I say if the where
39:13
the width where the original width was for example the position
39:18
240 so if I made it uh 224 the width
39:24
what is going to be the um what is going to be the new
39:30
location so the way that I'm going to do it is that I'm going to multiply
39:35
224 by 240 divided by the width and this cross multiplication will give us a the
39:42
end uh or end position so you can do that by
39:49
specifying key points and you can take the second uh
39:56
like um yeah so you can take the first element then the third element then The
40:01
Fifth Element so on and so forth so you can have the width this this is how you
40:07
can do it and the way that you're going to do it is you can multiply it by
40:14
224 [Music] um and then you divide by
40:20
width and this is to adjust the x coordinates
40:28
um of the key points we will need to also adjust the Y coordinates so we can
40:35
start off with one not zero and um and
40:41
divide by the height and not the width and yeah and now we're done so you
40:48
can just return the image and the key points and your uh data set is ready so
40:59
we can afterwards um we can specify the um we
41:05
can initialize this uh data set we can specify the uh training and uh
41:11
validation uh data sets so you can do like this uh
41:17
data set equal key points let's run
41:24
this um so you can have the key points data set you can specify the image
41:30
directory which is images and then you can specify the Json file which is going to be data
41:38
slash um and this data and this Json file of course has the annotations so
41:44
it's um train. Json and if you have any doubts
41:50
about those locations you can just go back here and see it uh you can see that the data has images and we have a
41:57
training Json and a validation J Json and this is the training data set
42:03
so you can also have the validation data set by doing this and specifying here
42:11
the uh Val Json and yeah now you have your own data
42:20
sets just to use them in the um in the training we need to put them into loader
42:27
so you're going to do that by writing it like this and you can specify that data
42:34
loader give it the training data set specify the batch size we can specify it as eight here and we can also Shuffle
42:42
the same thing that we uh that we did for training we can do for validation and yeah and now we're
42:51
ready so now we want to uh now our data set is ready we want to create our model
42:59
so to create our model we just need
43:05
um um so yeah so to create our model um we're
43:11
going to initialize it first so we're going to say that it's going to be
43:18
models and we're going to choose reset
43:24
50 uh and we're going to choose the pre-trained equal true now this is going
43:30
to uh use and download a pre-trained convolutional neural network that was
43:36
trained on other images and um this is this is going to
43:44
uh download the model and have it in the U model uh um
43:51
variable uh but this reset 50 was not trained for keypoint extraction so uh we
43:57
will need to replace the last layer to reflect our own uh needs so this is
44:03
called like fine-tuning where you get the reset 50 which is a a trained model
44:11
and you utilize most of its layers again uh that was trained on another data set
44:18
uh on this problem so the way that we're going to do it is that we're going to specify the
44:26
last layer which is the fully connected layer the last one and we're going to
44:32
say that this layer is going to be a linear layer which is just going to be a flat
44:40
layer with um just the features uh the input
44:48
features the the features that is going to be inputed here and the output is
44:53
going to be 14 * 2 we will have 14 key points and each key Point has an X and Y
45:00
which is going to be uh 28 at the end so this just replaces the last layer of the
45:09
of the neural network um so now our model is done uh
45:16
the next thing is that we want to move the model to the uh correct
45:23
device so whether we have uh this device is in Cuda or CPU we want to move this
45:31
to Cuda or CPU and the last step is actually
45:38
training the model so we
45:43
can so we can start training the model so first thing is that we want to
45:50
define a loss function and since this is going to be a regression uh function
45:57
then we're going to use uh mean squared error loss so we're going to have the
46:03
Criterion set to uh torch Ms eloss uh then we're going to specify
46:11
also the the optimizer and you can specify the
46:16
optimizer to be whatever you want um I I chose Adam and I am going to also um
46:25
choose learning rate of 1 E4 now we can have as much EPO as we
46:33
want so I'm going to choose only 20 and we're going to Loop over each
46:43
Epoch in range
46:49
EPO and I am going to get the image
46:57
and key points um again I'm I'm not running it
47:02
locally because I'm going to run it on the um uh on the Google collab but the
47:09
rest of the tutorial I'm going to be running locally so that uh you can see things step by
47:15
step you can just say enumerate which is going to return the index and we can
47:22
have the train loader
47:28
and yeah the train loader is going to return back the image and the key points
47:34
so we are going to have the it's images it's multiple images so
47:41
you can have it the images to device we can move it to the device we can also
47:46
move the key points to the device that we want we then want to flush out the optimizer so that it has um like to
47:55
flush show the uh gradients um and then we want to predict
48:02
uh the um we want to predict the model uh the
48:08
output uh like we want to use the model to predict the key points on the images that is
48:15
provided and after we predict it we want to um U like uh calculate the loss which
48:24
is going to be like this we give it the outputs and we give it the key points and it's going to use the mean squared
48:31
error loss to calculate our loss and at the end we want to do a
48:37
backward propagation and we want to take a step
48:43
an Optimizer step just to do a learning
48:48
step and yeah and just for logging
48:53
purposes we can log every uh 10 steps
48:58
which is going to be like this which is if I is divisible by 10 then we're going
49:05
to uh print out the epoch we're going to print out the I and we're also going to
49:12
print out the loss so you can go ahead in your uh Google collab or if you want to train it
49:19
locally train it locally um and run it so you can you can see that it ran and
49:26
the loss was very high now it's decreasing a little by little and at the
49:32
end of the day you're going to need to save it so after you run it uh you'll
49:39
need to uh save it in and download it so so to save it we just going to run torch
49:48
Dove then give it the model dot State dict
49:59
and you can uh specify the output path of it so you can have the key
50:05
points model. pth and you run it and save it so I'm
50:13
running it in collab so you can save it and then you can download it like we downloaded the um YOLO model and then
50:21
you can come paste it again um in the models directory and
50:28
paste it uh now we have the other model
50:35
ready so now that we're done and our models ready to be utilized we can close
50:42
down all this we can save it you can download you can close all this
50:50
up and now we can start uh coding our tennis analyzer
Tennis Analyzer
50:56
so we can just specify the main and write it right
51:04
here and we can have the main
51:09
function and we can do a print word right now and then we can call the
51:18
main so after we set up the main. pi uh
51:24
we just want to start with the uh basically reading the video because we
51:31
won't be able to we we don't want to run
51:36
run it like that um we basically want to run it
51:42
um um like frame by frame uh so yeah we're going to need to
51:50
read in the video as frames and then have the ability to also save it as frames
51:56
uh so let's start with that uh we can create a new folder called
52:03
utils and inside the utils uh we're going to need to create a a folder a
52:11
file called video
52:23
TS okay uh inside the video Tils we're going to
52:28
import CV2 because this is the way that we're going to read and save our videos we're
52:35
going to create a function called read video it takes a video path um and then
52:44
it um opens um like it it opens a connection to the video and right now we
52:51
have an empty uh list with frames and we Loop uh and we're going to Loop
53:00
over this uh till the frames are done so what we do is that we use c. read to
53:06
read in the frame and then we have the return this return is going to be false
53:12
when the when the there is no more frames to read so if there is so if it
53:18
is actually false we're going to break this Loop otherwise we're going to
53:23
append the frame to the list of frames and then at the end of the day we're going to release it and return back the
53:32
frames um we are also going to want to have a way to save the video so that we
53:40
can see what we do so we can Define save
53:46
uh video that takes an output
53:52
video frames and it takes in an output video
54:02
path and it's going to save this as um
54:07
um it's going to yeah it's going to save this as a video so yeah I'm going to utilize what uh GitHub co-pilot has
54:15
suggested but I'm going to edit it a little bit so first what the format that we want is going to
54:22
be MJ PG
54:27
and we want to Output it as a 24 frames per second and yeah that is it I'm going I'm
54:35
just going to remove that as print and yeah this is it um in order to
54:42
expose those functions to the outside uh to to outside of this folder um we need
54:49
to create a new file called init.py
54:56
and whips I just need to create replace this with a DOT and in the init.py we
55:04
just like um mention all the functions that we want to have um available
55:13
outside um outside the util so what functions we want to expose outside the
55:18
utils and we write it here so we can write from video utils we can import or
55:25
read video and save video um and after we read and save
55:31
video we can go right here write from
55:37
utils import read video and save video
55:43
we can also put it in Brackets and because we're going to have a lot more functions in the utils so make it neat
55:51
and organize from now and yeah we can uh then uh read in
55:58
the data set read in the the video sorry so we can specify the input video path
56:06
input video path is equal to input videos.
56:11
input video. MP4 then we can readin the video frames
56:18
by using the function that we have from the utils and afterwards
56:25
um we want to save the video so we can have actually we can create a folder
56:32
called output videos that is going to have our output um inside of it so we
56:40
can have the save video uh function that we also have in the um
56:48
yours uh you can uh give it the video frames and you can also create the
56:55
give it the output path so uh yeah let's run this and see if it
57:04
works so there is an issue with the output format so let me go and check it
57:11
real quick so yeah this issue was because I wrote MP4 at the end and it should
57:18
beavi so if we run it again you shouldn't get this error and yeah so you can open it up
57:28
here in the output videos and you're going to see the same video again uh outputed to
57:37
us okay uh that's set up that is all set
57:42
now so we can start defining our uh trackers basically so you can create a
57:49
new folder called trackers inside of it you can create a file called called player tracker.
58:00
py and inside this player tracker we're going to create the uh tracking for the
58:08
players so uh we're going to import YOLO so from ultral litics import
58:17
YOLO and we're going to specify the class which is player uh
58:23
tracker we're going to specify the uh init
58:29
function and it's going to take in the model path which is what model are we going to use
58:37
and yeah and we can just do self. model
58:44
equal YOLO model path and to detect on a frame uh we can
58:53
use the same code that we did earlier so we can have Define
59:00
detect frame and we can just do the same code that we have earlier so we're going
59:06
to take a frame which is basically an image we have the uh results from it and
59:13
then we run the model on it so model.
59:18
track because we want the players to retract here and we give it the frame
59:25
and we also tell it to P like the persist function we're going to give it
59:30
true now persist here it tells the model that the tracks that this is not going
59:37
to be um just one individual frame I'm going to give you another frame
59:43
afterwards and you should be able to persist the tracks within those frames um because we're not giving the
59:49
whole video at one time so we need to uh set this up so that it can remember the
59:54
tracks that were done before um then uh we're just going to uh
1:00:02
need to have this um map of lists um like this map of IDs to names so um it
1:00:12
is in the results so you can have the results do names and it will give you
1:00:18
the results we're going to have the output in a dictionary where the key is
1:00:24
going to be the player ID and the output is going to be the bounding box and
1:00:29
we're going to Loop over each bounding box in the results and we want to only
1:00:35
choose the bounding box that are uh people that have a person inside of it
1:00:40
we want to exclude um clocks we want to exclude rackets we want to exclude
1:00:46
everything except people um and we're going to have another tracker for the
1:00:51
balls so we will exclude that also here
1:00:56
um so yeah we are going to take in the
1:01:02
zero with option because it's only one image and we going to run
1:01:07
results of boxes and we are going to get the track
1:01:14
ID and this is the number that you saw on top of the uh people uh in in the
1:01:21
track example that I gave you before we're going to make it as an integer
1:01:26
then we going to take box uh. id. to
1:01:33
list and this is the Tracker ID and we want to also have the bounding box so we
1:01:40
can also do a result which is one result
1:01:46
um we can say that box and we want it to have it in the xyxy format uh which is X
1:01:53
minimum y minimum X y maximum y maximum and we're going to keep that consistent throughout this
1:01:58
video and the uh we also want to have the object class
1:02:04
name so the class ID so we can say object CLS ID as box do
1:02:14
CLS and. to list um if I can write list
1:02:22
correctly and we can also have the zero one um and we want to map this ID to the
1:02:30
name so that we know what we're looking at so we can have the
1:02:37
object class name as ID to name of object
1:02:43
ID and we can simply say if the object uh name is equal to person then we are
1:02:52
going to uh take it we're going to have the track ID and then put uh the value
1:02:59
like the key as the track ID and the value as the bounding box and if it's
1:03:04
not a person then we're not going to do anything we're not going to take this so
1:03:09
we are going at the end to return this um and have uh and and get the results
1:03:18
of one frame we want to also create a function
1:03:23
that detects multiple frames so we can have detect frames and this is going to
1:03:30
have the self and it's going to take frames it's also going to have um it's
1:03:39
it's going to utilize the detect frame function so what we do is we have the
1:03:45
player detections and for frame in frames
1:03:55
and we want to do this we want to detect
1:04:00
each frame and then put it right here and append it to the output to the
1:04:07
output list and now we are done so you can have
1:04:14
this player tracker uh ready for use and it will return back the list of like the
1:04:22
list of detections for each frame and to also expose it outside this folder we need to have the
1:04:31
init the init one uh init file and you can write
1:04:40
from player tracker import player
1:04:48
tracker you can put a dot right here so um
1:04:55
afterwards we can detect from we can import it so from trackers import player
1:05:05
tracker so we can we can initialize the player tracker first so we can have the
1:05:13
uh player tracker as
1:05:20
player tracker and we give it the YOLO V8 X1 as the model
1:05:32
path and yeah now we initialized it so
1:05:37
let's use it to get the detections so player detections is equal
1:05:44
to player. detect frames and we give it the video frames and that should be it so here we
1:05:53
are reading the video Read video and here we
1:06:00
are detecting
1:06:06
players okay so now we're ready um but the video won't have the uh detections
1:06:14
on top of it so we will need to create a function that uh draws the bounding
1:06:21
boxes on top of the video frames so the way that we're going to do that is that
1:06:27
we're going to add a new function into the players uh tracker that is going to
1:06:33
add those um drawings on top of the frames so you can go back again to the
1:06:39
player tracker then go back here
1:06:48
whoops and uh you can have a function called Define draw Bo boxes BB boxes
1:06:55
bounding boxes so it takes in the video
1:07:04
frames um and it takes in the player
1:07:13
detections um so uh we are also going to have the output frames as an empty
1:07:21
list let's call it output video
1:07:27
frames and I am going to Loop over the frame and the uh output dictionary so we
1:07:35
can have the frame then player dict IN
1:07:42
Zip and give it the video frames and the player
1:07:51
detections zip allows us to Loop over two lists at the same time so that we
1:07:56
don't have to keep an index of them um and then we just want to draw the the
1:08:04
bounding boxes so here we are going to draw the bounding
1:08:10
boxes so we are going to Loop over each track
1:08:17
ID and BB box in the player dect items and let's import CB2
1:08:28
and see how it goes so the first thing we extract the X1 y1 X2 Y2 from the
1:08:35
bounding box and then we draw a
1:08:40
rectangle that has the like the corners of it which is going to be X1 y1 and the
1:08:47
other corner is going to be X2 Y2 um and we are going to specify a
1:08:56
color um and we can make this color uh right here um so this is an an
1:09:04
RGB format uh so uh yeah and yeah the two
1:09:13
here means that it's not going to be filled it's just going to be the outside uh borders of
1:09:20
it um we also want to put in some text thatth tells us this is the player and
1:09:29
what id is it so we can just uh do something like this
1:09:36
CB2 and then uh put
1:09:43
text we give it the frame and then we give it
1:09:49
the string that we want to print out so we have the player
1:09:58
ID and then we want to put in the track
1:10:06
ID uh we also want to have the position of it so the position is going to be int
1:10:13
of the BB box of zero which is going to be the minimum and it's also going to be
1:10:20
the end of the BB box of one which is going to be minimum y so this is minimum X and this
1:10:27
is minimum Y and we want to also have a little bit of a buffer so let's do it like uh minus
1:10:35
10 and yeah uh we can also specify
1:10:41
the um the font of it and the the font size and the color of it as well so we
1:10:50
can have this and let's increase the size a little bit so to
1:10:55
0.9 and this is and this should be it so
1:11:01
um and yeah you can also assign it right here like this one you can assign it
1:11:07
frame equals frame but it actually writes on top of the frame so we don't
1:11:13
have to do it so we can do this like we can do it like this and afterwards we
1:11:22
just out put this again as a frame like append it to the output and then at the
1:11:28
end of the function we return the output frames um so yeah let's
1:11:36
also uh return back to the main um use the player tracker right
1:11:42
here so we are going to uh be drawing some things so uh draw
1:11:51
output and the first thing that we are are going to draw is
1:11:56
draw player bounding
1:12:02
boxes and we are going to draw uh the bounding boxes give it the
1:12:09
video frames and give it the player detections uh the video frames right
1:12:15
here we are going to uh yeah we can call it here the
1:12:22
output uh video
1:12:27
frames and then save it again so yeah let's run it h there is an error uh
1:12:36
trackers do no modules called it's called like that so trackers do player
1:12:44
tracker
1:12:52
um
1:12:58
ah whoops I misspelled it right here so it's tracker um you can clear the output and
1:13:07
run it
1:13:14
again so it is going to take a while to run this all um so yeah I am going next
1:13:23
to create um a stub where we can save the output of this tracker uh into a
1:13:30
file and then read it instead of predicting it again and again and it would help us in development it will
1:13:37
help speed up the development a little bit but uh yeah this is going to be the next step so uh yeah I'm going to cut
1:13:45
the video for now and come back when the run is
1:13:52
over so I've come into an error right here
1:13:59
and it seems to be that I have missed the bracket so if you did the same
1:14:04
mistake uh just come here at the add the bracket for the int and make
1:14:11
sure that your brackets are correct and
1:14:17
yeah I think I'm missing one so yeah right here
1:14:25
and so everything is good now um so yeah you can uh run it
1:14:32
again and yeah I'll come back when it's uh when it's done
1:14:43
running okay so now it's done so let's go back to our output videos and open
1:14:50
this and you're going to find the output very similar to what we had uh in our uh
1:14:59
in our ultral litics output which is going to be the player and then the ID I
1:15:04
didn't put the confidence because I don't care about it right now I just care about the IDS and the bounding
1:15:12
boxes so it all looks good now I just want to add another thing in the player
1:15:19
trackers which is going to be uh basic basically uh saving the output so that
1:15:27
we don't have when each time when we run we don't have to run the detector again we can just uh take it take the output
1:15:35
if there is any so we can create um a folder called tracker
1:15:42
stops tracker stops like this uh
1:15:52
whips and we are going to be saving the output
1:15:59
of this uh detect frames um in a pickle format so let's import
1:16:09
pickle and right here in the detect frames uh
1:16:15
function uh we can take two more inputs which is going to
1:16:22
be read from stop it's going to be either
1:16:28
true or false um if it's false then we're going to run it if it's true then
1:16:34
we're going to uh put uh put it into a stop then we are going to take a stop
1:16:42
path and uh this stop path is going to be none as
1:16:50
default um so yeah if then if we have
1:16:57
the um if we have the stop
1:17:03
path then if we have the if we have the
1:17:09
stop path which is going to be if stop path uh is not
1:17:18
none uh then we are going to save it basically so we are going to open it and
1:17:27
then uh pickle dump the player detection uh inside this path um we are also going to check if
1:17:37
the read from stop is actually true and if it is um we are going to read the
1:17:44
Stop and not uh basically detect each frame so we are going to check if read
1:17:52
from stop is true um and the stop path is not
1:18:00
equal to none um then we are going to open it then load the pickle and then
1:18:09
return the player detections and yeah this is it right now
1:18:15
we want to add those two in so in the
1:18:20
detect frames we are going to give it two more things uh we are going to read
1:18:29
from stub is equal to false right now we're going to make it false because we
1:18:34
don't have a St and we're going to generate it after this and the other one is going to be stop
1:18:43
path and we are going
1:18:48
to tracker specify the output one so specify the output path which is going
1:18:55
to be tracker stops slash then player
1:19:03
detections do pkl which is the pickle format pickle extension so right now
1:19:11
we're going to run it again and it is going to detect the frames but afterwards it's going to save it in the
1:19:18
stops so that we don't have to run it again uh so let's run it and we're going
1:19:24
to have to wait a while so I'm going to cut the video again but hopefully this is the uh last time that we're going to
1:19:32
detect it um with the players we're going to do another one with the balls
1:19:37
but we're also going to run it one time and then the Run should be a little bit faster afterwards so yeah see you
1:19:49
then okay so now it's done and you you can find them in the tracker stobs you
1:19:54
can find the player detection. pickle so all what so all we do right now is just
1:20:00
change this to true and if we run it again then you are going to find that it
1:20:07
takes way less time so um give it just a couple of seconds and it's done so you
1:20:14
can go also to the output folder and every time it it overwrites the file and
1:20:20
you can see that we have the same out it uh now we want to do the same thing
1:20:28
uh the same like we want to track the ball so you can copy it then uh copy the
1:20:34
player tracker and uh then you can paste it right
1:20:39
in after pasting it you can uh rename it to a ball
1:20:46
tracker like that and after you name the ball tracker
1:20:53
you can uh rename also the uh the class
1:21:01
name and we're going to change the detect frame a little bit so the detect
1:21:06
frame right here uh basically um is checking for the if
1:21:14
class name is equal to person and since that we have only one class then we can
1:21:20
delete this if function so we we can delete this uh if statement and we can also delete this uh
1:21:28
checking for the names and we can also delete this because it's not used
1:21:35
anymore and yeah we can rename the player dict to Bal
1:21:42
dict and let's also have it right here and H it here and let's not track it
1:21:49
since we only have one ball so we can just predict it we can set the confidence to uh 0 uh uh
1:21:57
like 15 uh I think that is um that was good enough uh and 0.2 is also working
1:22:05
fine um so uh we're going to we're not going to have any tracks so we're going to
1:22:11
have only one ball but we want to have the output consistent so we're going to have um just one which is track one and
1:22:20
put at it the result and yeah we also want to have um this
1:22:29
detect frames to uh to stay the same but we don't want to have it to call to be
1:22:36
called player detections we can call it ball detections and rename each instance of
1:22:46
this and now we're done so the last thing that we are going to need to
1:22:52
change is the draw boxes um so the draw boxes right here is
1:23:00
going to be ball ID and we can also call it here ball
1:23:07
dict I don't think that we're going to change anything else than the naming um but yeah that is
1:23:17
it uh yeah if I didn't miss anything I think this is
1:23:23
it for yeah this is it for this class so we can go here we can also import it in
1:23:29
the player tracker we can import ball tracker we can go back here and we can
1:23:36
import ball tracker as well let's um um so yeah let's detect
1:23:46
now the uh balls so we can call detect players and ball
1:23:53
we can also have a ball tracker which is going to be ball
1:23:59
tracker and we are going to give it this time the model path to be
1:24:06
models and YOLO 5 Dash um slash
1:24:15
last do pt and we are going to detect also the
1:24:24
frames so like we did in the players we're going to do with the uh ball as
1:24:29
well so we're going to call it ball detections we are going to read from the
1:24:34
stop if it exists if it doesn't then we read it um then we have the uh we can
1:24:43
call it the ball detections and save it as well and yeah afterwards in the drawing
1:24:53
the outputs we can also draw the uh ball
1:24:58
output like this and give it the uh ball detections and yeah that should be it uh
1:25:07
we can now run it we'll have to wait a little bit for the ball tracker to run the first time um but yeah I'll come
1:25:16
back when it's finished yeah before we I run into an
1:25:21
error that tells me that this doesn't exist so you can change it to read stop
1:25:27
from false till we have the first initial uh stop so I'm running into
1:25:33
another error again so let me uh figure it out and come back to you
1:25:41
afterwards uh so I'm back and I have this prectical true this is uh for only
1:25:47
tracking so make sure to remove it and uh save it again
1:25:53
and run it and hopefully this time it won't crash again um just give it a minute make sure
1:25:59
that it's running and then I'm going to cut the video if it is yeah it is running so I'm going to come back when
1:26:07
it's finished um so yeah see you then so now it's finished and we can go
1:26:16
back again to the output video now see it and you can see that the ball is
1:26:21
being uh tracked as well uh so let's give the ball another color than red so
1:26:27
that we can differentiate it quite easily and we can uh do this by going to
1:26:34
the ball trackers then go to draw boxes and give it here in the RGB section you
1:26:42
can just give it another color and I am going to choose a yellowish color like
1:26:50
this and this time I'm not going to uh I'm going to use the uh stubs so that I
1:26:56
don't have to run it again so like this and you can just run it again and
1:27:06
yeah this time it should be a very fast run so I'm not going to cut the video um
1:27:12
yeah it's done already so you can now see the results the ball is in uh yellow you can also
1:27:20
change the writing to yellow uh so like here you can also
1:27:26
change it to be yellow and yeah that is it let's now detect the uh
1:27:35
Court key points um so in order to do that let's also create another folder
1:27:41
that is going to be called Court line
1:27:51
detector and we are going to have um a file inside of it that is called
1:27:58
Court line detector. py so this is going to read in
1:28:04
the model that we have trained and then use it for prediction so in order to do that we are
1:28:11
going to import uh torch because the model is written in
1:28:18
torch and we are also going to import torch uh
1:28:23
vision and uh we are going to specifically import from it the
1:28:29
transforms uh to apply the same Transformations that we did earlier on this uh uh on the images uh we are going
1:28:38
to also import CV2 to read in the images if we want and to do any uh thing uh any
1:28:45
uh uh any manipulations if we want and yeah let's start uh writing the uh
1:28:54
class so we can have the uh whs we can
1:28:59
write the cour line detector and we can start off with the
1:29:07
init function and we are going to take the
1:29:12
model path as an input also
1:29:19
um so let me just fix that and you can have the self model
1:29:27
equal models do uh we're going to do the same one so we're going to have the uh
1:29:34
models. reset and I did not import it so I need to import it first um and we are
1:29:43
also going to replace the last fully connected layer with uh the one that um
1:29:49
that is going to have the uh 28 uh key points
1:29:56
um so FC is equal to um
1:30:05
torch do NN do linear and then it's going to be
1:30:11
self. model. fully connected uh in features and then have
1:30:18
the 14 * 2 we can just write 28 if we want but I
1:30:25
just write this to remind myself that it's 14 key points and with uh with X
1:30:30
and Y um then to load in the model I'm just going to do the self. model. load
1:30:38
State dict uh we are going to load in
1:30:44
the model and I am going to map it to uh look uh the CPU because because right
1:30:52
now I have a CPU machine and I don't have a GPU inside of it so I'm just going to map it to a
1:30:59
CPU so now we have created the model and we have loaded the uh weights of the
1:31:06
model inside this model so that we can have the same uh output that we uh like
1:31:13
we can get the predictions of the train model that we have um the last thing
1:31:18
that we are going to do in the init is going to specify the transform function which is going to be the same thing that
1:31:26
we did so you can actually go copy and paste it so you can have it right
1:31:35
here if you have it ready you can just copy paste it if you want uh like this
1:31:43
and it should be uh fine um then we are going to create the predict function
1:31:53
it's going to take in the image which is a frame um we are going to basically
1:32:00
predict the first image and not predict it again because the camera is not
1:32:06
moving so the key points won't change positions so we are just going to uh run
1:32:11
it on the first frame and that's it um so what we do is that we have the
1:32:20
image uh we just make sure that it's in RGB so we can just convert it from BGR
1:32:29
to RGB and then we um apply the
1:32:35
Transformations on the uh on the image so we just do the
1:32:41
self. transform and then give it the image RGB and we want it to have uh like we
1:32:51
want to UNS squeeze uh UNS squeeze it and yeah we we then want to run the
1:32:58
model on it and the way that we do that is that we do it like
1:33:04
this outputs equals self do model and then
1:33:09
give it the image T um and you have the key points right now
1:33:16
in the outputs so you can have the outputs
1:33:22
dot squeeze uh then uh two list by the way
1:33:30
UNS squeezed right here just means that if you have the image like
1:33:37
this um you just put another list on top of it so it's it's going to be like this
1:33:45
uh this is uh on squeeze uh this is essential because um when a model tries
1:33:51
to predict things it it usually takes in a list of things to predict on and if
1:33:56
you are just predicting on one thing like this one image uh you need to put it into a list and the output is also
1:34:04
going to be a list so uh we also want to have the zero um like you want to have
1:34:11
the zero position of it you can just write dot do zero or you just can
1:34:17
squeeze it and by squeezing it it just removes the list
1:34:22
so back to the key points thing where we squeezed it um we can uh move it to
1:34:31
CPU and then we can make it into a
1:34:36
numpy like this and um we can also have the um like
1:34:46
like the key points right now are um are the positions for the 224 by
1:34:54
224 so we need to map it again to the um to the original image size and image
1:35:01
width so the way that we're going to do that is that we're going to have the
1:35:06
original height and original
1:35:13
width and we can leave it like this or we can just take the first two
1:35:20
and uh do it like that um so the way that we did it when
1:35:27
training is that we did it with cross multiplication and this is how we are
1:35:32
going to do it again right here so we are going to get the key
1:35:38
points then get all the width of the key point so every uh every other element uh
1:35:45
starting from zero um then we are going to multiply it by original. height over
1:35:55
2440 this is going to map it to the original width and the original
1:36:01
height um we are also going to do the same thing but for the
1:36:08
heights this was for the width and this one was for the heights uh this one starts from zero and this one is going
1:36:14
to start from one every second element starting from one and yeah this should be it we can
1:36:22
have the we can just return the key points and there you go that is how you
1:36:29
um uh that is how you uh get the results uh from the model before returning back
1:36:37
to the main we also want to draw those draw those predictions on top of frames
1:36:43
so let's do that while we're here so we can just have the
1:36:49
Define and uh called uh draw key
1:36:55
points and we can take an image and the key points that we have just
1:37:00
returned um we can uh loop over each uh
1:37:05
one each um uh each key point that we have and we
1:37:13
want to Loop over 2 by two and this is
1:37:19
because it is going to be XY then XY then XY and one XY is one position so we
1:37:27
are going to Loop over it from zero and to the length of key points but the next
1:37:34
step is going to jump two so instead of I being one it's going to
1:37:40
be two so we're going to skip one in the middle so we're going to make x equal
1:37:47
int we just make sure that it's an INT because like when you specify a pixel
1:37:53
position um it must be an INT and it won't be fractions it won't accept any
1:37:59
fractions and then it's going to be the I position and the Y is going to be the
1:38:05
I +1 position um afterwards we just want to
1:38:11
display two things we just want to put the dot in the place and then we want to
1:38:17
have the um key Point number on top of it so you can have the
1:38:23
CV2 dop put text and you can write it on top of the
1:38:31
image then you can write um the um like
1:38:37
you can write the Str Str and then I / by two and this is integr division so
1:38:44
it's going to be an integer at the end um and X um
1:38:52
where minus 10 so this is going to take the X position of it and the Y position
1:38:59
and we're going to make a buffer at 10 so we can put it on top of the um uh on
1:39:06
top of the point so we are also going to specify
1:39:13
the font and the U uh font uh the font
1:39:19
sides as well so let's do that here so font we also going to uh choose the
1:39:27
simplex one we are going to choose uh
1:39:33
font size then we are also going
1:39:40
to choose the color this is in a BGR format so this is or which is red um and
1:39:49
then we are going to specify this and at the end we want to
1:39:57
put a circle on the image in the XY
1:40:03
position and its uh radius is going to be 5 pixels and um we are also going to make
1:40:11
it red and then uh we are going to specify
1:40:19
that it's going to be filled so1 means that it's going to be filled and at the
1:40:25
end of the day we are going to return this image now we are done with drawing on
1:40:32
one image but uh we also want to have a convenient function where we can take a
1:40:38
list of images which is all the video frames and run all uh the um and draw in
1:40:45
all of them and return back the results so we can have the draw key points again
1:40:53
but on video and this takes in the video
1:41:00
frames then the key points and it has the output video
1:41:08
frames and yeah it Loops over the video frames and the key points uh actually
1:41:16
uh yeah actually it did it uh like the auto to complete um the theong so you
1:41:23
can remove this because there is only one set of key points and we're going to
1:41:30
draw it again and again so the key points right here and we are uh going to
1:41:37
put it right here in the key points so again always check what um
1:41:46
what GitHub copet is uh is suggesting because it might might suggest things that are wrong and you need to fix it so
1:41:55
uh draw key points right here is I think is working fine the draw key points it
1:42:02
takes key points and then the frame I'm just checking it again uh so yeah it
1:42:07
looks like it's working fine so
1:42:15
yeah uh so before moving forward we just want to create an init
1:42:22
file and we want to expose the C line detector again outside of
1:42:31
this folder so we can um use it in the main function in the
1:42:38
main. pi so we can write from Court line detector import Cod line
1:42:46
detector we also want to have uh we want want to like we want to do the same that
1:42:52
we did with the trackers we want to initialize it then uh detect on the
1:42:58
frame so we can do that by writing
1:43:03
here um cour line detection detector model we
1:43:12
can qu model path we can specify its path first which is models Das line
1:43:21
model. PT not sure that it's the correct name so I'm going to yeah it's not so
1:43:29
just copy the name and paste it right here then um write the initialize the
1:43:38
call TR detector like this and at the end of the day get the
1:43:45
court key points
1:43:51
and we are going to run it like this dot
1:43:59
predict and give it the first video frame so give it only one video
1:44:07
frame and it should return back the key points um and after that is done we can
1:44:15
also draw it so to draw it um
1:44:22
to draw it we can just write it right
1:44:35
here so you can have it uh right here output video
1:44:41
frames and you are going to do Cod line
1:44:49
detector dot draw
1:44:54
key points on
1:45:00
video and then H give it the output uh the output frames right here
1:45:06
give it the output frames and then give it the quot key points so we have the quot key points
1:45:14
right here just give it right here and you should have the output ready I
1:45:21
think this might not yeah I misspelled it um I misspelled
1:45:29
it at the beginning so I'm going to um fix it uh I also noticed that here I'm
1:45:36
detecting both on video frames I should be detecting on output video
1:45:42
frames and yeah that should be it uh I'm making sure that here we're reading from
1:45:49
stubs uh and this prediction shouldn't take long since we are predicting on only one frame so yeah let's try it
1:46:09
out okay so now it's done so we can go back to the output video right here and
1:46:15
we can see that the key points are being extracted correctly uh there is a little
1:46:21
bit of error if you notice like for three it's a little bit shifted to the right um things like that but it is
1:46:27
close enough for our use case uh so we'll proceed from here um yeah so let's return back to the
1:46:37
code and let's um close down all those
1:46:42
unnecessary tabs let's return back to the output and
1:46:49
focus more on the ball detections so you can see that the ball is being detected
1:46:56
way better than what we had originally but for example you can see right here
1:47:01
the ball is not being detected at all and it's being detected like the one
1:47:07
frame before and the one frame after so like this and this like you can see like
1:47:15
um we can easily um we can easily estimate the position given the the the
1:47:22
position before it was lost and the position after it was lost like this
1:47:27
one we can estimate it to be for example the middle position um and if there were
1:47:34
more than one position you can divide it by two divide the the the position by
1:47:41
two and to estimate it uh luckily we can just uh use the interpolate uh function
1:47:49
in the pandas uh library and it would uh fill out
1:47:55
those uh those bolts uh for us so let's
1:48:00
uh let's create that now so we can go back again to the uh tracker which is
1:48:06
the ball ball tracker and uh we can write an
1:48:13
interpolation function so let's uh let's
1:48:18
start here so um we can just write here
1:48:28
Define interpolate ball
1:48:34
positions and it's going to take in the uh ball positions or ball uh
1:48:42
yeah we have it called ball detections in the main so but we don't care about
1:48:47
that right now um so what we do is that we only have one track so we don't
1:48:54
actually need to have the track number I just need the list of uh positions that
1:48:59
we uh that uh the bounding boxes that we get so I can just have the ball
1:49:06
positions equal and then dot
1:49:11
get one and if there is none and if there's uh no one uh that means that
1:49:19
there was no detections I'm going I'm just going to return back an empty
1:49:24
list and I'm just going to do a on line for Loop that is going to Loop over the
1:49:30
ball position so now we just have a list of bounding boxes that is going to be empty
1:49:39
when there is no detections the list inside is not is going to be empty when there's no
1:49:44
detections uh we can convert this list into a data frame so that we can do the
1:49:50
interpolation quite easily so we can import
1:49:56
pandas as PD then we can just do
1:50:03
pd. uh data frame and then give it the ball positions which is this
1:50:11
list and also give it the colums uh which is going to be the column names
1:50:17
it's going to be um X 1
1:50:23
then y1 then X2 Y2 and I'm going to put it in a DF ball
1:50:32
uh positions uh data frame this is what
1:50:37
it's called and then uh this just converts it convert the list into a
1:50:47
panda data frame um then we just interpolate the missing
1:50:55
values and the way that we do that is that we
1:51:00
use the interpolate function inside of pandas so we can just do this and run
1:51:10
interpolate and this interpolates um if something is
1:51:16
missing uh between two frames or between mult multiple uh frames but um it's it's
1:51:23
not going to interpolate positions at the beginning so at the beginning we
1:51:29
want to make sure that there is no missing values uh not to crash our code
1:51:35
so we can just duplicate the the the the
1:51:41
the earliest uh detection we can duplicate it to the start of the frames so the way that we do it is just we
1:51:47
backfill it so uh we do the bill function to do it um again this is just
1:51:54
to handle the edge cases of um of not handling of not getting any detections
1:52:00
the first frame but otherwise it should be fine um and then at the end we just want
1:52:08
to convert this back into the same um format that we got the ball detections
1:52:16
from so um we have B positions equal and then we can start
1:52:24
it again we had one as in the track id1 um and then uh we can put X which is
1:52:33
going to be from the for Loop the on line for Loop that we going to have and
1:52:39
DF dot uh DF uh ball
1:52:45
positions dot 2 nump I'm going to make it a
1:52:52
uh an npire array and then I'm going to make it into a
1:52:57
list and this is going to return back a list of dictionary where one is going to
1:53:04
be the track ID and X is going to be the bounding box it is the same format that
1:53:09
was uh handed to this function so I'm just going to return it back uh to the
1:53:16
ball positions and the the reason reason that we Chang it to Panda data frame
1:53:22
then back is that we just wanted to use those interpolate function in the pandas
1:53:28
data frame so that we don't have to do it by hand um yeah so now we can just here we
1:53:37
can just do it like this and we can call the interpolate function so we can have
1:53:46
the whips ball uh detections
1:53:51
we can call the ball detections and whoops it's it's called
1:53:58
the ball tracker so ball tracker dot
1:54:03
interpolate ball positions and give it the bulb detections and yeah we can run it again
1:54:10
right now and uh see how it
1:54:18
goes
1:54:25
okay so let's open this again and you're going to find the ball is being detected
1:54:32
way more so um so you like the last example I showed you here the ball was
1:54:39
not being detected but now it is uh being detected although you can find
1:54:45
here that the bounding box is not completely on top of the ball but it is close enough so it is uh close
1:54:54
enough and if I run the whole video you're going to find that the ball is being detected in almost every
1:55:02
frame uh this is going to help us way more in the analysis and makes it more smoother so uh yeah um so we're going to
1:55:12
keep that and after we like before we
1:55:17
continue I want wanted to I wanted to add the frame numbers on
1:55:26
top of the frame so that we can store it and um Trace back uh how it how it
1:55:33
functions so we can just write draw frame
1:55:40
number on top uh on the top left corner
1:55:47
so we just want to have the frame number on the top left corner of the video um and we can do it like this
1:55:56
um I am going to explain the code that was written by um the uh GitHub cellet
1:56:05
which is going to be uh looping over each one looping over each frame then
1:56:10
putting um the frame and then the number of the frame and uh then it's specifying
1:56:17
an exact position of it which is um X position of 10 and a y position of
1:56:23
30 and uh it's going to specify also the U uh the font uh type and the um font
1:56:33
size and the color um so yeah we can also make the
1:56:40
color uh like this uh but yeah we should have the
1:56:45
frame number on the top uh on the top left corner of the uh video right now so
1:56:52
let's run it
1:57:02
again okay now it's done so let's open it and you have the frames on the uh top
1:57:10
left corner like you see here I'm just going to minimize this a little bit so
1:57:15
you can see the frame number um and it's in renting we can now like utilize it we
1:57:23
we'll be able to utilize it um further on when we're uh tracing back anything
1:57:29
that is buggy that is happening um but yeah it's going to be super useful
1:57:38
here so let's see the output again and when you see the output we
1:57:44
have a lot of people being detected and we just want to detect the two players
1:57:50
in the field uh we can do that by selecting the players closest to the
1:57:56
court and we can use the key points to to determine which players or people are
1:58:03
closest to the court so let's do that right now so we can uh return back to the U
1:58:13
main.py and we can see that like we have
1:58:18
the quot key points and we have the player detections right here so we can uh
1:58:26
basically add a function that can uh determine which IDs or person IDs that
1:58:32
are closest to the court key points so we can uh so we can go to the
1:58:39
player tracker and add a function that is called chosen filter uh players so
1:58:45
we're going to choose the players and uh filter them based on on their uh
1:58:50
proximity with the court so let's go back again to The Trackers and the
1:58:59
players and let's create a function called Define
1:59:05
choose and filter
1:59:10
players this takes in the um the chord key points
1:59:21
and then it takes in the player the player
1:59:26
detections and yeah um we are just going to choose
1:59:33
the players based on the first frame and not all the videoos so we can do that by
1:59:39
just getting the player detections for the first
1:59:46
frame and we can just make it like this we take the zero with elements of the
1:59:52
player detections and we can also
1:59:58
um do another functions called like
2:00:03
chosen um chosen players equals self do
2:00:11
choose choose players that takes in court key points and the player
2:00:18
detections for the Press frame now let's create this function so we can
2:00:24
have the Define choose players self then C uh key points and then the player
2:00:30
detection frames um we can start by calculating
2:00:36
the distances so the distances between each um uh each uh player and the
2:00:43
court and we can do it by uh looping
2:00:48
over over each track so track ID and we have the bounding box um in
2:01:00
player let's call that player
2:01:05
dict so because it's a dictionary so we can have the
2:01:12
items um and you have the track ID and the bounding
2:01:18
box um and then we basically want to get the middle of the box so we can do that
2:01:24
by um like um getting the X minimum y minimum and dividing it by two to get
2:01:31
the middle of to get the middle position and do the same for y and rather than
2:01:37
doing it here we can also add it in the utils because um uh we are going to use
2:01:44
that also elsewhere so in the utils you can go go ahead and create another uh
2:01:50
file called BB box which is bounding box utils.py
2:01:58
and uh basically I want to get the center of the box so we can have the
2:02:04
Define um get um get
2:02:12
Center of BB box and then I'm going to give it the
2:02:19
box and I'm going to extract the XY positions add them both divide them by
2:02:26
two and add them both divide them by two and return at the end the center X and
2:02:32
the center y the only thing that was missed here is that they need to be int
2:02:39
so that they can be integ uh like pixel positions so we can have it like this
2:02:47
and it should be good to go um we also while we while we're here we also want
2:02:53
to measure distance between any two given points so that uh we can measure
2:02:58
the distance between the um uh between the point and the like the
2:03:05
key uh the bounding boxes and the key points uh so the way that we do that is
2:03:11
we're going to create another function that is called measure distance it's
2:03:18
going to take point .1 and 2 um and 01 is XY and point 2 is going
2:03:24
to be XY as well and we are going to return um this equation so this equation
2:03:33
basically measures the distance between any two points and it does that by uh
2:03:39
treating them as a right angle rectangle and getting the hypotenuse of it so just
2:03:45
to visualize it you see here that um like um you're measuring the distance
2:03:50
between a and c and the way that we do that is that we get the a squ which is
2:03:57
the difference in X's uh sorry the difference in y plus the difference in
2:04:03
um in x^ 2 and then you get the square root of it and this is going to be the
2:04:10
distance between a and C uh the same thing that we are doing right here and
2:04:16
multiply z z like the power 0.5 is just the root um and now we just want to export
2:04:25
those functions and in it so you can have from
2:04:30
dot BB box utils import get Center and measure
2:04:39
distance and in the players we can also have like we can also import the this
2:04:46
from the utils and we can import system as first and then system. pad. append um
2:04:57
like one folder before that just because we want to go one folder back so that we
2:05:03
can see the utils and then we say from utils
2:05:09
import uh we want measure distance and get Center of bounding box now we are
2:05:16
ready to use it so we can say get Center of bounding box and give it the bounding
2:05:24
box and now we have the uh center of the bounding
2:05:29
box and now we can assign it to the uh another variable called player Center
2:05:35
and now we have it now we just want to calculate the distance between the court
2:05:40
and the player and we're going to calculate the distance between the player and each key point in the court
2:05:48
and see which one is the closest so we're going to have uh
2:05:55
basically minimum distance um is equal to
2:06:09
float and then
2:06:15
Infinity then we are going to Loop over each key
2:06:22
point and uh qu key points and we're going to Loop over two at a time because
2:06:28
each one is going to be a one point um then we are going to get the uh Court
2:06:36
key Point um which is going to be the X and
2:06:41
Y positions then we are going to measure the distance between the player Center
2:06:46
and the chord key point and then put it into distance and if the
2:06:52
distance is less than the minimum distance we take the minimum distance and put it here um and yeah that is uh
2:07:03
going to be it so at the end we have the
2:07:10
distances do append and then uh we append two things
2:07:16
we append the track ID don't know if that was written correctly
2:07:23
track ID and then we app also the minimum distance so this way we have a tup we
2:07:30
have a list of tups with a track ID and a minimum distance
2:07:36
um so now we just want to choose the the track IDs that have the lowest distances
2:07:43
between the key points so we can just uh sort them
2:07:50
so we can sort the distances in ascending
2:07:58
order okay and we can do that by this so
2:08:04
distances do sort and then we sort by what value zero which is this one track
2:08:10
ID and one which is this one so we sort the distances based on the minimum
2:08:15
distance and then we choose the first two basically we get uh actually let's
2:08:24
call it choose the first two tracks and you can have the uh like the
2:08:35
chosen uh chosen players is equal to distance of zero and Zer which is going
2:08:41
to be track ID and then we are going to get the next one which is one and zero which is going to be also track ID so
2:08:48
this is going to be two players and we can just return back at the end of
2:08:53
chosen players and now let's also filter out
2:08:59
the chosen players so now we are going to Loop over
2:09:05
the frames and we are only we are only going to give the detections related to
2:09:10
those two chosen players so I can have like
2:09:17
filtered player detections and I'm going to keep it as
2:09:23
an empty uh list then I'm going to Loop over um the player
2:09:29
detections and I am going to uh choose
2:09:35
uh to Loop over each uh track ID in the player dict and I am only going to take
2:09:43
the ones that are in the chosen players so this is a oneline for Loop that can
2:09:48
be a little bit complicated but all it's doing is that it is looping over the
2:09:54
player uh dick uh item by item and if the track ID is in the chosen players
2:10:00
like this it is going to put the track ID and the bounding box and return back the dictionary afterwards after we have
2:10:08
the dictionary we append it to the player D detections and then we just
2:10:14
return back the uh output so now we have the output ready
2:10:20
and we can go back to the main uh right here and we can uh now filter out the
2:10:29
required uh players so we can have uh choose
2:10:35
players and we can write player detections equal player
2:10:42
trackers do shoes and filter players we can give it the court key points and can
2:10:48
give it the player detections and now we have the last player detections we should now have only two players and not
2:10:55
all the other people so let's run it and also see the
2:11:08
output okay so we can open it again and
2:11:13
like you see like other people are not being drone because we filtered the bounding boxes out out and only two
2:11:19
players are being detected and this will also simplify our lives a little bit uh
2:11:26
uh U simplifier life better
2:11:32
here so in the uh so in the the final output video that I've showed you I've
2:11:40
also showed you uh something like a mini cord that is being drawn um here so uh
2:11:48
you can see that uh this is uh this is is um the court that is being done here
2:11:57
and here's the position of the player one here's the position of player two and here's the position of the ball
2:12:03
itself and this is what we call Mini cour I call it mini cour right here um
2:12:11
we are going to be drawing on it and also we are going to make it um
2:12:18
uh very similar to the original uh like um proportions of the um um of of the
2:12:27
court so that we can measure distances and we can measure uh like the distance
2:12:33
between the player in the ball and how much uh did the ball cover and how much did the player cover quite um uh
2:12:41
accurately and yeah so we are going it's it's good for visualization but it's
2:12:47
also going to help us a little bit when we are trying to determine um the
2:12:53
distance between uh any two things uh so we can start
2:12:59
by uh like uh drawing this and then we
2:13:05
can move on from there so you can uh write uh tennis
2:13:14
court uh dimensions
2:13:19
and you have here the tennis core Dimensions that you uh see so this is
2:13:27
called like the the the high one is called the double alley which you can see it's a 10 uh meter you also have the
2:13:36
uh Center Line the service line the center line and uh you also have this part is
2:13:44
called No Man's Land um so yeah we're going to be
2:13:51
putting uh like some of those dimensions in constants and it's going to help us
2:13:58
um understand what is the actual distance that is being uh covered by
2:14:04
players in the ball so let's create a folder called
2:14:11
constants constants and let's create inside it um
2:14:20
an init
2:14:26
file and we can start by just writing down a couple of things so we can write
2:14:34
the single line width uh which is going to
2:14:41
be 8.23 this is what is called the single line width I I just have the uh 8.23
2:14:50
which is this one and this is the double line width double ali um so it's
2:14:59
10.97 so we can also write it here double line width which is going to be
2:15:12
10.97 um there is a half quart line width
2:15:25
um actually it's height um and it's going to be
2:15:31
11.88 and let me tell you which one that I'm referring to which is this one this
2:15:36
is the half court uh height this is the U uh like the meter in
2:15:46
meters uh you also have the service line
2:15:53
width and it is 6.4 you also have the double Aly
2:16:01
difference and it is 1.37 and again uh this is the double Al
2:16:08
difference right there so between the um
2:16:13
like the single allei and the double Ali it's 1.37 uh um those are just a couple of
2:16:19
contents so uh so like constants that are going to help us uh map between uh
2:16:28
pixel difference and meter difference so yeah you can just uh take them from here
2:16:36
5.48 and while we're here we also want to uh like determine the heights of the
2:16:44
players themselves and you can actually actually uh like if you opened it you
2:16:51
can see that uh you can see the names of those players and you can Google their
2:16:57
heights quite easily and I have Googled them and I've know known them so I'm
2:17:02
going to just write them here uh so player one
2:17:08
height in uh meters and it's going to be 1.88 and the player uh two height in
2:17:16
meters um it's going to be
2:17:25
1.91 those are also going to help us a little bit in uh mapping out uh uh like
2:17:32
pixels to met okay so now we're done with the
2:17:37
constants and now we want to draw the mini qu so we can make another uh folder
2:17:44
called Mini
2:17:51
and uh we can uh write the mini
2:17:56
uh class mini cord
2:18:07
dopy and yeah we can import
2:18:15
CV2 and we can also import sis and we
2:18:22
can uh from um we can sis. pad. append and we
2:18:29
can also return back one folder then from
2:18:39
utils actually let's not do that right now but we can import
2:18:46
constants we can import the
2:18:57
constants okay sounds good um we can def Define the class
2:19:04
start the class which is the mini
2:19:11
Court uh then we can Define the init function
2:19:21
and we can give it frame this Frame is just going to be the initial frame of the video uh just to get the the size uh
2:19:28
of it so um we can start by defining how uh like
2:19:37
um we can start by defining how wide and how tall this this should be like the
2:19:44
drawing style should it be uh large should it be uh small uh I'm going to
2:19:50
set it like the ones that you see it right here uh but yeah feel free to play
2:19:55
around with it a little bit so I'm going to set the self do
2:20:04
drawing rectangle width uh which is going to be 250 it's
2:20:11
going to be uh 250 pixels so uh this white rectangle is
2:20:17
going to be 250 in width and it's going to be 450 in height and the difference
2:20:25
between like the this padding difference um uh this uh this padding uh
2:20:32
difference is going to be uh 20 uh I'm going to make it 20 pixels uh around so
2:20:40
it's um there's going to be a little bit of padding between the qut itself and
2:20:46
the white rectangle and there is also a little bit of a
2:20:51
buffer between it and the top and the right this is 50 pixels so I'm just
2:20:57
going to Define it right here so let's define the drawing
2:21:04
rectangle uh height now again this is the uh White rectangle
2:21:13
that you saw and it's going to be 450 um let's also Define the buffer between
2:21:22
uh which is going to be this empty one uh this part and this part uh the buffer
2:21:28
between the edges is going to be 50 and the padding itself uh which is inside of
2:21:35
the white uh rectangle um so padding of the quart is
2:21:40
going to be uh 20 pixels um
2:21:48
so yeah so now that this is done uh we will just want to determine uh where
2:21:56
should we put the um uh this rectangle like now we should uh find out the the
2:22:03
exact X and Y coordinates we should put this rectangle on so let's create this
2:22:09
function here so we can have uh Define
2:22:14
set canvas background box
2:22:22
position and it's it takes self and it takes a frame which is going to be the first
2:22:28
frame then we do a frame. frame. copy uh
2:22:33
just to not override the original frame um we don't need to actually here but
2:22:40
let's keep it um we can uh Define the end of the frame which
2:22:48
is this bit the this end bit to be uh
2:22:54
the frame do shape 1 which is going to be the width of it minus self dot
2:23:04
drawing like self dot sorry buffer which is going to be 50 so this
2:23:11
is going to start uh 50 but from the end this is the end and we can also do
2:23:19
it self Dot and Y and it's going to be self. buffer
2:23:29
which is going to be 50 from the top and then 450 which is going to be this one
2:23:36
so self the buffer then self do drawing rectangle height we also want to get the
2:23:43
start and the end so the start is going to be end xus width minus the width and
2:23:50
the uh start is going to be also the end y minus the
2:23:56
height and now we have the positions in the uh self so don't we don't need to
2:24:03
return it but we do need to call it so we can call set canvas background
2:24:10
position and we can give it the frame awesome um now we just want to uh
2:24:19
see the position of the court itself this this mini Court we we made the
2:24:25
position of the rectangle the white rectangle now we want the position of the cord so let's also do a function for
2:24:33
that so Define set mini
2:24:38
Court position and uh it takes in self and
2:24:44
actually we don't need anything else so what we do is that we're going to
2:24:51
just add the paddings in the start and end and um like the the start X and YX
2:24:59
so we can have the self. qut start x equal self do start X Plus
2:25:10
self do padding C okay then we can do the same for the Y
2:25:18
um and we can do the same for the index but instead of adding it we subtract it
2:25:23
so that it can have uh a buffer right
2:25:29
here and um we can also
2:25:37
have and we can also have the endex like the end y uh so the n y minus padding
2:25:45
qu um now the what we also want to do is
2:25:51
that we want to define the width of the qut so the cour width um and let's call
2:25:58
it Court drawing because it's just the drawing uh it's going to be Court end x
2:26:06
minus uh the uh start X now we also need to call
2:26:13
it like that in the init
2:26:19
okay uh now we just want to uh specify those uh Court key points um the ones
2:26:27
that you see here in Red so those Court key points are going
2:26:32
to be a little bit manual so bear with me a little bit so we are going to write
2:26:41
Define uh set put
2:26:51
drawing key points okay I have misspelled it
2:27:01
right here it takes in um nothing it just
2:27:07
takes in the self and we can start by defining the
2:27:13
key points so we can have the key points all at
2:27:19
drawing key points we can have it all as zero and we
2:27:27
can have it 28 times so this is going to create a list of zeros and it's going to
2:27:34
have 28 zeros um so let's define
2:27:39
01 or 0 Z to be specific um so 0 Z is it's going to be
2:27:48
just this this point right here which is going to be the start of the court so
2:27:54
start X and start y so to do that we're just going to
2:28:01
create drawing key
2:28:08
points of zero and drawing key points of of one and it is going to be this start
2:28:17
X and start Y and let's also put ins on top of it so that we can make sure that
2:28:25
those can fit into pixel positions next we just want to do
2:28:31
01 and yeah end point1 is going to be this one which is going to be this one
2:28:37
this is the end of X but still the the start of Y so you can have the drawing
2:28:45
key points of two two two and three like 0o and one is for position zero 1 2 and
2:28:51
three is for position um 1 which is going to be the end of X and the start
2:28:58
of Y this is correct so let's move forward and let's also do it in the
2:29:06
point two point 2 is going to be this point
2:29:12
which is right here um and this is two2 quarts
2:29:17
uh like with each other this is a half qu and this is a half qut and we want to be able to make it as
2:29:26
like as proportional as possible to the actual uh meters that we have in the
2:29:31
constants so we're going to be adding some conversion logic right
2:29:37
here so this conversion logic is just going to be cross multiplication uh but since we're going
2:29:43
to use it over and over uh let me put it in the the
2:29:49
utils so in the utils you can have um a new file called
2:29:59
conversions conversions. py and you can open it right here um and
2:30:08
Define uh two functions which is convert pixels to distance and convert meters uh
2:30:15
to uh pixel so we're going to have
2:30:20
convert pixel to a
2:30:26
distance to MERS so convert a pixel distance to
2:30:32
meters so for example if the user moves from here to here how many meters did he move
2:30:40
we have the amount of pixels he moved it he moved from uh like X and Y position
2:30:46
position and then he went to X and Y position but we don't have the exact meters that he moved and we can do that
2:30:54
uh by doing some cross multiplications and seeing okay so from this point to
2:31:00
this point it is x m so from this point or from this pixel to this pixel it is
2:31:07
it should be y meters we can do it with simple cross
2:31:13
multiplication um so the way that we're going to do it is but we're going to take the pixel
2:31:19
distance and then we are going to take the
2:31:25
reference height in
2:31:31
meters then
2:31:39
reference height in
2:31:45
pixels then we going to return it back here so let me explain it first so now
2:31:52
we have the width of this um in pixels and we also have the width uh of this in
2:31:59
the constants if you open it and yeah the double Ali line the this one it's in
2:32:07
meters so you have this in pixels and meters so you can do any cross
2:32:13
multiplications to find anything so for examp example the height in pixels like
2:32:19
the width in pixels is let's say 20 and it's in meters it's
2:32:27
10.97 and uh now I want I want to give an arbitrary pixel distance and to
2:32:33
change it to meters I'm going to take this multiply it by meters then divide
2:32:39
it by 20 uh this is simple cross
2:32:44
multiplication and this is um and we can we can actually uh do it in in just one
2:32:51
line uh like this so pixel distance times meters over the pixels and Heights
2:32:58
we also want to have the Define
2:33:04
convert meters to pixel
2:33:15
distance so we have also the reference height in meters and the reference height in pixels and we're also going to
2:33:21
do some cross multiplication uh but but this time we're going to multiply by the pixel distance over the height
2:33:29
distance and yeah so let's now expose it right here so from dot conversions
2:33:38
import convert distance pixels and convert uh pixel distance and let's go
2:33:44
back here um think this is should be constants
2:33:51
constants why is it adding it SRE don't mind um then uh yeah we can
2:33:59
add from utils um we should import
2:34:05
convert this one and we should also
2:34:11
convert uh pixels pixel distance to meter distance
2:34:17
so yeah so let's continue down with the points um we have the uh drawing
2:34:29
Point drawing key
2:34:34
point of four and it is going to be uh the same x
2:34:41
value as the as the start so the X didn't change so we can just
2:34:46
um write it as int self. Court um start
2:34:55
x uh but the Y value changed so we can have this
2:35:01
as um so position two is going to be um
2:35:06
so the start y plus uh two half quarts
2:35:11
so the way that we're going to do that is we're going to uh take this start and
2:35:18
then y then add it to convert pixels sorry we want to convert
2:35:27
meters to pixels and then we have the Constance
2:35:32
dot um we want to get the half quart uh
2:35:38
height I just want to remember its name yeah so half quart line height um
2:35:46
so this one and since it's going to be the full qut like from here to to the
2:35:53
nut is the half qut so we want to do uh uh like two times this so we're going to
2:35:59
multiply by two and let's not forget to add the constants do half
2:36:05
cour and we want to give it the two references that we have right now so the
2:36:13
reference in that that we are going to use is that we already have the cord
2:36:19
width so we can uh simply write it right here and uh this cord twist is going to
2:36:26
be constants do double um like uh let's also go remember
2:36:34
the name it is the double uh double line
2:36:41
width so we're going to give it the double line width and then we are going
2:36:46
to give it the court uh chord drawing
2:37:07
WID okay so now we have the point two ready um and we are going to basically
2:37:14
converting a lot lot um of this um like
2:37:19
meters to pixels a lot so I'm going to make it a separate helper function right
2:37:25
here um it's going to be convert
2:37:32
meters um to pixels it's going to take the
2:37:42
meters and we are going to utilize this so you have this and you run it like
2:37:54
that and instead of meters instead of having it a constant we can take it here
2:38:00
and now we get the uh the distance in pixels when we have the meters so we can
2:38:07
just do like this self and we can close
2:38:12
down the bracket here and remove this um now it's a little bit easier for us
2:38:19
uh moving forward to 3 um so point3 is going to be uh again this point which is
2:38:28
going to be 2 plus the width of it um so let's uh let's do
2:38:36
it uh it's going to be um drawing six so
2:38:42
we're going to use the same x value as the first one like that and then we
2:38:49
can um actually I forgot a t right here let's add it let's add it right here we
2:38:56
can add the uh core drawing width uh since we already have it and we
2:39:05
can keep the same um y value as the previous one so that
2:39:15
we uh so we can keep the same y value as
2:39:22
this one so uh we had two and we're going to keep the Y value to have it for
2:39:29
three um again we're going to Loop over it again for
2:39:36
point4 and uh 4.4 we have other uh another uh another
2:39:44
uh 14 point that we want to do so what I'm going to do to not bore you I'm
2:39:50
going to fill it out and then uh come back
2:39:56
later so I've filled in the uh the all all the points right here uh the other
2:40:02
the points and at the end I just assign the drawing key points into a a self
2:40:09
variable so that we can have it uh here so right now we're just going to do the
2:40:16
self and um going to call it again and
2:40:21
right now we just want to define the lines so right here you have um apart
2:40:29
from the points you have the lines so you need to understand which lines you want to connect with like which two
2:40:36
points you want to con to connect a line with and for this we're going to also
2:40:42
manually select those and let's start with it um so we can Define set cour
2:40:52
lines and then give it the self and self.
2:41:00
lines equal and if you look at this you have a
2:41:06
line between zero and two and zero and one so we can put them uh right here so
2:41:16
0 and two and you can also have uh Z and
2:41:21
one uh you also have a couple more uh but I don't want to go like I don't want
2:41:29
to go through them all to not bore you you can just uh it's pretty
2:41:34
straightforward uh so I'm just going to copy paste it and I pasted it and and I pasted the
2:41:41
lines right here so again from 0 to two there's a line line from four to five
2:41:46
there's a line and you can find that those are uh what we see so you can set
2:41:53
CT lines also right like this and that is it and we are set with the uh like I
2:42:02
think there is no more manual work right here so I think we are ready to maybe
2:42:08
draw it um so let's draw it so we have
2:42:14
the draw background rectangle which is the white
2:42:20
rectangle that you saw so we can take in the frame and we can just uh first
2:42:29
initialize the um um like uh we want to
2:42:35
draw a white rectangle so we're going to do shapes like
2:42:41
NP Zer let me import n p
2:43:15
okay so now we have um the same like the the frame that we had um but we like the
2:43:24
image that we have but with all zeros and this is going to help us um do this
2:43:30
a little bit of transparency you can see that it's not an actual like filled
2:43:35
color it has a little bit of transparency in it and this is the way that you do it um you do a dummy image
2:43:42
uh which is going to be all zeros and then we going to add it to the image that is going to be the frame but with a
2:43:49
little bit of opacity difference um so on top of this we can draw the
2:43:56
rectangle uh which is going to be uh CV2 rectangle and then we draw on top of the
2:44:03
shapes one and then we give it the start X start Y and then the end X and Y and
2:44:11
we also want to make it uh uh like uh white so this is the white
2:44:18
BGR and negative one is filled and if the numbers are confusing you you can
2:44:24
just write CV2 do fi and it's going to be the same thing if you hover over it uh you're
2:44:31
going to see that it's an INT which is going to be negative 1 um so we're going to have an output
2:44:40
frame which is going to be the frame. copy and we have going to set an alpha
2:44:47
which is going to be 0.5 so it's going to be 50% transparent um then we are
2:44:54
going to set a mask which is going to be shapes as type
2:45:02
bull so anything that is zero uh so it doesn't have a rectangle uh so it's
2:45:09
going to have only the like the mask is only going to be two for the rectangle
2:45:17
bits and we are going to get the output then the mask only the pixels that we
2:45:24
want to have and we want to add it with weighted so that we can um add it a
2:45:32
little bit with a transparency Factor we want to add the frame and then the alpha
2:45:39
which is 0.5 we want to add the shapes which has the rectangle we just want to
2:45:45
have the um the other transparency of the shapes and yeah zero is
2:45:53
fulfilled and uh yeah so and then we get
2:45:58
the mask um then we write output equal
2:46:06
CV2 and then we just want to convert it so CVT
2:46:14
color uh BGR to RGB you just want to convert
2:46:20
it to an RGB format and then we return back the output of course this one draws
2:46:27
on one frame only so let's draw it on all frames like
2:46:32
Define draw mini
2:46:38
cord then self and give it the frames we then
2:46:45
uh have the output frames which is going to be
2:46:51
for frame in frames and we just want to have frame
2:47:00
equal self. draw rectangle and give it the
2:47:08
frame and at the end we just want to append it so output frames do
2:47:15
pen frame and return it
2:47:23
back and this is it um we should now have the white box and afterwards we
2:47:32
should be able to draw the key points uh so let's uh see the results
2:47:39
till now and then we can continue so in the mini in the mini cord
2:47:46
we just want to add an init py and this is also going to help
2:47:55
us a little bit with exposing the function or the class
2:48:00
outside of this
2:48:12
folder and we are going to go here from mini Court import mini
2:48:22
cour we also want to have um like here we want to initialize
2:48:31
the mini court so now we initialize the mini
2:48:37
court and and now we want to draw the mini qu
2:48:43
um on top of the the frames uh so let me do
2:48:50
that so draw mini
2:48:55
qut and I will have it the output frames
2:49:02
equal mini cord through mini cord output frames and yeah that should be it let's
2:49:12
run it and hope that it works
2:49:21
okay so we have an error um convert meters to pixels is not
2:49:28
defined um I think I've misf felt something so let me check yeah I've misspelled convert
2:49:35
meters to pixels I didn't I forgot to put the two so uh let me uh rerun it
2:49:41
again and now I have another error which is uh I Mis also wrote the uint 8 so I'm
2:49:49
going to fix it and uh come back to you I think is going to be
2:49:55
here um and it's going to be you int
2:50:01
8 so let me run
2:50:13
again so now it's working fine we can open
2:50:19
this up again right here you can see that the image is a little bit weird
2:50:25
because it's in BGR not in RGB uh but you see also the uh rectangle that is
2:50:32
transparent uh right here um but now we need to fix the uh BGR one so I see here
2:50:42
that we also convert it to BGR to
2:50:49
RGB and yeah maybe we don't need to do that
2:50:55
give me a
2:51:12
minute yeah we didn't need to convert it again from BGR to RGB because it was RGB
2:51:17
from the first place and now we have the um like the mini mini qut background
2:51:28
setup okay so so now that we have the background rectangle ready we can just
2:51:33
uh start drawing the court so to do that we can just write a new function right
2:51:40
here uh Define draw Court
2:51:46
uh which is going to take a self and a frame and we are going to Loop over each
2:51:54
point so in range and uh starts from zero till the
2:52:01
self do uh drawing key points and we Loop two at a time
2:52:09
and uh X is going to be int um the self.
2:52:17
drawing key points of I and Y is going to be the same but +
2:52:26
one because it's going to be the next valuable uh variable and then we just add a
2:52:35
circle on the frame
2:52:41
with X and Y we are also going to set the radius to five we are also going to
2:52:49
set the color and we are going
2:52:57
to um make it filled which is1 now we should have the
2:53:07
um now we should have the uh key points ready so let me return the frame
2:53:15
and uh see the results but before seeing the results we need to call it so I'm
2:53:21
going to call it right here self Dot and give it the frame and yeah that should be it so
2:53:30
let's call
2:53:38
it um there is something
2:53:43
missing H yeah so I I wrote uh here uh like the
2:53:51
two here in the length it should be outside the length so let's run
2:54:08
again okay uh let's uh see the output right now so you can see the output of
2:54:16
this is um um having the key points
2:54:21
right here right here right here and it looks fine but the width or the the
2:54:30
height of the um the height of the white box is
2:54:36
not big enough um I think we can expand
2:54:42
it a little bit it should be fine but yeah
2:54:48
um we can also make it in red like that we can make it in
2:54:55
red um but we can also expand the drawing rectangle height a little bit to
2:55:01
be for example uh
2:55:09
500 so that it yeah
2:55:18
it's running right now so let's see the output now the output looks fine we have
2:55:24
the court we have everything that is ready we just want to connect the lines
2:55:29
and this is going to be uh uh
2:55:37
simpler so in the draw cord function uh we just want to uh now draw the lines so
2:55:44
let's call draw lines and so for line
2:55:52
in self.
2:55:58
lines uh what we want to do yeah sorry four line in lines
2:56:06
um so start
2:56:13
point and it's going to be
2:56:19
um this one it's going to be the uh drawing key points of line zero
2:56:28
and this is also going to be uh the Y of it and uh we're going to have an end
2:56:35
point also and it's going to take from a one so uh line
2:56:41
one uh so each line is going to have like like we saw like two points zero
2:56:46
and one and we want to just connect them both and we're going to connect them
2:56:52
both with the CV2 line and we're going to give it the start position the end
2:56:57
point and we are going to give it also a color let's say it's black and yeah that
2:57:06
should be it let's uh run it and see the
2:57:11
results so I made a small mistake earlier where I didn't multiply the position by two and this is because the
2:57:20
the zeroth position is starts from 0 to 1 the first position uh starts from 2
2:57:26
and three and the second position starts from four and five so you can see that
2:57:32
you take the position multiply it by two to get the X1 and then add one to get the Y so you need to do this the same
2:57:40
here and if you uh run it here and and you're going to get the uh correct
2:57:47
output uh wait for a while and you should be done any anytime
2:57:55
soon okay uh now it's done if you look at it now you have the lines ready we
2:58:02
just don't have the uh net line uh this is going to be an easy one it's just
2:58:07
going to be the middle point of the cord so we can just calculate it real quick
2:58:13
and and yeah to uh to draw the net we
2:58:19
just get draw net so we need to get net start uh
2:58:29
point and it's going to be self.
2:58:36
drawing key points of zero because it's like the
2:58:43
zero with position and um it's also going to be int which is like the start
2:58:53
key point is going to be the zeroth position which is X which is going to be
2:58:59
um like this x this X and it's going to be this x at
2:59:04
the same time but it's going to be in between this one and this one so let me
2:59:11
uh calculate it like get the positions of them both and then divided by two so
2:59:17
we can have um self actually let's um let's use their
2:59:25
equation but edit this to five so now we can have the start
2:59:32
position so let's do the same for the end position let's copy paste it uh and
2:59:38
it right here put the end position and make it start from position two instead
2:59:43
of zero and keep the Y the same and lastly we just add the line and let's
2:59:51
make it this color and make it start from net start and end at net end and
2:59:59
yeah we can now run it and see the
3:00:12
results okay now it's finished and you can see
3:00:19
the chord is being drawn quite correctly and yeah that looks
3:00:25
good um so let's continue with that before
3:00:34
closing down this class uh we basically need to add a couple more functions
3:00:41
and yeah so we set a couple of variables um so let's uh let's make functions to
3:00:47
get them so let's get for example the start point of the Min
3:01:01
um self and then we're going to return back the self
3:01:08
uh self do Court start
3:01:14
X self. court and
3:01:22
um uh start whoops uh
3:01:28
Court start Y and we can also get the width of the
3:01:36
mini qu so we can Define get uh width
3:01:44
of mini cord and we can return back the drawing width um we can also return back
3:01:51
the key points if we want so let's get cour key
3:01:59
points actually let's call it cour drawing key
3:02:07
points and let's uh return the uh drawing key points and yeah I think this
3:02:15
should be it so now we're done with drawing the mini cord and I think uh we
3:02:22
are ready to go back here and uh
3:02:28
continue um so right now we have
3:02:33
the um this output and everything looks good but
3:02:41
let's now detect the the ball hits so at this Frame exactly let's minimize this a
3:02:49
little bit at uh around frame between 10 to 12
3:02:56
the ball was hit and we want to like get this ball hit frame and know which
3:03:04
player hit the ball and the same here um
3:03:09
so we can continue to detect the ball frames
3:03:15
so now we just want to detect the uh bow um we we just want to detect the ball
3:03:22
shots so we can create a temporary uh
3:03:27
folder um that is called um
3:03:34
basically maybe called analysis and let's make it a folder
3:03:41
sorry about that let's delete it
3:03:46
then let's create a folder called analysis and inside of it let's create
3:03:53
um ball analysis.
3:04:00
ipynb um now let's
3:04:05
import pickle because we're going to read the pickle uh St that we have for
3:04:11
the tracker right there and we are going to also
3:04:17
import uh pandas we are going to import M plot
3:04:23
lib pip plot and yeah I think that should be it um so the first thing is
3:04:32
that we want to uh read uh the pickle
3:04:39
file um so we are going to read it like that and let's call it uh ball
3:04:49
positions and let's also refer to the correct path which is called
3:04:57
tracker uh stops and ball
3:05:05
detections do pkl let's run it and let's make sure
3:05:13
that it threaded correctly so it it threaded correctly um we can also copy paste the
3:05:22
The Filling of of the U the interpolation that we had so let me open
3:05:29
up the tracker again and the ball tracker and let's copy this
3:05:36
code and yeah let's copy this code and put it right
3:05:42
here um this is going to be for uh
3:05:50
aspd so yeah you just run it
3:05:55
again and now you just have the um uh a pandas data frame that you can uh plot
3:06:03
out um so yeah so the first thing is that uh we basically want to have the
3:06:10
position of the ball and we can can um make um like the like um calculate the
3:06:19
center of the ball and the way that we do that is that we can have um we can
3:06:26
also create the mid y only like the middle y uh and it's going to
3:06:33
be uh this one like the y1 + Y 2/
3:06:39
2 and this is going to be get us the mid middle of the Y afterwards uh you can
3:06:46
see that we have pretty smooth um pretty smooth uh detections but in some
3:06:52
scenarios we need to remove any outliers and we can do that by having
3:06:59
the rolling mean so we can uh add it right here we actually don't need it
3:07:04
here but let's add it um for other use
3:07:10
cases maybe other videos have this J action but we can have the rolling
3:07:18
mean and this rolling mean is going to need a window so we are going to have a
3:07:24
window of five and uh we are also going to set a
3:07:30
minimum period of one um and we are not going to
3:07:39
center it so Center equal
3:07:45
false um and we are going to get the mean um
3:07:51
afterwards uh we can basically plot
3:07:59
it so we can plot this
3:08:12
out
3:08:18
so when we plot it out like this you can clearly see where the ball was hit so
3:08:25
the ball was moving like this then it changed white positions here and it then
3:08:32
change white positions here it changed white positions here it changed white positions here and this is like the
3:08:40
normal behavior of the ball like if if you see that um the ball is moving in
3:08:47
the y direction like this and after it was hit it changed Direction so the ball
3:08:53
instead of uh being more and more like the Y coordinates is being increased uh
3:09:00
it suddenly changed directions and now it's it's decreasing till the other player starts
3:09:08
hitting it again and instead of decreasing the Y it starts increasing
3:09:14
again so we want to detect when exactly in the plot that the
3:09:23
um that this is being um like the Y coordinates is being
3:09:29
changed um we can uh we can do that by
3:09:35
like analyzing the difference between each point and the other point is it
3:09:40
increasing is it decreasing and and how much so we can define a Delta
3:09:48
y so we can have the uh ball
3:09:55
positions Delta
3:10:01
Y and then we have the uh define B positions rolling mean
3:10:08
and we get the diff this difference is just going to sub subract
3:10:14
the uh two consecutive um like rows from each
3:10:21
other and yeah we can also try and plot it out and it should give us
3:10:27
approximately a very similar graph so there you go it's a very similar graph
3:10:33
and you can also understand where the ball was hit here here here here and
3:10:41
here and yeah you can continue on with
3:10:47
that um so yeah to understand where the
3:10:52
ball was hit um we are going to Loop over this and we are going to determine
3:11:00
whether the ball is increasing or decreasing the Delta Y is increasing or
3:11:06
decreasing and we are going to get the position of the the frame number
3:11:13
where the ball started to uh decrease when it was increasing like this change
3:11:21
and it kept on changing for at least like 25 frames so we will check this and
3:11:28
when it's at the bottom we will check if it's increasing
3:11:33
again um it's going it's it's going to be a very simple code so we can have the
3:11:40
ball positions and we can have the ball hit
3:11:46
is all set to zero so we can have it all set to zero at the beginning and then I'm going to
3:11:53
Loop over this data frame and like
3:12:02
this DF um ball positions
3:12:09
minus int and I'm also going to have the
3:12:15
um minimum uh minimum change
3:12:27
frames for hit and I'm going to send it to 25 so at least it's moving uh like
3:12:36
increasing and then at least for 25 frames it's it kept decreasing so the
3:12:41
change here kept decreasing 25 frames at a row or like maybe not in a row but um
3:12:49
within a certain buffer uh so I can just uh have this uh
3:12:56
and uh loop over uh like the length of the ball positions till minus minimum
3:13:04
changes and let's put a buffer of 20% so let's multiply it by
3:13:11
1.2 and continue um we we want to detect if
3:13:18
there is a negative change so there is a negative change that is happening where
3:13:23
where the ball is here and then it decreased in value so we can have a
3:13:29
negative position change uh where is it's going to be um
3:13:39
uh like uh both positions Delta y um iock uh of of I iock is just getting
3:13:47
the like the uh row number I and it's going to be if if it's a
3:13:54
negative change then it's going to be greater than zero but the the preceding one is going
3:14:02
to be less than zero so it was increasing and then it was decreasing so
3:14:08
now it's going to be less than zero we also want to detect the uh positive
3:14:15
change which is it was uh decreasing and then it was uh increasing and then it
3:14:22
became increasing and we can call it here positive
3:14:28
change positive position change um and if there is a negative
3:14:36
change or a positive change um we can uh
3:14:42
begin to count how many frames the change uh kept on going for so for
3:14:50
change frame in uh
3:14:55
range I + 1 till I
3:15:02
plus int and then minimum uh let's call it like the uh oh
3:15:12
yeah so we need to multiply this here and let's copy this put it right
3:15:20
here and we uh yeah and let's add one to
3:15:30
it and for for this we will need to copy
3:15:35
paste the same thing again we will need to uh do it and detect if there's a
3:15:41
negative ch change or a positive change uh but let's call it change in the
3:15:46
following frame okay so now we have the change in
3:15:53
the following frame and
3:15:59
um yeah but instead of checking I + one we need to check the change
3:16:09
frame and if
3:16:15
and if there's and if there's a negative uh and if there's a negative
3:16:20
change and there is a negative change in the following position um we just change
3:16:28
count and make it change count plus one I change count plus equals 1 we want to
3:16:36
do the same thing for the positive change so it's going to be the same thing and at the end we want to have
3:16:48
if um and yeah here we just want to have
3:16:54
if the change count is greater than the minimum change um hit minus one and if if that's
3:17:05
the IDE if that's the scenario then we need to change the location uh like the
3:17:10
rule the the ball hit in the row number I to one so that uh we now have the uh
3:17:19
basically um uh the the ball hit position so let's run it you're going to
3:17:26
find a couple of uh wearning messages don't worry about it and yeah you can
3:17:32
run it again and you can see the ball hit a column that is uh already there we
3:17:39
can filter it to only produce a or to only give us the ball hits that are one
3:17:46
so let's do it like this so ball hit equal equals to one and
3:17:53
let's turn it so you can find that there's um a hit in uh position uh frame
3:18:01
11 frame 58 frame 95 frame 131 and frame
3:18:07
182 and let's check if that's correct so here the frame number will
3:18:13
come in handy so let's um let's move this and see so approximately frame 11
3:18:21
starts the hit and if we go back again here so we have a hit in frame
3:18:27
11 and if we continue down the line we can see that around uh frame 57 which is
3:18:36
here 58 um another hit was being done another
3:18:41
shot thought was being done and again right here uh around frame 95 which is
3:18:49
another um another hit we can also see here which is around
3:18:56
131 another hit is being done and the last hit is at frames
3:19:02
182 so the logic is being um uh so the logic is is quite good and we can
3:19:09
continue on from this so we can just um uh get those
3:19:17
positions by just copy pasting this then saying that we want the index of
3:19:25
it okay then we want it to make it to
3:19:30
list uh you need to yeah you need to remove those packets from the index and now you have it as a list we can now
3:19:39
just uh frame nums you can have that frame
3:19:45
nums with ball
3:19:51
hits okay so now it's all good you can uh paste it in right
3:19:59
here and you can also try and
3:20:08
uh finalize your code um just just going to copy all this put it all right here
3:20:17
so that I can copy the code and paste it in the ball tracker so we can uh from
3:20:23
here we can start by uh writing the
3:20:31
Define get ball shot
3:20:37
frames it's going to take in the ball positions
3:20:44
and it is going to run this
3:20:51
basically so again uh we need to uh convert this into a data frame so we can
3:20:59
copy this from here uh like that and yeah I think we're done so it's
3:21:07
it's uh it's um having it but we're it's not returning it yet
3:21:12
so we can return it and now the uh function is done so let's uh do it right
3:21:23
here and we can
3:21:29
detect ball shots and we can have the
3:21:35
ball detector ball tracker Dot
3:21:43
what's the get ball shot frames and we give it the ball
3:21:52
detections we can write here ball shot
3:21:59
frames now let's print it out and uh see the results if it's the same or
3:22:10
not
3:22:18
so uh I think I forgot to uh copy paste something which is initialization of
3:22:25
the uh ball hit so it's going to be ball
3:22:31
hit and it's going to be all zeros so let me run it
3:22:40
again so yeah right now we have the 1158 and 95 all the frames that we detected
3:22:47
before are now being detected so all now is
3:22:52
good we can keep printing it but uh yeah we we removing we'll remove it uh quite
3:23:00
shortly up next is just we want to uh convert the player positions into the
3:23:08
mini cord positions and this is going to help us draw the mini cord that's first
3:23:14
and the second thing it's going to help us uh determine the amount of distance that is being covered by any object and
3:23:22
uh by tracking it on the mini cord and not the actual pixels right
3:23:27
here um so let's uh start uh by doing
3:23:34
that uh so you can go back to the mini cord that we had and we are going to add
3:23:41
one more function which is convert bounding boxes to actual mini mini cord
3:23:48
coordinates uh so let me explain the logic first we are going to measure the distance between any key Point let's say
3:23:55
key Point 2 and the player itself and now we have the distance in
3:24:02
pixels but I want to measure how much like this distance in meters so what we
3:24:10
have for reference is that we have the actual height of the player so we have
3:24:16
the height in meters and we have the height in um in pixels so we can do
3:24:23
cross multiplications to find the distance between the second key point or basically the closest keyo and the
3:24:30
player position and then I can come here and
3:24:36
say okay I can I have the distance in meters can can we convert it back into
3:24:43
pixels and we already have this function so we can just call this function with
3:24:48
meters and it will draw it in the uh position that is going to be relative to
3:24:54
the court and yeah that is going to be the
3:24:59
whole logic of this um so let
3:25:05
me uh begin the code so we can have the
3:25:10
convert convert
3:25:17
bounding boxes to mini
3:25:25
cour uh
3:25:33
coordinates and we are going to take the um player uh
3:25:40
boxes and we are going to also take the ball boxes we're going to convert them here
3:25:47
into one function um and for convenience and then we are going to
3:25:54
take the original uh cour key
3:26:04
points um so yeah let's start first by let's start first
3:26:11
by uh defining the player Heights so we can say that um player one
3:26:20
has the constants dot uh player
3:26:27
one uh height in meters we can have the same thing done
3:26:35
for player two like this
3:26:43
and then um we can Define the output boxes output player
3:26:54
boxes and we can Define the output ball
3:27:03
boxes and the first thing that we want to do is we want to Loop over the
3:27:09
frames so we're going to have the uh frame number
3:27:15
player uh bounding box and enumerate which is going to uh return back the
3:27:21
index that we are are looping over and let's Loop over the player bounding boxes right
3:27:29
now so uh the I so in the player bounding
3:27:34
boxes there are multiple tracks so we are going to Loop over each track so I
3:27:40
can have the play player ID and uh I can also do the bounding
3:27:47
box in player. BB box. items and now I
3:27:54
have it uh ready um the first thing that we want to
3:28:00
do is that we want to uh get the foot position of it so the foot position is
3:28:08
basically going to be like we are going to get the middle of the uh of the Box
3:28:16
in terms of X and then get the maximum y so it's going to be right here um we
3:28:23
don't want to have it to in the middle because here is actually where the uh
3:28:28
the player is standing it's not here it's uh it's actually here so to do that we can go back to the
3:28:38
utils and add another uh function in the uh BB box utils uh it's going to to be
3:28:47
called a get foot position so we can have the get
3:28:55
foot position and it takes in a bounding box
3:29:00
and it returns in the foot position so uh we can do it like
3:29:08
that so X1 uh Plus X2 which is the ex uh
3:29:13
like the x and x and we can divide it by two and we return also the uh maximum
3:29:21
key point we also want to uh expose it uh in the
3:29:29
init and we want to uh import it so we can get the foot
3:29:40
position of the BB
3:29:45
box and uh this is the foot
3:29:50
position okay uh now I want to get the closest
3:29:56
key point so I want to measure uh like uh like we we want to
3:30:04
get the closest uh key Point uh um
3:30:11
in pixels basically and we don't have to search
3:30:17
all the key points uh we can limit it to a couple so let's choose them right now
3:30:23
um so you have this zero which is going to represent the end and we have the two
3:30:29
is going to represent the other end and let's also take the middle of the course which is going to be 12 and 13 uh this
3:30:37
is going to be fair enough let's not uh overdo it and search all key points so
3:30:42
let's search only zero and two which is the extremes and two middle points which is 12 and 13 this one and this
3:30:52
one um yeah so we will need to have um
3:30:58
function get get closest key
3:31:04
Point index uh that basically takes in the
3:31:09
foot position
3:31:15
and the uh original key points and the uh filtered like the the
3:31:23
the key points that we want to search we said zero two and 12 and
3:31:29
13 and uh we return back to the uh closest key Point uh
3:31:37
index and this closest key point we will be uh using to measure the distance
3:31:42
between it and the player and uh yeah it's going to be the point of reference
3:31:49
uh for us so let's also add this uh get closest
3:31:55
key Point uh index uh to the uh BB box
3:32:05
utils so we can have it right here get close
3:32:11
closest key
3:32:16
Point index and we can have the point
3:32:21
that we want to uh measure the distance from we can also get the key points and
3:32:27
the keyo indices that we want to have and yeah we can uh loop over them let's
3:32:36
remove the suggested code and we can get the closest uh
3:32:44
distance which is going to be float of infinity right now and we can get the
3:32:53
key Point index um which is uh going to be
3:33:00
key Point uh candidates of zero we're just going to take the candidate zero right
3:33:07
now and overwrite it when we Loop then we are going to Loop over the key
3:33:16
Point candidates uh
3:33:24
indices so let's call it index in keypoint
3:33:29
indices and let's remove all to the suggested
3:33:34
code I don't think that it's going to work for us so we can uh write that the
3:33:41
key point is equal to um key
3:33:47
points of key Point index times
3:33:54
2 and then we want to also have it for
3:34:00
the Y so it's going to be the same but plus one at the end then we are going to
3:34:07
measure the distance which is going to be uh only in
3:34:14
y distance so let's only measure y distance so point1 minus uh key Point uh
3:34:26
1 and if distance is smaller than the closest key Point um then what we do is
3:34:35
that we assign the closest like the we assign the distance to the closest key point and then we we have the new index
3:34:42
uh that we want and at the end we can just return
3:34:51
it let's now expose this function um to the inits again so we can
3:34:58
access it let's go back to the bounding box um uh to the mini cord and we add
3:35:07
also this function and let's also uh yeah so it's
3:35:12
already being utilized here then we want to get the player
3:35:18
height in pixels so let's uh get the player height in
3:35:26
pixels um I want to also show you something before we get the player height is that the player might be
3:35:35
launching and is not uh straight up like like this one and this one so uh the
3:35:43
idea is that I'm going to get the maximum height within the fif within a 50 frame to ensure that the pixels truly
3:35:52
represent uh the total height of the player uh so let me uh try and get the
3:36:01
uh frames that we are going to search for um so let's uh get the
3:36:07
frame uh index uh minim
3:36:13
and it's going to be the maximum of zero and frame number minus 20 so we're going
3:36:21
to uh do um uh we're going to go back 20 frames and we want to also have the
3:36:29
maximum number the maximum index which is either going to be the length of the
3:36:34
frames or frame number uh plus 50 so we can go up to uh up to 50 frames
3:36:42
um then we want to detect the height of the Box in pixels so we can go back to
3:36:51
the utils and add another function um to
3:36:57
that so we can have Define get
3:37:02
height of uh BB box and it basically
3:37:08
takes a bounding box and let's see the
3:37:15
um return and it returns back the height
3:37:20
which is the maximum y minus the minimum y we can also expose it right here and
3:37:28
we can import it here and we can simply
3:37:34
uh get the heights of this so uh we can say BB boxes
3:37:41
Heights in pixels and we can simply have like uh
3:37:51
four I in range and it's going to be frame
3:37:58
minimum till frame maximum and we are going to get
3:38:05
the um get the height of the bounding box and and this is going to be player
3:38:12
bounding box of I now we have a list of heights of
3:38:18
bounding boxes in the frames of in the in the list frames that we want um we want to get the maximum one
3:38:27
so we can say max player height in
3:38:34
pixels and we can get the uh maximum bounding box uh
3:38:44
height um afterwards we want to get the
3:38:50
um the court position so now we have the enough information to um convert this
3:38:57
into the court position that we want uh so let's create another function that is
3:39:03
called get mini qu position so we are going to Define
3:39:11
another function so get mini
3:39:17
cord coordinates it's going to take in the object
3:39:23
position uh object
3:39:29
position it's going to take in the closest uh key
3:39:39
point and it's going to also take the closest keypoint
3:39:46
index and it's also going to take the player height in
3:39:57
pixels and let me just uh organize it into different lines so that it can be
3:40:04
easily uh seen and
3:40:11
so uh player height in pixels and then uh player height in meters so
3:40:18
player we can copy this and say
3:40:25
meters um yeah so right now we have the closest key Point index um let's also
3:40:33
Define the um like let's get the actual point
3:40:39
so we can say closest
3:40:44
um key
3:40:49
Point equal yep so it's going to be the
3:40:55
original key point to the closest key point and then multiply it by two and we
3:41:00
are also going to get the Y position of it okay so sounds good uh now we want to
3:41:09
continue with the mini uh with the mini cord coordinates um we want to first uh get
3:41:16
the distance uh between like the distance X and the distance y uh between
3:41:24
uh the closest key point and the player so we can get it so we can say
3:41:32
distance um from keyo
3:41:38
X pixel pixs then we can say distance from Key
3:41:44
Point y y pixels and then we can say it's equal to
3:41:53
measure XY distance and you give it two points
3:42:02
which is object position and closest key Point object position and closest key
3:42:08
points now we don't have the function yet so we can go back to the BB to the bounding box utils we can um basically
3:42:18
Define it and see it right here like now we get the X position the X difference
3:42:24
and then the Y different difference uh separately and when we return them both
3:42:30
we also want to expose it in the init and we also want to import it right
3:42:38
here and after we get this um we want to
3:42:44
convert this distance into meters so let's uh
3:42:50
convert pixel distance to
3:42:57
M and what we do is that we write distance from Key point x in
3:43:05
met equal um convert pixel distance to meters and then we
3:43:13
give it the pixels and we also give it the player height in meters and then the
3:43:20
uh player height in pixels so um player height in meters right
3:43:26
here and player height in
3:43:36
pixels we want to do the same thing but for the Y position so let's copy paste
3:43:43
it and get it also for the Y
3:43:49
position like that
3:43:58
and and now we have the meters ready so this is the amount of meters that they
3:44:03
that the player has uh really uh like um
3:44:10
moved and now we like uh this is the amount of meters that is between the key
3:44:17
point and the player and now we just want to convert this into play like
3:44:24
pixel coordinates again but for the mini qut so it's going to be for the mini size
3:44:31
qut so we are going to say the convert to mini Court coordinates
3:44:41
and what we do is that we write mini cord X
3:44:50
distance in pixels self do we have a already made
3:44:57
function for that which is convert meters to pixels and we just give it the
3:45:03
meters so like like that we do the same thing for the Y coordinates like this uh
3:45:09
we change it here to the Y and we change here also Y and yeah we also have we
3:45:16
also can get the closest mini position the closest uh Mini U uh mini Point Key
3:45:24
Point uh it's going to have the same order as the original key points so we
3:45:30
don't have to do any calculations here we just uh need to get the position of it so we can say
3:45:38
closest mini qu key
3:45:46
point is equal to um
3:45:52
self. drawing uh drawing uh key points
3:46:03
of closest uh keyo index time 2 and we also
3:46:11
want to have this for the Y but we are going to add one because it's a y
3:46:17
position and yeah that is it let me just format the bracket
3:46:25
correctly and at the end we just want
3:46:30
to um add the distance in pixels to the mini cord position to have the last
3:46:37
position so it's going to be mini cord
3:46:43
player position is equal to um mini cord player position of zero
3:46:52
times the distance in X and we want to have the same thing for the Y and yeah
3:46:59
that is it we can return back the results like
3:47:05
that and yeah we can now call it here so so we can call Mini uh
3:47:14
Court player
3:47:20
position position which is going to be calling get mini court court and we give it the
3:47:29
foot position and then we give it the closest key point then we give it the closest key Point index then we give it
3:47:38
the height and pixels of the player and we also give it the player height in
3:47:45
met uh we then uh want to uh assign this
3:47:52
so what we want to do is we want to have an output dictionary for each frame so
3:47:59
when output player uh BB boxes uh dick and it's
3:48:07
going to have the play ID as the key as usual and it's going to
3:48:15
have the position as the value now we want to do the same thing
3:48:21
but for the ball and since the ball doesn't have an exact height or the
3:48:26
height of it is going to be very small um we are going to use the closest uh
3:48:32
player to the ball and we are going to do the same calculation for it um so
3:48:39
yeah so let's calculate the uh balls first so um let's get the ball
3:48:48
uh box which is equal to ball boxes of frame
3:48:54
number and then we have the uh ball position uh and we are going to get the
3:49:00
uh center of the Box um let's not get the uh foot of it right now but let's
3:49:06
get the center of it and we can get the center of the Box um and we can call it
3:49:14
off uh BB box uh we can go here we can Define get
3:49:23
center of the BB box and we can return and write it right here so this is going
3:49:30
to get the center of the Box uh which is going to uh get both x's and divide them
3:49:38
by two get both y and divide them by two and this is going to get the center of the Box um then we also add it in the
3:49:47
init we also import it here in the um
3:49:53
mini uh position and now we can U we can utilize it here so now we have the ball
3:50:00
position um we can get the uh closest player ID to the
3:50:06
ball closest player ID uh to ball and this is going to be
3:50:15
the minimum of the player uh BB box do
3:50:24
keys where um actually it it it's uh it did it
3:50:32
quite good so this is what we do measure distance I think we already have the
3:50:38
measure distance in the utils right now so we don't need to rewrite it so let me
3:50:45
explain what the suggested code was all about um so right now it's going to
3:50:52
measure the distance between the ball position and the uh get foot position
3:50:57
let's let's also get the center of it let's get the center position um and the center position of
3:51:04
the player so it's going to measure the distance between this and this and it's Al Al it's going to return the key of
3:51:12
the minimum player bounding box and yeah
3:51:19
so that is it so we can go here
3:51:28
and we can yeah we can go here and we can write the the code for the ball
3:51:35
which is if the closest
3:51:40
uh if the closest player ID to the ball is equal equal to the player ID uh what
3:51:46
we want to do is the to get the closest key point also so
3:51:53
closest let's copy paste it so we need to get the closest key Point
3:52:01
again like that and instead of uh using the foot position we're going to use the
3:52:08
ball position
3:52:13
and now we can just run the mini cord function again like
3:52:21
this and instead also of the of the foot position we write the ball position and
3:52:28
now we have those two in place and the maximum height and the player height are
3:52:35
also being put um now the last last thing is that we want to have an output dictionary so
3:52:42
let's call it
3:52:47
um output ball BB box um so yeah um
3:52:57
let's so let's just add the output to the uh to our list which is going to be
3:53:06
output ball boxes do append and it's
3:53:11
going to be one because it's only one one uh one uh ball and we're going to
3:53:18
get the mini Court position right here um and at the end we want to return
3:53:27
both the so return the output player
3:53:35
dictionary and the output balls um actually we don't want to
3:53:42
return the uh we don't want to return that we don't want to return the
3:53:48
dictionary we want to return the output player boxes for the whole frames so
3:53:53
let's add it right here and uh and let's replace it
3:54:01
here so now we are ready so this is the uh coordinates of the um mini cord for
3:54:09
the players and the balls so we can go back to the main and we can call it from
3:54:16
there right here we are going to uh
3:54:21
convert the positions uh to mini Court uh positions
3:54:31
so uh we are going to write player uh mini cord
3:54:37
detections and we are also going to write ball mini
3:54:44
core detections and those are going to be
3:54:51
equal to mini do convert to mini Court positions
3:54:56
and we give it the court points and uh
3:55:02
uh yeah so we give it the uh player detections and the ball detections and
3:55:07
the court key points so we need to also give it the uh Court key points right
3:55:12
here like that and yeah uh now we want
3:55:23
to uh basically display this on the mini cord so we can have uh like actually
3:55:30
let's run it first make sure that nothing crashes and then we can create another function that draws uh those
3:55:37
positions onto to the mini cour
3:55:48
itself okay so we have a small
3:55:53
error uh I'm going to trace it back and come back to
3:55:58
you so I uh so the problem was that I renamed the function here it was convert
3:56:05
to Min cord positions it should be convert bounding box to mini cour coordinates um so let me run it again
3:56:13
and see if we have any more
3:56:19
errors okay we have one more error which is in line 32 of get center of the box
3:56:27
and uh I think the box has a key zero error so let me trace it back and come
3:56:34
back to you so I had two problems in the code one is that I was treating this as a
3:56:40
bounding box B bounding box but it was actually a dictionary so I needed to get
3:56:46
the one track the track number one and this will be now a bounding box and the
3:56:52
other one is going to be the um uh this one um I was uh giving it a
3:57:01
dictionary I needed to filter out the current player ID and this is how I did
3:57:07
it um and yeah that is now a bounding box also so if you can rerun it
3:57:18
again it should be working fine right now so now it's working fine um but we
3:57:24
want to also see the uh results so we're going to make another
3:57:31
function that is going to add the uh uh
3:57:38
the this drawings to it and we are almost uh uh finalized
3:57:46
with this mini cord so bear with me a little bit so to draw any points on the
3:57:52
uh mini Court we can just call draw uh
3:58:00
points on Mini
3:58:07
qut and we can write the self we can get the
3:58:13
frames and we can get the positions that we want to uh write it on and we can
3:58:18
also specify a color we can give it um um a default
3:58:26
color and we can Loop over the frames frame
3:58:31
number and frame and numerate frames
3:58:39
um we can also Loop over the positions that we want to uh uh that we want to
3:58:47
Output so uh right now we have the position of this Frame number we have the player ID we don't need it so we can
3:58:56
uh remove this we have the position and we can draw a circle with the frame and
3:59:02
the position and uh then uh the radius the
3:59:08
color and it's filled uh just to make sure that the
3:59:14
position is in we can just uh write it like this
3:59:19
position and we can make it as ins like
3:59:26
that and like that just to make sure that those are ins actually um and yeah
3:59:34
X and Y so so we can call this on our
3:59:44
code so right here uh we can have the output frames equal mini cour Dot and
3:59:52
then draw points on Mini
4:00:02
qut and then we uh give it the output frames we also give it the uh
4:00:08
positions uh that we want to uh put which is the player mini Cod
4:00:14
detections player mini cord detections and we can do the same for the
4:00:19
balls uh so we can call the ball uh mini
4:00:26
detections and we can give it another color just to differentiate both of them
4:00:32
and uh color is equal to uh 0 250 5 and
4:00:39
then 255 that's another color um we can then
4:00:45
uh run
4:00:54
it okay we have another error so let me trace it back and come back to you
4:01:00
guys so yeah we didn't return back the frames so we can just return it back
4:01:07
here return frames and it should work
4:01:26
fine so let's open the output and we don't see the key points
4:01:33
yet we don't see those uh the players yet on the
4:01:41
here let me trace it back and come back to
4:01:46
you so if you were following along I made a small mistake when the brackets
4:01:52
um right here in the closest mini uh key points I did uh the plus one outside the
4:01:59
bracket it should be inside so this was the problem so you can save it and you
4:02:07
can rerun it again again and you should find that the output has been uh on the
4:02:14
on your output video just wait for it a little bit and
4:02:19
yeah that is it um so you can open this
4:02:25
here and you can see how the player is
4:02:31
relative to the uh position here and the other player is here and the ball is
4:02:36
also very close to to its position and if you run it you're going to see that the ball is moving quite correctly and
4:02:44
the it's the ball is quite um that the P pill is moving correctly and the ball is
4:02:50
a little bit jumpy because it's fast um but otherwise everything looks good and
4:02:56
we can proceed from here so the last thing that we are going to work on is going to be um is going to
4:03:06
be the output of the kilometers per hour and I'm going to show you the output the
4:03:13
final output again and this is it that is the last thing that we are
4:03:20
going to work on it's going to have the uh shot speed and the player speed and
4:03:26
it's going to also um like count how many uh how many
4:03:31
shots that the that the player has uh shot each player has shot and I'm not
4:03:37
dis exping it here but we'll be calculating also um so let's uh Dive Right
4:03:45
In this is the last bit but afterwards you're going to have a super cool um
4:03:52
portfolio project to add to your CV so it's going to be totally worth it um yeah so let's jump into the main
4:04:02
and I think we are not going to need any other classes maybe I'm wrong but uh I
4:04:10
think uh we're done with those and the way that we are going to
4:04:17
do it is that um we are going to uh loop
4:04:22
over each shot in those frames and let me go
4:04:28
through the logic first so uh we are going to go each shot in
4:04:33
the frame so we have this uh this Frame number which is frame number 11 for this
4:04:40
shot and we have the other shot which is this one um which is frame 55 uh we are going
4:04:50
to measure the distance that the ball have covered um we are going to measure
4:04:55
it in uh U measure it um in the in pixels first maybe in the uh mini mini
4:05:02
qut and uh we can then switch it to meters
4:05:08
and uh we also have the uh frame difference so we know that this Frame is
4:05:15
um frame number 11 and it took it around um till frame 55 which is around maybe
4:05:25
uh 40 something frames to uh go there and we know that per second we have 24
4:05:31
frames so we can so we can measure the time in seconds and we have the meters
4:05:37
so we can measure the um the speed which is the kilometers per hour uh we also
4:05:44
have like this is the player who shot the ball we also have the position of
4:05:49
the opponent player and the amount that he covered the amount of um meters that
4:05:55
he covered and we also have the time that he covered it in so we can also
4:06:02
measure the player speed so we are going to Loop over the shot and take the next
4:06:08
chot into consideration and uh measure the distance covered by the opponent player
4:06:16
and the ball and basically um calculate the uh the kilometers per hour from
4:06:26
here so let's uh so let's start
4:06:32
um so for the for the shots we are going to
4:06:38
um uh we are going to Loop over the shot which is going to be shot index in range
4:06:45
length and we are going to have it uh
4:06:51
shot frames which we got
4:06:57
earlier and um we are not going to include the last one because the last
4:07:05
one doesn't have another one uh that is going to be uh like another uh frame so
4:07:11
we can't measure the the exact distance covered or the uh the amount of time
4:07:18
covered uh but we are going to measure it for the uh for all other ball
4:07:25
shots and yeah we can uh get the start frame
4:07:31
basically which is going to be the ball shot and uh we are going to get the ball
4:07:37
shot in Index this is the uh start frame and the end frame of the shot is going
4:07:42
to be the next um the next bullshot so it's going to be bullshot index +
4:07:50
one uh we can get the time difference in seconds of the bullshot which is going
4:07:56
to be uh bullshot time in
4:08:04
seconds which is just going to be the uh end end frame minus start frame over 24
4:08:12
because we have 24 frames per
4:08:17
second um then we have the uh get distance uh covered by the
4:08:29
ball and first we want to measure the distance in pixels so what we do is that
4:08:34
we get the distance uh covered
4:08:39
by ball in
4:08:45
pixels and we are going to measure the
4:08:51
distance we have this function in the utils I don't know if we imported it here or not so I don't think that we did
4:08:59
so let's do that here and yeah so let's continue on and so we have the measure
4:09:06
distance function and it will take the uh
4:09:12
ball mini cord detections of start frame
4:09:18
and it's going to take the ball mini cord detections of the end
4:09:24
frame and because we only have one uh track so then we are going to just get
4:09:31
the uh one yeah so we can we can use the convert pixels to me meters um that we
4:09:39
have in the mini and it should return back the
4:09:45
meters uh now to uh measure the uh speed so speed of the
4:09:51
ball shot in kilm per
4:09:59
hour um we have the speed of the ball which is going to be the distance
4:10:05
covered by ball in meters over the time in seconds time 3.6 and this time 3.6 is
4:10:11
just going to convert it to kilm per hour um now this is uh going to be the
4:10:19
speed of the ball uh now we want to get the speed of the opponent player so we
4:10:24
can have the opponent uh
4:10:30
player uh uh we can have the opponent player speed and before that we can also have
4:10:40
the um we can we can uh but before that we
4:10:45
need to understand which uh which player shot the ball so we can do that by
4:10:52
simply measuring the uh distance between the ball and the the two players and
4:10:58
getting uh the player that is closest closest to the ball when the ball was shot so we can do that by simply doing
4:11:07
that player who shot the ball we want to do that so player uh we
4:11:15
want to get the player positions uh and the player mini cord uh detections of
4:11:21
the start frame let's get the player that is closest to the ball so we can get the player who
4:11:28
shot uh the ball which is going to be mini uh minimum of uh player uh
4:11:38
positions do keys and we are going to have the
4:11:47
Lambda uh player ID and we are going to measure the
4:11:54
distance and the distance we are going to measure it is between the player position and the ball position so we
4:12:02
have the player positions of uh player I
4:12:09
and we also have the ball detections of
4:12:14
start frame of one and this is going to return back the player ID with the
4:12:20
minimum distance uh with that in hand we can
4:12:27
also uh def know which uh which which
4:12:32
player ID is the opponent which is going to be players
4:12:38
um opponent opponent player
4:12:45
ID is going to be opponent player ID one is going to be one if the player shot
4:12:51
the ball is equal to zero and else it's going to be
4:12:57
um actually it's it's going to be one if it's going if it's two and else is going
4:13:04
to be two so let's say that the the player who shot the ball is player uh
4:13:09
two I'm going to return one uh as in the opponent player I'm just going to return the inverse of it and if it's not one if
4:13:17
it's not two then I'm going to return two that's the opponent player um I want to uh measure the
4:13:26
distance covered by the opponent in pixels so
4:13:31
distance just like what we did in the ball uh but we are going to do it for the
4:13:40
covered by the opponent player by uh
4:13:48
opponent in pixels and it's going to measure the
4:13:54
distance between the uh player um it's
4:14:00
going to player like the start frame of the of the opponent ID and the end frame
4:14:06
of it so that is good now we want to convert it into meters so that is also going to
4:14:13
be the same as the mini qu uh one and then we want to measure the speed so
4:14:23
speed of
4:14:30
opponent opponent which is equal to the distance covered by opponent over B shot
4:14:37
time frames in second which is going to be the same uh frame time 3.6 to make it in kilm per
4:14:44
hour uh yeah so now we have the speeds and we have uh the speed of the ball and
4:14:51
the speed of the opponent uh we just need to put it in a type of a uh
4:14:58
structure data structure so that we can um display it in a better way so I am
4:15:05
going to choose to display it in a list of dictionary uh because it's going to
4:15:10
be easier for me to change it to a pandas data frame and to um expand it to
4:15:16
the whole um other frames as well so let's create this um data structure
4:15:25
which is going to be just a list of dictionary uh stats uh
4:15:32
data it's going to have a list and this list is going to be a dictionary uh the
4:15:39
first one is going to be a dictionary it's going to have a frame
4:15:44
number which is going to be zero at the beginning then it's going to have the
4:15:51
player one number of shots which is going to be
4:15:59
zero then uh it's going to have the
4:16:05
player one uh total uh shot
4:16:14
speeds now this uh now the number of shots is the number of times that the user that the player have shot the ball
4:16:22
the total speed is the summation of all the speeds that the user have done and you can calculate the average
4:16:29
by just um having this over this like this number over this number you can get
4:16:35
the average so I'm not going to have the average right here but I'm going to calculate it
4:16:41
later and we can have the player one last uh shot speed so this is the latest
4:16:50
shot that he did what's the speed of it and we can also do it with zero and we
4:16:57
can have the player one uh total distance uh total player speed um so
4:17:05
total player speed which is going to be zero
4:17:11
and we can also have the actually let's last player speed we can also have
4:17:19
the last player speed on and we can do the same thing for the um player two so
4:17:26
number of shots and the total speed of the shot the last shot uh the player
4:17:33
speed uh the last uh player speed as well
4:17:39
um so that should be it um so let us uh
4:17:46
import a copy uh mechanism which is from copy import deep copy because in order
4:17:55
to copy a dictionary you need to um uh copy it and not copy it reference so
4:18:01
deep copy helps us uh to copy the values um and the way way that we're
4:18:07
going to do that is that at the end of
4:18:12
this uh we are going to uh create a a status uh like the stats the
4:18:20
statistics so we have the current player stats which is going to be a deep copy
4:18:29
of the the the previous player stats and we are going to overwrite some things so
4:18:36
for examp example the frame number is going to be the sort of the frame number and then we want to have the uh
4:18:45
player number of shots which is going to be player number of shots plus one we want to also have the total speed to be
4:18:54
added uh we also want to have the um
4:19:00
last shot to be added here and we want to add the opponent player so the
4:19:08
current opponent player which is uh right here we want to add to the total speed of it and we want to add the last
4:19:16
speed and afterwards we want to have the player stats data. append current player
4:19:25
stats so now we have for each start frame we have this dictionary again but
4:19:31
with the new stats and for that we will need um like
4:19:42
um now we just have the uh like the short frames and we want to expand it to
4:19:48
the whole list of frames so that we just can Loop over without too much logic and
4:19:55
um basically from frame zero to the first start frame we just want to
4:20:01
duplicate this again and again so that we have um like uh
4:20:08
so that for each frame we have its statistics um we can also like Loop over
4:20:14
it and um do some logic so that we can uh know which uh position to to choose
4:20:22
from here but I'm going to uh choose to duplicate it and to make it into a
4:20:27
pandas data frame so that it can be easier to um
4:20:33
display so let me change it into a um first the data frame so data. DF uh I
4:20:42
don't know if we have pandas already here so I think we do maybe we don't um and then we have it so let's
4:20:51
import
4:21:00
pandas now we have it as a data frame um let's also have a frames number data
4:21:06
frame so frames DF which is going to be PD data frame which is equals to uh
4:21:14
frame number and it's going to have a list um
4:21:20
of range of length of the video uh this is going to be a data frame with frame
4:21:26
number and it's going to have zero till the uh length of the frame
4:21:32
number um I think there's a bracket missing or
4:21:37
something like that let me figure it
4:21:42
out yep there was a bracket missing and I just added it right here
4:21:50
and now we can just do this and merge it so now we are merging
4:21:59
the uh frames data frame with the player stats and I'm going to have it uh left
4:22:05
join on the frame number and that is going to result in multiple rows going
4:22:10
to have n because only the start frames of the B shots have value so other
4:22:17
things will have n and I want to fill it so the way that I'm going to do it is
4:22:24
that I'm going to do a front fill and uh basically like this which is equal to FF
4:22:34
fill it's going to replace a nan with its previous value that is not a Nan and
4:22:40
do this so on and so forth so that every frame we have the um we have the output
4:22:47
of it um now I want to uh basically calculate the average of it so let's
4:22:54
calculate also the player tats and data DF of
4:23:03
player average uh shot
4:23:10
speed and we are going whips we are going to um divide the total over the number
4:23:18
of shots um I think I misspelled it right here so let's um do this
4:23:28
and player one uh short
4:23:35
speed over the number of shots this is the correct
4:23:41
one um it's not it's it's it should be player one average shot speed and let's
4:23:50
me check this player one to to shot speed and the player one number of
4:23:57
shots that looks correct let's do the same thing for player
4:24:04
two and let let's do the same for the player speed so this is the player speed
4:24:11
and it's also getting the total over the it's not um it's not doing the over
4:24:19
correctly so um it should get the
4:24:28
other so it should have the total speed over the opponent's number of shots
4:24:34
because the player only should only like we are only calculating the run when a
4:24:41
user shoots and uh how the uh opponent reacts to it so this is the player one
4:24:50
over the number of shots that were done over player two and we're going to do the same for player two and we're going
4:24:58
to get the total of player two over the number of shots done by player
4:25:04
one so now all all the statistics are done we are just missing the last
4:25:11
drawing of this so we need to um draw this uh draw those tats and
4:25:20
yeah uh and we are done we are good to go
4:25:27
um so in the utils uh we can uh do another um another
4:25:35
function uh another file
4:25:41
called player
4:25:47
stats dra utils.py
4:25:52
and we are going to put the uh to put the uh the the drawing logic here it's
4:25:59
not going to be logic just going to be drawing um it's uh it's going to be easy
4:26:04
to do but uh it's going to consume a lot of lines so I thought to put it in the
4:26:10
utils and not in the main just to keep the main clean uh so we have the numpy as NP and
4:26:17
we also want to import CB2 and let's define the function so the function is going to be
4:26:25
draw player stats and we are going to have the
4:26:32
output uh video frames and we are going to have the
4:26:37
player stats and we are going to Loop over it
4:26:44
so Loop over the uh player stats so in
4:26:51
player stats dot it
4:26:58
RS and uh we have the player one shot speed as in row of player one
4:27:09
last shot speed we have also Player Two Shot speed
4:27:15
that is going to be last player two shot speed um we want to have the player one
4:27:24
speed which is going to be um player one last player uh speed
4:27:32
and we want to have it also for player two um we want to also get the average
4:27:38
player speeds so average one player shot speed and then the uh player two we want
4:27:47
to do it for the speed also um and average player
4:27:53
speed um now we want to get the frame so
4:27:59
frame is equal to the output frame of uh index should be index
4:28:08
and now we want to have uh
4:28:14
basically it's not that one um we want to have a black transparent box so we're
4:28:22
going to add also the position of the box and then make it transparent and and then we're going to
4:28:29
add those um um
4:28:34
statistics so adding those statistics are going to
4:28:42
be uh we are going to need the shapes again because we're adding a transparent
4:28:49
uh uh black box which is going to be also zeros like the one that we did
4:28:55
above above it and um we want zero like frame and we
4:29:05
want to Al to have it u in 8 let's write it correctly this
4:29:11
time and then we have the width is equal to 350 the height is equal to
4:29:20
230 we also want to um Define a start
4:29:25
and an end X so start X is going to be um frame.
4:29:34
shape of uh 1 minus uh
4:29:42
400 and we also want to have the start y
4:29:48
um which is going to be of zero and I think I wrote shape
4:29:55
wrong so let me fix
4:30:00
it and uh 550 and let's let's also Define the X's
4:30:08
so we have the end X is going to be start X Plus width and then end Y is
4:30:13
going to be start y plus uh the height um then we are going to have the overlay
4:30:21
which is going to be this one it's going to be the
4:30:29
overlay start X start y and x and y and
4:30:34
we are going to to uh put a black one this time a black box this time and it's
4:30:40
going to be filled and we are going to Define an alpha of also 0.5 so we are going to add it weighted
4:30:50
again and we're going to add it overlay the alpha the frame and then we have uh
4:30:58
the rest of it um then the output video frames
4:31:06
um then we can just have the output video frame of
4:31:12
index is equal to the overlay is equal to the frame
4:31:22
sorry okay now it's time to put in the text uh now the text is going to be
4:31:29
um like the text is going to be just putting the text like the the times that
4:31:36
we put the text here before um it's just going to be a matter of choosing the positions so I'm just going to copy
4:31:43
paste it and walk you through it so I copy pasted it right here and uh
4:31:50
right now we have the player one player two and then I put the text I chose the
4:31:58
start position and the end and start start x and x uh I also chose the colors
4:32:06
I did the same thing I put the shot speed I then wrote The Shot speed
4:32:13
themselves and then I did the same for the player speeds and then I did the same for the average speeds uh So
4:32:20
currently right now what I want to do is export this is expose this
4:32:26
again so uh from dot
4:32:31
uh uh player stats import uh draw player
4:32:36
stats we want to also import it in the main right
4:32:42
here like this and we want to now draw
4:32:47
it so uh let's draw player
4:32:53
stats and and we can have this like this so we
4:33:00
can have it uh like this draw the like call the draw player stat function and
4:33:08
now we just run
4:33:16
it so there's a so there's an error here that is called uh convert pixels to
4:33:22
meters um because the mini cord function does not have convert pixels to meters
4:33:28
it has convert meters to pixels so we will need to um so we will need to
4:33:35
import that from the utils convert meters to
4:33:40
pixels and we also want to import the uh
4:33:52
constants so what we do here is that we just want
4:33:58
to uh convert it and use the double line width like the width of the
4:34:05
uh the the field in meters and we also have the width of the mini cord so we
4:34:11
are going to use those to do some to convert the um pixels the pixel like the
4:34:19
pixels uh done into uh meters so what we're going to do is that
4:34:25
we are going to do like this we're going to choose the meters
4:34:31
right here then we are going to give it the
4:34:36
reference uh uh the reference um meters
4:34:42
which is going to be uh constant. double uh whoops it's not that was
4:34:50
filled incorrectly so you have the
4:34:58
width and then you have the mini quart and then you can get width of the
4:35:04
miniart um get mini height I think I need the width of
4:35:13
it um let me go and check if there's the width
4:35:18
ready this function get mini
4:35:24
cord get width of mini chord I think we have this
4:35:29
function so yeah so we have the get width of mini chord
4:35:36
and we will do it again right
4:35:42
here and instead of that we can use this and just delete
4:35:49
that let's run it
4:35:58
again so uh player one last shot speed I think this one is in in
4:36:07
the uh drawer because I added another S I think there shouldn't be an S like
4:36:13
here uh but let me check the line line 139 which is yeah so it's
4:36:21
going to be the uh drawer so yeah the speed is going to
4:36:28
be speed not speeds um so like this so let me run it
4:36:34
again
4:36:48
and now it's done so you can go back to the output and see it so um there is a
4:36:56
little bit of overlap so you can actually push it down a little bit so let's do that um let's uh move move this
4:37:05
here uh so let's move it down like 50 pixels so let's make it start at 50 uh
4:37:12
500 not 550 um let's also specify the width to
4:37:18
be a little bit more uh I think it's going um
4:37:26
above no it's not um oh yeah because it's not um so you're
4:37:35
going to find it to have uh oh there's some weird numbers
4:37:41
going on so we have some weird numbers like
4:37:46
here like 1,000 km/ hour and here is also 1,000 km/ hour uh let me trace it
4:37:52
back and come back to you but uh let's first before tracing it back let's see
4:37:58
if uh if this would push it down a little bit more like 500 the make it 500
4:38:04
and instead of 550 and let's see if there's something else that breaks but it
4:38:12
shouldn't Let's cross our fingers and we should be able to see the
4:38:18
box but we should still be uh seeing some weird kilm per hour that we need to
4:38:26
fix so yeah so right now it's uh it's it's actually good but the kilometers
4:38:33
per hour is way too much and I'm going to trace back Y and come back to you uh
4:38:38
so give me a minute so I'm back and I know the error um I've used the convert
4:38:45
pixels to this I've used convert uh meters to pixels uh and I should have
4:38:51
used the convert pixels uh to meters so I I have the distance covered in pixels
4:38:57
and I want to convert it to meters but I used the wrong function and uh you should be using this one convert pixel
4:39:03
distance to meters and if you run it again uh you should be
4:39:08
able to get the correct
4:39:21
output so you can now see um so you can now see as as soon as the player hit the
4:39:30
ball you can see the shot speed of the play player like this is 33 km/ hour and
4:39:38
player two is going to move by uh 1.7 km/ hour and when the other player shot
4:39:45
you can see that it was a harder shot by a 43 km per hour and the other player uh
4:39:52
moved with 4.5 km per hour and if you see that this player printed actually so
4:40:00
you can see that it has a 9 km per hour and and
4:40:06
um and yeah you can also see the averages right here the average player speed the average player um uh shot
4:40:14
speed and the actual player speed um you can do all sorts of fancy stuff like the
4:40:20
number of shots and you can analyze how fast a player is running when he's losing the pole and you can analyze how
4:40:27
fast um the ball like the how fast the ball is shot to make um a winning shot
4:40:34
um you can also do a lot of other stuff like check whether the ball is inside or outside the court when it's hits the
4:40:41
ground and the project can be very big I chose to make it simple right now uh but
4:40:48
yeah um you can we didn't also do anything with the net so you can also
4:40:55
add a little bit of net logic if something uh goes wrong or hits uh
4:41:01
before the net um so yeah you can you can build on this but currently you have
4:41:08
a very cool portfolio project right in your belt and hopefully it's going to
4:41:13
help you u landar a job in computer vision and
4:41:19
AI so that's it and uh have a wonderful day