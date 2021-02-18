import numpy as np
import os
import json
from nltk.tokenize import WordPunctTokenizer
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--in_path', type = str, default =  "../data")
parser.add_argument('--out_path', type = str, default = "prepro_data")

args = parser.parse_args()
in_path = args.in_path
out_path = args.out_path #Must Contain all of the metadata files (char2id.json, ner2id.json, rel2id.json, word2id.json)

char_limit = 128 #Maximum amount of characters in any word in the dataset

train_file_name = os.path.join(in_path, 'train_data.json')
validate_file_name = os.path.join(in_path, 'validate_data.json')
test_file_name = os.path.join(in_path, 'test_data.json')

rel2id = json.load(open(os.path.join(out_path, 'rel2id.json'), "r"))
id2rel = {v:u for u,v in rel2id.items()}
json.dump(id2rel, open(os.path.join(out_path, 'id2rel.json'), "w"))
fact_in_train = set([])
fact_in_dev_train = set([])

#max_length is the maximum number of words in an entire document
def init(data_file_name, rel2id, max_length = 16384, suffix=''):

	ori_data = json.load(open(data_file_name))

	data = []
	for i in range(len(ori_data)):
		Ls = [0] #Cumulative length of sentences
		L = 0 #Cumulative length of sentences
		for x in ori_data[i]['sents']:
			L += len(x)
			Ls.append(L)

		vertexSet =  ori_data[i]['vertexSet']
		# point position added with sent start position
		for j in range(len(vertexSet)):
			for k in range(len(vertexSet[j])):
				vertexSet[j][k]['sent_id'] = int(vertexSet[j][k]['sent_id'])

				sent_id = vertexSet[j][k]['sent_id']
				dl = Ls[sent_id]
				pos1 = vertexSet[j][k]['pos'][0]
				pos2 = vertexSet[j][k]['pos'][1]
				vertexSet[j][k]['pos'] = (pos1+dl, pos2+dl) #Turns position w.r.t. sentence into position w.r.t. document

		ori_data[i]['vertexSet'] = vertexSet

		item = {}
		item['vertexSet'] = vertexSet
		labels = ori_data[i].get('labels', []) #Empty list if labels do not exist

		train_triple = set([])
		new_labels = []
		for label in labels:
			rel = label['r']
			assert(rel in rel2id)
			label['r'] = rel2id[label['r']] #Maps relation to number in rel2id

			train_triple.add((label['h'], label['t']))


			if suffix=='_train':
				for n1 in vertexSet[label['h']]:
					for n2 in vertexSet[label['t']]:
						fact_in_dev_train.add((n1['name'], n2['name'], rel))

			# fix a bug here
			label['intrain'] = False
			label['indev_train'] = False

			for n1 in vertexSet[label['h']]:
				for n2 in vertexSet[label['t']]:
					if (n1['name'], n2['name'], rel) in fact_in_train:
						label['intrain'] = True

					if suffix == '_dev' or suffix == '_test':
						if (n1['name'], n2['name'], rel) in fact_in_dev_train:
							label['indev_train'] = True


			new_labels.append(label)

		item['labels'] = new_labels
		item['title'] = ori_data[i]['title']

		na_triple = []
		for j in range(len(vertexSet)):
			for k in range(len(vertexSet)):
				if (j != k):
					if (j, k) not in train_triple:
						na_triple.append((j, k))

		item['na_triple'] = na_triple
		item['Ls'] = Ls
		item['sents'] = ori_data[i]['sents']
		data.append(item)


	print ('data_len:', len(ori_data))


	# saving
	print("Saving files")
	name_prefix = "dev"

	json.dump(data , open(os.path.join(out_path, name_prefix + suffix + '.json'), "w")) #Main data saved to disk here

	char2id = json.load(open(os.path.join(out_path, "char2id.json")))
	# id2char= {v:k for k,v in char2id.items()}
	# json.dump(id2char, open("data/id2char.json", "w"))

	word2id = json.load(open(os.path.join(out_path, "word2id.json")))
	ner2id = json.load(open(os.path.join(out_path, "ner2id.json")))

	sen_tot = len(ori_data) #Total number of documents, not total number of sentences?
	sen_word = np.zeros((sen_tot, max_length), dtype = np.int64) #2D Matrix of all words in sentences
	sen_pos = np.zeros((sen_tot, max_length), dtype = np.int64)
	sen_ner = np.zeros((sen_tot, max_length), dtype = np.int64)
	sen_char = np.zeros((sen_tot, max_length, char_limit), dtype = np.int64) #3D Matrix of all characters in all words

	for i in range(len(ori_data)):
		item = ori_data[i]
		words = [] #List of all words in one document
		for sent in item['sents']:
			words += sent

		for j, word in enumerate(words):
			word = word.lower()

			if j < max_length:
				if word in word2id:
					sen_word[i][j] = word2id[word]
				else:
					sen_word[i][j] = word2id['UNK']

				for c_idx, k in enumerate(list(word)):
					if c_idx>=char_limit: #No character past the car_limit is recorded
						break
					sen_char[i,j,c_idx] = char2id.get(k, char2id['UNK'])

		for j in range(j + 1, max_length):
			sen_word[i][j] = word2id['BLANK']

		vertexSet = item['vertexSet']

		for idx, vertex in enumerate(vertexSet, 1):
			for v in vertex:
				sen_pos[i][v['pos'][0]:v['pos'][1]] = idx
				sen_ner[i][v['pos'][0]:v['pos'][1]] = ner2id[v['type']]

	print("Finishing processing")
	np.save(os.path.join(out_path, name_prefix + suffix + '_word.npy'), sen_word)
	np.save(os.path.join(out_path, name_prefix + suffix + '_pos.npy'), sen_pos)
	np.save(os.path.join(out_path, name_prefix + suffix + '_ner.npy'), sen_ner)
	np.save(os.path.join(out_path, name_prefix + suffix + '_char.npy'), sen_char)
	print("Finish saving")

init(train_file_name, rel2id, max_length = 16384, suffix='_train')
init(validate_file_name, rel2id, max_length = 16384, suffix='_validate')
init(test_file_name, rel2id, max_length = 16384, suffix='_test')
