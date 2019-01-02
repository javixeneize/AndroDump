import subprocess
import sys
import re
import xmltodict

APKPATH = 'apk/base.apk'
MANIFESTPATH = 'manifest/'
ANDROIDMANIFEST = 'AndroidManifest.xml'


class androDump():
    def __init__(self):
        self.packageName = ''
        self.path = ''
        self.usespermissions = []
        self.permissions = []
        self.activities = []
        self.services = []
        self.providers = []
        self.debuggable = False
        self.backup = False

    def getPackageName(self, packageFilter):
        getPackageName = ['adb', 'shell', 'pm', 'list', 'packages', '-f', '{}'.format(packageFilter)]
        try:
            result = subprocess.check_output(getPackageName).decode('utf-8').strip().split('\n')
            if result[0] == "":
                print("There is no package matching with the filter: {}".format(packageFilter))
                sys.exit(1)
            else:
                if len(result) > 1:
                    print("There are several results that match your search. Retrieving the first match...")
                self.packageName = result[0].split('=')[1]
                print("Package name: {}".format(self.packageName))
        except subprocess.CalledProcessError:
            pass

    def getPackageInfo(self):
        if self.packageName != '':
            getPackageInfo = ['adb', 'shell', 'dumpsys', 'package', '{}'.format(self.packageName)]
            result = subprocess.check_output(getPackageInfo).decode('utf-8')
            self.path = re.findall("path: (.*)", result)[0]

    def dumpFiles(self):
        files = subprocess.run(['adb', 'pull', '/data/data/{}'.format(self.packageName), 'dump'])
        print(files)

    def dumpAPK(self):
        if self.path != '':
            subprocess.run(['adb', 'pull', self.path, APKPATH])
            subprocess.run(['apktool', 'd', APKPATH, '-o', MANIFESTPATH, '-f'])
            print("APK file downloaded")

    def __getUsesPermissions(self, data):
        if (type(data) == list):
            for usespermission in data:
                for key, value in usespermission.items():
                    self.usespermissions.append(value)
        else:
            for key, value in usespermission.items():
                self.usespermissions.append(value)

    def __getPermissions(self, data):
        if (type(data) == list):

            for permission in data:
                self.permissions.append(permission['@android:name'])
        else:
            self.permissions.append(permission['@android:name'])

    def __getApplicationData(self, data):
        if '@android:allowBackup' in data and data['@android:allowBackup'] == "true":
            self.backup = True
        if '@android:debuggable' in data and data['@android:debuggable'] == "true":
            self.debuggable = True
        if 'activity' in data:
            self.__getActivities(data['activity'])
        if 'service' in data:
            self.__getServices(data['service'])
        if 'provider' in data:
            self.__getContentProviders(data['provider'])

    def _getActivityInfo(self, activity):
        try:
            if (activity['@android:exported'] == 'true'):
                self.activities.append(activity['@android:name'])
        except KeyError:
            if ('intent-filter' in activity):
                self.activities.append(activity['@android:name'])

    def __getActivities(self, activities):
        if (type(activities) == list):
            for activity in activities:
                self._getActivityInfo(activity)
        else:
            self._getActivityInfo(activities)

    def __getServicesInfo(self, service):
        try:
            if (service['@android:exported'] == 'true'):
                self.services.append(service['@android:name'])
        except KeyError:
            if ('intent-filter' in service):
                self.services.append(service['@android:name'])

    def __getServices(self, services):
        if (type(services) == list):

            for service in services:
                self.__getServicesInfo(service)
        else:
            self.__getServicesInfo(services)

    def __getContentProviderInfo(self, provider):
        try:
            if (provider['@android:exported'] == 'true'):
                self.providers.append(provider['@android:name'])
        except KeyError:
            if ('intent-filter' in provider):
                self.providers.append(provider['@android:name'])

    def __getContentProviders(self, providers):
        if (type(providers) == list):
            for provider in providers:
                self.__getContentProviderInfo(provider)
        else:
            self.__getContentProviderInfo(providers)

    def getDataFromManifest(self):
        with open(MANIFESTPATH + ANDROIDMANIFEST) as f:
            data = f.read()
        f.close()
        dataparsed = xmltodict.parse(data)['manifest']
        try:
            self.__getUsesPermissions(dataparsed['uses-permission'])
        except KeyError:
            pass
        try:
            self.__getPermissions(dataparsed['permission'])
        except KeyError:
            pass
        try:
            self.__getApplicationData(dataparsed['application'])
        except KeyError:
            pass

    def clear(self):
        self.__init__()


if __name__ == "__main__":
    a = androDump()
    a.getPackageName("test")
    a.getPackageInfo()
    a.dumpAPK()
    a.dumpFiles()
    a.getDataFromManifest()
    #
    # print(a.packageName)
    # print(a.usespermissions)
    # print(a.permissions)
    # print(a.activities)
    # print(a.services)
    # print(a.providers)
    # print(a.debuggable)
    # print(a.backup)
