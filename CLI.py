#!/usr/bin/env python
import argparse
import os
import subprocess
import json

ALLOWED_EXTENSIONS_APK = set(['apk'])

# check if the apk_file and apk_test_file are in format
def allowed_file_apk(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_APK

# get condition's informations
def check(list):
    cond = ""
    if not list is None:
        for i in xrange(len(list)):
            cond += '"'
            cond += list[i]
            cond += '"'
            if not i == len(list) - 1:
                cond += ", "
    else:
        cond += '""'
    return cond

def check_file_exists(path_filename):
    if os.path.isfile(path_filename):
        return False
    return True

def create_json(data, object, key, value):
    data[object].update({key: value})
    return data

def main():
    parser = argparse.ArgumentParser()
    
    # internet address
    parser.add_argument('--address', type=str, help="Host IP or web address")
    
    # test_project_name
    parser.add_argument('--project', type=str, help="Test project name")
    
    # apk_file / apke_test_file
    parser.add_argument('--apk', nargs=1, help="Application APK")
    parser.add_argument('--test-apk', nargs=1, help="Test application APK")
    
    # conditions
    parser.add_argument('--os', nargs='*', default=[''], help="Android release")
    parser.add_argument('--API', nargs='*', default=[''], help="API Level")
    parser.add_argument('--deviceType', nargs='*', default=[''], help="Board Specifications")
    parser.add_argument('--display', nargs='*', default=[''], help="Density")
    parser.add_argument('--arch', nargs='*', default=[''], help="CPU")
    
    # optional arguments
    parser.add_argument('--adb-timeout', nargs=1, help="Set maximum execution time per test in seconds")
    
    show_group = parser.add_mutually_exclusive_group()
    # informations
    show_group.add_argument('-q', '--quiet', action='store_true', help="simple output")
    show_group.add_argument('-v', '--verbose', action='store_true', help="detailed output")
    
    args = parser.parse_args()
    print args
        
    address = '127.0.0.1:5000'
    
    if args.address:
        address = args.address

    if args.apk and args.test_apk and args.project:
        test_project_name = args.project
        apk_file = args.apk[0]
        apk_test_file = args.test_apk[0]
        
        if not allowed_file_apk(apk_file) or not allowed_file_apk(apk_test_file):
            print "please make sure the files are in .apk format"
            return
        
        if check_file_exists(apk_file) or check_file_exists(apk_test_file):
            print "no apk or test_apk file in current folder"
            return

        # uploads
        subprocess.check_call(['curl', '-F', 'test_project_name=' + test_project_name, '-F', 'apk_file=@' + apk_file, '-F', 'apk_test_file=@' + apk_test_file, '-X', 'POST', address + '/uploads'])

    if args.project:
        test_project_name = args.project
        conditions = ""
        full_conditions = ""
        
        if args.os or args.API or args.deviceType or args.display or args.arch:
            conditions += check(args.os) + " " + check(args.API) + " " + check(args.deviceType) + " " + check(args.display) + " " + check(args.arch)
            full_conditions += "os: " + check(args.os) + "\nAPI: " + check(args.API) + "\ndeviceType: " + check(args.deviceType) + "\ndisplay: " + check(args.display) + "\narch: " + check(args.arch)
            
        else:
            conditions = "None"
            full_conditions = "None"
        
        if args.verbose:
            print 'The test project name is "' + test_project_name + '"'
            print 'APK files are "' + apk_file + '", "' + apk_test_file + '"'
            print full_conditions

        elif args.quiet:
            print test_project_name
            print apk_file, apk_test_file
            print conditions

        else:
            print "Project: " + test_project_name
            print "APK: " + apk_file, apk_test_file
            print "Requirements: " + conditions

        data = {}
        data['project'] = {}
        data['devices'] = {}
        data = create_json(data, 'project', 'project_name', test_project_name)
        data = create_json(data, 'devices', 'os', args.os)
        data = create_json(data, 'devices', 'API Level', args.API)
        data = create_json(data, 'devices', 'deviceType', args.deviceType)
        data = create_json(data, 'devices', 'display', args.display)
        data = create_json(data, 'devices', 'arch', args.arch)

        with open("testing_project.json", 'w') as outfile:
            json.dump(data, outfile, indent=4)

        # test
        subprocess.check_call(['curl', '-F', 'testing_project_json=@testing_project.json', '-X', 'POST', address + '/uploads_testing_project'])

        #subprocess.call(['rm', 'testing_project.json'])

    else:
        # get sevices status
        subprocess.call(['curl', address + '/get_devices_status'])

if __name__ == '__main__':
    main()
