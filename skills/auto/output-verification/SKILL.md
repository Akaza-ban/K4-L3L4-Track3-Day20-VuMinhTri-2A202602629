---
name: output-verification
description: Verify all required output files exist, are correctly formatted, and match specifications exactly before finishing the task.
---
Final verification checklist:
1. **Path check**: ensure all output files are written to the correct location (check working directory, absolute paths). Use `os.path.join` or verify with `ls`/`cat`.
2. **Format check**: read back the output file and validate it against the spec (JSON structure, CSV headers, timestamp formats, rounding, quoting).
3. **Edge-case check**: test with the specific failing inputs from any feedback you've received.
4. **Run the tests**: if there are test suites, run them to confirm everything passes.
5. **Don't leave early**: if the task isn't fully complete (e.g., output file not yet created), don't stop — finish creating all required outputs first.
