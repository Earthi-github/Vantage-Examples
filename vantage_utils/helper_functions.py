import cv2
import ffmpeg
import json
import os
import requests
import sys
import time


class Auth:
    USERNAME = ''
    API_KEY = ''


ENDPOINT = 'https://vantage.earthi.world/secure/api/v2.0'


def _get_config_id(response):
    return response.json()['id']


def _get_job_id(response):
    return response.json()['content']['id']


def _get_job_status(job_id):
    r = requests.get(f'{ENDPOINT}/jobs/{job_id}', auth=(Auth.USERNAME, Auth.API_KEY)).json()
    status = r['status']

    return status


def _get_output_id(job_id):
    return requests.get(f'{ENDPOINT}/jobs/{job_id}', auth=(Auth.USERNAME, Auth.API_KEY)).json()['_embedded'][
        'outputFiles'][0][
        'id']


def get_video(filename: str, aligned: bool = False):
    """
    Downloads Vivid-X2 video. Saves video and related files in {filename}.zip

    Parameters
    ----------
    filename: str
        Vivid-X2 filename.
    aligned: bool
        When set to True, downloads video after alignment

    Returns
    -------
    None

    """
    query = {'filter': filename}
    video_query_res = requests.get(
        'https://vantage.earthi.world/secure/api/v2.0/platformFiles/search/parametricFind?sort=filename&type=REMOTE_DATA&collection=https://vantage.earthi.world/secure/api/v2.0/collections/16',
        auth=(Auth.USERNAME, Auth.API_KEY), params=(query))

    if video_query_res.status_code == 401:
        sys.exit(
            f'Auth credentials are not valid. Please set Auth.USERNAME and Auth.API_KEY before calling get_video function')

    if video_query_res.json()['page']['totalElements'] == 0:
        sys.exit(f'File {filename} does not exist.')

    if aligned:
        service_id = '11'
    else:
        service_id = '25'

    headers = {'Accept': 'application/hal+json', 'Content-Type': 'application/hal+json'}
    data = {
        'service': f'https://vantage.earthi.world/secure/api/v2.0/services/{service_id}',
        'inputs': f'{{"VideoFile":["https://esrin-data-input.s3.eu-west-2.amazonaws.com/Vivid-X2/{filename}.zip"]}}',
        'label': 'getVideo1',
        'parent': None
    }

    formated_data = json.dumps(data).replace('\\', '').replace(' ', '').replace('"{"', '{"').replace('"]}"', '"]}')
    config_response = requests.post(f'{ENDPOINT}/jobConfigs/', auth=(Auth.USERNAME, Auth.API_KEY), data=formated_data,
                                    headers=headers)

    config_id_1 = _get_config_id(config_response)
    launch_response = requests.post(f'{ENDPOINT}/jobConfigs/{config_id_1}/launch', auth=(Auth.USERNAME, Auth.API_KEY))
    job_id = _get_job_id(launch_response)
    print(f'Launching job with id: {job_id}')

    status = 'PENDING'
    while status in ['PENDING', 'RUNNING']:
        time.sleep(30)
        try:
            status = _get_job_status(job_id)
            print(f'Job status: {status}')
        except Exception as e:
            print(e)
            sys.exit('Couldn\'t access job status.')

    print("")
    if status == 'COMPLETED':
        try:
            out_id = _get_output_id(job_id)
            response = requests.get(f'{ENDPOINT}/platformFiles/{out_id}/dl', auth=(Auth.USERNAME, Auth.API_KEY),
                                    allow_redirects=True)
            print(f'Job completed. Downloading output product.')
            if aligned:
                print(f'Saving file {filename}.mp4')
                with open(f'{filename}.mp4', 'wb') as f:
                    f.write(response.content)
            else:
                print(f'Saving file {filename}.zip')
                with open(f'{filename}.zip', 'wb') as f:
                    f.write(response.content)
            print('\nDone')
        except Exception as e:
            print(e)
            sys.exit('Couldn\'t access the output file.')
    else:
        print(f'Job exited without completion. Job status: {status}')


def _read_json(json_file, video_format='mp4'):
    vid_format_bit_mapping = {
        'mp4': 0,
        'avi': 0,
        'mov': 1
    }

    with open(json_file, "r") as json_data:
        data = json.load(json_data)
        json_data.close()
        bit_depth = data["streams"][vid_format_bit_mapping[video_format]]["bits_per_raw_sample"]
        print('Bit Depth of the given video: {}'.format(bit_depth))
    return bit_depth


def extract_frames(video_path: str,
                   image_format: str = 'tif',
                   out_folder: str = './frames'):
    """
    Extracts and saves video frames.

    Parameters
    ----------
    video_path: str
        Path to video (mp4, mov, avi)
    image_format: str
        Output frame format (tif, png, jpg).
    out_folder: str
        Path to output folder.

    Returns
    -------
    None

    """
    os.makedirs(out_folder, exist_ok=True)

    frname = os.path.splitext(os.path.basename(video_path))[0]

    if video_path[-3:] == 'mp4':
        os.system('ffprobe -v quiet -print_format json -show_format -show_streams ' + video_path + ' > output.json')
        bit_depth = _read_json('../forest_cover_mapping/output.json', video_format='mp4')
    elif video_path[-3:] == 'mov':
        os.system('ffprobe -v quiet -print_format json -show_format -show_streams ' + video_path + ' > output.json')
        # bit_depth = read_json_mov_avi('output.json')
        bit_depth = _read_json('../forest_cover_mapping/output.json', video_format='mov')
    elif video_path[-3:] == 'avi':
        os.system('ffprobe -v quiet -print_format json -show_format -show_streams ' + video_path + ' > output.json')
        bit_depth = _read_json('../forest_cover_mapping/output.json', video_format='avi')
    else:
        raise NotImplementedError('Supported video formats include only .mp4, .mov & .avi')

    if bit_depth == '8':

        if image_format == 'jpg':
            print('You have selected jpg format')
            print('Extracting frames ...')
            try:
                (ffmpeg.input(video_path)
                 .output(out_folder + '/' + frname + '_%04d.jpg',
                         pix_fmt='rgb24',
                         start_number=0)
                 .run(capture_stdout=True, capture_stderr=True))
            except ffmpeg.Error as e:
                print('stdout:', e.stdout.decode('utf8'))
                print('stderr:', e.stderr.decode('utf8'))

        elif image_format == 'png':
            print('You have selected png format')
            print('Extracting frames ...')
            try:
                (ffmpeg.input(video_path)
                 .output(out_folder + '/' + frname + '_%04d.png',
                         pix_fmt='rgb24',
                         start_number=0)
                 .run(capture_stdout=True, capture_stderr=True))
            except ffmpeg.Error as e:
                print('stdout:', e.stdout.decode('utf8'))
                print('stderr:', e.stderr.decode('utf8'))
        elif image_format == 'tif':
            print('You have selected tif format')
            print('Extracting frames ...')
            foldername = frname + '_' + image_format + '_frames'
            try:
                (ffmpeg.input(video_path)
                 .output(out_folder + '/' + frname + '_%04d.tif',
                         pix_fmt='rgb24',
                         start_number=0)
                 .run(capture_stdout=True, capture_stderr=True))
            except ffmpeg.Error as e:
                print('stdout:', e.stdout.decode('utf8'))
                print('stderr:', e.stderr.decode('utf8'))
        else:
            print('You have chosen wrong Image format, Enter either jpg or png or tif')
            print('Try Again ...')
            # main()
    elif bit_depth == '10':
        # v = Video.open(fname)
        if image_format == 'tif':
            print('You have selected tif format')
            print('Extracting frames ...')
            foldername = frname + '_16bit_' + image_format + '_frames'
            try:
                (ffmpeg.input(video_path)
                 .output(os.path.join(out_folder, frname + '_%04d.tif'),
                         pix_fmt='rgb48',
                         start_number=0)
                 .run(capture_stdout=True, capture_stderr=True))
                print('Converted video to frames')
            except ffmpeg.Error as e:
                print('Error')
                print('stdout:', e.stdout.decode('utf8'))
                print('stderr:', e.stderr.decode('utf8'))

        else:
            print('For 16 bit conversion enter tif only')
            print('Try Again ...')
    else:
        raise NotImplementedError('Supported bit-depths include only 8 & 10-bit values')

    num_frames = len([f for f in os.listdir(out_folder) if _is_image(f)])
    print(f'\nDone. Extracted {num_frames} frames.')


def _is_image(file_path):
    image_extensions = ['tif', 'png', 'jpg']
    file_ext = os.path.splitext(file_path)[-1].replace('.', '')

    if file_ext in image_extensions:
        return True
    return False


def frame_generator(frames_folder: str, grayscale: bool = False, normalization: bool = False):
    """
    Creates a generator that yields video frames.

    Parameters
    ----------
    frames_folder: str
        Path to frames folder
    grayscale: bool
        Yields 8-bit grayscale frames when set to True.
    normalization: bool
        Yields 8-bit RGB video frames when set to True. Otherwise uses original representation (e.g. 16-bit).

    Returns
    -------
    frame: numpy.ndarray

    """
    for root, dirs, files in os.walk(frames_folder):
        files.sort()
        for file in files:
            if _is_image(file):
                if grayscale:
                    frame = cv2.imread(os.path.join(root, file), 0)
                else:
                    if normalization:
                        frame = cv2.imread(os.path.join(root, file))
                    else:
                        frame = cv2.imread(os.path.join(root, file), -1)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                yield frame


if __name__ == '__main__':
    pass
