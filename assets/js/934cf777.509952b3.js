"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[1851],{63578:(e,n,a)=>{a.r(n),a.d(n,{assets:()=>c,contentTitle:()=>i,default:()=>p,frontMatter:()=>t,metadata:()=>o,toc:()=>l});var r=a(85893),s=a(11151);const t={},i="Cerebras",o={id:"guides/integrations/cerebras",title:"Cerebras",description:"Weave automatically tracks and logs LLM calls made via the Cerebras Cloud SDK.",source:"@site/docs/guides/integrations/cerebras.md",sourceDirName:"guides/integrations",slug:"/guides/integrations/cerebras",permalink:"/guides/integrations/cerebras",draft:!1,unlisted:!1,editUrl:"https://github.com/wandb/weave/blob/master/docs/docs/guides/integrations/cerebras.md",tags:[],version:"current",lastUpdatedAt:1730319461e3,frontMatter:{},sidebar:"documentationSidebar",previous:{title:"Anthropic",permalink:"/guides/integrations/anthropic"},next:{title:"Cohere",permalink:"/guides/integrations/cohere"}},c={},l=[{value:"Traces",id:"traces",level:2},{value:"Wrapping with your own ops",id:"wrapping-with-your-own-ops",level:2},{value:"Create a <code>Model</code> for easier experimentation",id:"create-a-model-for-easier-experimentation",level:2}];function d(e){const n={a:"a",code:"code",h1:"h1",h2:"h2",img:"img",p:"p",pre:"pre",...(0,s.a)(),...e.components};return(0,r.jsxs)(r.Fragment,{children:[(0,r.jsx)(n.h1,{id:"cerebras",children:"Cerebras"}),"\n",(0,r.jsxs)(n.p,{children:["Weave automatically tracks and logs LLM calls made via the ",(0,r.jsx)(n.a,{href:"https://inference-docs.cerebras.ai/introduction",children:"Cerebras Cloud SDK"}),"."]}),"\n",(0,r.jsx)(n.h2,{id:"traces",children:"Traces"}),"\n",(0,r.jsx)(n.p,{children:"Tracking LLM calls is crucial for debugging and performance monitoring. Weave helps you do this by automatically capturing traces for the Cerebras Cloud SDK."}),"\n",(0,r.jsx)(n.p,{children:"Here's an example of how to use Weave with Cerebras:"}),"\n",(0,r.jsx)(n.pre,{children:(0,r.jsx)(n.code,{className:"language-python",children:'import os\nimport weave\nfrom cerebras.cloud.sdk import Cerebras\n\n# Initialise the weave project\nweave.init("cerebras_speedster")\n\n# Use the Cerebras SDK as usual\napi_key = os.environ["CEREBRAS_API_KEY"]\nmodel = "llama3.1-8b"  # Cerebras model\n\nclient = Cerebras(api_key=api_key)\n\nresponse = client.chat.completions.create(\n    model=model,\n    messages=[{"role": "user", "content": "What\'s the fastest land animal?"}],\n)\n\nprint(response.choices[0].message.content)\n'})}),"\n",(0,r.jsx)(n.p,{children:"Weave will now track and log all LLM calls made through the Cerebras SDK. You can view the traces in the Weave web interface, including details like token usage and response time."}),"\n",(0,r.jsx)(n.p,{children:(0,r.jsx)(n.a,{href:"https://wandb.ai/capecape/cerebras_speedster/weave/traces",children:(0,r.jsx)(n.img,{alt:"cerebras_calls.png",src:a(12762).Z+"",width:"2716",height:"1844"})})}),"\n",(0,r.jsx)(n.h2,{id:"wrapping-with-your-own-ops",children:"Wrapping with your own ops"}),"\n",(0,r.jsx)(n.p,{children:"Weave ops offer a powerful way to enhance reproducibility and traceability in your experiments. By automatically versioning your code and capturing inputs and outputs. Here's an example of how you can leverage Weave ops with the Cerebras SDK:"}),"\n",(0,r.jsx)(n.pre,{children:(0,r.jsx)(n.code,{className:"language-python",children:'import os\nimport weave\nfrom cerebras.cloud.sdk import Cerebras\n\n# Initialise the weave project\nweave.init("cerebras_speedster")\n\nclient = Cerebras(api_key=os.environ["CEREBRAS_API_KEY"])\n\n# Weave will track the inputs, outputs and code of this function\n@weave.op\ndef animal_speedster(animal: str, model: str) -> str:\n    "Find out how fast an animal can run"\n    \n    response = client.chat.completions.create(\n        model=model,\n        messages=[{"role": "user", "content": f"How fast can a {animal} run?"}],\n    )\n    return response.choices[0].message.content\n\nanimal_speedster("cheetah", "llama3.1-8b")\nanimal_speedster("ostrich", "llama3.1-8b")\nanimal_speedster("human", "llama3.1-8b")\n'})}),"\n",(0,r.jsxs)(n.h2,{id:"create-a-model-for-easier-experimentation",children:["Create a ",(0,r.jsx)(n.code,{children:"Model"})," for easier experimentation"]}),"\n",(0,r.jsxs)(n.p,{children:["The ",(0,r.jsx)(n.a,{href:"/guides/core-types/models",children:"Model"})," class in Weave helps you organize and compare different iterations of your app. This is particularly useful when experimenting with Cerebras models. Here's an example:"]}),"\n",(0,r.jsx)(n.pre,{children:(0,r.jsx)(n.code,{className:"language-python",children:'import os\nimport weave\nfrom cerebras.cloud.sdk import Cerebras\n\n# Initialise the weave project\nweave.init("cerebras_speedster")\n\nclient = Cerebras(api_key=os.environ["CEREBRAS_API_KEY"])\n\nclass AnimalSpeedModel(weave.Model):\n    model: str\n    temperature: float\n\n    @weave.op\n    def predict(self, animal: str) -> str:\n        "Predict the top speed of an animal"        \n\n        response = client.chat.completions.create(\n            model=self.model,\n            messages=[{"role": "user", "content": f"What\'s the top speed of a {animal}?"}],\n            temperature=self.temperature\n        )\n        return response.choices[0].message.content\n\nspeed_model = AnimalSpeedModel(\n    model="llama3.1-8b",\n    temperature=0.7\n)\nresult = speed_model.predict(animal="cheetah")\nprint(result)\n'})}),"\n",(0,r.jsx)(n.p,{children:"With this setup, you can easily experiment with different models and parameters, all while keeping track of your Cerebras-powered inferences!"}),"\n",(0,r.jsx)(n.p,{children:(0,r.jsx)(n.a,{href:"https://wandb.ai/capecape/cerebras_speedster/weave/traces",children:(0,r.jsx)(n.img,{alt:"cerebras_model.png",src:a(52356).Z+"",width:"2726",height:"1680"})})})]})}function p(e={}){const{wrapper:n}={...(0,s.a)(),...e.components};return n?(0,r.jsx)(n,{...e,children:(0,r.jsx)(d,{...e})}):d(e)}},12762:(e,n,a)=>{a.d(n,{Z:()=>r});const r=a.p+"assets/images/cerebras_calls-6776c4bad7b594f664eae321260938c9.png"},52356:(e,n,a)=>{a.d(n,{Z:()=>r});const r=a.p+"assets/images/cerebras_model-68127a802d11327c9243b0cce52f867b.png"},11151:(e,n,a)=>{a.d(n,{Z:()=>o,a:()=>i});var r=a(67294);const s={},t=r.createContext(s);function i(e){const n=r.useContext(t);return r.useMemo((function(){return"function"==typeof e?e(n):{...n,...e}}),[n,e])}function o(e){let n;return n=e.disableParentContext?"function"==typeof e.components?e.components(s):e.components||s:i(e.components),r.createElement(t.Provider,{value:n},e.children)}}}]);