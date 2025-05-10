#Copyright © 2018 Naturalpoint
#
#Licensed under the Apache License, Version 2.0 (the "License")
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.


# OptiTrack NatNet direct depacketization sample for Python 3.x
#
# Uses the Python NatNetClient.py library to establish a connection (by creating a NatNetClient),
# and receive data via a NatNet connection and decode it using the NatNetClient library.

import sys
import time
import os
from contextlib import redirect_stdout

from app.OptiTrack.NatNetClient import *
import app.OptiTrack.DataDescriptions
import app.OptiTrack.MoCapData

from hardware.raspberry_pi.main import setOtData, move_to_endpoint

target_x = 0
target_y = 0

def setTarget(x, y):
    global target_x
    global target_y
    target_x = float(x)
    target_y = float(y)

# This is a callback function that gets connected to the NatNet client. It is called once per rigid body per frame
def receive_rigid_body_frame( new_id, position, rotation ):
    x, y, z = position
    if new_id == 429:
        setOtData(x, y, z, rotation)
        

def my_parse_args(arg_list, args_dict):
    # set up base values
    arg_list_len=len(arg_list)
    if arg_list_len>1:
        args_dict["serverAddress"] = arg_list[1]
        if arg_list_len>2:
            args_dict["clientAddress"] = arg_list[2]
        if arg_list_len>3:
            if len(arg_list[3]):
                args_dict["use_multicast"] = True
                if arg_list[3][0].upper() == "U":
                    args_dict["use_multicast"] = False

    return args_dict

# This is a callback function that gets connected to the NatNet client
# and called once per mocap frame.
def receive_new_frame(data_dict):
    pass

# start motion capture
def start():
    global target_x
    global target_y

    optionsDict = {}
    optionsDict["clientAddress"] = "192.168.1.234"
    optionsDict["serverAddress"] = "192.168.1.10"
    optionsDict["use_multicast"] = False

    # This will create a new NatNet client
    optionsDict = my_parse_args(sys.argv, optionsDict)

    streaming_client = NatNetClient()
    streaming_client.set_print_level(1)
    streaming_client.set_client_address(optionsDict["clientAddress"])
    streaming_client.set_server_address(optionsDict["serverAddress"])
    streaming_client.set_use_multicast(optionsDict["use_multicast"])

    # Configure the streaming client to call our rigid body handler on the emulator to send data out.
    streaming_client.new_frame_listener = receive_new_frame
    streaming_client.rigid_body_listener = receive_rigid_body_frame

    # Start up the streaming client now that the callbacks are set up.
    # This will run perpetually, and operate on a separate thread.
    streaming_client.set_print_level(0)
    # sys.stdout = open(os.devnull, 'w')
    is_running = streaming_client.run()
    # sys.stdout = sys.__stdout__
    if not is_running:
        print("ERROR: Could not start streaming client.")
        try:
            sys.exit(1)
        except SystemExit:
            print("...")
        finally:
            print("exiting")
    
    move_to_endpoint(target_x, target_y)
         
    # Check connection status
    while True:
        time.sleep(1)
        if streaming_client.connected() is False:
            print("ERROR: Could not connect properly.  Check that Motive streaming is on.")
            try:
                sys.exit(2)
            except SystemExit:
                print("...")
            finally:
                print("exiting")
