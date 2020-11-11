import csv
import random

random.seed(3)
target_name = 'Mobicom TPC-schedule_dummy.csv'

time_zones = {
    'UTC': 0,
    'SST': 8,
    'MDT': -6,
    'MST': -7,
    'EDT': -4,
    'CST': 8,
    'IST': 5.5,
    'PDT': -7,
    'GST': 4,
    'CET': 2,
    'KST': 9,
    'BST': 1,
    'CDT': -5,
    'PKT': 5
}

reviewers = {}
cnt = 0
with open('mobicom21-pcassignments.csv', newline='') as csvfile:
    csvr = csv.reader(csvfile, delimiter=',', quotechar='"')
    for line in csvr:

        cnt += 1
        if cnt == 1:  # skip header
            continue

        email = line[2]
        if not email in reviewers and email != "#pc":
            reviewers[email] = {}

            #heuristic 1
            duration = 3
            first_start = random.randint(7, 22-duration)
            first_start_min1 = random.randint(0, 5)
            first_start_min2 = random.randint(0, 5)
            second_start = random.randint(7, 22-duration)
            second_start_min1 = random.randint(0, 5)
            second_start_min2 = random.randint(0, 5)

            reviewers[email]['first'] = f'not {first_start}:{first_start_min1}0-{first_start + duration}:{first_start_min2}0'
            reviewers[email]['second'] = f'not {second_start}:{second_start_min1}0-{second_start + duration}:{second_start_min2}0'
            reviewers[email]['time_zone'] = random.choice(list(time_zones.keys()))


            #heuristic 2

            # duration = 12
            # first_start = random.randint(7, 22-duration)
            # second_start = random.randint(7, 22-duration)
            # reviewers[email]['first'] = f'{first_start}:00-{first_start + duration}:00'
            # reviewers[email]['second'] = f'{second_start}:00-{second_start + duration}:00'
            # reviewers[email]['time_zone'] = random.choice(list(time_zones.keys()))

f = open(target_name, 'w', newline='',encoding='utf-8')
wr = csv.writer(f)
wr.writerow(['idx','email','X','Y','Z','W','avail_first_day','avail_second_day','time_zone'])
idx = 0

for key in reviewers.keys():
    email = key
    first = reviewers[key]['first']
    second = reviewers[key]['second']
    time_zone = reviewers[key]['time_zone']
    wr.writerow([idx, email, "", "", "", "", first, second, time_zone])
    idx += 1

f.close()

print(reviewers)
