# import tables as tb
# class MazApnMap(tb.IsDescription):
#     maz = tb.Int64Col()
#     apn = tb.Int64Col()
#     x = tb.Float64Col()
#     y = tb.Float64Col()


# class HdfUtil:
#     file: tb.File
#     filename: str
#     group: tb.Group
#     groupname: str
#     table: tb.tableextension.Table
#     tablename: str
#     row: tb.tableextension.Row

#     def __init__(self, filename, groupname, tablename):
#         self.filename = filename
#         self.groupname = groupname
#         self.tablename = tablename
#         self.file = None
#         self.group = None
#         self.table = None
#         self.row = None

#     def create(self):
#         self.file = tb.open_file(self.filename, mode='w')
#         self.group = self.file.create_group('/', self.groupname,
#                                             'Utilities for conversion from MAG to MATsim format')
#         self.table = self.file.create_table(self.group,
#                                             self.tablename,
#                                             MazApnMap,
#                                             'Mapping APN from MAZ')

#     def insert(self, data):
#         row = self.table.row
#         # for entry in data:
#         #     pointer['maz'] = entry[0]
#         #     pointer['apn'] = entry[1]
#         #     pointer['x'] = entry[2]
#         #     pointer['y'] = entry[3]
#         self.table.append(data)
#         self.table.flush()
