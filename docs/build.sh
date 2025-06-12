#!/bin/bash
rm -f experiments plotting data_release gwtc_data_releases
ln -s ../experiments experiments
ln -s ../plotting plotting
ln -s ../data_release data_release
ln -s ../gwtc_data_releases gwtc_data_releases
jupyter-book build .
