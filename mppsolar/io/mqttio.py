import logging
import paho.mqtt.publish as publish
import paho.mqtt.subscribe as subscribe

# import time

from .baseio import BaseIO
from ..helpers import get_kwargs

log = logging.getLogger("MPP-Solar")


class MqttIO(BaseIO):
    def __init__(self, *args, **kwargs) -> None:
        # self._serial_port = device_path
        # self._serial_baud = serial_baud
        self.mqtt_broker = get_kwargs(kwargs, "mqtt_broker", "localhost")
        self.mqtt_port = get_kwargs(kwargs, "mqtt_port", 1883)
        self.mqtt_user = get_kwargs(kwargs, "mqtt_user")
        self.mqtt_pass = get_kwargs(kwargs, "mqtt_pass")
        log.info(
            f"MqttIO.__init__ mqtt_broker: {self.mqtt_broker}, port: {self.mqtt_port}, user: {self.mqtt_user}, pass: {self.mqtt_pass}"
        )

    def send_and_receive(self, full_command, client_id="ESP32-Sensor") -> dict:
        response_line = None
        # print(self.mqtt_broker)
        if self.mqtt_user is not None and self.mqtt_pass is not None:
            auth = {"username": self.mqtt_user, "password": self.mqtt_pass}
            log.info(f"Using mqtt authentication, username: {self.mqtt_user}, password: [supplied]")
        else:
            log.debug("No mqtt authentication used")
            auth = None
        command_topic = f"{client_id}/command"
        result_topic = f"{client_id}/result"
        print(f"topic: {command_topic}")

        # single(topic, payload=None, qos=0, retain=False, hostname="localhost",
        #        port=1883, client_id="", keepalive=60, will=None, auth=None, tls=None,
        #        protocol=mqtt.MQTTv311, transport="tcp")
        publish.single(
            topic=command_topic,
            payload=full_command,
            hostname=self.mqtt_broker,
            port=self.mqtt_port,
            auth=auth,
        )

        # simple(topics, qos=0, msg_count=1, retained=False, hostname="localhost",
        #       port=1883, client_id="", keepalive=60, will=None, auth=None, tls=None,
        #       protocol=mqtt.MQTTv311)
        # try:
        #     with serial.serial_for_url(self._serial_port, self._serial_baud) as s:
        #         log.debug(f"Executing command via serialio...")
        #         s.timeout = 1
        #         s.write_timeout = 1
        #         s.flushInput()
        #         s.flushOutput()
        #         s.write(full_command)
        #         time.sleep(0.1)  # give serial port time to receive the data
        #         response_line = s.read_until(b"\r")
        #         log.debug("serial response was: %s", response_line)
        #         return response_line
        # except Exception as e:
        #     log.warning(f"Serial read error: {e}")
        # log.info("Command execution failed")
        # return {"ERROR": ["Serial command execution failed", ""]}
