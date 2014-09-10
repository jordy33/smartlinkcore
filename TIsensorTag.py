#!/usr/bin/env python
# Fetch temperature from sensortag by bluetooth low energy and feed it up into xively.
# Source code is derived from https://github.com/msaunby/ble-sensor-pi
# usage: python sensortag2xively.py {mac address}
 
#import xively
import datetime
import sys
import time
#import pytz
import pexpect
import xml.etree.ElementTree as etree
XIVELY_API_KEY = "Your API Key here"
XIVELY_FEED_ID = 00000000
#tz = pytz.timezone('Asia/Tokyo')

def convert_hex_to_ascii(h):
    chars_in_reverse = []
    while h != 0x0:
        chars_in_reverse.append(chr(h & 0xFF))
        h = h >> 8
    chars_in_reverse.reverse()

    return ''.join(chars_in_reverse)

def floatfromhex(h):
    t = float.fromhex(h)
    if t > float.fromhex('7FFF'):
        t = -(float.fromhex('FFFF') - t)
        pass
    return t

def calcTmpTarget(objT, ambT):
    m_tmpAmb = ambT/128.0
    Vobj2 = objT * 0.00000015625
    Tdie2 = m_tmpAmb + 273.15
    S0 = 6.4E-14 # Calibration factor
    a1 = 1.75E-3
    a2 = -1.678E-5
    b0 = -2.94E-5
    b1 = -5.7E-7
    b2 = 4.63E-9
    c2 = 13.4
    Tref = 298.15
    S = S0*(1+a1*(Tdie2 - Tref)+a2*pow((Tdie2 - Tref),2))
    Vos = b0 + b1*(Tdie2 - Tref) + b2*pow((Tdie2 - Tref),2)
    fObj = (Vobj2 - Vos) + c2*pow((Vobj2 - Vos),2)
    tObj = pow(pow(Tdie2,4) + (fObj/S),.25)
    tObj = (tObj - 273.15)
    return tObj

def connect(bdaddr):
    resp=pexpect.spawn('hciconfig hci0 up')
    resp.expect('.*')
    tool = pexpect.spawn('gatttool -b ' + bdaddr + ' --interactive')
    tool.expect('\[LE\]>')
    print("Preparing to connect. You might need to press the side button...")
    tool.sendline('connect')
    # test for success of connect
    tool.expect('Connection successful.*\[LE\]>')
    print ("connection successful")
    tool.sendline('char-write-cmd 0x29 01')
    tool.expect('\[LE\]>')
    print ('sending command')
    tool.sendline('char-read-hnd 0x25')
    tool.expect('Characteristic value/descriptor: .*')
    return tool

def read_data(tool):
    tool.sendline('char-read-hnd 0x25')
    tool.expect('Characteristic value/descriptor: .*')
    rval = tool.after.split()
    objT = floatfromhex(rval[3].decode("utf-8")+rval[2].decode("utf-8"))
    ambT = floatfromhex(rval[5].decode("utf-8")+rval[4].decode("utf-8"))
    tmpr = calcTmpTarget(objT, ambT)
    print('temperatura',tmpr)
    tmpr=0
    return float("%.1f" % tmpr)
 
def main(bdaddr='bc:6a:29:ac:29:31'):
    #api = xively.XivelyAPIClient(XIVELY_API_KEY)
    #feed = api.feeds.get(XIVELY_FEED_ID)
    tool = connect(bdaddr)
    while True:
        try:
            tmpr = read_data(tool)
            #now = datetime.datetime.now(tz=tz)
            #feed.datastreams = [xively.Datastream(id='tmpr', current_value=tmpr, at=now),]
            #feed.update()
            #print(now, tmpr)
        except:
            print("Error:", sys.exc_info()[0])
            time.sleep(60)
 
if __name__ == '__main__':
    try:
        args = sys.argv[1:]
        main(*args)
    except KeyboardInterrupt:
        pass
