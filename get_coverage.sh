#!/bin/sh

pytest --cov=singleton_class_decorator tests/ | grep TOTAL | cut -f 51- -d ' '