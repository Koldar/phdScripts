#!/usr/bin/python3.6

import abc
import argparse
import math
import re
import sys
import logging
from typing import Iterable, Tuple, Dict

import yaml

FORMAT_WHOENIG = "whoenig_1.0"
FORMAT_MOVINGAI = "movingai_1.0"


def read_lines_in_file(filename: str) -> str:
    with open(filename, "r") as f:
        yield f.readline()[:-1]


class AbstractMapFormat(abc.ABC):

    def __init__(self, width: int, height: int, fill: float):
        self.__width = width
        self.__height = height
        self.__map = [[fill for x in range(width)] for y in range(height)]

    @abc.abstractmethod
    def encode(self) -> "str":
        pass

    @classmethod
    def create_from(cls, default: "AbstractMapFormat", **kwargs):
        logging.debug(f"kw args are {kwargs}")
        result = cls(width=default.width(), height=default.height(), fill=0, **kwargs)
        for y, x, val in default.cells():
            result.set_cell_value(y, x, val)
        return result

    def set_cell_value(self, y: int, x: int, val: float):
        self.__map[y][x] = val

    def get_cell_value(self, y: int, x: int) -> float:
        return self.__map[y][x]

    def width(self):
        return self.__width

    def height(self):
        return self.__height

    def cells(self) -> Iterable[Tuple[int, int, float]]:
        for y in range(self.__height):
            for x in range(self.__width):
                yield y, x, self.__map[y][x]


class WhoenigMapFormat(AbstractMapFormat):

    @classmethod
    def from_file(cls, filename: str, basecost: float) -> "WhoenigMapFormat":
        with open(filename, "r") as f:
            try:
                representation = yaml.load(f)
                result = WhoenigMapFormat(
                    width=representation['map']['dimensions'][0],
                    height=representation['map']['dimensions'][1],
                    fill=basecost,
                )
                for obs in representation['map']['obstacles']:
                    x, y = obs
                    logging.debug(f"obs is {obs} ({type(obs)})")
                    result.set_cell_value(y, x, float('+inf'))
                return result
            except yaml.YAMLError as exc:
                raise ValueError(f"error while parsing yaml! Exception {exc}")

    def encode(self) -> "str":
        result = []
        result.append("map:")
        result.append(f"   dimensions: [{self.width()}, {self.height()}]")
        result.append("    obstacles:")
        for y, x, value in self.cells():
            if math.isinf(value):
                result.append(f"    - !!python/tuple [{x},{y}]")
        return '\n'.join(result)


class MovingAIMapFormat(AbstractMapFormat):

    def __init__(self, width: int, height: int, fill: float, movingai_converter: Dict[str, float]):
        AbstractMapFormat.__init__(self, width, height, fill)
        logging.debug(f"movingai_converter is {movingai_converter}")
        self.__characters_to_cost = movingai_converter
        self.__cost_to_characters = {}
        for k, v in self.__characters_to_cost.items():
            for av in self.__cost_to_characters:
                if math.isclose(v, av):
                    raise ValueError(f"movingai_converter is not a unique mapping!")
            self.__cost_to_characters[v] = k
        logging.debug(f"cost to characters is {self.__cost_to_characters}")

    def encode(self) -> "str":
        logging.debug(list(self.__cost_to_characters.items()))
        result = []
        result.append("type octile")
        result.append(f"height: {self.height()}")
        result.append(f"width: {self.width()}")
        result.append(f"map")
        for y in range(self.height()):
            row = ""
            for x in range(self.width()):
                val = self.get_cell_value(y, x)
                logging.debug(f"y={y} x={x} val={val}")
                char = self.__cost_to_characters[val]
                row += char
            result.append(row)
        return '\n'.join(result)

    @classmethod
    def from_file(cls, filename: str, movingai_converter: Dict[str, float]) -> "MovingAIMapFormat":
        with open(filename, "r") as f:
            header = f.readline()[:-1]
            if header != "type octile":
                raise NotImplementedError(f"this utility can work only if the header of MovingAI is \"type octile\". it was: \"{header}\"!")

            height_str = f.readline()[:-1]
            m = re.match(r"^\s*height\s*(?P<height>\d+)\s*$", height_str)
            if m is None:
                raise ValueError(f"cannot detect height of map file! It was \"{height_str}\"")
            height = int(m.group("height"))

            width_str = f.readline()[:-1]
            m = re.match(r"^\s*width\s*(?P<width>\d+)\s*$", width_str)
            if m is None:
                raise ValueError(f"cannotr detect width of map file! It was \"{width_str}\"")
            width = int(m.group("width"))

            map_preamble = f.readline()[:-1]
            if map_preamble != "map":
                raise ValueError(f"cannot detected map preamble! Expecting \"map\" but was \"{map_preamble}\"!")
            # read the content of map
            result = MovingAIMapFormat(width=width, height=height, fill=0, movingai_converter=movingai_converter)
            for y in range(height):
                row = f.readline()[:-1]
                for x in range(width):
                    character = row[x]
                    try:
                        cost = movingai_converter[character]
                    except KeyError:
                        raise ValueError(
                            f"we encountered the character {character} in moving ai map but we don't know how to convert it! Have you specified --movingai_converter?")
                    result.set_cell_value(y, x, cost)
            return result


def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(prog="MAPF Map Converter", description="""
    The software allows you to convert one map format to another one.
    This is useful for example between movingAI map file format and whoenig
    map file format (e.g., in ECBS).
    
    In order to work, the following is required:
     - python3.6
     - pyyaml
     
    Usage Example:
    
    python3.6 -m MAPFMapConverter \
        --input="hrt201n.map" \
        --input_format="movingai_1.0" \
        --output="hrt201n.yaml" \
        --output_format="whoenig_1.0" \
        --movingai_converter="{'.':1000, '@':float('+inf'), 'T':2000}"
    """)

    parser.add_argument("--input", type=str, required=True, help="""
        Input map file you wish to convert
    """)
    parser.add_argument("--output", type=str, required=True, help="""
        Output map file you wish to create
    """)
    parser.add_argument("--input_format", type=str, required=True, help=f"""
        Represents the format of the input file. Allowed values are:\n\n
        - {FORMAT_MOVINGAI}\n\n
        - {FORMAT_WHOENIG}\n\n
    """)
    parser.add_argument("--output_format", type=str, required=True, help="""
        Represents the format of the output file. Allowed values are the same of "input_format"
    """)
    parser.add_argument("--movingai_converter", type=str, default=None, required=False, help="""
        If the input is a movingAI, you need to specify how to interpret the characters in the map.
        This parameter is string which can be evaluated to a python dictionary value.
        The dictionary keys are the character read from the moving ai file and have as values the
        base costs of the terrains. 
        For example
        --movingai_converter="{'@': float('inf'), 'T':2000, '.':1000}" 
    """)
    parser.add_argument("--whoenig_base_terrain_cost", type=float, default=1000, help="""
        If the conversion involes the whoenig format you need to specify the base terrain cost
        thanks to this parameter
    """)

    options = parser.parse_args(sys.argv[1:])

    input = options.input
    output = options.output
    input_format = options.input_format
    output_format = options.output_format

    movingai_converter = options.movingai_converter
    whoenig_base_terrain_cost = options.whoenig_base_terrain_cost

    if input_format == FORMAT_MOVINGAI:
        input_map = MovingAIMapFormat.from_file(filename=input, movingai_converter=eval(movingai_converter))
    elif input_format == FORMAT_WHOENIG:
        input_map = WhoenigMapFormat.from_file(filename=input, basecost=whoenig_base_terrain_cost)
    else:
        raise ValueError(f"invlaid input format {input_format}!")

    if output_format == FORMAT_MOVINGAI:
        output_map = MovingAIMapFormat.create_from(input_map, movingai_converter=eval(movingai_converter))
    elif output_format == FORMAT_WHOENIG:
        output_map = WhoenigMapFormat.create_from(input_map, basecost=whoenig_base_terrain_cost)
    else:
        raise ValueError(f"invalid output format {output_format}!")

    with open(output, "w") as fout:
        fout.write(output_map.encode())


if __name__ == '__main__':
    main()
