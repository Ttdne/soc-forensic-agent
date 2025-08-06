import os
import time
import json
import tkinter as tk
from tkinter import scrolledtext

def execute(text: str, attachments=None, state_dir: str = None, output_widget=None, **kwargs):
    timestamp = str(int(time.time()))
    
    if state_dir is None:
        state_dir = os.path.join("./test_environment", timestamp)
    
    if not os.path.exists(state_dir):
        os.makedirs(state_dir, exist_ok=True)
    
    # Log the message
    message_log_path = os.path.join(state_dir, "message_notify_log.txt")
    with open(message_log_path, "a", encoding='utf-8') as log_file:
        log_file.write(f"Message sent at: {time.ctime()}\n")
        log_file.write(f"Message text: {text}\n")
        if attachments:
            if isinstance(attachments, str):
                log_file.write(f"Attachment: {attachments}\n")
            else:
                for i, attachment in enumerate(attachments):
                    log_file.write(f"Attachment {i+1}: {attachment}\n")
    
    # Create a message record
    message_record = {
        "type": "notification",
        "timestamp": time.time(),
        "text": text,
        "attachments": attachments
    }
    
    record_path = os.path.join(state_dir, "message_notify_record.json")
    with open(record_path, "w", encoding="utf-8") as record_file:
        json.dump(message_record, record_file, indent=2)

    # Update the GUI widget if provided
    if output_widget:
        output_widget.configure(state='normal')
        output_widget.insert(tk.END, f"Message sent at: {time.ctime()}\n")
        output_widget.insert(tk.END, f"Message text: {text}\n")
        if attachments:
            if isinstance(attachments, str):
                output_widget.insert(tk.END, f"Attachment: {attachments}\n")
            else:
                for i, attachment in enumerate(attachments):
                    output_widget.insert(tk.END, f"Attachment {i+1}: {attachment}\n")
        output_widget.insert(tk.END, "\n")
        output_widget.configure(state='disabled')

    return {
        "tool": "message_notify_user",
        "success": True,
        "text": text,
        "attachments": attachments,
        "timestamp": time.time(),
        "record_file": record_path
    }

def main():
    root = tk.Tk()
    root.title("Notification System")

    text_output = scrolledtext.ScrolledText(root, width=60, height=20, state='disabled')
    text_output.pack(pady=10)

    # Sample usage of the execute function
    execute("This is a test message", ["attachment1.txt", "attachment2.png"], output_widget=text_output)

    root.mainloop()

if __name__ == "__main__":
    main()