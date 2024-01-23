from flask import Flask, request, jsonify
import requests
import re
from flask_cors import CORS
import execjs
import json
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['CORS_ALLOW_ORIGINS'] = '*'
app.config['CORS_ALLOW_METHODS'] = ['GET', 'POST']
app.config['CORS_ALLOW_HEADERS'] = ['Content-Type', 'Authorization']


def extract_link_id(url):
  pattern = r'explore/(\w+)'
  match = re.search(pattern, url)
  if match:
    link_id = match.group(1)
    return link_id
  else:
    return None


def get_response(url):
  headers = {
      "User-Agent":
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
  }
  try:
    r = requests.get(url, headers=headers)
    r.encoding = 'utf-8'
    return r
  except requests.exceptions.RequestException as e:
    print("请求发生异常:", e)
    return None


headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "no-cache",
    "content-type": "application/json;charset=UTF-8",
    "origin": "https://www.xiaohongshu.com",
    "pragma": "no-cache",
    "referer": "https://www.xiaohongshu.com/",
    "sec-ch-ua":
    "\"Chromium\";v=\"112\", \"Google Chrome\";v=\"112\", \"Not:A-Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "x-b3-traceid": "a31fffc0ee4f5d8f",
    "X-S-Common": ""
}


def getXs(cookie, api, data):
  current_directory = os.path.dirname(__file__)
  file_path = os.path.join(current_directory, "note_detail.js")
  with open(file_path, 'r', encoding='utf-8') as f:
    jstext = f.read()

  ctx = execjs.compile(jstext)

  match = re.search(r'a1=([^;]+)', cookie)
  a1 = ""
  if match:
    a1 = match.group(1)
  else:
    print("关键参数a1获取失败，请检查你的cookie")
    return "Cookie 配置错误"

  result = ctx.call("XsXt", api, data, a1)
  return result


def sentRequest(host, api, data, cookie):
  xs_xt = getXs(cookie, api, data)

  headers['cookie'] = cookie
  headers['X-s'] = xs_xt['X-s']
  headers['X-t'] = str(xs_xt['X-t'])

  url = host + api
  response = requests.post(url=url,
                           data=json.dumps(data,
                                           separators=(",", ":"),
                                           ensure_ascii=False).encode("utf-8"),
                           headers=headers)

  return response.json()


# 提取详细的笔记信息
def DoApi(param, cookie):
  api = '/api/sns/web/v1/feed'  # put the api there
  host = 'https://edith.xiaohongshu.com'
  data = {
      "source_note_id": param["note_id"],
  }

  return sentRequest(host, api, data, cookie)


# 提取简略的笔记信息
def extracted_xhs_rough_info(url):
  html = get_response(url).text

  filename = 'html.txt'
  with open(filename, 'w', encoding='utf-8') as file:
    file.write(html)

  patterns = {
      "collectionCount": r'"collectedCount":"(\d+[k|w]*)\+*"',
      "commentCount": r'"commentCount":"(\d+[k|w]*)\+*"',
      "shareCount": r'"shareCount":"(\d+[k|w]*)\+*"',
      "likeCount": r'"likedCount":"(\d+[k|w]*)\+*"',
      "lastUpdateTime": r'"lastUpdateTime":(.*?)}*,',
      "releaseTime": r',"time":(.*?)}*,',
      "title": r',"title":"([^"]+)"',
      "uploader": r'"nickname":"([^"]+)"'
  }

  # 提取信息
  extracted_info = {}
  for key, pattern in patterns.items():
    match = re.search(pattern, html)
    if match:
      value = match.group(1)
      print(key, value)
      if key in ["collectionCount", "commentCount", "likeCount", "shareCount"]:
        # 处理带有 k 或 K 的数字
        if 'k' in value.lower():
          value = float(value.lower().replace('k', '')) * 1000
        elif 'w' in value.lower():
          value = float(value.lower().replace('w', '')) * 10000
        extracted_info[key] = int(value)
      elif key in ["releaseTime", "lastUpdateTime"]:
        extracted_info[key] = int(match.group(1))
      else:
        extracted_info[key] = value
    else:
      # 如果没有找到匹配项，可以根据需要设置为 None 或其他默认值
      extracted_info[key] = None

  print(extracted_info)
  return extracted_info


# 1. 小红书基本数据
@app.route('/get_xhs_rough_data', methods=['POST'])
def get_xhs_data():
  # 使用 request.form 来获取表单数据
  url = request.form.get('url')
  print(url)

  if not url:
    return jsonify({"status": -100, "error": "No video URL provided"}), 400

  # 使用提供的类和函数处理视频
  xhs_info = extracted_xhs_rough_info(url)
  # 返回数据和图像
  return jsonify({"status": 200, "info": xhs_info})


@app.route('/get_xhs_detail_data', methods=['POST'])
def get_xhs_detail_data():
  # 使用 request.form 来获取表单数据
  url = request.form.get('url')

  cookie = request.form.get('cookie')
  xscommon = request.form.get('xSCommon')

  param = {"note_id": extract_link_id(url)}

  print("note_id", param["note_id"])
  print("cookie", len(cookie))
  print("xscommon", xscommon)
  headers["X-S-Common"] = str(xscommon)

  if not url or not cookie:
    return jsonify({"status": -100, "error": "No video URL provided"}), 400

  # 使用提供的类和函数处理视频
  xhs_detail_info = DoApi(param, cookie)
  # 返回数据和图像
  return jsonify({"status": 200, "info": xhs_detail_info})


app.run(host='0.0.0.0', port=81)
