from future.modified_builtins import super
class VerboseList(list):
    def append(self, item):
        print 'Adding an item'
        super(VerboseList, self).append(item)