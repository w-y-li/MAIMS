import copy
import json
import time

from sklearn.metrics import f1_score, accuracy_score
import math
from tqdm import trange
from ms import MS
from datetime import datetime
from openai import OpenAI


def output_records(ms_name, records, accuracy, precision, recall, f1_score, score_show):
    now = datetime.now()
    formatted_now = now.strftime("%m_%d_%H_%M_%S")
    with open(f'output/{ms_name}_{formatted_now}.txt', 'w+') as f:
        for record in records:
            f.write(f'Id: {record[0]}\n')
            f.write(f'True Label: {record[1]}\n')
            f.write(f'Post: \n\'\'\'\n{record[2]}\'\'\'\n')
            f.write(f'Answer to the Scale: {record[3]}\n')
            f.write(f'Reason to Scale\'s answer: {record[4]}\n')
            f.write(f'Result: {record[5]}\n')
            f.write(f'Explanation to the Result: {record[6]}\n\n\n')

        f.write(str(score_show[0]) + '\n')
        f.write(str(score_show[1]) + '\n')
        f.write('\nAccuracy: ' + str(accuracy) + '\n')
        f.write('Precision: ' + str(precision) + '\n')
        f.write('Recall: ' + str(recall) + '\n')
        f.write('F1 Score: ' + str(f1_score) + '\n')

class Data:
    def __init__(self, dataset_name,ms_name):
        self.dataset_name = dataset_name
        self.ms_name = ms_name
        self.posts = []
        self.questions = []
        self.labels = []
        self.answers={'DR':['Yes','No'],'dreaddit':['Yes','No'],'Irf':['Yes','No'],'MultiWD':['Yes','No'],'SAD':['financial problem','This post shows other stress causes','everyday decision making','emotion turmoil','family issues','social relationships','work','health issues','school']}
        self.questionnaire = MS
        self.questionnaire_len=len(self.questionnaire[self.ms_name][0])

    def load_data(self):
        with open('data/MentalLLaMA-main/test_data/test_instruction/'+self.dataset_name+'_processed.tsv', 'r',encoding='utf-8') as file:
            file = file.readlines()
            print(self.dataset_name+' dataset loaded.')
            print('Total posts of '+str(len(file)))
            for line in file[1:]:
                line=line.split('\t')
                self.posts.append(line[2])
                self.questions.append(line[0])
                self.labels.append(line[1])

    def create_questionnaire(self,incorrect_index=[]):
        scale_content = []
        for i in range(1, len(self.questionnaire[self.ms_name][0]) + 1):
            if str(i)  in incorrect_index:
                scale_content.append([str(i),f"Question ID of {i}: {self.questionnaire[self.ms_name][0][str(i)]}\nOptions: "])
                for j in range(len(self.questionnaire[self.ms_name][1][str(i)])):
                    scale_content[-1][1] = scale_content[-1][1]+self.questionnaire[self.ms_name][1][str(i)][j] + ',\t'

        return scale_content

def use_gpt(client,call_num,total_num,messages,model,max_try,process_func):
    cnt = 0
    while cnt < max_try:
        try:
            chat_completion = client.chat.completions.create(
                messages=messages,
                model=model,
            )
            answer = chat_completion.choices[0].message.content.strip()
            if 'Output:' in answer:
                results = process_func(answer.split('Output:', 2)[1])
            else:
                results = process_func(answer)
            return results
        except Exception as e:
            e=str(e)
            e=e.replace('\n','//n')
            print(e)
            cnt += 1
            time.sleep(0.1)
            print(f'Try {cnt} for {call_num} of {total_num}... ')

    return f"Error: Failed {call_num} of {total_num} after {max_try} attempts"

def process_do_ms(answer):
    answer=json.loads(answer)
    results={}
    for i in range(len(answer)):
        results[str(answer[i]['ID'])]=[answer[i]['Judgement'],answer[i]['Answer']+'###'+answer[i]['Reason']]
        id = int(answer[i]['ID'])
    return results

def process_check_ms(answer):
    answer=json.loads(answer)
    results={}
    for i in range(len(answer)):
        results[str(answer[i]['ID'])]=[answer[i]['Judgement'],answer[i]['Advice']]
        id = int(answer[i]['ID'])
    return results

def process_gen_result(answer):
    answer=json.loads(answer)
    results={}
    results[str(answer['ID'])]=[answer['Response'],answer['Reason']]
    id = int(answer['ID'])
    return results

def process_check_gen_result(answer):
    answer=json.loads(answer)
    results={}
    results[str(answer['ID'])]=[answer['Judgement'],answer['Advice']]
    id=int(answer['ID'])
    return results

def do_ms(client,scale_content,post,model,max_try,windowsize,feedbacks):
    results=[]
    for i in trange(math.ceil(len(scale_content)/windowsize),desc="Doing mental scale..."):
        criteria = ''
        if i == math.ceil(len(scale_content)/windowsize)-1:
            second_elements = [element[1] for element in scale_content[i*windowsize:]]
            scale = '\n'.join(second_elements)
            for j in range(i * windowsize,len(scale_content)):
                if scale_content[j][0] in feedbacks:
                    criteria=criteria+f'Advice for question {scale_content[j][0]}: '+feedbacks[scale_content[j][0]]+'\n'
        else:
            second_elements = [element[1] for element in scale_content[i * windowsize:(i+1) * windowsize]]
            scale = '\n'.join(second_elements)
            for j in range(i * windowsize,(i + 1) * windowsize):
                if scale_content[j][0] in feedbacks:
                    criteria=criteria+f'Advice for question {scale_content[j][0]}: '+feedbacks[scale_content[j][0]]+'\n'

        if criteria != '':
            criteria='Pay attention to the following advice when you do your task:\n'+criteria
        messages=[
        {'role': 'system', 'content': 'You are a psychology expertise,you are familiar with all kinds of people,you are good at role playing someone just based on some of his/her text.'},
        {'role': 'user', 'content': f"Your task is to read a post on social media,then judge whether the post mention some questions from mental scales and act as the poster to answer these questions."
                                    f"\nI will give you a post of the poster and some questions,you should output the judgement ,answers and the reason to your answers."
                                    f"\nThe inputs are as follows:\nPost:\n{post}\n\nQuestions:\n{scale}\n\n"
                                    f"\nYour output should be a list of JSON objects for each question,each with keys are 'ID','Judgement','Answer' and 'Reason',one example of the format is:[{'{'}\"ID\":\"\",\"Judgement\":\"\",\"Answer\":\"\",\"Reason\":\"\"'{'}'}{'{'}\"ID\":\"\",\"Judgement\":\"\",\"Answer\":\"\",\"Reason\":\"\"'{'}'}]"
                                    f"\n\nUnder 'ID',you should just say the question ID as I give to you in the input,don't change any."
                                    f"\n\nUnder 'Judgement',if you think the post directly mention the question,show the answer of the question, you should say 'directly_mention'.Else if you think the post indirectly mention the question,but it contains some information that you can use your knowledge of a psychology expertise to make proper deduction from the information and answer the question,you should say 'indirectly_mention'.Else you think the post doesn't mention the question at all and doesn't have any information that can help you deduce the answer,you should say 'not_mention'."
                                    f"\n\nUnder 'Answer',if you say 'directly_mention' or 'indirectly_mention' in the content of 'Judgement',you should just say your answer to the question here. Else if you say 'not_mention' in the content of 'Judgement',you should say 'Doesn't mention at all.' here.You answer should be in the first person."
                                    f"\n\nUnder 'Reason',give a short and concise reason for your answer, but you should explain your answer thoroughly.You reason should be in the first person."
                                    f"\n\nPay attention that you should totally base on the post to act as the poster to answer the questions.Don't make ANY deduction by yourself,you must base on the information from the post."
                                    f"\n\n{criteria}"
                                    f"\n\nDon't say any other words,don't explain,just give your output of a JSON list as I request."}]

        results.append(use_gpt(client,i,math.ceil(len(scale_content)/windowsize),messages,model,max_try,process_do_ms))

    try:
        ms_answer=results[0]
    except:
        a=1
    for i in range(1,len(results)):
        ms_answer.update(results[i])

    return ms_answer

def check_ms(sorted_ms_answer,post,model,max_try,windowsize):
    results = []

    for i in trange(math.ceil(len(sorted_ms_answer)/windowsize),desc="Checking mental scale's answer..."):
        if i == math.ceil(len(sorted_ms_answer)/windowsize)-1:
            scale = '\n'.join(sorted_ms_answer[i*windowsize:])
        else:
            scale = '\n'.join(sorted_ms_answer[i * windowsize:(i + 1) * windowsize])

        messages=[
        {'role': 'system', 'content': 'You are a psychology tutor, and you are very good at pointing out students\' mistakes.'},
        {'role': 'user', 'content': f"The students majoring in psychology are doing a task of reading someone's post on sociel media and act as the poster to answer some questions from mental scales,they are asked to answer the question just base on the post."
                                    f"\n\nThis task aims to enhance their ability to carefully analysis the social media post,and to use the knowledge of psychology to act as the poster."
                                    f"\n\nHowever,some of the students don't do well,they always make the following mistakes:"
                                    f"\n\n1.They always over inference the poster,they are always likely to think the poster has some negative characteristics even there is no information in the post to prove that."
                                    f"\n\n2.They always thought the post doesn't contain any information of the question,the students always lack of carefully analysis and just thought the post doesn't mention the question at all."
                                    f"\n\n3.Some posts are telling the people around the poster but not the poster himself,the students always make mistake at this time,infer the poster based the people around the poster,this is wrong."
                                    f"\n\nYour task as their teacher is to judge whether they do a good role playing of the poster or not,whether they make the above mistakes."
                                    f"\n\nThe input will be the social media post of the poster ,some questions from mental scale and the answer they made acting as the poster.Your output should be your judgement and advice to the students."
                                    f"\n\nThe inputs are as follows:\nPost:\n{post}\n\nQuestions and Students' answers:\n{scale}\n\n"
                                    f"\n\nYour output should be a list of JSON objects for each question,each with keys are 'ID','Judgement' and 'Advice',one example of the format is:[{'{'}\"ID\":\"\",\"Judgement\":\"\",\"Advice\":\"\"'{'}'}{'{'}\"ID\":\"\",\"Judgement\":\"\",\"Advice\":\"\"'{'}'}]"
                                    f"\n\nUnder 'ID',you should just say the question ID as I give to you in the input,don't change any."
                                    f"\n\nUnder 'Judgement',if you think the student's answer is correct,the student doesn't make these mistakes, he correctly play the role of the poster, properly answer the question based on the post and show a correct deduction process,you should say 'Correct' here.Else you should say 'Incorrect' here."
                                    f"\n\nUnder 'Advice',give the students your advice to help them correctly do the task."
                                    f"\n\nPay attention to these mistake,they are easy to make for the psychology students."
                                    f"\n\nDon't say any other words,don't explain,just give your output as I request."}]

        results.append(use_gpt(client,i,math.ceil(len(sorted_ms_answer)/windowsize),messages,model,max_try,process_check_ms))

    check_ms_answer=results[0]
    for i in range(1,len(results)):
        check_ms_answer.update(results[i])

    return check_ms_answer

def gen_result(ms_answer_results,posts,questions,answer_list,model,max_try,post_incorrect_index,post_advices):
    results = []

    for i in trange(len(ms_answer_results),desc="Generating results for detection..."):
        advice=''
        if str(i) in post_incorrect_index:
            ms_answer_content=''
            if ms_answer_results[i] == {}:
                ms_answer_content+='(There is no answered questions this time.)'
            else:
                ms_answer_results[i]=sorted(ms_answer_results[i].items(), key=lambda item: int(item[0]))
                for j in range(len(ms_answer_results[i])):
                    ms_answer_content+=ms_answer_results[i][j][1]
                    ms_answer_content+='\n'

            if str(i) in post_advices:
                advice = advice + f'Advice for post {i}: ' + post_advices[str(i)] + '\n'

            if advice != '':
                advice='Pay attention to the following advice when you do your task:\n'+advice
            messages=[
            {'role': 'system', 'content': 'You are a psychology expertise,you are familiar with all the mental health problem and you are good at recognize them.'},
            {'role': 'user', 'content': f"Your task is to recognize the poster's mental health problem and give response to a mental health question as I request below."
                                        f"\n\nI will give you a post of a poster,some question-answer pairs to the questions of a relevant mental scale done by the poster that help you better give response,you should follow my instruction to analyse the poster's mental health."
                                        f"\n\nThe inputs are as follows:\n"
                                        f"\n\nPost of ID {i}:\n{posts[i]}\n\nAnswered Questions of mental scale:\n{ms_answer_content}\n\n"
                                        f"\n\nYour output should be in JSON format with keys are 'ID','Response' and 'Reason'"
                                        f"\n\nUnder 'ID',you should just output the ID of the post as I told you,don't change any."
                                        f"\n\nUnder 'Response',you should answer this mental health question:\n{questions[i]}\n,your response to the question should be one in the following list:\n{str(answer_list)}\n"
                                        f"\n\nUnder 'Reason',you should explain why you make this response."
                                        f"\n\n{advice}"
                                        f"\n\nDon't say any other words,don't explain,just give your output as I request."
            }]

            results.append(use_gpt(client,i,len(ms_answer_results),messages,model,max_try,process_gen_result))


    detection_results=results[0]
    for i in range(1,len(results)):
        detection_results.update(results[i])

    return detection_results

def check_gen_result(detection_results,ms_answer_results,posts,questions,answer_list,model,max_try,post_incorrect_index):
    results = []

    for i in trange(len(ms_answer_results),desc="Checking detection results..."):
        if str(i) in post_incorrect_index:

            ms_answer_content=''
            if ms_answer_results[i] == {}:
                ms_answer_content+='(There is no answered questions this time.)'
            else:
                ms_answer_results[i]=sorted(ms_answer_results[i].items(), key=lambda item: int(item[0]))
                for j in range(len(ms_answer_results[i])):
                    ms_answer_content+=ms_answer_results[i][j][1]
                    ms_answer_content+='\n'

            messages=[
            {'role': 'system', 'content': 'You are a psychology tutor, and you are very good at pointing out students\' mistakes.'},
            {'role': 'user', 'content': f"The students majoring in psychology are doing a task of answering some mental health questions based on a post and aom answered questions from a relevant mental health scale."
                                        f"\n\nThis task aims to enhance their ability to carefully analysis the social media post,and answer mental health question for the post."
                                        f"\n\nHowever,some of the students don't do well,they always make the following mistakes:"
                                        f"\n\n1.They always over inference the poster,they are always likely to think the poster has some negative characteristics even there is no information in the post to prove that."
                                        f"\n\n2.Some posts are telling the people around the poster but not the poster himself,the students always make mistake at this time,infer the poster based the people around the poster,this is wrong."
                                        f"\n\nYour task as their teacher is to judge whether they make the mistake of over inference or not,wrongly response the given mental health question."
                                        f"\n\nThe input will be the social media post ,some answered questions from a relevant mental scale that help the students make response,and the response they give to the mental health question.Your output should be your judgement and advice to the students."
                                        f"\n\nThe inputs are as follows:\nPost of ID {i}:\n{posts[i]}\n\nAnswered Questions of a relevant mental scale:\n{ms_answer_content}\n\nThe mental health question:\n{questions[i]}\n(The response to the question should be one in the following list:\n{str(answer_list)})\n\nStudents' answer to the mental health question:\n{detection_results[str(i)][0]+detection_results[str(i)][1]}\n\n"
                                        f"\n\nYour output should be in JSON format with keys are 'ID','Judgement' and 'Advice'."
                                        f"\n\nUnder 'ID',you should just say the post ID as I give to you in the input,don't change any."
                                        f"\n\nUnder 'Judgement',if you think the student's answer is correct,the student doesn't make the mistake of over inference, he correctly answer the mental health question based on the post and the answered questions of a relevant mental scale,show a correct deduction process,then you should say 'Correct' here.Else you should say 'Incorrect' here."
                                        f"\n\nUnder 'Advice',give the students your advice to help them correctly do the task."
                                        f"\n\nPay attention to these mistake,they are easy to make for the psychology students."
                                        f"\n\nDon't say any other words,don't explain,just give your output as I request."
            }]

            results.append(use_gpt(client,i,len(ms_answer_results),messages,model,max_try,process_check_gen_result))

    check_detection_results=results[0]
    for i in range(1,len(results)):
        check_detection_results.update(results[i])

    return check_detection_results


def evaluate(ds,final_detection_results):
    output_label=[]
    golden_label=[]
    for key, value in final_detection_results.items():
        if ds.dataset_name in ['DR', 'dreaddit', 'Irf', 'MultiWD']:
            if 'yes' in value.lower():
                output_label.append(1)
            elif 'no' in value.lower():
                output_label.append(0)
            else:
                raise Exception('Wrong label in predictions for {}'.format(ds.ms_name))

            if 'yes' in ds.labels[int(key)].lower():
                golden_label.append(1)
            elif 'no' in ds.labels[int(key)].lower():
                golden_label.append(0)

        elif ds.dataset_name == 'SAD':
            if 'school' in value.lower():
                output_label.append(0)
            elif 'financial' in value.lower():
                output_label.append(1)
            elif 'family' in value.lower():
                output_label.append(2)
            elif 'social' in value.lower():
                output_label.append(3)
            elif 'work' in value.lower():
                output_label.append(4)
            elif 'health' in value.lower():
                output_label.append(5)
            elif 'emotional' in value.lower():
                output_label.append(6)
            elif 'everyday' in value.lower():
                output_label.append(7)
            elif 'other' in value.lower():
                output_label.append(8)
            else:
                raise Exception('Wrong label in predictions for {}'.format(ds.ms_name))

            if 'school' in ds.labels[int(key)].lower():
                golden_label.append(0)
            elif 'financial problem' in ds.labels[int(key)].lower():
                golden_label.append(1)
            elif 'family issues' in ds.labels[int(key)].lower():
                golden_label.append(2)
            elif 'social relationships' in ds.labels[int(key)].lower():
                golden_label.append(3)
            elif 'work' in ds.labels[int(key)].lower():
                golden_label.append(4)
            elif 'health issues' in ds.labels[int(key)].lower():
                golden_label.append(5)
            elif 'emotion turmoil' in ds.labels[int(key)].lower():
                golden_label.append(6)
            elif 'everyday decision making' in ds.labels[int(key)].lower():
                golden_label.append(7)
            elif 'other' in ds.labels[int(key)].lower():
                golden_label.append(8)

    avg_accuracy = round(accuracy_score(golden_label, output_label) * 100, 2)
    weighted_f1 = round(f1_score(golden_label, output_label, average='weighted') * 100, 2)
    micro_f1 = round(f1_score(golden_label, output_label, average='micro') * 100, 2)
    macro_f1 = round(f1_score(golden_label, output_label, average='macro') * 100, 2)
    return avg_accuracy, weighted_f1, micro_f1,macro_f1


if __name__ == '__main__':
    outputs=[]
    datasets=[('DR','BDI'),('Irf','INQ-15')]
    for dataset in datasets:
        client = OpenAI(
            api_key="Your kwy",
            base_url="Your URL",
            timeout=20
        )
        ds=Data(dataset[0],dataset[1])
        ds.load_data()


        max_try=math.inf
        iter_max=5
        windowsize=2

        ms_answer_results=[]
        ds.posts=ds.posts[2:4]
        for i in range(len(ds.posts)):
            ms_answer_result={}
            incorrect_index=[str(num) for num in range(1,ds.questionnaire_len+1)]
            feedbacks={}
            iter_count=0
            while len(ms_answer_result) < ds.questionnaire_len and iter_count<iter_max:
                scale_content_iter = ds.create_questionnaire(incorrect_index)
                ms_answer=do_ms(client,scale_content_iter,ds.posts[i],'gpt-3.5-turbo',max_try,windowsize,feedbacks)
                sorted_ms_answer = sorted(ms_answer.items(), key=lambda item: int(item[0]))

                for j in range(len(sorted_ms_answer)):
                    sorted_ms_answer[j]=f"Question ID of {sorted_ms_answer[j][0]}: {ds.questionnaire[ds.ms_name][0][sorted_ms_answer[j][0]]}\nAnswer:\nMy post {sorted_ms_answer[j][1][0]} the question,My answer is {sorted_ms_answer[j][1][1]} "


                ms_check=check_ms(sorted_ms_answer,ds.posts[i],'gpt-3.5-turbo',max_try,windowsize)
                sorted_ms_check = sorted(ms_check.items(), key=lambda item: int(item[0]))

                incorrect_index=[]
                feedbacks={}
                for j in range(len(sorted_ms_check)):
                    if sorted_ms_check[j][1][0] == 'Correct':
                        answer_tmp=ms_answer[sorted_ms_check[j][0]][1].split('###',2)
                        answer_tmp=answer_tmp[0]
                        if ms_answer[sorted_ms_check[j][0]][0] == 'not_mention':
                            answer_tmp = 'Don\'t have any problem with this question.'
                        ms_answer_result[sorted_ms_check[j][0]]=f"Question ID of {sorted_ms_check[j][0]}: {ds.questionnaire[ds.ms_name][0][sorted_ms_check[j][0]]}\nAnswer:\n {answer_tmp} "
                    elif sorted_ms_check[j][1][0] == 'Incorrect':
                        incorrect_index.append(sorted_ms_check[j][0])
                        feedbacks[sorted_ms_check[j][0]] = sorted_ms_check[j][1][1]
                    else:
                        print('WRONG ! ! !')
                        print('####\n'+str(sorted_ms_check[j])+'\n####')

                iter_count+=1

            print('TOTAL ITER :' + str(iter_count))
            ms_answer_results.append(ms_answer_result)
            print(f'Finsh post {i}')


        final_detection_results = {}
        post_incorrect_index = [str(num) for num in range(len(ds.posts))]
        post_advices = {}
        iter_count = 0
        while len(final_detection_results) < len(ds.posts) and iter_count<iter_max:
            detection_results = gen_result(copy.deepcopy(ms_answer_results), ds.posts,ds.questions,ds.answers[ds.dataset_name],'gpt-3.5-turbo', max_try,post_incorrect_index,post_advices)
            check_detection_results = check_gen_result(detection_results,copy.deepcopy(ms_answer_results), ds.posts,ds.questions,ds.answers[ds.dataset_name],'gpt-3.5-turbo', max_try,post_incorrect_index)
            sorted_check_detection_results = sorted(check_detection_results.items(), key=lambda item: int(item[0]))

            post_incorrect_index = []
            post_advices = {}
            for i in range(len(sorted_check_detection_results)):
                if sorted_check_detection_results[i][1][0] == 'Correct':
                    final_detection_results[sorted_check_detection_results[i][0]]=detection_results[sorted_check_detection_results[i][0]][0]
                elif sorted_check_detection_results[i][1][0] == 'Incorrect':
                    post_incorrect_index.append(sorted_check_detection_results[i][0])
                    post_advices[sorted_check_detection_results[i][0]] = sorted_check_detection_results[i][1][1]
                else:
                    print('WRONG ! ! !')
                    print('####\n' + str(sorted_check_detection_results[i]) + '\n####')
            iter_count +=1

        print('TOTAL ITER :' + str(iter_count))
        avg_accuracy, weighted_f1, micro_f1,macro_f1 = evaluate(ds, final_detection_results)
        print("Dataset: {}, average acc:{}, weighted F1 {}, micro F1 {}, macro F1 {}".format(ds.dataset_name,
                                                                                             avg_accuracy, weighted_f1,
                                                                                             micro_f1, macro_f1))
        outputs.append("Dataset: {}, average acc:{}, weighted F1 {}, micro F1 {}, macro F1 {}".format(ds.dataset_name,
                                                                                             avg_accuracy, weighted_f1,
                                                                                             micro_f1, macro_f1))
    with open('output.txt','w+',encoding='utf-8') as file:
        for item in outputs:
            file.write(item+'\n')
