import os.path
import pickle
import time

import py2neo
from bs4 import BeautifulSoup, Tag
from selenium import webdriver
from tqdm import tqdm


def crawl_manual():
    driver = webdriver.Chrome()
    url = 'http://conf.ruijie.work/pages/viewpage.action?pageId=475040466'
    driver.get(url)
    input('fuck you')
    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")  # 解析网页
    func_list = soup.find_all("span", class_="plugin_pagetree_children_span")
    url_dict_cfg = {}
    url_dict_cmd = {}
    for func in func_list:
        title = func.text.strip()
        if ' ' in title:
            url_type = title.split(' ')[-1]
            url_key = title.split(' ')
            url_key.pop(-1)
            url_key = ' '.join(url_key)
            if url_type == '配置指南':
                url_dict_cfg.__setitem__(url_key, func.contents[1].attrs['href'])
            elif url_type == '命令参考':
                url_dict_cmd.__setitem__(url_key, func.contents[1].attrs['href'])
    # for url_dict in [url_dict_cfg, url_dict_cmd]:
    for url_dict in [url_dict_cfg]:
        for key in url_dict.keys():
            sub_url = 'http://conf.ruijie.work' + url_dict[key]
            driver.get(sub_url)
            html = driver.page_source
            soup = BeautifulSoup(html, "lxml")
            sub_func_list = soup.find_all("div", class_="page view")[0]
            sub_func_list = sub_func_list.find_all("span", class_="plugin_pagetree_children_span")
            url_dict_sub = {}
            for sub_func in sub_func_list:
                title = sub_func.text
                url_dict_sub.__setitem__(title, sub_func.contents[1].attrs['href'])
            url_dict[key] = url_dict_sub
    for key in url_dict_cfg.keys():
        for sub_key in url_dict_cfg[key].keys():
            sub_url = 'http://conf.ruijie.work' + url_dict_cfg[key][sub_key]
            driver.get(sub_url)
            html = driver.page_source
            soup = BeautifulSoup(html, "lxml")
            catalog = soup.find_all("div", class_="office-document")[0]
            catalog = catalog.contents[1]
            if catalog.contents[3].attrs['style'] == "-aw-sdt-tag:''":
                catalog = catalog.contents[3]
            catalog_dict = {}
            for entry in catalog.contents:
                if type(entry) is Tag and len(entry.text.strip()) > 0:
                    title = entry.text.strip().replace('\n', ' ')
                    while '  ' in title:
                        title = title.replace('  ', ' ')
                    if title[0].isdigit():
                        index = title.split(' ')[0]
                        index = index.split('.')
                        title = title.split(' ')
                        title.pop(0)
                        title = ' '.join(title)
                        temp_dict = catalog_dict
                        for sub_index in index:
                            if sub_index not in temp_dict.keys():
                                temp_dict.__setitem__(sub_index, [title, None])
                            else:
                                if temp_dict[sub_index][1] is None:
                                    temp_dict[sub_index][1] = {}
                                temp_dict = temp_dict[sub_index][1]
            url_dict_cfg[key][sub_key] = {'url': url_dict_cfg[key][sub_key], 'catalog': catalog_dict}
    pickle.dump(url_dict_cfg, open('manual.pkl', 'wb'))


def label_manual():
    url_dict_cfg = pickle.load(open('manual.pkl', 'rb'))
    level1_labels = list(url_dict_cfg.keys())
    level2_labels = []
    level3_labels = []
    for level1_label in level1_labels:
        level2_labels_tmp = url_dict_cfg[level1_label]
        level2_labels += list(level2_labels_tmp.keys())
        for leve2_label in list(level2_labels_tmp.keys()):
            level3_labels_tmp = url_dict_cfg[level1_label][leve2_label]['catalog']['1'][1]
            level3_labels_tmp = [level3_labels_tmp[key][0] for key in level3_labels_tmp.keys()]
            level3_labels += level3_labels_tmp
    if os.path.exists('symbols_lv2.pkl'):
        level2_map_dict = pickle.load(open('symbols_lv2.pkl', 'rb'))
    else:
        level2_map_dict = {'sym2cfg': {}, 'cfg2sym': {}}
    for level2_label in level2_labels:
        print('level2_label:', level2_label)
        if level2_label in level2_map_dict['cfg2sym'].keys():
            print('label:', level2_map_dict['cfg2sym'][level2_label])
            cmd = ''
            while cmd not in ['y', 'n']:
                cmd = input('modify label? (y/n)')
            if cmd == 'n':
                continue
            else:
                del level2_map_dict['sym2cfg'][level2_map_dict['cfg2sym'][level2_label]]
                del level2_map_dict['cfg2sym'][level2_label]
        symbol = input('label?:')
        if symbol == '':
            break
        else:
            level2_map_dict['sym2cfg'].__setitem__(symbol, level2_label)
            level2_map_dict['cfg2sym'].__setitem__(level2_label, symbol)
    pickle.dump(level2_map_dict, open('symbols_lv2.pkl', 'wb'))


def write_manual(product_name):
    level2_map_dict = pickle.load(open('symbols_lv2.pkl', 'rb'))
    node_names = list(level2_map_dict['sym2cfg'].keys())
    graph = py2neo.Graph("http://localhost:7474", name='neo4j', password="20291224")
    product_node = py2neo.Node('Entry', name=product_name.lower(), entry_type='pro')
    node_matcher = py2neo.NodeMatcher(graph)
    all_nodes = node_matcher.match("Entry").all()
    for node_name in node_names:
        cmd = ''
        while cmd not in ['y', 'n']:
            cmd = input('Now writing "' + node_name + '" to the graph: (y/n)')
        if cmd == 'y':
            node = py2neo.Node('Entry', name=node_name.lower(), entry_type='tec')
            graph.merge(node, 'Entry', 'name')
            support = py2neo.Relationship(product_node, "contain", node)
            graph.merge(support, 'Entry', 'name')
            link_entries_one_2_all(graph, node, all_nodes)
            time.sleep(0.1)


def link_entries_one_2_all(graph, node, nodes):
    for peer_node in tqdm(nodes):
        if 'content' in peer_node.keys() and peer_node['name'] != node['name']:
            if node['name'] in peer_node['content']:
                contain = py2neo.Relationship(peer_node, "contain", node)
                graph.merge(contain, 'Entry', 'name')


if __name__ == '__main__':
    # crawl_manual()
    # label_manual()
    write_manual(product_name='RG-N8000-R')
    print('Done')
