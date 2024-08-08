"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[4064],{24211:(e,n,t)=>{t.r(n),t.d(n,{assets:()=>s,contentTitle:()=>l,default:()=>p,frontMatter:()=>o,metadata:()=>r,toc:()=>c});var a=t(85893),i=t(11151);const o={},l="LiteLLM",r={id:"guides/integrations/litellm",title:"LiteLLM",description:"Weave automatically tracks and logs LLM calls made via LiteLLM, after weave.init() is called.",source:"@site/docs/guides/integrations/litellm.md",sourceDirName:"guides/integrations",slug:"/guides/integrations/litellm",permalink:"/weave/guides/integrations/litellm",draft:!1,unlisted:!1,editUrl:"https://github.com/wandb/weave/blob/master/docs/docs/guides/integrations/litellm.md",tags:[],version:"current",frontMatter:{},sidebar:"documentationSidebar",previous:{title:"Open Router",permalink:"/weave/guides/integrations/openrouter"},next:{title:"Local Models",permalink:"/weave/guides/integrations/local_models"}},s={},c=[{value:"Traces",id:"traces",level:2},{value:"Wrapping with your own ops",id:"wrapping-with-your-own-ops",level:2},{value:"Create a <code>Model</code> for easier experimentation",id:"create-a-model-for-easier-experimentation",level:2},{value:"Function Calling",id:"function-calling",level:2}];function d(e){const n={a:"a",blockquote:"blockquote",code:"code",h1:"h1",h2:"h2",img:"img",p:"p",pre:"pre",strong:"strong",...(0,i.a)(),...e.components};return(0,a.jsxs)(a.Fragment,{children:[(0,a.jsx)(n.h1,{id:"litellm",children:"LiteLLM"}),"\n",(0,a.jsxs)(n.p,{children:["Weave automatically tracks and logs LLM calls made via LiteLLM, after ",(0,a.jsx)(n.code,{children:"weave.init()"})," is called."]}),"\n",(0,a.jsx)(n.h2,{id:"traces",children:"Traces"}),"\n",(0,a.jsx)(n.p,{children:"It's important to store traces of LLM applications in a central database, both during development and in production. You'll use these traces for debugging, and as a dataset that will help you improve your application."}),"\n",(0,a.jsxs)(n.blockquote,{children:["\n",(0,a.jsxs)(n.p,{children:[(0,a.jsx)(n.strong,{children:"Note:"})," When using LiteLLM, make sure to import the library using ",(0,a.jsx)(n.code,{children:"import litellm"})," and call the completion function with ",(0,a.jsx)(n.code,{children:"litellm.completion"})," instead of ",(0,a.jsx)(n.code,{children:"from litellm import completion"}),". This ensures that all functions and attributes are correctly referenced."]}),"\n"]}),"\n",(0,a.jsx)(n.p,{children:(0,a.jsx)(n.a,{href:"https://colab.research.google.com/github/wandb/weave/blob/master/examples/cookbooks/weave_litellm_integration_docs.ipynb",children:(0,a.jsx)(n.img,{src:"https://colab.research.google.com/assets/colab-badge.svg",alt:"Open In Colab"})})}),"\n",(0,a.jsxs)(n.p,{children:["Weave will automatically capture traces for LiteLLM. You can use the library as usual, start by calling ",(0,a.jsx)(n.code,{children:"weave.init()"}),":"]}),"\n",(0,a.jsx)(n.pre,{children:(0,a.jsx)(n.code,{className:"language-python",children:'import litellm\nimport weave\n\n# highlight-next-line\nweave.init("weave_litellm_integration")\n\nopenai_response = litellm.completion(\n    model="gpt-3.5-turbo", \n    messages=[{"role": "user", "content": "Translate \'Hello, how are you?\' to French"}],\n    max_tokens=1024\n)\nprint(openai_response.choices[0].message.content)\n\nclaude_response = litellm.completion(\n    model="claude-3-5-sonnet-20240620", \n    messages=[{"role": "user", "content": "Translate \'Hello, how are you?\' to French"}],\n    max_tokens=1024\n)\nprint(claude_response.choices[0].message.content)\n'})}),"\n",(0,a.jsx)(n.p,{children:"Weave will now track and log all LLM calls made through LiteLLM. You can view the traces in the Weave web interface."}),"\n",(0,a.jsx)(n.h2,{id:"wrapping-with-your-own-ops",children:"Wrapping with your own ops"}),"\n",(0,a.jsxs)(n.p,{children:["Weave ops make results reproducible by automatically versioning code as you experiment, and they capture their inputs and outputs. Simply create a function decorated with ",(0,a.jsx)(n.code,{children:"@weave.op()"})," that calls into LiteLLM's completion function and Weave will track the inputs and outputs for you. Here's an example:"]}),"\n",(0,a.jsx)(n.pre,{children:(0,a.jsx)(n.code,{className:"language-python",children:'import litellm\nimport weave\n\n# highlight-next-line\nweave.init("weave_litellm_integration")\n\n# highlight-next-line\n@weave.op()\ndef translate(text: str, target_language: str, model: str) -> str:\n    response = litellm.completion(\n        model=model,\n        messages=[{"role": "user", "content": f"Translate \'{text}\' to {target_language}"}],\n        max_tokens=1024\n    )\n    return response.choices[0].message.content\n\nprint(translate("Hello, how are you?", "French", "gpt-3.5-turbo"))\nprint(translate("Hello, how are you?", "Spanish", "claude-3-5-sonnet-20240620"))\n'})}),"\n",(0,a.jsxs)(n.h2,{id:"create-a-model-for-easier-experimentation",children:["Create a ",(0,a.jsx)(n.code,{children:"Model"})," for easier experimentation"]}),"\n",(0,a.jsxs)(n.p,{children:["Organizing experimentation is difficult when there are many moving pieces. By using the ",(0,a.jsx)(n.code,{children:"Model"})," class, you can capture and organize the experimental details of your app like your system prompt or the model you're using. This helps organize and compare different iterations of your app."]}),"\n",(0,a.jsxs)(n.p,{children:["In addition to versioning code and capturing inputs/outputs, Models capture structured parameters that control your application's behavior, making it easy to find what parameters worked best. You can also use Weave Models with ",(0,a.jsx)(n.code,{children:"serve"}),", and Evaluations."]}),"\n",(0,a.jsx)(n.p,{children:"In the example below, you can experiment with different models and temperatures:"}),"\n",(0,a.jsx)(n.pre,{children:(0,a.jsx)(n.code,{className:"language-python",children:'import litellm\nimport weave\n\n# highlight-next-line\nweave.init(\'weave_litellm_integration\')\n\n# highlight-next-line\nclass TranslatorModel(weave.Model):\n    model: str\n    temperature: float\n  \n    # highlight-next-line\n    @weave.op()\n    def predict(self, text: str, target_language: str):\n        response = litellm.completion(\n            model=self.model,\n            messages=[\n                {"role": "system", "content": f"You are a translator. Translate the given text to {target_language}."},\n                {"role": "user", "content": text}\n            ],\n            max_tokens=1024,\n            temperature=self.temperature\n        )\n        return response.choices[0].message.content\n\n# Create instances with different models\ngpt_translator = TranslatorModel(model="gpt-3.5-turbo", temperature=0.3)\nclaude_translator = TranslatorModel(model="claude-3-5-sonnet-20240620", temperature=0.1)\n\n# Use different models for translation\nenglish_text = "Hello, how are you today?"\n\nprint("GPT-3.5 Translation to French:")\nprint(gpt_translator.predict(english_text, "French"))\n\nprint("\\nClaude-3.5 Sonnet Translation to Spanish:")\nprint(claude_translator.predict(english_text, "Spanish"))\n'})}),"\n",(0,a.jsx)(n.h2,{id:"function-calling",children:"Function Calling"}),"\n",(0,a.jsx)(n.p,{children:"LiteLLM supports function calling for compatible models. Weave will automatically track these function calls."}),"\n",(0,a.jsx)(n.pre,{children:(0,a.jsx)(n.code,{className:"language-python",children:'import litellm\nimport weave\n\n# highlight-next-line\nweave.init("weave_litellm_integration")\n\nresponse = litellm.completion(\n    model="gpt-3.5-turbo",\n    messages=[{"role": "user", "content": "Translate \'Hello, how are you?\' to French"}],\n    functions=[\n        {\n            "name": "translate",\n            "description": "Translate text to a specified language",\n            "parameters": {\n                "type": "object",\n                "properties": {\n                    "text": {\n                        "type": "string",\n                        "description": "The text to translate",\n                    },\n                    "target_language": {\n                        "type": "string",\n                        "description": "The language to translate to",\n                    }\n                },\n                "required": ["text", "target_language"],\n            },\n        },\n    ],\n)\n\nprint(response)\n'})}),"\n",(0,a.jsx)(n.p,{children:"We automatically capture the functions you used in the prompt and keep them versioned."}),"\n",(0,a.jsx)(n.p,{children:(0,a.jsx)(n.a,{href:"https://wandb.ai/a-sh0ts/weave_litellm_integration/weave/calls",children:(0,a.jsx)(n.img,{alt:"litellm_gif.png",src:t(25971).Z+"",width:"740",height:"480"})})})]})}function p(e={}){const{wrapper:n}={...(0,i.a)(),...e.components};return n?(0,a.jsx)(n,{...e,children:(0,a.jsx)(d,{...e})}):d(e)}},25971:(e,n,t)=>{t.d(n,{Z:()=>a});const a=t.p+"assets/images/litellm_gif-0d244c8a37332356eaa663f46931bf31.gif"},11151:(e,n,t)=>{t.d(n,{Z:()=>r,a:()=>l});var a=t(67294);const i={},o=a.createContext(i);function l(e){const n=a.useContext(o);return a.useMemo((function(){return"function"==typeof e?e(n):{...n,...e}}),[n,e])}function r(e){let n;return n=e.disableParentContext?"function"==typeof e.components?e.components(i):e.components||i:l(e.components),a.createElement(o.Provider,{value:n},e.children)}}}]);