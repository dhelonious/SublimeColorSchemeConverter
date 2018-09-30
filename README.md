Sublime Color Scheme Converter
==============================

**Note**: Not all features of the `sublime-color-scheme` format are supported. See the list of supported features below.

Simple Sublime Text 3 plugin to convert the `sublime-color-scheme` json format to `tmTheme` plist format. While the configuration of json files is far more convenient, some plugins rely on a `tmTheme`-formatted color scheme.

Supported features (c.f. [https://www.sublimetext.com/docs/3/color_schemes.html]):
* Variables
* 6-digit Hex RGB and 8-digit Hex RGBA
* RGB, RGBA, HSL, and HSLA functional notations
* CSS color names
* alpha() adjuster
* Replace underscore by uppercase letters

The plugin tries to replace all patterns, where a color is recognized. Therefore `color(#000000`

Example:
--------

*theme.sublime-color-scheme*:

``` json
{
    "name": "Test Theme",
    "author": "Me",
    "variables": {
        "white": "#ffffff",
        "black": "rgb(0, 0, 0)",
        "gray": "#000000aa"
    },
    "globals": {
        "foreground": "var(black)",
        "background": "#ffffff",
        "invisibles": "color(var(white) alpha(0.2))",
        "accent": "hsl(0, 100%, 50%)",
        "minimap_border": "color(#000000, alpha(1))"
    },
    "rules": [
        {
            "name": "Rule",
            "scope": "rule",
            "foreground": "var(black)",
            "background": "var(white)",
            "font_style": "italic"
        }
    ]
}
```

*theme.tmTheme*:

``` xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>author</key>
    <string>Me</string>
    <key>name</key>
    <string>Test Theme</string>
    <key>settings</key>
    <array>
        <dict>
            <key>settings</key>
            <dict>
                <key>accent</key>
                <string>#ff0000</string>
                <key>invisibles</key>
                <string>#ffffff33</string>
                <key>foreground</key>
                <string>#000000</string>
                <key>background</key>
                <string>#ffffff</string>
                <key>minimapBorder</key>
                <string>#000000ff</string>
            </dict>
        </dict>
        <dict>
            <key>scope</key>
            <string>rule</string>
            <key>name</key>
            <string>Rule</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>#000000</string>
                <key>fontStyle</key>
                <string>italic</string>
                <key>background</key>
                <string>#ffffff</string>
            </dict>
        </dict>
    </array>
</dict>
</plist>
```