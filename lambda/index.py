import json
import os
import urllib.request
import urllib.error

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))

        # リクエストボディを読み取る
        body = json.loads(event['body'])
        message = body['message']
        conversation_history = body.get('conversationHistory', [])

        # 独自 FastAPI へ送るペイロードの構築
        payload = {
            "message": message,
            "conversationHistory": conversation_history
        }

        # FastAPI のエンドポイント URL（必要に応じて変更）
        api_url = "https://c63a-35-187-249-19.ngrok-free.app/invoke"

        # HTTPリクエストの設定
        req = urllib.request.Request(
            api_url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        # FastAPI にリクエスト送信
        with urllib.request.urlopen(req) as response:
            response_body = response.read().decode('utf-8')
            print("API response:", response_body)

            # レスポンスのパース
            response_json = json.loads(response_body)
            assistant_message = response_json.get('response', '')

        # 会話履歴にアシスタントの応答を追加
        conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": assistant_message,
                "conversationHistory": conversation_history
            }),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        }

    except urllib.error.HTTPError as e:
        error_message = f"HTTPError: {e.code} - {e.reason}"
        print(error_message)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": error_message})
        }

    except Exception as e:
        error_message = f"Exception: {str(e)}"
        print(error_message)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": error_message})
        }
