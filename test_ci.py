# The CI failed specifically for `test._3_7`
# Message: The version '3.7' with architecture 'x64' was not found for Ubuntu 24.04.
# The other tests were cancelled.
# We just need to remove python 3.7 and 3.8 from the CI since they are unsupported on Ubuntu 24.04 actions environment.
