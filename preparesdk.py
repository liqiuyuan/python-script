#!/usr/bin/env python
# -*- coding: utf8 -*-
import os
import zipfile
import shutil

baseDir = os.getcwd()
packageDir = baseDir + '/sdkpackage'
zipSdkDir = baseDir + '/unzip'


with open('build.conf') as f:
    nowBuildVersion = ''.join(f.read().split('"')[1].split(':'))
print(nowBuildVersion)

for dirpath, dirnames, filenames in os.walk(packageDir):
    for filename in filenames:
        filepath = os.path.join(dirpath, filename)
        suffixName = os.path.splitext(filepath)[1]
        if suffixName == '.zip':
            if not os.path.isdir(zipSdkDir):
                os.mkdir(zipSdkDir)
            zipf = zipfile.ZipFile(filepath, 'r')
            zipf.extractall(zipSdkDir)

with open('%s/build/build_source.txt' % zipSdkDir) as f:
    buildFile = f.readlines()[0]
    buildFile = "".join(buildFile)
    buildVersion = buildFile.strip('\r\n').split('\\')[-4]

if nowBuildVersion == buildVersion:
    print('The right sdk build version')
else:
    print('The wrong sdk builed version, Please chechk!')
    shutil.rmtree(zipSdkDir)
