# import requests
#
# requests.get("http://207.251.86.238/cctv42.jpg")
try:
    from urllib.request import urlretrieve
except ImportError:
    from urllib import urlretrieve
import os
import arrow
from time import clock, sleep
import hashlib
from random import random
import grequests
import shutil

# urlretrieve("http://207.251.86.238/cctv42.jpg", "00000002.jpg")


def acquire_current_image(cam_url, save_path):
    urlretrieve(cam_url, save_path)


def create_save_folder(cam_id, duration):
    start_time = arrow.utcnow().to('US/Eastern')
    format_time = start_time.format('HH-mm-ss--MM-DD-YYYY')
    dirname = "{cam_id}_{dur}s_{date}".format(
        cam_id=cam_id,
        dur=duration,
        date=format_time
    )
    rel_path = "data/{}".format(dirname)
    os.mkdir(rel_path)
    return rel_path


def create_cam_url(cam_id):
    url = "http://207.251.86.238/cctv{id}.jpg?math={rand}".format(
        id=cam_id,
        rand=random()
    )
    return url


def create_image_path(data_dir, img_count):
    return "{d}/image{num}.jpg".format(
        d=data_dir,
        num="%08d" % img_count
    )


def acquire_video_from_camera(cam_id, duration):
    data_directory = create_save_folder(cam_id, duration)
    cam_url = create_cam_url(cam_id)
    start_time = clock()
    elapsed_time = 0
    img_counter = 0
    prev_hash = ""
    while elapsed_time <= duration:
        cam_url = create_cam_url(cam_id)
        print("Fetching Image #{} from {}...".format(img_counter, cam_url))
        save_path = create_image_path(data_directory, img_counter)
        print(save_path)
        acquire_current_image(cam_url, save_path)
        new_hash = hashfile(save_path)
        print(new_hash)
        print(prev_hash)
        if new_hash != prev_hash:
            # This is a new image. We should keep it. Increment img counter
            img_counter += 1
        prev_hash = new_hash
        elapsed_time = clock() - start_time


def async_acquire_video(cam_id, duration):
    data_directory = create_save_folder(cam_id, duration)
    cam_url = create_cam_url(cam_id)
    start_time = clock()
    elapsed_time = 0
    img_counter = 0
    prev_hash = ""
    glets = []
    while elapsed_time <= duration:
        loop_start = clock()
        cam_url = create_cam_url(cam_id)
        print("Fetching Image #{} from {}...".format(img_counter, cam_url))
        save_path = create_image_path(data_directory, img_counter)
        print(save_path)
        glets.append(async_acquire_current_image(cam_url, save_path))
        img_counter += 1
        while clock()-loop_start < .5:
            pass
        elapsed_time = clock() - start_time
    print dir(glets[0])
    # for glet in glets:
    #     glet.join()


def make_callback(save_path):
    def callback(r, *args, **kwargs):
        print("Received r")
        with open(save_path, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

    return callback


def async_acquire_current_image(cam_url, save_path):
    print("Async call to {}".format(cam_url))
    req = grequests.get(cam_url, hooks=dict(response=make_callback(save_path)))
    glet = grequests.send(req, grequests.Pool(50))
    glet.run()
    return glet


def hashfile(path, blocksize=65536):
    afile = open(path, 'rb')
    hasher = hashlib.md5()
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    afile.close()
    return hasher.hexdigest()


def main():
    clock()  # Call initially in case we're in Windows
    # acquire_video_from_camera(486, 10)
    async_acquire_video(486, 10)
    # sleep(20    )

if __name__ == '__main__':
    main()
