import cv2
import numpy as np
import winsound
import os
import time
#%%
cropping = False
refpt = []
fbf = 0
tf = 0
#%%
# Cropping out Region of Area wanted
def cc(event, x, y, flags, param):
     global refpt, cropping
     
     if event == cv2.EVENT_LBUTTONDOWN:
          refpt = [(x, y)]
          cropping = True
     elif event == cv2.EVENT_LBUTTONUP:
          refpt.append((x,y))
          cropping = False
          
     return refpt

#%%
#Cosine Rule
def cra(a,b,c):
     # Radian to degree 
     angle = np.arccos((b**2+c**2-a**2)/(2*b*c)) * (180/np.pi)
     return angle
#%%
#Applying background substractor and masking it.
def mask(x, fgbg):
     # Appling Background substractor, dilating the mask and bluring.
     fgmask = fgbg.apply(x)
     fgmask = cv2.dilate(fgmask,kernel,iterations = 3)
     fgmask = cv2.GaussianBlur(fgmask,(5,5),100) 
   
     # Appling the mask on ROI
     res = cv2.bitwise_and(x, x, mask=fgmask)
     return res, fgmask
#%%
def hull_defects(cnt, res):
    l = 0
    # Finding Convexhull and defects
    hull = cv2.convexHull(cnt,returnPoints = False)
    defects = cv2.convexityDefects(cnt,hull)
    
    area = cv2.contourArea(cnt)
    for i in range(defects.shape[0]):
         
         # s = start, e = end, f= far, d=approximate distance to farthest point
      
         s,e,f,d = defects[i,0]
         start = tuple(cnt[s][0])
         end = tuple(cnt[e][0])
         far = tuple(cnt[f][0])
         
         #Looking for distance between s,e and f
         a = np.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
         b = np.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
         c = np.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)
    
         # Using cosine law to find angle to eliminate unwanted defects
         angle = np.arccos((b**2+c**2-a**2)/(2*b*c)) * (180/np.pi)
         # Range of wanted defects angle.
         if angle <= 95 and angle > 30:
              
              # Counting defects
              l += 1
              cv2.circle(res, far, 3, [255,0,0], -1)
         cv2.line(res,start, end, [0,255,0], 2)
    return l, area
#%%

# Capturing default web cam
cap = cv2.VideoCapture(0)
        
# Will be used to dilate the mask
kernel = np.ones((3,3),np.uint8)

# Using BackgroundSubtractor to mask region of interested area
fgbg = cv2.bgsegm.createBackgroundSubtractorMOG(history=100, nmixtures=6, backgroundRatio=0.007)
fgbg2 = cv2.bgsegm.createBackgroundSubtractorMOG(history=100, nmixtures=6, backgroundRatio=0.007)

while(True):
     # Using try since easy to close if there is an error.
     try:
          timestr = time.strftime("%Y%m%d-%H%M%S")
          #time = "xd"
          key = cv2.waitKey(1) & 0xFF
          # Reading default webcam
          ret, frame = cap.read()
          
          # Number of convexdefects will be explained later.
          l = 0
          tf = 0
          
          # Showing default webcam
          cv2.namedWindow("frame")
          cv2.moveWindow("frame", 700,300)
          cv2.imshow("frame", frame)
          cv2.setMouseCallback("frame", cc)
          
          font = cv2.FONT_HERSHEY_COMPLEX_SMALL
          
          # If region of interested is selected
          if len(refpt) == 2:
               fbf+= 1
               print(fbf)
               
               # Region of interest cropped               
               x_half = refpt[0][0]+((refpt[1][0]-refpt[0][0])//2)
               
               #player1
               roi = frame[refpt[0][1]:refpt[1][1], refpt[0][0]:x_half]
               
               #player2
               roi2 = frame[refpt[0][1]:refpt[1][1], x_half:refpt[1][0]]
               
               # Draw a diagonal blue line with thickness of 5 px
               cv2.line(frame,(x_half,refpt[0][1]),(x_half,refpt[1][1]),(255,0,0),5)
               cv2.line(frame,(refpt[0][0],refpt[0][1]),(refpt[0][0],refpt[1][1]),(255,0,0),3)
               cv2.line(frame,(refpt[1][0],refpt[0][1]),(refpt[1][0],refpt[1][1]),(255,0,0),3)
               
               
               cv2.namedWindow("roi")
               cv2.moveWindow("roi", 200,100)
               cv2.imshow("roi", roi)
               
               cv2.namedWindow("roi2")
               cv2.moveWindow("roi2", 1400,100)
               cv2.imshow("roi2", roi2)
               
               res, fgmask = mask(roi, fgbg)
               res2, fgmask2 = mask(roi2, fgbg2)
                                           
               _,contours,hierarchy= cv2.findContours(fgmask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
               _2,contours2,hierarchy2= cv2.findContours(fgmask2,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

               if fbf <= 50:
                   p1 = None
                   p2 = None
                   cv2.putText(frame,'Countdowns!',(150,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
               elif fbf <= 70:        
                   cv2.putText(frame,'1',(200,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
               elif fbf <= 80:              
                   cv2.putText(frame,'2',(200,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
               elif fbf <= 90:
                   cv2.putText(frame,'3',(200,50), font, 2, (0,0,255), 3, cv2.LINE_AA)                   
               elif fbf > 91:
                   # In the beginning contours will have zero value which causes error.
                   if len(contours) >= 1:
                        cnt = max(contours, key = lambda x: cv2.contourArea(x))
                        l, area = hull_defects(cnt, res)
                        #cv2.imshow("res", res)
                        font = cv2.FONT_HERSHEY_COMPLEX_SMALL  
                        # For player 1                                                          
                        if l==0:
                             if area < 10000:
                                 cv2.putText(frame,'Rock',(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
                                 if fbf == 105:
                                     p1 = "Rock"
                                     winsound.PlaySound("Sounds/rock.wav",winsound.SND_FILENAME)
                             else:
                                  cv2.putText(frame,'Paper',(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
                                  if fbf == 105:
                                     p1 = "Paper"
                                     winsound.PlaySound("Sounds/paper.wav",winsound.SND_FILENAME)                            
                             
                        elif l<=2:
                             if area < 10000:
                                 cv2.putText(frame,'Scissors',(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
                                 if fbf == 105:
                                     p1 = "Scissors"
                                     winsound.PlaySound("Sounds/Scissors.wav",winsound.SND_FILENAME)
                             else:
                                 cv2.putText(frame,'Paper',(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
                                 if fbf == 105:
                                     p1 = "Paper"
                                     winsound.PlaySound("Sounds/paper.wav",winsound.SND_FILENAME)
                        elif l>2:
                             cv2.putText(frame,'Paper',(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
                             if fbf == 105:
                                 p1 = "Paper"
                                 winsound.PlaySound("Sounds/paper.wav",winsound.SND_FILENAME)

                        
                   # For player2
                   if len(contours2) >= 1:
                        cnt2 = max(contours2, key = lambda x: cv2.contourArea(x))
                        l2, area2 = hull_defects(cnt2, res2)
                        #cv2.imshow("res2", res2)                                                                                                                  
                        if l2==0:
                             
                             if area2 < 10000:
                                 cv2.putText(frame,'Rock',(400,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
                                 if fbf == 105:
                                     p2 = "Rock"
                                     winsound.PlaySound("Sounds/rock.wav",winsound.SND_FILENAME)
                             else:
                                  cv2.putText(frame,'Paper',(400,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
                                  if fbf == 105:
                                      p2 = "Paper"
                                      winsound.PlaySound("Sounds/paper.wav",winsound.SND_FILENAME)                             
                             
                        elif l2<=2:
                             if area2 < 10000:
                                 cv2.putText(frame,'Scissors',(400,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
                                 if fbf == 105:
                                     p2 = "Scissors"
                                     winsound.PlaySound("Sounds/Scissors.wav",winsound.SND_FILENAME)
                             else:
                                 cv2.putText(frame,'Paper',(400,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
                                 if fbf == 105:
                                     p2 = "Papper" 
                                     winsound.PlaySound("Sounds/paper.wav",winsound.SND_FILENAME)
                        elif l2>2:
                             cv2.putText(frame,'Paper',(400,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
                             if fbf == 105:
                                 p2 = "Paper"
                                 winsound.PlaySound("Sounds/paper.wav",winsound.SND_FILENAME)
                    
                   if fbf == 105:
                        cv2.imwrite(os.path.join("last_frame","Winner "+timestr+".jpg"), frame)
                        if p1 == p2:
                            winsound.PlaySound("Sounds/draw.wav",winsound.SND_FILENAME)
                        elif p1 == "Rock":
                            if p2 == "Paper":
                                winsound.PlaySound("Sounds/p2win.wav",winsound.SND_FILENAME)
                            else:
                                winsound.PlaySound("Sounds/p1win.wav",winsound.SND_FILENAME)
                        elif p1 == "Paper":
                            if p2 == "Scissors":
                                winsound.PlaySound("Sounds/p2win.wav",winsound.SND_FILENAME)
                            else:
                                winsound.PlaySound("Sounds/p1win.wav",winsound.SND_FILENAME)
                        elif p1 == "Scissors":
                            if p2 == "Rock":
                                winsound.PlaySound("Sounds/p2win.wav",winsound.SND_FILENAME)
                            else:
                                winsound.PlaySound("Sounds/p1win.wav",winsound.SND_FILENAME)
                        else:
                            print("Didn't play fast enough")
               
          cv2.imshow("frame", frame)
          if key == ord("r"):
             fbf = 0              
     except:
          pass
     
     if key == ord("q"):
          break


cap.release()
cv2.destroyAllWindows()

     