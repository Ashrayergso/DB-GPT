import numpy as np
import requests
from multiagents.utils.core import read_yaml
import pdb
import json


def prometheus(url, params):
    
    conf = read_yaml('PROMETHEUS', 'config/tool_config.yaml')
    res = requests.get(url=conf.get('api_url') + url, params=params)

    return res.json()


def detect_anomalies(data, significance_level=0.2):

    # assume the workload is steadily running 

    """
    Detects anomalies in the given data using the KS test algorithm.
    
    Args:
        data (numpy.ndarray): 1-D array of data values.
        significance_level (float): Level of significance for the KS test (default: 0.05).
    
    Returns:
        numpy.ndarray: Boolean array indicating anomalies (True) and non-anomalies (False).
    """

    sorted_data = np.sort(data)
    n = len(sorted_data)
    
    # Calculate the expected CDF assuming a normal distribution
    expected_cdf = np.arange(1, n + 1) / n
    
    # Calculate the empirical CDF
    empirical_cdf = np.searchsorted(sorted_data, sorted_data, side='right') / n
    
    # Calculate the maximum absolute difference between the expected and empirical CDFs
    ks_statistic = np.max(np.abs(empirical_cdf - expected_cdf))
    
    # Calculate the critical value based on the significance level and sample size
    critical_value = np.sqrt(-0.1 * np.log(significance_level / 2) / n)

    # pdb.set_trace()

    # Compare the KS statistic with the critical value
    anomalies = np.where(ks_statistic > critical_value, True, False)

    '''
    # Calculate the mean and standard deviation of the data
    anomalies = False

    mean = np.mean(data)
    max_value = np.max(data)

    #print("mean: ", mean)
    #print("max_value: ", max_value)

    if max_value > 2.05 * mean:
        anomalies = True
    
    '''
    
    return anomalies
