from crawl_coordinate_AWS import *
import sys
import pickle
import os
package_dir = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    print('start crawling')

    #with open('/home/ubuntu/Cafe_biz_analysis/resource/cafe_all_addr.pickle', 'rb') as f:
    with open(package_dir + '/resource/cafe_all_addr.pickle', 'rb') as f:
        addr_ls = pickle.load(f)
    # num: 1, ..., 7
    num = int(sys.argv[1])
    from_, to_ = 10000*(num-1), 10000*num
    try:
        addr_ls = addr_ls[from_:to_]
    except:
        addr_ls = addr_ls[to_:]

    get_coordinates(addr_ls, num)
