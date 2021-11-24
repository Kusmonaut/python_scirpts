import struct
import logging
from collections import OrderedDict, defaultdict
from typing import Any, Dict, Optional

import numpy as np

PRF_CONSTANT = 121.74


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
    # 51-66/51-193 "acc_memory" -> bytewise 14-142 bytes

    diag: Dict[str, Any] = {}
    diag["log"] = {"cir_real": [], "cir_imag": []}
    diag["cir_amplitude"] = []
    diag["raw_cir"] = []

    DIAG_READ_SUPPORT = "<BL5s4hL5s5sHh5sHLhH"
    DIAG_ACC_MEM = "<143B"

    DIAG_HEADER_LENGTH = 51
    DIAG_LENGTH = 194
    DWT_DIAGNOSTIC_LOG_REV_5 = 5

    if len(payload) == DIAG_LENGTH:
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
            carrier_recovery_integrator,
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
        diag["RXPACC"] = int.from_bytes(rx_frame_info, "little") >> 28 & 0x1FFF

        diag["RXTOFS"] = int.from_bytes(rx_time_tracking_offset, "little", signed=True) & 0x07FFFF
        diag["RSMPDEL"] = int.from_bytes(rx_time_tracking_offset, "little") >> 24 & 0xFF
        diag["RCPHASE"] = int.from_bytes(rx_time_tracking_offset, "little") >> 32 & 0x7F

        diag["rx_timestamp"] = int.from_bytes(rx_timestamp, "little")
        diag["raw_timestamp"] = int.from_bytes(raw_timestamp, "little")

        diag["drx_carr_int"] = float(carrier_recovery_integrator >> 17 & 0x0F) + float(
            carrier_recovery_integrator & 0x1FFFF
        ) / (0x1FFFF + 0x01)

        # check for diagnostics
        if head != DWT_DIAGNOSTIC_LOG_REV_5:
            logging.warning(f"decoding of diagnostics header faild. [node_id: {node_id:016x}, tag_id: {tag_id:016x}]")
            return None

        logging.info(f"diagnostics header decoded. [node_id: {node_id:016x}, tag_id: {tag_id:016x}]")

        if len(payload) == DIAG_LENGTH:
            diag["raw_cir"] = struct.unpack(DIAG_ACC_MEM, payload[DIAG_HEADER_LENGTH:])

        # decode accumulator of diagnostics
        for i in range(1, len(diag["raw_cir"]), 4):
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


def get_best_node(node_quality, tag_id):

    # sort the node id due to the delta
    sorted_nodes = dict(OrderedDict(sorted(node_quality.items(), key=lambda t: t[1])))

    nodes = list(sorted_nodes.keys())[:]

    for n in nodes:
        logging.info(f"node_id: {n}, quality_index: {sorted_nodes[n]}")

    logging.debug(f"tag_id : {tag_id}")

    # return the node with the smalest delta
    return list(sorted_nodes.keys())[0]


def calc_peak_difference(diagnostics):

    if "fp_index" not in diagnostics:
        return None
    if "pp_index" not in diagnostics:
        return None

    rc = diagnostics["pp_index"] - diagnostics["fp_index"]

    return rc


def get_qualified_node(power_level: dict) -> int:
    delta = {}

    # calculate the difference between the first path power level and receive singal power.
    # The smaler the difference, the higher the chance that the connection between node and tag
    # is line of sight.
    for node_uid in power_level:
        delta[node_uid] = float(np.abs(power_level[node_uid]["fp_power"] - power_level[node_uid]["rx_power"]))

    # sort the node id due to the delta
    sorted_nodes = dict(OrderedDict(sorted(delta.items(), key=lambda t: t[1])))

    # return the node with the smalest delta
    return list(sorted_nodes.keys())[0]


def calc_power_level(diagnostics: dict) -> Optional[Dict[str, float]]:
    try:
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
