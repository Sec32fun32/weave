"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[9926],{19016:(e,n,t)=>{t.r(n),t.d(n,{assets:()=>l,contentTitle:()=>o,default:()=>p,frontMatter:()=>a,metadata:()=>s,toc:()=>d});var r=t(85893),i=t(11151);const a={title:"Handling and Redacting PII"},o="How to use Weave with PII data:",s={id:"reference/gen_notebooks/pii",title:"Handling and Redacting PII",description:"Open in Colab",source:"@site/docs/reference/gen_notebooks/pii.md",sourceDirName:"reference/gen_notebooks",slug:"/reference/gen_notebooks/pii",permalink:"/reference/gen_notebooks/pii",draft:!1,unlisted:!1,editUrl:"https://github.com/wandb/weave/blob/master/docs/docs/reference/gen_notebooks/pii.md",tags:[],version:"current",lastUpdatedAt:172710544e4,frontMatter:{title:"Handling and Redacting PII"},sidebar:"notebookSidebar",previous:{title:"Log Calls from Existing CSV",permalink:"/reference/gen_notebooks/import_from_csv"}},l={},d=[{value:"During Testing",id:"during-testing",level:2},{value:"In Production",id:"in-production",level:2},{value:"Encryption Tips",id:"encryption-tips",level:2}];function c(e){const n={a:"a",admonition:"admonition",code:"code",h1:"h1",h2:"h2",img:"img",li:"li",ol:"ol",p:"p",pre:"pre",ul:"ul",...(0,i.a)(),...e.components},{Details:a}=n;return a||function(e,n){throw new Error("Expected "+(n?"component":"object")+" `"+e+"` to be defined: you likely forgot to import, pass, or provide it.")}("Details",!0),(0,r.jsxs)(r.Fragment,{children:[(0,r.jsxs)(n.admonition,{title:"This is a notebook",type:"tip",children:[(0,r.jsx)("a",{href:"https://colab.research.google.com/github/wandb/weave/blob/master/docs/./notebooks/pii.ipynb",target:"_blank",rel:"noopener noreferrer",class:"navbar__item navbar__link button button--secondary button--med margin-right--sm notebook-cta-button",children:(0,r.jsxs)("div",{children:[(0,r.jsx)("img",{src:"https://upload.wikimedia.org/wikipedia/commons/archive/d/d0/20221103151430%21Google_Colaboratory_SVG_Logo.svg",alt:"Open In Colab",height:"20px"}),(0,r.jsx)("div",{children:"Open in Colab"})]})}),(0,r.jsx)("a",{href:"https://github.com/wandb/weave/blob/master/docs/./notebooks/pii.ipynb",target:"_blank",rel:"noopener noreferrer",class:"navbar__item navbar__link button button--secondary button--med margin-right--sm notebook-cta-button",children:(0,r.jsxs)("div",{children:[(0,r.jsx)("img",{src:"https://upload.wikimedia.org/wikipedia/commons/9/91/Octicons-mark-github.svg",alt:"View in Github",height:"15px"}),(0,r.jsx)("div",{children:"View in Github"})]})})]}),"\n",(0,r.jsx)("img",{src:"http://wandb.me/logo-im-png",width:"400",alt:"Weights & Biases"}),"\n",(0,r.jsx)(n.h1,{id:"how-to-use-weave-with-pii-data",children:"How to use Weave with PII data:"}),"\n",(0,r.jsx)(n.p,{children:"In this tutorial, we'll demonstrate how to utilize Weave while preventing your Personally Identifiable Information (PII) data from being incorporated into Weave or the LLMs you employ."}),"\n",(0,r.jsxs)(n.p,{children:["To protect our PII data, we'll employ a couple techniques. First, we'll use regular expressions to identify PII data and redact it. Second, we'll use Microsoft's ",(0,r.jsx)(n.a,{href:"https://microsoft.github.io/presidio/",children:"Presidio"}),", a python-based data protection SDK. This tool provides redaction and replacement functionalities, both of which we will implement in this tutorial."]}),"\n",(0,r.jsxs)(n.p,{children:["For this use-case. We will leverage Anthropic's Claude Sonnet to perform sentiment analysis. While we use Weave's ",(0,r.jsx)(n.a,{href:"https://wandb.github.io/weave/quickstart",children:"Traces"})," to track and analize the LLM's API calls. Sonnet will receive a block of text and output one of the following sentiment classifications:"]}),"\n",(0,r.jsxs)(n.ol,{children:["\n",(0,r.jsx)(n.li,{children:"positive"}),"\n",(0,r.jsx)(n.li,{children:"negative"}),"\n",(0,r.jsx)(n.li,{children:"neutral"}),"\n"]}),"\n",(0,r.jsx)(n.pre,{children:(0,r.jsx)(n.code,{className:"language-python",children:"%%capture\n# @title required python packages:\n!pip install presidio_analyzer\n!pip install presidio_anonymizer\n!python -m spacy download en_core_web_lg # Presidio uses spacy NLP engine\n!pip install Faker                       # we'll use Faker to replace PII data with fake data\n!pip install weave                        # To leverage Traces\n!pip install set-env-colab-kaggle-dotenv -q # for env var\n!pip install anthropic                      # to use sonnet\n!pip install cryptography                   # to encrypt our data\n"})}),"\n",(0,r.jsx)(n.h1,{id:"setup",children:"Setup"}),"\n",(0,r.jsx)(n.pre,{children:(0,r.jsx)(n.code,{className:"language-python",children:'# @title Make sure to set up set up your API keys correctly\nfrom set_env import set_env\n\n_ = set_env("ANTHROPIC_API_KEY")\n_ = set_env("WANDB_API_KEY")\n'})}),"\n",(0,r.jsx)(n.pre,{children:(0,r.jsx)(n.code,{className:"language-python",children:'import weave\n\nWEAVE_PROJECT = "pii_cookbook"\nweave.init(WEAVE_PROJECT)\n'})}),"\n",(0,r.jsx)(n.p,{children:"Let's load our initial PII data. For demonstration purposes, we'll use a dataset containing 10 text blocks. A larger dataset with 1000 entries is available."}),"\n",(0,r.jsx)(n.pre,{children:(0,r.jsx)(n.code,{className:"language-python",children:'import requests\n\nurl = "https://raw.githubusercontent.com/wandb/weave/master/docs/notebooks/10_pii_data.json"\nresponse = requests.get(url)\npii_data = response.json()\n'})}),"\n",(0,r.jsx)(n.h1,{id:"using-weave-safely-with-pii-data",children:"Using Weave Safely with PII Data"}),"\n",(0,r.jsx)(n.h2,{id:"during-testing",children:"During Testing"}),"\n",(0,r.jsxs)(n.ul,{children:["\n",(0,r.jsx)(n.li,{children:"Log anonymized data to check PII detection"}),"\n",(0,r.jsx)(n.li,{children:"Track PII handling processes with Weave traces"}),"\n",(0,r.jsx)(n.li,{children:"Measure anonymization performance without exposing real PII"}),"\n"]}),"\n",(0,r.jsx)(n.h2,{id:"in-production",children:"In Production"}),"\n",(0,r.jsxs)(n.ul,{children:["\n",(0,r.jsx)(n.li,{children:"Never log raw PII"}),"\n",(0,r.jsx)(n.li,{children:"Encrypt sensitive fields before logging"}),"\n"]}),"\n",(0,r.jsx)(n.h2,{id:"encryption-tips",children:"Encryption Tips"}),"\n",(0,r.jsxs)(n.ul,{children:["\n",(0,r.jsx)(n.li,{children:"Use reversible encryption for data you need to decrypt later"}),"\n",(0,r.jsx)(n.li,{children:"Apply one-way hashing for unique IDs you don't need to reverse"}),"\n",(0,r.jsx)(n.li,{children:"Consider specialized encryption for data you need to analyze while encrypted"}),"\n"]}),"\n",(0,r.jsx)(n.h1,{id:"method-1",children:"Method 1:"}),"\n",(0,r.jsxs)(n.p,{children:["Our initial method is to use ",(0,r.jsx)(n.a,{href:"https://docs.python.org/3/library/re.html",children:"regular expressions (regex)"})," to identify PII data and redact it. It allows us to define patterns that can match various formats of sensitive information like phone numbers, email addresses, and social security numbers. By using regex, we can scan through large volumes of text and replace or redact information without the need for more complex NLP techniques."]}),"\n",(0,r.jsx)(n.pre,{children:(0,r.jsx)(n.code,{className:"language-python",children:'import re\n\n\ndef clean_pii_with_regex(text):\n    # Phone number pattern\n    # \\b         : Word boundary\n    # \\d{3}      : Exactly 3 digits\n    # [-.]?      : Optional hyphen or dot\n    # \\d{3}      : Another 3 digits\n    # [-.]?      : Optional hyphen or dot\n    # \\d{4}      : Exactly 4 digits\n    # \\b         : Word boundary\n    text = re.sub(r"\\b\\d{3}[-.]?\\d{3}[-.]?\\d{4}\\b", "<PHONE>", text)\n\n    # Email pattern\n    # \\b         : Word boundary\n    # [A-Za-z0-9._%+-]+ : One or more characters that can be in an email username\n    # @          : Literal @ symbol\n    # [A-Za-z0-9.-]+ : One or more characters that can be in a domain name\n    # \\.         : Literal dot\n    # [A-Z|a-z]{2,} : Two or more uppercase or lowercase letters (TLD)\n    # \\b         : Word boundary\n    text = re.sub(\n        r"\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b", "<EMAIL>", text\n    )\n\n    # SSN pattern\n    # \\b         : Word boundary\n    # \\d{3}      : Exactly 3 digits\n    # -          : Literal hyphen\n    # \\d{2}      : Exactly 2 digits\n    # -          : Literal hyphen\n    # \\d{4}      : Exactly 4 digits\n    # \\b         : Word boundary\n    text = re.sub(r"\\b\\d{3}-\\d{2}-\\d{4}\\b", "<SSN>", text)\n\n    # Simple name pattern (this is not comprehensive)\n    # \\b         : Word boundary\n    # [A-Z]      : One uppercase letter\n    # [a-z]+     : One or more lowercase letters\n    # \\s         : One whitespace character\n    # [A-Z]      : One uppercase letter\n    # [a-z]+     : One or more lowercase letters\n    # \\b         : Word boundary\n    text = re.sub(r"\\b[A-Z][a-z]+ [A-Z][a-z]+\\b", "<NAME>", text)\n\n    return text\n\n\n# Test the function\ntest_text = "My name is John Doe, my email is john.doe@example.com, my phone is 123-456-7890, and my SSN is 123-45-6789."\ncleaned_text = clean_pii_with_regex(test_text)\nprint(cleaned_text)\n'})}),"\n",(0,r.jsx)(n.h1,{id:"method-2-microsoft-presidio",children:"Method 2: Microsoft Presidio"}),"\n",(0,r.jsxs)(n.p,{children:["In this example, we'll create a ",(0,r.jsx)(n.a,{href:"https://wandb.github.io/weave/guides/core-types/models",children:"Weave Model"})," which is a combination of data (which can include configuration, trained model weights, or other information) and code that defines how the model operates.\nIn this model, we will include our predict function where the Anthropic API will be called."]}),"\n",(0,r.jsx)(n.p,{children:"Once you run this code you will receive a link to the Weave project page"}),"\n",(0,r.jsx)(n.pre,{children:(0,r.jsx)(n.code,{className:"language-python",children:'import json\n\nfrom anthropic import AsyncAnthropic\n\nimport weave\n\n\n# Weave model / predict function\nclass sentiment_analysis_model(weave.Model):\n    model_name: str\n    system_prompt: str\n    temperature: int\n\n    @weave.op()\n    async def predict(self, text_block: str) -> dict:\n        client = AsyncAnthropic()\n\n        response = await client.messages.create(\n            max_tokens=1024,\n            model=self.model_name,\n            system=self.system_prompt,\n            messages=[\n                {"role": "user", "content": [{"type": "text", "text": text_block}]}\n            ],\n        )\n        result = response.content[0].text\n        if result is None:\n            raise ValueError("No response from model")\n        parsed = json.loads(result)\n        return parsed\n\n    # create our LLM model with a system prompt\n\n\nmodel = sentiment_analysis_model(\n    name="claude-3-sonnet",\n    model_name="claude-3-5-sonnet-20240620",\n    system_prompt=\'You are a Sentiment Analysis classifier. You will be classifying text based on their sentiment. Your input will be a block of text. You will answer with one the following rating option["positive", "negative", "neutral"]. Your answer should be one word in json format: {classification}. Ensure that it is valid JSON.\',\n    temperature=0,\n)\n'})}),"\n",(0,r.jsx)(n.h1,{id:"method-2a",children:"Method 2A:"}),"\n",(0,r.jsx)(n.p,{children:"Our next method involves complete removal of PII data using Presidio. This approach redacts PII and replaces it with a placeholder representing the PII type. For example:"}),"\n",(0,r.jsx)(n.pre,{children:(0,r.jsx)(n.code,{children:' "My name is Alex"\n'})}),"\n",(0,r.jsx)(n.p,{children:"Will be:"}),"\n",(0,r.jsx)(n.pre,{children:(0,r.jsx)(n.code,{children:' "My name is <PERSON>"\n'})}),"\n",(0,r.jsxs)(n.p,{children:["Presidio comes with a built-in ",(0,r.jsx)(n.a,{href:"https://microsoft.github.io/presidio/supported_entities/",children:"list of recognizable entities"}),". We can select the ones that are important for our use case. In the below example, we are only looking at redicating names and phone numbers from our text:"]}),"\n",(0,r.jsx)(n.p,{children:(0,r.jsx)(n.img,{src:t(37065).Z+"",width:"3024",height:"1890"})}),"\n",(0,r.jsx)(n.pre,{children:(0,r.jsx)(n.code,{className:"language-python",children:'from presidio_analyzer import AnalyzerEngine\nfrom presidio_anonymizer import AnonymizerEngine\n\ntext = "My phone number is 212-555-5555 and my name is alex"\n\n# Set up the engine, loads the NLP module (spaCy model by default)\n# and other PII recognizers\nanalyzer = AnalyzerEngine()\n\n# Call analyzer to get results\nresults = analyzer.analyze(\n    text=text, entities=["PHONE_NUMBER", "PERSON"], language="en"\n)\n\n# Analyzer results are passed to the AnonymizerEngine for anonymization\n\nanonymizer = AnonymizerEngine()\n\nanonymized_text = anonymizer.anonymize(text=text, analyzer_results=results)\n\nprint(anonymized_text)\n'})}),"\n",(0,r.jsx)(n.p,{children:"Let's encapsulate the previous step into a function and expand the entity recognition capabilities. We will expand our redaction scope to include addresses, email addresses, and US Social Security numbers."}),"\n",(0,r.jsx)(n.pre,{children:(0,r.jsx)(n.code,{className:"language-python",children:'from presidio_analyzer import AnalyzerEngine\nfrom presidio_anonymizer import AnonymizerEngine\n\nanalyzer = AnalyzerEngine()\nanonymizer = AnonymizerEngine()\n"""\nThe below function will take a block of text, process it using presidio\nand return a block of text with the PII data redicated.\nPII data to be redicated:\n- Phone Numbers\n- Names\n- Addresses\n- Email addresses\n- US Social Security Numbers\n"""\n\n\ndef anonymize_my_text(text):\n    results = analyzer.analyze(\n        text=text,\n        entities=["PHONE_NUMBER", "PERSON", "LOCATION", "EMAIL_ADDRESS", "US_SSN"],\n        language="en",\n    )\n    anonymized_text = anonymizer.anonymize(text=text, analyzer_results=results)\n    return anonymized_text.text\n'})}),"\n",(0,r.jsx)(n.pre,{children:(0,r.jsx)(n.code,{className:"language-python",children:'# for every block of text, anonymized first and then predict\nfor entry in pii_data:\n    anonymized_entry = anonymize_my_text(entry["text"])\n    (await model.predict(anonymized_entry))\n'})}),"\n",(0,r.jsx)(n.h1,{id:"method-2b-replace-pii-data-with-fake-data",children:"Method 2B: Replace PII data with fake data"}),"\n",(0,r.jsxs)(n.p,{children:["Instead of redacting text, we can anonymize it by swapping PII (like names and phone numbers) with fake data generated using the ",(0,r.jsx)(n.a,{href:"https://faker.readthedocs.io/en/master/",children:"Faker"})," Python library. For example:"]}),"\n",(0,r.jsx)(n.pre,{children:(0,r.jsx)(n.code,{children:'"My name is Raphael and I like to fish. My phone number is 212-555-5555"\n'})}),"\n",(0,r.jsx)(n.p,{children:"Will be:"}),"\n",(0,r.jsx)(n.pre,{children:(0,r.jsx)(n.code,{children:'"My name is Katherine Dixon and I like to fish. My phone number is 667.431.7379"\n\n'})}),"\n",(0,r.jsx)(n.p,{children:"To effectively utilize Presidio, we must supply references to our custom operators. These operators will direct Presidio to the functions responsible for swapping PII with fake data."}),"\n",(0,r.jsx)(n.p,{children:(0,r.jsx)(n.img,{src:t(4627).Z+"",width:"3024",height:"1900"})}),"\n",(0,r.jsx)(n.pre,{children:(0,r.jsx)(n.code,{className:"language-python",children:'from faker import Faker\nfrom presidio_anonymizer import AnonymizerEngine\nfrom presidio_anonymizer.entities import OperatorConfig\n\nfake = Faker()\n\n\n# Create faker functions (note that it has to receive a value)\ndef fake_name(x):\n    return fake.name()\n\n\ndef fake_number(x):\n    return fake.phone_number()\n\n\n# Create custom operator for the PERSON and PHONE_NUMBER" entities\noperators = {\n    "PERSON": OperatorConfig("custom", {"lambda": fake_name}),\n    "PHONE_NUMBER": OperatorConfig("custom", {"lambda": fake_number}),\n}\n\n\ntext_to_anonymize = (\n    "My name is Raphael and I like to fish. My phone number is 212-555-5555"\n)\n\n# Analyzer output\nanalyzer_results = analyzer.analyze(\n    text=text_to_anonymize, entities=["PHONE_NUMBER", "PERSON"], language="en"\n)\n\n\nanonymizer = AnonymizerEngine()\n\n# do not forget to pass the operators from above to the anonymizer\nanonymized_results = anonymizer.anonymize(\n    text=text_to_anonymize, analyzer_results=analyzer_results, operators=operators\n)\n\nprint(anonymized_results.text)\n'})}),"\n",(0,r.jsx)(n.p,{children:"Let's consolidate our code into a single class and expand the list of entities to include the additional ones we identified earlier."}),"\n",(0,r.jsx)(n.pre,{children:(0,r.jsx)(n.code,{className:"language-python",children:'from anthropic import AsyncAnthropic\nfrom faker import Faker\nfrom presidio_anonymizer import AnonymizerEngine\nfrom presidio_anonymizer.entities import OperatorConfig\n\nimport weave\n\n\n# Let\'s build a custom class for generating fake data that will extend Faker\nclass my_faker(Faker):\n    # Create faker functions (note that it has to receive a value)\n    def fake_address(x):\n        return fake.address()\n\n    def fake_ssn(x):\n        return fake.ssn()\n\n    def fake_name(x):\n        return fake.name()\n\n    def fake_number(x):\n        return fake.phone_number()\n\n    def fake_email(x):\n        return fake.email()\n\n    # Create custom operators for the entities\n    operators = {\n        "PERSON": OperatorConfig("custom", {"lambda": fake_name}),\n        "PHONE_NUMBER": OperatorConfig("custom", {"lambda": fake_number}),\n        "EMAIL_ADDRESS": OperatorConfig("custom", {"lambda": fake_email}),\n        "LOCATION": OperatorConfig("custom", {"lambda": fake_address}),\n        "US_SSN": OperatorConfig("custom", {"lambda": fake_ssn}),\n    }\n\n    def anonymize_my_text(self, text):\n        anonymizer = AnonymizerEngine()\n        analyzer_results = analyzer.analyze(\n            text=text,\n            entities=["PHONE_NUMBER", "PERSON", "LOCATION", "EMAIL_ADDRESS", "US_SSN"],\n            language="en",\n        )\n        anonymized_results = anonymizer.anonymize(\n            text=text, analyzer_results=analyzer_results, operators=self.operators\n        )\n        return anonymized_results.text\n\n\nfaker = my_faker()\nfor entry in pii_data:\n    anonymized_entry = faker.anonymize_my_text(entry["text"])\n    (await model.predict(anonymized_entry))\n'})}),"\n",(0,r.jsxs)(a,{children:[(0,r.jsx)("summary",{children:" (Optional) Encrypting our data "}),(0,r.jsx)(n.p,{children:(0,r.jsx)(n.img,{src:t(73484).Z+"",width:"3024",height:"1890"})}),(0,r.jsxs)(n.p,{children:["In addition to anonymizing PII, we can add an extra layer of security by encrypting our data using the cryptography library's ",(0,r.jsx)(n.a,{href:"https://cryptography.io/en/latest/fernet/",children:"Fernet"})," symmetric encryption. This approach ensures that even if the anonymized data is intercepted, it remains unreadable without the encryption key."]}),(0,r.jsx)(n.pre,{children:(0,r.jsx)(n.code,{className:"language-python",children:'import os\nfrom cryptography.fernet import Fernet\nfrom pydantic import BaseModel, ValidationInfo, model_validator\n\ndef get_fernet_key():\n    # Check if the key exists in environment variables\n    key = os.environ.get(\'FERNET_KEY\')\n    \n    if key is None:\n        # If the key doesn\'t exist, generate a new one\n        key = Fernet.generate_key()\n        # Save the key to an environment variable\n        os.environ[\'FERNET_KEY\'] = key.decode()\n    else:\n        # If the key exists, ensure it\'s in bytes\n        key = key.encode()\n    \n    return key\n\ncipher_suite = Fernet(get_fernet_key())\n\nclass EncryptedSentimentAnalysisInput(BaseModel):\n    encrypted_text: str = None\n\n    @model_validator(mode="before")\n    def encrypt_fields(cls, values):\n        if "text" in values and values["text"] is not None:\n            values["encrypted_text"] = cipher_suite.encrypt(values["text"].encode()).decode()\n            del values["text"]\n        return values\n\n    @property\n    def text(self):\n        if self.encrypted_text:\n            return cipher_suite.decrypt(self.encrypted_text.encode()).decode()\n        return None\n\n    @text.setter\n    def text(self, value):\n        self.encrypted_text = cipher_suite.encrypt(str(value).encode()).decode()\n\n    @classmethod\n    def encrypt(cls, text: str):\n        return cls(text=text)\n\n    def decrypt(self):\n        return self.text\n\n# Modified sentiment_analysis_model to use the new EncryptedSentimentAnalysisInput\nclass sentiment_analysis_model(weave.Model):\n    model_name: str\n    system_prompt: str\n    temperature: int\n\n    @weave.op()\n    async def predict(self, encrypted_input: EncryptedSentimentAnalysisInput) -> dict:\n        client = AsyncAnthropic()\n\n        decrypted_text = encrypted_input.decrypt() # We use the custom class to decrypt the text\n\n        response = await client.messages.create(\n            max_tokens=1024,\n            model=self.model_name,\n            system=self.system_prompt,\n            messages=[\n                {   "role": "user",\n                    "content":[\n                        {\n                            "type": "text",\n                            "text": decrypted_text\n                        }\n                    ]\n                }\n            ]\n        )\n        result = response.content[0].text\n        if result is None:\n            raise ValueError("No response from model")\n        parsed = json.loads(result)\n        return parsed\n\nmodel = sentiment_analysis_model(\n    name="claude-3-sonnet",\n    model_name="claude-3-5-sonnet-20240620",\n    system_prompt="You are a Sentiment Analysis classifier. You will be classifying text based on their sentiment. Your input will be a block of text. You will answer with one the following rating option[\\"positive\\", \\"negative\\", \\"neutral\\"]. Your answer should one word in json format dict where the key is classification.",\n    temperature=0\n)\n\nfor entry in pii_data:\n    encrypted_input = EncryptedSentimentAnalysisInput.encrypt(entry["text"])\n    await model.predict(encrypted_input)\n'})})]})]})}function p(e={}){const{wrapper:n}={...(0,i.a)(),...e.components};return n?(0,r.jsx)(n,{...e,children:(0,r.jsx)(c,{...e})}):c(e)}},73484:(e,n,t)=>{t.d(n,{Z:()=>r});const r=t.p+"assets/images/encrypt-74cc555a643f9b82f85d0dd118277956.png"},37065:(e,n,t)=>{t.d(n,{Z:()=>r});const r=t.p+"assets/images/redact-58d40c51ced2248dbc17b7366ca55c1b.png"},4627:(e,n,t)=>{t.d(n,{Z:()=>r});const r=t.p+"assets/images/replace-c0cde4b527e4baa3f7310dedaed082cf.png"},11151:(e,n,t)=>{t.d(n,{Z:()=>s,a:()=>o});var r=t(67294);const i={},a=r.createContext(i);function o(e){const n=r.useContext(a);return r.useMemo((function(){return"function"==typeof e?e(n):{...n,...e}}),[n,e])}function s(e){let n;return n=e.disableParentContext?"function"==typeof e.components?e.components(i):e.components||i:o(e.components),r.createElement(a.Provider,{value:n},e.children)}}}]);