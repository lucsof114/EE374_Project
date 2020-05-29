
def load_params():
    params = { 
            "beta" : 0.3, 
            "lv" : 0.001, #hash rate of a voter chain
            "lp" : 0.1, #hash rate of a proposer chain
            "lt" : 1, #hash rate of transactions block
            "num_voter_chains" : 1000,
            "prop_delay" : 0.2, # in seconds
            "num_miners": 10000,
            "txPerBlock": 100,
            "communication_cost": 0.001
             }
    return params
