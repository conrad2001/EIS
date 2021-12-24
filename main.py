"""setup and measure data from Analog Discovery Kit 2.
"""

import os
import logging
import win32com.client
from contextlib import suppress
from pathlib import Path
import time
from datetime import datetime
from tqdm import trange
from AnalogMux import AnalogMux

from DUT import DUT
from SerialComm import SerialComm

import json5 as json

def main():

    main_path = r"C:\Users\User01\Desktop\EIS\Cal Poly\EIS Team - MSMT_data"

    with open('configuration.json') as f:
        json_f = json.load(f)
    DUT_info = json_f['DUT_info']
    MSMT_param = json_f['MSMT_param']
    DUTs = []
    interval = 10  # interval between measurements in seconds
    total_seconds = 60
    start_time = time.time()
    current_time = time.time()
    log_folder = os.path.join(main_path, 'log_file', f'{datetime.now():%m_%d_%Y}')
    Path(log_folder).mkdir(parents=True, exist_ok=True)
    log_file = os.path.join(log_folder, f'{datetime.now():%m_%d_%H_%M_%Y}.log')
    shortcut = os.path.join(main_path, 'measurement status.lnk')
    logging.basicConfig(format='%(asctime)-8s - %(levelname)-8s: %(message)s', filename = log_file, level=logging.INFO)
    create_shortcut(log_file, shortcut)
    logging.info('Program begins')
    ## setup serial communication with microcontroller
    ser = SerialComm(auto_connect=True)

    mux = AnalogMux(MSMT_param, ser) # create mux instance and measure open cirucit impedance
    
    for channel, info in DUT_info.items():    # create DUT instances
        DUTs.append(DUT(MSMT_param, channel, info, main_path, mux))

    

    ## measure impedance of each DUT within the total measurement time
    while current_time - start_time < total_seconds:
        logging.info(f'measurment time left: {total_seconds - current_time + start_time}s')
        print(current_time - start_time)
        for _DUT in DUTs:
            mux.switch_channel(_DUT.channel)
            _DUT.Measure_Impedance()
            _DUT.Generate_Report()
        print('waiting for next measurement')
        ## delay with progress bar
        for _ in trange(interval):
            time.sleep(1)
        current_time = time.time()
    

    
    ## generate Summary file for each DUT
    for _DUT in DUTs:
        _DUT.Generate_Summary()
        
    logging.info('Program Finished')

    ## remove shortcut
    with suppress(FileNotFoundError):
        os.remove(shortcut)
    
    
def create_shortcut(root_file, output_path):
    '''create shortcut of the root file
    output_path: path of the shortcut file
    root_file: location of the root file
    '''
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(output_path)
    shortcut.Targetpath = root_file
    shortcut.IconLocation = root_file
    shortcut.save()


if __name__ == '__main__':

    main()

