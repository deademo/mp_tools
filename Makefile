dev: upload

upload:
	python3 tools/upload.py

upload_firmware:
	esptool.py --port /dev/tty.wchusbserial1420 --baud 460800 erase_flash
	esptool.py --port /dev/tty.wchusbserial1420 --baud 460800 write_flash --flash_size=detect -fm dio 0 firmware/esp8266-20171101-v1.9.3.bin --verify

upload_wired:
	ampy --port /dev/tty.wchusbserial1420 -d 1 put boot.py
	ampy --port /dev/tty.wchusbserial1420 -d 1 put picoweb.py
	ampy --port /dev/tty.wchusbserial1420 -d 1 put wlog.py

python: upload_firmware upload_wired

connect_wired:
	screen /dev/tty.wchusbserial1420 115200

connect:
	python3 tools/connect.py

compile_micropython:
	brew install libffi
	sudo port install pkgconfig
	sh -c "git clone https://github.com/micropython/micropython-lib; echo 'done'"
	sh -c "git clone https://github.com/pfalcon/micropython; echo 'done'"
	cd micropython && git submodule update --init
	cd micropython/ports/unix && make

clear:
	rm -rf micropython
	rm -rf micropython-lib
