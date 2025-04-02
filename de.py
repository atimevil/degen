import json
import sys
import re
from pycparser import c_ast

def from_json_to_ast(ast_json_path):
    """Load JSON and convert to AST"""
    with open(ast_json_path, 'r') as f:
        ast_dict = json.load(f)
    return from_dict(ast_dict)

def from_dict(node_dict):
    """Convert dictionary representation to AST nodes"""
    class_name = node_dict.pop('_nodetype')
    klass = getattr(c_ast, class_name)
    
    objs = {}
    for key, value in node_dict.items():
        if key == 'coord':
            objs[key] = _parse_coord(value)
        else:
            objs[key] = _convert_to_obj(value)
    
    return klass(**objs)

def _parse_coord(coord_str):
    """Parse coordinate string"""
    if coord_str is None:
        return None
    
    vals = coord_str.split(':')
    vals.extend([None] * 3)
    filename, line, column = vals[:3]
    return c_ast.Coord(filename, line, column)

def _convert_to_obj(value):
    """Convert dict/list objects recursively"""
    if isinstance(value, dict):
        return from_dict(value)
    elif isinstance(value, list):
        return [_convert_to_obj(item) for item in value]
    else:
        return value

def reconstruct_c_code(ast_json_path, output_path=None):
    """Main function to convert AST JSON to C code"""
    ast = from_json_to_ast(ast_json_path)
    c_code = generate_c_code(ast)
    
    if output_path:
        with open(output_path, 'w') as f:
            f.write(c_code)
    else:
        return c_code

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else None
        
        if output_path:
            reconstruct_c_code(input_path, output_path)
            print(f"C code reconstructed and saved to {output_path}")
        else:
            code = reconstruct_c_code(input_path)
            print(code)
    else:
        print("Usage: python reconstruct.py ast.json [output.c]")
