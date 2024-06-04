# High-Resolution Painting Scanner

## Summary

For my senior design engineering class, I created a high-resolution painting scanner prototype with two teammates. It is supposed to offer high spatial resolution and high color resolution. It uses a monochrome camera and takes pictures of the painting close enough to offer 600 ppi or more spatial resolution. It uses a monochrome camera to collect more frequency information than a standard color camera which only collects red, green, and blue light. The final design will use many more frequencies of light to allow artists to have fine control over how their painting's scan will look and be able to simulate being lit by different light sources. We picked out 11 different color LEDs that evenly cover the whole visible spectrum but we tested our prototype with only red, green, and blue LEDs. This is because, as we discovered several times during the project, it is trickier than we thought to get each frequency of light to illuminate the painting evenly and consistently. Most of the time spent in this project was trying to design a lighting system that was small enough to fit on the scanner, cheap enough to fall within our budget, and high-quality enough to create a very realistic scan of the painting. The camera is mounted to a modified CNC router and Gcode commands are used to move the camera from section to section to scan the entire painting. Our prototype can scan a 9 in by 9.5 in painting but the final design will be able to accommodate a 2 ft by 3 ft painting. 

## Technical Details

### Scanner Frame

The scanner frame is made from two modified Sainsmart Genmitsu 3018-PRO CNC Router Kits that my teammate was given for free by a friend. The head that held the motor was replaced by 3D-printed parts that hold the camera and the fiber optic cables from the lighting system. The original design criteria specified a frame that could scan a 2 ft by 3 ft painting. However, when my teammate created a bill of materials for the design that would meet this requirement, the cost of just the frame was more than half of our budget. This, along with complications with the lighting system reduced the painting size to what we could scan with the two router kits. The router kits we received use two lead screws to move the base plate and the router head. The lead screw that moves the router head is longer than the lead screw that moves the base plate so my teammate replaced the shorter lead screw of one router with the longer lead screw of the other. He also replaced the 80/20 stock with longer 80/20 stock to properly support the longer lead screw. The final frame design CAD drawing is shown below and the actual assembled frame is shown below the CAD drawing.

<p align="center">
    <img src="" title="CAD drawing of frame">
    <img src="" title="Picture of frame">
</p>

### Lighting System

The lighting system proved to be the most challenging aspect of this project. Our prototype uses two red, green, and blue LEDs inside reflective cones that funnel the light into fiber optic cables. The cables are made of 14 fibers that pipe the light to two clamps on either side of the camera and point at the canvas at 45-degree angles. This system is the best we were able to design and produced the only decent scans we could make. However, this system is flawed due to a time limit and a lack of experience with optics. Our first idea was to create different frequencies of light by filtering a white light source. We considered using optical filters, a prism, or a diffraction grating to filter out desired frequencies of light, but the filters were far too expensive and the prism and diffraction grating required a setup that was far too large and tedious. I then remembered that LEDs generally output relatively narrow bands of light and they are much cheaper than filters and are significantly smaller than any previous idea. We picked out 11 LEDs that output frequencies across the visible spectrum and we used a spectrometer to test 9 of them which can be seen in the image below.

<p align="center">
    <img src="" title="Spectrographs of 9 LEDs">
</p>

As is seen in the spectrographs above, one of the green LEDs has a much wider output spectrum than the rest of the LEDs. This LED falls in the "green gap" which is a gap in the visible spectrum where it is difficult to make narrow-band LEDs. We ordered small filters to cover only this LED so it outputs about 570 nm in a much narrower band. To make testing easier, we only used red, green, and blue LEDs with output frequencies most similar to the outputs of the LEDs that make up LED screens. The spectrographs of just these three are seen below.

<p align="center">
    <img src="" title="Spectrographs of RGB LEDs">
</p>

Acquiring and testing the LEDs solved what we would use as a light source but did not solve how we would use them to evenly illuminate the painting. If the LEDs were side by side directly shining on the painting, the recreated color photo looked like a rainbow. We settled on using fiber optic cables to get the light to originate from the same place so each frequency would illuminate the painting in the same way. We decided to use a reflective cone made from reflective vinyl to hopefully funnel as much light as possible into the cables. This was only somewhat successful since a lot of light bled through the cones and came out the back of the cones. However, since the scan was to be done in a dark room, the lights being dim was solved by increasing the exposure time. When we performed a color scan, we were surprised to find that even though the light was originating from the same place the different colors still illuminated the painting differently. An example of a ribbon of wires we scanned is shown below.

<p align="center">
    <img src="" title="Scan of wires">
</p>

We suspect that this is due to refraction since the light was coming directly out of the ends of the fiber optic cables. We talked to a physics professor and he confirmed that this was most likely the case. We asked him how to improve the light going in and coming out of the cables and he said that both ends would probably require a series of lenses and mirrors to properly pipe the light through. Since we did not have the time to implement this, it is being left to the next senior design group that takes this project on.

### Firmware

I was the Software and Control System Lead on this project and I wrote the code for this project. The scanner uses a Raspberry Pi to run the scanner and process the images. The scan starts with a file called Scan.py which is a graphical user interface (GUI) I made that asks for custom parameters like the painting dimensions and the desired exposure times. When a button labeled "Start Scan" is pressed, it runs the code found in the include folder called use_cam.py. This uses three other custom header files I wrote to control the camera, CNC controller, and LEDs. After the code initializes everything, it enters a triple nested for loop that will scan the entire painting. First, it takes three pictures of the first position while illuminating the red, green, and blue LEDs for each respective picture. Then, the lens distortion is removed from each image and the three images are combined into one color image using a 3D numpy array. It then repeats these steps for each section the painting in a grid and saves every picture it takes as a raw, undistorted, and color image. It attempts to stitch the images in each row using OpenCV's image stitcher unless one of them fails. We have never been able to stitch any images during a scan which we believe to be because there is not enough detail at the scale we are scanning at, the lighting system does not illuminate the canvas well enough, or both. A completed 2 X 2 scan of a white paper with a ribbon of colorful wires on it is contained in Images/Complete_Scan.
