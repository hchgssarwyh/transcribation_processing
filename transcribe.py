import requests

class Transcribe:
    def __init__(self, endpoint_url: str, api_key: str):
        self.endpoint_url = endpoint_url
        self.api_key = api_key
    
    def upload_audio(self, audio_url, title):
        mutation = """
        mutation uploadAudio($input: AudioUploadInput) {
            uploadAudio(input: $input) {
                success
                title
                message
                id
            }
        }
        """
        variables = {
            "input": {
                "url": audio_url,
                "title": title,
            }
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        response = requests.post(self.endpoint_url, json={"query": mutation, "variables": variables}, headers=headers)
        result = response.json()
    
        if result["data"]["uploadAudio"]["success"]:
            return result["data"]["uploadAudio"]["id"]
        else:
            return None

    def check_audio_status(self, audio_id):
        query = """
        query checkAudioStatus($input: AudioStatusInput) {
            checkAudioStatus(input: $input) {
                success
                status
                message
            }
        }
        """
        variables = {
            "input": {
                "id": audio_id  # Предполагается, что API принимает идентификатор аудио
            }
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        response = requests.post(self.endpoint_url, json={"query": query, "variables": variables}, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            return result.get("data", {}).get("checkAudioStatus", {})
        else:
            return {"success": False, "message": "Failed to fetch status."}
    def get_transcription_result(self, audio_id):
        status_result = self.check_audio_status(audio_id)

        if status_result.get("success") and status_result.get("status") == "processed":
            query = """
            query getTranscriptionResult($input: TranscriptionInput) {
                getTranscriptionResult(input: $input) {
                    success
                    transcription
                    message
                }
            }
            """
            variables = {
                "input": {
                    "id": audio_id
                }
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            response = requests.post(self.endpoint_url, json={"query": query, "variables": variables}, headers=headers)

            if response.status_code == 200:
                result = response.json()
                return result.get("data", {}).get("getTranscriptionResult", {})
            else:
                return {"success": False, "message": "Failed to fetch transcription result."}
        
        return {"success": False, "message": "Audio is not processed yet."}