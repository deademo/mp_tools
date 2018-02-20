print("Executing application.lua")

port = 80
timeout = 5

_BUFFER = {}

function buffer_append(str)
    table.insert(_BUFFER, str)
end

function buffer_erase()
    _BUFFER = {}
end

function buffer_get(part)
    if part ~= nil then
        return _BUFFER[part]
    else
        return _BUFFER
    end
end

function buffer_payload_length()
    local length = 0
    if not #_BUFFER then
        return length
    end

    local _, _, first_message_payload = string.find(_BUFFER[1], "\r\n\r\n(.*)")

    for i, item in ipairs(_BUFFER) do
        if i == 1 then
            item = first_message_payload
        end
        length = length + item:len()
    end

    return length
end

function split(string, separator)
    lines = {}
    string:gsub("([^"..separator.."]*)"..separator, function(c)
       table.insert(lines, c)
    end)
    return lines
end

function strip(s)
    return (s:gsub("^%s*(.-)%s*$", "%1"))
end

function handler_upload(client, request, params)
    filename = params['filename']
    print(request)
    if filename then
        print('Filename:\n'..filename)
    else
        print('No filename provided')
        return nil
    end

    local _, _, payload = string.find(request, "\r\n\r\n(.*)")
    if payload then
        payload = strip(payload)
    end
    if file.open(filename, 'w') then
        for i, current_payload in ipairs(buffer_get()) do
            if i == 1 then
                current_payload = payload
            end
            file.write(current_payload)
        end
        file.close()
        print('Writen new file "'..filename..'"')
    end

    local http_response = ""..
        "HTTP/1.1 200 OK\r\n"..
        "Server: esp8266 server\r\n"..
        "Content-Length: %s\r\n"..
        "Content-Type: text/html\r\n"..
        "Connection: Closed\r\n\r\n"..
        "%s\r\n"
    local data = "ok"
    local response = string.format(http_response, string.len(data), data)

    if params['restart'] then
        print('Got restart command')
        client:send(response, function()
            node:restart()
        end)
    end

    return response
end

function handler_mem(client, request, params)
    local http_response = ""..
        "HTTP/1.1 200 OK\r\n"..
        "Server: esp8266 server\r\n"..
        "Content-Length: %s\r\n"..
        "Content-Type: text/html\r\n"..
        "Connection: Closed\r\n\r\n"..
        "%s\r\n"
    local data = tostring(node.heap())
    local response = string.format(http_response, string.len(data), data)
    return response
end

function handler_404(client, request, params)
    local http_response = ""..
        "HTTP/1.1 404 Not Found\r\n"..
        "Server: esp8266 server\r\n"..
        "Content-Length: %s\r\n"..
        "Content-Type: text/html\r\n"..
        "Connection: Closed\r\n\r\n"..
        "%s\r\n"
    local data = "Not found"

    return string.format(http_response, string.len(data), data)
end

function parse_first_line(request)
    local _, _, method, path, vars = string.find(request, "([A-Z]+) (.+)?(.+) HTTP")
    if method == nil then
        _, _, method, path = string.find(request, "([A-Z]+) (.+) HTTP")
    end

    return method, path, vars
end

function receiver(client, request)
    local content_length = nil
    local method, path, vars = parse_first_line(request)

    if method then
        local port, ip = client:getpeer()
        local request_meta = split(request, "\r\n")[1]
        if not request_meta then request_meta = 'nil' end
        print(string.format("From %s: %s", ip, request_meta))

        buffer_erase()
    end
    buffer_append(request)

    local buffer = buffer_get(1)
    _, _, content_length = string.find(buffer, 'Content%-Length: (%d+)')
    content_length = tonumber(content_length)
    if content_length then
        local _, _, payload = string.find(buffer, "\r\n\r\n(.*)")
        if buffer_payload_length() ~= content_length then
            print('Got just part of request. Do not handling it.')
            return false
        end
    end

    handle(client, buffer)
    collectgarbage()
end

function handle(client, request)
    local method, path, vars = parse_first_line(request)

    local params = {}
    if vars ~= nil then
        for k, v in string.gmatch(vars, "([%w%-%.]+)=([%w%-%.]+)&*") do
            params[k] = v
            -- print(string.format('%s = %s', k, v))
        end
    end

    router = {}
    router["POST /upload"] = handler_upload
    router["GET /mem"] = handler_mem
    handler = router[method.." "..path]
    if handler == nil then
        handler = handler_404
    end

    pcall(function()
        client:send(handler(client, request, params))
    end)
end

local server = net.createServer(net.TCP, 30)
if server then
    server:listen(port, function(connection)
        connection:on("receive", receiver)
    end)
end