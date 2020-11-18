import os
import time
from string import digits
from datetime import datetime as dt
from selenium import webdriver
from PIL import Image
from io import BytesIO


pwd = os.path.dirname(os.path.realpath(__file__))
urls = {
    '7sec': 'https://processed-video.s3-eu-west-1.amazonaws.com/mpeg-dash-7/birds.mpd',
    '15sec': 'https://processed-video.s3-eu-west-1.amazonaws.com/mpeg-dash/birds.mpd',
    '30sec': 'https://processed-video.s3-eu-west-1.amazonaws.com/mpeg-dash-30/birds.mpd'
}
screenshot_dir = os.path.join(pwd, 'screenshots')

working_dir = os.path.join(
    screenshot_dir,
    dt.now().strftime("%m-%d-%Y_%H-%M-%S")
)


def create_directories():
    if not os.path.exists(screenshot_dir):
        os.mkdir(screenshot_dir)
    os.mkdir(working_dir)


def extract_numbers(driver, xpath):
    text = driver.find_element_by_xpath(xpath).text
    value = text.split(':')[1].replace(' ', '')
    sanitized_values = [
        ''.join(bar for bar in foo if bar in [*digits, '.'])
        for foo in value.split('|')
    ]
    return sanitized_values


def capture_element(driver, working_dir, filename):

    image_path = os.path.join(working_dir, '{}.png'.format(filename))

    # find part of the page you want image of
    element = driver.find_element_by_class_name('chart-panel')
    location = element.location
    size = element.size
    png = driver.get_screenshot_as_png()  # saves screenshot of entire page

    im = Image.open(BytesIO(png))  # uses PIL library to open image in memory

    left = location['x']
    top = location['y']
    right = location['x'] + size['width']
    bottom = location['y'] + size['height']

    im = im.crop((left, top, right, bottom))  # defines crop points
    im.save(image_path)  # saves new cropped image


def watch_videos():
    create_directories()

    driver = webdriver.Chrome()
    driver.get(
        "http://mediapm.edgesuite.net/dash/public/nightly/samples/dash-if-reference-player/index.html")

    for segment, url in urls.items():
        input_box = driver.find_element_by_xpath(
            '/html/body/div[2]/div[2]/div/input')
        input_box.clear()
        input_box.send_keys(url)

        load_button = driver.find_element_by_xpath(
            '/html/body/div[2]/div[2]/div/span/button[2]')
        load_button.click()

        check_box_ids = [
            'videoBufferCB',
            'videoBitrateCB',
            'videoLatencyCB',
            'videoDroppedFramesCB',
            'videoDownloadCB'
        ]

        for check_box_id in check_box_ids:
            check_box = driver.find_element_by_id(check_box_id)
            if not check_box.is_selected():
                check_box.click()

        # element = driver.find_element_by_class_name('chart-panel')
        graph_intervals = [20, 70, 140, 280]

        csv_data = [
            'Timestamp,BufferLength,BitrateDownloading(kbps),DroppedFrames,MinLatency,AvgLatency,MaxLatency,MinDownload,AvgDownload,MaxDownload\n'
        ]
        for foo in range(10, 300, 10):
            interval = 10
            time.sleep(interval)

            if foo in graph_intervals:
                capture_element(
                    driver,
                    working_dir,
                    '{0}-{1}'.format(segment, foo)
                )

            xpaths = [
                '/html/body/div[2]/div[4]/div[2]/div/div/div[1]/div/div[1]',
                '/html/body/div[2]/div[4]/div[2]/div/div/div[1]/div/div[2]',
                '/html/body/div[2]/div[4]/div[2]/div/div/div[1]/div/div[5]',
                '/html/body/div[2]/div[4]/div[2]/div/div/div[1]/div/div[6]',
                '/html/body/div[2]/div[4]/div[2]/div/div/div[1]/div/div[7]'
            ]
            data = [driver.find_element_by_id('videoTime').text]
            for foo in [extract_numbers(driver, xpath) for xpath in xpaths]:
                data.extend(foo)

            csv_data.append(','.join(data)+'\n')

        with open(os.path.join(working_dir, 'data-{0}.csv'.format(segment)), 'w') as file:
            file.writelines(csv_data)

    driver.quit()


if __name__ == "__main__":
    watch_videos()
