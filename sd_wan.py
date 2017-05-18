import json
import requests
from stub import get_dummy_data
from stub import get_dummy_alarm

grant_type = 'client_credentials'
native_portal_link = 'https://portal.ntt.net/'

"""
_login() : Get Accesstoken of SD-WAN by using API-GW Credentials
"""
def _login(client_id, client_secret):
    url = 'https://api.ntt.com/v1/oauth/accesstokens'
    headers = {'Content-Type':'application/json;charset=utf-8', 'Accept':'application/json'}
    payload = {'clientId': client_id, 'clientSecret': client_secret, 'grantType': grant_type}
    
    r = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
    data = json.loads(r.text)
    accesstoken = data['accessToken']

    return accesstoken

"""
get_id_list() : get list of summary ids of SD-WAN under a specified contract
by requesting /sdwan/contracts/<Contract Number>/summary
token : accesstoken from _login()
return : call format_data()
"""
# contract number doesn't need to be multiple ? -> **kwargs?
def get_id_list(is_stub, client_id, client_secret, contractId):
    if(is_stub):
        dummy_data = get_dummy_data()
        return format_data(dummy_data, contractId, 0, is_stub)

    accesstoken = _login(client_id, client_secret)
    url = 'https://api.ntt.com/v1/sdwan/contracts/'+contractId+'/summary'
    token = 'Bearer ' + accesstoken
    headers = {'Accept':'application/json', 'Authorization': token}
    r = requests.get(url, headers=headers, verify=False)
    data = json.loads(r.text)

    return format_data(data, contractId, token, is_stub)

"""
get_alarm() : get alarms data of a specified terminal ID
by requesting /sdwan/contracts/<contractID>/<gatewayID>/<terminalID>
token : accesstoken from _login()
return : Jason data from API
"""
def get_alarms(contractId, gatewayId, terminalId, token, is_stub):
    if(is_stub):
        return get_dummy_alarm()

    url = 'https://api.ntt.com/v1/sdwan/contracts/'+ contractId +'/gateways/'+ gatewayId +'/terminals/'+ terminalId +'/alarms'
    headers = {'Accept':'application/json', 'Authorization': token}
    r = requests.get(url, headers=headers, verify=False)
    data = json.loads(r.text)

    return data

"""
Format result Json data from API to a dump of Json data which CMP can recognise.
Currently, <Terminal ID> and its <alarm status> are formatted and used by CMP to display.
especially, <Alarm Status> and <orderStatus> <overlayVpnContractId> <overlayVpnNo> <overlayVpnConnectedId> <gatewayId>
are used as 'metadata' in CMP view

"""
def format_data(data, contractId, token, is_stub):
    result = []
    try:
        terminals = data['terminals']
        intcs = data['interconnections']
        gateways = data['gateways']
    except:
        pass

    try:
        for terminal in terminals:
            alarm = get_alarms(contractId, terminal['gatewayId'], terminal['terminalId'], token, is_stub)
            terminal_resource ={
                'id': terminal['terminalId'],
                'connections': {},
                'type': 'appliance',
                'base':
                {
                    'native_portal_link': native_portal_link,
                    'name': 'terminal-'+terminal['terminalId'],
                },
                'details':
                {
                    'appliance':
                    {
                     'type_id': 'terminal',
                    }
                },
                'metadata':
                {
                    "provider_specific":
                    {
                        "state": alarm['status'],
                        "installRequestDate": terminal['installRequestDate'],
                        "orderStatus": terminal['orderStatus'],
                    }
                 }
            }
            result.append(terminal_resource)
    except:
        pass

    try:
        for intc in intcs:
            interconnection_resource ={
                'id': intc['interconnectionId'],
                'connections': {},
                'type': 'network',
                'base': 
                {
                    'name': 'interconnection-'+intc['managementName']
                },
                'details': 
                {
                    'network': {}
                },
                'metadata': 
                {
                    "provider_specific": 
                    {
                        "orderStatus": intc['orderStatus'],
                        "overlayVpnContractId": intc['overlayVpnContractId'],
                        "overlayVpnNo": intc['overlayVpnNo'],
                        "overlayVpnConnectedId": intc['overlayVpnConnectedId'],
                        "gatewayId": intc['gatewayId'],
                    }
                }
            }

            result.append(interconnection_resource)
    except:
        pass

    try:
        for gateway in gateways:
            gateway_resource = {
                'id': gateway['gatewayId'],
                'connections': {},
                'type': 'network',
                'base': 
                {
                    'name': 'gateway-'+gateway['gatewayId'],
                },
                'details': 
                {
                    'network': {}
                },
                'metadata': 
                {
                    "provider_specific": 
                    {
                        "orderStatus": gateway['orderStatus'],
                    }
                }
            }

            result.append(gateway_resource)
    except:
        pass

    return result