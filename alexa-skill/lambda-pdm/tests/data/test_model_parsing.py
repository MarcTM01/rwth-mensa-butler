import json
from pathlib import Path

from src.data.menu_model import MensaDayMenus


def test_model_parsing():
    """Test the parsing of the model from a json file."""
    model_path = Path(__file__).parent / 'example_model.json'
    assert model_path.exists()
    assert model_path.is_file()

    with open(model_path, 'r') as f:
        model = json.load(f)

    MensaDayMenus(**model)
