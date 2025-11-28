#!/bin/bash
export JAVA_HOME=/opt/android-studio/jbr
export PATH=$JAVA_HOME/bin:$PATH
cd /home/dniel/django/photo_album_app
flutter devices
echo ""
echo "Available devices listed above."
echo "To run on emulator, use: flutter run -d emulator-5554"
