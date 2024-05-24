import include.ZWO_camera as zwo    # The class that runs the camera
import include.gcode as gcode       # The class that runs the CNC controller
import include.led as led           # The class that runs the LED GPIO pins
import cv2 as cv
import numpy as np
#import time
import sys
from datetime import datetime as dt
import os

# This was mostly used when testing the camera code at the beginning 
# and is not currently used in the code.
def showPic(image, width, height):
    cv.namedWindow('Picture', cv.WINDOW_NORMAL)
    cv.resizeWindow('Picture', width, height)
    cv.imshow('Picture', image)
    cv.waitKey(0)
    cv.destroyAllWindows()

# This saves the image in the specified directory with the specified name.
def save_image(image, imdir, im_fold, im_coord):
    file_type = ".png"
    imname = "image" + im_coord
    file = imdir+im_fold+imname+file_type
    # Setting the file to have no compression
    cv.imwrite(file, image, [cv.IMWRITE_PNG_COMPRESSION,0])

# This is the main function that runs the entire scanner.
def run_scanner(settings):
    print("Initializing Machine...")
    # Retrieving the settings from the input
    painting_width = float(settings['width'])
    painting_height = float(settings['height'])
    bw_exposure = int(settings['exposure_bw_length'])
    exposure = []   # Array of the different color exposures
    exposure.append(int(settings['exposure_r_length']))
    exposure.append(int(settings['exposure_g_length']))
    exposure.append(int(settings['exposure_b_length']))
    gain = int(settings['gain'])
    led_amount = int(settings['led_amount'])
    com_port = settings['com_port']

    im_type = "RAW16"

    # The stitching tries to stitch images until it fails. 
    # Once it fails, the code no longer attempts to stitch images together to save time.
    stitching = True
    stitcher = cv.Stitcher.create()

    # Setting up the GPIO port if there are leds
    if led_amount != 0:
        leds = led.LED()
        leds.init_led(led_amount)
        leds_on = True
    else:
        leds_on = False

    # Initializing the matricies to undistort the images
    mtx = np.array([[1.72644371e+3, 0.00000000e+0, 6.69183685e+2],
                    [0.00000000e+0, 1.72521065e+3, 5.38624943e+2],
                    [0.00000000e+0, 0.00000000e+0, 1.00000000e+0]])
    dist = np.array([-3.05893821e-1, -2.83371174e-2, -1.84252378e-3, -3.02394827e-4, 4.18439617e-1])
    new_cam_mtx = np.array([[1.59453522e+3, 0.00000000e+0, 6.71522857e+2],
                            [0.00000000e+0, 1.59463203e+3, 5.40117580e+2],
                            [0.00000000e+0, 0.00000000e+0, 1.00000000e+0]])

    # Setting up the directories for the images to go
    imdir = "/home/user/Desktop/Scans/"
    now = dt.now()
    fold_date = now.strftime("%d_%m_%Y_%H,%M,%S")
    imdir = imdir+fold_date+"/"
    os.mkdir(imdir)
    raw = "Raw_Images/"
    und_raw = "Undistorted_Raw_Images/"
    color = "Color_Images/"
    stitch = "Stitched_Images/"
    os.mkdir(imdir+raw)
    os.mkdir(imdir+und_raw)
    os.mkdir(imdir+stitch)
    if led_amount != 0:
        os.mkdir(imdir+color)

    # Initializing the camera
    cam = zwo.Camera(gain, im_type)

    # Initializing the CNC machine
    cnc = gcode.CNC(com_port, painting_width, painting_height)
    cnc.init_cnc()
    cnc.close_cnc()

    # Perform the scan
    print("Finished Initialization. Beginning Scan.")
    # With LEDs
    if led_amount != 0:
        full_image = []
        for i in range(cnc.numYSteps):
            if i != 0:  # Doesn't move on the first loop
                cnc.init_cnc()
                cnc.new_line()
                cnc.close_cnc()
            image_row = []
            for j in range(cnc.numXSteps):
                if j != 0:  # Doesn't move on the first loop
                    cnc.init_cnc()
                    cnc.move_over()
                    cnc.close_cnc()
                bw_images = []
                for k in range(led_amount):
                    #turn on k led
                    leds.led_on(k)
                    cam.init_camera(exposure[k])
                    status, image = cam.take_picture()
                    cam.close_camera()
                    # Closes everything and exits the program if image fails
                    if not status:
                        print("Taking a picture failed. This could be because the exposure is too high.")
                        leds.led_off(k)
                        leds.close_led()
                        sys.exit(1)
                    leds.led_off(k)
                    save_image(image, imdir, raw, "("+str(j)+","+str(i)+")_"+str(k))
                    # Undistorting and cropping the image
                    undist = cv.undistort(image, mtx, dist, None, new_cam_mtx)
                    undist = undist[30:930, 30:1250]
                    save_image(undist, imdir, und_raw, "("+str(j)+","+str(i)+")_"+str(k))
                    bw_images.append(undist)
                # Creating the color image from the multiple b&w images
                if led_amount == 3:
                    # Images go in color image as BGR not RGB
                    color_img = np.dstack([bw_images[2], bw_images[1], bw_images[0]])
                    save_image(color_img, imdir, color, "("+str(j)+","+str(i)+")")
                    if stitching:
                        image_row.append(color_img)
                else:
                    # Create color image using 11 LEDs and save it
                    pass
            # Checks if the code is still trying to stitch images
            if stitching:
                # Attempts to stitch all the images in a row together
                status, stitched = stitcher.stitch(image_row)
                if status == 0:
                    # Saves the stitched row if the stitch succeeds
                    save_image(stitched, imdir, stitch, "_Row"+str(i))
                    full_image.append(stitched)
                else:
                    # Sets stitching to false if stitching fails
                    stitching = False
        # Checks if the code is still trying to stitch images
        if stitching:
            # Attempts to stitch all the rows together to make the whole image
            status, stitched = stitcher.stitch(full_image)
            if status == 0:
                # Saves the completed image if the stitch succeeds
                save_image(stitched, imdir, stitch, "_Full")
            else:
                # Sets stitching to false if stitching fails
                stitching = False

    # Without LEDs AKA black and white mode
    else:
        full_image = []
        for i in range(cnc.numYSteps):
            if i != 0:  # Doesn't move on the first loop
                cnc.init_cnc()
                cnc.new_line()
                cnc.close_cnc()
            image_row = []
            for j in range(cnc.numXSteps):
                if j != 0:  # Doesn't move on the first loop
                    cnc.init_cnc()
                    cnc.move_over()
                    cnc.close_cnc()
                cam.init_camera(bw_exposure)
                status, image = cam.take_picture()
                cam.close_camera()
                # Closes everything and exits the program if image fails
                if not status:
                    print("Taking a picture failed. This could be because the exposure is too high.")
                    sys.exit(1)
                save_image(image, imdir, raw, "("+str(j)+","+str(i)+")")
                undist = cv.undistort(image, mtx, dist, None, new_cam_mtx)
                undist = undist[30:930, 30:1250]
                save_image(undist, imdir, und_raw, "("+str(j)+","+str(i)+")")
            # Checks if the code is still trying to stitch images
            if stitching:
                # Attempts to stitch all the images in a row together
                status, stitched = stitcher.stitch(image_row)
                if status == 0:
                    # Saves the stitched row if the stitch succeeds
                    save_image(stitched, imdir, stitch, "_Row"+str(i))
                    full_image.append(stitched)
                else:
                    # Sets stitching to false if stitching fails
                    stitching = False
        # Checks if the code is still trying to stitch images
        if stitching:
            # Attempts to stitch all the rows together to make the whole image
            status, stitched = stitcher.stitch(full_image)
            if status == 0:
                # Saves the completed image if the stitch succeeds
                save_image(stitched, imdir, stitch, "_Full")
            else:
                # Sets stitching to false if stitching fails
                stitching = False

    # Sends the gantry back to its starting point
    cnc.init_cnc()
    cnc.zero()
    cnc.close_cnc()
        
    # Properly free up the resources that are used
    if leds_on:
        leds.close_led()
    #cam.close_camera()
    #cnc.close_cnc()
    print("Scan Finished")
