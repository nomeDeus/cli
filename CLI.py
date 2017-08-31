#!/usr/bin/env python
import argparse
import os
import subprocess
import socket

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

def main():
    parser = argparse.ArgumentParser()
    
    # host IP
    parser.add_argument('--host', type=str, help="Host IP")
    
    # test_project_name
    parser.add_argument('-n', '--name', type=str, help="Test project name")
    
    # apk_file / apke_test_file
    parser.add_argument('--apk', nargs=1, help="Application APK")
    parser.add_argument('--test-apk', nargs=1, help="Test application APK")
    
    # conditions
    parser.add_argument('--os', nargs='*', help="Android release")
    parser.add_argument('--API', nargs='*', help="API Level")
    parser.add_argument('--deviceType', nargs='*', help="Board Specifications")
    parser.add_argument('--display', nargs='*', help="Density")
    parser.add_argument('--arch', nargs='*', help="CPU")
    
    # optional arguments
    parser.add_argument('--adb-timeout', nargs=1, help="Set maximum execution time per test in seconds")
    
    show_group = parser.add_mutually_exclusive_group()
    # informations
    show_group.add_argument('-q', '--quiet', action='store_true', help="simple output")
    show_group.add_argument('-v', '--verbose', action='store_true', help="detailed output")
    
    args = parser.parse_args()
    print args
        
    host = '127.0.0.1'
    
    if args.host:
        try:
            socket.inet_pton(socket.AF_INET, args.host)
            host = args.host
            print host
        
        except socket.error:
            print "invalid IP"
            return
    
    if args.apk and args.test_apk and args.name:
        test_project_name = args.name
        apk_file = args.apk[0]
        apk_test_file = args.test_apk[0]
        
        if not allowed_file_apk(apk_file) or not allowed_file_apk(apk_test_file):
            print "please make sure the files are in .apk format"
            return
        
        if not check_file_exists(apk_file) or not check_file_exists(apk_test_file):
            print "no apk or test_apk file in current folder"
            return
        
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
        
        informations = '{"project":{"project_name": "' + test_project_name + '"},"devices":{"os": [ ' + check(args.os) + ' ],"API Level" : [ ' + check(args.API) + ' ],"deviceType" : [ ' + check(args.deviceType) + ' ],"display" : [ ' + check(args.display) + ' ],"arch" : [ ' + check(args.arch) + ' ]}}'
        
        f = open("testing_project.json", 'w')
        f.write(informations)
        f.close()
        
        # uploads
        os.system('curl -F "test_project_name=' + test_project_name + '" -F "apk_file=@' + apk_file + '" -F "apk_test_file=@' + apk_test_file + '" -X POST http://127.0.0.1:5000/uploads')
        #subprocess.check_output(['curl -F "test_project_name=', test_project_name, '" -F "apk_file=@', apk_file, '" -F "apk_test_file=@', apk_test_file, '" -X POST http://127.0.0.1:5000/uploads'])
        
        # test
        os.system('curl -F "testing_project_json=@testing_project.json" -X POST http://' + host + ':5000/uploads_testing_project')
        os.system('rm testing_project.json')

    else:
        # get sevices status
        os.system('curl http://' + host + ':5000/get_devices_status')

if __name__ == '__main__':
    main()
