import yaml
import os

def load_config(config_path='config/config.yaml'):
    """
    Load configuration from a YAML file.

    Parameters:
    - config_path (str): The path to the configuration file.

    Returns:
    - dict: The configuration dictionary.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    return config
