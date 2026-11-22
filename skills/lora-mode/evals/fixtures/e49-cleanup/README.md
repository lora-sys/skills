# Cleanup fixture

`main.py` is the application entry point. Run the test suite with:

```sh
python3 -m unittest discover -s tests -v
```

The plugin loader reads handler names from `plugins.json`. Keep those modules even when a search finds no Python import.
