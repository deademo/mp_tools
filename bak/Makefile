upload_wired:
	cd ~/Documents/esp/
	echo "Started uploading"
	until nodemcu-uploader --timeout 10 --port /dev/tty.wchusbserial1420 upload devserver.lua credentials.lua init.lua; do sleep 1; done

upload:
	python3 upload.py

lua: flash upload_wired

flash:
	esptool.py --port /dev/tty.wchusbserial1420 erase_flash
	esptool.py --port /dev/tty.wchusbserial1420  --baud 460800 write_flash --flash_size=detect 0 ~/Downloads/nodemcu-master-7-modules-2018-02-10-16-03-43-float.bin --verify

connect:
	screen /dev/tty.wchusbserial1420 115200

dev: upload

test_upload: 
	curl -X POST -d "test-test-test" http://192.168.1.13/upload
