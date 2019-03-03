from typing import List, T
from lxml import etree as et
from math import floor

from mag_handler.matsim_plan import MatsimPlan, MatsimAct, MatsimLeg
from mag_handler.encoded_data_util import Purpose, Mode


class MatsimXml:
    def __init__(self, location_type):
        '''Location type is either (`maz` | `coord`)'''
        self.location_type = location_type

    def time_str(self, minutes):
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

    def set_time(self, act: MatsimAct, node):
        '''0 = end_time; 1 = duration'''
        if act.end_time:
            node.attrib['end_time'] = self.time_str(
                abs(act.end_time) + (4.5 * 60))
        if act.duration:
            node.attrib['dur'] = self.time_str(abs(act.duration))

    def set_loc(self, act: MatsimAct, node):
        node.attrib['maz'] = str(act.maz)
        node.attrib['apn'] = str(act.apn)
        node.attrib['x'] = str(act.coord[0])
        node.attrib['y'] = str(act.coord[1])

    def leg(self, parent, plan: MatsimLeg) -> et.ElementBase:
        leg = et.SubElement(parent, 'leg')
        leg.attrib['mode'] = Mode(plan.mode).name

    def act(self, parent, act: MatsimAct) -> et.ElementBase:
        node = et.SubElement(parent, 'act')
        node.attrib['type'] = Purpose(act.type_).name
        self.set_loc(act, node)
        self.set_time(act, node)

    def write(self, plans: List[MatsimPlan], filepath):
        root = et.Element('population')
        for person_plan in plans:
            person = et.SubElement(root, 'person')
            person.attrib['id'] = str(person_plan.plan_id)
            plan = et.SubElement(person, 'plan')
            plan.attrib['selected'] = 'yes'

            trips = et.SubElement(plan, 'act')
            trips.attrib['type'] = Purpose(person_plan.plan[0].type_).name
            self.set_loc(person_plan.plan[0], trips)
            self.set_time(person_plan.plan[0], trips)

            for value in person_plan.plan[1::]:
                if isinstance(value, MatsimAct):
                    self.act(plan, value)
                elif isinstance(value, MatsimLeg):
                    self.leg(plan, value)
                else:
                    raise ValueError(
                        'Each value in a plan must be either MatsimAct or MatsimLeg')
        with open(filepath, 'wb+') as handle:
            handle.write(et.tostring(root, pretty_print=True))
