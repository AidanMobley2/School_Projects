# AQIQ Project

## Summary

I worked with the Air Quality InQuiry (AQIQ) research group at University of Colorado Boulder during the summer of 2023 through the CU Boulder SPUR program. AQIQ is a group of engineering researchers and students who work on creating and using a versatile air quality measurement pod. The pod is used by the researchers to help them conduct their graduate research. The engineering students design, assemble, and troubleshoot the old and new versions of the pods. The following picture is an open pod.

![Open Pod](pod.jpg)

Another aspect of the AQIQ group is a public outreach program where some students and researchers travel to a rural school and teach them about air quality, the work AQIQ does, and why it is important. They then split the students into groups, lead the students to conduct experiments of their own related to air quality, take notes, and discuss their findings. The students would then present their findings to the rest of the students, sometimes with a little help from the AQIQ student who led their group.
 
## Technical Description

The AQIQ program is over 20 years old and they have had countless past designs. The most recent finalized design when I worked there was the Y-Pod. The version I worked on during my time there was the Rev-4 version of the X-Pod. Each X-Pod is a durable box which contained one large PCB, an Arduino Mega, fans, and air vents. The PCB held all of the air quality sensors which measured CO, CO2, ozone, particulate matter, NxO, VOCs, methane, wind speed, wind direction, and others. The pods are designed to be customizable since each researcher needs to make different measurements. The board is powered by 12 V which is brought down to the 5 V required by most sensors and the Arduino Mega. There is an optional air pump attachment that runs off of 12 V which is why the board takes in 12 V instead of 5 V. The sensors which use 3.3 V are powered by the Arduino's 3.3 V supply. The board also holds a GPS sensor to make it easier to organize which pod is which for each researcher in the field. A micro SD card is used to store the data the Arduino collects. There are options for WIFI and cellular to connect the pods to the internet and store the data on Blynk, but that was a work in progress while I worked there and never fully worked. The code attached in my repository is the latest version that I worked on. The link to the active GitHub repository is [here](https://github.com/coffeye/xpod).

## My Contributions

### Populating the PCBs
 
I worked both with the engineering students to build and troubleshoot the Rev-4 version of the pods, and the outreach program. At the beginning of the summer, my main job was to populate some of the boards with various sensors and headers for the sensors. At first, with the help of two other students, I helped populate 10 PCBs for testing. Once testing was done, we needed to populate many more boards for the researchers to use. By the end of my time there, I had helped to populate or completely populated 80 PCBs which provided me with valuble soldering experience. 
 
### Breaking CO2 Sensors

When we started testing, we noticed something was wrong very quickly since several hours after uploading the code and letting it run, the Arduino would freeze and all activity would stop. This was a big problem because, in the field, they would have to run constantly for weeks or months at a time. After weeks of troubleshooting, the problem was narrowed down to the CO2 sensors. The shiny golden sensor in the following picture is the CO2 sensor.
 
![Board with CO2 sensor](board_with_CO2.jpg)
 
After looking at the PCB layout and schematic, I realized that one of the power pins on the CO2 sensor did not have filter capacitors to keep the power as constant as possible. I tried soldering a capacitor between the power pin and the closest ground pin. After soldering the capacitor, the time between starting the code and the Arduino freezing was substantially increased and, on some boards, the Arduino never froze during our testing. Below shows a picture of the capacitor fix.
 
![CO2 Fix](CO2_fix.jpg)
 
However, since the problem was not completely fixed on all boards, a temporary software fix was necessary to allow the pods to collect data even after the Arduino freezes. I remembered that microcontrollers usually have a watchdog timer on completely separate hardware than the main processor which could help. I implemented the watchdog into the code on the longest timer possible. This cause the main processor to reset after it would freeze, allowing the pod to continue taking measurements for the duration of any tests it was a part of. 

### Misconnected Power Supply

Since some of the researchers needed air pumps instead of fans, the power supply for the pumps needed to be tested. The volume of air over time needed to be controlled for the pump and this was done by using a PWM-controlled motor driver IC. When no load was connected, it would output the expected voltage. However, when I tested it with a pump, the voltage would drop to about 1 V. After looking at the schematic I realized that one of the resistors were the wrong value and I soldered on the correct value. This helped a little but still did not fix it. After looking over it with the engineer who designed the PCB, we realized that the schematic was wrong and another change needed to be made. We had to scratch out one of the traces and rewire it to the other side of a capacitor. In the following picture, the small black wire in the center is the rewired circuit and the resistor that is circled is the incorrect resistor.

![Power supply fix](power_supply_fix.jpg)

After applying these fixes, the air pump power supply worked as desired.

### Misconnected Met Station

A met station is a measurement tool that collects wind speed and wind direction data. It measures wind speed using magnets and reed switches to count how many times a propeller rotates in a set amount of time. This is implemented using a hardware interrupt in Arduino. However, I realized that it was attached to a pin that was not capable of performing hardware interrupts. I cut the trace to where it was incorrectly wired and rewired it to an avaliable pin that could do hardware interrupts. This completely fixed the problem and allowed met station data to be properly recorded and stored. Below is a picture of the met station fix.

![Met station fix](MET_fix.jpg)

### Implemeted a New Sensor

Towards the end of the summer, one of the researchers wanted to use a new sensor and I volunteered to implement it. It is a particulate matter sensor called an OPC-R2 made by Alphasense that communicates via SPI. There was sparse documentation on it and I could only find one person who had written code for it. However, the code was much more detailed than necessary and always output much more information than needed. I found another person who wrote code for a slightly different sensor made by the same company as the sensor I was using that was much simpler and easier to use. I decided to merge the two codes together to make a simple yet versitile "library" for the sensor which is organized the same way as the rest of the sensors in the project. This code that I wrote is in the OPC.h and OPC.cpp in the xpod_node folder. The peoples' code that I used are [Joseph Habeck](https://github.com/JHabeck/Alphasense-OPC-N2/tree/master) who wrote the simple code for a different sensor, and [Marcel Olivera](https://github.com/shyney7/OPC-R2_ESP32/tree/main) who wrote the complicated code for the correct sensor.

### Rural Schools Outreach

Another way the pods are used is in a rural school outreach program. Since the X-Pods were not completely done, we used Y-Pods to perform air quality tests. I attended four of the outreach programs during my time there. During these, we started out by giving the students a presentation where I helped explain what air pollutants are, how they work, and how they affect people and the planet. I also helped explain what can be done to help with air pollution, what the researchers do, and why their research matters. After the presentation, we would split the students into about as many groups as there were of us. The students would brainstorm what they would want to measure and how they would measure it. We would lead our groups to the places they thought would be interesting to measure and help them use the pods to measure the air. Once the group had collected all of their data, we would bring them back to the initial meeting place and help them look at the data and interpret it. Once all groups had finished interpreting the data, they would present their findings to the rest of the students, often times with some help from us. These were very fun and working with the children was a blast. I really enjoyed teaching them about something that I found interesting.