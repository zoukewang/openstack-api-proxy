from flask import Flask
from flask import request
import json
import os
import time
import re
import traceback

app = Flask(__name__)

@app.route("/vimproxy", methods=['POST'])
def add_vim_proxy():
    data = json.loads(request.data)
    vimid = data["vimid"]
    vimurl = data["vimurl"]
    print("recieve add vim proxy vimid=" + vimid + ", vimurl=" + vimurl)
    try:
        add_vimproxy(vimid, vimurl)
        reload_nginx()
        return "add vim proxy ok"
    except Exception as e:
        traceback.print_exc()
        return "add vim proxy failed + " + str(e)

@app.route("/vimproxy/<vimid>", methods=['DELETE'])
def del_vim_proxy(vimid):
    print("recieve del vim proxy vimid=" + vimid)
    try:
        del_vimproxy(vimid)
        reload_nginx()
        return "del vim proxy ok"
    except Exception as e:
        traceback.print_exc()
        return "del vim proxy failed + " + str(e)

@app.route("/vimproxy", methods=['GET'])
def get_vim_proxy():
    print("recieve get vim proxy")
    try:
        ret = get_vimproxy()
        return {"vimproxys": ret}
    except Exception as e:
        traceback.print_exc()
        return "get vim proxy failed + " + str(e)

filename = "/usr/local/nginx/conf/default.conf"
now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
servers = ["5000", "35357", "8774", "9292", "9696", "8776", 8004]
proxyurl = "http://" + os.environ.get("PROXY_IP")

def reload_nginx():
    os.system("/usr/local/nginx/sbin/nginx -s reload")

def create_location_with_filter(vimid, vimurl, port, version):
    ret = []
    ret.append("    location /" + vimid + "/" + version + "/ {\n")
    ret.append("        proxy_pass {}:{}/{}/;\n".format(vimurl, port, version))
    ret.append("        proxy_set_header Accept-Encoding \"\";\n")
    ret.append("        sub_filter_once off;\n")
    ret.append("        sub_filter_types *;\n")
    for port in servers:
        if version == "v2.0":
            ret.append("        sub_filter '\"publicURL\": \"{}:{}' '\"publicURL\": \"{}:{}/{}';\n".format(vimurl, port, proxyurl, port, vimid))
        else:
            ret.append("        sub_filter '\"url\": \"{}:{}' '\"url\": \"{}:{}/{}';\n".format(vimurl, port, proxyurl, port, vimid))
    ret.append("    }\n")
    return ret

def create_location(vimid, vimurl, port):
    ret = []
    ret.append("    # " + now + "\n")
    ret.append("    location /" + vimid + "/ {\n")
    ret.append("        proxy_pass {}:{}/;\n".format(vimurl, port))
    ret.append("    }\n")
    return ret

def check_location(vimid):
    with open(filename, 'r') as file:
        for line in file:
            if (line.find("location /" + vimid) >= 0):
                return True
    return False

def add_location(lines, port, vimid, vimurl):
    for line in create_location(vimid, vimurl, port):
        lines.append(line)
    if port == "5000" or port == "35357":
        for line in create_location_with_filter(vimid, vimurl, port, "v3"):
            lines.append(line)
        for line in create_location_with_filter(vimid, vimurl, port, "v2.0"):
            lines.append(line)

def add_vimproxy(vimid, vimurl):
    lines = []
    index = 0

    if check_location(vimid):
        print(vimid + " is exist!")
        return
    with open(filename, 'r') as file:
        for line in file:
            lines.append(line)
            if (line.find("error_page") >= 0):
                add_location(lines, servers[index], vimid, vimurl)
                index += 1
    s = ''.join(lines)
    with open(filename, 'w') as file:
        file.write(s)

def del_vimproxy(vimid):
    lines = []

    if not check_location(vimid):
        print(vimid + " is not exist!")
        return
    with open(filename, 'r') as file:
        for line in file:
            lines.append(line)

    for i, d in enumerate(lines):
        if (d.find("location /" + vimid) >= 0):
            lines[i-1] = ""
            for index in range(3):
                lines[i+index] = ""
        if (d.find("location /" + vimid + "/v") >= 0):
            for index in range(13):
                lines[i+index] = ""
    s = ''.join(lines)
    with open(filename, 'w') as file:
        file.write(s)

def get_vimproxy():
    lines = []
    ret = []

    with open(filename, 'r') as file:
        for line in file:
            lines.append(line)

    for i, d in enumerate(lines):
        print(d)
        vimidre = re.search(r"location /(.*)/", d)
        if vimidre:
            v = {}
            v["vimid"] = vimidre.groups()[0]
            vimurlre = re.search(r"(http:.*):", lines[i+1])
            v["vimurl"] = vimurlre.groups()[0]
            if (v["vimid"] not in [item["vimid"] for item in ret]) and (v["vimid"].find("/v") < 0):
                ret.append(v)
    return ret
