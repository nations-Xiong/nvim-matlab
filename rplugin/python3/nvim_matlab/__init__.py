import pynvim
import os
import time


from .matlab_cli_controller import MatlabCliController
from .python_nvim_utils import PythonNvimUtils as py_nvim_helper
import nvim_matlab.python_nvim_utils as python_nvim_utils

TIME_INTERVAL_RETRY = 1

@pynvim.plugin
class VimMatlab():
    def __init__(self, nvim):
        self.nvim = nvim
        python_nvim_utils.nvim = nvim
        self.cli_controller = None

    @pynvim.command('MatlabCliShowHelp', sync=True)
    def show_help_in_matlab_cli(self):
        if self.cli_controller is None:
            self.connect_to_matlab_cli()
        pass

    @pynvim.command('MatlabCliShowDoc', sync=True)
    def show_doc_in_matlab_cli(self):
        if self.cli_controller is None:
            self.connect_to_matlab_cli()
        pass

    @pynvim.command('MatlabCliRunSelection', sync=True)
    def run_selection_in_matlab_cli(self):
        if self.cli_controller is None:
            self.connect_to_matlab_cli()

        lines = py_nvim_helper.get_lines_selected()
        self.cli_controller.exec_code(lines)

    @pynvim.command('MatlabCliRunCurrentLine', sync=True)
    def run_current_line_in_matlab_cli(self):
        if self.cli_controller is None:
            self.connect_to_matlab_cli()

        line = py_nvim_helper.get_current_line()
        self.cli_controller.exec_code(line)

    @pynvim.command('MatlabCliRunAsScript', sync=True)
    def run_current_file_as_m_script(self):
        if self.cli_controller is None:
            self.connect_to_matlab_cli()

        py_nvim_helper.save_current_buffer()
        m_script_path = py_nvim_helper.get_current_file_path()
        cmd = [f"run('{m_script_path}');"]
        self.cli_controller.exec_code(cmd)

    @pynvim.command('MatlabCliCancel', sync=True)
    def cancel_execution_in_matlab_cli(self):
        if self.cli_controller is None:
            self.connect_to_matlab_cli()
        self.cli_controller.send_ctrl_c()

    @pynvim.command('MatlabCliConnect', sync=True)
    def connect_to_matlab_cli(self):
        if self.cli_controller is not None:
            return
        while True:
            try:
                self.cli_controller = MatlabCliController()
            except Exception as e:
                self.start_matlab_cli_server()
                time.sleep(TIME_INTERVAL_RETRY)
            else:
                break

    @pynvim.command('MatlabCliDisconnect', sync=True)
    def disconnect_from_matlab_cli(self):
        if self.cli_controller is None:
            return
        self.cli_controller.disconnect_to_server()
        self.cli_controller = None

    @pynvim.command('MatlabCliServerStart')
    def start_matlab_cli_server(self):
        if self.cli_controller is not None:
            return
        try:
            server_path = os.path.join(os.path.dirname(__file__), '../../../scripts/matlab-server.py')
            self.nvim.command(f'!tmux split-window -h python {server_path}')
        except Exception as e:
            pass

    @pynvim.command('MatlabCliServerStop')
    def stop_matlab_cli_server(self):
        if self.cli_controller is None:
            return
        self.cli_controller.send_kill()
        self.disconnect_from_matlab_cli()
