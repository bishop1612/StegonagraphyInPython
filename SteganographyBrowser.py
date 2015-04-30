import sys
import os
from PySide.QtCore import *
from PySide.QtGui import *
import math
import base64
from SteganographyGUI import *
from NewSteganograhy import *
from Crypto import Random
from Crypto.Cipher import AES

#Bold & Beautiful
class SteganographyBrowser(QMainWindow, Ui_MainWindow):
    """
    The class that handles all the functionality of the UI
    Functions : __init__, clear_message,handle,extract,wipe_dial
    """
    def __init__(self, parent=None):
        """
        Used to initialise the Steganography Browser
        class. THe application does not start if a folder is not selected.
        :param parent:
        :return: None if application exits
        """
        super(SteganographyBrowser, self).__init__(parent)
        self.directory =  self.getDir()
        if self.directory != "":
            self.setupUi(self)
            self.InitialState()
            self.btnExtract.setEnabled(False);
            self.btnWipeMedium.setEnabled(False);
            self.fileTreeWidget.expandAll()
            self.scn = ""
        else:
            exit ()

        #Connecting the buttons to the right functions
        self.fileTreeWidget.itemClicked.connect(self.handle)
        self.btnExtract.clicked.connect(lambda: self.extract(self.mes,self.img))
        self.btnWipeMedium.clicked.connect(lambda: self.wipe_dial(self.mes,self.img,self.item))
        self.viewMedium.show()

    def clear_message(self):
        """
        Function to clear the message from the
        message widget boxes.
        :return:
        """
        if self.stackMessage.currentIndex() == 0:
            if self.scn != "":
                self.scn.removeItem(self.pixItem)
                self.viewMessage.setScene(self.scn)
                self.viewMessage.show()
                self.scn = ""
        else:
            self.txtMessage.setPlainText("")

    def handle(self,item,column):
        """
        Function to display the images in the
        viewMedium() widget. Column is the image name in the folder
        :param item:
        :param column:
        :return:
        """
        self.clear_message()

        #Placing the image in the graphics view
        cur_img = item.text(column)
        if cur_img in {"ColorImage","Text","GrayImage"}:
            cur_img = item.parent().text(column)

        scn = QtGui.QGraphicsScene()
        pixmap = QtGui.QPixmap(self.directory +"/"+ cur_img)
        pixItem = QtGui.QGraphicsPixmapItem(pixmap)
        self.viewMedium.fitInView(pixItem,Qt.KeepAspectRatio)
        scn.addItem(pixItem)
        self.viewMedium.setScene(scn)
        nw = NewSteganography(self.directory+"/"+cur_img,"horizontal")
        mes = nw.checkIfMessageExists()

        #Enabling the right button widgets based on the selection
        if mes[0] == True:
            self.btnExtract.setEnabled(True)
            self.btnWipeMedium.setEnabled(True)
            self.dir = "horizontal"
        else:
            nw = NewSteganography(self.directory+"/"+cur_img,"vertical")
            mes = nw.checkIfMessageExists()
            self.dir = "vertical"
            if mes[0] == True:
                self.btnExtract.setEnabled(True)
                self.btnWipeMedium.setEnabled(True)
            else:
                self.btnExtract.setEnabled(False)
                self.btnWipeMedium.setEnabled(False)
        self.mes = mes[1]
        self.item = item
        self.img = cur_img

    def extract(self,message,image):
        """
        FUnction to extract the message from the image and display
        it in the right widget
        :param message:
        :param image:
        :return:
        """
        nw = Steganography(self.directory+"/"+image,self.dir)
        ges = nw.extractMessageFromMedium()
        if ges != None:
            lines = ges.xml_str
            lines = lines.strip()
            matches = re.findall(".+type=\"(.+)\" size=\"(.+)\" encrypted=\"(.+)\">\\n(.+)\\n</message>",lines)
            if len(matches) != 0:
                self.messagetype = matches[0][0]
                self.size = matches[0][1]
                self.encrypt = matches[0][2]
                self.xml = matches[0][3]
                if self.encrypt != "True" :
                    if self.messagetype != "Text":
                        decoded = base64.b64decode(bytearray(self.xml,'utf-8'))
                    else:
                        decoded = base64.b64decode(self.xml)

                    #Decoding images and displaying them
                    if message != "Text":
                        self.stackMessage.setCurrentIndex(0)
                        width = int(self.size.split(',')[0])
                        height = int(self.size.split(',')[1])
                        if message == "ColorImage":
                            band = height  * width
                            r = decoded[0:int(band)]
                            g = decoded[band:2*band]
                            b = decoded[2*band:3*band]
                            im = Image.new('RGB',[width,height])
                            rgb = [(r,g,b) for r,g,b in zip(r,g,b)]
                            im.putdata(rgb)
                            im.save("ex.jpg")
                        else:
                            sizes = self.size.split(',')
                            width = int(sizes[0])
                            height = int(sizes[1])
                            new = Image.frombytes('L',[width,height],decoded)
                            new.save("ex.jpg")

                        self.scn = QtGui.QGraphicsScene()
                        pixmap = QtGui.QPixmap("ex.jpg")
                        self.pixItem = QtGui.QGraphicsPixmapItem(pixmap)
                        self.scn.addItem(self.pixItem)
                        self.viewMessage.fitInView(self.pixItem,Qt.KeepAspectRatio)
                        self.viewMessage.setScene(self.scn)
                        self.viewMessage.show()
                    else:
                        self.stackMessage.setCurrentIndex(1)
                        self.txtMessage.setPlainText(str(decoded,"utf-8"))
                    self.btnExtract.setEnabled(False)
                else:
                    self.enc()

    def enc(self):
        """
        Requesting the password
        for encryption
        :return:
        """
        passwd,res = QInputDialog.getText(self,"Prompt","Enter Password",QLineEdit.Password)
        if res == True:
            self.extractenc(passwd)

    def extractenc(self,passwd):
        """
        Extracting text if password
        is wrong
        :param passwd:
        :return:
        """
        msgBox = QMessageBox()
        try:
            decoded = base64.b64decode(self.xml)
            IV = Random.new().read(16)
            aes = AES.new(passwd, AES.MODE_ECB, IV)
            enctxt = aes.decrypt(decoded)
            self.stackMessage.setCurrentIndex(1)
            self.txtMessage.setPlainText(str(enctxt,"utf-8"))
            self.btnExtract.setEnabled(False)
            msgBox.setText("The message has been extracted.");
            msgBox.exec_();
        except:
            msgBox.setText("The password is wrong.");
            msgBox.exec_();

    def wipe_dial(self,message,image,item):
        """
        Function for wiping the medium
        :param message:
        :param image:
        :param item:
        :return:
        """
        msgBox = QMessageBox()
        msgBox.setInformativeText("Are you sure?")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.Yes)
        ret = msgBox.exec_();
        if ret == QMessageBox.Yes:
            nw = NewSteganography(self.directory+"/"+image,self.dir)
            nw.wipeMedium()
            self.btnExtract.setEnabled(False)
            self.btnWipeMedium.setEnabled(False)
            self.fileTreeWidget.clear()
            self.InitialState()
            self.clear_message()



    def InitialState(self):
        """
        Function to populate the tree
        Widget with images from the
        selected folder
        :return:
        """
        pics = os.listdir(self.directory)
        dir = self.directory.split("/")
        self.fileTreeWidget.setHeaderItem(QtGui.QTreeWidgetItem([dir[len(dir)-1]]))
        for pic in pics:
            parentItem=QtGui.QTreeWidgetItem([pic])
            self.fileTreeWidget.addTopLevelItem(parentItem)
            nw = NewSteganography(self.directory+"/"+pic,"horizontal")
            mes = nw.checkIfMessageExists()
            if mes[0] == True:
                childItem=QtGui.QTreeWidgetItem([mes[1]])
                parentItem.insertChild(0, childItem)
                parentItem.setForeground(0,QtGui.QBrush(QtGui.QColor("red")))
                childItem.setForeground(0,QtGui.QBrush(QtGui.QColor("green")))
            else:
                nw = NewSteganography(self.directory+"/"+pic,"vertical")
                mes = nw.checkIfMessageExists()
                if mes[0] == True:
                    childItem=QtGui.QTreeWidgetItem([mes[1]])
                    parentItem.insertChild(0, childItem)
                    parentItem.setForeground(0,QtGui.QBrush(QtGui.QColor("red")))
                    childItem.setForeground(0,QtGui.QBrush(QtGui.QColor("green")))
                else:
                    parentItem.setForeground(0,QtGui.QBrush(QtGui.QColor("blue")))


    def getDir(self):
        """
        This is the function that
        displays the initial dialog box
        from where you select the desired folder
        with images to perform the extraction
        :return:
        """
        dialog = QtGui.QFileDialog()
        dialog.setFileMode(QtGui.QFileDialog.Directory)
        dialog.setOption(QtGui.QFileDialog.ShowDirsOnly)
        directory = dialog.getExistingDirectory(self, 'Choose Directory', os.path.curdir)
        return directory

currentApp = QApplication(sys.argv)
currentForm = SteganographyBrowser()

currentForm.show()
currentApp.exec_()
