import os
import glob
import pandas as pd

# directory = 'data/MentalLLaMA-main/test_data/test_instruction'
#
# csv_files = glob.glob(os.path.join(directory, "*.csv"))
#
# for csv_file in csv_files:
#     df = pd.read_csv(csv_file)
#     splits = df['query'].str.split('Question:',expand=True)[0]
#     df['post'] = df['query'].str.split('Question: ',expand=True)[0]
#     df['question'] = df['query'].str.split('Question: ', expand=True)[1]
#
#     if 'SAD' in csv_file:
#         df['answer'] = df['gpt-3.5-turbo'].str.split('.', expand=True)[0]
#         df['answer'] = df['answer'].str.replace('This post shows the stress cause related to ','')
#     else:
#         df['answer'] = df['gpt-3.5-turbo'].str.split(', ', expand=True)[0]
#
#     df['post'] =   df['post'].str.replace('Consider this post: ',' ')
#     df['post'] = df['post'].str.replace('"',' ')
#     df['post'] = df['post'].str.replace('\t', ' ')
#     df['question'] = df['question'].str.replace('\t', ' ')
#     #print(df.head())
#     print(df['answer'][:3])
#     columns_order = ['question', 'answer','post']
#
#     df.to_csv(csv_file.replace('.csv', '_processed.tsv'), sep='\t', columns=columns_order, index=False)


# directory = 'data/MentalLLaMA-main/test_data/test_instruction'
#
# csv_files = glob.glob(os.path.join(directory, "*.csv"))
#
# for csv_file in csv_files:
#     df = pd.read_csv(csv_file)
#
#     columns_order = ['query']
#
#     df.to_csv(csv_file.replace('.csv', '_instruction.tsv'), sep='\t', columns=columns_order, index=False)


import os
import glob
import pandas as pd

directory = 'data/MentalLLaMA-main/human_evaluation/test_instruction_expert'

csv_files = glob.glob(os.path.join(directory, "*.csv"))

for csv_file in csv_files:
    df = pd.read_csv(csv_file)


    df[['post', 'question']] = df['query'].str.split('Question: ', expand=True)
    df['post'] = df['post'].str.replace('Consider this post: ', ' ', regex=False)


    df['post'] = df['post'].str.replace(r'["\n\t]+', ' ', regex=True)
    df['question'] = df['question'].str.replace(r'["\n\t]+', ' ', regex=True)

    if 'SAD' in csv_file:
        df['answer'] = df['gpt-3.5-turbo'].str.split('.', expand=True)[0]
        df['answer'] = df['answer'].str.replace('This post shows the stress cause related to ','')
    else:
        df['answer'] = df['gpt-3.5-turbo'].str.split(', ', expand=True)[0]

    df['gpt-3.5-turbo'] = df['gpt-3.5-turbo'].str.replace('Reasoning: ', ' ', regex=False)

    columns_order = ['question', 'gpt-3.5-turbo', 'post','answer']

    df.to_csv(csv_file.replace('.csv', '_processed.tsv'), sep='\t', columns=columns_order, index=False)
