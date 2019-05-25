from sys import argv
import json

def json_to_conll(inputfile,outputfile,is_gold):

    fr = open(inputfile,'r')
    fw = open(outputfile,'w')

    # fw.write('#begin document (Oshin);\n')

    for line in fr.readlines():
        doc_as_json = json.loads(line)
        doc_key = doc_as_json['doc_key']
        fw.write("#begin document " + doc_key + '\n')
        words = [word for sent in doc_as_json['sentences'] for word in sent]
        tags = [{'index':str(i),'word':word,'tag':'-'} for i,word in enumerate(words)]
        clusters = list(doc_as_json['clusters']) if is_gold else doc_as_json['predicted']
        for clustNum,cluster in enumerate(clusters):
            for mention in cluster:
                if mention[0] == mention[1]:
                    if tags[mention[0]]['tag'] == '-':
                        tags[mention[0]]['tag'] = '('+str(clustNum)+')'
                    else:
                        tags[mention[0]]['tag'] += '|('+str(clustNum)+')'
                else:
                    if tags[mention[0]]['tag'] == '-':
                        tags[mention[0]]['tag'] = '('+str(clustNum)
                    else:
                        tags[mention[0]]['tag'] += '|('+str(clustNum)
                    if tags[mention[1]]['tag'] == '-':
                        tags[mention[1]]['tag'] = str(clustNum)+')'
                    else:
                        tags[mention[1]]['tag'] += '|' + str(clustNum)+')'

        for i,row in enumerate(tags):
            if i == 0:
                parse = '(TOP*'
            elif i == len(tags)-1:
                parse = '*)'
            else:
			    parse = '*'
            if type(row['word']) != 'str':
                row['word'] = row['word'].encode('utf-8')
			# fw.write(doc_key+'\t0\t'+row['index']+'\t'+row['word']+'\t'+row['tag']+'\n')
            fw.write(row['word'] + ' ' + row['tag'] + '\n')
			#fw.write(doc_key+'\t0\t'+row['index']+'\t'+row['word']+'\tXX\t'+parse+'\t-\t-\t-\t-\t*\t*\t'+row['tag']+'\n')
        fw.write('\n')
        fw.write('#end document\n')

    # fw.write('#end document')
    fr.close()
    fw.close()

if __name__ == "__main__":
    inputfile = argv[1]
    outputfile = argv[2]
    is_gold = argv[3]
    json_to_conll(inputfile,outputfile,is_gold.lower() == 'y')
