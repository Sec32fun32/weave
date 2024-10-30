"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[9944],{93137:(e,n,t)=>{t.r(n),t.d(n,{assets:()=>l,contentTitle:()=>i,default:()=>h,frontMatter:()=>a,metadata:()=>r,toc:()=>d});var s=t(85893),o=t(11151);const a={},i="App versioning",r={id:"tutorial-weave_models",title:"App versioning",description:"Tracking the inputs, outputs, metadata as well as data flowing through your app is critical to understanding the performance of your system. However versioning your app over time is also critical to understand how modifications to your code or app attributes change your outputs. Weave's Model class is how these changes can be tracked in Weave.",source:"@site/docs/tutorial-weave_models.md",sourceDirName:".",slug:"/tutorial-weave_models",permalink:"/tutorial-weave_models",draft:!1,unlisted:!1,editUrl:"https://github.com/wandb/weave/blob/master/docs/docs/tutorial-weave_models.md",tags:[],version:"current",lastUpdatedAt:1730319461e3,frontMatter:{},sidebar:"documentationSidebar",previous:{title:"Trace Applications",permalink:"/tutorial-tracing_2"},next:{title:"Build an Evaluation",permalink:"/tutorial-eval"}},l={},d=[{value:"Using <code>weave.Model</code>",id:"using-weavemodel",level:2},{value:"Exporting and re-using a logged <code>weave.Model</code>",id:"exporting-and-re-using-a-logged-weavemodel",level:2},{value:"What&#39;s next?",id:"whats-next",level:2}];function c(e){const n={a:"a",code:"code",h1:"h1",h2:"h2",img:"img",li:"li",p:"p",pre:"pre",strong:"strong",ul:"ul",...(0,o.a)(),...e.components};return(0,s.jsxs)(s.Fragment,{children:[(0,s.jsx)(n.h1,{id:"app-versioning",children:"App versioning"}),"\n",(0,s.jsxs)(n.p,{children:["Tracking the ",(0,s.jsx)(n.a,{href:"/quickstart",children:"inputs, outputs, metadata"})," as well as ",(0,s.jsx)(n.a,{href:"/tutorial-tracing_2",children:"data flowing through your app"})," is critical to understanding the performance of your system. However ",(0,s.jsx)(n.strong,{children:"versioning your app over time"})," is also critical to understand how modifications to your code or app attributes change your outputs. Weave's ",(0,s.jsx)(n.code,{children:"Model"})," class is how these changes can be tracked in Weave."]}),"\n",(0,s.jsx)(n.p,{children:"In this tutorial you'll learn:"}),"\n",(0,s.jsxs)(n.ul,{children:["\n",(0,s.jsxs)(n.li,{children:["How to use Weave ",(0,s.jsx)(n.code,{children:"Model"})," to track and version your app and its attributes."]}),"\n",(0,s.jsxs)(n.li,{children:["How to export, modify and re-use a Weave ",(0,s.jsx)(n.code,{children:"Model"})," already logged."]}),"\n"]}),"\n",(0,s.jsxs)(n.h2,{id:"using-weavemodel",children:["Using ",(0,s.jsx)(n.code,{children:"weave.Model"})]}),"\n",(0,s.jsxs)(n.p,{children:["Using Weave ",(0,s.jsx)(n.code,{children:"Model"}),"s means that attributes such as model vendor ids, prompts, temperature, and more are stored and versioned when they change."]}),"\n",(0,s.jsxs)(n.p,{children:["To create a ",(0,s.jsx)(n.code,{children:"Model"})," in Weave, you need the following:"]}),"\n",(0,s.jsxs)(n.ul,{children:["\n",(0,s.jsxs)(n.li,{children:["a class that inherits from ",(0,s.jsx)(n.code,{children:"weave.Model"})]}),"\n",(0,s.jsx)(n.li,{children:"type definitions on all class attributes"}),"\n",(0,s.jsxs)(n.li,{children:["a typed ",(0,s.jsx)(n.code,{children:"invoke"})," function with the ",(0,s.jsx)(n.code,{children:"@weave.op()"})," decorator"]}),"\n"]}),"\n",(0,s.jsxs)(n.p,{children:["When you change the class attributes or the code that defines your model, ",(0,s.jsx)(n.strong,{children:"these changes will be logged and the version will be updated"}),". This ensures that you can compare the generations across different versions of your app."]}),"\n",(0,s.jsxs)(n.p,{children:["In the example below, the ",(0,s.jsx)(n.strong,{children:"model name, temperature and system prompt will be tracked and versioned"}),":"]}),"\n",(0,s.jsx)(n.pre,{children:(0,s.jsx)(n.code,{className:"language-python",children:'import json\nfrom openai import OpenAI\n\nimport weave\n\n@weave.op()\ndef extract_dinos(wmodel: weave.Model, sentence: str) -> dict:\n    response = wmodel.client.chat.completions.create(\n        model=wmodel.model_name,\n        temperature=wmodel.temperature,\n        messages=[\n            {\n                "role": "system",\n                "content": wmodel.system_prompt\n            },\n            {\n                "role": "user",\n                "content": sentence\n            }\n            ],\n            response_format={ "type": "json_object" }\n        )\n    return response.choices[0].message.content\n\n# Sub-class with a weave.Model\n# highlight-next-line\nclass ExtractDinos(weave.Model):\n    client: OpenAI = None\n    model_name: str\n    temperature: float\n    system_prompt: str\n\n    # Ensure your function is called `invoke` or `predict`\n    # highlight-next-line\n    @weave.op()\n    # highlight-next-line\n    def invoke(self, sentence: str) -> dict:\n        dino_data  = extract_dinos(self, sentence)\n        return json.loads(dino_data)\n'})}),"\n",(0,s.jsxs)(n.p,{children:["Now you can instantiate and call the model with ",(0,s.jsx)(n.code,{children:"invoke"}),":"]}),"\n",(0,s.jsx)(n.pre,{children:(0,s.jsx)(n.code,{className:"language-python",children:'weave.init(\'jurassic-park\')\nclient = OpenAI()\n\nsystem_prompt = """Extract any dinosaur `name`, their `common_name`, \\\nnames and whether its `diet` is a herbivore or carnivore, in JSON format."""\n\n# highlight-next-line\ndinos = ExtractDinos(\n    client=client,\n    model_name=\'gpt-4o\',\n    temperature=0.4,\n    system_prompt=system_prompt\n)\n\nsentence = """I watched as a Tyrannosaurus rex (T. rex) chased after a Triceratops (Trike), \\\nboth carnivore and herbivore locked in an ancient dance. Meanwhile, a gentle giant \\\nBrachiosaurus (Brachi) calmly munched on treetops, blissfully unaware of the chaos below."""\n\n# highlight-next-line\nresult = dinos.invoke(sentence)\nprint(result)\n'})}),"\n",(0,s.jsxs)(n.p,{children:["Now after calling ",(0,s.jsx)(n.code,{children:".invoke"})," you can see the trace in Weave ",(0,s.jsx)(n.strong,{children:"now tracks the model attributes as well as the code"})," for the model functions that have been decorated with ",(0,s.jsx)(n.code,{children:"weave.op()"}),'. You can see the model is also versioned, "v21" in this case, and if you click on the model ',(0,s.jsx)(n.strong,{children:"you can see all of the calls"})," that have used that version of the model"]}),"\n",(0,s.jsx)(n.p,{children:(0,s.jsx)(n.img,{alt:"Re-using a weave model",src:t(46446).Z+"",width:"1664",height:"1292"})}),"\n",(0,s.jsx)(n.p,{children:(0,s.jsxs)(n.strong,{children:["A note on using ",(0,s.jsx)(n.code,{children:"weave.Model"}),":"]})}),"\n",(0,s.jsxs)(n.ul,{children:["\n",(0,s.jsxs)(n.li,{children:["You can use ",(0,s.jsx)(n.code,{children:"predict"})," instead of ",(0,s.jsx)(n.code,{children:"invoke"})," for the name of the function in your Weave ",(0,s.jsx)(n.code,{children:"Model"})," if you prefer."]}),"\n",(0,s.jsxs)(n.li,{children:["If you want other class methods to be tracked by weave they need to be wrapped in ",(0,s.jsx)(n.code,{children:"weave.op()"})]}),"\n",(0,s.jsx)(n.li,{children:"Attributes starting with an underscore are ignored by weave and won't be logged"}),"\n"]}),"\n",(0,s.jsxs)(n.h2,{id:"exporting-and-re-using-a-logged-weavemodel",children:["Exporting and re-using a logged ",(0,s.jsx)(n.code,{children:"weave.Model"})]}),"\n",(0,s.jsx)(n.p,{children:"Because Weave stores and versions Models that have been invoked, it is possible to export and re-use these models."}),"\n",(0,s.jsxs)(n.p,{children:[(0,s.jsx)(n.strong,{children:"Get the Model ref"}),"\nIn the Weave UI you can get the Model ref for a particular version"]}),"\n",(0,s.jsxs)(n.p,{children:[(0,s.jsx)(n.strong,{children:"Using the Model"}),"\nOnce you have the URI of the Model object, you can export and re-use it. Note that the exported model is already initialised and ready to use:"]}),"\n",(0,s.jsx)(n.pre,{children:(0,s.jsx)(n.code,{className:"language-python",children:'# the exported weave model is already initialised and ready to be called\n# highlight-next-line\nnew_dinos = weave.ref("weave:///morgan/jurassic-park/object/ExtractDinos:ey4udBU2MU23heQFJenkVxLBX4bmDsFk7vsGcOWPjY4").get()\n\n# set the client to the openai client again\nnew_dinos.client = client\n\nnew_sentence = """I also saw an Ankylosaurus grazing on giant ferns"""\nnew_result = new_dinos.invoke(new_sentence)\nprint(new_result)\n'})}),"\n",(0,s.jsx)(n.p,{children:"Here you can now see the name Model version (v21) was used with the new input:"}),"\n",(0,s.jsx)(n.p,{children:(0,s.jsx)(n.img,{alt:"Re-using a weave model",src:t(52771).Z+"",width:"1260",height:"1120"})}),"\n",(0,s.jsx)(n.h2,{id:"whats-next",children:"What's next?"}),"\n",(0,s.jsxs)(n.ul,{children:["\n",(0,s.jsxs)(n.li,{children:["Follow the ",(0,s.jsx)(n.a,{href:"/tutorial-eval",children:"Build an Evaluation pipeline tutorial"})," to start iteratively improving your applications."]}),"\n"]})]})}function h(e={}){const{wrapper:n}={...(0,o.a)(),...e.components};return n?(0,s.jsx)(n,{...e,children:(0,s.jsx)(c,{...e})}):c(e)}},46446:(e,n,t)=>{t.d(n,{Z:()=>s});const s=t.p+"assets/images/tutorial-model_invoke3-7aacbc42abd7b9a7321db68d3b191484.png"},52771:(e,n,t)=>{t.d(n,{Z:()=>s});const s=t.p+"assets/images/tutorial-model_re-use-15b0a000e5e4b0fc3efa1b35ad212fdc.png"},11151:(e,n,t)=>{t.d(n,{Z:()=>r,a:()=>i});var s=t(67294);const o={},a=s.createContext(o);function i(e){const n=s.useContext(a);return s.useMemo((function(){return"function"==typeof e?e(n):{...n,...e}}),[n,e])}function r(e){let n;return n=e.disableParentContext?"function"==typeof e.components?e.components(o):e.components||o:i(e.components),s.createElement(a.Provider,{value:n},e.children)}}}]);