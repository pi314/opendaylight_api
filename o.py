from __future__ import print_function
import httplib
import urllib
import json
import pprint
pp = pprint.PrettyPrinter(indent=2)

__HOST = ''
__COOKIE = ''
debug = False

def http_request (method, resource, param, headers):
    """Wrap http request procedure into one function.

       Special design:
           If ``method'' starts with ``%'', the output will not show.

           If ``method'' follows the format like ``GET test'',
            the function will output ``test'' instead of the full resource name.
    """
    global __HOST
    global debug
    if method[0] == '%':
        quiet = True
        method = method[1:]
    else:
        quiet = False

    if debug: quiet = False

    if not quiet:
        print('+===========================')

    conn = httplib.HTTPConnection(__HOST)

    if ' ' in method:
        tmp = method.split()
        if not quiet:
            print('|', tmp[0] + 'ing', ' '.join(tmp[1:]) )
        conn.request(tmp[0], resource, param, headers)
    else:
        if not quiet:
            print('|', method + 'ing', resource)
        conn.request(method, resource, param, headers)
    response = conn.getresponse()
    response_headers = dict(response.getheaders())
    if not quiet:
        print('|', 'Status code:', response.status, response.reason)
        print('+===========================')
    response_body = response.read()
    conn.close()
    return response.status, response_headers, response_body

def get_flow (node_id=None, flow_name=None):
    global __COOKIE
    if not node_id:
        resource = '/controller/nb/v2/flowprogrammer/default'
    elif not flow_name:
        resource = '/controller/nb/v2/flowprogrammer/default/node/OF/' + node_id
    else:
        resource = '/controller/nb/v2/flowprogrammer/default/node/OF/' + node_id + '/staticFlow/' + flow_name

    param = ''
    headers = {
        'Cookie': __COOKIE,
        }
    status, res_headers, res_body = http_request('%GET', resource, param, headers)
    data = json.loads(res_body)

    if not node_id or not flow_name:
        if flow_name:
            for i in data['flowConfig']:
                if i['name'] == flow_name:
                    return i
        return data['flowConfig']
    else:
        # both node_id and flow_name are given, query result will not be a list
        return data

def add_flow (node_id, flow_name, constrains, actions, priority=500, active=True):
    global __COOKIE
    resource = '/controller/nb/v2/flowprogrammer/default/node/OF/%s/staticFlow/%s' % (
        node_id, flow_name)

    flow_data = get_flow(node_id, flow_name)
    if flow_data == None:
        flow_data = {}
    flow_data.update( (key, value) for (key, value) in constrains.items())

    if 'etherType' not in flow_data:
        # This property is essential or controller responses 406 not acceptable
        flow_data['etherType'] = '0x800'

    # priority is not essential, but I give it a default value 500
    if 'priority' not in flow_data:
        flow_data['priority'] = priority

    # installInHw is not essential, but I give it a default value True
    if 'installInHw' not in flow_data:
        flow_data['installInHw'] = ['false', 'true'][active]

    flow_data['actions'] = actions
    flow_data['name'] = flow_name
    flow_data['node'] = {
            'id': node_id,
            'type': 'OF'
        }
    param = json.dumps(flow_data)

    headers = {
        'Content-Length': len(param),
        'Content-Type': 'application/json', # needed
        'Cookie': __COOKIE,
        }

    status, res_headers, res_body = http_request('PUT', resource, param, headers)
    return status

def toggle_flow (node_id, flow_name):
    global __COOKIE
    resource = '/controller/nb/v2/flowprogrammer/default/node/OF/%s/staticFlow/%s' % (
        node_id, flow_name)
    param = ''
    headers = {
        'Content-Length': len(param),
        'Content-Type': 'application/json', # needed
        'Cookie': __COOKIE,
        }

    status, res_headers, res_body = http_request('POST', resource, param, headers)
    return status

def remove_flow (node_id, flow_name):
    global __COOKIE
    resource = '/controller/nb/v2/flowprogrammer/default/node/OF/%s/staticFlow/%s' % (
        node_id, flow_name)
    param = ''
    headers = {
        'Content-Length': len(param),
        'Content-Type': 'application/json', # needed
        'Cookie': __COOKIE,
        }

    status, res_headers, res_body = http_request('DELETE', resource, param, headers)
    return status

def login (host, username='admin', password='admin'):
    global __HOST
    global __COOKIE
    __HOST = host

    resource = '/'
    param = ''
    headers = dict({})
    status, res_headers, res_body = http_request('%GET', resource, param, headers)
    cookie = res_headers['set-cookie'][:43]

    if status >= 400:
        return False

    resource = '/j_security_check'
    param = urllib.urlencode({
        'j_username': username,
        'j_password': password,
        })
    headers = {
        'Host': __HOST,
        'Connection': 'keep-alive',
        'Content-Length': len(param),
        'Cache-Control': 'max-age=0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Origin': 'http://' + __HOST,
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.76 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded', # needed
        'Referer': 'http://' + __HOST,
        'Accept-Encoding': 'gzip,deflate,sdch',
        'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4',
        'Cookie': cookie,
        }
    status, res_headers, res_body = http_request('%POST', resource, param, headers)

    if status >= 400:
        return False

    resource = '/'
    param = ''
    headers = {
        'Cookie': cookie,
        }
    status, res_headers, res_body = http_request('%GET', resource, param, headers)
    __COOKIE = res_headers['set-cookie'].replace('Path=/', '').replace(' , ', '').replace('; ', '').replace(';', '; ')
    return True

def get_host_list ():
    global __COOKIE
    #resource = '/controller/nb/v2/topology/default'
    resource = '/controller/nb/v2/hosttracker/default/hosts/active'
    headers = {
        'Cookie': __COOKIE,
        }
    param = ''
    status, res_headers, res_body = http_request('%GET host list', resource, param, headers)
    data = json.loads(res_body)
    return [ {
        'mac': i['dataLayerAddress'],
        'ip': i['networkAddress'],
        'switch': i['nodeId'],
        'connector_id': i['nodeConnectorId'],
        }
        for i in data['hostConfig'] ]

def get_connector_list (node_id):
    global __COOKIE
    resource = '/controller/nb/v2/switchmanager/default/node/OF/' + node_id
    headers = {
        'Cookie': __COOKIE,
        }
    param = ''
    status, res_headers, res_body = http_request('%GET connector list of switch ' + node_id,
        resource, param, headers)
    data = json.loads(res_body)
    return {i['nodeconnector']['id']:i['properties']['name']['value'] for i in data['nodeConnectorProperties']}

def get_switch_links ():
    global __COOKIE
    #resource = '/controller/nb/v2/switchmanager/default/node/OF/00:00:00:00:00:00:00:01'
    resource = '/controller/nb/v2/topology/default'
    headers = {
        'Cookie': __COOKIE,
        }
    param = ''
    status, res_headers, res_body = http_request('%GET switch links', resource, param, headers)
    data = json.loads(res_body)
    return [
        (   i['edge']['headNodeConnector']['node']['id'],
            i['edge']['tailNodeConnector']['node']['id'],
            i['properties']['name']['value']) for i in data['edgeProperties']
        ]

def get_topo ():
    global __COOKIE

    host_list = get_host_list()
    topo = {}

    connector_list = {}
    for i in host_list:
        if i['switch'] not in topo:
            topo[ i['switch'] ] = {}

        if i['switch'] not in connector_list:
            connector_list[ i['switch'] ] = get_connector_list(i['switch'])

        if i['ip'] not in topo[ i['switch'] ]:
            topo[ i['switch'] ][ i['ip'] ] = {
                    'connector_id':  i['connector_id'],
                    'mac': i['mac'],
                }
    for sw in topo:
        for host in topo[sw]:
            topo[sw][host]['port'] = connector_list[sw][ topo[sw][host]['connector_id'] ]
            del(topo[sw][host]['connector_id'])

    switch_links = get_switch_links()
    for link in switch_links:
        if link[0] not in topo:
            topo[ link[0] ] = {}
        topo[ link[0] ][ link[1] ] = {}
        topo[ link[0] ][ link[1] ]['port'] = link[2]

    return topo

def test ():
    global __COOKIE
    #resource = '/controller/nb/v2/switchmanager/default/node/OF/00:00:00:00:00:00:00:01'
    #resource = '/controller/nb/v2/topology/default'
    resource = '/controller/nb/v2/switchmanager/default/nodes'
    headers = {
        'Cookie': __COOKIE,
        }
    param = ''
    status, res_headers, res_body = http_request('GET test', resource, param, headers)
    data = json.loads(res_body)
    for i in data['nodeProperties']:
        #pp.pprint(i)
        print(i['node']['id'], i['properties']['macAddress']['value'])
        print('')

def main ():
    global pp
    print('Login status:', login('192.168.179.129:8080'))
    print('Topology:')
    pp.pprint( get_topo() )

    print('Static flows:')
    pp.pprint(get_flow())

    node_id = '00:00:00:00:00:00:00:01'
    flow_name = 'newFlow'
    constrains = {  
                    u'etherType': u'0x800',
                    u'protocol': u'TCP'}
    actions = ["CONTROLLER"]

    #add_flow(node_id, flow_name, constrains, actions, 600, True)

    constrains = {'protocol': 'UDP'}
    actions = ["DROP"]
    #add_flow(node_id, flow_name, constrains, actions, 700, False)
    #toggle_flow(node_id, flow_name)
    remove_flow(node_id, flow_name)
    #test()

if __name__ == '__main__':
    main()
