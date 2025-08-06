import os
import time
import json

def execute(text: str, attachments=None, suggest_user_takeover: str = "none", state_dir: str = None, **kwargs):
    # Create directory based on timestamp if not provided
    if state_dir is None:
        timestamp = str(int(time.time()))
        state_dir = os.path.join("./test_environment", timestamp)
    
    if not os.path.exists(state_dir):
        os.makedirs(state_dir, exist_ok=True)
    
    # Log the question
    question_log_path = os.path.join(state_dir, "message_ask_log.txt")
    with open(question_log_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"Question asked at: {time.ctime()}\n")
        log_file.write(f"Question text: {text}\n")
        log_file.write(f"Suggest user takeover: {suggest_user_takeover}\n")
        if attachments:
            if isinstance(attachments, str):
                log_file.write(f"Attachment: {attachments}\n")
            else:
                for i, attachment in enumerate(attachments):
                    log_file.write(f"Attachment {i+1}: {attachment}\n")
    
    # Create a question record
    question_record = {
        "type": "question",
        "timestamp": time.time(),
        "text": text,
        "attachments": attachments,
        "suggest_user_takeover": suggest_user_takeover,
        "awaiting_response": True
    }
    
    record_path = os.path.join(state_dir, "message_ask_record.json")
    with open(record_path, "w") as record_file:
        json.dump(question_record, record_file, indent=2)
    
    # In a real implementation, this would wait for user response
    # For this mock, we'll simulate a response
    simulated_response = "This is a simulated user response."
    
    # Update the record with the response
    question_record["response"] = simulated_response
    question_record["response_timestamp"] = time.time()
    question_record["awaiting_response"] = False
    
    with open(record_path, "w") as record_file:
        json.dump(question_record, record_file, indent=2)
    
    return {
        "tool" : "message_ask_user",
        "success": True,
        "text": text,
        "attachments": attachments,
        "suggest_user_takeover": suggest_user_takeover,
        "timestamp": time.time(),
        "response": simulated_response,
        "record_file": record_path
    }
