import visa
import sys, time

class RfControl:
    """
    Class RfControl: mechanical RF Attenuation units controller
    """

    # Resource manager instance
    resource_mgr = None
    # VISA resource name
    resource_names = []
    # VISA instrument instance - virtual control unit for end device
    instruments = []
    #
    att_values_allowed = {}

    def __init__(self, timeout=1000, line_termination='\r\n'):
        """
        Construct rf control object
        :param timeout: instrument default timeout value
        :type timeout: int
        :param line_termination: line termination pattern
        :type line_termination: str
        :raises: NameError
        """
        # Initiate resource manager for pyvisa-py backend
        self.resource_mgr = visa.ResourceManager('@py')

        # Lookup for ACM devices in all possible visa resources
        self.resource_names = get_acm_ctrl_list(self.resource_mgr.list_resources())
        if not self.resource_names:
            raise NameError('No ACM resources found, please check your devices connection')

        # Setup instrument instances list for all connected VISA devices
        self.instruments = {'att%d' % self.resource_names.index(ins) : self.resource_mgr.open_resource(ins)
                            for ins in self.resource_names}

        # Apply instrument settings
        for unit in self.instruments.values():
            unit.read_termination = line_termination
            unit.timeout = timeout

        # Get allowed gain values
        self.att_values_allowed = {name: list(ins.query('ATT:ATTTabGet?').split(','))
                                   for name, ins in self.instruments.items()}


    def get_instrument_names(self):
        """
        Get instrument names for available VISA units
        :return: Istrument names list to reference for control operations
        :rtype: list
        """
        return list(self.instruments.keys())

    def get_available_gain_values(self):
        """
        Get possible attenuation values for all available instruments
        :return: Dictionary of attenuator name and possible attenuation values list
        :rtype: dict
        """
        return self.att_values_allowed


    def get_att_value(self, instrument_name):
        """
        Get current attenuation setting for particular attenuator identified by 'instrument_name'
        :param instrument_name: instrument name to handle
        :type instrument_name: string
        :return: execution status, current attenuation value setting(dB), error message
        :rtype: bool, int, str
        """
        status = False
        att_val = None
        msg = ''

        if instrument_name in self.instruments.keys():
            status = True
            att_val = float(self.instruments[instrument_name].query('ATT:ATTGetCurVal?'))
        else:
            msg = 'Instrument name not found'
        return status, att_val, msg

    def set_att_value(self, instrument_name, att_value):
        """
        Set attenuation value for specific instrument if possible
        :param instrument_name: instrument name to handle
        :type instrument_name: str
        :param att_value: attenuation value in dB
        :type att_value: float
        :return: execution status, current attenuation value setting(dB), error message
        :rtype: bool, int, str
        """
        status = False
        att_val = None
        msg = ''

        if instrument_name in self.instruments.keys():
            if att_value in self.att_values_allowed[instrument_name]:
                att_val = float(self.instruments[instrument_name].query('ATT:ATTSet? {:f}'.format(float(att_value))))
                status = True
            else:
                msg = 'Unsupported attenuation value'
        else:
            msg = 'Instrument name not found'
        return status, att_val, msg

    def set_step_up(self, instrument_name):
        """
        Increase attenuation value by one step
        :param instrument_name: instrument name to handle
        :type instrument_name: str
        :return: execution status, current attenuation value setting(dB), error message
        :rtype: bool, int, str
        """
        status = False
        att_val = None
        msg = ''

        if instrument_name in self.instruments.keys():
            att_val = float(self.instruments[instrument_name].query('ATT:ATTSetUp?'))
            status = True
        else:
            msg = 'Unsupported attenuation value'
        return status, att_val, msg

    def set_step_down(self, instrument_name):
        """
        Decrease attenuation value by one step
        :param instrument_name: string, instrument name to handle
        :type instrument_name: str
        :return: execution status, current attenuation value setting(dB), error message
        :rtype: bool, int, str
        """
        status = False
        att_val = None
        msg = ''

        if instrument_name in self.instruments.keys():
            att_val = float(self.instruments[instrument_name].query('ATT:ATTSetDown?'))
            status = True
        else:
            msg = 'Unsupported attenuation value'
        return status, att_val, msg


    def __del__(self):
        """
        Destructor for resources and resource manager instance
        """
        for ins in self.instruments.values():
            ins.close()
        self.resource_mgr.close()

def get_acm_ctrl_list(interfaces_list):
    """
    Return list of ACM interfaces corresponding to target VISA devices
    :param interfaces_list: list of strings referring possible VISA addresses by control lines
    :type interfaces_list: list
    :return: list of available ACM-managed addresses for VISA devices
    :rtype: list
    """
    return [elem for elem in interfaces_list if 'ACM' in elem]

if __name__ == '__main__':

    opts = sys.argv[1:]
    action = opts[0]

    ctl = RfControl()

    if action == 'names':
        print(ctl.get_instrument_names())
    elif action == 'get_val':
        print(ctl.get_att_value(opts[1]))
    elif action == 'allow':
        print(ctl.get_available_gain_values())
    elif action == 'set':
        print(ctl.set_att_value(opts[1], opts[2]))
    elif action == 'get':
        print(ctl.get_att_value(opts[1]))
    elif action == 'up':
        print(ctl.set_step_up(opts[1]))
    elif action == 'down':
        print(ctl.set_step_down(opts[1]))
    elif action == 'test':
        a = ctl.get_available_gain_values()
        for val in a[opts[1]]:
            print(ctl.set_att_value(opts[1],val))
            time.sleep(1)


