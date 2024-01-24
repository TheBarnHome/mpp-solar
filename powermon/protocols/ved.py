""" protocols / ved.py """
import logging
from enum import Enum
# from typing import Tuple
from struct import unpack

from mppsolar.protocols.protocol_helpers import vedHexChecksum
from powermon.commands.command_definition import CommandDefinition
from powermon.commands.reading_definition import ReadingType, ResponseType
from powermon.commands.result import ResultType
from powermon.errors import CommandError
from powermon.protocols.abstractprotocol import AbstractProtocol

# from .pi30 import COMMANDS

log = logging.getLogger("ved")


class VictronCommandType(Enum):
    """ enum of valid types of Results """
    PING = 1
    GET_FW = 3
    GET_ID = 4
    RESTART = 6
    GET = 7
    SET = 8
    ASYNC = 'A'
    LISTEN = 'L'


COMMANDS = {
    "vedtext": {
        "name": "vedtext",
        "description": "VE Direct Text",
        "help": " -- the output of the VE Direct text protocol",
        "device_command_type": VictronCommandType.LISTEN,
        "result_type": ResultType.VED_INDEXED,
        "reading_definitions": [
            {"index": "V", "description": "Main or channel 1 battery voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "V2", "description": "Channel 2 battery voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "V3", "description": "Channel 3 battery voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "VS", "description": "Auxiliary starter voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "VM", "description": "Mid-point voltage of the battery bank", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "DM", "description": "Mid-point deviation of the battery bank", "reading_type": ReadingType.PERCENTAGE, "response_type": ResponseType.FLOAT},
            {"index": "VPV", "description": "Panel voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "PPV", "description": "Panel power", "reading_type": ReadingType.WATTS, "response_type": ResponseType.FLOAT},
            {"index": "I", "description": "Main or channel 1 battery current", "reading_type": ReadingType.CURRENT, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "I2", "description": "Channel 2 battery current", "reading_type": ReadingType.CURRENT, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "I3", "description": "Channel 3 battery current", "reading_type": ReadingType.CURRENT, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "IL", "description": "Load current", "reading_type": ReadingType.CURRENT, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "LOAD", "description": "Load output state ON/OFF", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.BYTES},
            {"index": "T", "description": "Battery temperature", "reading_type": ReadingType.TEMPERATURE, "response_type": ResponseType.FLOAT},
            {"index": "P", "description": "Instantaneous power", "reading_type": ReadingType.WATTS, "response_type": ResponseType.FLOAT},
            {"index": "CE", "description": "Consumed Amp Hours", "reading_type": ReadingType.ENERGY, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "SOC", "description": "State-of-charge", "reading_type": ReadingType.PERCENTAGE, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/10"},
            {"index": "TTG", "description": "Time-to-go", "reading_type": ReadingType.TIME_MINUTES, "response_type": ResponseType.FLOAT},
            {"index": "Alarm", "description": "Alarm condition active", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.STRING},
            {"index": "Relay", "description": "Relay state", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.STRING},
            {"index": "AR", "description": "Alarm reason", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.STRING},
            {"index": "OR", "description": "Off reason", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.STRING},
            {"index": "H1", "description": "Depth of the deepest discharge", "reading_type": ReadingType.ENERGY, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "H2", "description": "Depth of the last discharge", "reading_type": ReadingType.ENERGY, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "H3", "description": "Depth of the average discharge", "reading_type": ReadingType.ENERGY, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "H4", "description": "Number of charge cycles", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.INT},
            {"index": "H5", "description": "Number of full discharges", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.INT},
            {"index": "H6", "description": "Cumulative Amp Hours drawn", "reading_type": ReadingType.ENERGY, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "H7", "description": "Minimum main battery voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "H8", "description": "Maximum main battery voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "H9", "description": "Number of seconds since last full charge", "reading_type": ReadingType.TIME_SECONDS, "response_type": ResponseType.FLOAT},
            {"index": "H10", "description": "Number of automatic synchronizations", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.INT},
            {"index": "H11", "description": "Number of low main voltage alarms", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.INT},
            {"index": "H12", "description": "Number of high main voltage alarms", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.INT},
            {"index": "H13", "description": "Number of low auxiliary voltage alarms", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.INT},
            {"index": "H14", "description": "Number of high auxiliary voltage alarms", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.INT},
            {"index": "H15", "description": "Minimum auxiliary battery voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "H16", "description": "Maximum auxiliary battery voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/1000"},
            {"index": "H17", "description": "Amount of discharged energy", "reading_type": ReadingType.KILOWATT_HOURS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/100"},
            {"index": "H18", "description": "Amount of charged energy", "reading_type": ReadingType.KILOWATT_HOURS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/100"},
            {"index": "H19", "description": "Yield total - user resettable counter", "reading_type": ReadingType.KILOWATT_HOURS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/100"},
            {"index": "H20", "description": "Yield today", "reading_type": ReadingType.KILOWATT_HOURS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/100"},
            {"index": "H21", "description": "Maximum power today", "reading_type": ReadingType.WATTS, "response_type": ResponseType.FLOAT},
            {"index": "H22", "description": "Yield yesterday", "reading_type": ReadingType.KILOWATT_HOURS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/100"},
            {"index": "H23", "description": "Maximum power yesterday", "reading_type": ReadingType.WATTS, "response_type": ResponseType.FLOAT},
            {"index": "ERR", "description": "Error code", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.STRING},
            {"index": "CS", "description": "State of operation", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.STRING},
            {"index": "BMV", "description": "Model description", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.STRING},
            {"index": "FW", "description": "Firmware version 16 bit", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.STRING},
            {"index": "FWE", "description": "Firmware version 24 bit", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.STRING},
            {"index": "PID", "description": "Product ID", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.STRING},
            {"index": "SER#", "description": "Serial number", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.STRING},
            {"index": "HSDS", "description": "Day sequence number 0..364", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.STRING},
            {"index": "MODE", "description": "Device mode", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.STRING},
            {"index": "AC_OUT_V", "description": "AC output voltage", "reading_type": ReadingType.VOLTS, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r*100"},
            {"index": "AC_OUT_I", "description": "AC output current", "reading_type": ReadingType.CURRENT, "response_type": ResponseType.TEMPLATE_INT, "format_template": "r/10"},
            {"index": "AC_OUT_S", "description": "AC output apparent power", "reading_type": ReadingType.APPARENT_POWER, "response_type": ResponseType.FLOAT},
            {"index": "WARN", "description": "Warning reason", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.STRING},
            {"index": "MPPT", "description": "Tracker operation mode", "reading_type": ReadingType.MESSAGE, "response_type": ResponseType.STRING},
            {"index": "Checksum", "description": "Checksum", "reading_type": ReadingType.HEX_STR, "response_type": ResponseType.HEX_CHAR},
        ],
        "test_responses": [
            b"H1\t-32914\r\nH2\t0\r\nH3\t0\r\nH4\t0\r\nH5\t0\r\nH6\t-35652\r\nH7\t12041\r\nH8\t14282\r\nH9\t0\r\nH10\t0\r\nH11\t0\r\nH12\t0\r\nH15\t-22\r\nH16\t0\r\nH17\t46\r\nH18\t48\r\nChecksum\t\x1a\r\nPID\t0xA389\r\nV\t12865\r\nVS\t-14\r\nI\t0\r\nP\t0\r\nCE\t0\r\nSOC\t1000\r\nTTG\t-1\r\nAlarm\tOFF\r\nAR\t0\r\nBMV\tSmartShunt 500A/50mV\r\nFW\t0405\r\nChecksum\tL\r\n",
            b"\x00L\r\nH1\t-32914\r\nH2\t0\r\nH3\t0\r\nH4\t0\r\nH5\t0\r\nH6\t-35652\r\nH7\t12041\r\nH8\t14282\r\nH9\t0\r\nH10\t0\r\nH11\t0\r\nH12\t0\r\nH15\t-22\r\nH16\t0\r\nH17\t46\r\nH18\t48\r\nChecksum\t\x1a\r\nPID\t0xA389\r\nV\t12868\r\nVS\t-12\r\nI\t0\r\nP\t0\r\nCE\t0\r\nSOC\t1000\r\nTTG\t-1\r\nAlarm\tOFF\r\nAR\t0\r\nBMV\tSmartShunt 500A/50mV\r\nFW\t0405\r\nChecksum\tK\r",
            b"\nH1\t-32914\r\nH2\t0\r\nH3\t0\r\nH4\t0\r\nH5\t0\r\nH6\t-35652\r\nH7\t12041\r\nH8\t14282\r\nH9\t0\r\nH10\t0\r\nH11\t0\r\nH12\t0\r\nH15\t-22\r\nH16\t0\r\nH17\t46\r\nH18\t48\r\nChecksum\t\x1a\r\nPID\t0xA389\r\nV\t12868\r\nVS\t-13\r\nI\t0\r\nP\t0\r\nCE\t0\r\nSOC\t1000\r\nTTG\t-1\r\nAlarm\tOFF\r\nAR\t0\r\nBMV\tSmartShunt 500A/50mV\r\nFW\t0405\r\nChecksum\tJ\r",
        ],
    },
    "batteryCapacity": {
        "name": "batteryCapacity",
        "description": "Battery Capacity",
        "help": " -- display the Battery Capacity",
        "device_command_type": VictronCommandType.GET,
        "device_command_code": "1000",  # or should be the more accurate 1000
        "result_type": ResultType.SLICED,
        "reading_definitions": [
            {"description": "Command type", "slice": [0, 1],
                "reading_type": ReadingType.MESSAGE,
                "response_type": ResponseType.INT},
            {"description": "Command", "slice": [1, 5],
                "reading_type": ReadingType.HEX_STR,
                "response_type": ResponseType.LE_2B_S},
            {"description": "Command response flag", "slice": [5, 7],
                "reading_type": ReadingType.MESSAGE,
                "response_type": ResponseType.OPTION,
                "options": {"00": "OK",
                            "01": "Unknown ID",
                            "02": "Not supported",
                            "04": "Parameter Error"}},
            {"description": "Battery Capacity", "slice": [7, 11],
                "reading_type": ReadingType.ENERGY,
                "response_type": ResponseType.LE_2B_S},
        ],
        "test_responses": [
            b":70010007800C6\n",
            b"\x00\x1a:70010007800C6\n",
        ],
    },
}


class VictronEnergyDirect(AbstractProtocol):
    """
    VictronEnergyDirect - VEDirect protocol handler
    """

    def __str__(self):
        return "VED protocol handler for Victron direct SmartShunts"

    def __init__(self) -> None:
        super().__init__()
        self.protocol_id = b"VED"
        self.add_command_definitions(COMMANDS)
        self.STATUS_COMMANDS = [
            "vedtext",
        ]
        self.SETTINGS_COMMANDS = [
            "",
        ]
        self.DEFAULT_COMMAND = "vedtext"
        # self._command_definition = None
        self.check_definitions_count(expected=2)

    def get_full_command(self, command) -> bytes:
        """
        Override the default get_full_command as its different for VEDirect
        """
        log.info("Using protocol %s with %i commands", self.protocol_id, len(self.command_definitions))

        command_definition : CommandDefinition = self.get_command_definition(command)
        if command_definition is None:
            return None

        # VEDHEX
        # : start of command
        # 7 Get
        # 0000 id of the value to get
        # 00 flags
        # 00 cs
        # \n
        # eg b':70010003E\n' = get battery capacity id = 0x1000 = 0010 little endian

        # if cmd_type == "VEDTEXT":
        #     # Just listen - dont need to send a command
        #     log.debug("command is VEDTEXT type so returning %s", cmd_type)
        #     return cmd_type

        command_type = command_definition.device_command_type
        match command_type:
            case VictronCommandType.GET:
                # command components
                raw_command_code = command_definition.device_command_code  # eg 1000 for batteryCapacity
                command_code = f"{unpack('<h', bytes.fromhex(raw_command_code))[0]:04X}"
                flags = "00"

                # build command
                cmd = f"{command_type.value}{command_code}{flags}"
                # pad cmd and convert to bytes and determine checksum
                checksum = vedHexChecksum(bytes.fromhex(f"0{cmd}"))

                # build full command
                cmd = f":{cmd}{checksum:02X}\n"
                log.debug("full command: %s", cmd)
                return cmd
            case VictronCommandType.LISTEN:
                # Just listen - dont need to send a command
                log.debug("command is LISTENT type so returning %s", command_type)
                return command_type
        raise CommandError(f"unable to generate full command for {command}, type {command_type} - is the definition wrong or CommandType not implemented?")

    # def check_valid(self, response: str) -> bool: - not needed, use superclass

    def check_crc(self, response: str) -> bool:
        """ crc check, needs override in protocol """
        log.debug("no check crc for %s", response)
        return True

    def trim_response(self, response: str) -> str:
        """ Remove extra characters from response """
        log.debug("response: %s", response)
        if b":" in response:
            # HEX response, e.g. b":70010007800C6\n"
            _ret = response.split(b":")[1][:-3]
        else:
            # VEDTEXT response, return the lot
            _ret = response
        # _ret = _ret.encode()
        log.debug("trim_response: %s", _ret)
        return _ret

    # def check_response_and_trim(self, response) -> Tuple[bool, dict]:
    #     """
    #     VED HEX protocol - sum of bytes should be 0x55
    #     VED Text protocol - no validity check
    #     """
    #     if not response:
    #         return False, {"validity check": ["Error: Response was empty", ""]}
    #     if b":" in response:
    #         # HEX protocol response
    #         log.debug("checking validity of '%s'", response)
    #         _r = response.split(b":")[1][:-1].decode()
    #         # print(f"trimmed response {_r}")
    #         _r = f"0{_r}"
    #         # print(f"padded response {_r}")
    #         _r = bytes.fromhex(_r)
    #         # print(f"bytes response {_r}")
    #         data = _r[:-1]
    #         checksum = _r[-1:][0]
    #         if vedHexChecksum(data) == checksum:
    #             log.debug("VED Hex Checksum matches in response '%s' checksum:'%s'", response, checksum)
    #             return True, {}
    #         else:
    #             # print("VED Hex Checksum does not match")
    #             return False, {
    #                 "validity check": [
    #                     f"Error: VED HEX checksum did not match for response {response}",
    #                     "",
    #                 ]
    #             }
    #     else:
    #         return True, {}

    # def get_responses(self, response):
    #     """
    #     Override the default get_responses as its different for PI00
    #     """
    #     # remove \n
    #     response = response.replace(b"\n", b"")
    #     responses = []
    #     # for hex protocol responses - these contain a :
    #     if b":" in response:
    #         # trim anything before ':'
    #         _r = response.split(b":")[1].decode()
    #         # pad command (which is single char)
    #         _r = f"0{_r}"
    #         _r = bytes.fromhex(_r)
    #         if (
    #             self._command_definition is not None
    #             and self._command_definition.result_type == ResultType.POSITIONAL
    #         ):
    #             # Have a POSITIONAL type response, so need to break it up...
    #             for defn in self._command_definition.reading_definitions:
    #                 size = defn[1]
    #                 item = _r[:size]
    #                 responses.append(item)
    #                 _r = _r[size:]
    #             return responses
    #         else:
    #             return bytearray(response)
    #             # convert string hex to bytes
    #             # _r = bytes.fromhex(_r)
    #             # return bytearray(_r)
    #     else:
    #         # for text protocol responses
    #         _responses = response.split(b"\r")
    #         for resp in _responses:
    #             _resp = resp.split(b"\t")
    #             responses.append(_resp)
    #     # Trim leading '(' of first response
    #     # 3responses[0] = responses[0][1:]
    #     # Remove CRC and \r of last response
    #     # responses[-1] = responses[-1][:-3]
    #     return responses
