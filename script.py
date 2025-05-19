import os
import urllib.request
import concurrent.futures
import subprocess

url = input("Enter url: ")
os.makedirs("ts", exist_ok=True)
headers = {
    "Referer": "https://turtleviplay.xyz/"
}

ts_links = []
qualities = []

# Downloading index
urllib.request.urlretrieve(url, "index.m3u8")
count = 1
with open("index.m3u8") as index:
    for line in index.readlines():
        if "BANDWIDTH" in line:
            leftSub = line[line.index("RESOLUTION=") + 11:]
            print(f"{count}. {leftSub[:leftSub.index(",")]}")
            count += 1
        if "https" in line:
            qualities.append(line.strip())
choice = int(input("Enter choice: ")) - 1

# Downloading video M3U8
req = urllib.request.Request(qualities[choice],headers=headers)
with urllib.request.urlopen(req) as response:
    content = response.read()
    with open("video.m3u8", "wb") as video:
        video.write(content)

# Read and download ts files
main_url = qualities[choice][:qualities[choice].rfind('/')]
with open("video.m3u8") as video:
    for line in video.readlines():
        if "EXT" not in line:
            ts_links.append(f"{main_url}/{line.strip()}")

def download_file(ts_url, num):
    urllib.request.urlretrieve(ts_url, f"ts/{num}.ts")
    print(f"{num}.ts downloaded of {len(ts_links)} files...")

threads = 20

with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
    executor.map(download_file, ts_links, range(1, len(ts_links) + 1))


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