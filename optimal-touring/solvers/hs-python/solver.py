import sys
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans


def OptimalTouring():
	df_site = pd.DataFrame(0, index=np.arange(200), columns=["site", "x",  "y" ,"desiredtime", "value"])
	df_site_info = pd.DataFrame(0, index=np.arange(2000), columns=["site", "day",  "begin" ,"close"])

	state = 0
	count = 0
	other_count = 0
	for line in sys.stdin:
	    ln = line.split()
	    if not ln:
	      continue
	    if state == 0:
	      # site avenue street desiredtime value
	      state = 1
	    elif state == 1:
	      if ln[0][0].isdigit():
	         df_site.iloc[count] ["site"]= int(ln[0])
	         df_site.iloc[count] ["x"]= int(ln[1])
	         df_site.iloc[count] ["y"]= int(ln[2])
	         df_site.iloc[count] ["desiredtime"]= int(ln[3])
	         df_site.iloc[count] ["value"]= float(ln[4])
	         count = count + 1 
	      else:
	        # site day beginhour endhour
	        state = 2
	    elif state == 2:
	        df_site_info.iloc[other_count] ["site"]= int(ln[0])
	        df_site_info.iloc[other_count] ["day"]= int(ln[1])
	        df_site_info.iloc[other_count] ["begin"]= int(ln[2])
	        df_site_info.iloc[other_count] ["close"]= int(ln[3])
	        other_count = other_count  +  1 
	max_days = max(df_site_info["day"])
	max_site = max(df_site["site"])

	df_site = df_site.iloc[:max_site]
	df_site_info = df_site_info.iloc[:max_site*max_days]

	kmeans = KMeans(n_clusters= max_days)
	df_forcluster = df_site[['x', 'y']]
	kmeans.fit(df_forcluster)
	df_site['cluster'] = kmeans.predict(df_forcluster).tolist()
	df_site['value/min'] = df_site['value']/df_site['desiredtime']
	df_site['cluster'] = df_site['cluster'] + 1

	schedule_matrix = []
	val = 0
	for day in range(1, max_days + 1):
	    current_schedule = []
	    df_req = df_site[df_site['cluster'] == day].sort_values(['value'], ascending= False).reset_index()
	    next_site = df_req.iloc[0]
	    current_time = int(df_site_info[(df_site_info['site']== int(next_site['site'])) & (df_site_info['day'] == day) ]['begin']) *60
	    time_to_reach = 0
	    required_time = next_site['desiredtime']
	    closing_time = int(df_site_info[(df_site_info['site']== int(next_site['site'])) & (df_site_info['day'] == day) ]['close']) *60

	                                    
	    for j in range(len(df_req)-1):
	        if current_time + time_to_reach + required_time < closing_time:
	             current_site = next_site
	             current_schedule.append(int(current_site['site']))
	             val += current_site['value']
	             current_time = current_time + required_time
	             next_site = df_req.iloc[j+1]
	             time_to_reach = abs(next_site['x']- current_site['x']) + abs(next_site['y']- current_site['y'])
	             required_time = next_site['desiredtime']
	             closing_time = int(df_site_info[(df_site_info['site']== int(next_site['site'])) & (df_site_info['day'] == day) ]['close']) *60 
	        else:
	            next_site = df_req.iloc[j+1]
	            time_to_reach = abs(next_site['x']- current_site['x']) + abs(next_site['y']- current_site['y'])
	            required_time = next_site['desiredtime']
	            closing_time = int(df_site_info[(df_site_info['site']== int(next_site['site'])) & (df_site_info['day'] == day) ]['close']) *60 
	       
	            
	    schedule_matrix.append(current_schedule)
	print(val)
	return schedule_matrix

def main():
  schedule_matrix= OptimalTouring()
  # optimal_touring.print_data()
  for visit_on_day in schedule_matrix:
    print(*visit_on_day)
if __name__ == '__main__':
  main()
