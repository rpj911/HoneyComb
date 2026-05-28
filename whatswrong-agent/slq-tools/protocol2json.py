import re
import json
import unittest

def protocolToDict(text: str) -> dict:
    """
    Parse structured text in the format:
    key: value = data
    key: value = {
        nested content
    }
    
    Returns a dict
    """
    
    def tokenize(text: str):
        """Tokenize the input text into meaningful parts"""
        tokens = []
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line == '{':
                tokens.append(('OPEN_BRACE', '{'))
            elif line == '}':
                tokens.append(('CLOSE_BRACE', '}'))
            else:
                # Match pattern: key: value = data
                match = re.match(r'^([^:]+):\s*value\s*=\s*(.+)$', line)
                if match:
                    key = match.group(1).strip()
                    value = match.group(2).strip()
                    if value == '{':
                        tokens.append(('KEY', key))
                        tokens.append(('OPEN_BRACE', '{'))
                    else:
                        tokens.append(('KEY_VALUE', (key, value)))
        
        return tokens
    
    def parse_tokens(tokens):
        """Parse tokens into a nested dictionary structure with array support for duplicate keys"""
        result = {}
        i = 0
        
        while i < len(tokens):
            token_type, token_value = tokens[i]
            
            if token_type == 'KEY_VALUE':
                key, value = token_value
                converted_value = convert_value(value)
                
                # Handle duplicate keys by creating arrays
                if key in result:
                    if not isinstance(result[key], list):
                        result[key] = [result[key]]
                    result[key].append(converted_value)
                else:
                    result[key] = converted_value
                i += 1
                
            elif token_type == 'KEY':
                key = token_value
                i += 1
                # Next token should be OPEN_BRACE
                if i < len(tokens) and tokens[i][0] == 'OPEN_BRACE':
                    i += 1
                    # Parse nested content
                    nested_result, new_i = parse_nested(tokens, i)
                    
                    # Handle duplicate keys by creating arrays
                    if key in result:
                        if not isinstance(result[key], list):
                            result[key] = [result[key]]
                        result[key].append(nested_result)
                    else:
                        result[key] = nested_result
                    i = new_i
                else:
                    raise ValueError(f"Expected opening brace after key '{key}'")
            else:
                i += 1
                
        return result
    
    def parse_nested(tokens, start_index):
        """Parse nested content within braces with array support for duplicate keys"""
        result = {}
        i = start_index
        brace_count = 1  # We already encountered one opening brace
        
        while i < len(tokens) and brace_count > 0:
            token_type, token_value = tokens[i]
            
            if token_type == 'CLOSE_BRACE':
                brace_count -= 1
                if brace_count == 0:
                    break
                i += 1
                
            elif token_type == 'KEY_VALUE':
                key, value = token_value
                converted_value = convert_value(value)
                
                # Handle duplicate keys by creating arrays
                if key in result:
                    if not isinstance(result[key], list):
                        result[key] = [result[key]]
                    result[key].append(converted_value)
                else:
                    result[key] = converted_value
                i += 1
                
            elif token_type == 'KEY':
                key = token_value
                i += 1
                if i < len(tokens) and tokens[i][0] == 'OPEN_BRACE':
                    i += 1
                    brace_count += 1
                    nested_result, new_i = parse_nested(tokens, i)
                    
                    # Handle duplicate keys by creating arrays
                    if key in result:
                        if not isinstance(result[key], list):
                            result[key] = [result[key]]
                        result[key].append(nested_result)
                    else:
                        result[key] = nested_result
                    i = new_i
                    brace_count -= 1  # Closing brace will be handled in next iteration
                else:
                    raise ValueError(f"Expected opening brace after key '{key}'")
            else:
                i += 1
        
        return result, i + 1
    
    def convert_value(value_str):
        return value_str.strip()
    
    try:
        tokens = tokenize(text)
        result = parse_tokens(tokens)
        return result
    except Exception as e:
        raise ValueError(f"Failed to parse structured text: {str(e)}")

if __name__ == '__main__':
    hdr_full_path = "CT55.4245.1.1.1397560845.140840.protocol"
    hdr_anon_path = "CT55.4245.1.1.1397560845.140840.protocol.a"
    with open(hdr_full_path, 'r') as hf:
        hdr_full_text = hf.read()
    with open(hdr_anon_path, 'r') as ha:
        hdr_anon_text = ha.read()
    hdr_full_dict = protocolToDict(hdr_full_text)
    hdr_anon_dict = protocolToDict(hdr_anon_text)