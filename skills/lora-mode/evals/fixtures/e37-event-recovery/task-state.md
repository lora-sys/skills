# Active task checkpoint

## Original request

Fix the fee importer so it accepts `$1,234.50` and plain decimals, rejects blank or malformed input instead of silently treating it as zero, and identifies the physical input line in errors. Add regression tests for valid input, blank and malformed rows, and line numbers. Update this README's format and usage example. Run the documented tests and use `sample_fees.txt` with the CLI. Do not add dependencies.

## Last known progress

- The CLI and parser exist, and the original three tests cover plain and dollar amounts.
- The last local test run passed before the comma formatted amount was added to the sample.
- The README still documents only plain amounts and its commands use `python`.
- No evidence exists that the current checkout passes the full request. Re-read the files and verify current state before relying on this checkpoint.

## Remaining acceptance

- Parse comma grouped dollar amounts and ordinary decimals correctly.
- Reject blank and malformed rows with the physical line number.
- Add regression tests for valid formats, empty/bad rows and the reported line number.
- Update the README format and usage example.
- Run the documented test command and CLI sample, using an available Python interpreter if the documented one is absent.
- Record actual commands, results and any remaining blocker here before reporting completion.
