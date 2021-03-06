# -*- coding: utf-8 -*-
from kartograph import Kartograph
import re
import unicodedata
from subprocess import Popen, PIPE, STDOUT
import os


class MapGenerator():

    def generate(self, codes):
        codes = self.default_codes if len(codes) == 0 else codes
        for code in codes:
            self.generate_one(code)

    def generate_map(self, config, name):
        K = Kartograph()
        directory = 'map'
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_name = os.path.join(directory, name + '.svg')
        K.generate(config, outfile=file_name)
        SingleMapGenerator().codes_hacks(file_name)
        print "generated map:", file_name
        print " to view it in google-chrome run: ' google-chrome", file_name, "'"


class SingleMapGenerator(object):
    def get_map_name(self):
        return self.code.lower()

    def hacky_fixes(self, map_data):
        return map_data

    def codes_hacks(self, file_name):
        mapFile = open(file_name)
        map_data = mapFile.read()
        mapFile.close()

        mapFile = open(file_name, 'w')

        map_data = re.sub(r'"[A-Z]{2}"', dashrepl, map_data)
        map_data = re.sub(r'\-code="[^"]*"', slugrepl, map_data)
        map_data = self.hacky_fixes(map_data)

        map_data = re.sub(r'("[A-Z]{2})\.([A-Z0-9]{2}")', "\\1-\\2", map_data)
        map_data = re.sub(r'"[A-Z]{2}\-[A-Z0-9]{2}"', dashrepl, map_data)
        if "africa" in file_name:
            # set missing iso codes of Somaliland xs
            map_data = map_data.replace('"-99"', '"xs"')
        if "europe" in file_name:
            # set missing iso codes of Kosovo xk
            map_data = map_data.replace('"-99"', '"xk"')
            map_data = map_data.replace('r="2"', 'r="10"')
            map_data = map_data.replace('-code="San Marino"', '-code="San_Marino"')
            # Move Vienna to the west
            map_data = map_data.replace('cx="485.279892452"', 'cx="480.279892452"')
            # Move Bratislava to the east
            map_data = map_data.replace('cx="495.028537448"', 'cx="500.028537448"')
        elif "world" in file_name:
            map_data = map_data.replace('r="2"', 'r="6"')
            # set missing iso codes of Kosovo and Somaliland to xk and xs
            map_data = map_data.replace('data-code="-99" data-name="Kosovo"',
                                        'data-code="xk" data-name="Kosovo"')
            map_data = map_data.replace('data-code="-99" data-name="Somaliland"',
                                        'data-code="xs" data-name="Somaliland"')
            # TODO: set missing iso code of Northern Cyprus. But what code?
        elif "asia" in file_name:
            map_data = map_data.replace('r="2"', 'r="8"')
        elif "samerica" in file_name:
            map_data = map_data.replace('r="2"', 'r="24"')
        elif "namerica" in file_name:
            map_data = map_data.replace('r="2"', 'r="8"')
        elif ("ar." in file_name or
              "no." in file_name):
            map_data = map_data.replace('r="2"', 'r="24"')
        elif ("ar." in file_name or
              "se." in file_name or
              "fi." in file_name):
            map_data = map_data.replace('r="2"', 'r="36"')
        map_data = map_data.replace('r="2"', 'r="16"')

        map_data = self.fix_code_conflicts(map_data)

        p = Popen(["xmllint", "--format", '-'], stdout=PIPE, stderr=STDOUT, stdin=PIPE)
        out, err = p.communicate(input=map_data)

        mapFile.write(out)
        mapFile.close()

    def fix_code_conflicts(self, map_data):
        codes = ['district', 'chko', 'surface', 'soorp', 'soopu']
        for code in codes:
            code_id = 'id="' + code + '"'
            try:
                start_position = map_data.index(code_id)
                end_position = map_data.index('</g>', start_position)
                layer = map_data[start_position:end_position]
                layer = layer.replace('code="', 'code="' + code + '-')
                map_data = map_data[:start_position] + layer + map_data[end_position:]
            except ValueError:
                pass
        return map_data

    def generate_map(self):
        K = Kartograph()
        directory = 'map'
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_name = os.path.join(directory, self.map_name + '.svg')
        K.generate(self.config, outfile=file_name)
        self.codes_hacks(file_name)
        print "generated map:", file_name
        print " to view it in google-chrome run: ' google-chrome", file_name, "'"


def slugrepl(matchobj):
    text = re.sub(r"\s+", '_', matchobj.group(0)).decode("utf-8")
    return unicodedata.normalize('NFD', text).encode('ascii', 'ignore')


def dashrepl(matchobj):
    return matchobj.group(0).lower()
