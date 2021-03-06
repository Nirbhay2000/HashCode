from check_sol_v2 import calc_score, read_input, read_output
import sys
print(sys.argv)
V,E,R,C,X,vidsize,endpoints,requests = read_input(sys.argv[1])


# per endpoint the caches sorted by latency (cache_id, latency)
endpoint_cache_latency = { e_id:sorted([[cache[0], endpoint[0][0] - cache[1]] for cache in endpoint[1:]], key = lambda x: -x[1]) for e_id, endpoint in enumerate(endpoints)}
endpoint_cache_latency_dict = { e_id:{cache[0]: endpoint[0][0] - cache[1] for cache in endpoint[1:]} for e_id, endpoint in enumerate(endpoints)}
endpoint_cache ={ e_id:set([cache[0] for cache in endpoint[1:]]) for e_id, endpoint in enumerate(endpoints)}

# Calc metric for all requests
request_with_metric = [] # video_id, endpoint_id, #requests, metric, cache_id
for v_id, e_id, num_req in requests:
    if len(endpoint_cache_latency[e_id]) != 0:
        # get fastest cache
        c_id, latency = endpoint_cache_latency[e_id][0]
        metric = num_req*latency
        request_with_metric.append([v_id, e_id, num_req, metric, c_id])


#sort by metric
request_with_metric = sorted(request_with_metric, key = lambda x: x[3])[::-1]

# Create output structure
cache_size_left = [X for i in range(C)] # size of cache
videos_in_cache = [set() for i in range(C)] # videos in cache

#RESUME
if (len(sys.argv) >2):
    S,caches = read_output(sys.argv[2])
    for cache in caches:
        if len(cache) == 0:
            continue
        c_id = cache[0]
        for v_id in cache[1:]:
            videos_in_cache[c_id].add(v_id)
            cache_size_left[c_id] -= vidsize[v_id]
print("n_metrics:", len(request_with_metric))
k =0
from collections import defaultdict
cached = defaultdict(set)
import random
while len(request_with_metric) > 0:
    k+=1
    if (k %1000 == 0):
        print(k,len(request_with_metric), "left")
    idx = random.randint(0,min(10, len(request_with_metric)-1))
    idx= 0
    v_id, e_id, num_req, metric, c_id = request_with_metric.pop(idx)
    # check if request is still valid
    if v_id in videos_in_cache[c_id]:
        # if the video is already in cache disregard
        continue

    # If video is already in cache benefit gets smaller
    if v_id in cached:
        max_elat = 0
        for ec_id in cached[v_id]:
            if ec_id in endpoint_cache[e_id]:
                max_elat = max(max_elat, endpoint_cache_latency_dict[e_id][ec_id])
        if 0< max_elat*num_req< metric and max_elat >0:
            metric = metric-max_elat*num_req
            # insert at correct position
            for i, target in enumerate(request_with_metric):
                if target[3] < metric:
                    break
            request_with_metric.insert(i, [v_id, e_id, num_req, metric, c_id])
            continue


    if cache_size_left[c_id] < vidsize[v_id]:
        # recalculate metric
        for c_id, latency in endpoint_cache_latency[e_id]:
            if cache_size_left[c_id] >= vidsize[v_id]:
                break
        else:
            continue
        metric = num_req * latency
        # insert at correct position
        for i, target in enumerate(request_with_metric):
            if target[3] < metric:
                break
        request_with_metric.insert(i, [v_id, e_id, num_req, metric, c_id])
        continue
    # add video to cache:
    videos_in_cache[c_id].add(v_id)
    cache_size_left[c_id] -= vidsize[v_id]
    cached[v_id].add(c_id)


caches = [[i]+list(cache) for i, cache in enumerate(videos_in_cache)]
import os

score = calc_score(caches, vidsize, endpoints, requests, V, X)
file_name = os.path.join("output", '.'.join(sys.argv[1].split('.')[:-1])+'_'+str(score)+'.out')
with open(file_name, 'w') as f:
    f.write(str(len(videos_in_cache))+"\n")
    for c_id, videos in enumerate(videos_in_cache):
        f.write(f"{c_id} {' '.join(map(str,videos))}"+"\n")



# for request in sorted list:
    #
