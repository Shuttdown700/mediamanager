#!/usr/bin/env python3

def import_libraries():
    import pip
    aliases = {'numpy':'np'}
    libraries = ['alive_progress','colorama','ffmpeg','glob','mutagen','os','numpy','pymediainfo','random','sys',
                 'selenium','shutil','time','urllib','urllib.request','warnings','win32file']
    for l in libraries: 
        try:
            exec(f"import {l} as {aliases[l]}") if l in list(aliases.keys()) else exec(f"import {l}")
        except ImportError:
            print(f'Installing... {l}')
            pip.main(['install',l])
    sublibraries = [('alive_progress',['alive_bar']),('colorama',['Fore','Style']),('mutagen.mp4',['MP4','MP4Cover']),
                    ('selenium',['webdriver']),('selenium.webdriver.common.keys',['Keys'])]
    for s in sublibraries:
        for sl in s[1]:
            exec(f'from {s[0]} import {sl}')

import_libraries()
import alive_progress
import colorama
import glob
import os
import numpy as np
import shutil
import sys
import string
import time
import urllib
import urllib.request
import warnings
import win32file
import win32api

from alive_progress import alive_bar
from colorama import Fore, Style
from mutagen.mp4 import MP4, MP4Cover
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pymediainfo import MediaInfo

warnings.filterwarnings("ignore")

def read_alexandria(parent_dirs,extension = '.mp4'):
    """
    Returns all files of a given extension from a list of parent directories

    Parameters
    ----------
    parent_dirs : list
        Parent directories to be searched through.
    extension : TYPE, optional
        Extension to search for. The default is '.mp4'.

    Returns
    -------
    all_titles : list
        A list of all filenames, excluding the extension.
    all_paths : list
        A list of all paths to corresponding files.
    """
    all_titles, all_paths = [], []
    for p in parent_dirs:
        subDirectories = sorted(list([x[0].replace('\\','/') for x in os.walk(p) if 'metadata' not in x[0] and (x[0][-1] in string.digits or 'Movies' in x[0])]))
        for sd in subDirectories:
            l = sorted([gg.replace('\\','/') for gg in glob.glob("{}/*{}".format(sd.replace('\\','/'),extension))])
            for i in range(len(l)):
                all_titles.append('.'.join(l[i].split('/')[-1].split('.')[:-1]))
                all_paths.append('/'.join(l[i].split('/')[:-1]))
    return all_titles, all_paths

def get_time():
    """
    Returns current time
    
    Returns
    -------
    curr_time: str
        Time in 'TTTT on DDMMMYYYY' format
    """
    time_dict = {'dotw':time.ctime().split()[0],'month':time.ctime().split()[1],'day':time.ctime().split()[2],
                 'hour_24_clock':time.ctime().split()[3].split(':')[0],'minute':time.ctime().split()[3].split(':')[1],
                 'second':time.ctime().split()[3].split(':')[2],'year':time.ctime().split()[4]}
    if len(time_dict["minute"]) < 2: time_dict['minute'] = '0'+time.ctime().split()[3].split(':')[1]
    if len(time_dict["day"]) < 2: time_dict['day'] = '0'+time.ctime().split()[2]
    curr_time = f'{time_dict["hour_24_clock"]}{time_dict["minute"]} on {time_dict["day"]}{time_dict["month"].upper()}{time_dict["year"]}'
    return curr_time

def get_time_elapsed(start_time):
    """
    Prints the elapsed time since the input time
    
    Parameters
    ----------
    start_time : float
        Time as a floating pouint number in seconds

    Returns
    -------
    None.
    """
    hour_name, min_name, sec_name = 'hours', 'minutes', 'seconds'
    t_sec = round(time.time() - start_time)
    (t_min, t_sec) = divmod(t_sec,60)
    (t_hour,t_min) = divmod(t_min,60)
    if t_hour == 1: hour_name = 'hour'
    if t_min == 1: min_name = 'minute'
    if t_sec == 1: sec_name = 'second'
    print(f'\nThis process took: {t_hour} {hour_name}, {t_min} {min_name}, and {t_sec} {sec_name}')

def does_drive_exist(letter):
    """
    Checks if a drive exists 

    Parameters
    ----------
    letter : str
        Drive letter [A-Z] (Windows)

    Returns
    -------
    bool
        Returns TRUE if drive exists, otherwise returns FALSE.

    """
    return (win32file.GetLogicalDrives() >> (ord(letter.upper()) - 65) & 1) != 0

def get_drive_name(letter):
    return win32api.GetVolumeInformation(f"{letter}:/")[0]

def get_drive_size(letter):
    return shutil.disk_usage(f'{letter}:/')[0]/10**9

def get_file_size(file_with_path):
    if file_with_path[-4] == '.': return os.path.getsize(file_with_path)/10**9
    else: return os.path.getsize(file_with_path+'.mp4')/10**9

def get_show_files(pd,show):
    file_names, file_paths = read_alexandria([f'{pd}:/Movies/',f'{pd}:/Shows/',f'{pd}:/Anime/'],extension = '.mp4')
    show_files_with_path1 = [file_paths[i]+'/'+file_names[i]+'.mp4' for i in range(len(file_paths)) if file_paths[i] != f'{pd}:/Movies']
    show_files_with_path2 = [sfwp for sfwp in show_files_with_path1 if show == sfwp.split('/')[2].split('(')[0].strip()]
    return show_files_with_path2

def get_show_size(show_files_with_path):
    show_size = 0
    for sfwp in show_files_with_path: show_size += get_file_size(sfwp)  
    return round(show_size,2)

### FILE THUMBNAIL FUNCTIONS ###
    
def create_driver(driver_dir):
    options = webdriver.ChromeOptions(); options.add_argument("headless")
    return webdriver.Chrome(rf"{driver_dir}/chromedriver.exe", chrome_options=options)

def remove_duplicate_tv_shows(all_titles):
    all_titles2 = []
    for at in all_titles:
        if at[-1] == ')': all_titles2.append(at)
        else: all_titles2.append(' '.join(at.split()[:-1]))
    return sorted(list(set(all_titles2)))

def get_mp4s(mp4_dir):
    # os.chdir(mp4_dir)
    film_paths = glob.glob(f"{mp4_dir}*.mp4")
    film_names_and_years = []
    for i in range(len(film_paths)): film_names_and_years.append(".".join(film_paths[i].split('/')[-1].split('.')[:-1]))
    return film_paths, film_names_and_years

def get_cover_files(cover_dir):
    # os.chdir(cover_dir)
    cover_paths = [gg.replace('\\','/') for gg in glob.glob(f"{cover_dir}*.jpg")]
    cover_names = []
    for i in range(len(cover_paths)): cover_names.append(".".join(cover_paths[i].split('/')[-1].split('.')[:-1]))
    return cover_paths, cover_names

def compare(film_names_and_years, cover_names):
    films_without_covers, films_with_covers = [], []
    for f in film_names_and_years:
        if f+' COVER' not in cover_names: films_without_covers.append(f)
        else: films_with_covers.append(f)
    return films_without_covers, films_with_covers

def save_cover(driver,name,search,cover_dir):
    driver.get('https://www.google.ca/imghp?hl=en&tab=ri&authuser=0&ogbl')
    try:
        search_box = driver.find_element_by_xpath('//*[@id="sbtc"]/div[2]/div[2]/input')
    except:
        try:
            search_box = driver.find_element_by_xpath('//*[@id="sbtc"]/div/div[2]/input')
        except:
            try:
                search_box = driver.find_element_by_xpath('/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div[1]/div/div[2]/input')
            except:
                search_box = driver.find_element_by_xpath('/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input')    
    search_box.send_keys('{} movie poster IMDb'.format(search))
    search_box.send_keys(Keys.ENTER)
    # os.chdir(cover_dir)
    img = driver.find_element_by_xpath('//*[@id="islrg"]/div[1]/div[1]/a[1]/div[1]/img')
    urllib.request.urlretrieve(img.get_attribute('src'),f'{cover_dir}{name} COVER.jpg')

def get_covers(cover_dir,driver_dir,movie_dir,show_dir,anime_dir):
    cover_paths , cover_names = get_cover_files(cover_dir)
    all_titles = remove_duplicate_tv_shows(read_alexandria([movie_dir,show_dir,anime_dir])[0])
    films_without_covers, films_with_covers = compare(all_titles, cover_names)
    index = 0
    while len(films_without_covers) > 0:
        if index == 0: print('\nFetching film and show covers...')
        driver = create_driver(driver_dir)
        for fwc in films_without_covers:
            search = fwc
            if search.strip()[-1] != ")": search += ' TV SHOW'
            print(search)
            save_cover(driver,fwc,search,cover_dir)
            time.sleep(np.random.exponential(0.5))
        driver.quit()
        film_paths, film_names_and_years = get_mp4s(movie_dir)
        cover_paths , cover_names = get_cover_files(cover_dir)
        films_without_covers, films_with_covers = compare(film_names_and_years, cover_names)

def apply_covers_to_movies(cover_dir,driver_dir,movie_dir):
    film_paths, film_names_and_years = get_mp4s(movie_dir)
    cover_paths , cover_names = get_cover_files(cover_dir)
    films_without_covers, films_with_covers = compare(film_names_and_years, cover_names)
    os.chdir(movie_dir)
    with open("_covered_movies.txt",mode='a+',encoding='utf-8') as file:
        file.seek(0)
        lines = file.readlines()
        lines = [str(l).strip() for l in lines]
        num_films_with_covers = int(len(films_with_covers) - len(list(set(films_with_covers)&set(lines))))
        if num_films_with_covers > 0:
            print(f'\nApplying thumbnails to {num_films_with_covers} films...')
            for f in films_with_covers:
                if f not in lines:
                    print(str(f))
                    try:
                        video = MP4("{}.mp4".format(f))
                        os.chdir(cover_dir)
                        with open("{} COVER.jpg".format(f), "rb") as cov:
                            video["covr"] = [MP4Cover(cov.read(), imageformat=MP4Cover.FORMAT_JPEG)]
                        os.chdir(movie_dir)
                        file.write(str(f)+'\n')
                        video.save()
                    except:
                        print('Failed: '+ str(f))
                        continue

def apply_covers_to_TV_shows(cover_dir,driver_dir,movie_dir,show_dir,anime_dir):
    film_paths, film_names_and_years = get_mp4s(show_dir)
    cover_paths , cover_names = get_cover_files(cover_dir)
    films_without_covers, films_with_covers = compare(film_names_and_years, cover_names)
    os.chdir(show_dir)
    all_titles, all_paths = read_alexandria([movie_dir,show_dir,anime_dir])
    tv_shows = []
    tv_show_paths = []
    for at in range(len(all_titles)):
        if ':/Movies' not in all_paths[at]:
            tv_shows.append(all_titles[at])
            tv_show_paths.append(all_paths[at])
    os.chdir(show_dir)
    print_statment_bool = True
    with open("_covered_shows.txt",mode='a+',encoding='utf-8') as file2:
        file2.seek(0)
        lines = file2.readlines()
        lines = [str(l).strip() for l in lines]
        num_to_cover = int(len(tv_shows) - len(list(set(tv_shows)&set(lines))))
        if num_to_cover > 0:
            for f in range(len(tv_shows)):
                if tv_shows[f] not in lines:
                    if print_statment_bool: print(f'\nApplying thumbnails to {num_to_cover} TV shows...'); print_statment_bool = False
                    print(str(tv_shows[f]))
                    try:
                        os.chdir(tv_show_paths[f])
                        video = MP4("{}.mp4".format(tv_shows[f]))
                        os.chdir(cover_dir)
                        with open("{} COVER.jpg".format(' '.join(tv_shows[f].split()[:-1])), "rb") as cov:
                            video["covr"] = [MP4Cover(cov.read(), imageformat=MP4Cover.FORMAT_JPEG)]
                        os.chdir(show_dir)
                        file2.write(str(tv_shows[f])+'\n')
                        os.chdir(tv_show_paths[f])
                        video.save()
                    except:
                        print('Failed: '+ str(f))
                        continue

### BACKUP FUNCTIONS ###

def read_whitelist(drive_name):
    os.chdir(r'C:\Users\brend\Documents\Coding Projects\Alexandria\Show Lists')
    whitelist_file_name = '_'.join(drive_name.split())+'_whitelist.txt'
    with open (whitelist_file_name,mode='r') as file:
        return [w.strip() for w in file.readlines()]

def do_I_backup_this_movie(drive,primary_drive,movie,no_movie_drives = ['ColdStorage']):
    movie_list = []
    noBackup_movieFiles = []
    keywords = []
    drive_name = get_drive_name(drive)
    if drive_name in no_movie_drives:
        return False
    elif drive_name == 'AnimeStorage':
        with open(f'{primary_drive}:/Movies/_covered_movies.txt',mode='r',encoding='utf-8') as mvs:
            all_mvs = [l.strip() for l in mvs.readlines()]
        with open('C:/Users/brend/Documents/Coding Projects/Alexandria/Show Lists/anime_movies.txt',mode='r',encoding='utf-8') as amvs:
            anime_mvs = [l.strip() for l in amvs.readlines()]
        movie_list = [m for m in all_mvs if m not in anime_mvs]
        if movie in movie_list:
            return False
        return True
    elif drive_name == 'MikesMovies' or drive_name == 'Alexandria' or drive_name == 'DaniMovies':
        noBackup_movieFiles = ['anime_movies.txt']
        keywords = ['Scooby-Doo','Pokémon','Chipmunks','Tom and Jerry','Atlas Shrugged','Futurama']
    elif drive_name == 'Alexandria 2':
        keywords = ['Scooby-Doo','Pokémon','Chipmunks','Tom and Jerry','Atlas Shrugged','Futurama']
    os.chdir(r'C:\Users\brend\Documents\Coding Projects\Alexandria\Show Lists')
    for nbmf in noBackup_movieFiles:
        with open(nbmf,mode='r',encoding='utf-8') as movie_file:
            movie_list += [m.strip() for m in movie_file.readlines()]
    if movie in movie_list:
        return False
    for k in keywords:
        if k in movie:
            return False
    return True

def backup(pd,bd,no_movie_drives = ['ColdStorage']):
    def backup_function(backup_tuples):
        for bt in backup_tuples: print('Backing up: {}'.format(bt[0].split('/')[-1][:-4].strip())); shutil.copyfile(bt[0], bt[1])
    def split_backup_tuples(num_threads,backup_tuples):
        backup_tracker = [[] for nt in range(num_threads)]
        i = 0
        for bt in backup_tuples: 
            backup_tracker[i].append(bt); i += 1
            if i == num_threads: i = 0
        return backup_tracker
    def integrity_assurance(pd,bd):
        primary_titles, primary_paths = read_alexandria([f'{pd}:/Movies/',f'{pd}:/Shows/',f'{pd}:/Anime/'])
        backup_titles, backup_paths = read_alexandria([f'{bd}:/Movies/',f'{bd}:/Shows/',f'{bd}:/Anime/'])
        primary_items = [(primary_paths[i] + '/' +primary_titles[i])[1:] for i in range(len(primary_titles))]
        backup_items = [(backup_paths[i] + '/' +backup_titles[i])[1:] for i in range(len(backup_titles))]
        combined_items = sorted(list(set(backup_items)&set(primary_items)))
        with alive_bar(len(combined_items),ctrl_c=False,dual_line=True,title='Integrity Check',bar='classic',spinner='classic') as bar:
            for i in range(len(combined_items)):
                if os.stat(f'{pd}{combined_items[i]}.mp4').st_size != os.stat(f'{bd}{combined_items[i]}.mp4').st_size:
                    print(f'[{i+1}/{len(combined_items)}] Rewriting {combined_items[i].split("/")[-1]}')
                    shutil.copyfile(f'{pd+combined_items[i]}.mp4', f'{bd+combined_items[i]}.mp4')
                bar()
    primary_titles, primary_paths = read_alexandria([f'{pd}:/Movies/',f'{pd}:/Shows/',f'{pd}:/Anime/'])
    backup_titles, backup_paths = read_alexandria([f'{bd}:/Movies/',f'{bd}:/Shows/',f'{bd}:/Anime/'])
    primary_items = [(primary_paths[i] + '/' +primary_titles[i])[1:] for i in range(len(primary_titles))]
    backup_items = [(backup_paths[i] + '/' +backup_titles[i])[1:] for i in range(len(backup_titles))]
    not_in_backup = []
    for pi in primary_items:
        if pi not in backup_items: not_in_backup.append(pi)
    not_in_primary = []
    for bi in backup_items:
        if bi not in primary_items: not_in_primary.append(bi)
    ui = 'n'
    if len(not_in_primary) > 0:
        print(f'\nThe following files are not in {drive_colors[primary_drive]}{Style.BRIGHT}{get_drive_name(primary_drive)}{Style.RESET_ALL}:')
        for nip in not_in_primary:
            print(nip)
        ui = ''
        while ui != 'n' and ui != 'y':
            if len(not_in_primary) > 1:
                ui = input(f'Do you want to delete these {len(not_in_primary)} items? [Y/N] ').lower()
            else:
                ui = input('Do you want to delete this item? [Y/N] ').lower()
    if ui.lower() == 'y':
        for nip in not_in_primary:
            print(f'Deleting: {bd}{nip}')
            os.remove(f'{bd}{nip}.mp4')
    ### backup primary ###
    print(f'\nBacking up {drive_colors[pd]}{Style.BRIGHT}{get_drive_name(pd)}{Style.RESET_ALL} files to {drive_colors[bd]}{Style.BRIGHT}{get_drive_name(bd)}{Style.RESET_ALL}...\n')
    drive_name = get_drive_name(bd)
    whitelist = read_whitelist(drive_name)
    backup_tuples = []
    for i in range(len(not_in_backup)):
        file = ''.join(not_in_backup[i].split('/')[-1]).strip()
        if ' '.join(file.split()[:-1]) not in whitelist and not_in_backup[i].split('/')[1]!='Movies': continue
        if drive_name in no_movie_drives and not_in_backup[i].split('/')[1]=='Movies': continue 
        if not do_I_backup_this_movie(bd,pd,file,no_movie_drives): continue
        path = '/'.join(not_in_backup[i].split('/')[:-1]).strip()+'/'
        ppath = pd+path
        bpath = bd+path
        original = r'{}{}.mp4'.format(ppath,file)
        target = r'{}{}.mp4'.format(bpath,file)
        while True:
            if os.path.isdir(bpath):
                backup_tuples.append((original,target))
                break
            else:
                try:
                    os.mkdir(bpath)
                    print(f'Creating path: {bpath}')
                    backup_tuples.append((original,target))
                    break
                except:
                    index = -2
                    while True:
                        try:
                            bpath2 = '/'.join(bpath.split('/')[:index])
                            os.mkdir(bpath2)
                            print(f'Creating path: {bpath2}')
                            break
                        except:
                            index += 1
                            if index > len(bpath.split('/')):
                                break
    multi_threading_bool = False
    if len(backup_tuples) > 4: multi_threading_bool = True
    if multi_threading_bool:
        if len(backup_tuples) > 4: num_threads = 4
        else: num_threads = len(backup_tuples)
        backup_tracker = split_backup_tuples(num_threads,backup_tuples)
        from threading import Thread
        t1 = Thread(target=backup_function,args=(backup_tracker[0],))
        t2 = Thread(target=backup_function,args=(backup_tracker[1],))
        t3 = Thread(target=backup_function,args=(backup_tracker[2],))
        t4 = Thread(target=backup_function,args=(backup_tracker[3],))
        t1.start(); t2.start(); t3.start(); t4.start()
        t1.join(); t2.join(); t3.join(); t4.join()
    else:
        backup_tracker = split_backup_tuples(1,backup_tuples)
        backup_function(backup_tracker[0])
    integrity_assurance(pd,bd)
    drives = [pd,bd]
    for i,d in enumerate(drives):
        disk_obj = shutil.disk_usage(f'{d}:/')
        gb_remaining = int(disk_obj[2]/10**9)
        if i == 0: print(f'\n{gb_remaining:,} GB of space left on {drive_colors[d]}{Style.BRIGHT}{get_drive_name(d)}{Style.RESET_ALL}...')    
        else: print(f'{gb_remaining:,} GB of space left on {drive_colors[d]}{Style.BRIGHT}{get_drive_name(d)}{Style.RESET_ALL}...')  
        
### ANALYTICS FUNCTIONS ###

def find_duplicates_and_show_data(drive):
    print(f'\nFinding duplicate files on {drive_colors[drive]}{Style.BRIGHT}{get_drive_name(drive)} ({drive} drive){Style.RESET_ALL}...')
    are_there_duplicates = False
    cleared_duplciates = []
    duplicates = []
    file_names, file_paths = read_alexandria([f'{drive}:/Movies/',f'{drive}:/Shows/',f'{drive}:/Anime/'])
    file_names_with_path = [file_paths[i]+'/'+file_names[i]+'.mp4' for i in range(len(file_paths)) if file_paths[i] != f'{drive}:/Movies']
    show_files = {}
    show_sizes = {}
    for fnwp in file_names_with_path:
        file_path_list = []
        show_name = ' '.join(fnwp.split('/')[2].split()[:-1]).strip()
        for fnwp2 in file_names_with_path:
            if show_name+' (' and show_name+' S' in fnwp2:
                file_path_list.append(fnwp2)
        show_files.update({show_name:file_path_list})
    shows = list(show_files.keys())
    os.chdir(r'C:\Users\brend\Documents\Coding Projects\Alexandria')
    with open(f'show_menu_{drive}_drive.txt', mode = 'w', encoding = 'utf-8') as menu_file:
        for s in shows:
            total_size_in_gb = 0
            episode_sizes = []
            show_episode_files = show_files[s]
            if len(show_episode_files) == 0: continue
            show_seasons = []
            for sef in show_episode_files:
                size_in_gb = get_file_size(sef)
                episode_sizes.append(size_in_gb)
                total_size_in_gb += size_in_gb
                show_seasons.append(f'{sef.split("/")[3].strip()}')
            show_seasons = list(set(show_seasons))
            year = show_episode_files[0].split('/')[2].split()[-1][1:-1]
            menu_file.write(f'{s}, {year}, {len(show_seasons)} {"Seasons" if len(show_seasons) != 1 else "Season"}, {len(show_episode_files)} Episodes, {total_size_in_gb:,.2f} GB\n')
            for i, es in enumerate(episode_sizes):
                 if episode_sizes.count(es) > 1:
                    ep_file = show_episode_files[i].split("/")[-1].split(".mp4")[0]
                    if ep_file not in cleared_duplciates:
                        print(f'Match: {ep_file} is {es} GB')
                        are_there_duplicates = True
                        duplicates.append(ep_file)
            show_sizes.update({s:total_size_in_gb})
    show_sizes = dict(sorted(show_sizes.items(), key=lambda item: item[1],reverse=True))
    os.chdir(r'C:\Users\brend\Documents\Coding Projects\Alexandria')
    with open(f'show_sizes_{drive}_drive.txt', mode = 'w', encoding = 'utf-8') as size_file:
        size_file.seek(0)
        for s in list(show_sizes.keys()):
            percent = round(show_sizes[s]/sum(list(show_sizes.values()))*100,2)
            size_file.write(f'{s}: {round(show_sizes[s],2)} GB ({percent}%)\n')
    if not are_there_duplicates:
        print('\nNo Duplicates found.')
        return None
    else:
        # print('\nDuplicates found:')
        with open(f'duplicate_shows_{drive}_drive.txt', mode = 'w', encoding = 'utf-8') as duplicates_file:
            duplicates_file.seek(0)
            for d in duplicates:
                # print(d)
                duplicates_file.write(d+'\n')
        return duplicates

def check_backup_surface_area(pd, drives):
    connected_drives = []
    mp4_tracker = {}
    drives += [pd]
    for d in drives:
        if not does_drive_exist(d): continue
        connected_drives.append(d)
        file_names, file_paths = read_alexandria([f'{d}:/Movies/',f'{d}:/Shows/',f'{d}:/Anime/'])
        files = [file_paths[i][3:]+'/'+file_names[i] for i in range(len(file_names))]
        for f in files:
            try:
                mp4_tracker[f] +=1
            except KeyError:
                mp4_tracker.update({f:1})
    one_count_list = []
    two_count_list = []
    threePlus_count_list = []
    mp4_keys = list(mp4_tracker.keys())
    for m in mp4_keys:
        count = mp4_tracker[m]
        if count == 1:
            one_count_list.append(f'{pd}:/{m}')
        elif count == 2:
            two_count_list.append(f'{pd}:/{m}')
        elif count >= 3:
            threePlus_count_list.append(f'{pd}:/{m}')
    with open('not_backed_up_files.txt',mode='w',encoding='utf-8') as file:
        file.seek(0)
        ocls = []
        for i,ocl in enumerate(sorted(list(set([' '.join(o.split('/')[-1].split()[:-1]) for o in one_count_list if o.split('/')[1] != 'Movies'])))):
            if i == 0: print('\nThe following shows are not backed up:')
            show_size = get_show_size(get_show_files(pd,ocl))
            if ocl.split('(')[0].strip() in ocls: continue
            ocls.append(ocl.split('(')[0].strip())
            file.write(f'{ocl}: {show_size} GB\n')
            print(f'{ocl}: {show_size} GB')
    total = len(one_count_list)+len(two_count_list)+len(threePlus_count_list)
    singleCountPercent = len(one_count_list)/total*100
    doubleCountPercent = len(two_count_list)/total*100
    triplePlusCountPercent = len(threePlus_count_list)/total*100
    singleData = sum([get_file_size(ocl+'.mp4') for ocl in one_count_list])
    doubleData = sum([get_file_size(tcl+'.mp4') for tcl in two_count_list])
    triplePlusData = sum([get_file_size(tpcl+'.mp4') for tpcl in threePlus_count_list])
    totalData = sum([singleData,doubleData,triplePlusData])
    print(f'\nAcross the {len(connected_drives)} connected drives: {", ".join(sorted([get_drive_name(c) for c in connected_drives]))}\n')
    print(f'{(singleData/totalData)*100:.2f}% of data ({singleData/1000:,.2f} TB) is not backed up')
    print(f'{singleCountPercent:.2f}% of files are not backed up\n###')    
    print(f'{(doubleData/totalData)*100:.2f}% of data ({doubleData/1000:,.2f} TB) is backed up once')
    print(f'{doubleCountPercent:.2f}% of files are backed up once\n###')
    print(f'{(triplePlusData/totalData)*100:.2f}% of data ({triplePlusData/1000:,.2f} TB) is backed up more than once')
    print(f'{triplePlusCountPercent:.2f}% of files are backed up more than once')

def determine_backup_feasibility(pd, bd, no_movie_drives = ['ColdStorage']):
    drive_name = get_drive_name(bd)
    drive_size = get_drive_size(bd)
    whitelist = read_whitelist(drive_name)
    file_names, file_paths = read_alexandria([f'{pd}:/Movies/',f'{pd}:/Shows/',f'{pd}:/Anime/'])
    tv_names_with_path = [file_paths[i]+'/'+file_names[i]+'.mp4' for i in range(len(file_paths)) if file_paths[i] != f'{primary_drive}:/Movies']
    movie_names_with_path = [file_paths[i]+'/'+file_names[i]+'.mp4' for i in range(len(file_paths)) if file_paths[i] == f'{primary_drive}:/Movies']  
    curr_file_names, curr_file_paths = read_alexandria([f'{bd}:/Movies/',f'{bd}:/Shows/',f'{bd}:/Anime/'])
    curr_file_names = [curr_file_names[i] for i in range(len(curr_file_paths)) if curr_file_paths[i] != f'{bd}:/Movies']
    curr_shows = list(set([' '.join(cfn.split()[:-1]) for cfn in curr_file_names]))
    curr_shows_not_in_whitelist = [cs for cs in curr_shows if cs not in whitelist]
    if len(curr_shows_not_in_whitelist) > 0:
        print(f'\nThe following shows are not in {drive_name}\'s whitelist, but exist on the drive:')
        for csniw in curr_shows_not_in_whitelist:
            print('> '+csniw)
    size_needed = 0
    for mnwp in movie_names_with_path:
        if drive_name not in no_movie_drives:
            if do_I_backup_this_movie(bd,pd,mnwp.split('/')[-1].split('.mp4')[0],no_movie_drives):
                  size_needed += get_file_size(mnwp)
    for tnwp in tv_names_with_path:
        name = ' '.join(tnwp.split('/')[-1].split()[:-1])
        if name in whitelist or name in curr_shows_not_in_whitelist:
            size_needed += get_file_size(tnwp)
    # print(f'Drive Size: {drive_size}, Backup Size {size_needed}')
    if drive_size > size_needed:
        return True
    else:
        print(f'\nThe requested backup to {drive_name} ({bd} drive) is {int(size_needed - drive_size)} GB too big!')
        return False

def get_drive_stats(drive):
    file_names, file_paths = read_alexandria([f'{drive}:/Movies/',f'{drive}:/Shows/',f'{drive}:/Anime/'])
    num_movie_files = len([f for f in file_paths if f == f'{drive}:/Movies'])
    num_show_files = len([f for f in file_paths if f'{drive}:/Shows' in f])
    num_shows = len(list(set([f.split('/')[2].strip() for f in file_paths if f'{drive}:/Shows' in f])))
    num_anime_files = len([f for f in file_paths if f'{drive}:/Anime' in f])
    num_animes = len(list(set([f.split('/')[2].strip() for f in file_paths if f'{drive}:/Anime' in f])))
    print(f'\n{drive_colors[drive]}{Style.BRIGHT}{get_drive_name(drive)}{Style.RESET_ALL} Stats:')
    print(f'{num_movie_files:,} Movies, {num_shows:,} TV Shows ({num_show_files:,} TV Show files), {num_animes:,} Anime shows ({num_anime_files:,} Anime files)')
    
### MAIN FUNCTION ###

def main(primary_drive,backup_drive,no_movie_drives):
    # backup_drive = 'E'
    cover_dir = f"{primary_drive}:/MP4_COVERS/"
    driver_dir = 'C:/Users/brend/'
    movie_dir = f"{primary_drive}:/Movies/"
    show_dir = f'{primary_drive}:/Shows/'
    anime_dir = f'{primary_drive}:/Anime/'
    print(f'\nPrimary Drive: {drive_colors[primary_drive]}{Style.BRIGHT}{get_drive_name(primary_drive)} ({primary_drive} drive){Style.RESET_ALL}')
    print(f'Backup Drive: {drive_colors[backup_drive]}{Style.BRIGHT}{get_drive_name(backup_drive)} ({backup_drive} drive){Style.RESET_ALL}')
    ###
    get_covers(cover_dir,driver_dir,movie_dir,show_dir,anime_dir)
    ###
    apply_covers_to_movies(cover_dir,driver_dir,movie_dir)
    ###
    apply_covers_to_TV_shows(cover_dir,driver_dir,movie_dir,show_dir,anime_dir)
    ###
    if determine_backup_feasibility(primary_drive,backup_drive,no_movie_drives):
        backup(primary_drive,backup_drive,no_movie_drives)

def set_color_scheme(primary_drive,drives):
    global drive_colors
    drive_colors = {primary_drive:Fore.YELLOW}
    possible_colors = [Fore.GREEN,Fore.MAGENTA,Fore.RED,Fore.BLUE,Fore.CYAN]
    for i,d in enumerate(drives):
        drive_colors.update({d:possible_colors[i % len(possible_colors)]})

if __name__ == '__main__':
    # starts time
    start_time = time.time()
    # define the primary_drive
    primary_drive = 'V'
    # define the drives to NOT backup into
    drive_blacklist = ['C','T',primary_drive]
    # searches for backup drives
    drives = [sau for sau in string.ascii_uppercase if does_drive_exist(sau) and sau != os.getcwd()[0] and sau not in drive_blacklist]
    # sets color scheme for print statements relating to drives
    set_color_scheme(primary_drive,drives)
    # defines drives that should not backup movies (from <drive>:/Movies directory)
    no_movie_drives = ['ColdStorage'] # drives with no movies
    # prints time the script starts
    print(f'\nMain process initiated at {get_time()}...\n\n#################################')
    for backup_drive in drives:
        main(primary_drive,backup_drive,no_movie_drives)
        print('\n#################################')
    # searches for duplicate files within shows in the primary drive
    duplicates = find_duplicates_and_show_data(primary_drive)
    time.sleep(1)
    # determines what percentage of files are backed up at different levels
    check_backup_surface_area(primary_drive,drives)
    # fetches file stats for the primary drive
    get_drive_stats(primary_drive)
    print('\n#################################')
    print(f'\nMain process completed at {get_time()}.')
    get_time_elapsed(start_time)
    if sys.stdin and sys.stdin.isatty(): time.sleep(100)