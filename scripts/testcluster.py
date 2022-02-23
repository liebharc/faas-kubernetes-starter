#!/usr/bin/python

import sys
import re
import requests

def capture_std_out_of_command(command, numberOfLines = -1):
    import subprocess
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    capture = ""

    s = process.stdout.read(1)
    while len(s) > 0:
        sys.stdout.write(s)
        sys.stdout.flush()
        capture += s
        if numberOfLines > 0 and len(capture.splitlines()) >= numberOfLines:
            break
        s = process.stdout.read(1)

    return capture

def open_tunnel_and_get_url():
    stdout = capture_std_out_of_command("minikube service ingress-nginx-controller --namespace ingress-nginx --url", numberOfLines=9)
    print(stdout)
    is_host = re.compile("(http://(.*):(.*))")
    for line in stdout.splitlines():
        match = is_host.match(line)
        if match:
            return match.group(1)
    return None


url = open_tunnel_and_get_url()
hello_url = url + "/v1/hello"
print("Hello URL: " + hello_url)
print(requests.get(hello_url).text)