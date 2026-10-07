from flask import Flask
from flask import Flask, render_template, Response, redirect, request, session, abort, url_for
from camera import VideoCamera
from camera2 import VideoCamera2
from datetime import datetime
from datetime import date
import os
import base64
import datetime
import random
from random import seed
from random import randint
import cv2
from mtcnn import MTCNN
import numpy as np
import threading

import time
import shutil
import imagehash
import hashlib
import PIL.Image
from PIL import Image
from PIL import ImageTk
import urllib.request
import urllib.parse
from urllib.request import urlopen
import webbrowser
import mysql.connector

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization

from Crypto import Random
from Crypto.Cipher import AES

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="",
  charset="utf8",
  database="atm_face_multi"
)
app = Flask(__name__)
##session key
app.secret_key = 'abcdef'

class AESCipher(object):

    def __init__(self, key):
        self.bs = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode()))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]


@app.route('/',methods=['POST','GET'])
def index():
    cnt=0
    act=""
    msg=""
    ff=open("det.txt","w")
    ff.write("1")
    ff.close()

    ff1=open("photo.txt","w")
    ff1.write("1")
    ff1.close()

    ff11=open("img.txt","w")
    ff11.write("1")
    ff11.close()

    if request.method == 'POST':
        username1 = request.form['uname']
        password1 = request.form['pass']
        mycursor = mydb.cursor()
        mycursor.execute("SELECT count(*) FROM admin where username=%s && password=%s",(username1,password1))
        myresult = mycursor.fetchone()[0]
        if myresult>0:
            result=" Your Logged in sucessfully**"
            return redirect(url_for('admin')) 
        else:
            result="Incorrect USername or Password!!!"
        

    return render_template('index.html',msg=msg,act=act)



@app.route('/login_admin', methods=['POST','GET'])
def login_admin():
    result=""
    ff1=open("photo.txt","w")
    ff1.write("1")
    ff1.close()
    if request.method == 'POST':
        username1 = request.form['uname']
        password1 = request.form['pass']
        mycursor = mydb.cursor()
        mycursor.execute("SELECT count(*) FROM admin where username=%s && password=%s",(username1,password1))
        myresult = mycursor.fetchone()[0]
        if myresult>0:
            result=" Your Logged in sucessfully**"
            return redirect(url_for('admin')) 
        else:
            result="Incorrect USername or Password!!!"
                
    
    return render_template('login_admin.html',result=result)

@app.route('/admin',methods=['POST','GET'])
def admin():
    msg=""
    st=""
    act=request.args.get("act")
    data=[]
    mycursor = mydb.cursor()

    mycursor.execute("SELECT count(*) FROM register")
    cnt = mycursor.fetchone()[0]
    if cnt>0:
        st="1"
        mycursor.execute("SELECT * FROM register")
        data = mycursor.fetchall()

    if act=="del":
        did=request.args.get("did")

        mycursor.execute("SELECT * FROM register where id=%s",(did,))
        d1 = mycursor.fetchone()

        mycursor.execute("delete from vt_face where vid=%s",(did,))
        mydb.commit()

        mycursor.execute("delete from user_account where rid=%s",(did,))
        mydb.commit()

        mycursor.execute("delete from event where user_id=%s",(did,))
        mydb.commit()

        mycursor.execute("delete from register where id=%s",(did,))
        mydb.commit()
        return redirect(url_for('admin')) 
        

    return render_template('admin.html',msg=msg,act=act,st=st,data=data)
    
@app.route('/add_cus',methods=['POST','GET'])
def add_cus():
    msg=""
    email=""
    mess=""
    vid=""
    ff1=open("photo.txt","w")
    ff1.write("2")
    ff1.close()

    mycursor = mydb.cursor()
    if request.method=='POST':
        name=request.form['name']
        mobile=request.form['mobile']
        email=request.form['email']
        address=request.form['address']
        #branch=request.form['branch']
        aadhar=request.form['aadhar']

        now = datetime.datetime.now()
        rdate=now.strftime("%d-%m-%Y")
        
        
        mycursor.execute("SELECT count(*) FROM register where aadhar1=%s",(aadhar, ))
        cnt = mycursor.fetchone()[0]
        if cnt==0:
            mycursor.execute("SELECT max(id)+1 FROM register")
            maxid = mycursor.fetchone()[0]
            if maxid is None:
                maxid=1

            str1=str(maxid)
            ac=str1.rjust(4, "0")
            account="2600"+ac

            xn=randint(1000, 9999)
            rv1=str(xn)
            xn2=randint(1000, 9999)
            rv2=str(xn2)
            card=rv1+account+rv2
       
            
            sql = "INSERT INTO register(id, name, mobile, email, address,  bank, accno, branch, card, deposit,password, rdate, aadhar1) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (maxid, name, mobile, email, address, '', '', '', card, '0','', rdate, aadhar)
            vid=str(maxid)
            mycursor.execute(sql, val)
            mydb.commit()
            mess="Dear "+name+", Your Card No."+card
            #url="http://iotcloud.co.in/testmail/sendmail.php?email="+email+"&message="+message
            #webbrowser.open_new(url)
            msg="success"
            #return redirect(url_for('add_photo',vid=maxid)) 
        else:
            msg="Already Exist!"

    mycursor.execute("SELECT amount FROM admin WHERE username='admin'")
    value = mycursor.fetchone()[0]
    
    return render_template('add_cus.html',msg=msg,value=value,email=email,mess=mess,vid=vid)

@app.route('/add_bank',methods=['POST','GET'])
def add_bank():
    msg=""
    vid=request.args.get("vid")
    now = datetime.datetime.now()
    rdate=now.strftime("%d-%m-%Y")
    rtime=now.strftime("%H-%M-%S")
    rdd=rdate+" "+rtime

    mycursor = mydb.cursor()
    if request.method=='POST':
        bank=request.form['bank']
        account=request.form['account']
        ifsc_code=request.form['ifsc_code']
        branch=request.form['branch']

        '''ky="a"+str(vid)
        obj=AESCipher(ky)
        bank1=obj.encrypt(bank)
        account1=obj.encrypt(account)
        ifsc_code1=obj.encrypt(ifsc_code)
        branch1=obj.encrypt(branch)'''

        

        mycursor.execute("SELECT count(*) FROM user_account where account=%s",(account, ))
        cnt = mycursor.fetchone()[0]
        if cnt==0:
            mycursor.execute("SELECT max(id)+1 FROM user_account")
            maxid = mycursor.fetchone()[0]
            if maxid is None:
                maxid=1

            sql = "INSERT INTO user_account(id,rid,bank,account,ifsc_code,branch,deposit) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            val = (maxid,vid,bank,account,ifsc_code,branch,'10000')
            
            mycursor.execute(sql, val)
            mydb.commit()

            mycursor.execute("SELECT max(id)+1 FROM event")
            maxid2 = mycursor.fetchone()[0]
            if maxid2 is None:
                maxid2=1

            sql = "INSERT INTO event(id,name,accno,amount,rdate,user_id) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (maxid2,"Deposit",account,'10000',rdd,maxid)
            
            mycursor.execute(sql, val)
            mydb.commit()
        
            msg="success"
        else:
            msg="fail"

    return render_template('add_bank.html',msg=msg,vid=vid)


@app.route('/add_depo',methods=['POST','GET'])
def add_depo():
    msg=""
    vid=request.args.get("vid")
    bid=request.args.get("bid")

    now = datetime.datetime.now()
    rdate=now.strftime("%d-%m-%Y")
    rtime=now.strftime("%H-%M-%S")
    rdd=rdate+" "+rtime
        
    mycursor = mydb.cursor()
    if request.method=='POST':
        amount=request.form['amount']
        amt=int(amount)

        mycursor.execute("SELECT * FROM user_account where id=%s",(bid,))
        d1 = mycursor.fetchone()
        account=d1[3]

        mycursor.execute("SELECT max(id)+1 FROM event")
        maxid = mycursor.fetchone()[0]
        if maxid is None:
            maxid=1

        sql = "INSERT INTO event(id,name,accno,amount,rdate,user_id) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (maxid,"Deposit",account,amount,rdd,vid)
        
        mycursor.execute(sql, val)
        mydb.commit()
        
        mycursor.execute("update user_account set deposit=deposit+%s where id=%s",(amt,bid))
        mydb.commit()
        msg="success"


    return render_template('add_depo.html',msg=msg,vid=vid)

@app.route('/view_trans',methods=['POST','GET'])
def view_trans():
    msg=""
    st=""
    data=[]
    vid=request.args.get("vid")
    bid=request.args.get("bid")
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM user_account where id=%s",(bid,))
    d1 = mycursor.fetchone()
    account=d1[3]

    mycursor.execute("SELECT count(*) FROM event where accno=%s",(account,))
    cnt = mycursor.fetchone()[0]
    if cnt>0:
        st="1"
        mycursor.execute("SELECT * FROM event where accno=%s",(account,))
        data = mycursor.fetchall()

    return render_template('view_trans.html',msg=msg,vid=vid,data=data,st=st)

def getImagesAndLabels(path):

    
    detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml");

    imagePaths = [os.path.join(path,f) for f in os.listdir(path)]     
    faceSamples=[]
    ids = []

    for imagePath in imagePaths:

        PIL_img = Image.open(imagePath).convert('L') # convert it to grayscale
        img_numpy = np.array(PIL_img,'uint8')

        id = int(os.path.split(imagePath)[-1].split(".")[1])
        faces = detector.detectMultiScale(img_numpy)

        for (x,y,w,h) in faces:
            faceSamples.append(img_numpy[y:y+h,x:x+w])
            ids.append(id)

    return faceSamples,ids


@app.route('/add_photo',methods=['POST','GET'])
def add_photo():
    vid=""
    ff1=open("photo.txt","w")
    ff1.write("2")
    ff1.close()

    cursor = mydb.cursor()
    
    
    vid = request.args.get('vid')
    
    cursor.execute("SELECT * FROM register where id=%s",(vid,))
    value = cursor.fetchone()
    name=value[1]
    
    ff=open("user.txt","w")
    ff.write(name)
    ff.close()

    ff=open("user1.txt","w")
    ff.write(vid)
    ff.close()
    
    if request.method=='POST':
        vid=request.form['vid']
        fimg="v"+vid+".jpg"
        

        cursor.execute('delete from vt_face WHERE vid = %s', (vid, ))
        mydb.commit()

        ff=open("det.txt","r")
        v=ff.read()
        ff.close()
        vv=int(v)
        v1=vv-1
        vface1="User."+vid+"."+str(v1)+".jpg"
        i=2
        while i<vv:
            
            cursor.execute("SELECT max(id)+1 FROM vt_face")
            maxid = cursor.fetchone()[0]
            if maxid is None:
                maxid=1
            vface="User."+vid+"."+str(i)+".jpg"
            sql = "INSERT INTO vt_face(id, vid, vface) VALUES (%s, %s, %s)"
            val = (maxid, vid, vface)
            print(val)
            cursor.execute(sql,val)
            mydb.commit()
            i+=1

        
            
        cursor.execute('update register set fimg=%s WHERE id = %s', (vface1, vid))
        mydb.commit()
        shutil.copy('faces/f1.jpg', 'static/photo/'+vface1)
        ##########
        
        ##Training face
        # Path for face image database
        path = 'dataset/user'+vid

        recognizer = cv2.face.LBPHFaceRecognizer_create()

        # function to get the images and label data
        

        print ("\n [INFO] Training faces. It will take a few seconds. Wait ...")
        faces,ids = getImagesAndLabels(path)
        recognizer.train(faces, np.array(ids))

        # Save the model into trainer/trainer.yml
        recognizer.write('trainer/trainer.yml') # recognizer.save() worked on Mac, but not on Pi

        # Print the numer of faces trained and end program
        print("\n [INFO] {0} faces trained. Exiting Program".format(len(np.unique(ids))))






        #################################################
        return redirect(url_for('view_photo',vid=vid,act='success'))
        
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM register")
    data = cursor.fetchall()
    return render_template('add_photo.html',data=data, vid=vid)

@app.route('/view_full',methods=['POST','GET'])
def view_full():
    data=[]
    data2=[]
    st=""
    act=request.args.get("act")
    vid=request.args.get("vid")

    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM register where id=%s",(vid,))
    data = mycursor.fetchone()


    mycursor.execute("SELECT count(*) FROM user_account where rid=%s",(vid,))
    cnt = mycursor.fetchone()[0]
    if cnt>0:
        st="1"
        mycursor.execute("SELECT * FROM user_account where rid=%s",(vid,))
        data2 = mycursor.fetchall()

    if act=="del":
        did=request.args.get("did")

        mycursor.execute("SELECT * FROM user_account where id=%s",(did,))
        d1 = mycursor.fetchone()
        acc=d1[3]

        mycursor.execute("delete from event where accno=%s",(acc,))
        mydb.commit()
        
        mycursor.execute("delete from user_account where id=%s",(did,))
        mydb.commit()
        return redirect(url_for('view_full',vid=vid)) 
        
    

    return render_template('view_full.html',data=data,data2=data2,vid=vid,st=st)

@app.route('/view_cus',methods=['POST','GET'])
def view_cus():
    data=[]
    act=request.args.get("act")
    
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM register")
    value = mycursor.fetchall()
    for dd in value:
        dt=[]
        dt.append(dd[0])
        dt.append(dd[1])
        dt.append(dd[2])
        dt.append(dd[3])
        dt.append(dd[4])
        dt.append(dd[6]) #card
        dt.append(dd[12]) #rdate
        dt.append(dd[13]) #adhar1
        dt.append(dd[17]) #fimg

        ky="a"+str(dd[0])
        obj=AESCipher(ky)
        
        dtt=[]
        mycursor.execute("SELECT * FROM user_account where rid=%s",(dd[0],))
        value1 = mycursor.fetchall()
        for d1 in value1:
            dt1=[]
            dt1.append(d1[0])
            dt1.append(d1[1])

            dt1.append(d1[2])
            dt1.append(d1[3])
            dt1.append(d1[4])
            dt1.append(d1[5])
            dt1.append(d1[6])
            

            '''bank=obj.decrypt(d1[2].encode("utf-8"))
            account=obj.decrypt(d1[3].encode("utf-8"))
            ifsc_code=obj.decrypt(d1[4].encode("utf-8"))
            branch=obj.decrypt(d1[5].encode("utf-8"))
            deposit=obj.decrypt(d1[6].encode("utf-8"))
            
            dt1.append(bank)
            dt1.append(account)
            dt1.append(ifsc_code)
            dt1.append(branch)
            dt1.append(deposit)'''
            dtt.append(dt1)
        dt.append(dtt)
        data.append(dt)

    if act=="del":
        did=request.args.get("did")
        mycursor.execute('delete from user_account WHERE id = %s', (did, ))
        mydb.commit()
        return redirect(url_for('view_cus')) 
        
    
    return render_template('view_cus.html', data=data,act=act)

###Preprocessing
@app.route('/view_photo',methods=['POST','GET'])
def view_photo():
    ff1=open("photo.txt","w")
    ff1.write("1")
    ff1.close()
    vid=""
    value=[]
    if request.method=='GET':
        vid = request.args.get('vid')
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM vt_face where vid=%s",(vid, ))
        value = mycursor.fetchall()

    if request.method=='POST':
        print("Training")
        vid=request.form['vid']
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM vt_face where vid=%s",(vid, ))
        dt = cursor.fetchall()
        for rs in dt:
            ##Preprocess
            path="static/frame/"+rs[2]
            path2="static/process1/"+rs[2]
            mm2 = PIL.Image.open(path).convert('L')
            rz = mm2.resize((200,200), PIL.Image.ANTIALIAS)
            rz.save(path2)
            
            '''img = cv2.imread(path2) 
            dst = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 15)
            path3="static/process2/"+rs[2]
            cv2.imwrite(path3, dst)'''
            ######
            img = cv2.imread(path2)
            gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            ret, thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

            # noise removal
            kernel = np.ones((3,3),np.uint8)
            opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 2)

            # sure background area
            sure_bg = cv2.dilate(opening,kernel,iterations=3)

            # Finding sure foreground area
            dist_transform = cv2.distanceTransform(opening,cv2.DIST_L2,5)
            ret, sure_fg = cv2.threshold(dist_transform,0.5*dist_transform.max(),255,0)

            # Finding unknown region
            sure_fg = np.uint8(sure_fg)
            segment = cv2.subtract(sure_bg,sure_fg)
            img = Image.fromarray(img)
            segment = Image.fromarray(segment)
            path3="static/process2/"+rs[2]
            segment.save(path3)
            
            #####
            image = cv2.imread(path2)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edged = cv2.Canny(gray, 50, 100)
            image = Image.fromarray(image)
            edged = Image.fromarray(edged)
            path4="static/process3/"+rs[2]
            edged.save(path4)
            ##
            #shutil.copy('static/images/11.png', 'static/process4/'+rs[2])
       
        return redirect(url_for('view_photo1',vid=vid))
        
    return render_template('view_photo.html', result=value,vid=vid)


#MTCNN - Face Detection & Alignment
detector = MTCNN()
def MTCNN_model(image):
    # Read image
    img = cv2.imread(image)
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Detect faces
    faces = detector.detect_faces(rgb_img)

    print("Number of faces detected:", len(faces))

    for i, face in enumerate(faces):
        x, y, w, h = face['box']
        confidence = face['confidence']

        # Draw bounding box
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(img, f"{confidence:.2f}", (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)

    cv2.imshow("MTCNN Face Detection", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def align_face(image, keypoints):
    left_eye = keypoints['left_eye']
    right_eye = keypoints['right_eye']

    # Calculate angle between eyes
    dy = right_eye[1] - left_eye[1]
    dx = right_eye[0] - left_eye[0]
    angle = np.degrees(np.arctan2(dy, dx))

    # Compute center between eyes
    eyes_center = (
        int((left_eye[0] + right_eye[0]) / 2),
        int((left_eye[1] + right_eye[1]) / 2)
    )

    # Rotate image
    M = cv2.getRotationMatrix2D(eyes_center, angle, scale=1)
    aligned_face = cv2.warpAffine(image, M, (image.shape[1], image.shape[0]))

    return aligned_face

def verify_align():
    for face in faces:
        x, y, w, h = face['box']
        keypoints = face['keypoints']

        aligned = align_face(rgb_img, keypoints)

        # Crop aligned face
        aligned_face = aligned[y:y+h, x:x+w]

        # Resize for FaceNet (160x160)
        aligned_face = cv2.resize(aligned_face, (160, 160))

        cv2.imshow("Aligned Face", cv2.cvtColor(aligned_face, cv2.COLOR_RGB2BGR))
        cv2.waitKey(0)

#Liveness Verification

def CNN_model():
    IMG_SIZE = 128

    model = Sequential([
        Conv2D(32, (3,3), activation='relu', input_shape=(IMG_SIZE, IMG_SIZE, 3)),
        BatchNormalization(),
        MaxPooling2D(2,2),

        Conv2D(64, (3,3), activation='relu'),
        BatchNormalization(),
        MaxPooling2D(2,2),

        Conv2D(128, (3,3), activation='relu'),
        BatchNormalization(),
        MaxPooling2D(2,2),

        Flatten(),
        Dense(128, activation='relu'),
        Dropout(0.5),
        Dense(1, activation='sigmoid')  # 1 = Real, 0 = Spoof
    ])

    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )

    model.summary()
    datagen = ImageDataGenerator(
        rescale=1./255,
        validation_split=0.2
    )

    train_gen = datagen.flow_from_directory(
        "dataset",
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=32,
        class_mode="binary",
        subset="training"
    )

    val_gen = datagen.flow_from_directory(
        "dataset",
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=32,
        class_mode="binary",
        subset="validation"
    )

    model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=15
    )

    model.save("liveness_cnn.h5")

def predict_liveness(face_img):
    face = cv2.resize(face_img, (IMG_SIZE, IMG_SIZE))
    face = face.astype("float32") / 255.0
    face = np.expand_dims(face, axis=0)

    prob = model.predict(face)[0][0]
    label = "REAL" if prob > 0.5 else "SPOOF"
    return label, prob

def liveness_detection():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = detector.detect_faces(rgb)

        for face in faces:
            x, y, w, h = face['box']
            x, y = abs(x), abs(y)

            face_img = rgb[y:y+h, x:x+w]

            if face_img.size == 0:
                continue

            label, prob = predict_liveness(face_img)

            # Colors
            color = (0, 255, 0) if label == "REAL" else (0, 0, 255)

            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(
                frame,
                f"{label} ({prob:.2f})",
                (x, y-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                color,
                2
            )

        cv2.imshow("Live Face Liveness Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
cv2.destroyAllWindows()
##########
                
@app.route('/view_photo1',methods=['POST','GET'])
def view_photo1():
    vid=""
    value=[]
    if request.method=='GET':
        vid = request.args.get('vid')
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM vt_face where vid=%s",(vid, ))
        value = mycursor.fetchall()
    return render_template('view_photo1.html', result=value,vid=vid)

@app.route('/view_photo2',methods=['POST','GET'])
def view_photo2():
    vid=""
    value=[]
    if request.method=='GET':
        vid = request.args.get('vid')
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM vt_face where vid=%s",(vid, ))
        value = mycursor.fetchall()
    return render_template('view_photo2.html', result=value,vid=vid)    

@app.route('/view_photo3',methods=['POST','GET'])
def view_photo3():
    vid=""
    value=[]
    if request.method=='GET':
        vid = request.args.get('vid')
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM vt_face where vid=%s",(vid, ))
        value = mycursor.fetchall()
    return render_template('view_photo3.html', result=value,vid=vid)

@app.route('/view_photo4',methods=['POST','GET'])
def view_photo4():
    vid=""
    value=[]
    if request.method=='GET':
        vid = request.args.get('vid')
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM vt_face where vid=%s",(vid, ))
        value = mycursor.fetchall()
    return render_template('view_photo4.html', result=value,vid=vid)

@app.route('/message',methods=['POST','GET'])
def message():
    vid=""
    name=""
    if request.method=='GET':
        vid = request.args.get('vid')
        mycursor = mydb.cursor()
        mycursor.execute("SELECT name FROM register where id=%s",(vid, ))
        name = mycursor.fetchone()[0]
    return render_template('message.html',vid=vid,name=name)


@app.route('/login',methods=['POST','GET'])
def login():
    uname=""
##    value=["1","2","3","4","5","6","7","8","9","0"]
##    change=random.shuffle(value)
##    print(change)
    if 'username' in session:
        uname = session['username']
    print(uname)
    mycursor1 = mydb.cursor()

    mycursor1.execute("SELECT * FROM register where card=%s",(uname, ))
    value = mycursor1.fetchone()
    accno=value[5]
    session['accno'] = accno
    
    mycursor1.execute("SELECT number FROM numbers order by rand()")
    value = mycursor1.fetchall()
    msg=""
        
    if request.method == 'POST':
        password1 = request.form['password']
        mycursor = mydb.cursor()
        mycursor.execute("SELECT count(*) FROM register where card=%s && password=%s",(uname, password1))
        myresult = mycursor.fetchone()[0]
        if password1=="":
            
            return render_template('login.html')
        else:
            
            #if str(password1)==str(myresult[10]):
            if myresult>0:
                #ff2=open("log.txt","w")
                #ff2.write(password1)
                #ff2.close()
                result=" Your Logged in sucessfully**"
                
                return redirect(url_for('userhome'))
            else:
                msg="Your logged in fail!!!"
                #return render_template('userhome.html',result=result)
    
    
    return render_template('login.html',value=value,msg=msg)



@app.route('/userhome')
def userhome():
    uname=""
    #if 'username' in session:
    #    uname = session['username']
    ff2=open("un.txt","r")
    uname=ff2.read()
    ff2.close() 

    name=""
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM register where card=%s",(uname, ))
    value = mycursor.fetchone()
    

    print(uname)
    
    mycursor.execute("SELECT * FROM register where card=%s",(uname, ))
    value = mycursor.fetchone()
    print(value)
    name=value[1]  
        
    return render_template('userhome.html',name=name,value=value)


@app.route('/user_account',methods=['POST','GET'])
def user_account():
    uname=""
    #if 'username' in session:
    #    uname = session['username']
    ff2=open("un.txt","r")
    uname=ff2.read()
    ff2.close() 

    name=""
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM register where card=%s",(uname, ))
    value = mycursor.fetchone()
    user_id=value[0]
    

    print(uname)
    
    mycursor.execute("SELECT * FROM register where card=%s",(uname, ))
    value = mycursor.fetchone()
    print(value)
    name=value[1]

    mycursor.execute("SELECT * FROM user_account where rid=%s",(user_id, ))
    value1 = mycursor.fetchall()
    
        
    return render_template('user_account.html',name=name,value=value,value1=value1)

'''@app.route('/deposit')
def deposit():
    return render_template('deposit.html')
@app.route('/deposit_amount',methods=['POST','GET'])
def deposit_amount():
    if request.method=='POST':
        name=request.form['name']
        accountno=request.form['accno']
        amount=request.form['amount']
        today = date.today()
        rdate = today.strftime("%b-%d-%Y")
        mycursor = mydb.cursor()
        mycursor.execute("SELECT max(id)+1 FROM event")
        maxid = mycursor.fetchone()[0]
        sql = "INSERT INTO event(id, name, accno, amount, rdate) VALUES (%s, %s, %s, %s, %s)"
        val = (maxid, name, accountno, amount, rdate)
        mycursor.execute(sql, val)
        mydb.commit()   
    return render_template('userhome.html')'''

'''@app.route('/withdraw')
def withdraw():

    
    return render_template('withdraw.html')'''

@app.route('/verify_face',methods=['POST','GET'])
def verify_face():
    msg=""
    ss=""
    uname=""
    act=""
    if request.method=='GET':
        act = request.args.get('act')
        
    #if 'username' in session:
    #    uname = session['username']
    ff2=open("un.txt","r")
    uname=ff2.read()
    ff2.close()
    
                
    return render_template('verify_face.html',msg=msg)

@app.route('/face',methods=['POST','GET'])
def face():
    msg=""
    ss=""
    uname=""
    act=""
    if request.method=='GET':
        act = request.args.get('act')
        
    #if 'username' in session:
    #    uname = session['username']
    ff2=open("un.txt","r")
    uname=ff2.read()
    ff2.close()
    print("uname="+uname)
    shutil.copy('static/faces/f1.jpg', 'static/f1.jpg')

    ff3=open("img.txt","r")
    mcnt=ff3.read()
    ff3.close()

    mcnt1=int(mcnt)
    if mcnt1==2:
        msg="Face Detected"
    elif mcnt1>2:
        msg="Multiple Face Detected!"
    else:
        msg=""
   
    
    
                
    return render_template('face.html',msg=msg,act=act,mcnt1=mcnt1)

@app.route('/process',methods=['POST','GET'])
def process():
    vid=""
    pg="0"
    act="1"
    uname=""
    #if 'username' in session:
    #    uname = session['username']
    ff2=open("un.txt","r")
    uname=ff2.read()
    ff2.close()
    value=[]
    shutil.copy('static/faces/f1.jpg', 'static/f1.jpg')
    cursor = mydb.cursor()
    cursor.execute('SELECT * FROM register WHERE card = %s', (uname, ))
    account = cursor.fetchone()
    name=account[1]
    mobile=account[3]
    
    email=account[4]
    vid=account[0]
    cursor.execute("SELECT vface FROM vt_face where vid=%s limit 0,1",(vid, ))
    value = cursor.fetchone()[0]
        
    
    return render_template('process.html', vid=vid,pg=pg,act=act,result=value)

@app.route('/pro',methods=['POST','GET'])
def pro():
    vid=""
    value=[]
    pgg=0
    act="1"
    uname=""
    #if 'username' in session:
    #    uname = session['username']
    ff2=open("un.txt","r")
    uname=ff2.read()
    ff2.close()
    if request.method=='GET':
        act = request.args.get('act')
    
        vid = request.args.get('vid')
        pg = request.args.get('pg')
        #pgg=int(pg)+1
        pgg=2
        mycursor = mydb.cursor()
        mycursor.execute("SELECT count(*) FROM vt_face where vid=%s",(vid,))
        dtt = mycursor.fetchone()[0]
        
        if dtt<=pgg:
            act="1"
        else:
            act="2"
        
        mycursor.execute("SELECT vface FROM vt_face where vid=%s limit 0,1",(vid, ))
        value = mycursor.fetchone()[0]
        #print(value)
        
    return render_template('pro.html', result=value,vid=vid,pg=pgg,act=act)

@app.route('/verify_face2',methods=['POST','GET'])
def verify_face2():
    msg=""
    ss=""
    uname=""
    mess=""
    act=""
    if request.method=='GET':
        act = request.args.get('act')
        
    #if 'username' in session:
    #    uname = session['username']
    ff2=open("un.txt","r")
    uname=ff2.read()
    ff2.close()

    ff2=open("bc.txt","r")
    bc=ff2.read()
    ff2.close()

    ff2=open("bk_det.txt","r")
    bkdata=ff2.read()
    ff2.close()

    ff2=open("facest.txt","r")
    fst=ff2.read()
    ff2.close()
    
    cursor = mydb.cursor()
    cursor.execute('SELECT * FROM register WHERE card = %s', (uname, ))
    account = cursor.fetchone()
    id1=str(account[0])
    name=account[1]
    mobile=account[3]
    print(mobile)
    email=account[4]
    vid=account[0]
    
    
    shutil.copy('static/faces/f1.jpg', 'faces/s1.jpg')
    cutoff=5
    img="v"+str(vid)+".jpg"
    '''cursor.execute('SELECT * FROM vt_face WHERE vid = %s', (vid, ))
    dt = cursor.fetchall()
    for rr in dt:
        hash0 = imagehash.average_hash(Image.open("static/frame/"+rr[2])) 
        hash1 = imagehash.average_hash(Image.open("faces/s1.jpg"))
        cc1=hash0 - hash1
        print("cc="+str(cc1))
        if cc1<=cutoff:
            ss="ok"
            break
        else:
            ss="no"'''

    
    if id1==fst:
        act="2"
        msg="Face Verified"
        print("correct person")
        return redirect(url_for('userhome', msg=msg))
    else:
        act="1"
        msg="Unknown Face Found"
        print("wrong person")
        #xn=randint(1000, 9999)
        #otp=str(xn)
        
        #cursor1 = mydb.cursor()
        #cursor1.execute('update register set otp=%s WHERE card = %s', (otp, uname))
        #mydb.commit()

        mess="Someone Access your account"
        url2="http://localhost/atm1/img.txt"
        ur = urlopen(url2)#open url
        data1 = ur.read().decode('utf-8')

       
        #idd=int(data1)+1
        #url="http://iotcloud.co.in/testsms/sms.php?sms=link12&name="+name+"&mess="+mess+"&mobile="+str(mobile)+"&bc="+bc
        #print(url)
        #webbrowser.open_new(url)
            
                
    return render_template('verify_face2.html',msg=msg,act=act,mess=mess,mobile=mobile,name=name,bc=bc,bkdata=bkdata)

@app.route('/cap',methods=['POST','GET'])
def cap():
    msg=""

    ff2=open("bc.txt","r")
    bc=ff2.read()
    ff2.close()

    
    
    return render_template('cap.html',msg=msg,bc=bc)

@app.route('/page',methods=['POST','GET'])
def page():
    msg=""
    st=""
    mess=""
    data=[]
    ff2=open("bc.txt","r")
    bc=ff2.read()
    ff2.close()

    ff2=open("facest.txt","r")
    st=ff2.read()
    ff2.close()

    ff2=open("bk_det.txt","r")
    bkdata=ff2.read()
    ff2.close()

    ff2=open("facest_det.txt","r")
    ud=ff2.read()
    ff2.close()

    ff2=open("sm.txt","r")
    sm=ff2.read()
    ff2.close()

    ff2=open("sm2.txt","r")
    sm2=ff2.read()
    ff2.close()

    u1=ud.split("|")
    name=u1[0]
    mobile=u1[1]

    if st=="no":
        ff2=open("facest_det.txt","r")
        dd=ff2.read()
        ff2.close()

        data=dd.split("|")
        #name|mob|mess
        

        ff2=open("facest.txt","w")
        ff2.write("")
        ff2.close()

        ff2=open("sm.txt","w")
        ff2.write("")
        ff2.close()

    logfn=bc+".txt"
    url2="http://localhost/atm1/"+logfn
    ur = urlopen(url2)#open url
    data11 = ur.read().decode('utf-8')
    

    if data11=="":
        s=1
    else:
        dat=data11

        d1=dat.split("-")
        if len(d1)>1:
            ds=int(d1[1])
            if d1[0]=="accepted":
                ff2=open("sm2.txt","w")
                ff2.write("")
                ff2.close()
            
            if d1[0]=="accepted" and ds>1:
                
                mess="Amount: Rs."+d1[1]+" has debited"
                if sm2=="":
                    ff2=open("sm2.txt","w")
                    ff2.write("2")
                    ff2.close()
                
        '''if data11 == "":
            s = 1
        else:
            parts = data11.split("-")

            # Check if split worked properly
            if len(parts) >= 2:
                status = parts[0]
                amount = int(parts[1])

                # If accepted - clear file
                if status == "accepted":
                    with open("sm2.txt", "w") as ff2:
                        ff2.write("")

                # If accepted and amount > 1
                if status == "accepted" and amount > 1:
                    mess = "Amount: Rs." + str(amount) + " has debited"

                    # Check sm2 value properly
                    try:
                        with open("sm2.txt", "r") as f:
                            sm2 = f.read().strip()
                    except:
                        sm2 = ""

                    if sm2 == "":
                        with open("sm2.txt", "w") as ff2:
                            ff2.write("2")'''

            
        ff=open("unknown_face.txt","w")
        ff.write(dat)
        ff.close()
    if sm2=="2":
        ff2=open("sm2.txt","w")
        ff2.write("3")
        ff2.close()
        

    
    return render_template('page.html',msg=msg,bc=bc,st=st,data=data,bkdata=bkdata,sm=sm,sm2=sm2,name=name,mess=mess,mobile=mobile)

@app.route('/verify',methods=['POST','GET'])
def verify():
    msg=""
    data1=""
    #act=""
    amtt=""
    bkid=""
    cc=""
    name=""
    mobile=""
    mess=""
    ff2=open("un.txt","r")
    uname=ff2.read()
    ff2.close()
    #data1="4"

    ff2=open("bc.txt","r")
    bc=ff2.read()
    ff2.close()

    logfn=bc+".txt"
    
    
    url2="http://localhost/atm1/"+logfn
    ur = urlopen(url2)#open url
    data11 = ur.read().decode('utf-8')

    #url2=r"C:/wamp/atm1/"+logfn
    #ff=open(url2,"r")
    #data11=ff.read()
    #ff.close()

    
    if data11=="":
        s=1
    else:
        
        vv=data11.split('-')
        data1=vv[0]
        amtt=vv[1]
        bkid=vv[2]
        print(data1)
    
    act = request.args.get('act')
    if act is None:
        act=""
    
    print("act="+str(act))
    if data1=="accept":
        act="1"

    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM register where card=%s",(uname, ))
    value = mycursor.fetchone()
  
    
    if act=="3":
        amt=0
        amt1=0
        amt2=0
    
        
        amount1=amtt
        
       
        mycursor.execute("SELECT amount FROM admin where username='admin'")
        amt1 = mycursor.fetchone()[0]

        #mycursor.execute("SELECT deposit FROM register where card=%s",(uname, ))
        #amt2 = mycursor.fetchone()[0]
        mycursor.execute("SELECT * FROM user_account where id=%s",(bkid, ))
        bdat = mycursor.fetchone()
        user_id=bdat[1]
        amt2=bdat[6]
        

        mycursor.execute("SELECT * FROM register where card=%s",(uname, ))
        ddt = mycursor.fetchone()
        name=ddt[1]
        mobile=ddt[3]

        amt=int(amount1)
        if amt<=amt1:

            if amt<=amt2:
                #mycursor.execute("UPDATE admin SET amount=amount-%s WHERE username='admin'",(amount1, ))
                #mydb.commit()
                mycursor.execute("UPDATE user_account SET deposit=deposit-%s WHERE id=%s",(amount1, bkid))
                mydb.commit()

                now = datetime.datetime.now()
                rdate=now.strftime("%d-%m-%Y")
                mycursor.execute("SELECT max(id)+1 FROM event")
                maxid = mycursor.fetchone()[0]
                if maxid is None:
                    maxid=1
                sql = "INSERT INTO event(id, name, accno, amount, rdate,user_id) VALUES (%s, %s, %s, %s, %s, %s)"
                val = (maxid, name, uname, amt, rdate, user_id)
                mycursor.execute(sql, val)
                mydb.commit()

                mess="Amount Debited Rs."+str(amt)
                #url="http://iotcloud.co.in/testsms/sms.php?sms=msg&name="+name+"&mess="+mess+"&mobile="+str(mobile)
                #webbrowser.open_new(url)
            
                msg="Withdraw success..."
            else:
                mess="Your Account balance is low!"
                #url="http://iotcloud.co.in/testsms/sms.php?sms=emr&name="+name+"&mess="+mess+"&mobile="+str(mobile)
                #webbrowser.open_new(url)
                msg="Your Account balance is low!"
        else:
            msg="Cash is not available in ATM!!"
    
        
    return render_template('verify.html',msg=msg,act=act,amtt=amtt,data1=data1,name=name,mobile=mobile,mess=mess,value=value)


@app.route('/otp', methods=['GET', 'POST'])
def otp():
    msg=""
    key=""
    if 'username' in session:
        uname = session['username']
    cursor = mydb.cursor()
    cursor.execute('SELECT otp FROM register WHERE card = %s', (uname, ))
    account = cursor.fetchone()[0]
    key=account
    
    if request.method=='POST':
        otp=request.form['otp']
        
        if otp==key:
            session['username'] = uname
            
            return redirect(url_for('verify_aadhar'))
        else:
            msg = 'OTP wrong!'
    return render_template('otp.html',msg=msg,key=key)

@app.route('/atm_balance',methods=['POST','GET'])
def atm_balance():
    msg=""
    ff2=open("un.txt","r")
    uname=ff2.read()
    ff2.close()

    cursor = mydb.cursor()
    if request.method=='POST':
        amount=request.form['amount']
        cursor.execute("UPDATE admin SET amount=%s WHERE username='admin'",(amount, ))
        mydb.commit()
        return redirect(url_for('admin'))

        
    
    cursor.execute("SELECT amount FROM admin WHERE username='admin'")
    value = cursor.fetchone()[0]
    
    return render_template('atm_balance.html',msg=msg,value=value)

@app.route('/withdraw',methods=['POST','GET'])
def withdraw():
    uname=""
    rid=request.args.get("rid")
    ##if 'username' in session:
    #    uname = session['username']
    #    accno = session['accno']
    ff2=open("un.txt","r")
    uname=ff2.read()
    ff2.close()
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM register where card=%s",(uname, ))
    value = mycursor.fetchone()

    mycursor.execute("SELECT * FROM user_account where id=%s",(rid, ))
    data1 = mycursor.fetchone()
    amt2=int(data1[6])
    print(amt2)
    
    st="" 
    msg=""
    amt=0
    amt1=0
   
    name=""
    mobile=""
    mess=""
    if request.method=='POST':
        
        amount1=request.form['amount']
        amt=int(amount1)
        

        mycursor.execute("SELECT amount FROM admin where username='admin'")
        amt1 = mycursor.fetchone()[0]

        #mycursor.execute("SELECT deposit FROM register where card=%s",(uname, ))
        #amt2 = mycursor.fetchone()[0]

        mycursor.execute("SELECT * FROM register where card=%s",(uname, ))
        ddt = mycursor.fetchone()
        name=ddt[1]
        mobile=ddt[3]
        user_id=ddt[0]

        
        if amt<=amt1:
          
            if amt<=amt2:
                #mycursor.execute("UPDATE admin SET amount=amount-%s WHERE username='admin'",(amount1, ))
                #mydb.commit()
                mycursor.execute("UPDATE user_account SET deposit=deposit-%s WHERE id=%s",(amount1, rid))
                mydb.commit()

                now = datetime.datetime.now()
                rdate=now.strftime("%d-%m-%Y")
                mycursor.execute("SELECT max(id)+1 FROM event")
                maxid = mycursor.fetchone()[0]
                if maxid is None:
                    maxid=1
                sql = "INSERT INTO event(id, name, accno, amount, rdate,user_id) VALUES (%s, %s, %s, %s, %s, %s)"
                val = (maxid, name, uname, amt, rdate,user_id)
                mycursor.execute(sql, val)
                mydb.commit()

                mess="Amount Debited Rs."+str(amt)
                #url="http://iotcloud.co.in/testsms/sms.php?sms=emr&name="+name+"&mess="+mess+"&mobile="+str(mobile)
                #webbrowser.open_new(url)
                st="1"
                msg="Withdraw success..."
            else:
                st="2"
                msg="Your Account balance is low!"
        else:
            st="3"
            msg="Cash is not available in ATM!!"
        
    return render_template('withdraw.html',msg=msg,name=name,mobile=mobile,mess=mess,value=value,st=st,data1=data1)


@app.route('/balance')
def balance():
    uname=""
    #if 'username' in session:
    #    uname = session['username']
    #    accno = session['accno']
    rid=request.args.get("rid")
    ff2=open("un.txt","r")
    uname=ff2.read()
    ff2.close()
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM register where card=%s",(uname, ))
    value = mycursor.fetchone()
    
    
    mycursor.execute("SELECT * FROM register where card=%s",(uname, ))
    data = mycursor.fetchone()
    

    mycursor.execute("SELECT * FROM user_account where id=%s",(rid, ))
    data1 = mycursor.fetchone()
    deposit=data1[6]
    print(str(deposit))
    
    return render_template('balance.html', deposit=deposit,value=value,data1=data1)



@app.route('/user_view')
def user_view():
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM register")
    result = mycursor.fetchall()
    return render_template('user_view.html', result=result)

@app.route('/view_withdraw')
def view_withdraw():
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM event order by id desc")
    result = mycursor.fetchall()
    return render_template('view_withdraw.html', result=result)

@app.route('/logout')
def logout():
    # remove the username from the session if it is there
    #session.pop('username', None)
    return redirect(url_for('index'))
#########
def gen2(camera):
    
    while True:
        frame = camera.get_frame()
        
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    
@app.route('/video_feed2')       
def video_feed2():
    return Response(gen2(VideoCamera2()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
################
def gen(camera):
    
    while True:
        frame = camera.get_frame()
        
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    
@app.route('/video_feed')
        

def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True,host='0.0.0.0', port=5000)
