#!/usr/local/bin/python3.4
from __future__ import print_function
import glob
import sys
import os
import filecmp
import re
import math
import base64
from PIL import Image



class Message:
    """
    Class Message
    to encode and decode text and pixels
    and then convert it into an xml string
    """
    def __init__(self,**kwargs):
        """
        Initializing the instance of the message class. It assigns the file path and message type or xml string.
        Raises ValueError if one of the arguments are wrong
        """
        #Checking the length of the arguments
        if(len(kwargs) < 1 or len(kwargs) > 2):
            raise  ValueError("Missing Arguement")

        #Initialising the xml string if length of argument is 1
        if len(kwargs) == 1 :
            for key,value in kwargs.items():
                if str(key) != "XmlString":
                    raise ValueError("Wrong Argument")
                else:
                    self.xml_str = value

        #Initialising the file path and message type if length of arguments is 2
        if len(kwargs) == 2:
            for key,value in kwargs.items():
                if str(key) == "filePath":
                    self.filepath = str(value)
                    if self.filepath == "":
                        raise ValueError("No filepath")
                elif str(key) == "messageType":
                    self.messagetype = str(value)
                    if (self.messagetype != "Text") :
                        if (self.messagetype != "GrayImage") :
                            if (self.messagetype != "ColorImage") :
                                raise ValueError("Wrong Message Type")
                else:
                    raise ValueError("Wrong Argument")

    def MessageSize(self):
        """
        Returns length of the xml string
        """
        length = len(self.xml_tsr)
        if length == 0:
            raise Exception("No Data Exists")
        return length

    def saveToImage(self,targetImagePath):
        """
        Function to convert xml string to image
        and then save it in the target image path
        """
        #Finding the data from xml
        lines = self.xml_str
        lines = lines.strip()
        xml = self.extractinfo(lines)
        self.filepath = targetImagePath

        if(self.messagetype == ""):
            raise  Exception("No Data Exists")

        if(self.messagetype == "Text"):
            raise TypeError("Message Type is not Image Type")

        if(self.xml == ""):
            raise  Exception("No Data Exists")

        if(self.size == ""):
            raise  Exception("No Data Exists")

        #Decoding the message
        decoded = base64.b64decode(bytearray(self.xml,'utf-8'))

        #Saving GrayScale Image
        if(self.messagetype == "GrayImage"):
            sizes = self.size.split(',')
            width = int(sizes[0])
            height = int(sizes[1])
            new = Image.frombytes('L',[width,height],decoded)
            new.save(targetImagePath)

        #Saving Color Image
        if(self.messagetype == "ColorImage"):
            width = int(self.size.split(',')[0])
            height = int(self.size.split(',')[1])
            band = height  * width
            r = decoded[0:int(band)]
            g = decoded[band:2*band]
            b = decoded[2*band:3*band]
            im = Image.new('RGB',[width,height])
            rgb = [(r,g,b) for r,g,b in zip(r,g,b)]
            im.putdata(rgb)
            im.save(targetImagePath)


    def saveToTextFile(self,targetTextFilePath):
        """
        Function to convert xml string to text
        and then save it in the target image path
        """
        #Finding the data from xml
        lines = self.xml_str
        lines = lines.strip()
        xml = self.extractinfo(lines)
        self.filepath = targetTextFilePath

        if(self.messagetype == ""):
            raise  Exception("No Data Exists")

        if(self.xml == ""):
            raise  Exception("No Data Exists")

        if(self.messagetype != "Text"):
            raise TypeError("Message Type is not Image Type")

        decoded = base64.b64decode(self.xml)

        #Saving Text File
        try:
            o = open(targetTextFilePath,'w', newline="\r\n")
        except:
            raise  Exception("No Data Exists")
        o.write(str(decoded,"utf-8"))
        o.close()

    def extractinfo(self,lines):
        """
        Function to extract information from
        Xml string using regular expressions
        """
        matches = re.findall(".+type=\"(.+)\" size=\"(.+)\" encrypted=\"(.+)\">\\n(.+)\\n</message>",lines)
        if len(matches) != 0:
            self.messagetype = matches[0][0]
            self.size = matches[0][1]
            self.encrypt = matches[0][2]
            self.xml = matches[0][3]
        else:
            raise  Exception("No Data Exists")
        return self.xml

    def saveToTarget(self,targetPath):
        """
        Function to redirect the xml string into
        the right function and save it in the right file.
        :param targetPath:
        :return:
        """
        lines = self.xml_str
        lines = lines.strip()
        xml = self.extractinfo(lines)
        self.filepath = targetPath
        if(self.messagetype == "Text"):
            self.saveToTextFile(self.filepath)
        else:
            self.saveToImage(self.filepath)

    def getXmlString(self):
        """
        Function converting an image,text
        to an xml string
        :return:
        """
        if self.messagetype == "" and self.filepath == "":
            raise Exception("No Data Exists")


        #Encoding text message
        if self.messagetype == "Text":
            try:
                with open(self.filepath,"r") as f:
                    lines = f.read()
            except :
                print("File does not exist")
            encoded = base64.b64encode(bytes(lines,"UTF-8"))
            textsize = len(lines)
            encoded_str = str(encoded,"UTF-8")

        #Encoding grayscale Image
        if self.messagetype == "GrayImage":
            try:
                im = Image.open(self.filepath)
            except :
                print("File does not exist")
            pixels = list(im.getdata())
            encoded = base64.b64encode(bytes(pixels))
            encoded_str = str(encoded,"UTF-8")

        #Encoding grayscale Image
        if self.messagetype == "ColorImage":
            try:
                im = Image.open(self.filepath)
            except :
                print("File does not exist")
            r = list(im.getdata(0))
            g = list(im.getdata(1))
            b = list(im.getdata(2))
            pixels = list(r + g + b)
            encoded = base64.b64encode(bytes(pixels))
            encoded_str = str(encoded,"UTF-8")

        #Xml String for String
        if self.messagetype != "Text":
            self.xml_str = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
            self.xml_str += "<message type=\"" + str(self.messagetype) +"\" size=\"" +str(im.size[0])+","+str(im.size[1]) + "\" encrypted=\"False\">\n"
            self.xml_str += encoded_str
            self.xml_str += "\n</message>"
        else:
        #Xml String for Images
            self.xml_str = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
            self.xml_str += "<message type=\"" + str(self.messagetype) +"\" size=\"" +str(textsize) + "\" encrypted=\"False\">\n"
            self.xml_str += encoded_str
            self.xml_str += "\n</message>"

        return self.xml_str

class Steganography:
    """
    Class to extract xml messages into
    a GrayScale Image
    """
    def __init__(self,imagePath,direction='horizontal'):
        """
        Function to initialise member
        variables of Steganography Class

        :param imagePath: Desired Image Path
        :param direction: Reading Image Direction
        :return:
        """
        self.dir  = str(direction)
        self.path = imagePath
        if self.dir != "horizontal":
            if self.dir != "vertical":
                raise ValueError("Enter the right image direction")
        try:
            self.im = Image.open(imagePath)
        except :
            raise ValueError("File does not exist")
        self.size = self.im.size[0] * self.im.size[1]
        self.format = str(self.im.mode)
        if self.format != "L":
            raise TypeError("It is not a gray scale image")

    def embedMessageInMedium(self,message,targetImagePath):
        """
        Function to embed an xml message
        into the image
        :param message: Xml Message
        :param targetImagePath: Intended file path
        :return:
        """
        if self.dir == "vertical":
            self.im = self.im.transpose(Image.TRANSPOSE)

        #Message
        mes = message.getXmlString()

        #Width and Height of Image
        width = int(self.im.size[0])
        height = int(self.im.size[1])

        #Converting string to message
        bytes_list = list(mes)

        #Generating the data to be embedded
        i = 0
        bytes_message = ""
        for char in bytes_list:
            bytes_list[i] = ord(str(char))
            bytes_list[i] = bin(bytes_list[i])[2:].zfill(8)
            bytes_message += bytes_list[i]
            i += 1


        if len(mes) > self.size:
            raise ValueError("Size of given message is larger than the medium can hold")

        pixels = list(self.im.getdata())

        #Changing pixels of medium based on message from medium
        i = 0
        for bit in bytes_message:
            if bit == '0':
                if pixels[i] % 2 != 0:
                    pixels[i] -= 1
            if bit == '1':
                if pixels[i] % 2 == 0:
                    pixels[i] += 1
            i += 1

        #Building the image
        encoded = base64.b64encode(bytes(pixels))
        encoded_str = str(encoded,"UTF-8")
        decoded = base64.b64decode(encoded_str)
        new = Image.frombytes('L',[width,height],decoded)
        if self.dir == "vertical":
            new = new.transpose(Image.TRANSPOSE)
        new.save(targetImagePath)

    def extractMessageFromMedium(self):
        """
        Function to extract xml message
        from any medium
        :return: xml string
        """
        if self.dir == "vertical":
            self.im = self.im.transpose(Image.TRANSPOSE)
        pixels = list(self.im.getdata())

        #Generating the Binary stream
        i = 0
        for ind in pixels:
            if ind % 2 == 0:
                pixels[i] = '0'
            else:
                pixels[i] = '1'
            i += 1

        i = 0

        new_list = []
        newstr = ""

        #Appending the binary stream into a string
        c = 1
        for ind in pixels:
            newstr += ind
            if c == 8:
                new_list.append(newstr)
                newstr = ""
                c = 0

            c += 1

        i = 0
        sum = 0
        k = 0
        new_str = ""

        #Generating the message
        for byt in new_list:
            for bit in byt:
                sum += int(bit)*2**(7-k)
                k += 1
            new_list[i] = chr(int(sum))
            new_str += new_list[i]
            k = 0
            sum  = 0
            i += 1

        #Checking the right format of the message
        matches = re.search(".+type=\"(.+)\" size=\"(.+)\" encrypted=\"(.+)\">\\n(.+)\\n</message>",new_str)

        #Generated the xml string
        if matches != None:
            rstr = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"+matches.group()
            mes = Message(XmlString=rstr)
            return mes
        else:
            return None

if __name__ == "__main__":
    pass
