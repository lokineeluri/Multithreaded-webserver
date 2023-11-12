import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import os
import time

def download_url(url, output_dir, resource_type):
    try:
        start_time = time.time()
        response = requests.get(url, stream=True)
        end_time = time.time()

        if response.status_code == 200:
            filename = os.path.join(output_dir, os.path.basename(url))
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            print(f'Downloaded ({resource_type}): {url}, Response Time: {end_time - start_time:.2f} seconds')
        else:
            print(f'Failed to download ({resource_type}): {url}')

    except Exception as e:
        print(f'Error downloading ({resource_type}): {url}: {str(e)}')

def parse_and_request_resources(html_file, server_url):
    with open(html_file, 'r') as file:
        soup = BeautifulSoup(file, 'html.parser')

    with ThreadPoolExecutor(max_workers=5) as executor:
        for tag in soup.find_all(['link', 'img', 'script']):
            resource_type = tag.name  # 'link', 'img', or 'script'
            if 'src' in tag.attrs:
                resource = tag['src']
                resource_url = server_url + resource
                executor.submit(download_url, resource_url, 'downloaded_files', resource_type)
            if 'href' in tag.attrs:
                resource = tag['href']
                resource_url = server_url + resource
                executor.submit(download_url, resource_url, 'downloaded_files', resource_type)

if __name__ == "__main__":
    server_ip = "127.0.0.1"
    server_port = input("Enter server port: ")
    server_url = f'http://{server_ip}:{server_port}/'
    html_file = input("Enter the HTML file to parse: ")

    if not os.path.exists('downloaded_files'):
        os.makedirs('downloaded_files')

    print(f'Requesting the HTML file: {html_file}')
    html_url = server_url + html_file
    download_url(html_url, 'downloaded_files', 'html')

    print("Waiting for the HTML file to be downloaded...")
    time.sleep(5)

    print(f'Parsing and requesting additional resources in {html_file}')

    with open(html_file, 'r') as file:
        soup = BeautifulSoup(file, 'html.parser')

    for tag in soup.find_all(['link', 'img', 'script']):
        resource_type = tag.name
        if 'src' in tag.attrs:
            resource = tag['src']
            print(f'Requesting ({resource_type}) file: {resource}')
        if 'href' in tag.attrs:
            resource = tag['href']
            print(f'Requesting ({resource_type}) file: {resource}')

    parse_and_request_resources('downloaded_files/' + os.path.basename(html_file), server_url)
