import os
import re
import click
import time
import json
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def gen_default_template(question, input):
    return f"""{question}\n{input if input else ""}"""


def chatgpt(input, sleep_seconds=60, use_chatgpt4=False) -> str:
    # Start a webdriver instance and open ChatGPT
    chrome_options = Options()
    # You need to launch another chrome instance with the --remote-debugging-port=9222 flag. The instance contains all the cookies and login information. So you can keep your login information in the browser and use it in the webdriver instance.
    # If you use macOS, you can use the following command to launch another chrome instance:
    # /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
    # NOTICE: You need to close all other chrome instances before launching the new one.
    # If you launch chrome successfully, you can see the following message:
    # DevTools listening on ws://127.0.0.1:9222/devtools/browser/ef03fa20-25f2-4c27-ac46-d56403301a40
    chrome_options.debugger_address = "localhost:9222"
    driver = webdriver.Chrome(options=chrome_options)
    # driver.maximize_window()
    if use_chatgpt4:
        url = 'https://chat.openai.com/?model=gpt-4'
    else:
        url = "https://chat.openai.com/"
    driver.get(url)

    # Wait for the page to load
    driver.implicitly_wait(sleep_seconds)

    # Find the input field and send a question
    input_field = driver.find_element(By.ID, 'prompt-textarea')
    print("HTML Element: %s" % input_field.get_attribute('outerHTML'))
    input = re.sub(r'\n', "<br/>", input)
    input_field.clear()
    input_field.send_keys(input)
    print("Send keys to input field")

    time.sleep(sleep_seconds)
    input_field.send_keys(Keys.RETURN)

    print("Wait for response")
    time.sleep(sleep_seconds)

    # Find the response and save it to a file
    responses = driver.find_elements(By.CLASS_NAME, 'markdown')
    # Get the last response
    result = responses[-1].text
    print("Output:\n%s" % result)

    # Close the webdriver instance
    # driver.quit()

    return result

@dataclass
class Question:
    question: str
    input: Optional[str] = None


def get_instructions(
    questions: List[Question],
    sleep=15,
    steps=3,
    answer_file="answers.json",
    template_fn=gen_default_template,
    use_chatgpt4=False,
):
    if os.path.exists(answer_file):
        with open(answer_file, "r") as f:
            responses = json.loads(f.read())
            current_questions = [r["question"].strip() for r in responses]
    else:
        responses = []
        current_questions = []

    for i, question in enumerate(questions):
        question_str = question.question.strip()
        if question_str in current_questions:
            print(f'Skipping {i} question "{question_str}". Already answered.\n')
            continue
        else:
            print(f'Asking {i} question \n "{question_str}" with input \n "{question.input}"')
            input = question.input.strip() if question.input else ""

            question = template_fn(question_str, input)

            response = chatgpt(question, sleep_seconds=sleep, use_chatgpt4=use_chatgpt4)
            responses.append({"question": question, "answer": response})
            print(f"Q: {question}\nA: {response}\n")

        if (i + 1) % steps == 0:
            with open(f"answers.json", "w") as f:
                f.write(json.dumps(responses))

    return responses


@click.command()
@click.option(
    "--question-file",
    default="questions.json",
    help='File containing questions to ask GPT-4, default questions.json. Each question should be a dictionary with a "question" key and a "input" key if you want to provide a custom input prompt.',
)
@click.option(
    "--output-file",
    default="answers.json",
    help="File to write answers to, default answers.json",
)
@click.option(
    "--steps", default=1, help="Number of steps to save in the output file, default 10"
)
@click.option(
    "--sleep", default=30, help="Seconds to sleep between questions, default 30. If you encounter rate limiting or cannot get a response, try increasing this."
)
@click.option(
    "--use-chatgpt4", default=False, help="Use ChatGPT-4 instead of ChatGPT-3.5", is_flag=True
)
def main(question_file, output_file, steps, sleep, use_chatgpt4):
    if not os.path.exists(question_file):
        raise Exception(
            f"Question file {question_file} does not exist, please create it or specify a different file with --question-file."
        )

    with open(question_file, "r") as f:
        questions = json.loads(f.read())
        questions = [Question(**q) for q in questions]

    responses = get_instructions(
        questions, steps=steps, sleep=sleep, answer_file=output_file, use_chatgpt4=use_chatgpt4
    )
    with open(output_file, "w") as f:
        f.write(json.dumps(responses))


if __name__ == "__main__":
    main()
