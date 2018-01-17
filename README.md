# Sublime .NET Config

This package aims to provide better syntax highlighting of `.config` files that relate to .NET (i.e. C#) XML configuration.
For example, it is common to use [configuration transformations](https://msdn.microsoft.com/en-us/library/dd465326%28v=vs.110%29.aspx?f=255&MSPPError=-2147217396) to automatically update config files for different environments. This makes it much easier to keep track of the differences between environments (dev, QA, production etc.).
If you have the [XPath 1.0 package](https://packagecontrol.io/packages/xpath) installed, the syntax highlighting included in this package will highlight
the XPath syntax in the `xdt:Transform` and `xdt:Locator` attributes, for convenience.

## How it works

### Syntax Highlighting

This package makes use of the [YAMLMacros package](https://packagecontrol.io/packages/YAMLMacros) to build a syntax definition based on the XML syntax definition, with a few extra features for .NET configuration files. This is the easiest way at the moment to extend or modify existing syntax definitions without needing to manually copy and paste the entire definition.

Due to the use of the `embed` feature, this package is only compatible with ST build 3156 or newer.

### Configuration Transformation

Configuration Transformations require the `.NET Core 2.0 SDK` to be installed and available on the `PATH`. This functionality uses https://www.nuget.org/packages/Microsoft.DotNet.Xdt.Tools/ to perform the transformations. It can be a little slow the first time the build command is used, due to it needing to create a new project, download the package and build the project.

After the file has been transformed, it is automatically opened in ST, and acts just like any normal unsaved config file. As an added bonus, if you have https://packagecontrol.io/packages/IndentX installed, the file will be pretty-printed/indented after transformation.

### Unit Tests

To run the unit tests, you will need to install https://packagecontrol.io/packages/UnitTesting, and then use the `UnitTesting: Test Current Package` entry in the command palette.

## Planned features

Hopefully, in future, we can even get configuration transformation previews to show the original and transformed configuration files side by side with the differences highlighted...
It may turn out to be useful to be able to turn the pretty-printing off via a preference, or to pretty-print the source file as well for comparison.

Autocompletion for known .NET configuration elements and attributes would also be cool.

It might also be useful to be able to create a transform file automatically from a source file and a target file, for cases where, for example, a Production config file has been altered by somebody with access to that environment, and you want to ensure your deployment script doesn't lose those changes, while also keeping them under source control. https://github.com/CameronWills/FatAntelope looks useful in this regard, but unfortunately targets the full .NET Framework.
