#!/usr/bin/env python3

def import_libraries():
    """
    Helps load/install required libraries when running from cmd prompt

    Returns
    -------
    None.

    """
    import pip
    import warnings
    warnings.filterwarnings("ignore")
    exec('warnings.filterwarnings("ignore")')
    aliases = {'numpy':'np','pandas':'pd'}
    libraries = ['alive_progress','colorama','ffmpeg','glob','integv','json','mutagen','os','numpy','pymediainfo','random','sys',
                 'pandas','selenium','shutil','time','urllib','urllib.request','warnings','win32file']
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
import json
import os
import numpy as np
import pandas as pd
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
from colorama import Fore, Style, Back
from mutagen.mp4 import MP4, MP4Cover
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pymediainfo import MediaInfo

def read_alexandria(parent_dirs,extensions = ['.mp4','.mkv']):
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
        walk = sorted(list([x for x in os.walk(p) if 'metadata' not in x[0] and (x[0][-1] in string.digits or x[0][-2] in string.digits or 'Movies' in x[0] or 'Temp' in x[0]) and x[2] != []]))
        for w in walk:
            parent_path = w[0]
            if parent_path[-1] == '/': parent_path = parent_path[:-1]
            file_list = [f for f in w[-1] if f[-4:] in extensions]
            for i,f in enumerate(file_list):
                all_titles.append(f.replace('\\','/'))
                all_paths.append(parent_path.replace('\\','/'))
    return all_titles, all_paths

def get_time():
    """
    Returns current time.
    
    Returns
    -------
    curr_time: str
        Time in 'TTTT on DDMMMYYYY' format.
        
    """
    time_dict = {'dotw':time.ctime().split()[0],'month':time.ctime().split()[1],'day':time.ctime().split()[2],
                 'hour_24_clock':time.ctime().split()[3].split(':')[0],'minute':time.ctime().split()[3].split(':')[1],
                 'second':time.ctime().split()[3].split(':')[2],'year':time.ctime().split()[4]}
    if len(time_dict["minute"]) < 2: time_dict['minute'] = '0'+time.ctime().split()[3].split(':')[1]
    if len(time_dict["day"]) < 2: time_dict['day'] = '0'+time.ctime().split()[2]
    curr_time = f'{time_dict["hour_24_clock"]}{time_dict["minute"]} on {time_dict["day"]}{time_dict["month"].upper()}{time_dict["year"][2:]}'
    return curr_time

def get_time_elapsed(start_time):
    """
    Prints the elapsed time since the input time.
    
    Parameters
    ----------
    start_time : float
        Time as a floating pouint number in seconds.

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
        Drive letter [A-Z] (Windows).

    Returns
    -------
    bool
        Returns TRUE if drive exists, otherwise returns FALSE.
        
    """
    return (win32file.GetLogicalDrives() >> (ord(letter.upper()) - 65) & 1) != 0

def get_drive_name(letter):
    """
    Gets drive name from letter.

    Parameters
    ----------
    letter : str
        Drive letter [A-Z] (Windows).

    Returns
    -------
    str
        Return name of the drive, as displayed in file explorer.

    """
    return win32api.GetVolumeInformation(f"{letter}:/")[0]

def get_drive_size(letter):
    return shutil.disk_usage(f'{letter}:/')[0]/10**9

def get_file_size(file_with_path):
    try:
        if file_with_path[-4] == '.': return os.path.getsize(file_with_path)/10**9
        else: return os.path.getsize(file_with_path)/10**9
    except FileNotFoundError:
        if file_with_path[-4] == '.': return os.path.getsize(file_with_path[:-4]+'.mkv')/10**9
        else: return os.path.getsize(file_with_path)/10**9

def get_show_files(show):
    file_names, file_paths = read_alexandria([movie_dir,show_dir,anime_dir,anime_movie_dir])
    show_files_with_path1 = [file_paths[i]+'/'+file_names[i] for i in range(len(file_paths)) if 'Movies' not in file_paths[i]]
    show_files_with_path2 = [sfwp for sfwp in show_files_with_path1 if show == sfwp.split('/')[2].split('(')[0].strip()]
    return show_files_with_path2

def get_show_size(show_files_with_path):
    if isinstance(show_files_with_path, str): show_files_with_path = get_show_files(show_files_with_path)
    show_size = 0
    for sfwp in show_files_with_path: show_size += get_file_size(sfwp)  
    return round(show_size,2)

def get_space_remaining(drive):
    for i,d in enumerate([primary_drive,secondary_drive,drive]):
        disk_obj = shutil.disk_usage(f'{d}:/')
        gb_remaining = int(disk_obj[2]/10**9)
        if i == 0: print(f'\n{gb_remaining:,} GB of space left on {drive_colors[d]}{Style.BRIGHT}{get_drive_name(d)}{Style.RESET_ALL}...')    
        else: print(f'{gb_remaining:,} GB of space left on {drive_colors[d]}{Style.BRIGHT}{get_drive_name(d)}{Style.RESET_ALL}...')  

def get_shows_list(drive):
    all_titles, all_paths = read_alexandria([f'{drive}:\\Shows\\',f'{drive}:\\Anime\\'])
    return sorted(list(set([' '.join(at.split()[:-1]) for at in all_titles])))

def order_txt_doc(txt_file):
    try:
        if txt_file[-4:] != '.txt': txt_file += '.txt'
        with open(txt_file,mode='r',encoding='utf-8') as file: items = sorted(list(set([l.strip() for l in file.readlines()])))
        temp_files = [x[:-4] for x in read_alexandria([f'{primary_drive}:\\Temp\\'],['.mp4','.mkv'])[0]]
        if '_covered_movies' in txt_file: 
            primary_movies = [m[:-4].strip() for m in read_alexandria([movie_dir,anime_movie_dir],['.mp4','mkv'])[0]]
            with open(txt_file,mode='w',encoding='utf-8') as file: 
                file.seek(0)
                for i in items:
                    if i in primary_movies and i not in temp_files:
                        file.write(i+'\n')
        elif '_covered_episodes' in txt_file: 
            primary_shows = [m[:-4].strip() for m in read_alexandria([show_dir,anime_dir],['.mp4','.mkv'])[0]]
            with open(txt_file,mode='w',encoding='utf-8') as file: 
                file.seek(0)
                for i in items:
                    if i in primary_shows:
                        file.write(i+'\n')
        else:
            with open(txt_file,mode='w',encoding='utf-8') as file: 
                file.seek(0)
                for i in items:
                    file.write(i+'\n')
    except FileNotFoundError:
        pass

### FILE THUMBNAIL FUNCTIONS ###
    
def create_driver(headless=True):
    options = webdriver.ChromeOptions()
    if headless: options.add_argument("headless")
    options.add_argument('--log-level=3'); options.add_argument("--silent")
    try:
        return webdriver.Chrome(rf"{driver_dir}/chromedriver.exe", chrome_options=options)
    except NameError:
        return webdriver.Chrome("C:/Users/brend/chromedriver.exe", chrome_options=options)

def remove_duplicate_tv_shows(all_titles):
    all_titles2 = []
    for at in all_titles:
        if at[-1] == ')': all_titles2.append(at)
        else: all_titles2.append(' '.join(at.split()[:-1]))
    return sorted(list(set(all_titles2)))

def get_mp4s(mp4_dir_list):
    # os.chdir(mp4_dir)
    film_names_and_years = []
    film_paths = []
    for mpFour in mp4_dir_list:
        film_paths += [gg.replace('\\','/') for gg in glob.glob(f"{mpFour}*.mp4")]
        for i in range(len(film_paths)): film_names_and_years.append(film_paths[i].split('/')[-1])
    return film_paths, film_names_and_years

def get_cover_files():
    cover_paths = [gg.replace('\\','/') for gg in glob.glob(f"{cover_dir}*.jpg")]
    cover_names = []
    for i in range(len(cover_paths)): cover_names.append(".".join(cover_paths[i].split('/')[-1].split('.')[:-1]))
    return cover_paths, cover_names

def compare(film_names_and_years, cover_names):
    films_without_covers, films_with_covers = [], []
    film_names_and_years = [fnay[:-4] if fnay[-4:-2] == '.m' else fnay for fnay in film_names_and_years]
    for f in film_names_and_years:
        if f+' COVER' not in cover_names: films_without_covers.append(f)
        else: films_with_covers.append(f)
    return films_without_covers, films_with_covers

def save_cover(driver,name,search):
    driver.get('https://www.google.ca/imghp?hl=en&tab=ri&authuser=0&ogbl')
    try:
        driver.find_element_by_xpath('//*[@id="L2AGLb"]/div').click()
    except:
        pass
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
    search_box.send_keys('{} poster'.format(search))
    search_box.send_keys(Keys.ENTER)
    img = driver.find_element_by_xpath('//*[@id="islrg"]/div[1]/div[1]/a[1]/div[1]/img')
    if name[-4:-2] == '.m': name = name[:-4]
    urllib.request.urlretrieve(img.get_attribute('src'),f'{cover_dir}{name} COVER.jpg')

def get_covers():
    cover_paths , cover_names = get_cover_files()
    # primary_titles = remove_duplicate_tv_shows(read_alexandria([movie_dir,show_dir,anime_dir,anime_movie_dir])[0])
    p_names = sorted(list(set([' '.join(p.rstrip().split()[:-1]) if p.rstrip().split()[-1][0] == 'S' or p.rstrip().split()[-1][-3] == 'E' or p.rstrip().split()[-1][3] == 'E' else p for p in primary_titles])))
    films_without_covers, films_with_covers = compare(p_names, cover_names)
    index = 0
    while len(films_without_covers) > 0:
        if index == 0 and len(films_without_covers) > 1: print('\nFetching film/show covers...')
        if index == 0 and len(films_without_covers) == 1: print('\nFetching film/show cover...')
        driver = create_driver()
        for fwc in films_without_covers:
            if fwc[-4:-2] == '.m': search = fwc[:-4]
            else: search = fwc
            if search.strip()[-1] != ")": search += ' TV SHOW tvdb'
            else: search += ' IMDB'
            print(' '.join(search.split()[:-1]))
            save_cover(driver,fwc,search)
            time.sleep(np.random.exponential(0.5))
        driver.quit()
        film_paths, film_names_and_years = get_mp4s([movie_dir,anime_movie_dir])
        cover_paths , cover_names = get_cover_files()
        films_without_covers, films_with_covers = compare(film_names_and_years, cover_names)

def apply_covers_to_movies():
    movie_dirs = [movie_dir,anime_movie_dir]
    for mdir in movie_dirs:
        # film_paths, film_names_and_years = get_mp4s([mdir])
        movie_files = read_alexandria([mdir],['.mp4'])[0]
        cover_paths , cover_names = get_cover_files()
        films_with_covers = sorted(list(set(compare(movie_files, cover_names)[1])))        
        os.chdir(mdir)
        with open(fr'{primary_drive}:\Movies\_covered_movies.txt',mode='a+',encoding='utf-8') as file:
            file.seek(0)
            lines = file.readlines()
            lines = [str(l).strip() for l in lines]
            films_with_covers = [f for f in movie_files if f[:-4] not in lines and f[-4:] == '.mp4']
            num_films_with_covers = len(films_with_covers)
            if num_films_with_covers > 100:
                ui = ''
                while ui not in ['y','n']:
                    ui = input(f'Do you want to thumbnail {num_films_with_covers} films/shows? [y/n] ').lower()
                if ui == 'n':
                    return None
            if num_films_with_covers > 0:
                if num_films_with_covers == 1: print(f'\nApplying thumbnail to {num_films_with_covers} film in {mdir}...\n')
                else: print(f'\nApplying thumbnails to {num_films_with_covers} films in {mdir}...')
                for f in films_with_covers:
                    if f[:-4] not in lines:
                        print(str(f[:-4]))
                        video = MP4("{}{}".format(mdir+'/'+str(f[:-4])+'/',f))
                        os.chdir(cover_dir)
                        with open("{} COVER.jpg".format(f[:-4]), "rb") as cov:
                            video["covr"] = [MP4Cover(cov.read(), imageformat=MP4Cover.FORMAT_JPEG)]
                        os.chdir(mdir+'/'+str(f[:-4])+'/')
                        file.write(str(f[:-4])+'\n')
                        lines.append(str(f[:-4]))
                        video.save()
    for mdir in movie_dirs:
        order_txt_doc(f'{mdir}/_covered_movies.txt')

def apply_covers_to_TV_shows():
    for d in [show_dir,anime_dir]:
        show_files, shows = read_alexandria([d],['.mp4'])
        shows = list(set([' '.join(x.split('/')[2].split()[:-1]) for x in shows]))
        cover_paths , cover_names = get_cover_files()
        films_without_covers, films_with_covers = compare(shows, cover_names)
        os.chdir(d)
        tv_shows = []
        tv_show_paths = []
        for at in range(len(primary_titles)):
            if 'Movies' not in primary_paths[at]:
                tv_shows.append(primary_titles[at])
                tv_show_paths.append(primary_paths[at])
        os.chdir(d)
        print_statment_bool = True
        with open(f'{show_dir}_covered_episodes.txt',mode='a+',encoding='utf-8') as file2:
            file2.seek(0)
            lines = file2.readlines()
            lines = [str(l).strip() for l in lines]
            num_to_cover = len([x for x in tv_shows if x[:-4] not in lines and x[-4:] == '.mp4'])
            if num_to_cover > 0:
                for f in range(len(tv_shows)):
                    if tv_shows[f][:-4] not in lines and tv_shows[f][-4:] == '.mp4':
                        if print_statment_bool and num_to_cover > 1: print(f'\nApplying thumbnails to {num_to_cover:,} show episodes...\n'); print_statment_bool = False
                        if print_statment_bool and num_to_cover == 1: print(f'\nApplying thumbnails to {num_to_cover} show episode...\n'); print_statment_bool = False
                        print(str(tv_shows[f])[:-4])
                        os.chdir(tv_show_paths[f])
                        video = MP4("{}".format(tv_shows[f]))
                        os.chdir(cover_dir)
                        with open("{} COVER.jpg".format(' '.join(tv_shows[f].split()[:-1])), "rb") as cov:
                            video["covr"] = [MP4Cover(cov.read(), imageformat=MP4Cover.FORMAT_JPEG)]
                        os.chdir(d)
                        file2.write(str(tv_shows[f][:-4])+'\n')
                        os.chdir(tv_show_paths[f])
                        video.save()
        order_txt_doc(f'{show_dir}_covered_episodes.txt')

### BACKUP FUNCTIONS ###

def read_whitelist(drive_name):
    os.chdir(rf'{os_drive}:\Users\brend\Documents\Coding Projects\Alexandria\Show Lists')
    whitelist_file_name = '_'.join(drive_name.split())+'_whitelist.txt'
    with open (whitelist_file_name,mode='r') as file:
        return [w.strip() for w in file.readlines()]

def movie_score_filter(threshold):
    directory = 'V:/EmbyServerCache/omdb'
    try:
        dirs = sorted([x[0].replace('\\','/') for x in os.walk(directory) if x[0] != directory],key = lambda x: int(x.split('/')[-1]))
        if dirs == []: dirs = [directory]
        all_files_omdb = []
        for d in dirs:
            all_files_omdb += sorted([gg.replace('\\','/') for gg in glob.glob(f'{d}/*.json')])
        while [] in all_files_omdb: all_files_omdb.remove([])
        meta = []
        for af in all_files_omdb:
            with open(af,'r',encoding='utf-8') as file:
                data = json.load(file)
            try:
                if int(data['Runtime'].split()[0]) < 60: continue
                title = data['Title']
                year = data['Year']    
                imdbRating = float(data['imdbRating'])
                metascore = float(data['Metascore'])
                if imdbRating == '': continue
                meta.append([title,year,imdbRating,metascore])
            except (KeyError, IndexError, ValueError):
                continue
        df_omdb = pd.DataFrame(meta,columns=['Title','Year','IMDB Rating','Metascore'])
        df_omdb.to_csv(rf'{os_drive}:\Users\brend\Documents\Coding Projects\Alexandria\omdb.csv')
    except:
        df_omdb = pd.read_csv(rf'{os_drive}:\Users\brend\Documents\Coding Projects\Alexandria\omdb.csv')
    df_filters = df_omdb[df_omdb['IMDB Rating'] < threshold].reset_index(drop=True)
    bad_movies = [f"{df_filters.loc[i,'Title']} ({df_filters.loc[i,'Year']})" for i in range(len(df_filters))]
    return bad_movies

def do_I_backup_this_movie(drive,movie,bad_movies,no_movie_drives = ['ColdStorage']):
    if not 'primary_drive' in globals():
        global primary_drive; primary_drive = 'S'
    if not 'secondary_drive' in globals():
        global secondary_drive; secondary_drive = 'N'
    if movie not in bad_movies and drive not in no_movie_drives:
        # movie_list = []
        # noBackup_movieFiles = []
        keywords = []
        drive_name = get_drive_name(drive)
        no_anime_drives = ['Alexandria','DaniMovies',"Mike's Movies",'NielsonMovies']
        if drive_name in no_movie_drives:
            return False
        elif drive_name in no_anime_drives:
            anime_movies = [m[:-4] for m in read_alexandria([anime_movie_dir])[0]]
            if movie in anime_movies:
                return False
            # noBackup_movieFiles = ['anime_movies.txt']
            keywords = ['Scooby-Doo','Pokémon','Chipmunks','Tom and Jerry','Atlas Shrugged','Futurama']
        elif drive_name == 'Alexandria 2':
            keywords = ['Scooby-Doo','Pokémon','Chipmunks','Tom and Jerry','Atlas Shrugged','Futurama']
        # os.chdir(rf'{os_drive}:\Users\brend\Documents\Coding Projects\Alexandria\Show Lists')
        # for nbmf in noBackup_movieFiles:
        #     with open(nbmf,mode='r',encoding='utf-8') as movie_file:
        #         movie_list += [m.strip() for m in movie_file.readlines()]
        # if movie in movie_list:
        #     return False
        for k in keywords:
            if k in movie:
                return False
        return True
    return False

def backup(bd,no_movie_drives = ['ColdStorage']):
    def backup_function(backup_tuples):
        for bt in backup_tuples: print('Backing up: {}'.format(bt[0].split('/')[-1][:-4].strip())); shutil.copyfile(bt[0], bt[1])
    def split_backup_tuples(num_threads,backup_tuples):
        backup_tracker = [[] for nt in range(num_threads)]
        i = 0
        for bt in backup_tuples: 
            backup_tracker[i].append(bt); i += 1
            if i == num_threads: i = 0
        return backup_tracker
    def integrity_assurance(bd):
        # primary_titles, primary_paths = read_alexandria([movie_dir,show_dir,anime_dir,anime_movie_dir])
        # backup_titles, backup_paths = read_alexandria([f'{bd}:/Movies/',f'{bd}:/Shows/',f'{bd}:/Anime/',f'{bd}:/Anime Movies'])
        primary_items = [(primary_paths[i] + '/' +primary_titles[i])[1:] for i in range(len(primary_titles))]
        backup_items = [(backup_paths[i] + '/' +backup_titles[i])[1:] for i in range(len(backup_titles))]
        combined_items = sorted(list(set(backup_items)&set(primary_items)))
        with alive_bar(len(combined_items),ctrl_c=False,dual_line=True,title='Integrity Check',bar='classic',spinner='classic') as bar:
            for i in range(len(combined_items)):
                if 'Anime' in combined_items[i] or '4K' in combined_items[i]:
                    primary_size = os.stat(f'{secondary_drive}{combined_items[i]}').st_size
                else:
                    primary_size = os.stat(f'{primary_drive}{combined_items[i]}').st_size
                backup_size = os.stat(f'{bd}{combined_items[i]}').st_size
                if primary_size != backup_size and primary_size > 100:
                    print(f'[{i+1}/{len(combined_items)}] Rewriting \"{combined_items[i].split("/")[-1][:-4]}"')
                    if 'Anime' in combined_items[i] or '4k' in combined_items:
                        shutil.copyfile(f'{secondary_drive+combined_items[i]}', f'{bd+combined_items[i]}')
                    else:
                        shutil.copyfile(f'{primary_drive+combined_items[i]}', f'{bd+combined_items[i]}')                        
                bar()
    # primary_titles, primary_paths = read_alexandria([movie_dir,show_dir,anime_dir,anime_movie_dir])
    backup_titles, backup_paths = read_alexandria([f'{bd}:/Movies/',f'{bd}:/Shows/',f'{bd}:/Anime/',f'{bd}:/Anime Movies/'])
    primary_items = [(primary_paths[i] + '/' +primary_titles[i])[1:] for i in range(len(primary_titles))]
    backup_items = [(backup_paths[i] + '/' +backup_titles[i])[1:] for i in range(len(backup_titles))]
    not_in_backup = []
    for pi in primary_items:
        if pi not in backup_items: not_in_backup.append(pi)
    not_in_primary = []
    for bi in backup_items:
        if bi not in primary_items: not_in_primary.append(bi)
    ui = ''
    if len(not_in_primary) > 0:
        print(f'\n{Back.RED}The following files are not in the primary drives:')
        for nip in not_in_primary:
            print(nip)
        ui = ''
        while ui != 'n' and ui != 'y':
            if len(not_in_primary) > 1:
                ui = input(f'\nDo you want to delete these {len(not_in_primary)} items? [Y/N] ').lower()
            else:
                ui = input('\nDo you want to delete this item? [Y/N] ').lower()
    if ui.lower() == 'y':
        for nip in not_in_primary:
            print(f'Deleting: {Style.BRIGHT}{bd}{nip}{Style.RESET_ALL}')
            os.remove(f'{bd}{nip}')
    ### backup primary ###
    drive_name = get_drive_name(bd)
    whitelist = read_whitelist(drive_name)
    backup_tuples = []
    bad_movies = movie_score_filter(imdb_min)
    for i in range(len(not_in_backup)):
        file = ''.join(not_in_backup[i].split('/')[-1]).strip()
        if ' '.join(file.split()[:-1]) not in whitelist and 'Movies' not in not_in_backup[i].split('/')[1]: continue
        if drive_name in no_movie_drives and 'Movies' in not_in_backup[i].split('/')[1]: continue
        if 'Movies' not in not_in_backup[i].split('/')[1]: pass
        else: 
            if not do_I_backup_this_movie(bd,file[:-4],bad_movies,no_movie_drives): continue
        path = '/'.join(not_in_backup[i].split('/')[:-1]).strip()+'/'
        if 'Anime' in path or '4K' in path:
            ppath = secondary_drive+path
        else: 
            ppath = primary_drive+path
        bpath = bd+path
        original = r'{}{}'.format(ppath,file)
        target = r'{}{}'.format(bpath,file)
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
                except FileNotFoundError:
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
    if len(backup_tuples) == 1: print(f'\nBacking up {len(backup_tuples)} file to {drive_colors[bd]}{Style.BRIGHT}{get_drive_name(bd)}{Style.RESET_ALL}...\n')
    elif len(backup_tuples) > 0: print(f'\nBacking up {len(backup_tuples)} files to {drive_colors[bd]}{Style.BRIGHT}{get_drive_name(bd)}{Style.RESET_ALL}...\n')
    else: print('\n'); integrity_assurance(bd); return 0
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
        t1.start(); time.sleep(0.1); t2.start(); time.sleep(0.1); t3.start(); time.sleep(0.1); t4.start()
        t1.join(); t2.join(); t3.join(); t4.join()
    else:
        backup_tracker = split_backup_tuples(1,backup_tuples)
        backup_function(backup_tracker[0])
    integrity_assurance(bd)
    # for i,d in enumerate([primary_drive,bd]):
    #     disk_obj = shutil.disk_usage(f'{d}:/')
    #     gb_remaining = int(disk_obj[2]/10**9)
    #     if i == 0: print(f'\n{gb_remaining:,} GB of space left on {drive_colors[d]}{Style.BRIGHT}{get_drive_name(d)}{Style.RESET_ALL}...')    
    #     else: print(f'{gb_remaining:,} GB of space left on {drive_colors[d]}{Style.BRIGHT}{get_drive_name(d)}{Style.RESET_ALL}...')  
        
### ANALYTICS FUNCTIONS ###


def write_show_catalog():
    shows_only_paths = list(set([p.split('/')[-2] for p in primary_paths if 'Shows' in p]))
    year_sorted = sorted(shows_only_paths,key = lambda x: (x.split()[-1],' '.join(x.split()[:-1])),reverse=(True))
    with open(rf'{os_drive}:\Users\brend\Documents\Coding Projects\Alexandria\year_sorted_shows.txt', mode='w',encoding='utf-8') as file:
        file.seek(0)
        for p in year_sorted:
            file.write(p+'\n')

def find_duplicates_and_show_data():
    write_show_catalog()
    print('\nSearching for duplicate files...')
    are_there_duplicates = False
    cleared_duplciates = ['Shaun the Sheep S03E10','Shaun the Sheep S05E07']
    duplicates = []
    # primary_titles, primary_paths = read_alexandria([movie_dir,show_dir,anime_dir,anime_movie_dir])
    file_names_with_path = [primary_paths[i]+'/'+primary_titles[i] for i in range(len(primary_paths)) if 'Movies' not in primary_paths[i]]
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
    os.chdir(rf'{os_drive}:\Users\brend\Documents\Coding Projects\Alexandria')
    with open('show_menu.txt', mode = 'w', encoding = 'utf-8') as menu_file:
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
                    ep_file = '.'.join(show_episode_files[i].split("/")[-1].split(".")[:-1])
                    if ep_file not in cleared_duplciates:
                        print(f'{Fore.RED}{Style.BRIGHT}Match{Style.RESET_ALL}: {ep_file} is {es} GB')
                        are_there_duplicates = True
                        duplicates.append(ep_file)
            show_sizes.update({s:total_size_in_gb})
    show_sizes = dict(sorted(show_sizes.items(), key=lambda item: (item[1],item[0]),reverse=True))
    os.chdir(rf'{os_drive}:\Users\brend\Documents\Coding Projects\Alexandria')
    with open('show_sizes.txt', mode = 'w', encoding = 'utf-8') as size_file:
        size_file.seek(0)
        for s in list(show_sizes.keys()):
            percent = round(show_sizes[s]/sum(list(show_sizes.values()))*100,2)
            size_file.write(f'{s}: {round(show_sizes[s],2)} GB ({percent}%)\n')
    if not are_there_duplicates:
        print(f'\n{Back.GREEN}No Duplicates found.{Style.RESET_ALL}')
        return None
    else:
        print(f'\n{Back.RED}Duplicates found{Style.RESET_ALL}')
        with open('duplicate_shows.txt', mode = 'w', encoding = 'utf-8') as duplicates_file:
            duplicates_file.seek(0)
            for d in duplicates:
                # print(d)
                duplicates_file.write(d+'\n')
        return duplicates

def check_backup_surface_area(drives):
    connected_drives = []
    mp4_tracker = {}; show_tracker = {}
    if primary_drive not in drives: drives += [primary_drive]
    if secondary_drive not in drives: drives += [secondary_drive]
    for d in drives:
        if not does_drive_exist(d): continue
        connected_drives.append(d)
        file_names, file_paths = read_alexandria([f'{d}:/Movies/',f'{d}:/Shows/',f'{d}:/Anime/',f'{d}:/Anime Movies/','f{d}:/4K Movies'])
        files = [[file_paths[i][3:]+'/'+file_names[i],file_paths[i][0]] for i in range(len(file_names))]
        for f in files:
            try:
                mp4_tracker[f[0]][0] += 1
                mp4_tracker[f[0]][1].append(f[1])
            except KeyError:
                mp4_tracker.update({f[0]:[1,[f[1]]]})
    connected_drives = sorted(connected_drives,key=lambda x: get_drive_name(x))
    one_count_list = []; two_count_list = []; threePlus_count_list = []
    mp4_keys = list(mp4_tracker.keys())
    for m in mp4_keys:
        count = mp4_tracker[m][0]
        drive_list = ', '.join(mp4_tracker[m][1]).strip()
        if m not in list(show_tracker.keys()) and 'Movies' not in m: show_tracker.update({' '.join(m.split('/')[1].split()[:-1]):(count,drive_list)})
        if 'Movies' in m or 'Shows' in m:
            parent_drive = 'S'
        if 'Anime' in m or '4K' in m:
            parent_drive = 'N'
        if count == 1:
            one_count_list.append(f'{parent_drive}:/{m}')
        elif count == 2:
            two_count_list.append(f'{parent_drive}:/{m}')
        elif count >= 3:
            threePlus_count_list.append(f'{parent_drive}:/{m}')
    with open('not_backed_up_files.txt',mode='w',encoding='utf-8') as file:
        file.seek(0)
        ocls = []
        for i,ocl in enumerate(sorted(list(set([' '.join(o.split('/')[-1].split()[:-1]) for o in one_count_list if 'Movies' not in o.split('/')[1]])))):
            if i == 0: print(f'\n{Back.YELLOW}The following shows are not backed up:{Style.RESET_ALL}')
            show_size = get_show_size(get_show_files(ocl))
            if ocl.split('(')[0].strip() in ocls: continue
            ocls.append(ocl.split('(')[0].strip())
            file.write(f'{ocl}: {show_size} GB\n')
            print(f'{ocl}: {show_size} GB')
    drive_string = ''
    for c in connected_drives:
        drive_string += f'{drive_colors[c]}{Style.BRIGHT}{get_drive_name(c)}{Style.RESET_ALL}, '
    print(f'\nAssessing backup surface area across {drive_string.rstrip()[:-1]}...')
    show_tracker = dict(sorted(show_tracker.items(), key=lambda item: (item[1][0],item[0])))
    with open('show_backup_tracker.txt',mode='w',encoding='utf-8') as file:
        file.seek(0)
        for st in list(show_tracker.keys()):
            file.write(f'{st}: {show_tracker[st][0]} [{show_tracker[st][1]}] ({get_show_size(get_show_files(st))} GB)\n')
    total = len(one_count_list)+len(two_count_list)+len(threePlus_count_list)
    singleCountPercent = len(one_count_list)/total*100
    doubleCountPercent = len(two_count_list)/total*100
    triplePlusCountPercent = len(threePlus_count_list)/total*100
    singleData = sum([get_file_size(ocl) for ocl in one_count_list])
    # FileNotFoundError; problem with files on backup but not on main drive
    doubleData = sum([get_file_size(tcl) for tcl in two_count_list])
    triplePlusData = sum([get_file_size(tpcl) for tpcl in threePlus_count_list])
    totalData = sum([singleData,doubleData,triplePlusData])
    # print(f'\nAcross the {len(connected_drives)} connected drives: {", ".join(sorted([str({drive_colors[c]}{Style.BRIGHT}{get_drive_name(c)}{Style.RESET_ALL}) for c in connected_drives]))}\n')
    print(f'\nAcross the {len(connected_drives)} connected drives: '+drive_string.rstrip()[:-1])
    print(f'{(singleData/totalData)*100:.2f}% of data ({singleData/1000:,.2f} TB) is not backed up')
    print(f'{singleCountPercent:.2f}% of files are not backed up\n###')    
    print(f'{(doubleData/totalData)*100:.2f}% of data ({doubleData/1000:,.2f} TB) is backed up once')
    print(f'{doubleCountPercent:.2f}% of files are backed up once\n###')
    print(f'{(triplePlusData/totalData)*100:.2f}% of data ({triplePlusData/1000:,.2f} TB) is backed up more than once')
    print(f'{triplePlusCountPercent:.2f}% of files are backed up more than once')

def determine_backup_feasibility(bd, no_movie_drives = ['ColdStorage']):
    try:
        drive_name = get_drive_name(bd)
        drive_size = get_drive_size(bd)
        whitelist = read_whitelist(drive_name)
        # primary_titles, primary_paths = read_alexandria([movie_dir,show_dir,anime_dir,anime_movie_dir])
        tv_names_with_path = [primary_paths[i]+'/'+primary_titles[i] for i in range(len(primary_paths)) if 'Movies' not in primary_paths[i]]
        movie_names_with_path = [primary_paths[i]+'/'+primary_titles[i] for i in range(len(primary_paths)) if 'Movies' in primary_paths[i]]
        # curr_file_names, curr_file_paths = read_alexandria([f'{bd}:/Movies/',f'{bd}:/Shows/',f'{bd}:/Anime/',f'{bd}:/Anime Movies'])
        # curr_file_names, curr_file_paths = backup_titles, backup_paths
        curr_file_names = [backup_titles[i] for i in range(len(backup_paths)) if 'Movies' not in backup_paths[i]]
        curr_shows = list(set([' '.join(cfn.split()[:-1]) for cfn in curr_file_names]))
        curr_shows_not_in_whitelist = [cs for cs in curr_shows if cs not in whitelist]
        if len(curr_shows_not_in_whitelist) > 0:
            # print(f'\nThe following shows are not in {drive_name}\'s whitelist, but exist on the drive:')
            for csniw in curr_shows_not_in_whitelist:
                pass
                # print('> '+csniw)
        size_needed = 0
        bad_movies = movie_score_filter(imdb_min)
        for mnwp in movie_names_with_path:
            if drive_name not in no_movie_drives:
                if do_I_backup_this_movie(bd,'.'.join(mnwp.split('/')[-1].split('.')[:-1]),bad_movies,no_movie_drives):
                      size_needed += get_file_size(mnwp)
        for tnwp in tv_names_with_path:
            name = ' '.join(tnwp.split('/')[-1].split()[:-1])
            if name in whitelist:
                size_needed += get_file_size(tnwp)
        # print(f'Drive Size: {drive_size}, Backup Size {size_needed}')
        shows_on_drive = get_shows_list(bd)
        not_on_whitelist = []
        not_backed_up = []
        for show in shows_on_drive:
            if show not in whitelist and show != 'Spongebob Squarepants':
                not_on_whitelist.append(show)
        for wShow in whitelist:
            if wShow not in shows_on_drive:
                not_backed_up.append(wShow)
        if len(not_on_whitelist) > 0:
            if len(not_on_whitelist) == 1: print(f'\n{len(not_on_whitelist)} Show Unexpectedly on {drive_colors[bd]}{Style.BRIGHT}{drive_name} ({bd} drive){Style.RESET_ALL}')
            else: print(f'\n{len(not_on_whitelist)} Shows Unexpectedly on {drive_colors[bd]}{Style.BRIGHT}{drive_name} ({bd} drive){Style.RESET_ALL}\n')
            for now in not_on_whitelist:
                ui = ''
                while ui not in ['y','n']:
                    ui = input(f'Do you want to delete {Back.CYAN}{now}{Style.RESET_ALL} from {drive_colors[bd]}{Style.BRIGHT}{drive_name}{Style.RESET_ALL}? [Y/N] ').lower()
                if ui == 'y':
                    print(f'Deleting {Back.CYAN}{now}{Style.RESET_ALL} from {drive_colors[bd]}{Style.BRIGHT}{drive_name}{Style.RESET_ALL}...\n')
                    files_with_path = [bd+x[1:] for x in get_show_files(now)]
                    shows_with_path = list(set(['/'.join(fwp.split('/')[:-2]) for fwp in files_with_path]))
                    # for fwp in files_with_path:
                    #     os.remove(fwp)
                    for swp in shows_with_path:
                        # print(swp)
                        if len(swp.split('/'))  > 2:
                            shutil.rmtree(swp)
        if len(not_backed_up) > 0:
            if len(not_backed_up) == 1: print(f'\n{len(not_backed_up)} show not backed up {drive_colors[bd]}{Style.BRIGHT}{drive_name} ({bd} drive){Style.RESET_ALL}')
            else: print(f'\n{len(not_backed_up)} shows not backed up to {drive_colors[bd]}{Style.BRIGHT}{drive_name} ({bd} drive){Style.RESET_ALL}')
            for i,nbu in enumerate(not_backed_up):
                print(f'[-] {nbu}')
                # if i == len(not_backed_up) - 1 : print('\n')
        if drive_size > size_needed:
            return True
        else:
            print(f'\nThe requested backup to {drive_colors[bd]}{Style.BRIGHT}{drive_name} ({bd} drive){Style.RESET_ALL} is {int(size_needed - drive_size)} GB too big!\n')     
            return False
    except FileNotFoundError as e:
        print(f'Backup feasibility check bypassed due to error: {e}')
        return True

def get_stats():
    primary_titles, primary_paths = read_alexandria([movie_dir,show_dir,anime_dir,anime_movie_dir,uhd_movie_dir])
    movies = []; tv_shows = []; animes = []; uhd_movies = []
    for i,f in enumerate(primary_paths):
        if 'Movies' in f and '4K' not in f:
            movies.append(f+'/'+primary_titles[i])
        elif ':/Shows' in f:
            tv_shows.append(f+'/'+primary_titles[i])
        elif ':/Anime' in f:
            animes.append(f+'/'+primary_titles[i])
        elif ':/4K Movies/' in f:
            uhd_movies.append(f+'/'+primary_titles[i])
    num_show_files = len(tv_shows)
    num_shows = len(list(set(([f.split('/')[2].strip() for f in tv_shows]))))
    size_shows = round(sum([get_file_size(show) for show in tv_shows])/10**3,2)
    num_anime_files = len(animes)
    num_animes = len(list(set(([f.split('/')[2].strip() for f in animes]))))
    size_animes = round(sum([get_file_size(anime) for anime in animes])/10**3,2)
    num_movie_files = len(movies)
    size_movies = round(sum([get_file_size(movie) for movie in movies])/10**3,2)
    num_4k_movie_files = len(uhd_movies)
    size_4k_movies = round(sum([get_file_size(movie) for movie in uhd_movies])/10**3,2)    
    print('\nDatabase Stats:')
    print(f'{num_movie_files:,} HD Movies ({size_movies:,} TB)\n{num_4k_movie_files:,} 4K Movies ({size_4k_movies:,} TB)\n{num_shows:,} TV Shows ({num_show_files:,} TV Show Episodes, {size_shows:,} TB)\n{num_animes:,} Anime Shows ({num_anime_files:,} Anime Episodes, {size_animes:,} TB)')
    
### MAIN FUNCTION ###

def main(backup_drive,no_movie_drives):
    print(f'\nPrimary Drive: {drive_colors[primary_drive]}{Style.BRIGHT}{get_drive_name(primary_drive)} ({primary_drive} drive){Style.RESET_ALL}')
    print(f'Secondary Drive: {drive_colors[secondary_drive]}{Style.BRIGHT}{get_drive_name(secondary_drive)} ({secondary_drive} drive){Style.RESET_ALL}')
    print(f'Backup Drive: {drive_colors[backup_drive]}{Style.BRIGHT}{get_drive_name(backup_drive)} ({backup_drive} drive){Style.RESET_ALL}')
    ###
    # get_covers()
    ###
    # apply_covers_to_movies()
    ###
    # apply_covers_to_TV_shows()
    ###
    if determine_backup_feasibility(backup_drive,no_movie_drives):
        backup(backup_drive,no_movie_drives)
    ###
    get_space_remaining(backup_drive)


def set_color_scheme(drives):
    """
    Defines global variable drive_colors in support of print statements

    Parameters
    ----------
    drives : list
        List of backup drive letters.

    Returns
    -------
    None.

    """
    global drive_colors; drive_colors = {primary_drive:Fore.YELLOW,
                                         secondary_drive:Fore.GREEN}
    possible_colors = [Fore.MAGENTA,Fore.BLUE,Fore.CYAN,Fore.RED]
    for i,d in enumerate(drives):
        drive_colors.update({d:possible_colors[i % len(possible_colors)]})
        
def get_imdb_minimum(drive):
    """
    

    Parameters
    ----------
    drive : string
        Letter of backup drive.

    Returns
    -------
    float
        Returns the minimum IMDB rating of movies to be backed up on the drive.

    """
    imdb_min_path = rf'{os_drive}:\Users\brend\Documents\Coding Projects\Alexandria\imdb_drive_minimums.txt'
    with open(imdb_min_path,mode='r',encoding='utf-8') as imdb_file:
        lines = imdb_file.readlines()
    imdb_dict = {}
    for l in lines:
        imdb_dict.update({l.split('|')[0].strip():float(l.split('|')[1].strip())})
    return imdb_dict.get(get_drive_name(drive),5.99)

global os_drive; os_drive = 'C'
if __name__ == '__main__':
    # sets global variables & define the primary_drive and secondary_drive
    global primary_drive; primary_drive = 'S'
    global secondary_drive; secondary_drive = 'N'
    global cover_dir; cover_dir = f"{primary_drive}:/MP4_COVERS/"
    global driver_dir; driver_dir = f'{os_drive}:/Users/brend/'
    global movie_dir; movie_dir = f"{primary_drive}:/Movies/"
    global uhd_movie_dir; uhd_movie_dir = f"{secondary_drive}:/4K Movies/"
    global show_dir; show_dir = f'{primary_drive}:/Shows/'
    global anime_dir; anime_dir = f'{secondary_drive}:/Anime/'
    global anime_movie_dir; anime_movie_dir = f'{secondary_drive}:/Anime Movies/'
    global primary_titles; global primary_paths; primary_titles, primary_paths = read_alexandria([movie_dir,show_dir,anime_dir,anime_movie_dir])
    global backup_titles; global backup_paths
    global imdb_min
    # starts time
    start_time = time.time()
    # define the drives to NOT backup into
    drive_blacklist = [os_drive,primary_drive,secondary_drive,'T']
    # searches for backup drives
    drives = [sau for sau in string.ascii_uppercase if does_drive_exist(sau) and sau != os.getcwd()[0] and sau not in drive_blacklist]
    # sets color scheme for print statements relating to drives
    set_color_scheme(drives)
    # defines drives that should not backup movies (from <drive>:/Movies directory)
    global no_movie_drives; no_movie_drives = ['ColdStorage'] # drives with no movies
    # prints time the script starts
    print(f'\nMain process initiated at {get_time()}...\n\n#################################')
    for bd in drives:
        imdb_min = get_imdb_minimum(bd)
        backup_titles, backup_paths = read_alexandria([f'{bd}:/Movies/',f'{bd}:/Shows/',f'{bd}:/Anime/',f'{bd}:/Anime Movies'])
        try:
            main(bd,no_movie_drives)
        except OSError as e:
            print(f'Error: {e}')
            print(f'\n{bd} drive is likely full')
            continue
        print('\n#################################')
    # searches for duplicate files within shows in the primary drive
    primary_titles, primary_paths = read_alexandria([movie_dir,show_dir,anime_dir,anime_movie_dir])
    duplicates = find_duplicates_and_show_data()
    time.sleep(1)
    # determines what percentage of files are backed up at different levels
    check_backup_surface_area(drives)
    time.sleep(1)
    # fetches file stats for the primary drive
    get_stats()
    txt_doc_list = [rf'{os_drive}:\Users\brend\Documents\Coding Projects\Alexandria\Show Lists\anime_movies.txt',
                    rf'{os_drive}:\Users\brend\Documents\Coding Projects\Alexandria\Show Lists\anime_shows.txt',
                    rf'{os_drive}:\Users\brend\Documents\Coding Projects\Alexandria\Show Lists\Alexandria_whitelist.txt',
                    rf'{os_drive}:\Users\brend\Documents\Coding Projects\Alexandria\Show Lists\Alexandria_2_whitelist.txt',
                    rf'{os_drive}:\Users\brend\Documents\Coding Projects\Alexandria\Show Lists\Alexandria_4_whitelist.txt',
                    rf'{os_drive}:\Users\brend\Documents\Coding Projects\Alexandria\Show Lists\DaniMovies_whitelist.txt',
                    rf"{os_drive}:\Users\brend\Documents\Coding Projects\Alexandria\Show Lists\Mike's_Movies_whitelist.txt"]
    for tdl in txt_doc_list:
        order_txt_doc(tdl)
    print('\n#################################')
    print(f'\nMain process completed at {get_time()}.')
    get_time_elapsed(start_time)
    if sys.stdin and sys.stdin.isatty(): time.sleep(100)

# Good idea section
'''
rewrite functions to deal with video files with extensions other than .mp4
Create runtime metric
Create tool that overwrites COVERs with poster files
Create a tool that detects episodes named different than show
'''    



    
