import sublime
import sublime_plugin
import os
import subprocess
import xml.etree.ElementTree as ET


def cache_path():
    return os.path.join(sublime.cache_path(), 'xdt-transform')

class XdtTransformCommand(sublime_plugin.WindowCommand):
    def run(self, transformation_file, base_file = None):
        path = cache_path()
        if not os.path.isdir(path):
            os.makedirs(path, exist_ok=True)
            # set up a new .NET Core 2.0 project
            subprocess.call(['dotnet', 'new', 'web'], cwd = path)
            # read the project config
            tree = ET.parse(os.path.join(path, 'xdt-transform.csproj'))
            root = tree.getroot()
            item_group = root.findall("./ItemGroup[PackageReference]")[0]
            # add a sub element to reference the NuGet package required for XML config transformations
            ET.SubElement(item_group, 'DotNetCliToolReference', attrib = { 'Include': 'Microsoft.DotNet.Xdt.Tools', 'Version': '2.0.0' })
            # save the project file
            tree.write(os.path.join(path, 'xdt-transform.csproj'))
            # execute the build command so that it will download the NuGet package
            subprocess.call(['dotnet', 'build'], cwd = path)
        
        # TODO: more useful expansion of env vars
        if transformation_file == '$file':
            transformation_file = self.window.active_view().file_name()
        
        if os.path.isfile(transformation_file):
            do_transform(self.window, base_file, transformation_file)
        else:
            # TODO: prompt for transformation file
            #       - if transformation_file is a folder, show relevant files inside it
            #         otherwise, show relevant files from inside the folder containing base_file
            #         - if no such folder, show error
            pass

def do_transform(window, base_file, transformation_file):
    if transformation_file and not base_file:
        base_file = find_base_file(transformation_file)
    
    path = cache_path()
    # perform the transformation
    subprocess.call(['dotnet', 'transform-xdt', '-x', base_file, '-t', transformation_file, '-o', os.path.join(path, 'transformed.config')], cwd = path)
    
    # open the transformed file
    if window:
        window.open_file(os.path.join(path, 'transformed.config'))

def find_base_file(transformation_file):
    """Given the full path to the file that contains the transformation to apply, guess the filename of the base file to be transformed, and return the path to it."""
    base_folder = os.path.dirname(transformation_file)
    transformation_filename, extension = os.path.splitext(os.path.basename(transformation_file))
    base_file = transformation_filename.split('.', maxsplit = 1)[0] + extension
    return os.path.join(base_folder, base_file)
