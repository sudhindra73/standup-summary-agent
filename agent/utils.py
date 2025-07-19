import yaml

def load_team_config(path="config/team.yaml"):
    with open(path, 'r') as f:
        return yaml.safe_load(f)