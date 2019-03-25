from typing import List, Dict, T
from lxml import etree as et
from math import floor

from mag_handler.matsim_plan import MatsimPlan, MatsimAct, MatsimLeg
from mag_handler.encoded_data_util import purpose_encode, mode_encode


class MatsimXml:
    def __init__(self, location_type):
        '''Location type is either (`maz` | `coord`)'''
        self.location_type = location_type

    def leg(self, leg: MatsimLeg) -> Dict[str, str]:
        node = dict()
        node['mode'] = leg.mode
        return node

    def act(self, act: MatsimAct) -> Dict[str, str]:
        node = dict()
        node['type'] = act.purpose
        node = self.set_loc(act, node)
        node = self.set_time(act, node)
        return node

    def set_time(self, act: MatsimAct, node: Dict[str, str]) -> Dict[str, str]:
        '''0 = end_time; 1 = duration'''
        if act.end_time:
            node['end_time'] = self.time_str(
                abs(act.end_time) + (4.5 * 60))
        if act.duration:
            node['dur'] = self.time_str(abs(act.duration))
        return node

    def set_loc(self, act: MatsimAct, node: Dict[str, str]) -> Dict[str, str]:
        node['maz'] = str(act.maz)
        node['apn'] = str(act.apn)
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

    def write(self, plans: List[MatsimPlan], filepath: str, use_mag=True):
        root = et.Element('population')
        matplan: MatsimPlan
        uid = 0
        for matplan in plans:
            person = et.SubElement(root, 'person')
            if use_mag:
                person.attrib['id'] = f'{matplan.mag_pnum}_{matplan.mag_hhid}'
            else:
                person.attrib['id'] = str(matplan.person_id)

            plan = et.SubElement(person, 'plan')
            plan.attrib['selected'] = 'yes'

            event_list = list()
            for value in matplan.events:
                if isinstance(value, MatsimAct):
                    pair = ('act', self.act(value))
                    pair[1]['uid'] = str(uid)
                    event_list.append(pair)
                elif isinstance(value, MatsimLeg):
                    pair = ('leg', self.leg(value))
                    pair[1]['uid'] = str(uid)
                    event_list.append(pair)
                else:
                    print(value)
                    raise ValueError('''Each value in a plan must 
                                        be either MatsimAct or MatsimLeg''')
                uid += 1
            for event in event_list:
                try:
                    sub = et.SubElement(plan, event[0], attrib=event[1])
                except TypeError:
                    print(event[1])
                    exit(1)

        with open(filepath, 'w+') as handle:
            handle.write(et.tostring(root, encoding=str, pretty_print=True))
