do_mental_scale = [
    {'role': 'system',
     'content': 'You are a psychology expertise,you are familiar with all kinds of people,you are good at role playing someone just based on some of his/her text.'},
    {'role': 'user',
     'content': "Your task is to read a post on social media,then judge whether the post mention some questions from mental scales and act as the poster to answer these questions."
                "\nI will give you a post of the poster and some questions,you should output the judgement ,answers and the reason to your answers."
                "\nThe inputs are as follows:\nPost:\n{post}\n\nQuestions:\n{scale}\n\n"
                "\nYour output should be a list of JSON objects for each question in order,each with keys are 'Judgement','Answer' and 'Reason',one example of the format is:[{'{'}\"Judgement\":\"\",\"Answer\":\"\",\"Reason\":\"\"'{'}'}{'{'}\"Judgement\":\"\",\"Answer\":\"\",\"Reason\":\"\"'{'}'}]"
                "\n\nUnder 'Judgement',if you think the post directly mention the question,show the answer of the question, you should say 'directly_mention'.Else if you think the post indirectly mention the question,but it contains some information that you can use your knowledge of a psychology expertise to make proper deduction from the information and answer the question,you should say 'indirectly_mention'.Else you think the post doesn't mention the question at all and doesn't have any information that can help you deduce the answer,you should say 'not_mention'."
                "\n\nUnder 'Answer',if you say 'directly_mention' or 'indirectly_mention' in the content of 'Judgement',you should just say your answer to the question here. Else if you say 'not_mention' in the content of 'Judgement',you should say 'Doesn't mention at all.' here.You answer should be in the first person."
                "\n\nUnder 'Reason',give a short and concise reason for your answer, but you should explain your answer thoroughly.You reason should be in the first person."
                "\n\nPay attention that you should totally base on the post to act as the poster to answer the questions.Don't make ANY deduction by yourself,you must base on the information from the post."
                "\n\n{criteria}"
                "\n\nDon't say any other words,don't explain,just give your output of a JSON list as I request."}]

check_mental_scale=[
        {'role': 'system', 'content': 'You are a psychology tutor, and you are very good at pointing out students\' mistakes.'},
        {'role': 'user', 'content': "The students majoring in psychology are doing a task of reading someone's post on sociel media and act as the poster to answer some questions from mental scales,they are asked to answer the question just base on the post."
                                    "\n\nThis task aims to enhance their ability to carefully analysis the social media post,and to use the knowledge of psychology to act as the poster."
                                    "\n\nHowever,some of the students don't do well,they always make the following mistakes:"
                                    "\n\n1.They always thought the post doesn't contain any information of the question,the students always lack of carefully analysis and just thought the post doesn't mention the question at all."
                                    "\n\n2.They always over inference the poster,they are always likely to think the poster has some negative characteristics even there is no information in the post to prove that."
                                    "\n\n3.Some posts are telling the people around the poster but not the poster himself,the students always make mistake at this time,infer the poster based the people around the poster,this is wrong."
                                    "\n\nYour task as their teacher is to judge whether they do a good role playing of the poster or not,whether they make the above mistakes."
                                    "\n\nThe input will be the social media post of the poster ,some questions from mental scale and the answer they made acting as the poster.Your output should be your judgement and advice to the students."
                                    "\n\nThe inputs are as follows:\nPost:\n{post}\n\nQuestions and Students' answers:\n{scale}\n\n"
                                    "\n\nYour output should be a list of JSON objects for each question in order,each with keys are 'Judgement' and 'Advice',one example of the format is:[{'{'},\"Judgement\":\"\",\"Advice\":\"\"'{'}'}{'{'}\"Judgement\":\"\",\"Advice\":\"\"'{'}'}]"
                                    "\n\nUnder 'Judgement',if you think the student's answer is correct,the student doesn't make these mistakes, he correctly play the role of the poster, properly answer the question based on the post and show a correct deduction process,you should say 'Correct' here.Else you should say 'Incorrect' here."
                                    "\n\nUnder 'Advice',give the students your advice to help them correctly do the task."
                                    "\n\nPay attention to these mistake,they are easy to make for the psychology students."
                                    "\n\nPay attention to that your advice should against the students' answer,you can't just talk and unrealistic."
                                    "\n\nPay attention to that your advice should be consistent with your judgement,they should align to each other."
                                    "\n\nDon't say any other words,don't explain,just give your output as I request."}]

mental_health_analysis=[
    {'role': 'system', 'content': 'You are a psychology expertise,you are familiar with all the mental health problem and you are good at recognize them.'},
    {'role': 'user', 'content': "Your task is to recognize the poster's mental health problem and give response to a mental health question as I request below."
                                "\n\nI will give you a post of a poster,some question-answer pairs to the questions of a relevant mental scale done by the poster that help you better give response,you should follow my instruction to analyse the poster's mental health."
                                "\n\nThere sre some examples for you to better understand the task and do your analysis."#\n{fs_content}\n
                                "\n\nThe inputs are as follows:\n"
                                "\n\nPost:\n{post}\n\nAnswered Questions of mental scale:\n{ms_answer_content}\n\n"
                                "\n\nYour output should be in JSON format with keys are 'Response' and 'Reason'"
                                "\n\nUnder 'Response',you should answer this mental health question:\n{question}\n,your response to the question should be one in the following list:\n{str(answer_list)}\n"
                                "\n\nUnder 'Reason',you should explain why you make this response."
                                "\n\n{advice}"
                                "\n\nDon't say any other words,don't explain,just give your output as I request."
    }]

check_mental_health_analysis=[
    {'role': 'system', 'content': 'You are a psychology tutor, and you are very good at pointing out students\' mistakes.'},
    {'role': 'user', 'content': "The students majoring in psychology are doing a task of analysing mental health based on a post and some answered questions from a relevant mental health scale."
                                "\n\nThis task aims to enhance their ability to carefully analysis the poster's mental health problem."
                                "\n\nThere sre some examples for you to better understand the task."#\n{fs_content}\n
                                "\n\nHowever,some of the students don't do well,they always make the following mistakes:"
                                "\n\n1.They always over inference the poster,they are always likely to think the poster has some negative characteristics even there is no information in the post to prove that."
                                "\n\n2.Some posts are telling the people around the poster but not the poster himself,the students always make mistake at this time,wrongly thought the mental health of the people around the poster to be the poster's mental health situation."
                                "\n\nYour task as their teacher is to judge whether they make the above mistakes or not,wrongly response the given mental health question."
                                "\n\nThe input will be the social media post ,some answered questions from a relevant mental scale that help the students make response,and the response they give to the mental health question.Your output should be your judgement and advice to the students."
                                "\n\nThe inputs are as follows:\nPost :\n{post}\n\nAnswered Questions of a relevant mental scale:\n{ms_answer_content}\n\nThe mental health question:\n{question}\n(The response to the question should be one in the following list:\n{str(answer_list)})\n\nStudents' answer to the mental health question:\n{detection_result[1]+detection_result[2]}\n\n"
                                "\n\nYour output should be in JSON format with keys are 'Judgement' and 'Advice'."
                                "\n\nUnder 'Judgement',if you think the student's answer is correct,the student doesn't make the mistakes , he correctly answer the mental health question based on the post and the answered questions of a relevant mental scale,show a correct deduction process,then you should say 'Correct' here.Else you should say 'Incorrect' here."
                                "\n\nUnder 'Advice',give the students your advice to help them correctly do the task."
                                "\n\nPay attention to these mistake,they are easy to make for the psychology students."
                                "\n\nPay attention to that your advice should against the students' answer,you can't just talk and unrealistic."
                                "\n\nPay attention to that your advice should be consistent with your judgement,they should align to each other."
                                "\n\nDon't say any other words,don't explain,just give your output as I request."
    }]



