
# MalKG
*Official repository for MalKG*

***Paper title**: Knowledge Graph Generation and Entity Prediction for Contextual Malware Threat Intelligence*

## Relation Extraction

### Installation and Requirements

All python files were ran using Python 3.8
All notebook files were ran using Google Colab
#### SpaCy

    $pip3 install -U pip setuptools wheel
    $pip3 install -U spacy
    $python3 -m spacy download en_core_web_sm

#### DocRED

16GB of Video Memory Compatible with CUDA
32GB of RAM

    $pip3 install -r /Code/DocRED/code/requirements.txt

#### Flair12
    $pip3 install -U flair

### Training
#### Data Set
We trained the DocRED model with a set of 64 hand annotated threat reports. These reports were annotated using BRAT, and can be found under [Code/Training Data Parser/input/](Code/Training%20Data%20Parser/input/).

#### Preprocessing
##### Converting BRAT annotations into JSON files for DocRED
To convert the text files and BRAT annotation files into the appropriate format for DocRED go to [Code/Training Data Parser/](Code/Training%20Data%20Parser/) and run:

    $python3 SpaCy_parser.py

The output will be under [Code/Preprocessing/annotated_data.json](Code/Preprocessing/).

##### Cleaning Up JSON files for DocRED
Due to memory constraints, we were only able to run documents that contained 80 named entities or fewer through DocRED. Thus, we broke documents containing more than 80 named entities into multiple documents. We also excluded documents containing more than 16384 words and changed some of the named entity classifications to match flair12. Finally, we had to split the documents into a training set and a validation set. All of this can be accomplished by navigating to [Code/Preprocessing/](Code/Preprocessing/) and running:

    $python3 docred_preprocessing.py

The output will be under [Code/DocRED Input/train_data.json](Code/DocRED%20Input/) and [Code/DocRED Input/validate_data.json](Code/DocRED%20Input/)

#### DocRED
We ran DocRED using Google Colab with the notebook [Code/DocRED/DOCRED.ipynb](Code/DocRED/). [Code/DocRED/data/](Code/DocRED/data/) should contain train_data.json, validate_data.json, and test_data.json. This will be processed by running:

    $python3 gen_data.py --in_path ../data --out_path prepro_data

The number of epochs used for training can be set in [Code/DocRED/code/train.py](Code/DocRED/code/), and we have it set to 10,000. Every 5 epochs DocRED compares the current epoch to the previous best epoch, and saves the model to [Code/DocRED/code/checkpoint/checkpoint_BiLSTM.zip](Code/DocRED/code/checkpoint/) if it is better. Training can be done by running:

CUDA_VISIBLE_DEVICES=0 python3 train.py --save_name checkpoint_BiLSTM --train_prefix dev_train --test_prefix dev_validate
### Testing
#### Converting PDFs to TXT
Threat Report PDFs were ran through Adobe Acrobat using the Action Wizard with Export PDFs to TXTs.sequ to convert them into TXTs.

#### Named Entity Recognition
We used Flair12 and SetExpan to extract named entities from our test data. Entities can be extracted form Threat Reports by navigating to (Code/NER/)[Code/NER/], and using the notebook file or by running:

    $python3 automated_flair12.py

The output will be under [Code/Preprocessing/threatreport_flair12_data.json](Code/Preprocessing/)

#### Cleaning Up JSON files for DocRED
Similarly to the training data, we needed to break the testing data apart due to memory constraints. This can be done by navigating to [Code/Preprocessing/](Code/Preprocessing/) and running:

    $python3 docred_preprocessing.py

All of the testing documents will be output under [Code/DocRED Input/threatreport_flair12_test_data_all.json](Code/DocRED%20Input/) and [Code/DocRED Input/threatreport_setexpan_test_data_all.json](Code/DocRED%20Input/). However, we were only able to test 256 documents at one time. Thus, [Code/DocRED Input/Threat Report Flair12 Data/](Code/DocRED Input/Threat Report Flair12 Data/) and [Code/DocRED Input/Threat Report SetExpan Data/](Code/DocRED%20Input/Threat%20Report SetExpan%20Data/) contains the testing data split by 256 documents.

#### DocRED
In order to test with DocRED, the JSON file you want to test must be renamed to test_data.json and placed under [Code/DocRED/data/](Code/DocRED/data/). This can be processed by running:

    $python3 gen_data.py --in_path ../data --out_path prepro_data

and testing can be done by running:

    $CUDA_VISIBLE_DEVICES=0 python3 test.py --save_name checkpoint_BiLSTM --train_prefix dev_train --test_prefix dev_test --input_theta 0.5

The results of the test will be output as [Code/DocRED/code/dev_test_index.json](Code/DocRED/code/).

#### Converting the DocRED output into CSVs
To convert DocRED output into CSVs, go to [Code/Postprocessing/](Code/Postprocessing/) and run:

    $python3 format.py

This outputs to the corresponding csvs directories, as well as Results.


### Citations
@inproceedings{yao2019DocRED,
  title={{DocRED}: A Large-Scale Document-Level Relation Extraction Dataset},
  author={Yao, Yuan and Ye, Deming and Li, Peng and Han, Xu and Lin, Yankai and   
                Liu, Zhenghao and Liu, Zhiyuan and Huang, Lixin and Zhou, Jie and Sun, 	 
                Maosong},
  booktitle={Proceedings of ACL 2019},
  year={2019}
}
