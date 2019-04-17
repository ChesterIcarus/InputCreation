from typing import List, Dict, T
from xml.etree import ElementTree as et
from math import floor
import csv

from mag_handler.fast.matsim_plan import FastMatsimPlan, MatsimAct, MatsimLeg
from mag_handler.encoded_data_util import purpose_encode, mode_encode


class MatsimXml:
    def __init__(self, location_type):
        '''Location type is either (`maz` | `coord`)'''
        self.location_type = location_type

    def leg(self, leg: MatsimLeg) -> Dict[str, str]:
        node = dict()
        node['mode'] = leg.mode
        return self.set_leg_times(leg, node)

    def act(self, act: MatsimAct) -> Dict[str, str]:
        node = dict()
        node['type'] = act.purpose
        node = self.set_loc(act, node)
        return self.set_act_time(act, node)

    def set_leg_times(self, leg: MatsimLeg, node: Dict[str, str]) -> Dict[str, str]:
        node['dep_time'] = self.time_str(
            abs(leg.dep_time) + (4.5 * 60))
        node['trav_time'] = self.time_str(abs(leg.trav_time))
        return node

    def set_act_time(self, act: MatsimAct, node: Dict[str, str]) -> Dict[str, str]:
        '''0 = end_time; 1 = duration'''
        if act.end_time:
            node['end_time'] = self.time_str(
                abs(act.end_time) + (4.5 * 60))
        if act.duration:
            node['dur'] = self.time_str(abs(act.duration))
        return node

    def set_loc(self, act: MatsimAct, node: Dict[str, str]) -> Dict[str, str]:
        # node['maz'] = str(act.maz)
        # node['apn'] = str(act.apn)
        node['x'] = str(act.coord.x)
        node['y'] = str(act.coord.y)
        return node

    def time_str(self, minutes: int) -> str:
        hour = str(floor(minutes / 60))
        if len(hour) == 1:
            hour = f'0{hour}'
        minute = str(floor(minutes - (int(hour) * 60)))
        if len(minute) == 1:
            minute = f'0{minute}'
        second = str(floor((minutes - floor(minutes)) * 60))
        if len(second) == 1:
            second = f'0{second}'
        return f'{hour}:{minute}:{second}'

    def write(self, plans: List[FastMatsimPlan], filepath: str, use_mag=True):
        root = et.Element('population')
        tree = et.ElementTree(root)
        matplan: FastMatsimPlan
        uid = 0
        pid = 0
        pid_list = list()
        for matplan in plans:
            person = et.SubElement(root, 'person')
            person.attrib['id'] = str(pid)
            pid += 1
            pid_list.append((matplan.pnum, matplan.hhid))
            # person.attrib['pnum'] = str(matplan.pnum)
            # person.attrib['hhid'] = str(matplan.hhid)

            plan = et.SubElement(person, 'plan')
            plan.attrib['selected'] = 'yes'

            event_list = list()
            for value in matplan.events:
                if isinstance(value, MatsimAct):
                    pair = ('act', self.act(value))
                    # pair[1]['uid'] = str(uid)
                    event_list.append(pair)
                elif isinstance(value, MatsimLeg):
                    pair = ('leg', self.leg(value))
                    # pair[1]['uid'] = str(uid)
                    event_list.append(pair)
                else:
                    print(value)
                    raise ValueError('''Each value in a plan must
                                        be either MatsimAct or MatsimLeg''')
                uid += 1
            for event in event_list:
                et.SubElement(plan, event[0], attrib=event[1])

        tree.write(filepath)
        # with open(filepath, 'w+') as handle:
            # handle.write(et.tostring(root, encoding=str, pretty_print=True))
        with open(filepath.split('.xml')[0] + '.csv', 'w+') as handle:
            writer = csv.writer(handle)
            writer.writerows(pid_list)


