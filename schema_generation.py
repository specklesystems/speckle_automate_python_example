import json
from main import FunctionInputs


if __name__ == "__main__":
    print(json.dumps(FunctionInputs.model_json_schema()))