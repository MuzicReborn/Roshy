import os
import shutil
import urllib.request
import concurrent.futures
import subprocess

count = 1
ts_links = []
qualities = []
downloads_folder = os.path.expanduser('~') + "/Downloads/"

def download_file(file_url, file_name):
    file_name = downloads_folder + file_name
    req = urllib.request.Request(file_url, headers={"Referer": "https://turtleviplay.xyz/"})
    with urllib.request.urlopen(req) as response:
        with open(file_name, "wb") as f:
            f.write(response.read())
    if len(ts_links) != 0:
        print(f"Downloaded {file_name[file_name.rfind('/') + 1 : file_name.find('.')]}\\{len(ts_links)}")
    else:
        print(f"Downloaded {file_name}!")

os.makedirs(downloads_folder + "ts", exist_ok=True)

url = input("Enter url: ")
name = input("Enter file name: ")

# Save main url
main_url = url[:url.rfind("m3u8")][:url[:url.rfind("m3u8")].rfind("/") + 1]

# Downloading index
download_file(url, "index.m3u8")
with open(f"{downloads_folder}index.m3u8") as index:
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
download_file(qualities[choice], "index.m3u8")
qualities.clear()

with open(f"{downloads_folder}index.m3u8") as playlist:
    for line in playlist.readlines():
        if "EXT" not in line and "https" not in line:
            ts_links.append(f"{main_url}{line.strip()}")
        elif "https" in line:
            ts_links.append(f"{line.strip()}")

fileNames = [f"ts/{i}.ts" for i in range(1, len(ts_links) + 1)]

print(f"Downloading {len(ts_links)} files...")
with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
    executor.map(download_file, ts_links, fileNames)

# Append downloaded ts to single file
with open(downloads_folder + "out.ts", 'wb') as output:
    for i in range(1, len(ts_links) + 1):
        file =  downloads_folder + f"ts/{i}.ts"
        if os.path.exists(file):
            with open(file, 'rb') as ts_file:
                content = ts_file.read()
                output.write(content)

# ffmpeg to convert to mp4
ffmpeg_command = [
    "ffmpeg",
    "-i", downloads_folder + "out.ts",
    "-c:v", "copy",
    "-c:a", "copy",
    downloads_folder + f"{name}.mp4"
]
subprocess.run(ffmpeg_command)

# Clean up
shutil.rmtree(downloads_folder + "ts")
os.remove(downloads_folder + "out.ts")
os.remove(downloads_folder + "index.m3u8")
