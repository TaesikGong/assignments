import csv
import json
import random



time_zones = {
    'SST': 8,
    'MDT': -6,
    'EDT': -4,
    'CST': 8,
    'IST': 5.5,
    'PDT': -7,
    'GST': 4,
    'CET': 2,
    'KST': 9,
    'BST': 1,
    'CDT': -5
    }


def local_to_global(time, time_zone):
    if isinstance(time, list):
        return list(map(lambda x: x + 9 - time_zones[time_zone], time))
    else:
        return time + 9 - time_zones[time_zone]
    # return time


def global_to_local(time, time_zone):
    if isinstance(time, list):
        return list(map(lambda x: (x + 9 - time_zones[time_zone]) % 24, time))
    else:
        glob = (time - 9 + time_zones[time_zone]) % 24
        #glob = glob if glob < 24 else glob - 24
    return glob
    # glob = time



detailed_debug = False
debug_id = '591aaa'

#   8---------------16------------24             8------------16-----------24
#                   8-------------16-------------24
#                                  8-------------16-----------24


# Acceptable meeting hours in global time -- these are all hours
sched_time = [local_to_global(7, 'CST'), local_to_global(23, 'BST')]

# Acceptable working hours
default_time = [7, 22]



def similar(p1, p2):
    return len(list(set(p1['reviewers']) & set(p2['reviewers'])))
    #return len(intersection(p1['reviewers'], p2['reviewers']))






def get_paper_hours(times):
    hours = []
    for time in times:
        h = range(round(time[0]), round(time[1]))
        h = list(map(lambda x: x%24, h))
        hours.extend(h)
    return hours


def get_hour_index(hour):
    if hour >= sched_time[0] and hour < sched_time[1]:
        return hour - sched_time[0]
    elif hour >= sched_time[0] + 24 and hour < sched_time[1] + 24:
        return hour - sched_time[0] - 24
    elif hour + 24 >= sched_time[0] and hour + 24 < sched_time[1]:
        return hour + 24 - sched_time[0]
    else:
        return -1

def get_index_hours(index):
    assert(index >= 0 and index < sched_time[1])
    return [index + sched_time[0], index + sched_time[0] + 1]





def time_parse(time, time_zone):
    times = []
    cnt = 0
    notimes = len(time.split(","))
    for interval in time.split(","):
        neg = False
        cnt = cnt + 1
        if interval[0:3] == "not":
            neg = True
            interval = interval[3:]
        time = []
        if interval.strip():
            for hour in interval.strip().split("-"):
                if ":" in hour:
                    a = hour.split(":")
                    time.append(float(a[0]) + float(a[1]) / 60)
                else:
                    time.append(float(hour))
        if len(time) == 0:
            assert(cnt == 1)
            if not neg:
                time = list(map(lambda x : local_to_global(x, time_zone), default_time))
            times.append(time)
        else:
            assert(len(time) == 2)
            if neg:
                assert(cnt == 1 and notimes == 1)
                if time[0] > default_time[0]:
                    times.append([local_to_global(default_time[0], time_zone), local_to_global(time[0], time_zone)])
                if time[1] < default_time[1]:
                    times.append([local_to_global(time[1], time_zone), local_to_global(default_time[1], time_zone)])
            else:
                times.append(list(map(lambda x : local_to_global(x, time_zone), time)))

    return times


def check_empty(time):
    return [] if time[0] == time[1] else time

def intersect_time(time1, time2):
    if not time1 or not time2:
        return []
    if time1[1] < time2[0] or time1[0] > time2[1]: 
        return []
    if time1[0] <= time2[0] and time1[1] <= time2[1]:
        return check_empty([time2[0], time1[1]])
    elif time2[0] <= time1[0] and time2[1] <= time1[1]:
        return check_empty([time1[0], time2[1]])
    elif time2[0] <= time1[0] and time2[1] >= time1[1]:
        return check_empty(time1)
    else:
        # if not (time1[0] <= time2[0] and time1[1] >= time2[1]):
        #     print("Assert: {} {}".format(time1, time2))
        assert(time1[0] < time2[0] and time1[1] > time2[1])
        return check_empty(time2)



def intersect_times(times1, times2):
    result = []
    for t1 in times1:
        inc_t1 = list(map(lambda x : x+24, t1))
        for t2 in times2:
            inc_t2 = list(map(lambda x : x+24, t2))

            inter = intersect_time(t1, t2)
            if detailed_debug:
                print(f"      II1: {t1} cup {t2} = {inter}")

            if inter:
                result.append(inter)
            
            inter = intersect_time(inc_t1, t2)
            if detailed_debug:
                print(f"      II2: {inc_t1} cup {t2} = {inter}")
            if inter:
                result.append(inter)

            inter = intersect_time(t1, inc_t2)
            if detailed_debug:
                print(f"      II3: {t1} cup {inc_t2} = {inter}")
            if inter:
                result.append(inter)

    return result





def _find_best_times(revs):
    result = [[], []]
    for d in range(0,2):
        times = [sched_time]
        if detailed_debug:
            print(f"Day {d}:")
        for r in revs:
            old_times = times.copy()
            times = intersect_times(times, reviewers[r]["times"][d])
            if detailed_debug:
                print(f"   I{d}: {old_times} cup {reviewers[r]['times'][d]} = {times}")
        result[d] = times
    return result


def find_best_times(revs):
    if detailed_debug:
        print("\n")
    result = _find_best_times(revs)
    if detailed_debug:
        print(f"F0: {result}\n")
    if not result[0] and not result[1]:
        for r in revs:
            new_rev = revs.copy()
            new_rev.remove(r)
            result = _find_best_times(new_rev)
            if detailed_debug:
                print(f"F1: {result}\n")
            if result[0] or result[1]:
                return result, -1
    if not result[0] and not result[1]:
        for r in revs:
            for r1 in revs:
                if not r == r1:
                    new_rev = revs.copy()
                    new_rev.remove(r)
                    new_rev.remove(r1)
                    result = _find_best_times(new_rev)
                    if detailed_debug:
                        print(f"F2: {result}\n")
                    if result[0] or result[1]:
                        return result, -2
    return result, 0






papers = {}
reviewers = {}


cnt = 0

with open('Mobicom TPC-schedule.csv', newline='') as csvfile:
    csvr = csv.reader(csvfile, delimiter=',', quotechar='"')
    for line in csvr:
        cnt = cnt + 1
        if cnt > 1:
            email = line[1].strip()
            time_zone = line[8]
            day_1 = time_parse(line[6], time_zone)
            day_2 = time_parse(line[7], time_zone)

            reviewers[email] = {
                "times" : [day_1, day_2],
                "time_zone" : time_zone,
                "papers" : [],
                "slots" : []
            }



cnt = 0

with open('mobicom20-pcassignments.csv', newline='') as csvfile:
    csvr = csv.reader(csvfile, delimiter=',', quotechar='"')
    for line in csvr:
        if line[1] == 'clearreview':
            cnt = cnt + 1
            papers[line[0]] = {
                'title' : line[4],
                'reviewers' : []
            }
        elif line[1] == 'primary':
            rev = line[2].strip()
            papers[line[0]]['reviewers'].append(rev)
            if rev not in reviewers.keys():
                assert(False)
                #reviewers[rev] = []
            reviewers[rev]["papers"].append(line[0].strip())
        #else:
            #print(line)


# print(json.dumps(papers, indent=2))
# print(json.dumps(reviewers, indent=2))

# Number of papers per reviewer
# for r,v in reviewers.items():
#     print("{}: {}".format(r, len(v["papers"])))

# Reviewer's availability
# for r,v in reviewers.items():
#     print("{}: {} {}".format(r, v["times"][0], v["times"][1]))




for k,v in papers.items():
    v["times"], v["rev"] = find_best_times(v["reviewers"])
    if (k == debug_id):
        print(f"DEBUG_BEST_TIMES: {k} {v['times']} {v['rev']}")
        for r in v["reviewers"]:
            print("  {}: {} {}".format(r, reviewers[r]["times"][0], reviewers[r]["times"][1]))



# Find schedule
sched = [
    [[] for i in range(sched_time[1] - sched_time[0])],
    [[] for i in range(sched_time[1] - sched_time[0])]
]


# DEBUG - easier debugging
random.seed(10)


cnt = 0
for k,v in papers.items():
    cnt = cnt + 1
    day = 0

    if v["times"][0] and v["times"][1]:
        day = random.randint(0, 1)
    elif v["times"][0]:
        day = 0
    elif v["times"][1]:
        day = 1
    else:
        assert(False)

    # DEBUG
    # if k == debug_id:
    #     day = 1


    hour = round(v["times"][day][0][0])
    index = get_hour_index(hour)
    if index < 0:
        print(f"{k} {v['times'][day][0]} {hour} {index} {v}")
    assert(index >= 0)
    sched[day][index].append(k)

    # DEBUG
    if k == debug_id:
        print(f"DEBUG_INITIAL: id={k} day={day} int_start={v['times'][day][0][0]} hour={hour} hour_index={index}")



iter = 0
for iter in range(0,10):
    iday = 0
    for day in sched:
        ihour = 0
        for hour in day:
            for id in hour:

                # DEBUG
                pr = (id == debug_id)

                paper = papers[id]
                moved = False
                for canditate_day in range(0,2):
                    paper_hours = get_paper_hours(paper["times"][canditate_day])
                    if pr:
                        print(f"{id}: day/hour={iday}/{ihour} {canditate_day}/{paper_hours} - {paper['times'][canditate_day]}")
                        print(f"    {hour}")
                    for new_hour in paper_hours:
                        new_hour_idx = get_hour_index(new_hour)
                        if pr:
                            print(f"DEBUG_CANDIDATE_MOVE: id={id} old_day={iday} old_hour={ihour} new_day={canditate_day} new_hour={new_hour}/{new_hour_idx} "
                                   "old_len={} new_len={}".format(len(hour), len(sched[canditate_day][new_hour_idx])))
                        if (new_hour_idx < 0):
                            continue
                        if len(sched[canditate_day][new_hour_idx]) < len(hour):
                            if pr:
                                print(f"*** DEBUG_MOVE: id={id} old_day={iday} old_hour={ihour} new_day={canditate_day} new_hour={new_hour}/{new_hour_idx} "
                                      f"{hour}, {sched[canditate_day][new_hour_idx]}")
                            sched[canditate_day][new_hour_idx].append(id)
                            hour.remove(id)
                            if pr:
                                print(f"{hour}, {sched[canditate_day][new_hour_idx]}")
                            moved = True
                            break
                    if moved:
                        break
            ihour = ihour + 1
        iday = iday + 1



#print(json.dumps(sched, indent=2))

# Copy assignment to papers and reviewers
for ihour in range(0, len(sched[0])):
    iday = 0
    for day in sched:
        hour = day[ihour]
        interv = get_index_hours(ihour)
        for id in hour:
            papers[id]["slot"] = interv
            papers[id]["day"] = iday
            inter = intersect_times([interv], papers[id]["times"][iday])
            #print(f"{id}: {iday}/{ihour}/{interv} {papers[id]['times'][iday]} {inter}")
            assert(len(inter[0]) > 0)

            for r in papers[id]["reviewers"]:
                matches = [x for x in reviewers[r]["slots"] \
                    if x["day"] == iday and x["slot"][0] == interv[0] and x["slot"][1] == interv[1]]
                if not matches:
                    reviewers[r]["slots"].append(
                        {
                            "day" : iday,
                            "slot" : interv
                        }
                    )

        iday = iday + 1




feas = 0
feas_1 = 0
feas_2 = 0
infeas = 0

for k,v in papers.items():
    if v["times"][0] or v["times"][1]:
        if v["rev"] == 0:
            feas = feas + 1
        elif v["rev"] == -1:
            feas_1 = feas_1 + 1
        elif v["rev"] == -2:
            feas_2 = feas_2 + 1
        else:
            assert(False)
    else:
        infeas = infeas + 1
    #print("{} ({}): {} {}".format(k, v["rev"], v["times"][0], v["times"][1]))




print(f"TPC time:")
print("  HKG: {:2}:00-{:2}:00 ".format(global_to_local(sched_time[0], 'CST'), global_to_local(sched_time[1], 'CST')))
print("  LON: {:2}:00-{:2}:00 ".format(global_to_local(sched_time[0], 'BST'), global_to_local(sched_time[1], 'BST')))
print("")
print(f"Default working hours: {default_time}\n")


total = feas+feas_1+feas_2+infeas
print(f"\nSummary: ")
print(f"  Total papers      = {total}")
print(f"  All reviewers     = {feas}")
print(f"  All reviewers - 1 = {feas_1}")
print(f"  All reviewers - 2 = {feas_2}")
print(f"  Infeasible        = {infeas}")
print("\n")


# for k,v in papers.items():
#     if v["rev"] < 0:
#         print("**** {} ({}): ".format(k, v["rev"]))
#     else:
#         print("{}: ".format(k))
#     for r in v["reviewers"]:
#         tz = reviewers[r]["time_zone"]
#         t0 = list(map(lambda x : global_to_local(x, tz), v["times"][0][0])) if len(v["times"][0]) > 0 else []
#         t1 = list(map(lambda x : global_to_local(x, tz), v["times"][1][0])) if len(v["times"][1]) > 0 else []
#         print("  {}: {} {}".format(r, t0, t1))



total = 0

print_detail = False
#print_detail = True

print("  HGK     LON                     HGK     LON        ")
print("--------------------            ---------------------")

first_half = [0, 0]
second_half = [0, 0]

for ihour in range(0, len(sched[0])):
    iday = 0
    for day in sched:
        hour = day[ihour]
        interv = get_index_hours(ihour)
        if print_detail:
            print(f"{iday} ", end='')
        # print(f"{ihour:2} [{interv[0]:2} {interv[1]:2}] ", end='')
        print("[{:2} {:2}] ".format(global_to_local(interv[0], 'CST'), global_to_local(interv[1], 'CST')), end='')
        print("[{:2} {:2}] ".format(global_to_local(interv[0], 'BST'), global_to_local(interv[1], 'BST')), end='')
        print(f": {len(hour):2} \t\t", end='')
        if print_detail:
            print("")

        if ihour > len(sched[0])/2:
            second_half[iday] = second_half[iday] + len(hour)
        else:
            first_half[iday] = first_half[iday] + len(hour)

        if print_detail:
            for id in hour:
                print(f"{id}: [{interv[0]}-{interv[1]}] {papers[id]['times']}")
        total = total + len(hour)
        iday = iday + 1
    print("")

#print("Total: {}".format(total))

print("")
print(f"First half:  {first_half[0]}                 First half:  {first_half[1]}")
print(f"Second half: {second_half[0]}                 Second half: {second_half[1]}")






print("\n\n\n\n")
print("Paper assignment per slot\n")

iday = 0
for day in sched:
    if iday == 0:
        print("\n     MON")
    else:
        print("\n     TUE")
    print("  HGK     LON       ")
    print("--------------------")
    for ihour in range(0, len(sched[0])):
        hour = day[ihour]
        interv = get_index_hours(ihour)
        print("[{:2} {:2}] ".format(global_to_local(interv[0], 'CST'), global_to_local(interv[1], 'CST')), end='')
        print("[{:2} {:2}] ".format(global_to_local(interv[0], 'BST'), global_to_local(interv[1], 'BST')), end='')

        for id in hour:
            print(f"#{id} ", end="")
        print("")

    iday = iday + 1


#print(json.dumps(papers, indent=2))
#print(json.dumps(reviewers, indent=2))


print("\n\n")
print("Time slots per reviewer in local time zones:")
print("--------------------------------------------")
for r,v in reviewers.items():
    print(f"{r}, Mon: ", end="")
    for s in v["slots"]:
        if s["day"] == 0:
            print("[{:2} {:2}] ".format(
                global_to_local(s["slot"][0], v["time_zone"]), 
                global_to_local(s["slot"][1], v["time_zone"])), end='')
    print(f", Tue: ", end="")
    for s in v["slots"]:
        if s["day"] == 1:
            print("[{:2} {:2}] ".format(
                global_to_local(s["slot"][0], v["time_zone"]), 
                global_to_local(s["slot"][1], v["time_zone"])), end='')
    print("")
    



# # Reviewer's availability
# for r,v in reviewers.items():
#     assign = v["papers"]
#     time_zone = v["time_zone"]
#     print(f"{r} ({time_zone}): ", end="")
#     for id in assign:
#         paper = papers[id]
#         print("{} {}".format(r, v["times"][0], v["times"][1]))

