from json import loads

""" 
Creation of a program that takes in corrupted JSON file data, parses it for errors, provides corrections and 
    builds a correct mapping for a bus system.
Name: Joel Strong
GitHub: jdstrongpdx
Date: 6/17/2023
Description: Hyperskill Easy Rider Bus Company
"""
bus_dict = {}
bus_data = {}
not_on_demand = ()


def main():
    """Main function for running the program"""
    user_input = input()
    raw_data = loads(user_input)
    parse_json(raw_data)
    parse_routes()
    parse_stops()
    on_demand()


def parse_json(raw_data):
    """Read raw_data input from JSON data, check each field for errors and sum the number of errors in the file"""
    error_count = {'bus_id': 0, 'stop_name': 0, 'stop_type': 0, 'stop_id': 0, 'a_time': 0}
    bus_id, stop_id, stop_name, next_stop, stop_type, a_time = None, None, None, None, None, None
    for count, item in enumerate(raw_data):

        field = 'bus_id'
        try:
            if type(item[field]) != int:
                raise TypeError
            bus_id = item[field]
        except (TypeError, ValueError):
            error_count[field] += 1
        except KeyError:
            pass

        field = 'stop_id'
        try:
            if type(item[field]) != int:
                raise TypeError
            stop_id = item[field]
        except (TypeError, KeyError):
            error_count[field] += 1

        field = 'stop_name'
        suffix = ['Road', 'Avenue', 'Boulevard', 'Street']
        try:
            if type(item[field]) != str:
                raise TypeError
            if item[field] == "":
                raise ValueError
            stop_list = item[field].split(" ")
            if len(stop_list) < 2:
                raise ValueError
            elif 90 < ord(stop_list[0][0]) or ord(stop_list[0][0]) < 65:
                raise ValueError
            if stop_list[-1] not in suffix:
                raise ValueError
            stop_name = item[field]
        except (TypeError, KeyError, ValueError):
            error_count[field] += 1

        field = 'next_stop'
        try:
            if type(item[field]) != int:
                raise TypeError
            next_stop = item[field]
        except (TypeError, KeyError):
            error_count[field] += 1

        field = 'stop_type'
        character = ['S', 'O', 'F', '']
        try:
            if type(item[field]) != str:
                raise TypeError
            if item[field] not in character:
                raise ValueError
            stop_type = item[field]
        except (TypeError, KeyError, ValueError):
            error_count[field] += 1

        field = 'a_time'
        try:
            if type(item[field]) != str:
                raise TypeError
            if item[field] == "":
                raise ValueError
            item[field] = item[field].split(":")
            if len(item[field]) != 2 or len(item[field][0]) != 2 or len(item[field][1]) != 2:
                raise ValueError
            hour = int(item[field][0])
            minute = int(item[field][1])
            if 24 < hour or hour < 0:
                raise ValueError
            if 60 < minute or minute < 0:
                raise ValueError
            a_time = tuple(item[field])
        except (TypeError, KeyError, ValueError):
            error_count[field] += 1

        bus_data[count] = {'bus_id': bus_id, 'stop_id': stop_id, 'stop_name': stop_name, 'next_stop': next_stop,
                           'stop_type': stop_type, 'a_time': a_time}

        if bus_id not in bus_dict:
            bus_dict[bus_id] = []
        bus_dict[bus_id].append({'stop_id': stop_id, 'stop_name': stop_name, 'next_stop': next_stop,
                                 'stop_type': stop_type, 'a_time': a_time})


def parse_routes():
    """Parses the bus data to determine the bus route start, transfer, and finish locations"""
    global not_on_demand
    route_dict = {'Start stops': [], 'Transfer stops': [], 'Finish stops': []}
    transfer = []
    for key, value in bus_dict.items():
        start = ""
        finish = ""
        for stop in value:
            stop_type = stop['stop_type']
            stop_name = stop['stop_name']
            if stop_type == 'S':
                start = stop_name
                if start not in route_dict['Start stops']:
                    route_dict['Start stops'].append(start)
            elif stop_type == 'F':
                finish = stop_name
                if finish not in route_dict['Finish stops']:
                    route_dict['Finish stops'].append(finish)
            if stop_name in transfer:
                if stop_name not in route_dict['Transfer stops']:
                    route_dict['Transfer stops'].append(stop_name)
            if stop_name not in transfer:
                transfer.append(stop_name)
        if not finish or not start:
            print(f'There is no start or end stop for the line: {key}')
            return
    not_on_demand = set(route_dict['Start stops'] + route_dict['Transfer stops'] + route_dict['Finish stops'])


def parse_stops():
    """Checks that each stop their estimated arrival times are in the correct order"""
    bus_routes = {}
    for bus in bus_dict:
        bus_routes[bus] = []
        val = ''
        while val != 'F':
            for key, value in bus_data.items():
                if value['bus_id'] == bus:
                    if len(bus_routes[bus]) == 0:
                        if value['stop_type'] == 'S':
                            bus_routes[bus].append(key)
                            val = value['next_stop']
                    elif value['stop_type'] == 'F':
                        bus_routes[bus].append(key)
                        val = 'F'
                    elif value['stop_id'] == val:
                        bus_routes[bus].append(key)
                        val = value['next_stop']


def on_demand():
    """Checks that any 'on-demand' stops adhere to the correct definition"""
    wrong_list = []
    print("On demand stops test:")
    for value in bus_data.values():
        if value['stop_type'] == 'O':
            if value['stop_name'] in not_on_demand:
                if value['stop_name'] not in wrong_list:
                    wrong_list.append(value['stop_name'])
    if not wrong_list:
        print("OK")
    else:
        print(f'Wrong stop type: {sorted(wrong_list)}')


"""     CODE FROM PRIOR PHASE - UNUSED - SAVED IF NEEDED IN THE FUTURE
    print('Arrival time test:')
    count = 0
    for route in bus_routes.values():
        prior, first_flag, skip_flag = 0, 1, 0
        for stop in route:
            if first_flag == 1:
                prior = data[stop]['a_time'][0] * 60 + data[stop]['a_time'][1]
                first_flag = 0
            elif skip_flag != 1:
                current = data[stop]['a_time'][0] * 60 + data[stop]['a_time'][1]
                if current < prior:
                    print(f"bus_id line {data[stop]['bus_id']} wrong time on station {data[stop]['stop_name']}")
                    count += 1
                    skip_flag = 1
                else:
                    prior = data[stop]['a_time'][0] * 60 + data[stop]['a_time'][1]
    if count == 0:
        print("OK")
    """


if __name__ == "__main__":
    main()
