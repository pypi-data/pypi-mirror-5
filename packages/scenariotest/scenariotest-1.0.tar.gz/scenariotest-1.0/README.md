scenariotest
============

This testing helper-class was taken from a gist written by github user
‘bigjason’. It combines a prototypical test case with a list of dictionaries
(each a dict of keyword arguments) and transforms the two into a series of
unittest-compatible test cases. The advantage of this approach is that an
identical test can be applied to multiple scenarios with minimal repetition
of code, while still having each scenario tested independently and reported
to the user by the test runner.

Example of usage can be found in the file xunit.py, or on
bigjason's blog post which introduced the concept:

    <http://www.bigjason.com/blog/scenario-testing-python-unittest/>

The original code this was based off of can be found on GitHub:

    <https://gist.github.com/856821/8966346d8e50866eae928ababa86acea6504bcee>
