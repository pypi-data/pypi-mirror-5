#!/bin/sh

#
# This is the path to the sikuli-script jar as found on osx, update to reflect
# your platform
#
PATH_TO_SIKULI_JAR=/Applications/Sikuli-IDE.app/Contents/Resources/Java/
cd src
java -cp "$PATH_TO_SIKULI_JAR/sikuli-script.jar" org.python.util.jython -m jython_sikuli_server
cd ..
