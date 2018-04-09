import serial
import serial.tools.list_ports
from time import sleep


class Device:
    """
      This is a library for controlling uArms that have uFactories communication protocol of version 0.9.6
    """

    def __init__(self, port):
        """
        :param port: The COM port that the robot is plugged in to.
        """
        self._serial = None  # The serial connection to the robot
        self._connect_to_robot(port)
        print("Connected to robot.")

    # Functions that are only used inside of this library
    def _connect_to_robot(self, port):
        self._serial = serial.Serial(port=port,
                                     baudrate=9600,
                                     parity=serial.PARITY_NONE,
                                     stopbits=serial.STOPBITS_ONE,
                                     bytesize=serial.EIGHTBITS,
                                     timeout=.1)
        sleep(3)

    def set_person_status(self, person_there: bool):
        cmd = "person:" + str(int(person_there))
        self._send_and_receive(cmd)

    def _send_and_receive(self, cmnd):
        """
        This command will send a command and receive the robots response. There must always be a response!
        Responses should be recieved immediately after sending the command, after which the robot will proceed to
        perform the action.
        :param cmnd: a String command, to send to the robot
        :return: The robots response
        """

        # Prepare and send the command to the robot
        cmndString = bytes(cmnd,
                           encoding='ascii')  # "[" + cmnd + "]"

        try:
            self._serial.write(cmndString)
        except serial.serialutil.SerialException:
            print("Communication| ERROR while sending command ", cmnd,
                  ". Disconnecting Serial!")
            raise

        # Read the response from the robot (THERE MUST ALWAYS BE A RESPONSE!)
        response = ""
        while True:
            try:
                response += str(self._serial.read(), 'ascii')
                response = response.replace(' ', '')

            except serial.serialutil.SerialException as e:
                print("Communication| ERROR ", e, "while sending command ",
                      cmnd, ". Disconnecting Serial!")
                raise

            if "[" in response and "]" in response:
                response = str(response.replace("\n", ""))
                response = str(response.replace("\r", ""))
                break

        # Clean up the response
        response = response.replace("[", "")
        response = response.replace("]", "")

        return response
