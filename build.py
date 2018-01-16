import sublime
import sublime_plugin
import os
import subprocess
import xml.etree.ElementTree as ET


def cache_path():
    return os.path.join(sublime.cache_path(), 'xdt-transform')

def exec_subprocess(cmd):
    # Hide the console window on Windows
    startupinfo = None
    if os.name == "nt":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    subprocess.call(cmd, cwd = cache_path(), startupinfo = startupinfo)

class XdtTransformCommand(sublime_plugin.WindowCommand):
    def run(self, transformation_file, base_file = None):
        path = cache_path()
        if not os.path.isdir(path):
            os.makedirs(path, exist_ok=True)
            # set up a new .NET Core 2.0 project
            exec_subprocess(['dotnet', 'new', 'web'])
            # read the project config
            tree = ET.parse(os.path.join(path, 'xdt-transform.csproj'))
            root = tree.getroot()
            item_group = root.findall("./ItemGroup[PackageReference]")[0]
            # add a sub element to reference the NuGet package required for XML config transformations
            ET.SubElement(item_group, 'DotNetCliToolReference', attrib = { 'Include': 'Microsoft.DotNet.Xdt.Tools', 'Version': '2.0.0' })
            # save the project file
            tree.write(os.path.join(path, 'xdt-transform.csproj'))
            # execute the build command so that it will download the NuGet package and the project - using `restore` isn't enough
            exec_subprocess(['dotnet', 'build'])
        
        transformation_file = expand_variables(self.window, transformation_file)
        if base_file:
            base_file = expand_variables(self.window, base_file)
        
        if os.path.isfile(transformation_file):
            do_transform(self.window, base_file, transformation_file)
        else:
            # TODO: prompt for transformation file
            #       - if transformation_file is a folder, show relevant files inside it
            #         otherwise, show relevant files from inside the folder containing base_file
            #         - if no such folder, show error
            pass

def expand_variables(window, text):
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

def do_transform(window, base_file, transformation_file):
    if transformation_file and not base_file:
        base_file = find_base_file(transformation_file)
    
    path = cache_path()
    # perform the transformation
    exec_subprocess(['dotnet', 'transform-xdt', '-x', base_file, '-t', transformation_file, '-o', os.path.join(path, 'transformed.config')])
    
    # open the transformed file
    if window:
        view = window.open_file(os.path.join(path, 'transformed.config'))
        def check_loaded():
            if view.is_loading():
                sublime.set_timeout_async(check_loaded, 5)
            else:
                # retarget the view so it is as if the file hasn't been saved anywhere yet
                view.retarget('')
                # pretty print the file - this currently uses https://packagecontrol.io/packages/IndentX if it is installed
                view.run_command('basic_indent')
        # after the file has loaded, perform some actions
        check_loaded()

def find_base_file(transformation_file):
    """Given the full path to the file that contains the transformation to apply, guess the filename of the base file to be transformed, and return the path to it."""
    base_folder = os.path.dirname(transformation_file)
    transformation_filename, extension = os.path.splitext(os.path.basename(transformation_file))
    base_file = transformation_filename.split('.', maxsplit = 1)[0] + extension
    return os.path.join(base_folder, base_file)
