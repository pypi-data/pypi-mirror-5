#!/usr/bin/env python

# pywws - Python software for USB Wireless Weather Stations
# http://github.com/jim-easterbrook/pywws
# Copyright (C) 2008-13  Jim Easterbrook  jim@jim-easterbrook.me.uk

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

"""Convert EasyWeather.dat data to pywws format
::

%s

This program assumes that EasyWeather used your local time, and
converts time stamps to UTC. This can create ambiguities when the
clocks go back in October, which the program attempts to detect and
correct.

"""

__docformat__ = "restructuredtext en"
__usage__ = """
 usage: python -m pywws.EWtoPy [options] EasyWeather_file data_dir
 options are:
  -h or --help    display this help
 EasyWeather_file is the input data file, e.g. EasyWeather.dat
 data_dir is the root directory of the weather data
"""
__doc__ %= __usage__
__usage__ = __doc__.split('\n')[0] + __usage__

from datetime import datetime, timedelta
import getopt
import os
import sys

from pywws import DataStore
from pywws import TimeZone

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        opts, args = getopt.getopt(argv[1:], "h", ['help'])
    except getopt.error, msg:
        print >>sys.stderr, 'Error: %s\n' % msg
        print >>sys.stderr, __usage__.strip()
        return 1
    # process options
    for o, a in opts:
        if o in ('-h', '--help'):
            print >>sys.stderr, __usage__.strip()
            return 0
    # check arguments
    if len(args) != 2:
        print >>sys.stderr, 'Error: 2 arguments required\n'
        print >>sys.stderr, __usage__.strip()
        return 2
    # process arguments
    in_name = args[0]
    out_name = args[1]
    # open input
    in_file = open(in_name, 'r')
    # open data file store
    ds = DataStore.data_store(out_name)
    # get time to go forward to
    first_stored = ds.after(datetime.min)
    if first_stored == None:
        first_stored = datetime.max
    # copy any missing data
    last_date = None
    count = 0
    for line in in_file:
        items = line.split(',')
        local_date = DataStore.safestrptime(items[2].strip(), '%Y-%m-%d %H:%M:%S')
        local_date = local_date.replace(tzinfo=TimeZone.Local)
        date = local_date.astimezone(TimeZone.utc)
        if last_date and date < last_date:
            date = date + timedelta(hours=1)
            print "Corrected DST ambiguity %s %s -> %s" % (
                local_date, local_date.tzname(), date)
        last_date = date
        date = date.replace(tzinfo=None)
        # get data
        data = {}
        data['delay'] = int(items[3])
        data['hum_in'] = int(items[4])
        data['temp_in'] = float(items[5])
        try:
            data['hum_out'] = int(items[6])
        except:
            data['hum_out'] = None
        try:
            data['temp_out'] = float(items[7])
        except:
            data['temp_out'] = None
        data['abs_pressure'] = float(items[10])
        try:
            data['wind_ave'] = float(items[12])
        except:
            data['wind_ave'] = None
        try:
            data['wind_gust'] = float(items[14])
        except:
            data['wind_gust'] = None
        try:
            data['wind_dir'] = int(items[16])
        except:
            data['wind_dir'] = None
        data['rain'] = int(items[18]) * 0.3
        data['status'] = int(items[35].split()[15], 16)
        # check against first_stored
        if first_stored - date < timedelta(minutes=data['delay'] // 2):
            break
        ds[date] = data
        count += 1
    print "%d records written" % count
    in_file.close()
    del ds
    return 0
if __name__ == "__main__":
    sys.exit(main())
