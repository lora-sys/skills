# Feature review fixture

`baseline/` is the code before the summary export feature. `working/` is the current feature diff.
Run the tests from `working/` with:

```sh
python3 -m unittest discover -s tests -v
```

Only the summary export feature and its direct caller belong to this review.
