dev: upload

upload:
	python tools/upload.py

upload_firmware:
	esptool.py --port /dev/tty.wchusbserial1420 --baud 460800 erase_flash
	esptool.py --port /dev/tty.wchusbserial1420 --baud 460800 write_flash --flash_size=detect -fm dio 0 firmware/esp8266-20171101-v1.9.3.bin --verify

upload_wired:
	ampy --port /dev/tty.wchusbserial1420 -d 1 put main.py
	ampy --port /dev/tty.wchusbserial1420 -d 1 put wlog.py
	ampy --port /dev/tty.wchusbserial1420 -d 1 put discovery.py
	ampy --port /dev/tty.wchusbserial1420 -d 1 put app.py
	ampy --port /dev/tty.wchusbserial1420 -d 1 put screen.py
	ampy --port /dev/tty.wchusbserial1420 -d 1 put hashfile.py
	ampy --port /dev/tty.wchusbserial1420 -d 1 put settings.py
	ampy --port /dev/tty.wchusbserial1420 -d 1 put settings_local.py
	ampy --port /dev/tty.wchusbserial1420 -d 1 put upload.py
	ampy --port /dev/tty.wchusbserial1420 -d 1 put wifi.py
	ampy --port /dev/tty.wchusbserial1420 -d 1 put deaweb.mpy


upload_wired_windows:
	set AMPY_PORT=COM5
	ampy -d 1 put main.py
	ampy -d 1 put wlog.py
	ampy -d 1 put discovery.py
	ampy -d 1 put app.py
	ampy -d 1 put screen.py
	ampy -d 1 put hashfile.py
	ampy -d 1 put settings.py
	ampy -d 1 put settings_local.py
	ampy -d 1 put upload.py
	ampy -d 1 put wifi.py
	ampy -d 1 put deaweb.mpy


deps:
	-git clone https://github.com/deademo/deaweb
	-@copy /y deaweb\deaweb.mpy deaweb.mpy
	-@cp deaweb/deaweb/deaweb.py deaweb.py
	-rmdir /S /Q deaweb
	-rm -rf deaweb

init_windows: upload_firmware_windows deps upload_wired_windows connect

deps_compile: mpy-cross
	git clone https://github.com/deademo/deaweb
	@cp deaweb/deaweb/deaweb.py deaweb.py
	./mpy-cross deaweb.py
	rm deaweb.py
	rm -rf deaweb	

upload_firmware_windows:
	esptool.py --port COM5 --baud 460800 erase_flash
	esptool.py --port COM5 --baud 460800 write_flash --flash_size=detect -fm dio 0 firmware/esp8266-20171101-v1.9.3.bin --verify

python: upload_firmware upload_wired

connect_wired:
	screen /dev/tty.wchusbserial1420 115200

connect:
	python tools/connect.py

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

discovery:
	python tools/discovery.py

mpy-cross:
	git clone https://github.com/pfalcon/micropython
	cd micropython/mpy-cross && make
	cp micropython/mpy-cross/mpy-cross mpy-cross

mpy:
	./mpy-cross deaweb.py
