import sublime
import sublime_plugin
import os
from Default.exec import AsyncProcess, ProcessListener
import time

def expand_window_variables(window, text):
    return sublime.expand_variables(text, get_variables_for_window(window))

def get_variables_for_window(window):
    return dict(
        dict(
            {
                'packages': sublime.packages_path(),
                'folder': next(iter(window.folders()), ''),
                'cache_path': sublime.cache_path(),
            },
            **get_variables_for_file_path(window.active_view().file_name(), 'file')
        ),
        **get_variables_for_file_path(window.project_file_name(), 'project')
    )

def get_variables_for_file_path(file_path, prefix):
    if not file_path:
        return dict()
    
    file_name = os.path.basename(file_path)
    file_name_no_ext, file_extension = os.path.splitext(file_name)
    return {
        prefix: file_path,
        prefix + '_path': os.path.dirname(file_path),
        prefix + '_name': file_name,
        prefix + '_extension': file_extension,
        prefix + '_base_name': file_name_no_ext,
    }

class ExecShowOutputCommand(sublime_plugin.WindowCommand, ProcessListener):
    encoding = 'utf-8'
    action = dict()

    def run(self, action, working_dir = None, **kwargs):
        if working_dir:
            os.chdir(working_dir)

        kwargs['action'] = action
        proc = AsyncProcess(kwargs.get('cmd', []), kwargs.get('shell_cmd', ''), kwargs.get('env', {}), self)
        # I wonder if we could have a race condition here, where on_data or on_finished could get called first?
        self.action[proc] = kwargs

    def on_data(self, proc, data):
        self.window.run_command('exec_data_received', dict(self.action[proc], **{ 'data': data.replace('\r\n', '\n') }))

    def on_finished(self, proc):
        elapsed = time.time() - proc.start_time
        exit_code = proc.exit_code()
        self.window.run_command('exec_finished', dict(self.action[proc], **{ 'elapsed': elapsed, 'exit_code': exit_code if exit_code is not None else 0 }))

# TODO: switch to a publish/subscribe model instead of relying on listening for post window command events, as they are not always fired (i.e. when run from another synchronous command)

class ExecDataReceived(sublime_plugin.WindowCommand):
    def run(self, data, action, **kwargs):
        pass

class ExecFinished(sublime_plugin.WindowCommand):
    def run(self, action, **kwargs):
        pass
