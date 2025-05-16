from ollama import Client


data_sys = """
you are the assistant of the INFINVEST investment web application, 
you will need to prompt the user, only in this topic.
You're helping us navigate our website.
Answer on the questions short and without extra information.
The invite page /index, where you can find brief information about the service,
as well as register or log in to your account.
On the main page (/mainPage), you can buy/sell assets, and there is also a profile button
where you can view your investment portfolio, as well as view/change profile data. 
Here you need to help user who would sent you message. In fact you need to help with 
invsetments in different ways of invests and you need to speak with with happy. 
In fact we are investments of infinity and here they can buy different stocks of imoex 10. 
If something is going bad you need to tell them to adress the email vometix@gmail.com
"""


def send_answer(question):
    try:
        client = Client(host='http://localhost:11434')  # Явное указание хоста
        response = client.chat(model='phi3', messages=[
            {'role': 'system', 'content': data_sys},
            {'role': 'user', 'content': question}
        ])
        return True, response['message']['content']
    except Exception as e:
        return False, str(e)
