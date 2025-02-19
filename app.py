from flask import Flask, render_template, request, jsonify, send_file
import requests
import json
import os
from datetime import datetime
import re
import time

app = Flask(__name__)

# API配置
API_TOKEN = "your key"
CHAT_API_URL = "https://cephalon.cloud/user-center/v1/model/chat/completions"
IMAGE_API_URL = "https://cephalon.cloud/user-center/v1/model/comfyui"

# 确保存储图片的目录存在
UPLOAD_FOLDER = 'static/images'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def extract_think_and_prompt(text):
    """从AI响应中提取思考过程和最终提示词"""
    think_match = re.search(r'<think>(.*?)</think>', text, re.DOTALL)
    think_content = think_match.group(1).strip() if think_match else ""
    
    # 提取最终提示词（在</think>标签后的内容）
    final_prompt = re.sub(r'.*</think>\s*', '', text, flags=re.DOTALL).strip()
    
    return think_content, final_prompt

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-prompt', methods=['POST'])
def generate_prompt():
    max_retries = 2
    retry_count = 0
    
    while retry_count <= max_retries:
        try:
            user_prompt = request.form.get('prompt', '')
            if not user_prompt:
                return jsonify({'error': '请输入描述文字'}), 400

            # 调用AI生成提示词
            chat_headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {API_TOKEN}',
            }
            
            chat_data = {
                "model": "DeepSeek-R1-Distill-Qwen-32B",
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的AI绘图提示词专家。请帮助用户将中文描述转换为详细的AI绘图英文提示词，用逗号分隔关键词"
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                "stream": False
            }

            chat_response = requests.post(CHAT_API_URL, headers=chat_headers, json=chat_data)
            chat_response.raise_for_status()
            
            # 解析AI返回的内容
            ai_response = chat_response.json()['choices'][0]['message']['content'].strip()
            think_content, final_prompt = extract_think_and_prompt(ai_response)

            return jsonify({
                'success': True,
                'think_content': think_content,
                'final_prompt': final_prompt
            })

        except requests.exceptions.RequestException as e:
            retry_count += 1
            if retry_count > max_retries:
                return jsonify({'error': f'生成提示词过程中出错: {str(e)}'}), 500
            # 如果还有重试次数，等待一秒后继续
            time.sleep(1)
            continue

    return jsonify({'error': '服务器响应超时，请重试'}), 500

@app.route('/generate-image', methods=['POST'])
def generate_image():
    max_retries = 2
    retry_count = 0
    
    while retry_count <= max_retries:
        try:
            ai_prompt = request.form.get('ai_prompt', '')
            aspect_ratio = request.form.get('aspect_ratio', '1:1')
            
            if not ai_prompt:
                return jsonify({'error': '缺少AI提示词'}), 400

            # 根据选择的比例设置宽高
            aspect_ratios = {
                '1:1': (1024, 1024),
                '16:9': (1344, 768),
                '9:16': (768, 1344),
                '4:3': (1024, 768),
                '3:4': (768, 1024)
            }
            
            width, height = aspect_ratios.get(aspect_ratio, (1024, 1024))

            # 调用图片生成API
            image_headers = {
                'Authorization': f'Bearer {API_TOKEN}',
                'Model-Id': '1854732937730371541',
                'Content-Type': 'application/json'
            }
            
            image_data = {
                "prompt": ai_prompt,
                "width": width,
                "height": height,
                "guidance_scale": 3.5,
                "seed": 320521890,
                "steps": 25
            }

            image_response = requests.post(IMAGE_API_URL, headers=image_headers, json=image_data)
            image_response.raise_for_status()

            # 保存生成的图片
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_filename = f'generated_{timestamp}.png'
            image_path = os.path.join(UPLOAD_FOLDER, image_filename)
            
            with open(image_path, 'wb') as f:
                f.write(image_response.content)

            return jsonify({
                'success': True,
                'message': '图片生成成功',
                'image_url': f'/static/images/{image_filename}',
                'image_filename': image_filename
            })

        except requests.exceptions.RequestException as e:
            retry_count += 1
            if retry_count > max_retries:
                return jsonify({'error': f'生成图片过程中出错: {str(e)}'}), 500
            # 如果还有重试次数，等待一秒后继续
            time.sleep(1)
            continue

    return jsonify({'error': '服务器响应超时，请重试'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_file(
            os.path.join(UPLOAD_FOLDER, filename),
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': f'下载文件时出错: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)