"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[5172],{5347:(e,n,t)=>{t.r(n),t.d(n,{assets:()=>c,contentTitle:()=>r,default:()=>u,frontMatter:()=>s,metadata:()=>o,toc:()=>d});var a=t(5893),i=t(1151);const s={},r="Track data flows and app metadata",o={id:"tutorial-tracing_2",title:"Track data flows and app metadata",description:"In the Track LLM inputs & outputs tutorial, the basics of tracking the inputs and outputs of your LLMs was covered.",source:"@site/docs/tutorial-tracing_2.md",sourceDirName:".",slug:"/tutorial-tracing_2",permalink:"/weave/tutorial-tracing_2",draft:!1,unlisted:!1,editUrl:"https://github.com/wandb/weave/blob/master/docs/docs/tutorial-tracing_2.md",tags:[],version:"current",frontMatter:{},sidebar:"documentationSidebar",previous:{title:"Track LLM inputs & outputs",permalink:"/weave/quickstart"},next:{title:"App versioning",permalink:"/weave/tutorial-weave_models"}},c={},d=[{value:"Tracking nested function calls",id:"tracking-nested-function-calls",level:2},{value:"Tracking metadata",id:"tracking-metadata",level:2},{value:"What&#39;s next?",id:"whats-next",level:2}];function l(e){const n={a:"a",admonition:"admonition",code:"code",h1:"h1",h2:"h2",img:"img",li:"li",p:"p",pre:"pre",strong:"strong",ul:"ul",...(0,i.a)(),...e.components};return(0,a.jsxs)(a.Fragment,{children:[(0,a.jsx)(n.h1,{id:"track-data-flows-and-app-metadata",children:"Track data flows and app metadata"}),"\n",(0,a.jsxs)(n.p,{children:["In the ",(0,a.jsx)(n.a,{href:"/quickstart",children:"Track LLM inputs & outputs"})," tutorial, the basics of tracking the inputs and outputs of your LLMs was covered."]}),"\n",(0,a.jsx)(n.p,{children:"In this tutorial you will learn how to:"}),"\n",(0,a.jsxs)(n.ul,{children:["\n",(0,a.jsxs)(n.li,{children:[(0,a.jsx)(n.strong,{children:"Track data"})," as it flows though your application"]}),"\n",(0,a.jsxs)(n.li,{children:[(0,a.jsx)(n.strong,{children:"Track metadata"})," at call time"]}),"\n",(0,a.jsxs)(n.li,{children:[(0,a.jsx)(n.strong,{children:"Export data"})," that was logged to Weave"]}),"\n"]}),"\n",(0,a.jsx)(n.h2,{id:"tracking-nested-function-calls",children:"Tracking nested function calls"}),"\n",(0,a.jsxs)(n.p,{children:["LLM-powered applications can contain multiple LLMs calls and additional data processing and validation logic that is important to monitor. Even deep nested call structures common in many apps, Weave will keep track of the parent-child relationships in nested functions as long as ",(0,a.jsx)(n.code,{children:"weave.op()"})," is added to every function you'd like to track."]}),"\n",(0,a.jsxs)(n.p,{children:["Building on our ",(0,a.jsx)(n.a,{href:"/quickstart",children:"basic tracing example"}),", we will now add additional logic to count the returned items from our LLM and wrap them all in a higher level function. We'll then add ",(0,a.jsx)(n.code,{children:"weave.op()"})," to trace every function, its call order and its parent-child relationship:"]}),"\n",(0,a.jsx)(n.pre,{children:(0,a.jsx)(n.code,{className:"language-python",children:'import weave\nimport json\nfrom openai import OpenAI\n\nclient = OpenAI(api_key="...")\n\n# highlight-next-line\n@weave.op()\ndef extract_dinos(sentence: str) -> dict:\n    response = client.chat.completions.create(\n        model="gpt-4o",\n        messages=[\n            {\n                "role": "system",\n                "content": """Extract any dinorsaur `name`, their `common_name`, \\\n  names and whether its `diet` is a herbivore or carnivore, in JSON format."""\n            },\n            {\n                "role": "user",\n                "content": sentence\n            }\n            ],\n            response_format={ "type": "json_object" }\n        )\n    return response.choices[0].message.content\n\n# highlight-next-line\n@weave.op()\ndef count_dinos(dino_data: dict) -> int:\n    # count the number of items in the returned list\n    k = list(dino_data.keys())[0]\n    return len(dino_data[k])\n\n# highlight-next-line\n@weave.op()\ndef dino_tracker(sentence: str) -> dict:\n    # extract dinosaurs using a LLM\n    dino_data = extract_dinos(sentence)\n    \n    # count the number of dinosaurs returned\n    dino_data = json.loads(dino_data)\n    n_dinos = count_dinos(dino_data)\n    return {"n_dinosaurs": n_dinos, "dinosaurs": dino_data}\n\n# highlight-next-line\nweave.init(\'jurassic-park\')\n\nsentence = """I watched as a Tyrannosaurus rex (T. rex) chased after a Triceratops (Trike), \\\nboth carnivore and herbivore locked in an ancient dance. Meanwhile, a gentle giant \\\nBrachiosaurus (Brachi) calmly munched on treetops, blissfully unaware of the chaos below."""\n\nresult = dino_tracker(sentence)\nprint(result)\n'})}),"\n",(0,a.jsx)(n.p,{children:(0,a.jsx)(n.strong,{children:"Nested functions"})}),"\n",(0,a.jsxs)(n.p,{children:["When you run the above code you will see the the inputs and outputs from the two nested functions (",(0,a.jsx)(n.code,{children:"extract_dinos"})," and ",(0,a.jsx)(n.code,{children:"count_dinos"}),"), as well as the automatically-logged OpenAI trace."]}),"\n",(0,a.jsx)(n.p,{children:(0,a.jsx)(n.img,{alt:"Nested Weave Trace",src:t(1627).Z+"",width:"1354",height:"1334"})}),"\n",(0,a.jsx)(n.h2,{id:"tracking-metadata",children:"Tracking metadata"}),"\n",(0,a.jsxs)(n.p,{children:["Tracking metadata can be done easily by using the ",(0,a.jsx)(n.code,{children:"weave.attributes"})," context manger and passing it a dictionary of the metadata to track at call time."]}),"\n",(0,a.jsx)(n.p,{children:"Continuing our example from above:"}),"\n",(0,a.jsx)(n.pre,{children:(0,a.jsx)(n.code,{className:"language-python",children:"import weave \n\nweave.init('jurassic-park')\n\nsentence = \"\"\"I watched as a Tyrannosaurus rex (T. rex) chased after a Triceratops (Trike), \\\nboth carnivore and herbivore locked in an ancient dance. Meanwhile, a gentle giant \\\nBrachiosaurus (Brachi) calmly munched on treetops, blissfully unaware of the chaos below.\"\"\"\n\n# track metadata alongside our previously defined function\n# highlight-next-line\nwith weave.attributes({'user_id': 'lukas', 'env': 'production'}):\n    result = dino_tracker(sentence)\n"})}),"\n",(0,a.jsxs)(n.admonition,{type:"note",children:[(0,a.jsx)(n.p,{children:"It's recommended to use metadata tracking to track metadata at run time, e.g. user ids or whether or not the call is part of the development process or is in production etc."}),(0,a.jsxs)(n.p,{children:["To track system attributes, such as a System Prompt, we recommend using ",(0,a.jsx)(n.a,{href:"guides/core-types/models",children:"weave Models"})]})]}),"\n",(0,a.jsx)(n.h2,{id:"whats-next",children:"What's next?"}),"\n",(0,a.jsxs)(n.ul,{children:["\n",(0,a.jsxs)(n.li,{children:["Follow the ",(0,a.jsx)(n.a,{href:"/tutorial-weave_models",children:"App Versioning tutorial"})," to capture, version and organize ad-hoc prompt, model, and application changes."]}),"\n"]})]})}function u(e={}){const{wrapper:n}={...(0,i.a)(),...e.components};return n?(0,a.jsx)(n,{...e,children:(0,a.jsx)(l,{...e})}):l(e)}},1627:(e,n,t)=>{t.d(n,{Z:()=>a});const a=t.p+"assets/images/tutorial_tracing_2_nested_dinos-d137d99f1797b8bd10ec6060ebf3f41d.png"},1151:(e,n,t)=>{t.d(n,{Z:()=>o,a:()=>r});var a=t(7294);const i={},s=a.createContext(i);function r(e){const n=a.useContext(s);return a.useMemo((function(){return"function"==typeof e?e(n):{...n,...e}}),[n,e])}function o(e){let n;return n=e.disableParentContext?"function"==typeof e.components?e.components(i):e.components||i:r(e.components),a.createElement(s.Provider,{value:n},e.children)}}}]);