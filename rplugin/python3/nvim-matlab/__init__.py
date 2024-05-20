import pynvim


from .matlab_cli_controller import MatlabCliController
from .python_nvim_utils import PythonNvimUtils as py_nvim_helper
import python_nvim_utils


@pynvim.plugin
class VimMatlab():
    def __init__(self, nvim):
        self.nvim = nvim
        python_nvim_utils.nvim = nvim
        self.cli_controller = None

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
        self.cli_controller = MatlabCliController()
