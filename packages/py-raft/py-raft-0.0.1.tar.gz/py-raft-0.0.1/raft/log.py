class RaftLog(object):
    def __init__(self, log):
        if not log:
            le = logentry(0, '', {})
            le['index'] = 0
            le['committed'] = True
            log = {0: le}
        self.log_by_index = log
        self.log_by_msgid = {}
        for ent in self.log_by_index.values():
            msgid = ent['msgid']
            self.log_by_msgid[msgid] = ent

    def dump(self):
        return self.log_by_index

    def get_max_index_term(self):
        maxindex = self.maxindex()
        maxterm = self.log_by_index.get(maxindex, {}).get('term', None)
        return maxindex, maxterm

    def has_uuid(self, uuid):
        return uuid in self.log_by_msgid

    def maxindex(self):
        return max(self.log_by_index)

    def get(self, idx):
        return self.log_by_index.get(idx, None)

    def get_by_uuid(self, uuid):
        return self.log_by_msgid.get(uuid, None)

    def get_by_index(self, index):
        return self.get(index)

    def get_term_of(self, idx):
        le = self.get(idx)
        return le['term']

    def remove(self, idx):
        ent = self.log_by_index[idx]
        del self.log_by_index[idx]
        msgid = ent['msgid']
        del self.log_by_msgid[msgid]

    def add(self, logentry):
        if not 'index' in logentry:
            # this is being appended to a leader's log; reject if msgid is
            # known and allocate a new index for it
            if logentry['msgid'] in self.log_by_msgid:
                return
            index = self.maxindex() + 1
            logentry['index'] = index
        else:
            # this is a follower being told to put logentry in a specific spot
            index = logentry['index']
            mi = self.maxindex()
            if mi + 1 != index:
                # remove everything in the log after and including the current
                # index
                remove = [x for x in self.log_by_index if x >= index]
                for rem in remove:
                    self.remove(rem)
        self.log_by_index[index] = logentry
        msgid = logentry['msgid']
        self.log_by_msgid[msgid] = logentry
        return index

    def add_ack(self, index, term, uuid):
        ent = self.log_by_index[index]
        if uuid in ent['acked']:
            return
        ent['acked'].append(uuid)

    def num_acked(self, index):
        ent = self.log_by_index[index]
        return len(ent['acked'])

    def commit(self, index, term):
        ent = self.log_by_index[index]
        assert ent['term'] == term
        ent['committed'] = True

    def force_commit(self, index):
        # this is more dangerous; only call it from followers on orders
        # from the leader
        ent = self.log_by_index.get(index, None)
        if ent is None:
            return
        ent['committed'] = True

    def is_committed(self, index, term):
        ent = self.log_by_index[index]
        if ent['term'] != term:
            return False
        index = ent['index']
        return index <= self.get_commit_index()

    def is_committed_by_uuid(self, uuid):
        ent = self.log_by_msgid.get(uuid, None)
        if ent is None:
            return False
        index = ent['index']
        return index <= self.get_commit_index()

    def logs_after_index(self, index):
        last = self.maxindex()
        logs = {}
        for x in range(index, min(last, index + 50)):
            logs[x+1] = self.log_by_index[x+1]
        return logs

    def committed_logs_after_index(self, index):
        last = self.get_commit_index()
        logs = {}
        for x in range(index, last):
            logs[x+1] = self.log_by_index[x+1]
        return logs

    def get_commit_index(self):
        for k in reversed(sorted(self.log_by_index)):
            v = self.log_by_index[k]
            if v['committed']:
                return v['index']
        return 0

    def exists(self, index, term):
        return self.log_by_index.get(index, {}).get('term', None) == term

    def __le__(self, other):
        mi, mt = self.get_max_index_term()
        oi, ot = other.get_max_index_term()
        return ot > mt or ot == mt and oi >= mi

    def __gt__(self, other):
        return not self <= other


def logentry(term, uuid, msg):
    rpc = {
        'term': term,
        'msgid': uuid,
        'committed': False,
        'acked': [],
        'msg': msg,
    }
    return rpc
