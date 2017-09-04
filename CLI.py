#!/usr/bin/env python
import argparse
import os
import subprocess
import json

ALLOWED_EXTENSIONS_APK = set(['apk'])

# check if the apk_file and apk_test_file are in format
def allowed_file_apk(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_APK

def check_file_exists(path_filename):
    if os.path.isfile(path_filename):
        return False
    return True

def create_json(data, object, key, value):
    if value:
        data[object].update({key: value})
    return data

def main():
    parser = argparse.ArgumentParser()
    
    # internet address
    parser.add_argument('--address', default='127.0.0.1:5000', type=str, help="Host IP or web address")
    
    # test_project_name
    parser.add_argument('-project', type=str, help="Test project name")
    
    # apk_file / apke_test_file
    parser.add_argument('-apk', type=str, help="Application APK")
    parser.add_argument('-test-apk', type=str, help="Test application APK")
    
    # conditions
    parser.add_argument('-os', nargs='+', help="Android release")
    parser.add_argument('-api', nargs='+', help="API Level")
    parser.add_argument('-devicetype', nargs='+', help="Board Specifications")
    parser.add_argument('-display', nargs='+', help="Density")
    parser.add_argument('-arch', nargs='+', help="CPU")
    
    # optional arguments
    parser.add_argument('-status', action='store_true', help="Show devices status")
    
    show_group = parser.add_mutually_exclusive_group()
    
    # informations
    show_group.add_argument('-v', '--verbose', action='store_true', help="detailed output")
    
    args = parser.parse_args()
    
    if args.project:
        if args.apk and args.test_apk:
            if not allowed_file_apk(args.apk) or not allowed_file_apk(args.test_apk):
                print "please make sure the files are in .apk format"
                return
            
            if check_file_exists(args.apk) or check_file_exists(args.test_apk):
                print "no apk or test_apk file in current folder"
                return
            
            # uploads
            subprocess.check_call(['curl', '-F', 'test_project_name=' + args.project, '-F', 'apk_file=@' + args.apk, '-F', 'apk_test_file=@' + args.test_apk, '-X', 'POST', args.address + '/uploads'])
    
        if args.apk is None and args.test_apk is None:
            args.apk = ''
            args.test_apk = ''

        data = {}
        data['project'] = {}
        data['devices'] = {}
        
        data = create_json(data, 'project', 'project_name', args.project)
        data = create_json(data, 'devices', 'os', args.os)
        data = create_json(data, 'devices', 'API Level', args.api)
        data = create_json(data, 'devices', 'deviceType', args.devicetype)
        data = create_json(data, 'devices', 'display', args.display)
        data = create_json(data, 'devices', 'arch', args.arch)

        # create testing project json
        with open("testing_project.json", 'w') as outfile:
            json.dump(data, outfile, indent=4)

        conditions = ""
        full_conditions = ""

        for key in data['devices']:
            conditions += str(data['devices'][key])
            full_conditions += key + ": " + str(data['devices'][key]) + "\n"
        
        # show detailed informations
        if args.verbose:
            print 'The test project name is "' + args.project + '"'
            print 'APK files are "' + args.apk + '", "' + args.test_apk + '"'
            print full_conditions
        
        # show defualt
        else:
            print "Project: " + args.project
            print "APK: " + args.apk, args.test_apk
            print "Requirements: " + conditions

        # test
        subprocess.call(['curl', '-F', 'testing_project_json=@testing_project.json', '-X', 'POST', args.address + '/uploads_testing_project'])

        # remove testing project json
        subprocess.call(['rm', 'testing_project.json'])
    
    elif args.status:
        # get sevices status
        subprocess.call(['curl', args.address + '/get_devices_status'])
    
    else:
        # home
        subprocess.call(['curl', args.address])

if __name__ == '__main__':
    main()
