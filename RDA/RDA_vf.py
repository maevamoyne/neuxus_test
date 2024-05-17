"""
Simple Python RDA client for the RDA tcpip interface of the BrainVision Recorder
It reads all the information from the recorded EEG,
prints EEG and marker information to the console and calculates and
prints the average power every second


Brain Products GmbH
Gilching/Freiburg, Germany
www.brainproducts.com

"""

# needs socket and struct library
from socket import *
from struct import *
import numpy as np
import mne


# Marker class for storing marker information
class Marker:
    def __init__(self):
        self.position = 0
        self.points = 0
        self.channel = -1
        self.type = ""
        self.description = ""

# Helper function for receiving whole message
def RecvData(socket, requestedSize):
    returnStream = b''
    while len(returnStream) < requestedSize:
        databytes = socket.recv(requestedSize - len(returnStream))
        if databytes == '':
            raise(RuntimeError, "connection broken")
        returnStream += databytes
 
    return returnStream   

    
# Helper function for splitting a raw array of
# zero terminated strings (C) into an array of python strings
def SplitString(raw):
    stringlist = []
    s = ""
    for i in range(len(raw)):
        if raw[i] != '\x00':
            s = s + str(raw[i])
        else:
            stringlist.append(s)
            s = ""

    return stringlist
    

# Helper function for extracting eeg properties from a raw data array
# read from tcpip socket
def GetProperties(rawdata):

    # Extract numerical data
    (channelCount, samplingInterval) = unpack('<Ld', rawdata[:12])

    # Extract resolutions
    resolutions = []
    for c in range(channelCount):
        index = 12 + c * 8
        restuple = unpack('<d', rawdata[index:index+8])
        resolutions.append(restuple[0])

    # Extract channel names
    channelNames = SplitString(rawdata[12 + 8 * channelCount:])

    return (channelCount, samplingInterval, resolutions, channelNames)

# Helper function for extracting eeg and marker data from a raw data array
# read from tcpip socket       
def GetData(rawdata, channelCount):

    # Extract numerical data
    (block, points, markerCount) = unpack('<LLL', rawdata[:12])

    # Extract eeg data as array of floats
    data = []
    for i in range(points * channelCount):
        index = 12 + 4 * i
        value = unpack('<f', rawdata[index:index+4])
        data.append(value[0])

    # Extract markers
    try:
        markers = []
        index = 12 + 4 * points * channelCount
        for m in range(markerCount):
            markersize = unpack('<L', rawdata[index:index+4])

            ma = Marker()
            (ma.position, ma.points, ma.channel) = unpack('<LLl', rawdata[index+4:index+16])
            typedesc = SplitString(rawdata[index+16:index+markersize[0]])
            ma.type = typedesc[0]
            ma.description = typedesc[1]

            markers.append(ma)
            index = index + markersize[0]
    except Exception as e:
        pass
    return (block, points, markerCount, data, markers)


##############################################################################################
#
# Main RDA routine
#
##############################################################################################

# Create a tcpip socket
con = socket(AF_INET, SOCK_STREAM)

print("Waiting for connection...")
while True:
    try:
        # Create a tcpip socket
        con.connect(("localhost", 51254))
        break
    except Exception as e:
        continue
        

# Flag for main loop
finish = False

# data buffer for calculation, empty in beginning
buffer = None

# block counter to check overflows of tcpip buffer
lastBlock = -1

#### Main Loop ####
while not finish:

    # Get message header as raw array of chars
    rawhdr = RecvData(con, 24)

    # Split array into usefull information id1 to id4 are constants
    (id1, id2, id3, id4, msgsize, msgtype) = unpack('<llllLL', rawhdr)

    # Get data part of message, which is of variable size
    rawdata = RecvData(con, msgsize - 24)

    # Perform action dependend on the message type
    if msgtype == 1:
        # Start message, extract eeg properties and display them
        # TODO: channel names not display
        (channelCount, samplingInterval, resolutions, channelNames) = GetProperties(rawdata)
        # reset block counter
        lastBlock = -1

        print("Start")
        print("Number of channels: " + str(channelCount))
        print("Sampling interval: " + str(samplingInterval))
        print("Resolutions: " + str(resolutions))
        print("Channel Names: " + str(channelNames))

        buffer = np.empty((channelCount, 1))



    elif msgtype == 4:
        # Data message, extract data and markers
        (block, points, markerCount, data, markers) = GetData(rawdata, channelCount)
        data = np.array(data)
        data = data.reshape(points, channelCount).T

        # Check for overflow
        if lastBlock != -1 and block > lastBlock + 1:
            print("*** Overflow with " + str(block - lastBlock) + " datablocks ***")
        lastBlock = block

        # Print markers, if there are some in actual block
        try:
            if markerCount > 0:
                for m in range(markerCount):
                    print("Marker " + markers[m].description + " of type " + markers[m].type)
        except Exception as e:
            pass

        # Put data at the end of actual buffer
        buffer = np.hstack((buffer, data))
        print(buffer.shape)



    elif msgtype == 3:
        # Stop message, terminate program
        print("Stop")
        finish = True

# Close tcpip connection
con.close()

# Create Raw Array
if channelNames == []:
    ch_names = [str(i+1) for i in range(channelCount)]
else:
    ch_names = channelNames
sfreq = 1 / samplingInterval * 1000
info = mne.create_info(ch_names=ch_names,
                       sfreq=250,
                       ch_types='eeg')

data = buffer * 1e-6
raw = mne.io.RawArray(data, info)
# Save
raw.save('test_raw.fif', overwrite=True)


