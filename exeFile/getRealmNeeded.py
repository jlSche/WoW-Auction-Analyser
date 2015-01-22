from pandas import *
import os
from collections import Counter


def returnRealm(directory='../sourceDir/0314-0316/'):
    realm_list = []
    for subdirectory in os.listdir(directory):
        for filename in os.listdir(directory + subdirectory):
            realm_list.append(filename)
    return realm_list

def returnAuctionDataRealm(directory='../sourceDir/auctionData/'):
    realm_list = []
    for subdirectory in os.listdir(directory):
        realm_list.append(subdirectory)
    return realm_list



def removeFraction(realm_list):
    return [removeFractionString(realm) for realm in realm_list]

def removeFractionString(realm):
    fraction_string = ['_alliance','_horde']
    for fraction in fraction_string:
        realm = realm.replace(fraction,"")
    return realm

def dropDuplicates(realm_list):
    return list(set(realm_list))

def main():
    
    realm_list1 = returnRealm()
    print '1. original length', len(realm_list1)
    realm_list1 = removeFraction(realm_list1)
    print '1. after remove fraction', len(realm_list1)
    duplicate_dropped_list1 = dropDuplicates(realm_list1)
    print '1. after drop duplicates', len(duplicate_dropped_list1),'\n\n'
    
    realm_list2 = returnAuctionDataRealm()
    print '2. original length', len(realm_list2)
    realm_list2 = removeFraction(realm_list2)
    print '2. after remove fraction', len(realm_list2)
    duplicate_dropped_list2 = dropDuplicates(realm_list2)
    print '2. after drop duplicates', len(duplicate_dropped_list2)
    return list(set(duplicate_dropped_list1)- set(duplicate_dropped_list2)), list(set(duplicate_dropped_list2)-set(duplicate_dropped_list1))



