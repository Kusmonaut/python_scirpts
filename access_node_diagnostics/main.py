
import json
import logging
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import struct

from paho.mqtt.client import Client as MQTTClient, MQTTMessage
from libscrc import kermit

from config import (
    ACC_HEAD,
    ACC_DATA,
    ACC_LOG,
    FRAME_DATA_IDX,
    MQTT_HOST,
    MQTT_PASS,
    MQTT_PORT,
    MQTT_USER,
    FRAME_HEADER_LEN,
    STX,
    ETX,
    ACCESS_ACCUMULATOR_MEMORY,
    FRAME_DATA_IDX,
    RTLS_LOG_ACCUMULATOR_IND,
)
acc_head_keys = ["rtlsCmd", "type", "seqNum", "logNum", "tagId"]
acc_data_keys = ["fpIndex", "maxNoise", "firstPathAmp1", "stdNoise", "firstPathAmp2", "firstPathAmp3", "maxGrowthCIR", "rxPreamCount", "ppIndex", "peakPathAmp", ]

dlAccumulatorLog = { } 
{"acc_data": { "real": [], "imag": [] }}
def handle_accumulator_log(rxBytes, length):
    # dlAccumulatorLog["rtlsCmd"], dlAccumulatorLog["type"], dlAccumulatorLog["seqNum"], dlAccumulatorLog["logNum"], dlAccumulatorLog["tagId"] = struct.unpack('<BBBIQ', rxBytes[:ACC_HEAD])
    # dlAccumulatorLog["fpIndex"], dlAccumulatorLog["maxNoise"], dlAccumulatorLog["firstPathAmp1"], dlAccumulatorLog["stdNoise"], dlAccumulatorLog["firstPathAmp2"], dlAccumulatorLog["firstPathAmp3"], dlAccumulatorLog["maxGrowthCIR"], dlAccumulatorLog["rxPreamCount"],dlAccumulatorLog["ppIndex"], dlAccumulatorLog["peakPathAmp"] = 
    dlAccumulatorLog.update(dict(zip(acc_head_keys ,struct.unpack('<BBBIQ', rxBytes[:ACC_HEAD]))))
    dlAccumulatorLog.update(dict(zip(acc_data_keys ,struct.unpack('<HhhhhhHHHh', rxBytes[ACC_HEAD:ACC_HEAD+ACC_DATA]))))
    
    dlAccumulatorLog["log"] = { "real": [], "imag": [] }
    dlAccumulatorLog["amplitude"] = []

    accumlated_memory = rxBytes[ACC_HEAD + ACC_DATA : ACC_HEAD + ACC_DATA + ACC_LOG]
    test = len(rxBytes)

    # begin reading from array at index 1. Ignore value at index 0
    for i in range(1, len(accumlated_memory), 4):
        dlAccumulatorLog["log"]["real"].append(int.from_bytes(accumlated_memory[i:i+2], "little", signed=True))
        dlAccumulatorLog["log"]["imag"].append(int.from_bytes(accumlated_memory[i+2:i+4], "little", signed=True))
        dlAccumulatorLog["amplitude"].append(max(abs(dlAccumulatorLog["log"]["real"][-1]), abs(dlAccumulatorLog["log"]["imag"][-1])) + 1/4*min(abs(dlAccumulatorLog["log"]["real"][-1]), abs(dlAccumulatorLog["log"]["imag"][-1])))
        # dlAccumulatorLog["amplitude"].append(np.sqrt(dlAccumulatorLog["log"]["real"][-1]*dlAccumulatorLog["log"]["real"][-1] + dlAccumulatorLog["log"]["imag"][-1]*dlAccumulatorLog["log"]["imag"][-1]))

    print(str(hex(dlAccumulatorLog["tagId"])))
    if 405993332951747092 == dlAccumulatorLog["tagId"]:
        
        print(f'maxNoise: {dlAccumulatorLog["maxNoise"]}')
        print(f'fpIndex: {(dlAccumulatorLog["fpIndex"]>>6)+(dlAccumulatorLog["fpIndex"]&0x3F)/1000}')
        print(f'firstPathAmp1: {dlAccumulatorLog["firstPathAmp1"]}')
        print(f'firstPathAmp2: {dlAccumulatorLog["firstPathAmp2"]}')
        print(f'firstPathAmp3: {dlAccumulatorLog["firstPathAmp3"]}')
        
        plt.title("tag_ID : " + str(hex(dlAccumulatorLog["tagId"])))
        plt.plot(dlAccumulatorLog["amplitude"])
        plt.ylabel('Channel Impulse Response Amplitude')
        plt.xlabel('Sample Index')
        plt.scatter( [(dlAccumulatorLog["fpIndex"]>>6)+ 1, (dlAccumulatorLog["fpIndex"]>>6)+ 2, (dlAccumulatorLog["fpIndex"]>>6)+ 3 ], [dlAccumulatorLog["firstPathAmp3"],
            dlAccumulatorLog["firstPathAmp2"], dlAccumulatorLog["firstPathAmp1"]], marker='x')
        plt.scatter( dlAccumulatorLog["ppIndex"], dlAccumulatorLog["peakPathAmp"], marker='x', color='r')
        plt.axhline(y=dlAccumulatorLog["maxNoise"], color='blue', linestyle='--')
        fp_index = float(dlAccumulatorLog["fpIndex"]>>6)+float((dlAccumulatorLog["fpIndex"]&0x3F)/1000)
        plt.axvline(x=fp_index, color='red')
        plt.show()

def on_connect(client: MQTTClient, userdata, flags, rc, properties=None):
    logging.debug("Connected to MQTT")

    client.subscribe("node/01aa2145ca141c2d/tdoa")
    client.message_callback_add("node/01aa2145ca141c2d/tdoa", on_tdoa)

def on_tdoa(client: MQTTClient, userdata, msg: MQTTMessage, properties=None):

    data = msg.payload
    length = len(data)

    
    # the data coming from the anchor is framed:
    # <STX><LENlsb><LENmsb><DATA:<FC><XX>.....><CRClsb><CRCmsb><ETX>
    # STX = 0x2
    # LEN is the length of data message(16 bits)
    # CRC is the 16 - bit CRC of the data bytes
    # ETX = 0x3
    # FC = is the function code (API code)
    
    if data[0] == STX:
        hi = data[2]
        lo = data[1]

        flen = lo + (hi << 8)

        if flen + FRAME_HEADER_LEN > length:
            return

        if data[flen + 5] == ETX:
            paylod_crc_Hi = data[-2]
            paylod_crc_Lo = data[-3]
            crc_sum = kermit(data[3:-3])
            calc_crc_hi = crc_sum >> 8 & 0xFF
            calc_crc_low = crc_sum & 0xFF
        else:
            return
    else:
        return
    if (((flen + FRAME_HEADER_LEN) > length) or (length <= FRAME_HEADER_LEN)):
        return
    if (paylod_crc_Hi == calc_crc_hi) and (paylod_crc_Lo == calc_crc_low):
        fcode = data[FRAME_DATA_IDX]
        if fcode == RTLS_LOG_ACCUMULATOR_IND:
            handle_accumulator_log(data[3:-3], flen)
    else:
        return
   

if __name__ == "__main__":
    mqtt_client = MQTTClient()
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
    mqtt_client.on_connect = on_connect

    mqtt_client.connect(MQTT_HOST, MQTT_PORT)

    mqtt_client.publish("node/01aa2145ca141c2d/cmd", json.dumps(ACCESS_ACCUMULATOR_MEMORY))

    mqtt_client.loop_forever()