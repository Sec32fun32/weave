"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[3861],{38661:(e,s,a)=>{a.r(s),a.d(s,{assets:()=>k,contentTitle:()=>y,default:()=>C,frontMatter:()=>g,metadata:()=>v,toc:()=>N});var n=a(85893),i=a(11151),l=a(58219),t=a.n(l),c=(a(62316),a(51039)),r=a.n(c),o=(a(82723),a(9487)),d=a.n(o),m=(a(41429),a(5397)),p=a.n(m),h=a(4667),u=a.n(h),x=a(9472),j=a.n(x),b=(a(1176),a(92503)),f=(a(12005),a(85162));const g={id:"feedback-create-feedback-create-post",title:"Feedback Create",description:"Add feedback to a call or object.",sidebar_label:"Feedback Create",hide_title:!0,hide_table_of_contents:!0,api:"eJydVl2P2joQ/SuWnynZrvqUN7ptdVu1Klq2tw8IIRMP4NaJU9tZilD++52xA3GgbPfuCyT2fJ45M5MD92LjeD7nHwDkShQ/+WLEJbjCqtorU/GcT6Rk6+6WecMEK4TWzFhmVj+g8GM+4qYGK0j+o0SNo/SysCA8LM/fa+M8Kln41YDzb43c8/zAC1N5qDw9irrWqggGsx+OojhwV2yhFPRUW3LnFbjujaJYKklvfl8DRuC8VdUGfXjlNR1MoxTD+EYcfouy1hDyRo/K77POCl+0I74D8QhLC+unDH4nIXaPQkN7QTnPsmxoOItYZZUoIZdqg3kHXwERY0PS1f4rupyf+2xHp5Oq0Zq3iz6Ku059GMMnUQGblcpvg48T/NHK9ZyOHGAPJDC0WTTOmzLYq8VeG5HCHZNL4e5EBjYO/Cdgpfmj0A1gGgT1atk4sF3xXoLA9xX7hhZiYYfEfWdYZTxz4JlUFgPU+zGbgX1E8Z1CCosGU0KWEZ/3rDZ1o5GezG+VY2sFWo55i0GeJ0m8RXuSYEnYlxLnHPQetMUl3KGIcA+/0Fubmve2gXDgalO5SPfbmxv6G2Y6a4oCnFs3GhkZhdHlCxvq6UZCnI+0BbkU/k+ya2NLuuEShV55VQI/oyxINvH8ggBXm60v8v/j39/KF8qWJDMI6FlFc1Q09PLm9vayLv8KrWRAnb23NvTpC4siwQulQ3k8lO5SQJticPuMXlIYyQZs7MTuTFgr9gmQn00MkHAv3eapIn1BBooN8JOx66IBjDhl/lYhyiu67uSSWvTwRnSvp/EuwvcnZ0eRfx4ephcGY20dFI3FYR7gJLm3wimEe76gSVSC3xpae91aqwXO3ZxnxwmQRX5xskOzJ47CxmI1+db72uG28FYUMN6JSq7GQoUBd3Q6I0bEGieuT9iSBTIdpPB9Fe4paqLUfb9i38dBfL4y++Ika68/PO2npLuH66S/6PvyrLF77iHn1iZEf2wn4fxk+hG1CZnYNTfj1+Ob0OgIaClCX9DeTDfU3RHTQcMlHxHP+mzpMvDw22e1FirQPFTm0JVxfkr3NCiIgVsqNV4eDog3fLO6bekYwbbEEnx8FFaJFeU4p/bagpDYav0SvIuBvupWbdyJ+eVMoH6NGhOc8bV/UjZl4/Tr7AGFV93XVWkk6VixowbD35yH7zbSDuQKZzhHRLVpqI1zHm0SlXBRbhPORY6Nuv9kxuDQSeIL4Khigso0vamECNOoS6fpjtKJdFV/KpzbGSsT/bo7ovHVtv8BR/ayfw==",sidebar_class_name:"post api-method",info_path:"reference/service-api/fastapi",custom_edit_url:null},y=void 0,v={id:"reference/service-api/feedback-create-feedback-create-post",title:"Feedback Create",description:"Add feedback to a call or object.",source:"@site/docs/reference/service-api/feedback-create-feedback-create-post.api.mdx",sourceDirName:"reference/service-api",slug:"/reference/service-api/feedback-create-feedback-create-post",permalink:"/weave/reference/service-api/feedback-create-feedback-create-post",draft:!1,unlisted:!1,editUrl:null,tags:[],version:"current",frontMatter:{id:"feedback-create-feedback-create-post",title:"Feedback Create",description:"Add feedback to a call or object.",sidebar_label:"Feedback Create",hide_title:!0,hide_table_of_contents:!0,api:"eJydVl2P2joQ/SuWnynZrvqUN7ptdVu1Klq2tw8IIRMP4NaJU9tZilD++52xA3GgbPfuCyT2fJ45M5MD92LjeD7nHwDkShQ/+WLEJbjCqtorU/GcT6Rk6+6WecMEK4TWzFhmVj+g8GM+4qYGK0j+o0SNo/SysCA8LM/fa+M8Kln41YDzb43c8/zAC1N5qDw9irrWqggGsx+OojhwV2yhFPRUW3LnFbjujaJYKklvfl8DRuC8VdUGfXjlNR1MoxTD+EYcfouy1hDyRo/K77POCl+0I74D8QhLC+unDH4nIXaPQkN7QTnPsmxoOItYZZUoIZdqg3kHXwERY0PS1f4rupyf+2xHp5Oq0Zq3iz6Ku059GMMnUQGblcpvg48T/NHK9ZyOHGAPJDC0WTTOmzLYq8VeG5HCHZNL4e5EBjYO/Cdgpfmj0A1gGgT1atk4sF3xXoLA9xX7hhZiYYfEfWdYZTxz4JlUFgPU+zGbgX1E8Z1CCosGU0KWEZ/3rDZ1o5GezG+VY2sFWo55i0GeJ0m8RXuSYEnYlxLnHPQetMUl3KGIcA+/0Fubmve2gXDgalO5SPfbmxv6G2Y6a4oCnFs3GhkZhdHlCxvq6UZCnI+0BbkU/k+ya2NLuuEShV55VQI/oyxINvH8ggBXm60v8v/j39/KF8qWJDMI6FlFc1Q09PLm9vayLv8KrWRAnb23NvTpC4siwQulQ3k8lO5SQJticPuMXlIYyQZs7MTuTFgr9gmQn00MkHAv3eapIn1BBooN8JOx66IBjDhl/lYhyiu67uSSWvTwRnSvp/EuwvcnZ0eRfx4ephcGY20dFI3FYR7gJLm3wimEe76gSVSC3xpae91aqwXO3ZxnxwmQRX5xskOzJ47CxmI1+db72uG28FYUMN6JSq7GQoUBd3Q6I0bEGieuT9iSBTIdpPB9Fe4paqLUfb9i38dBfL4y++Ika68/PO2npLuH66S/6PvyrLF77iHn1iZEf2wn4fxk+hG1CZnYNTfj1+Ob0OgIaClCX9DeTDfU3RHTQcMlHxHP+mzpMvDw22e1FirQPFTm0JVxfkr3NCiIgVsqNV4eDog3fLO6bekYwbbEEnx8FFaJFeU4p/bagpDYav0SvIuBvupWbdyJ+eVMoH6NGhOc8bV/UjZl4/Tr7AGFV93XVWkk6VixowbD35yH7zbSDuQKZzhHRLVpqI1zHm0SlXBRbhPORY6Nuv9kxuDQSeIL4Khigso0vamECNOoS6fpjtKJdFV/KpzbGSsT/bo7ovHVtv8BR/ayfw==",sidebar_class_name:"post api-method",info_path:"reference/service-api/fastapi",custom_edit_url:null},sidebar:"serviceApiSidebar",previous:{title:"File Content",permalink:"/weave/reference/service-api/file-content-file-content-post"},next:{title:"Feedback Query",permalink:"/weave/reference/service-api/feedback-query-feedback-query-post"}},k={},N=[];function _(e){const s={p:"p",...(0,i.a)(),...e.components},{Details:a}=s;return a||function(e,s){throw new Error("Expected "+(s?"component":"object")+" `"+e+"` to be defined: you likely forgot to import, pass, or provide it.")}("Details",!0),(0,n.jsxs)(n.Fragment,{children:[(0,n.jsx)(b.default,{as:"h1",className:"openapi__heading",children:"Feedback Create"}),"\n",(0,n.jsx)(r(),{method:"post",path:"/feedback/create"}),"\n",(0,n.jsx)(s.p,{children:"Add feedback to a call or object."}),"\n",(0,n.jsx)(b.default,{id:"request",as:"h2",className:"openapi-tabs__heading",children:"Request"}),"\n",(0,n.jsx)(d(),{className:"openapi-tabs__mime",children:(0,n.jsx)(f.default,{label:"application/json",value:"application/json-schema",children:(0,n.jsxs)(a,{style:{},className:"openapi-markdown__details mime","data-collapsed":!1,open:!0,children:[(0,n.jsxs)("summary",{style:{},className:"openapi-markdown__details-summary-mime",children:[(0,n.jsx)("h3",{className:"openapi-markdown__details-summary-header-body",children:(0,n.jsx)(s.p,{children:"Body"})}),(0,n.jsx)("strong",{className:"openapi-schema__required",children:(0,n.jsx)(s.p,{children:"required"})})]}),(0,n.jsx)("div",{style:{textAlign:"left",marginLeft:"1rem"}}),(0,n.jsxs)("ul",{style:{marginLeft:"1rem"},children:[(0,n.jsx)(u(),{collapsible:!1,name:"project_id",required:!0,schemaName:"Project Id (string)",qualifierMessage:void 0,schema:{type:"string",title:"Project Id",examples:["entity/project"]}}),(0,n.jsx)(u(),{collapsible:!1,name:"weave_ref",required:!0,schemaName:"Weave Ref (string)",qualifierMessage:void 0,schema:{type:"string",title:"Weave Ref",examples:["weave:///entity/project/object/name:digest"]}}),(0,n.jsx)(u(),{collapsible:!0,className:"schemaItem",children:(0,n.jsxs)(a,{style:{},className:"openapi-markdown__details",children:[(0,n.jsxs)("summary",{style:{},children:[(0,n.jsx)("strong",{children:(0,n.jsx)(s.p,{children:"creator"})}),(0,n.jsx)("span",{style:{opacity:"0.6"},children:(0,n.jsx)(s.p,{children:"object"})})]}),(0,n.jsx)("div",{style:{marginLeft:"1rem"}}),(0,n.jsxs)("div",{children:[(0,n.jsx)("span",{className:"badge badge--info",children:(0,n.jsx)(s.p,{children:"anyOf"})}),(0,n.jsx)(j(),{children:(0,n.jsx)(f.default,{label:"MOD1",value:"0-item-properties",children:(0,n.jsx)("div",{style:{marginTop:".5rem",marginBottom:".5rem"},children:(0,n.jsx)(s.p,{children:"string"})})})})]})]})}),(0,n.jsx)(u(),{collapsible:!1,name:"feedback_type",required:!0,schemaName:"Feedback Type (string)",qualifierMessage:void 0,schema:{type:"string",title:"Feedback Type",examples:["custom"]}}),(0,n.jsx)(u(),{collapsible:!1,name:"payload",required:!0,schemaName:"object",qualifierMessage:void 0,schema:{type:"object",title:"Payload",examples:[{key:"value"}]}}),(0,n.jsx)(u(),{collapsible:!0,className:"schemaItem",children:(0,n.jsxs)(a,{style:{},className:"openapi-markdown__details",children:[(0,n.jsxs)("summary",{style:{},children:[(0,n.jsx)("strong",{children:(0,n.jsx)(s.p,{children:"wb_user_id"})}),(0,n.jsx)("span",{style:{opacity:"0.6"},children:(0,n.jsx)(s.p,{children:"object"})})]}),(0,n.jsx)("div",{style:{marginLeft:"1rem"},children:(0,n.jsx)("div",{style:{marginTop:".5rem",marginBottom:".5rem"},children:(0,n.jsx)(s.p,{children:"Do not set directly. Server will automatically populate this field."})})}),(0,n.jsxs)("div",{children:[(0,n.jsx)("span",{className:"badge badge--info",children:(0,n.jsx)(s.p,{children:"anyOf"})}),(0,n.jsx)(j(),{children:(0,n.jsx)(f.default,{label:"MOD1",value:"0-item-properties",children:(0,n.jsx)("div",{style:{marginTop:".5rem",marginBottom:".5rem"},children:(0,n.jsx)(s.p,{children:"string"})})})})]})]})})]})]})})}),"\n",(0,n.jsx)("div",{children:(0,n.jsx)("div",{children:(0,n.jsxs)(t(),{label:void 0,id:void 0,children:[(0,n.jsxs)(f.default,{label:"200",value:"200",children:[(0,n.jsx)("div",{children:(0,n.jsx)(s.p,{children:"Successful Response"})}),(0,n.jsx)("div",{children:(0,n.jsx)(d(),{className:"openapi-tabs__mime",schemaType:"response",children:(0,n.jsx)(f.default,{label:"application/json",value:"application/json",children:(0,n.jsxs)(j(),{className:"openapi-tabs__schema",children:[(0,n.jsx)(f.default,{label:"Schema",value:"Schema",children:(0,n.jsxs)(a,{style:{},className:"openapi-markdown__details response","data-collapsed":!1,open:!0,children:[(0,n.jsx)("summary",{style:{},className:"openapi-markdown__details-summary-response",children:(0,n.jsx)("strong",{children:(0,n.jsx)(s.p,{children:"Schema"})})}),(0,n.jsx)("div",{style:{textAlign:"left",marginLeft:"1rem"}}),(0,n.jsxs)("ul",{style:{marginLeft:"1rem"},children:[(0,n.jsx)(u(),{collapsible:!1,name:"id",required:!0,schemaName:"Id (string)",qualifierMessage:void 0,schema:{type:"string",title:"Id"}}),(0,n.jsx)(u(),{collapsible:!1,name:"created_at",required:!0,schemaName:"date-time",qualifierMessage:void 0,schema:{type:"string",format:"date-time",title:"Created At"}}),(0,n.jsx)(u(),{collapsible:!1,name:"wb_user_id",required:!0,schemaName:"Wb User Id (string)",qualifierMessage:void 0,schema:{type:"string",title:"Wb User Id"}}),(0,n.jsx)(u(),{collapsible:!1,name:"payload",required:!0,schemaName:"object",qualifierMessage:void 0,schema:{type:"object",title:"Payload"}})]})]})}),(0,n.jsx)(f.default,{label:"Example (from schema)",value:"Example (from schema)",children:(0,n.jsx)(p(),{responseExample:'{\n  "id": "string",\n  "created_at": "2024-08-13T01:11:32.989Z",\n  "wb_user_id": "string",\n  "payload": {}\n}',language:"json"})})]})})})})]}),(0,n.jsxs)(f.default,{label:"422",value:"422",children:[(0,n.jsx)("div",{children:(0,n.jsx)(s.p,{children:"Validation Error"})}),(0,n.jsx)("div",{children:(0,n.jsx)(d(),{className:"openapi-tabs__mime",schemaType:"response",children:(0,n.jsx)(f.default,{label:"application/json",value:"application/json",children:(0,n.jsxs)(j(),{className:"openapi-tabs__schema",children:[(0,n.jsx)(f.default,{label:"Schema",value:"Schema",children:(0,n.jsxs)(a,{style:{},className:"openapi-markdown__details response","data-collapsed":!1,open:!0,children:[(0,n.jsx)("summary",{style:{},className:"openapi-markdown__details-summary-response",children:(0,n.jsx)("strong",{children:(0,n.jsx)(s.p,{children:"Schema"})})}),(0,n.jsx)("div",{style:{textAlign:"left",marginLeft:"1rem"}}),(0,n.jsx)("ul",{style:{marginLeft:"1rem"},children:(0,n.jsx)(u(),{collapsible:!0,className:"schemaItem",children:(0,n.jsxs)(a,{style:{},className:"openapi-markdown__details",children:[(0,n.jsx)("summary",{style:{},children:(0,n.jsxs)("span",{className:"openapi-schema__container",children:[(0,n.jsx)("strong",{className:"openapi-schema__property",children:(0,n.jsx)(s.p,{children:"detail"})}),(0,n.jsx)("span",{className:"openapi-schema__name",children:(0,n.jsx)(s.p,{children:"object[]"})})]})}),(0,n.jsxs)("div",{style:{marginLeft:"1rem"},children:[(0,n.jsx)("li",{children:(0,n.jsx)("div",{style:{fontSize:"var(--ifm-code-font-size)",opacity:"0.6",marginLeft:"-.5rem",paddingBottom:".5rem"},children:(0,n.jsx)(s.p,{children:"Array ["})})}),(0,n.jsx)(u(),{collapsible:!0,className:"schemaItem",children:(0,n.jsxs)(a,{style:{},className:"openapi-markdown__details",children:[(0,n.jsx)("summary",{style:{},children:(0,n.jsxs)("span",{className:"openapi-schema__container",children:[(0,n.jsx)("strong",{className:"openapi-schema__property",children:(0,n.jsx)(s.p,{children:"loc"})}),(0,n.jsx)("span",{className:"openapi-schema__name",children:(0,n.jsx)(s.p,{children:"object[]"})}),(0,n.jsx)("span",{className:"openapi-schema__divider"}),(0,n.jsx)("span",{className:"openapi-schema__required",children:(0,n.jsx)(s.p,{children:"required"})})]})}),(0,n.jsxs)("div",{style:{marginLeft:"1rem"},children:[(0,n.jsx)("li",{children:(0,n.jsx)("div",{style:{fontSize:"var(--ifm-code-font-size)",opacity:"0.6",marginLeft:"-.5rem",paddingBottom:".5rem"},children:(0,n.jsx)(s.p,{children:"Array ["})})}),(0,n.jsxs)("div",{children:[(0,n.jsx)("span",{className:"badge badge--info",children:(0,n.jsx)(s.p,{children:"anyOf"})}),(0,n.jsxs)(j(),{children:[(0,n.jsx)(f.default,{label:"MOD1",value:"0-item-properties",children:(0,n.jsx)("div",{style:{marginTop:".5rem",marginBottom:".5rem"},children:(0,n.jsx)(s.p,{children:"string"})})}),(0,n.jsx)(f.default,{label:"MOD2",value:"1-item-properties",children:(0,n.jsx)("div",{style:{marginTop:".5rem",marginBottom:".5rem"},children:(0,n.jsx)(s.p,{children:"integer"})})})]})]}),(0,n.jsx)("li",{children:(0,n.jsx)("div",{style:{fontSize:"var(--ifm-code-font-size)",opacity:"0.6",marginLeft:"-.5rem"},children:(0,n.jsx)(s.p,{children:"]"})})})]})]})}),(0,n.jsx)(u(),{collapsible:!1,name:"msg",required:!0,schemaName:"Message (string)",qualifierMessage:void 0,schema:{type:"string",title:"Message"}}),(0,n.jsx)(u(),{collapsible:!1,name:"type",required:!0,schemaName:"Error Type (string)",qualifierMessage:void 0,schema:{type:"string",title:"Error Type"}}),(0,n.jsx)("li",{children:(0,n.jsx)("div",{style:{fontSize:"var(--ifm-code-font-size)",opacity:"0.6",marginLeft:"-.5rem"},children:(0,n.jsx)(s.p,{children:"]"})})})]})]})})})]})}),(0,n.jsx)(f.default,{label:"Example (from schema)",value:"Example (from schema)",children:(0,n.jsx)(p(),{responseExample:'{\n  "detail": [\n    {\n      "loc": [\n        "string",\n        0\n      ],\n      "msg": "string",\n      "type": "string"\n    }\n  ]\n}',language:"json"})})]})})})})]})]})})})]})}function C(e={}){const{wrapper:s}={...(0,i.a)(),...e.components};return s?(0,n.jsx)(s,{...e,children:(0,n.jsx)(_,{...e})}):_(e)}},13155:(e,s,a)=>{a.r(s),a.d(s,{default:()=>I});var n=a(67294),i=a(72389),l=a(90512),t=a(66412),c=a(35281),r=a(37016);const o={codeBlockContainer:"codeBlockContainer_APcc"};var d=a(85893);function m(e){let{as:s,...a}=e;const n=(0,t.p)(),i=(0,r.QC)(n);return(0,d.jsx)(s,{...a,style:i,className:(0,l.Z)(a.className,o.codeBlockContainer,c.k.common.codeBlock)})}const p={codeBlockContent:"codeBlockContent_m3Ux",codeBlockTitle:"codeBlockTitle_P25_",codeBlock:"codeBlock_qGQc",codeBlockStandalone:"codeBlockStandalone_zC50",codeBlockLines:"codeBlockLines_p187",codeBlockLinesWithNumbering:"codeBlockLinesWithNumbering_OFgW",buttonGroup:"buttonGroup_6DOT"};function h(e){let{children:s,className:a}=e;return(0,d.jsx)(m,{as:"pre",tabIndex:0,className:(0,l.Z)(p.codeBlockStandalone,"thin-scrollbar",a),children:(0,d.jsx)("code",{className:p.codeBlockLines,children:s})})}var u=a(86668),x=a(85448),j=a(42573);const b={codeLine:"codeLine_iPqp",codeLineNumber:"codeLineNumber_F4P7",codeLineContent:"codeLineContent_pOih"};function f(e){let{line:s,classNames:a,showLineNumbers:n,getLineProps:i,getTokenProps:t}=e;1===s.length&&"\n"===s[0].content&&(s[0].content="");const c=i({line:s,className:(0,l.Z)(a,n&&b.codeLine)}),r=s.map(((e,s)=>(0,d.jsx)("span",{...t({token:e,key:s})},s)));return(0,d.jsxs)("span",{...c,children:[n?(0,d.jsxs)(d.Fragment,{children:[(0,d.jsx)("span",{className:b.codeLineNumber}),(0,d.jsx)("span",{className:b.codeLineContent,children:r})]}):r,(0,d.jsx)("br",{})]})}var g=a(10195),y=a(95999),v=a(30345),k=a(37666);const N={copyButtonCopied:"copyButtonCopied__QnY",copyButtonIcons:"copyButtonIcons_FhaS",copyButtonIcon:"copyButtonIcon_phi_",copyButtonSuccessIcon:"copyButtonSuccessIcon_FfTR"};function _(e){let{code:s,className:a}=e;const[i,t]=(0,n.useState)(!1),c=(0,n.useRef)(void 0),r=(0,n.useCallback)((()=>{window.analytics?.track("Weave Docs: Code copied",{code:"string"==typeof s?s.slice(0,100):"code is not string"}),(0,g.default)(s),t(!0),c.current=window.setTimeout((()=>{t(!1)}),1e3)}),[s]);return(0,n.useEffect)((()=>()=>window.clearTimeout(c.current)),[]),(0,d.jsx)("button",{type:"button","aria-label":i?(0,y.translate)({id:"theme.CodeBlock.copied",message:"Copied",description:"The copied button label on code blocks"}):(0,y.translate)({id:"theme.CodeBlock.copyButtonAriaLabel",message:"Copy code to clipboard",description:"The ARIA label for copy code blocks button"}),title:(0,y.translate)({id:"theme.CodeBlock.copy",message:"Copy",description:"The copy button label on code blocks"}),className:(0,l.Z)("clean-btn",a,N.copyButton,i&&N.copyButtonCopied),onClick:r,children:(0,d.jsxs)("span",{className:N.copyButtonIcons,"aria-hidden":"true",children:[(0,d.jsx)(v.Z,{className:N.copyButtonIcon}),(0,d.jsx)(k.Z,{className:N.copyButtonSuccessIcon})]})})}var C=a(96043);const B={wordWrapButtonIcon:"wordWrapButtonIcon_iowe",wordWrapButtonEnabled:"wordWrapButtonEnabled_gY8A"};function L(e){let{className:s,onClick:a,isEnabled:n}=e;const i=(0,y.translate)({id:"theme.CodeBlock.wordWrapToggle",message:"Toggle word wrap",description:"The title attribute for toggle word wrapping button of code block lines"});return(0,d.jsx)("button",{type:"button",onClick:a,className:(0,l.Z)("clean-btn",s,n&&B.wordWrapButtonEnabled),"aria-label":i,title:i,children:(0,d.jsx)(C.Z,{className:B.wordWrapButtonIcon,"aria-hidden":"true"})})}function w(e){let{children:s,className:a="",metastring:n,title:i,showLineNumbers:c,language:o}=e;const{prism:{defaultLanguage:h,magicComments:b}}=(0,u.L)(),g=function(e){return e?.toLowerCase()}(o??(0,r.Vo)(a)??h),y=(0,t.p)(),v=(0,x.F)(),k=(0,r.bc)(n)||i,{lineClassNames:N,code:C}=(0,r.nZ)(s,{metastring:n,language:g,magicComments:b}),B=c??(0,r.nt)(n);return(0,d.jsxs)(m,{as:"div",className:(0,l.Z)(a,g&&!a.includes(`language-${g}`)&&`language-${g}`),children:[k&&(0,d.jsx)("div",{className:p.codeBlockTitle,children:k}),(0,d.jsxs)("div",{className:p.codeBlockContent,children:[(0,d.jsx)(j.Highlight,{theme:y,code:C,language:g??"text",children:e=>{let{className:s,style:a,tokens:n,getLineProps:i,getTokenProps:t}=e;return(0,d.jsx)("pre",{tabIndex:0,ref:v.codeBlockRef,className:(0,l.Z)(s,p.codeBlock,"thin-scrollbar"),style:a,children:(0,d.jsx)("code",{className:(0,l.Z)(p.codeBlockLines,B&&p.codeBlockLinesWithNumbering),children:n.map(((e,s)=>(0,d.jsx)(f,{line:e,getLineProps:i,getTokenProps:t,classNames:N[s],showLineNumbers:B},s)))})})}}),(0,d.jsxs)("div",{className:p.buttonGroup,children:[(v.isEnabled||v.isCodeScrollable)&&(0,d.jsx)(L,{className:p.codeButton,onClick:()=>v.toggle(),isEnabled:v.isEnabled}),(0,d.jsx)(_,{className:p.codeButton,code:C})]})]})]})}function I(e){let{children:s,...a}=e;const l=(0,i.default)(),t=function(e){return n.Children.toArray(e).some((e=>(0,n.isValidElement)(e)))?e:Array.isArray(e)?e.join(""):e}(s),c="string"==typeof t?w:h;return(0,d.jsx)(c,{...a,children:t},String(l))}}}]);