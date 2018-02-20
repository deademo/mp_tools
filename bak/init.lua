-- load credentials, 'SSID' and 'PASSWORD' declared and initialize in there
dofile("credentials.lua")

function led_on()
    pin = 4;
    gpio.mode(pin, gpio.OUTPUT); 
    gpio.write(pin, gpio.LOW);
end

function led_off()
    pin = 4;
    gpio.mode(pin, gpio.OUTPUT); 
    gpio.write(pin, gpio.HIGH);
end

function with_delay(delay, func)
    if delay == 0 then
        func()
        return nil
    end
    tmr.create():alarm(delay, tmr.ALARM_SINGLE, func)
end

function blink_ready()
    count = 2
    for i=0,count*2-1,1 do
        local needed_func = led_off
        if i % 2 == 0 then
            needed_func = led_on
        end
        with_delay(i*100, needed_func)
    end
end

-- Define WiFi station event callbacks 
wifi_connect_event = function(T) 
  print("Connection to AP("..T.SSID..") established!")
  print("Waiting for IP address...")
  if disconnect_ct ~= nil then disconnect_ct = nil end  
end

wifi_got_ip_event = function(T)
  -- Note: Having an IP address does not mean there is internet access!
  -- Internet connectivity can be determined with net.dns.resolve().    
  print("Wifi connection is ready! IP address is: "..T.IP)
  blink_ready()
  -- print("Startup will resume momentarily, you have 1 second to abort.")
  -- print("Waiting...") 
  -- tmr.create():alarm(1000, tmr.ALARM_SINGLE, startup)
end

wifi_disconnect_event = function(T)
  if T.reason == wifi.eventmon.reason.ASSOC_LEAVE then 
    --the station has disassociated from a previously connected AP
    return 
  end
  -- total_tries: how many times the station will attempt to connect to the AP. Should consider AP reboot duration.
  local total_tries = 5
  print("\nWiFi connection to AP("..T.SSID..") has failed!")

  --There are many possible disconnect reasons, the following iterates through 
  --the list and returns the string corresponding to the disconnect reason.
  for key,val in pairs(wifi.eventmon.reason) do
    if val == T.reason then
      print("Disconnect reason: "..val.." ("..key..")")
      break
    end
  end

  if disconnect_ct == nil then 
    disconnect_ct = 1 
  else
    disconnect_ct = disconnect_ct + 1 
  end
  if disconnect_ct < total_tries then 
    print("Retrying connection...(attempt "..(disconnect_ct+1).." of "..total_tries..")")
  else
    wifi.sta.disconnect()
    print("Aborting connection to AP!")
    disconnect_ct = nil
    node:restart()
  end
end

-- Register WiFi Station event callbacks
wifi.eventmon.register(wifi.eventmon.STA_CONNECTED, wifi_connect_event)
wifi.eventmon.register(wifi.eventmon.STA_GOT_IP, wifi_got_ip_event)
wifi.eventmon.register(wifi.eventmon.STA_DISCONNECTED, wifi_disconnect_event)

dofile("devserver.lua")

print("Connecting to WiFi access point...")
print("ssid="..SSID..", pwd="..PASSWORD)
wifi.setmode(wifi.STATION)
wifi.sta.config({ssid=SSID, pwd=PASSWORD})
-- wifi.sta.connect() not necessary because config() uses auto-connect=true by default
