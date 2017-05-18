from sd_wan import get_id_list
from stub import get_dummy_data
from sd_wan import _login

"""
is_stub : Boolean type to conclude whether the scripts are executing as a stub mode or not
client_id : API Credential 1
client_secret : API Credential 2
resources : The execution result of get_id_list() which requests SD-WAN APIs
context.config.get() : a method to get the real data of API credentials which was input by user when nFlex execution
"""
def get_resources(event, context):
    is_stub = context.config.get('is_stub')
    client_id = context.config.get('client_id')
    client_secret = context.config.get('client_secret')
    contract_id = context.config.get('contract_id')
    resources = get_id_list(is_stub, client_id, client_secret, contract_id)
    
    return list(resources)