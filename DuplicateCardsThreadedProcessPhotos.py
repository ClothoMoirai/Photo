#! /usr/bin/python3
from wand.image import Image
import os
import time
import argparse
import getpass
from multiprocessing.dummy import Pool
from typing import List

start = time.time()
default_local_dir = os.path.expanduser("~") + '/Pictures/'
default_source_dir = '/media'
thread_count = 4
default_resize = 33
default_thumbnail = 10


def process_file(this_fq_file):
    this_file = this_fq_file.rpartition('/')
    # print(this_file)
    this_file = this_file[-1]
    original_file = original_dir + '/' + this_file
    resize_file = resize_dir + '/resize_' + this_file
    thumbnail_file = thumb_dir + '/thumbnail_' + this_file
    # print(this_fq_file, original_file, resize_file, thumbnail_file, this_file)
    with Image(filename=this_fq_file) as this_image:
        this_image.auto_orient()
        this_image.save(filename=original_file)
        this_image.resize(width=int(this_image.width * 0.33), height=int(this_image.height * 0.33))
        this_image.save(filename=resize_file)
        this_image.resize(width=int(this_image.width * 0.103), height=int(this_image.height * 0.103))
        this_image.save(filename=thumbnail_file)
        my_results_dict = {this_file: {
                                'thumbnail': 'thumb/thumbnail_' + this_file,
                                'resize': 'resize/resize_' + this_file,
                                'original': 'original/' + this_file,
                                'height': this_image.height,
                                'width': this_image.width}}
    return my_results_dict


def check_directories():
    if not os.path.isdir(thumb_dir):
        os.makedirs(thumb_dir)
    if not os.path.isdir(resize_dir):
        os.makedirs(resize_dir)
    if not os.path.isdir(original_dir):
        os.makedirs(original_dir)
    return


def build_index(my_results):
    my_index_file = open(index_file, "w")
    my_index_file.write('<head><title>.</title></head><body><table><tr>')
    count = 0
    for this_file in sorted(my_results.keys()):
        my_index_file.write('<td align="center"><img src={thumbnail} height={height} width={width}><br><a href={resize}>small size</a> <a href={original}>large size</a></td>'.format(
            thumbnail=my_results[this_file]['thumbnail'], resize=my_results[this_file]['resize'], original=my_results[this_file]['original'], height=my_results[this_file]['height'], width=my_results[this_file]['width']))
        count += 1
        if not count % 5:
            my_index_file.write('</tr><tr>')
    my_index_file.write('</tr></table></body>')
    return count


def transfer_files(dest_dir, target_dir, my_dir):
    zip_command = 'zip -9r ' + target_dir + my_dir + '.zip ' + target_dir + args.directory + '/'
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(remote_host, username=remote_user)
    scp = SCPClient(ssh.get_transport())
    scp.put(dest_dir, recursive=True, remote_path=target_dir)
    scp.close()
    stdin, stdout, stderr = ssh.exec_command(zip_command)
    while not stdout.channel.exit_status_ready():
        time.sleep(1)
    ssh.close()


def generate_file_list() -> List[str]:
    file_list = []
    counter = 0
    for this_file in os.listdir(file_location[0]):
        counter += 1
        file_list.append(file_location[counter % len(file_location)] + '/' + this_file)
    return file_list


def main():
    if __name__ == '__main__':
        # for this_file in os.listdir(file_location):
        #    process_file(this_file)
        file_list = generate_file_list()
        check_directories()
        my_results = {}
        my_pool = Pool(processes=how_many)
        all_results = my_pool.imap(process_file, file_list)
        my_pool.close()
        my_pool.join()
        for this_result in all_results:
            my_results.update(this_result)
        total_files = build_index(my_results)
        if not args.noscp:
            transfer_files(dest_dir, target_dir, my_dir)
        end = time.time()
        print('Processed {filecount} photos in {elapsed} seconds'.format(filecount=total_files, elapsed=(end - start)))


parser = argparse.ArgumentParser(description='Process photos.')
parser.add_argument('--noscp', action='store_true', help='To inhibit scp of files and remote zip file creation.')
parser.add_argument('--threads', help='Number of execution threads. Default: {}'.format(thread_count), default=thread_count)
parser.add_argument('--media', default=[default_source_dir], action='append', help='Location of original image files. May be used more than once. Default: {}'.format(default_source_dir))
# parser.add_argument('--media2', default=None, help='Location of second original image files. Default: None')
parser.add_argument('--local_dir', default=default_local_dir, help='Local disk directory for output. Default: {}'.format(default_local_dir))
parser.add_argument('--remote_host', help='Remote hostname. Not required if --noscp is specified')
parser.add_argument('--remote_user', default=getpass.getuser(), help='remote username. default is local username. unused if --noscp is specified')
parser.add_argument('--remote_dir', default='~', help='remote directory. Unused if --noscp is specified.')
parser.add_argument('--resize_percent', default=default_resize, help='resize percentage. Default: {}'.format(default_resize))
parser.add_argument('--thumbnail_percent', default=default_thumbnail, help='thumbnail percentage. Default: {}'.format(default_thumbnail))
# parser.add_argument('--config', help='Use this section of the configuration settings file.')
# parser.add_argument('--create_config', help='Add this configuration to the settings file.')
parser.add_argument('directory', help='Event directory name')
args = parser.parse_args()
my_dir = args.directory
how_many = int(args.threads)
file_location = args.media
# workaround for a behavior of argparse: when using append and a default list value the result is default and specified.
if len(file_location) > 1:
    file_location.remove(default_source_dir)
base_dir = args.local_dir
if not args.noscp:
    import paramiko
    from scp import SCPClient
    target_dir = args.remote_dir
    remote_host = args.remote_host
    remote_user = args.remote_user
dest_dir = base_dir + my_dir
thumb_dir = dest_dir + '/thumb'
resize_dir = dest_dir + '/resize'
original_dir = dest_dir + '/original'
index_file = dest_dir + '/index.html'
thumbnail_percent = args.thumbnail_percent / 100
resize_percent = args.resize_percent / 100

main()
