import os
import urllib.request
import concurrent.futures
import subprocess

def downloadFile(file_url, file_name):
    req = urllib.request.Request(file_url, headers={"Referer": "https://turtleviplay.xyz/"})
    with urllib.request.urlopen(req) as response:
        with open(file_name, "wb") as file:
            file.write(response.read())
    print(f"Downloaded {file_name}!")

os.makedirs("ts", exist_ok=True)

count = 1
ts_links = []
qualities = []

url = input("Enter url: ")

# Save main url
main_url = url[:url.rfind("m3u8")][:url[:url.rfind("m3u8")].rfind("/") + 1]

# Downloading index
downloadFile(url, "index.m3u8")
with open("index.m3u8") as index:
    for line in index.readlines():
        if "RESOLUTION" in line:
            quality = line[line.find("RESOLUTION=") + 11:line.find("RESOLUTION=") + 11 + line[line.find("RESOLUTION=") + 11:].find(",")]
            print(f"{count}. {quality}")
            count += 1
        if "https" in line:
            qualities.append(line.strip())
        if "EXT" not in line:
            qualities.append(f"{main_url}{line.strip()}")

choice = int(input("Enter choice: ")) - 1
url = qualities[choice]
main_url = url[:url.rfind("m3u8")][:url[:url.rfind("m3u8")].rfind("/") + 1]
downloadFile(qualities[choice], "index.m3u8")
qualities.clear()

with open("index.m3u8") as playlist:
    for line in playlist.readlines():
        if "EXT" not in line and "https" not in line:
            ts_links.append(f"{main_url}{line.strip()}")
        elif "https" in line:
            ts_links.append(f"{line.strip()}")

fileNames = [f"ts/{i}.ts" for i in range(len(ts_links))]

print(f"Downloading {len(ts_links)} files...")
with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
    executor.map(downloadFile, ts_links, fileNames)

# Append downloaded ts to single file
with open("out.ts", 'wb') as output:
    for i in range(1, len(ts_links) + 1):
        file = f"ts/{i}.ts"
        if os.path.exists(file):
            with open(file, 'rb') as ts_file:
                content = ts_file.read()
                output.write(content)

# ffmpeg to convert to mp4
ffmpeg_command = [
    "ffmpeg",
    "-i", "out.ts",
    "-c:v", "copy",
    "-c:a", "copy",
    "output.mp4"
]
subprocess.run(ffmpeg_command)
