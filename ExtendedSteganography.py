from Steganography import *

class AesMessage(Message):

    def __init__(self,message,password):
        self.inst = message
        self.pwd = password
        if password == "":
            raise ValueError("Password is empty")

    def saveToImage(self,targetImagePath):
        self.inst.saveToImage(targetImagePath)

    def saveToTextFile(self,targetTextFilePath):
        self.inst.saveToTextFile(targetImagePath)

    def saveToTarget(self,targetPath):
        self.inst.saveToTarget(targetPath)

    def getXmlString(self):
        self.inst.getXmlString()

class ColorSteganography(Steganography):
    def __init__(self,imagePath,direction='horizontal'):
        pass

    def extractMessageFromMedium(self):
        pass

    def embedMessageInMedium(self,message,targetImagePath):
        passpwd