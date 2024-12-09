# Testing Instructions for Report Generator

## Prerequisites
Make sure you have Python installed on your machine. You will also need to install the `unittest` module, which is included in the standard library.

## Directory Structure
Ensure your project directory has the following structure:
```
your_project/
│
├── report_generator.py
├── tests/
│   ├── test_report_generator.py
│   └── TESTING.md
```

## Running the Tests
1. Open a terminal or command prompt.
2. Navigate to your project directory where `report_generator.py` is located.
3. Run the tests using the following command:
   ```bash
   python -m unittest discover -s tests
   ```

## Expected Output
You should see output indicating that the tests have run, along with a summary of the results. If all tests pass, you will see something like:
```
.
----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```
If any tests fail, the output will provide details about the failures.
