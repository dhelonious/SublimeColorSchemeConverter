"""
SublimeColorSchemeConverter

Converts sublime-color-scheme json files into tmTheme plist files.
"""

import os
import re
import json
import plistlib
import colorsys
import traceback
import collections

import sublime
import sublime_plugin

from SublimeColorSchemeConverter.lib import plistlib

re_var = re.compile("var\([^\)]+\)")
re_alpha = re.compile("alpha\(((0\.)?[0-9]+)\)")
re_hex = re.compile("(#[0-9,a-z,A-Z]{6})([0-9,a-z,A-Z]{2})?")
re_rgb = re.compile("rgb\((\d+),\s?(\d+),\s?(\d+)(,\s?(\d+\.?\d*))?\)")
re_hsl = re.compile("hsl\((\d+),\s?(\d+)%,\s?(\d+)%(,\s?(\d+\.?\d*))?\)")

def alpha_to_hex(a):
    return "{:02x}".format(int(255*float(a)))

def hexa_to_hex(hex, a):
    return hex[:7] + alpha_to_hex(a)

def rgb_to_hex(r, g, b, a=None):
    hexcode = "#{:02x}{:02x}{:02x}".format(r, g, b)
    if a:
        hexcode += alpha_to_hex(a)
    return hexcode

def get_alpha_adjuster(string, default=None):
    alpha = re_alpha.search(string)
    if alpha:
        return float(alpha.group(1))
    else:
        return default

def get_alpha_hex(hexcode):
    if len(hexcode) < 8:
        return None
    else:
        return int(hexcode[7:], 16)

def match_hex(string):
    match = re_hex.search(string)
    result = None
    if match:
        result = match.group(1)
        alpha = get_alpha_adjuster(string)
        if alpha:
            result += alpha_to_hex(alpha)
        elif match.group(2):
            result += match.group(2)
    return result

def match_rgb(string):
    match = re_rgb.search(string)
    result = None
    if match:
        r = int(match.group(1))
        g = int(match.group(2))
        b = int(match.group(3))
        a = get_alpha_adjuster(string, match.group(5))
        result = rgb_to_hex(r, g, b, a)
    return result

def match_hsl(string):
    match = re_hsl.search(string)
    result = None
    if match:
        h = int(match.group(1))/360
        s = int(match.group(2))/100
        l = int(match.group(3))/100
        a = get_alpha_adjuster(string, match.group(5))
        r, g, b = [255*int(v) for v in colorsys.hls_to_rgb(h, l, s)]
        result = rgb_to_hex(r, g, b, a)
    return result

def try_match_color(string):
    hexcode = match_hex(string)
    if not hexcode:
        hexcode = match_rgb(string)
    if not hexcode:
        hexcode = match_hsl(string)
    if hexcode:
        alpha = get_alpha_adjuster(string, get_alpha_hex(hexcode))
        if alpha:
            hexcode = hexa_to_hex(hexcode[:7], alpha)
    else:
        hexcode = string
    return hexcode

class ConvertSublimeColorSchemeCommand(sublime_plugin.TextCommand):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = None
        self.theme = None
        self.output = None
        self.output_view = None

    def convert_name(self, string):
        return re.sub(
            "_([a-z,A-Z,0-9])",
            lambda match: match.group(1).upper(),
            string
        )

    def parse_color(self, key, variables):
        if key in list(variables):
            return try_match_color(variables[key])
        else:
            var = re_var.search(key)
            if var:
                color = variables.get(var.group(), var.group())
                return try_match_color(key.replace(var.group(), color))
            else:
                return try_match_color(key)

    def parse_settings(self, settings, variables):
        parsed = {}
        for key in list(settings):
            value = settings[key]
            parsed[self.convert_name(key)] = self.parse_color(value, variables)
        return parsed

    def parse_scope(self, scope):
        parsed = self.convert_name(scope)
        parsed = re.sub("\s(-|\|)\s", ", ", parsed)
        parsed = re.sub("\s*(\(|\))\s*", " ", parsed)
        return parsed

    def parse_rules(self, rules, variables):
        parsed = []
        for settings in rules:
            rule = {}
            name = settings.pop("name", None)
            if name:
                rule["name"] = name
            scope = settings.pop("scope", None)
            if scope:
                rule["scope"] = self.parse_scope(scope)
            rule["settings"] = self.parse_settings(settings, variables)
            parsed.append(rule)
        return parsed

    def parse(self):
        name = self.theme.get("name", None)
        author = self.theme.get("author", None)
        variables = self.theme.get("variables", None)
        globals_ = self.theme["globals"]
        rules = self.theme["rules"]

        for key in list(variables):
            variables["var({})".format(key)] = variables.pop(key)

        settings = self.parse_settings(globals_, variables)
        rules = self.parse_rules(rules, variables)
        self.theme = {
            "name": name,
            "author": author,
            "settings": [{"settings": settings}] + rules
        }

    def convert(self):
        error = False
        try:
            dumps = plistlib.dumps(self.theme, sort_keys=False)
            self.output = dumps.decode("UTF-8")
        except Exception:
            error = True
            sublime.error_message("Could not convert Sublime Color Scheme")
            print("SublimeColorSchemeConverter:")
            print(traceback.format_exc())
        return error

    def read_source(self):
        error = False
        self.filename = self.view.file_name()
        try:
            if self.filename and os.path.exists(self.filename):
                with open(self.filename) as sublime_color_scheme:
                    self.theme = json.load(sublime_color_scheme)
        except Exception:
            error = True
            sublime.error_message("Could not read source")
            print("SublimeColorSchemeConverter:")
            print(traceback.format_exc())
        return error

    def write_buffer(self, edit):
        error = False
        output_name = os.path.splitext(os.path.basename(self.filename))[0] \
                      + ".tmTheme"
        try:
            self.output_view = self.view.window().new_file()
            self.output_view.set_encoding("UTF-8")
            self.output_view.set_name(output_name)
            self.output_view.replace(
                edit,
                sublime.Region(0, self.view.size()),
                self.output
            )
            self.output = None
        except Exception:
            error = True
            sublime.error_message("Could not write buffer")
            print("SublimeColorSchemeConverter:")
            print(traceback.format_exc())
        return error

    def run(self, edit):
        if not self.read_source():
            if not self.parse():
                if not self.convert():
                    self.write_buffer(edit)
        self.filename = None
        self.theme = None
        self.output = None
