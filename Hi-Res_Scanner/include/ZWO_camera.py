import asi
import numpy as np
import time

class Camera:
    def __init__(self, gain, im_type):
        num = asi.ASIGetNumOfConnectedCameras()

        # This gets all of the necessary details about the camera used
        rtn, info = asi.ASIGetCameraProperty(0)
        self.camID = info.CameraID
        self.width = info.MaxWidth
        self.height = info.MaxHeight
        self.frame_size = self.width*self.height

        #self.exposure = exposure
        self.gain = gain
        self.imtype = im_type

        # Different procedures are required for images of type RAW16 which we will be mainly using
        if self.imtype == "RAW16":
            self.frame_size = self.frame_size*2
            self.im_type = asi.ASI_IMG_RAW16
        else:
            self.im_type = asi.ASI_IMG_RAW8

        # This is to make sure the camera is properly closed before opening it
        time.sleep(0.1)
        asi.ASICloseCamera(self.camID)
        time.sleep(0.1)



    # Sets up the camera to operate with the desired exposure, gain, and image type
    def init_camera(self, exposure):
        #self.exposure = exposure
        # Opens the camera and initializes the camera with all of the desired information
        asi.ASIOpenCamera(self.camID)
        time.sleep(0.1)
        asi.ASIInitCamera(self.camID)
        status = asi.ASISetROIFormat(self.camID, self.width, self.height, 1, self.im_type)
        while status != asi.ASI_SUCCESS:
            status = asi.ASISetROIFormat(self.camID, self.width, self.height, 1, self.im_type)
        asi.ASISetControlValue(self.camID, asi.ASI_BANDWIDTHOVERLOAD, 94, asi.ASI_FALSE)
        asi.ASISetControlValue(self.camID, asi.ASI_EXPOSURE, exposure, asi.ASI_FALSE)
        asi.ASISetControlValue(self.camID, asi.ASI_GAIN, self.gain, asi.ASI_FALSE)
        asi.ASISetCameraMode(self.camID, asi.ASI_MODE_NORMAL)
        
        # This checks to make sure that the camera actually set the image type correctly 
        # because there have been errors where they were different. This is most likely fixed though
        id, w, h, bin, im = asi.ASIGetROIFormat(self.camID)
        if im != self.im_type:
            print("Image type is not correct(desired,actual): "+str(self.imtype)+","+str(im))
        #else:
        #    print("Image type is correct: "+str(im))

    # This is our desired method of taking a picture and getting it ready for processing
    def take_picture(self):
        # Initializing a numpy array which will store the image
        image = np.zeros(self.frame_size, dtype=np.uint8)
        
        # Starts the exposure and waits until the camera is not busy
        asi.ASIStartExposure(self.camID, asi.ASI_FALSE)
        rtn, status = asi.ASIGetExpStatus(self.camID)
        while status == asi.ASI_EXP_WORKING:
            rtn, status = asi.ASIGetExpStatus(self.camID)
        asi.ASIStopExposure(self.camID)

        if status == asi.ASI_EXP_SUCCESS:
            # Retrieves the image from the camera
            rtn, image = asi.ASIGetDataAfterExp(self.camID, self.frame_size)

            # If the image is RAW16, the bits must be rearranged to be able to use it
            if self.im_type == asi.ASI_IMG_RAW16:
                image = self.convert_raw16(image)
        
            # Changing the 1-D array into a 2-D array with the proper width and height
            image = np.reshape(image, (self.height, self.width))
            return True, image
        else:
            # If the exposure failed, close the camera and try again
            asi.ASICloseCamera(self.camID)
        
        #image = np.reshape(image, (self.height, self.width))
        return False, image

    def close_camera(self):
        asi.ASICloseCamera(self.camID)

    def convert_raw16(self, image):
        # The 16 bit image is originally saved as an 8 bit array of double the size.
        # The bits are aranged so that every 2 bytes represent 1 16 bit pixel.
        # The bytes are aranged with the least significant byte(lsB) first followed by the most significant byte(msB).
        # The bytes must then be put into one 16 bit pixel with the msB shifted left 8 bits, then ORed with the lsB.
        temp1 = np.linspace(0, self.frame_size-2, num=int(self.frame_size/2), dtype=np.uint32)
        temp2 = np.linspace(1, self.frame_size-1, num=int(self.frame_size/2), dtype=np.uint32)
        lsB = image[temp1]
        msB = image[temp2]
        msB = msB * 256
        newimage = msB | lsB
        
        return newimage
        
