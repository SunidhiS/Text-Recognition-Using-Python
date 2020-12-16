import numpy as np
import cv2
import os
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from keras.preprocessing.image import ImageDataGenerator
from keras.utils.np_utils import to_categorical

from keras.models import Sequential
from keras.layers import Dense
from keras.layers.core import Activation
from keras.optimizers import Adam
from keras.layers import Dropout,Flatten
from keras.layers.convolutional import Conv2D,MaxPooling2D


#####################################
path='My_data'
pathLabels = 'labels.csv'
testRatio=0.2
valRatio=0.2
imageDimensions= (32,32,3)

batchSizeVal=50
epochsVal=1
stepsPerEpoch=2000

#########################################
count=0
images=[]
classNo=[]
myList=os.listdir(path)
print("Total No Of Classes Detected",len(myList))
noOfClasses=len(myList)
print("Importing Classes.....")
for x in range(0,noOfClasses):
    myPicList=os.listdir(path+"/"+str(count))
    for y in myPicList:
        curImg=cv2.imread(path+"/"+str(count)+"/"+y)

        images.append(curImg)
        classNo.append(x)
    print(count,end=" ")
    count+=1
print(" ")
print("Total Images in Images list=",len(images))
print("Total IDS in ClassNo List=",len(classNo))

images=np.array(images)
classNo=np.array(classNo)
print(images.shape)

###Spliting the data
X_train,X_test,y_train,y_test = train_test_split(images,classNo,test_size=testRatio)
X_train,X_validation,y_train,y_validation = train_test_split(X_train,y_train,test_size=valRatio)

print(X_train.shape)
print(X_test.shape)
print(X_validation.shape)

numOfSamples=[]
for x in range(0,noOfClasses):
   print(len(np.where(y_train==x)[0]))
   numOfSamples.append(len(np.where(y_train==x)[0]))
print(numOfSamples)

plt.figure(figsize=(10,5))
plt.bar(range(0,noOfClasses),numOfSamples)
plt.title("No Of Images For Each Class")
plt.xlabel("Class Id")
plt.ylabel("Number Of Images")
plt.show()

def preProcessing(img):
#    img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
#    img = cv2.equalizeHist(img)
#    img = img/255
    return img

#img = preProcessing(X_train[30])
#img = cv2.resize(img,(300,300))
#cv2.imshow("PreProcessed",img)
#cv2.waitKey(0)

X_train= np.array(list(map(preProcessing,X_train)))
X_test= np.array(list(map(preProcessing,X_test)))
X_validation= np.array(list(map(preProcessing,X_validation)))

#X_train = X_train.reshape(X_train.shape[0],X_train.shape[1],X_train.shape[2],1)
#X_test = X_test.reshape(X_test.shape[0],X_test.shape[1],X_test.shape[2],1)
#X_validation = X_validation.reshape(X_validation.shape[0],X_validation.shape[1],X_validation.shape[2],1)


dataGen = ImageDataGenerator(width_shift_range=0.1,
                             height_shift_range=0.1,
                             zoom_range=0.2,
                             shear_range=0.1,
                             rotation_range=10)
#dataGen.fit(X_train)

y_train = to_categorical(y_train,noOfClasses)
y_test = to_categorical(y_test,noOfClasses)
y_validation = to_categorical(y_validation,noOfClasses)


def model():
    noOfFilters= 60
    sizeOfFilter1=(5,5)
    sizeOfFilter2=(3,3)
    sizeOfPool=(2,2)
    noOfNode=500

    model = Sequential()
    model.add((Conv2D(noOfFilters,sizeOfFilter1,input_shape=(imageDimensions[0],
                                                             imageDimensions[1],
                                                             1),activation='relu'
                                                               )))
    model.add((Conv2D(noOfFilters, sizeOfFilter1, activation='relu')))
    model.add(MaxPooling2D(pool_size=sizeOfPool))
    model.add((Conv2D(noOfFilters//2, sizeOfFilter2,activation='relu')))
    model.add((Conv2D(noOfFilters//2, sizeOfFilter2, activation='relu')))
    model.add(MaxPooling2D(pool_size=sizeOfPool))
    model.add(Dropout(0.5))

    model.add(Flatten())
    model.add(Dense(noOfNode,activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(noOfClasses,activation='softmax'))
    model.compile(optimizer =Adam,lr=0.01,loss='categorical crossentropy',
                  metrics=['accuracy'])
    return model

history = model.fit_generator(dataGen.flow(X_train,y_train,
                                           batch_size=batchSizeVal),
                                           steps_per_epoch=stepsPerEpochVal,
                                           epochs=epochsVal,
                                           validation_data=(X_validation,y_validation),
                                           shuffle=1)

plt.figure(1)
plt.plot(history['loss'])
plt.plot(history['val_loss'])
plt.legend(['training','validation'])
plt.title('Loss')
plt.xlabel('epoch')
plt.figure(2)
plt.plot(history['accuracy'])
plt.plot(history['val_accuracy'])
plt.legend(['training','validation'])
plt.title('Accuracy')
plt.xlabel('epoch')
plt.show()
score=model.evaluate(X_test,y_test,verbose=0)
print('Test Score=',score[0])
print('Test Accuracy=',score[1])
