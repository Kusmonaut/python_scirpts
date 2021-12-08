"""
Diagnostics Decoder

Copyright (c) IntraNav GmbH, 2017-2023. All rights reserved.
Usage without permission or license is forbidden.
If you want to use this product or license it, as it, please contact us.
IntraNav GmbH, Germany, www.intranav.com, info@intranav.com
"""

import struct
from typing import Any, Dict, List, Optional
import logging

from config import (
    SOLVER_MIN_NUMBER_REPORTS
)

import numpy as np

PRF_CONSTANT = 121.74
DWT_BR_110K = 0 # 110 K
DWT_BR_850K = 1 # 850 K
DWT_BR_6M8 = 2  # 6180 K


def create_quality_report(
    diagnostics:Dict[str, Any], tag_id:int
    ) -> Optional[Dict[str, Any]]:
 
    node:dict = {"tag_id": tag_id}
    node["diag"] = diagnostics

    delta_peak = calc_peak_difference(diagnostics)

    if not delta_peak:
        return None

    node["delta"] = delta_peak

    pwr_level = calc_power_level(diagnostics)

    if not pwr_level:
        return None
    
    node["pwr_level"] = pwr_level

    pwr_level_delta = calc_power_level_delta(node["pwr_level"])

    if not pwr_level_delta:
        return None
        
    node["pwr_level"]["delta"] = pwr_level_delta

    if node["delta"] <= 3.3:
        node["prNlos"] = 0
    elif node["delta"] < 6 and node["delta"] > 3.3:       # TODO CREATE CONSTANTS FOR MAGIC NUMBERS
        node["prNlos"] = 0.39178 * node["delta"] - 1.31719
    else:
        node["prNlos"] = 1 

    return node

def decode_diagnostics(payload: bytes, node_id: int, tag_id: int) -> Optional[Dict[str, Any]]:
    # NOTE: diagnostics data format rev 5 (DWT_DIAGNOSTIC_LOG_REV)
    # 00-01 "header"
    # 01-05 "status"
    # 05-10 "rx_frame_info" -> bytewise 5 bytes
    #     | 0-6:   7 Bits (RXFLEN) Receive Frame Length
    #     | 7-9:   3 Bits (RXFLE) Receive Frame Length Extension
    #     | 10:    1 Bit Reserved
    #     | 11-12: 2 Bits (RXNSPL) Receive non-standard preamble length
    #     | 13-14: 2 Bits (RXBR) Receive Bit Rate report
    #     | 15:    1 Bit (RNG) Receiver Ranging
    #     | 16-17: 2 Bits (RXPRFR) RX Pulse Repetition Rate report
    #     | 18-19: 2 Bits (RXPSR) RX Preamble Repetition
    #     v 20-31:12 Bits (RXPACC) Preamble Accumulation Count
    # 10-12 "rx_fqual_std_noise"
    # 12-14 "fp_amp2"
    # 14-16 "fp_amp3"
    # 16-18 "rx_fqual_cir_pwr"
    # 18-22 "rx_time_tracking_interval"
    # 22-27 "rx_time_tracking_offset" -> bytewise 5 bytes
    #     | 0-18: 19 Bits (RXTOFS) RX time tracking offset
    #     | 24-31: 8 Bits (RSMPDEL) This 8-bit field reports an internal re-sampler delay value
    #     V 0-6:   7 Bits (RCPHASE) This 7-bit field reports the receive carrier phase adjustment
    # # 27-32 "rx_timestamp" -> bytewise 5 bytes
    # # 32-34 "fp_index"
    # 34-36 "fp_amp1"
    # 36-41 "raw_timestamp" -> bytewise 5 bytes
    # 41-43 "pp_index"
    # 43-47 "drxconf_unknown"
    # 47-49 "pp_ampl"
    # 49-51 "noise_threshold"
    # 51-193 "acc_memory" -> bytewise 142 bytes

    diag: Dict[str, Any] = {}
    diag["log"] = {"cir_real": [], "cir_imag": []}
    diag["cir_amplitude"] = []
    diag["raw_cir"] = []

    DIAG_READ_SUPPORT = "<BL5s4HL5s5sHh5sHHhH"
    DIAG_ACC_MEM = "<4047B"

    DIAG_HEADER_LENGTH = 49
    DIAG_LENGTH = 4096
    DWT_DIAGNOSTIC_LOG_REV_5 = 5

    if len(payload) == DIAG_LENGTH or len(payload) == DIAG_HEADER_LENGTH:
        # decode diagnostics
        (
            head,
            diag["status"],
            rx_frame_info,
            diag["rx_fqual_std_noise"],
            diag["fp_ampl2"],
            diag["fp_ampl3"],
            diag["rx_fqual_cir_pwr"],
            diag["rx_time_tracking_interval"],
            rx_time_tracking_offset,
            rx_timestamp,
            fp_index,
            diag["fp_ampl1"],
            raw_timestamp,
            diag["pp_index"],
            diag["rxpacc_nosat"],
            diag["pp_ampl"],
            diag["noise_threshold"]
        ) = struct.unpack(DIAG_READ_SUPPORT, payload[:DIAG_HEADER_LENGTH])

        # shift vaule to get corect fp_index without decimal space
        diag["fp_index"] = float(fp_index >> 6 & 0x03FF) + float(fp_index & 0x3F) / (0x3F + 0x01)

        diag["RXFLEN"] = int.from_bytes(rx_frame_info, "little") >> 8 & 0x7F
        diag["RXFLE"] = int.from_bytes(rx_frame_info, "little") >> 15 & 0x07
        diag["RXNSPL"] = int.from_bytes(rx_frame_info, "little") >> 19 & 0x03
        diag["RXBR"] = int.from_bytes(rx_frame_info, "little") >> 21 & 0x03
        diag["RNG"] = int.from_bytes(rx_frame_info, "little") >> 23 & 0x01
        diag["RXPRFR"] = int.from_bytes(rx_frame_info, "little") >> 24 & 0x03
        diag["RXPSR"] = int.from_bytes(rx_frame_info, "little") >> 26 & 0x03
        diag["RXPACC"] = int.from_bytes(rx_frame_info, "little") >> 28 & 0xFFF

        diag["RXTOFS"] = int.from_bytes(rx_time_tracking_offset, "little", signed=True) & 0x07FFFF
        diag["RSMPDEL"] = int.from_bytes(rx_time_tracking_offset, "little") >> 24 & 0xFF
        diag["RCPHASE"] = int.from_bytes(rx_time_tracking_offset, "little") >> 32 & 0x7F

        diag["rx_timestamp"] = int.from_bytes(rx_timestamp, "little")
        diag["raw_timestamp"] = int.from_bytes(raw_timestamp, "little")

        # check for diagnostics
        if head != DWT_DIAGNOSTIC_LOG_REV_5:
            logging.warning(f"decoding of diagnostics header faild. [node_id={node_id:016x}, tag_id={tag_id:016x}]")
            return None

        logging.debug(f"Diagnostics header decoded [node_id={node_id:016x}, tag_id={tag_id:016x}]")

        if len(payload) == DIAG_LENGTH:
            diag["raw_cir"] = struct.unpack(DIAG_ACC_MEM, payload[DIAG_HEADER_LENGTH:])

        # decode accumulator of diagnostics
        for i in range(1, len(diag["raw_cir"]), 4):
            if i > 1280:
                pass
                t = 23
            diag["log"]["cir_real"].append(int.from_bytes(diag["raw_cir"][i : i + 2], "little", signed=True))
            diag["log"]["cir_imag"].append(int.from_bytes(diag["raw_cir"][i + 2 : i + 4], "little", signed=True))
            diag["cir_amplitude"].append(
                max(abs(diag["log"]["cir_real"][-1]), abs(diag["log"]["cir_imag"][-1]))
                + 1 / 4 * min(abs(diag["log"]["cir_real"][-1]), abs(diag["log"]["cir_imag"][-1]))
            )
        return diag
    return None


def calc_power_level_delta(pwr_level: Dict[str, float]) -> float:
    # Using these two calculations it may be possible to say whether the channel
    # is line-of-sight (LOS) or non-line-of-sight signal (NLOS). As a rule of
    # thumb, if the difference between RX_POWER and FP_POWER,
    # i.e. RX_POWER – FP_POWER, is less than 6dB the channel is likely to be
    # LOS, whilst if the difference is greater than 10dB the channel is likely
    # to be NLOS.
    return abs(pwr_level["fp_power"] - pwr_level["rx_power"])


def get_idle_ref_node(nodes):
    
    idle_Node:int = None 
    to_kick:List = list()

    for uid in nodes:
        if nodes[uid]['prNlos'] < 1:                    # TODO CREATE CONSTANT FOR MAGIC NUMBERS
            if nodes[uid]['pwr_level']['delta'] < 10:   # TODO CREATE CONSTANT FOR MAGIC NUMBERS

                if not idle_Node:
                    idle_Node = uid
                    continue

                if nodes[uid]['prNlos'] < nodes[idle_Node]['prNlos']:
                    idle_Node = uid
                else:
                    if nodes[uid]['pwr_level']['delta'] < nodes[idle_Node]['pwr_level']['delta']:
                        idle_Node = uid
            else:
                if len(nodes) - len(to_kick) > SOLVER_MIN_NUMBER_REPORTS:
                    to_kick.append(uid)
        else:
            if len(nodes) - len(to_kick) > SOLVER_MIN_NUMBER_REPORTS:
                to_kick.append(uid)

    return idle_Node, to_kick

def calc_peak_difference(
    diagnostics:Dict[str, float]
) -> Optional[float] :

    rc:float = float()

    if "fp_index" not in diagnostics:
        return None
    if "pp_index" not in diagnostics:
        return None

    rc = diagnostics["pp_index"] - diagnostics["fp_index"]

    return rc


def calc_power_level(diagnostics: dict) -> Optional[Dict[str, float]]:
    try:
        if diagnostics["RXPACC"] == diagnostics["rxpacc_nosat"]:
            if (diagnostics["RXBR"] == DWT_BR_110K):
                diagnostics["RXPACC"] -= 10
            elif (diagnostics["RXBR"] == DWT_BR_850K):
                diagnostics["RXPACC"] -= 18
            elif (diagnostics["RXBR"] == DWT_BR_6M8):
                diagnostics["RXPACC"] -= 82


        # TODO catch division by zero. Curently it ist the smartest solution I found
        if diagnostics["RXPACC"] == 0:
            diagnostics["RXPACC"] = 0.00001

        # calc first path power level
        # F_1 = First Path Amplitude (point 1) magnitude value reprted in the FP_AMPL1
        # F_2 = First Path Amplitude (point 2) magnitude value reprted in the FP_AMPL2
        # F_3 = First Path Amplitude (point 3) magnitude value reprted in the FP_AMPL3
        # A = constant 121.74 for a PRF of 64 MHz
        # N = the Preamble Accumulation Count value reported in the RXPACC
        # 10 * log( F_1^2 + F_2^2 + F_3^2 / N^2) - A dBm
        first_path_power_levle = (
            10
            * np.log10(
                (diagnostics["fp_ampl1"] ** 2 + diagnostics["fp_ampl2"] ** 2 + diagnostics["fp_ampl3"] ** 2)
                / diagnostics["RXPACC"] ** 2
            )
            - PRF_CONSTANT
        )
        # calculate estimate of the receive power level (in dBm)
        # C = the Channel Impulse Response Power value reported in the CIR_PWR
        # A = constant 121.74 for a PRF of 64 MHz
        # N = the Preamble Accumulation Count value reported in the RXPACC
        receive_power_lelvel = (
            10 * np.log10((diagnostics["rx_fqual_cir_pwr"] * 2 ** 17) / diagnostics["RXPACC"] ** 2) - PRF_CONSTANT
        )
        return {
            "fp_power": first_path_power_levle,
            "rx_power": receive_power_lelvel,
        }
    except:
        return None
