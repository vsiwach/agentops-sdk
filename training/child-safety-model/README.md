# Child Safety Model

## Install
```bash
ollama create child-safety -f Modelfile
```

## Usage
```python
import agentops
agentops.init(
    enable_llm_policy=True,
    llm_policy_model="child-safety",
    llm_base_url="http://localhost:11434/v1",
    llm_api_key="ollama"
)
```
