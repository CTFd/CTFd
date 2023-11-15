# How to add unit-tests for plugins?

## Steps

1. Create a new branch for the tests. For example: a branch named `flags-plugin-tests`.
2. Add a directory `tests` to the plugin. For example: `flags` will have a `flags/tests`.
3. Add an empty `__init__.py` file to the directory, for package initialization.
4. Add a test file in the format `test_*.py` with your unit-tests to the directory. For example: `test_flags.py`.
5. Run your tests in a terminal with: `pytest *path to test file*`. For example: `pytest CTFd/plugins/flags/tests/test_flags.py` .
6. If the tests succeed locally, you can push to your branch. `make test` in `.gitlab-ci.yml` will run all the tests in the entire repository in the pipeline.
7. Next issue a merge request to merge your tests into the main branch.
