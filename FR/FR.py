# -*- coding: utf-8 -*-

### Imports ###################################################################
import sys
sys.path.append("..")

from picamera.array import PiRGBArray
from picamera import PiCamera
from functools import partial

import multiprocessing as mp
import cv2
import os
import time

import MQTT.send as m_send
import MAIL.sendmail_with_image as sendMail

### Setup #####################################################################

resX = 320
resY = 240

# Setup the camera
camera = PiCamera()
time.sleep(2)
camera.resolution = ( resX, resY )
camera.framerate = 60

# Use this as our output
rawCapture = PiRGBArray( camera, size=( resX, resY ) )

# The face cascade file to be used
face_cascade = cv2.CascadeClassifier('/home/pi/opencv-3.3.0/data/lbpcascades/lbpcascade_frontalface.xml')

t_start = time.time()
fps = 0


### Helper Functions ##########################################################

def get_faces( img ):

    gray = cv2.cvtColor( img, cv2.COLOR_BGR2GRAY )
    faces = face_cascade.detectMultiScale( gray )

    if len(faces) > 0:
        # send MQTT info
        m_send.send("1")

        # save photo
        localtime = time.localtime(time.time())
        path_time = str(localtime.tm_year) + '-' + str(localtime.tm_mon) + '-' + str(localtime.tm_mday) + '-' + str(localtime.tm_hour) + '-' + str(localtime.tm_min) + '-' + str(localtime.tm_sec)
        IMAGE_PATH = '../IMAGE/' + path_time + '.jpg'
        cv2.imwrite(IMAGE_PATH, img)

        # pause 2s
        time.sleep(2)

        # send mail
        sendMail.sendMail(path_time + '.jpg')

        # pause 3s
        time.sleep(3)

    return faces, img

def draw_frame( img, faces ):

    global fps
    global time_t

    # Draw a rectangle around every face
    for ( x, y, w, h ) in faces:

        cv2.rectangle( img, ( x, y ),( x + w, y + h ), ( 200, 255, 0 ), 2 )
        cv2.putText(img, "Face No." + str( len( faces ) ), ( x, y ), cv2.FONT_HERSHEY_SIMPLEX, 0.5, ( 0, 0, 255 ), 2 )

    # Calculate and show the FPS
    fps = fps + 1
    sfps = fps / (time.time() - t_start)
    cv2.putText(img, "FPS : " + str( int( sfps ) ), ( 10, 10 ), cv2.FONT_HERSHEY_SIMPLEX, 0.5, ( 0, 0, 255 ), 2 )

    cv2.imshow( "Frame", img )
    cv2.waitKey( 1 )


### Main ######################################################################

if __name__ == '__main__':

    pool = mp.Pool( processes=4 )
    fcount = 0

    camera.capture( rawCapture, format="bgr" )

    r1 = pool.apply_async( get_faces, [ rawCapture.array ] )
    r2 = pool.apply_async( get_faces, [ rawCapture.array ] )
    r3 = pool.apply_async( get_faces, [ rawCapture.array ] )
    r4 = pool.apply_async( get_faces, [ rawCapture.array ] )

    f1, i1 = r1.get()
    f2, i2 = r2.get()
    f3, i3 = r3.get()
    f4, i4 = r4.get()

    rawCapture.truncate( 0 )

    for frame in camera.capture_continuous( rawCapture, format="bgr", use_video_port=True ):
        image = frame.array

        if   fcount == 1:
            r1 = pool.apply_async( get_faces, [ image ] )
            f2, i2 = r2.get()
            draw_frame( i2, f2 )

        elif fcount == 2:
            r2 = pool.apply_async( get_faces, [ image ] )
            f3, i3 = r3.get()
            draw_frame( i3, f3 )

        elif fcount == 3:
            r3 = pool.apply_async( get_faces, [ image ] )
            f4, i4 = r4.get()
            draw_frame( i4, f4 )

        elif fcount == 4:
            r4 = pool.apply_async( get_faces, [ image ] )
            f1, i1 = r1.get()
            draw_frame( i1, f1 )

            fcount = 0

        fcount += 1

        rawCapture.truncate( 0 )