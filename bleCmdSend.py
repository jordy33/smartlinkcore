import pexpect
import sys
import time

resp=pexpect.spawn('hciconfig hci0 up')
resp.expect('.*')
bluetooth_adr = 'de:2d:06:53:4b:ad'
tool = pexpect.spawn('gatttool -b ' + bluetooth_adr + ' --interactive -t random')
tool.expect('\[LE\]>')
print ("Listo para conectar prenda el dispositivo..")
tool.sendline('connect')
# test for success of connect
tool.expect('Connection successful.*\[LE\]>')
print ("successfull connection")
while True:
    n = input("Ponga (s) para salir:")
    cmd='00:00'
    if n.strip() == '1':
     cmd='01:00'
    if n.strip() == '2':
     cmd='02:00'
    tool.sendline('char-write-cmd 0x000e '+cmd)
    tool.expect('\[LE\]>')
    if n.strip() == 's':
        break
tool.sendline('disconnect')
