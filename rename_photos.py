#! /usr/bin/env python

from PIL import Image
from PIL.ExifTags import TAGS
import argparse
import glob
import os
import datetime

def parse_direc(direc):
    """
    Parse files in specified directory.

    Args:
        direc (str): Directory where files reside. Supported filetypes: jpeg,
            png.
    Returns:
        files (array-like) Files to be renamed.
    """
    print("Working in directory {}".format(direc))

    files = glob.glob(os.path.join(direc, "*jpeg")) + \
            glob.glob(os.path.join(direc, "*jpg")) + \
            glob.glob(os.path.join(direc, "*png")) + \
            glob.glob(os.path.join(direc, "*JPEG")) + \
            glob.glob(os.path.join(direc, "*JPG")) + \
            glob.glob(os.path.join(direc, "*PNG"))

    return files

def get_exif(filename):
    """ 
    Modified from code at:
    https://www.blog.pythonlibrary.org/2010/03/28/getting-photo-metadata-exif-using-python/
    
    Args:
        filename (str): Pathname of file.
    Returns:
        exif_info (dict): EXIF information.
    """
    
    exif_info = {}
    i = Image.open(filename)
    info = i._getexif()
    if info is None:
        return None
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        exif_info[decoded] = value
    
    return exif_info

def rename_files(files, in_format="%Y:%m:%d %H:%M:%S", 
                 out_format="%Y%m%d_%H%M%S", 
                 offset=None):
    """
    Rename photo filenames to reflect their datetime.

    Args:
        files (array-liked): Files to be renamed.
        in_format (str): Input photo's EXIF DateTime format in
            datetime.datetime nomenclature.
        out_format (str): Renamed output photo's name format in 
            datetime.datetime noemnclature.
        offset (float or None): If not None, an offset, in hours,
            to apply to the datetime filename.
    Returns:
        None
    """

    for item in files:
        filename = os.path.basename(item)
        file_noext = filename.split(".")[0]
        # Sometimes the file format is already what we want.
#        try:
#            dt = datetime.datetime.strptime(file_noext, out_format)
#            continue
#        except:
#            pass
        
        exif_info = get_exif(item)
        
        # In case the file doesn't have the necessary data.
        if exif_info is None:
            print("\tERROR: Cannot get EXIF info for {}".format(filename))
            continue
        
        p_date = exif_info["DateTime"]
        p_dt = datetime.datetime.strptime(p_date, in_format)
        if offset is not None:
            p_dt += datetime.timedelta(hours=offset)
        out_name = p_dt.strftime(out_format)
        out_file = item.replace(file_noext, out_name)
        # These shouldn't happen, but just in case.
        if out_file == item:
            continue
        if os.path.isfile(out_file):
            out_file = item.replace(file_noext, out_name+"_2")

        os.rename(item, out_file)
        print("\tRenamed {} -> {}".format(filename,
                                        os.path.basename(out_file)))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(dest="direc", 
                        help="Name of directory where files should be renamed")
    parser.add_argument("-i", dest="in_format", default="%Y:%m:%d %H:%M:%S",
                        help="Input photo's EXIF DateTime format")
    parser.add_argument("-o", dest="out_format", default="%Y%m%d_%H%M%S",
                        help="Renamed output photo's name format")
    args = parser.parse_args()
    
    files = parse_direc(args.direc)
    rename_files(files, args.in_format, args.out_format)
