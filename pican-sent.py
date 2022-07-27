
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import serial
import os
import time
import subprocess
import RPi.GPIO as GPIO
import tkinter as tk

from threading import Thread

ser = serial.Serial()
mclr = 26

root = tk.Tk()
root.title('PiCAN SENT v1.0 skpang.co.uk 2022')
root.geometry("780x780")
saved_secondary_color = "#D3D3D3"
saved_primary_color = "#D3D3D3"

send_status = 0
stop_cont_thread  = False
def open_config_window():
    print("test new pop up")
    config = Toplevel()
    config.title("Channel Configuration")
    config.geometry("750x500")
    
    button_frame = LabelFrame(config, text="buttons")
    button_frame.pack(fill="x", expand="yes", padx=20)
    send_button = Button(button_frame, text="Send Once", command = set_send)
    send_button.grid(row=1, column=0, padx=10, pady=10)

    config.wait_visibility()
    config.grab_set()
    config.transient()
    config.mainloop()
    
def rx_task():
    print('rx task stared')
    entries = 0
    while True:
                rc_ch = 0
                telegram_string = b''
                bytecount = 0
                while (not rc_ch == b'\r') and bytecount < 120:
                    rc_ch = ser.read()
                    if(not rc_ch == b'\r'):
                        telegram_string = telegram_string + rc_ch
                        bytecount+=1
                if bytecount > 50:
                    bytecount = 0
                
                print(telegram_string)
                if telegram_string[0] == 0x64:
                    if telegram_string[1] == 0x31: # d 1
                        if len(telegram_string) > 9:
                            chan1_status_var.set(chr(telegram_string[2]))
                            chan1_data_var.set(chr(telegram_string[3])+chr(telegram_string[4])+chr(telegram_string[5])+chr(telegram_string[6])+chr(telegram_string[7])+chr(telegram_string[8]))
                            #  telegram_string[3] telegram_string[4] telegram_string[5]
                            data = 0;
                            data = (int(chr(telegram_string[3]),16) <<8) + (int(chr(telegram_string[4]),16) <<4) + int(chr(telegram_string[3]),16) 
                            chan1_data_dec_var.set(data)
                            chan1_crc_var.set(chr(telegram_string[9]))
                        
                if telegram_string[0] == 0x64:
                    if telegram_string[1] == 0x32: # d 2
                        if len(telegram_string) > 9:
                            chan2_status_var.set(chr(telegram_string[2]))
                            chan2_data_var.set(chr(telegram_string[3])+chr(telegram_string[4])+chr(telegram_string[5])+chr(telegram_string[6])+chr(telegram_string[7])+chr(telegram_string[8]))
                            #  telegram_string[3] telegram_string[4] telegram_string[5]
                            data = 0;
                            data = (int(chr(telegram_string[3]),16) <<8) + (int(chr(telegram_string[4]),16) <<4) + int(chr(telegram_string[3]),16) 
                            chan2_data_dec_var.set(data)
                            chan2_crc_var.set(chr(telegram_string[9]))                    

                elif telegram_string[0] == 0x56: # V
                    status_var.set(telegram_string)
                elif telegram_string[0] == 0x76: # v
                    status_var.set(telegram_string)
                elif telegram_string[0] == 0x00: # 
                    status_var.set(telegram_string)
                elif telegram_string[0] == 0x45: # E
                    status_var.set(telegram_string)                    
                elif telegram_string[0] == 0x7a: # z
                    status_var.set(telegram_string)                 

def connect():
    try:
        #index = listbox_usb_ports.curselection()[0] 
        acm = '/dev/ttyS0'  # + listbox_usb_ports.get(index)
        print('port selected = ', acm)
        #ser.close()
        #ser = (serial.Serial(acm ,baudrate=9600,timeout=0.1,bytesize = 8, stopbits = 2,dsrdtr= False))
        ser.baudrate = 115200  
        ser.port = acm
        if ser.isOpen() == False:
            print('open port')
            ser.open()
            t = Thread(target = rx_task)
            t.start()
            time.sleep(0.1)
    
    except:
        print('can not open port')
    try:
        
        telegram_bin = bytearray()
        telegram_ascii_tx = b'V\r' 
        
        print('telegram_tx = ', telegram_ascii_tx)
        ser.write(telegram_ascii_tx)
        
        chan1_open_button['state'] = NORMAL
        chan1_close_button['state'] = NORMAL        
        chan1_set_tt_button['state'] = NORMAL  
        chan1_data_button['state'] = NORMAL  
        chan1_set_ft_button['state'] = NORMAL
        chan2_open_button['state'] = NORMAL
        chan2_close_button['state'] = NORMAL        
        chan2_set_tt_button['state'] = NORMAL  
        chan2_data_button['state'] = NORMAL  
        chan2_set_ft_button['state'] = NORMAL
       
    except:
        print('Can not start thread')

def chan1_sent_data():
 
    telegram_ascii_str = chan1_data.get()
    t=bytearray()
    t=b'd1'
    t=t+str.encode( telegram_ascii_str)   
    t=t+ b'\r'
    print('telegram_tx = ',t)
    ser.write(t)

def chan2_sent_data():
 
    telegram_ascii_str = chan2_data.get()
    t=bytearray()
    t=b'd2'
    t=t+str.encode( telegram_ascii_str)   
    t=t+ b'\r'
    print('telegram_tx = ',t)
    ser.write(t)
        
def set_send():

    telegram_ascii_str = strvar_command.get()
    t=bytearray()
    t=str.encode( telegram_ascii_str)   
    t=t+ b'\r'
    print('telegram_tx = ',telegram_ascii_str)
    ser.write(t)

def set_reset():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(mclr,GPIO.OUT)
    GPIO.output(mclr,False)
    time.sleep(0.1)
    GPIO.output(mclr,True)

def chan1_open():
    t=bytearray()
    index = radvar.get()
    print('index ',index)
    if index == 1:
        t=b'm1r\r'    # Receive mode for channel 1
    else:
        t=b'm1t\r'
    print('telegram_tx = ',t)
    ser.write(t)
    time.sleep(0.2)
    
    t=b'o1\r'
    print('telegram_tx = ',t)
    ser.write(t)
    chan1_set_tt_button['state'] = DISABLED  
    chan1_data_button['state'] = NORMAL  
    chan1_set_ft_button['state'] = DISABLED
    
def chan2_open():
    t=bytearray()
    index = radvar2.get()
    print('index ',index)
    if index == 1:
        t=b'm2r\r'    # Receive mode for channel 1
    else:
        t=b'm2t\r'
    print('telegram_tx = ',t)
    ser.write(t)
    time.sleep(0.2)
    
    t=b'o2\r'
    print('telegram_tx = ',t)
    ser.write(t)
    chan2_set_tt_button['state'] = DISABLED  
    chan2_data_button['state'] = NORMAL  
    chan2_set_ft_button['state'] = DISABLED    
    
def chan1_close():    
    t=bytearray()
    t=b'c1\r'
    print('telegram_tx = ',t)
    ser.write(t)
            
    chan1_set_tt_button['state'] = NORMAL  
    chan1_data_button['state'] = NORMAL  
    chan1_set_ft_button['state'] = NORMAL  

def chan2_close():    
    t=bytearray()
    t=b'c2\r'
    print('telegram_tx = ',t)
    ser.write(t)
            
    chan2_set_tt_button['state'] = NORMAL  
    chan2_data_button['state'] = NORMAL  
    chan2_set_ft_button['state'] = NORMAL     

def chan1_set_ft():
    ft=int(chkvar_1.get())
    if ft == 1:
        t=bytearray()
        t= b'p11\r'         
        print('telegram_tx = ',t)
        ser.write(t)
        time.sleep(0.1)
    else:
        t=bytearray()
        t= b'p10\r'         
        print('telegram_tx = ',t)
        ser.write(t)
        time.sleep(0.1)        
        
    try:
        interval_int=int(chan1_ft.get())
        print("Frame time {:d}".format(interval_int))
        if interval_int > 283 and interval_int <921:
            telegram_ascii_str = chan1_ft.get()
            t=bytearray()
            t= b'f1' 
            t= t+str.encode( telegram_ascii_str)   
            t = t+b'\r'
            print('telegram_tx = ',t)
            ser.write(t)
            
        else:
            status_var.set("Frame time must >283 and <921")
    except:
        status_var.set("Frame time must be a number")

def chan2_set_ft():
    ft=int(chkvar_2.get())
    if ft == 1:
        t=bytearray()
        t= b'p21\r'         
        print('telegram_tx = ',t)
        ser.write(t)
        time.sleep(0.1)
    else:
        t=bytearray()
        t= b'p20\r'         
        print('telegram_tx = ',t)
        ser.write(t)
        time.sleep(0.1)        
        
    try:
        interval_int=int(chan2_ft.get())
        print("Frame time {:d}".format(interval_int))
        if interval_int > 283 and interval_int <921:
            telegram_ascii_str = chan2_ft.get()
            t=bytearray()
            t= b'f2' 
            t= t+str.encode( telegram_ascii_str)   
            t = t+b'\r'
            print('telegram_tx = ',t)
            ser.write(t)
            
        else:
            status_var.set("Frame time must >283 and <921")
    except:
        status_var.set("Frame time must be a number")

def chan1_set_tt():
    try:
        interval_int=int(chan1_ticktime.get())
        print("interval {:d}".format(interval_int))
        if interval_int > 2 and interval_int <91:
            telegram_ascii_str = chan1_ticktime.get()
            t=bytearray()
            t= b't1' 
            if interval_int <10:
                t = t+b'0'
            t= t+str.encode( telegram_ascii_str)   
            t = t+b'\r'
            print('telegram_tx = ',t)
            ser.write(t)
            
        else:
            status_var.set("Tick time must >3 and <90us")
            
    except:
        status_var.set("Interval must be a number")

def chan2_set_tt():
    try:
        interval_int=int(chan2_ticktime.get())
        print("interval2 {:d}".format(interval_int))
        if interval_int > 2 and interval_int <91:
            telegram_ascii_str = chan1_ticktime.get()
            t=bytearray()
            t= b't2' 
            if interval_int <10:
                t = t+b'0'
            t= t+str.encode( telegram_ascii_str)   
            t = t+b'\r'
            print('telegram_tx = ',t)
            ser.write(t)
            
        else:
            status_var.set("Tick time must >3 and <90us")
            
    except:
        status_var.set("Interval must be a number")  
    
# Add Some Style
style = ttk.Style()

# Pick A Theme
style.theme_use('clam')
style.configure('Treeview.Heading',font =(None,8))
# Configure the Treeview Colors
style.configure("Treeview",
	background="#D3D3D3",
	foreground="black",
	rowheight=25,
	fieldbackground="#D3D3D3")

# Change Selected Color #347083
style.map('Treeview',
	background=[('selected', "#347083")])

# Define a Menu
my_menu = Menu(root)
root.config(menu=my_menu)
# Create Menu items
file_menu = Menu(my_menu)
my_menu.add_cascade(label="File",menu=file_menu)
file_menu.add_command(label="Exit",command=root.quit)
# Create another submenu


# Create Channel 1 Data Frame
chan1_status_var = StringVar()
chan1_status_var.set("0")
chan1_data_var = StringVar()
chan1_data_var.set("0")
chan1_data_dec_var = StringVar()
chan1_data_dec_var.set("0")
chan1_crc_var = StringVar()
chan1_crc_var.set("0")

chan1_frame = LabelFrame(root, text="Channel 1")
chan1_frame.pack(fill="x", expand="yes", padx=20)

chan1_status_lb = Label(chan1_frame, text="Status:")
chan1_status_lb.grid(row=0, column=0, padx=5, pady=10,sticky = 'W')

chan1_status = Label(chan1_frame, textvariable=chan1_status_var)
chan1_status.grid(row=0, column=1, padx=1, pady=10, sticky = 'W')

chan1_data_lb = Label(chan1_frame, text="Data:")
chan1_data_lb.grid(row=0, column=2, padx=1, pady=10, sticky = 'W')

chan1_data = Label(chan1_frame, textvariable=chan1_data_var)
chan1_data.grid(row=0, column=3, padx=1, pady=10, sticky = 'W')

chan1_data_dec = Label(chan1_frame, textvariable=chan1_data_dec_var)
chan1_data_dec.grid(row=0, column=4, pady=10, sticky = 'W')

chan1_crc_lb = Label(chan1_frame, text="CRC:")
chan1_crc_lb.grid(row=0, column=5, padx=1, pady=10, sticky = 'W')

chan1_crc = Label(chan1_frame, textvariable=chan1_crc_var)
chan1_crc.grid(row=0, column=6, padx=1, pady=10, sticky = 'W')
radvar = tk.IntVar()
rad_but_rx = tk.Radiobutton(chan1_frame,text = 'Rx',variable = radvar, value = 1) # Each radiobutton has
rad_but_tx = tk.Radiobutton(chan1_frame,text = 'Tx', variable = radvar, value = 2)       

rad_but_rx.select()   # Pre select Rx
rad_but_rx.grid(column = 0, row = 1, pady = 5,padx =1, sticky = 'W')
rad_but_tx.grid(column = 1, row = 1, pady = 5, sticky = 'W')
chan1_open_button = Button(chan1_frame,text = "Open Channel 1", command = chan1_open,state=DISABLED)
chan1_open_button.grid(row = 1, column = 3,padx=1,pady=10, sticky = 'W')
chan1_close_button = Button(chan1_frame,text = "Close Channel 1", command = chan1_close,state=DISABLED)
chan1_close_button.grid(row = 1, column = 4,padx=1,pady=10, sticky = 'W')

chkvar_1 = tk.IntVar()
chk_but_pause_pulse = ttk.Checkbutton(chan1_frame, text = 'Pause Pulse', variable = chkvar_1)
chk_but_pause_pulse.grid(row = 2, column = 0,padx =10, pady = 5, sticky = 'W')

chan1_pp_lb = Label(chan1_frame, text="Frame time (284 to 920):")
chan1_pp_lb.grid(row=2, column=1, padx=1, pady=10,sticky = 'E')

chan1_ft = tk.StringVar()
chan1_ft.set("284")
chan1_ticktime = tk.StringVar()
chan1_ticktime.set("3")
chan1_pause_entry = Entry(chan1_frame, width = 7, textvariable = chan1_ft)
chan1_pause_entry.grid(row=2, column=2, columnspan=1, padx=1, pady=10)


chan1_set_ft_button = Button(chan1_frame, text="Set Frame Time value", command = chan1_set_ft,state=DISABLED)
chan1_set_ft_button.grid(row=2, column=3, padx=1, pady=10,sticky = 'W')

chan1_ticktime_lb = Label(chan1_frame, text="Tick time (3 to 90us):")
chan1_ticktime_lb.grid(row=3, column=0,columnspan=2,padx=1,pady=10,sticky = 'E')
chan1_ticktime_entry = Entry(chan1_frame, width = 7,textvariable = chan1_ticktime)
chan1_ticktime_entry.grid(row=3, column=2, columnspan=1, padx=1, pady=10)
chan1_set_tt_button = Button(chan1_frame, text="Set Tick Time value", command = chan1_set_tt,state=DISABLED)
chan1_set_tt_button.grid(row=3, column=3, columnspan=1,padx=1,pady=10,sticky = 'W')

chan1_data = tk.StringVar()
chan1_data.set("f123456")
chan1_data_lb = Label(chan1_frame, text="Data: ")
chan1_data_lb.grid(row=4, columnspan=2,column=0,padx=1,pady=5,sticky = 'E')
chan1_data_entry = Entry(chan1_frame, width = 7,textvariable = chan1_data)
chan1_data_entry.grid(row=4,column=2,padx=1,pady=5)
chan1_data_button = Button(chan1_frame, text="Set Data value", command = chan1_sent_data,state=DISABLED)
chan1_data_button.grid(row=4,column=3,padx=1,pady=10,sticky = 'W')

# Create Channel 2 Data Frame
chan2_status_var = StringVar()
chan2_status_var.set("0")
chan2_data_var = StringVar()
chan2_data_var.set("0")
chan2_data_dec_var = StringVar()
chan2_data_dec_var.set("0")
chan2_crc_var = StringVar()
chan2_crc_var.set("0")

chan2_frame = LabelFrame(root, text="Channel 2")
chan2_frame.pack(fill="x", expand="yes", padx=20)

chan2_status_lb = Label(chan2_frame, text="Status:")
chan2_status_lb.grid(row=0, column=0, padx=5, pady=10,sticky = 'W')

chan2_status = Label(chan2_frame, textvariable=chan2_status_var)
chan2_status.grid(row=0, column=1, padx=1, pady=10, sticky = 'W')

chan2_data_lb = Label(chan2_frame, text="Data:")
chan2_data_lb.grid(row=0, column=2, padx=1, pady=10, sticky = 'W')

chan2_data = Label(chan2_frame, textvariable=chan2_data_var)
chan2_data.grid(row=0, column=3, padx=1, pady=10, sticky = 'W')

chan2_data_dec = Label(chan2_frame, textvariable=chan2_data_dec_var)
chan2_data_dec.grid(row=0, column=4, pady=10, sticky = 'W')

chan2_crc_lb = Label(chan2_frame, text="CRC:")
chan2_crc_lb.grid(row=0, column=5, padx=1, pady=10, sticky = 'W')

chan2_crc = Label(chan2_frame, textvariable=chan2_crc_var)
chan2_crc.grid(row=0, column=6, padx=1, pady=10, sticky = 'W')
radvar2 = tk.IntVar()
rad_but_rx2 = tk.Radiobutton(chan2_frame,text = 'Rx',variable = radvar2, value = 1) # Each radiobutton has
rad_but_tx2 = tk.Radiobutton(chan2_frame,text = 'Tx', variable = radvar2, value = 2)       

rad_but_rx2.select()   # Pre select Rx
rad_but_rx2.grid(column = 0, row = 1, pady = 5,padx =1, sticky = 'W')
rad_but_tx2.grid(column = 1, row = 1, pady = 5, sticky = 'W')
chan2_open_button = Button(chan2_frame,text = "Open Channel 1", command = chan2_open,state=DISABLED)
chan2_open_button.grid(row = 1, column = 3,padx=1,pady=10, sticky = 'W')
chan2_close_button = Button(chan2_frame,text = "Close Channel 1", command = chan2_close,state=DISABLED)
chan2_close_button.grid(row = 1, column = 4,padx=1,pady=10, sticky = 'W')

chkvar_2 = tk.IntVar()
chk_but_pause_pulse2 = ttk.Checkbutton(chan2_frame, text = 'Pause Pulse', variable = chkvar_2)
chk_but_pause_pulse2.grid(row = 2, column = 0,padx =10, pady = 5, sticky = 'W')

chan2_pp_lb = Label(chan2_frame, text="Frame time (284 to 920):")
chan2_pp_lb.grid(row=2, column=1, padx=1, pady=10,sticky = 'E')

chan2_ft = tk.StringVar()
chan2_ft.set("284")
chan2_ticktime = tk.StringVar()
chan2_ticktime.set("3")
chan2_pause_entry = Entry(chan2_frame, width = 7, textvariable = chan1_ft)
chan2_pause_entry.grid(row=2, column=2, columnspan=1, padx=1, pady=10)


chan2_set_ft_button = Button(chan2_frame, text="Set Frame Time value", command = chan2_set_ft,state=DISABLED)
chan2_set_ft_button.grid(row=2, column=3, padx=1, pady=10,sticky = 'W')

chan2_ticktime_lb = Label(chan2_frame, text="Tick time (3 to 90us):")
chan2_ticktime_lb.grid(row=3, column=0,columnspan=2,padx=1,pady=10,sticky = 'E')
chan2_ticktime_entry = Entry(chan2_frame, width = 7,textvariable = chan1_ticktime)
chan2_ticktime_entry.grid(row=3, column=2, columnspan=1, padx=1, pady=10)
chan2_set_tt_button = Button(chan2_frame, text="Set Tick Time value", command = chan2_set_tt,state=DISABLED)
chan2_set_tt_button.grid(row=3, column=3, columnspan=1,padx=1,pady=10,sticky = 'W')

chan2_data = tk.StringVar()
chan2_data.set("f123456")
chan2_data_lb = Label(chan2_frame, text="Data: ")
chan2_data_lb.grid(row=4, columnspan=2,column=0,padx=1,pady=5,sticky = 'E')
chan2_data_entry = Entry(chan2_frame, width = 7,textvariable = chan2_data)
chan2_data_entry.grid(row=4,column=2,padx=1,pady=5)
chan2_data_button = Button(chan2_frame, text="Set Data value", command = chan2_sent_data,state=DISABLED)
chan2_data_button.grid(row=4,column=3,padx=1,pady=10,sticky = 'W')


# End of channel 2

strvar_command = StringVar()
strvar_interval = StringVar()

# Commands frame
command_frame = LabelFrame(root, text="Commands")
command_frame.pack(fill="x", expand="yes", padx=20)

command_entry = Entry(command_frame, width = 32,textvariable = strvar_command)
command_entry.grid(row=0, column=0, columnspan=5, padx=10, pady=10)

send_button = Button(command_frame, text="Sent command", command = set_send)
send_button.grid(row=1, column=0, padx=10, pady=10)


# Buttons frame
button_frame = LabelFrame(root, text="Functions")
button_frame.pack(fill="x", expand="yes", padx=20)

connect_button = Button(button_frame, text="Connect",command = connect)
connect_button.grid(row=0, column=0, padx=10, pady=10)

add_button = Button(button_frame, text="Reset",command = set_reset)
add_button.grid(row=0, column=1, padx=10, pady=10)



remove_one_button = Button(button_frame, text="Test")
remove_one_button.grid(row=0, column=3, padx=10, pady=10)

# Status frame
status_frame = LabelFrame(root, text="Status")
status_frame.pack(fill="x", expand="yes", padx=20)

status_var = StringVar()
status_var.set("Ready to connect")

status_label = Label(status_frame, textvariable=status_var)
status_label.grid(row=0, column=0, padx=10, pady=10)

root.mainloop()