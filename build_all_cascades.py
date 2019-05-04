#coding:utf-8

'''
    Tasks in this script:

        1. build cascade by using all papers
        2. id subject general_subject
        3. save cascade seperately

'''
## task 1

from basic_config import *


def fetch_citing_relations(pathObj):

    field =pathObj.field
    logging.info('fetch citing relations ...')

    query_op = dbop()
    sql = 'select id,ref_id from wos_references'
    progress=0
    sub_progress = 0
    pid_cits = []
    saved_path = pathObj.pid_cits_path
    os.remove(saved_path) if os.path.exists(saved_path) else None
    pfile = open(saved_path,'w+')
    for pid,ref_id in query_op.query_database(sql):
        progress+=1
        if progress%10000000==0:
            logging.info('total progress {:} ...'.format(progress))
            pfile.write('\n'.join(pid_cits)+'\n')
            pid_cits = []

        pid_cits.append('{:}\t{:}'.format(ref_id,pid))

    query_op.close_db()
    pfile.write('\n'.join(pid_cits)+'\n')
    logging.info('{:} citing relations are saved to {:}'.format(progress,saved_path))

def build_cascade_from_pid_cits(pathObj):

    pid_cits_path = pathObj.pid_cits_path

    logging.info("build cascade from {:} .".format(pid_cits_path))

    pid_citations = defaultdict(list)
    for line in open(pid_cits_path):

        line = line.strip()
        pid,citing_id = line.split("\t")
        pid_citations[pid].append(citing_id)

    pids = pid_citations.keys()

    pid_dis = {}

    length = len(pids)
    logging.info('{:} citation relation loaded, start to build cascade ...'.format(length))
    progress = 0
    saved_path = pathObj.cascade_path
    os.remove(saved_path) if os.path.exists(saved_path) else None

    outfile = open(saved_path,'w+')
    citation_cascade = defaultdict(list)
    total_num = 0
    for pid in pids:
        progress+=1

        if progress%100000==0:
            total_num += len(citation_cascade.keys())
            outfile.write(json.dumps(citation_cascade)+'\n')
            logging.info('Building progress {:}/{:}, {:} citation cascades saved to {:}...'.format(progress,len(selected_IDs),total_num,saved_path))
            citation_cascade = defaultdict(list)

        citing_list = set(pid_citations.get(pid,[]))

        pid_dis[len(citing_list)]+=1

        if len(citing_list)==0:
            continue

        for cit in citing_list:

            if pid == cit:
                continue

            citation_cascade[pid].append([cit,pid])

            ## if cit has no citation
            cit_citation_list = set(pid_citations.get(cit,[]))

            if len(cit_citation_list)==0:
                continue

            for inter_pid in (citing_list & cit_citation_list):
                citation_cascade[pid].append([inter_pid,cit])

    outfile.write(json.dumps(citation_cascade)+"\n")
    logging.info("{:} citation cascade has been build, and saved to {:}".format(total_num,saved_path))


def fecth_subjects():
    # com_IDs = set([line.strip() for line in open(com_IDs_path)])
    # logging.info('fetch published year of {:} combine ids'.format(len(com_IDs)))
    _ids_subjects = defaultdict(list)
    ## query database wos_summary
    query_op = dbop()
    sql = 'select id,subject from wos_subjects'
    progress=0
    for pid,subject in query_op.query_database(sql):
        progress+=1
        if progress%1000000==0:
            logging.info('progress {:} ...'.format(progress))

        _ids_subjects[pid].append(subject)

    query_op.close_db()
    logging.info('{:} cited ids have subject'.format(len(_ids_subjects.keys())))
    open('data/_ids_subjects.json','w').write(json.dumps(_ids_subjects))
    # return com_ids_subjects


if __name__ == '__main__':
    ## task 1
    # if int(sys.argv[1])==0:
    #     field = 'physics'
    # else:
    field = 'ALL'

    paths = PATHS(field)

    ## task 4
    fetch_citing_relations(paths)

    ## task 5
    build_cascade_from_pid_cits(paths)

    # task 6
    fecth_subjects(paths)

    # task 7
    # fecth_subjects_of_com_ids(paths)











