from requests import get

with open("bypassed.txt", "r") as bpf:
    urls = bpf.read().splitlines()

failed_f = open("failed.txt", "a")

for url in urls:
    print("url:", url)
    try:
        tr = get(url)
    except Exception as e:
        failed_f.write("{}\n".format(url))
        print("Fehler beim Freischalten von {}: {}".format(url, e))

failed_f.close()
