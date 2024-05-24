"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[999],{277:(e,t,s)=>{s.r(t),s.d(t,{assets:()=>l,contentTitle:()=>r,default:()=>h,frontMatter:()=>i,metadata:()=>o,toc:()=>c});var a=s(5893),n=s(1151);const i={sidebar_position:1,hide_table_of_contents:!0},r="MistralAI",o={id:"guides/ecosystem/mistral",title:"MistralAI",description:"Weave automatically tracks and logs LLM calls made via the MistralAI Python library.",source:"@site/docs/guides/ecosystem/mistral.md",sourceDirName:"guides/ecosystem",slug:"/guides/ecosystem/mistral",permalink:"/weave/guides/ecosystem/mistral",draft:!1,unlisted:!1,editUrl:"https://github.com/wandb/weave/blob/master/docs/docs/guides/ecosystem/mistral.md",tags:[],version:"current",sidebarPosition:1,frontMatter:{sidebar_position:1,hide_table_of_contents:!0},sidebar:"documentationSidebar",previous:{title:"OpenAI",permalink:"/weave/guides/ecosystem/openai"},next:{title:"Tools",permalink:"/weave/guides/tools/"}},l={},c=[{value:"Traces",id:"traces",level:2},{value:"Wrapping with your own ops",id:"wrapping-with-your-own-ops",level:2}];function d(e){const t={a:"a",code:"code",em:"em",h1:"h1",h2:"h2",img:"img",p:"p",pre:"pre",...(0,n.a)(),...e.components};return(0,a.jsxs)(a.Fragment,{children:[(0,a.jsx)(t.h1,{id:"mistralai",children:"MistralAI"}),"\n",(0,a.jsxs)(t.p,{children:["Weave automatically tracks and logs LLM calls made via the ",(0,a.jsx)(t.a,{href:"https://github.com/mistralai/client-python",children:"MistralAI Python library"}),"."]}),"\n",(0,a.jsx)(t.h2,{id:"traces",children:"Traces"}),"\n",(0,a.jsx)(t.p,{children:"It\u2019s important to store traces of LLM applications in a central database, both during development and in production. You\u2019ll use these traces for debugging, and as a dataset that will help you improve your application."}),"\n",(0,a.jsxs)(t.p,{children:["Weave will automatically capture traces for ",(0,a.jsx)(t.a,{href:"https://github.com/mistralai/client-python",children:"mistralai"}),". You can use the library as usual, start by calling ",(0,a.jsx)(t.code,{children:"weave.init()"}),":"]}),"\n",(0,a.jsx)(t.pre,{children:(0,a.jsx)(t.code,{className:"language-python",children:'import weave\nweave.init("cheese_recommender")\n\n# then use mistralai library as usual\nimport os\nfrom mistralai.client import MistralClient\nfrom mistralai.models.chat_completion import ChatMessage\n\napi_key = os.environ["MISTRAL_API_KEY"]\nmodel = "mistral-large-latest"\n\nclient = MistralClient(api_key=api_key)\n\nmessages = [\n    ChatMessage(role="user", content="What is the best French cheese?")\n]\n\nchat_response = client.chat(\n    model=model,\n    messages=messages,\n)\n'})}),"\n",(0,a.jsx)(t.p,{children:"Weave will now track and log all LLM calls made through the MistralAI library. You can view the traces in the Weave web interface."}),"\n",(0,a.jsx)(t.p,{children:(0,a.jsx)(t.a,{href:"https://wandb.ai/capecape/mistralai_project/weave/calls",children:(0,a.jsx)(t.img,{alt:"mistral_trace.png",src:s(5877).Z+"",width:"3024",height:"1468"})})}),"\n",(0,a.jsx)(t.h2,{id:"wrapping-with-your-own-ops",children:"Wrapping with your own ops"}),"\n",(0,a.jsxs)(t.p,{children:["Weave ops make results ",(0,a.jsx)(t.em,{children:"reproducible"})," by automatically versioning code as you experiment, and they capture their inputs and outputs. Simply create a function decorated with ",(0,a.jsx)(t.a,{href:"https://wandb.github.io/weave/guides/tracking/ops",children:(0,a.jsx)(t.code,{children:"@weave.op()"})})," that calls into ",(0,a.jsx)(t.a,{href:"https://docs.mistral.ai/capabilities/completion/",children:(0,a.jsx)(t.code,{children:"mistralai.client.MistralClient.chat()"})})," and Weave will track the inputs and outputs for you. Let's see how we can do this for our cheese recommender:"]}),"\n",(0,a.jsx)(t.pre,{children:(0,a.jsx)(t.code,{className:"language-python",children:'# highlight-next-line\n@weave.op()\ndef cheese_recommender(region:str, model:str) -> str:\n    "Recommend the best cheese in a given region"\n    \n    messages = [ChatMessage(role="user", content=f"What is the best cheese in {region}?")]\n\n    chat_response = client.chat(\n        model=model,\n        messages=messages,\n    )\n    return chat_response.choices[0].message.content\n\ncheese_recommender(region="France", model="mistral-large-latest")\ncheese_recommender(region="Spain", model="mistral-large-latest")\ncheese_recommender(region="Netherlands", model="mistral-large-latest")\n'})}),"\n",(0,a.jsx)(t.p,{children:(0,a.jsx)(t.a,{href:"https://wandb.ai/capecape/mistralai_project/weave/calls",children:(0,a.jsx)(t.img,{alt:"mistral_ops.png",src:s(9265).Z+"",width:"2877",height:"1080"})})})]})}function h(e={}){const{wrapper:t}={...(0,n.a)(),...e.components};return t?(0,a.jsx)(t,{...e,children:(0,a.jsx)(d,{...e})}):d(e)}},9265:(e,t,s)=>{s.d(t,{Z:()=>a});const a=s.p+"assets/images/mistral_ops-dc76539153b4df98060b8a5a1964a817.png"},5877:(e,t,s)=>{s.d(t,{Z:()=>a});const a=s.p+"assets/images/mistral_trace-194ff2078c712f2d46e00a93a4b1599c.png"},1151:(e,t,s)=>{s.d(t,{Z:()=>o,a:()=>r});var a=s(7294);const n={},i=a.createContext(n);function r(e){const t=a.useContext(i);return a.useMemo((function(){return"function"==typeof e?e(t):{...t,...e}}),[t,e])}function o(e){let t;return t=e.disableParentContext?"function"==typeof e.components?e.components(n):e.components||n:r(e.components),a.createElement(i.Provider,{value:t},e.children)}}}]);