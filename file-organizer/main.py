import os
import shutil

def organize_folder(folder_path):
    file_types = {
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
        "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx", ".csv"],
        "Videos": [".mp4", ".mov", ".avi", ".mkv", ".wmv"],
        "Audio": [".mp3", ".wav", ".aac", ".flac"],
        "Code": [".py", ".js", ".html", ".css", ".json", ".ts"],
        "Archives": [".zip", ".rar", ".tar", ".gz"],
        "Others": []
    }

    files_moved = 0

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        if os.path.isdir(file_path):
            continue

        file_ext = os.path.splitext(filename)[1].lower()

        destination_folder = "Others"
        for folder_name, extensions in file_types.items():
            if file_ext in extensions:
                destination_folder = folder_name
                break

        destination_path = os.path.join(folder_path, destination_folder)
        if not os.path.exists(destination_path):
            os.makedirs(destination_path)

        shutil.move(file_path, os.path.join(destination_path, filename))
        print(f"Moved: {filename} → {destination_folder}")
        files_moved += 1

    print()
    print(f"Done! {files_moved} files organized.")

folder = input("Enter the full path of the folder to organize: ")
organize_folder(folder)