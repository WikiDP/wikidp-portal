#!/usr/bin/env bash
if (($1 == visual))
then
  py.test --cov=wikidp tests --cov-report html
  open htmlcov/index.html
else
  py.test --cov=wikidp tests
  coverage report
fi
