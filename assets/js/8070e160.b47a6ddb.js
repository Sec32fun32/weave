"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[651],{9759:(e,t,n)=>{n.r(t),n.d(t,{assets:()=>l,contentTitle:()=>s,default:()=>u,frontMatter:()=>o,metadata:()=>r,toc:()=>c});var i=n(5893),a=n(1151);const o={sidebar_position:1,hide_table_of_contents:!0},s="Quickstart",r={id:"quickstart",title:"Quickstart",description:"Installation",source:"@site/docs/quickstart.md",sourceDirName:".",slug:"/quickstart",permalink:"/weave/quickstart",draft:!1,unlisted:!1,editUrl:"https://github.com/wandb/weave/blob/master/docs/docs/quickstart.md",tags:[],version:"current",sidebarPosition:1,frontMatter:{sidebar_position:1,hide_table_of_contents:!0},sidebar:"documentationSidebar",previous:{title:"Introduction",permalink:"/weave/"},next:{title:"Tutorial: Build an Evaluation pipeline",permalink:"/weave/tutorial-eval"}},l={},c=[{value:"Installation",id:"installation",level:2},{value:"Track inputs &amp; outputs of functions",id:"track-inputs--outputs-of-functions",level:2},{value:"What&#39;s next?",id:"whats-next",level:2}];function d(e){const t={a:"a",admonition:"admonition",code:"code",h1:"h1",h2:"h2",li:"li",p:"p",pre:"pre",ul:"ul",...(0,a.a)(),...e.components};return(0,i.jsxs)(i.Fragment,{children:[(0,i.jsx)(t.h1,{id:"quickstart",children:"Quickstart"}),"\n",(0,i.jsx)("a",{target:"_blank",href:"http://wandb.me/weave_colab",children:(0,i.jsx)("img",{src:"https://colab.research.google.com/assets/colab-badge.svg",alt:"Open In Colab"})}),"\n",(0,i.jsx)(t.h2,{id:"installation",children:"Installation"}),"\n",(0,i.jsx)(t.p,{children:"Weave requires Python 3.9+."}),"\n",(0,i.jsx)(t.p,{children:(0,i.jsx)(t.code,{children:"pip install weave"})}),"\n",(0,i.jsx)(t.h2,{id:"track-inputs--outputs-of-functions",children:"Track inputs & outputs of functions"}),"\n",(0,i.jsxs)(t.ul,{children:["\n",(0,i.jsx)(t.li,{children:"Import weave"}),"\n",(0,i.jsxs)(t.li,{children:["Call ",(0,i.jsx)(t.code,{children:"weave.init('project-name')"})," to start logging"]}),"\n",(0,i.jsxs)(t.li,{children:["Add the ",(0,i.jsx)(t.code,{children:"@weave.op()"})," decorator to the functions you want to track"]}),"\n"]}),"\n",(0,i.jsxs)(t.p,{children:["In this example, we're using openai so you will need to ",(0,i.jsx)(t.a,{href:"https://platform.openai.com/docs/quickstart/step-2-setup-your-api-key",children:"add an openai API key"}),"."]}),"\n",(0,i.jsx)(t.pre,{children:(0,i.jsx)(t.code,{className:"language-python",children:'# highlight-next-line\nimport weave\nimport json\nfrom openai import OpenAI\n\n# highlight-next-line\n@weave.op()\ndef extract_fruit(sentence: str) -> dict:\n    client = OpenAI()\n\n    response = client.chat.completions.create(\n    model="gpt-3.5-turbo-1106",\n    messages=[\n        {\n            "role": "system",\n            "content": "You will be provided with unstructured data, and your task is to parse it one JSON dictionary with fruit, color and flavor as keys."\n        },\n        {\n            "role": "user",\n            "content": sentence\n        }\n        ],\n        temperature=0.7,\n        response_format={ "type": "json_object" }\n    )\n    extracted = response.choices[0].message.content\n    return json.loads(extracted)\n\n# highlight-next-line\nweave.init(\'intro-example\')\nsentence = "There are many fruits that were found on the recently discovered planet Goocrux. There are neoskizzles that grow there, which are purple and taste like candy."\nextract_fruit(sentence)\n'})}),"\n",(0,i.jsx)(t.p,{children:"Now, every time you call this function, weave will automatically capture the input & output data and log any changes to the code.\nRun this application and your console will output a link to view it within W&B."}),"\n",(0,i.jsx)(t.admonition,{type:"note",children:(0,i.jsxs)(t.p,{children:["Calls made with the openai library are automatically tracked with weave but you can add other LLMs easily by wrapping them with ",(0,i.jsx)(t.code,{children:"@weave.op()"})]})}),"\n",(0,i.jsx)(t.h2,{id:"whats-next",children:"What's next?"}),"\n",(0,i.jsxs)(t.ul,{children:["\n",(0,i.jsxs)(t.li,{children:["Follow the ",(0,i.jsx)(t.a,{href:"/tutorial-eval",children:"Build an Evaluation pipeline tutorial"})," to start iteratively improving your applications."]}),"\n"]})]})}function u(e={}){const{wrapper:t}={...(0,a.a)(),...e.components};return t?(0,i.jsx)(t,{...e,children:(0,i.jsx)(d,{...e})}):d(e)}},1151:(e,t,n)=>{n.d(t,{Z:()=>r,a:()=>s});var i=n(7294);const a={},o=i.createContext(a);function s(e){const t=i.useContext(o);return i.useMemo((function(){return"function"==typeof e?e(t):{...t,...e}}),[t,e])}function r(e){let t;return t=e.disableParentContext?"function"==typeof e.components?e.components(a):e.components||a:s(e.components),i.createElement(o.Provider,{value:t},e.children)}}}]);