import sublime
import sublime_plugin
import os
import xml.etree.ElementTree as ET
from .exec_cmd import get_variables_for_window


def cache_path():
    return os.path.join(sublime.cache_path(), 'xdt-transform')

class XdtTransformCommand(sublime_plugin.WindowCommand):
    def run(self, transformation_file, base_file = None, verbose = False):
        panel = self.window.create_output_panel('exec')
        show_panel_on_build = sublime.load_settings('Preferences.sublime-settings').get('show_panel_on_build', True)
        if show_panel_on_build:
            self.window.run_command('show_panel', { 'panel': 'output.exec' })
        
        if not os.path.isdir(cache_path()):
            create_project(self.window, base_file = base_file, transformation_file = transformation_file, verbose = verbose)
        else:
            transform(self.window, base_file = base_file, transformation_file = transformation_file, verbose = verbose)

def transform(window, base_file, transformation_file, verbose):
    window_variables = get_variables_for_window(window)
    transformation_file = sublime.expand_variables(transformation_file, window_variables)
    if base_file:
        base_file = sublime.expand_variables(base_file, window_variables)
    
    if os.path.isfile(transformation_file):
        do_transform(window, base_file, transformation_file, verbose = verbose)
    else:
        # TODO: prompt for transformation file
        #       - if transformation_file is a folder, show relevant files inside it
        #         otherwise, show relevant files from inside the folder containing base_file
        #         - if no such folder, show an error
        pass

def create_project(window, **kwargs):
    path = cache_path()
    os.makedirs(path, exist_ok = True)
    # set up a new .NET Core 2.0 project in the cache dir
    cmd = ['dotnet', 'new', 'web']
    window.run_command('exec_show_output', { 'cmd': cmd, 'working_dir': path, 'action': 'xdt-create_project', 'args': kwargs })

def build_project(window, **kwargs):
    path = cache_path()
    # read the project config
    tree = ET.parse(os.path.join(path, 'xdt-transform.csproj'))
    root = tree.getroot()
    item_group = root.findall("./ItemGroup[PackageReference]")[0]
    # add a sub element to reference the NuGet package required for XML config transformations
    ET.SubElement(item_group, 'DotNetCliToolReference', attrib = { 'Include': 'Microsoft.DotNet.Xdt.Tools', 'Version': '2.0.0' })
    # save the project file
    tree.write(os.path.join(path, 'xdt-transform.csproj'))
    # execute the build command so that it will download the NuGet package and the project - using `restore` isn't enough
    cmd = ['dotnet', 'build']
    window.run_command('exec_show_output', { 'cmd': cmd, 'working_dir': path, 'action': 'xdt-build_project', 'args': kwargs })

def do_transform(window, base_file, transformation_file, verbose = False):
    if transformation_file and not base_file:
        base_file = find_base_file(transformation_file)
        if verbose:
            window.run_command('exec_data_received', { 'data': 'File to transform not specified, trying "{}"...\n'.format(base_file), 'action': 'xdt-do_transform' })
        # if the inferred base file doesn't exist, fall back to `App.config`
        if not os.path.isfile(base_file):
            base_file = os.path.join(os.path.dirname(transformation_file), 'App.config')
            if verbose:
                window.run_command('exec_data_received', { 'data': 'File to transform not found, falling back to "{}"...\n'.format(base_file), 'action': 'xdt-do_transform' })
    
    path = cache_path()
    output_file = os.path.join(path, 'transformed.config')
    # perform the transformation
    cmd = ['dotnet', 'transform-xdt', '-x', base_file, '-t', transformation_file, '-o', output_file]
    if verbose:
        cmd.append('-v')
    window.run_command('exec_show_output', { 'cmd': cmd, 'working_dir': path, 'action': 'xdt-do_transform', 'args': { 'open': output_file } })

def find_base_file(transformation_file):
    """Given the full path to the file that contains the transformation to apply, guess the filename of the base file to be transformed, and return the path to it."""
    base_folder = os.path.dirname(transformation_file)
    transformation_filename, extension = os.path.splitext(os.path.basename(transformation_file))
    base_file = transformation_filename.rsplit('.', maxsplit = 1)[0] + extension
    return os.path.join(base_folder, base_file)

class TransformationListener(sublime_plugin.EventListener):
    def on_load_async(self, view):
        if view.file_name():
            if view.file_name() == os.path.join(cache_path(), 'transformed.config'):
                after_transformed_file_loaded(view)
    
    def on_post_window_command(self, window, command, args):
        if not (command.startswith('exec_') and command != 'exec_show_output' and args.get('action', '').startswith('xdt-')):
            return
        
        panel = window.find_output_panel('exec')
        if command == 'exec_finished':
            elapsed = args['elapsed']
            exit_code = args['exit_code']
            args['data'] = '[Finished in {:.1f}s{}]\n'.format(elapsed, '' if exit_code == 0 else ' with exit code {}'.format(exit_code))
        
        panel.run_command('append', { 'characters': args['data'] })
        
        if command == 'exec_finished':
            action = args['action'][len('xdt-'):]
            if action == 'do_transform':
                path = args['args']['open']
                if os.path.isfile(path):
                    window.open_file(path)
            elif action == 'create_project':
                build_project(window, **args['args'])
            elif action == 'build_project':
                transform(window, **args['args'])

def after_transformed_file_loaded(view):
    # retarget the view so it is as if the file hasn't been saved anywhere yet
    view.retarget('')
    # pretty print the file - this currently uses https://packagecontrol.io/packages/IndentX if it is installed
    view.run_command('basic_indent')
