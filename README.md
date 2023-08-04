### Config an environment

```
virtualenv -p python3 .env
source .env/bin/activate
cd ask-chatgpt

pip install selenium click
```

### Prepare the questions

- Create a file named questions.json in your current directory.
- Add the questions in the file, one question per a dictionary which contains two keys: "question" and "input". Please notice that the "input" key is optional. If you don't provide it, the script will use the "question" key only.

```
[
    {
        "question": "What is your name?",
        "input": "My name is John."
    },
    {
        "question": "What is your age?"
    }
]
```

We will render the question as the following format:

```
{question}\n{input if input else ""}
```

If you want to support more complex prompt, please modify the `gen_default_template` function.

### Run the script

You need to launch another chrome instance with the --remote-debugging-port=9222 flag. The instance contains all the cookies and login information. So you can keep your login information in the browser and use it in the webdriver instance.

If you use macOS, you can use the following command to launch another chrome instance:

```
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
```

NOTICE: You need to close all other chrome instances before launching the new one.
If you launch chrome successfully, you can see the following message:
DevTools listening on ws://127.0.0.1:9222/devtools/browser/ef03fa20-25f2-4c27-ac46-d56403301a40

```
python3 ask_chatgpt_by_selenium.py --question-file questions.json --output-file answers.json --steps 1 --sleep 60
```