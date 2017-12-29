# Sublime .NET Config

This package aims to provide better syntax highlighting of `.config` files that relate to .NET (i.e. C#) XML configuration.
For example, it is common to use [configuration transformations](https://msdn.microsoft.com/en-us/library/dd465326%28v=vs.110%29.aspx?f=255&MSPPError=-2147217396) to automatically update config files for different environments. This makes it much easier to keep track of the differences between environments (dev, QA, production etc.).
If you have the [XPath 1.0 package](https://packagecontrol.io/packages/xpath) installed, the syntax highlighting included in this package will highlight
the XPath syntax in the `xdt:Transform` and `xdt:Locator` attributes, for convenience.

## How it works

This package makes use of the [YAMLMacros package](https://packagecontrol.io/packages/YAMLMacros) to build a syntax definition based on the XML syntax definition, with a few extra features for .NET configuration files. This is the easiest way at the moment to extend or modify existing syntax definitions without needing to manually copy and paste the entire definition.

Due to the use of the `embed` feature, this package is only compatible with ST build 3156 or newer.

## Planned features

Hopefully, in future, we can even get configuration transformation previews to be a function of this plugin, to show the original and transformed configuration files side by side with the differences highlighted...

Autocompletion for known .NET configuration elements and attributes would also be cool.
