import{j as l}from"./vendor-charts-ByizP3Tw.js";import{r as w}from"./vendor-react-4UoDTOSx.js";import{z as U}from"./index-GloXtFG-.js";import{aZ as oe,i as tt,X as nt,u as rt}from"./vendor-ui-IuxYI6qn.js";import"./vendor-state-zRiuN2YE.js";import"./vendor-http-B9ygI19o.js";import"./vendor-date-C57suUB-.js";/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Ie=function(e){const t=[];let n=0;for(let r=0;r<e.length;r++){let a=e.charCodeAt(r);a<128?t[n++]=a:a<2048?(t[n++]=a>>6|192,t[n++]=a&63|128):(a&64512)===55296&&r+1<e.length&&(e.charCodeAt(r+1)&64512)===56320?(a=65536+((a&1023)<<10)+(e.charCodeAt(++r)&1023),t[n++]=a>>18|240,t[n++]=a>>12&63|128,t[n++]=a>>6&63|128,t[n++]=a&63|128):(t[n++]=a>>12|224,t[n++]=a>>6&63|128,t[n++]=a&63|128)}return t},at=function(e){const t=[];let n=0,r=0;for(;n<e.length;){const a=e[n++];if(a<128)t[r++]=String.fromCharCode(a);else if(a>191&&a<224){const s=e[n++];t[r++]=String.fromCharCode((a&31)<<6|s&63)}else if(a>239&&a<365){const s=e[n++],o=e[n++],i=e[n++],c=((a&7)<<18|(s&63)<<12|(o&63)<<6|i&63)-65536;t[r++]=String.fromCharCode(55296+(c>>10)),t[r++]=String.fromCharCode(56320+(c&1023))}else{const s=e[n++],o=e[n++];t[r++]=String.fromCharCode((a&15)<<12|(s&63)<<6|o&63)}}return t.join("")},st={byteToCharMap_:null,charToByteMap_:null,byteToCharMapWebSafe_:null,charToByteMapWebSafe_:null,ENCODED_VALS_BASE:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",get ENCODED_VALS(){return this.ENCODED_VALS_BASE+"+/="},get ENCODED_VALS_WEBSAFE(){return this.ENCODED_VALS_BASE+"-_."},HAS_NATIVE_SUPPORT:typeof atob=="function",encodeByteArray(e,t){if(!Array.isArray(e))throw Error("encodeByteArray takes an array as a parameter");this.init_();const n=t?this.byteToCharMapWebSafe_:this.byteToCharMap_,r=[];for(let a=0;a<e.length;a+=3){const s=e[a],o=a+1<e.length,i=o?e[a+1]:0,c=a+2<e.length,d=c?e[a+2]:0,u=s>>2,T=(s&3)<<4|i>>4;let k=(i&15)<<2|d>>6,N=d&63;c||(N=64,o||(k=64)),r.push(n[u],n[T],n[k],n[N])}return r.join("")},encodeString(e,t){return this.HAS_NATIVE_SUPPORT&&!t?btoa(e):this.encodeByteArray(Ie(e),t)},decodeString(e,t){return this.HAS_NATIVE_SUPPORT&&!t?atob(e):at(this.decodeStringToByteArray(e,t))},decodeStringToByteArray(e,t){this.init_();const n=t?this.charToByteMapWebSafe_:this.charToByteMap_,r=[];for(let a=0;a<e.length;){const s=n[e.charAt(a++)],i=a<e.length?n[e.charAt(a)]:0;++a;const d=a<e.length?n[e.charAt(a)]:64;++a;const T=a<e.length?n[e.charAt(a)]:64;if(++a,s==null||i==null||d==null||T==null)throw new ot;const k=s<<2|i>>4;if(r.push(k),d!==64){const N=i<<4&240|d>>2;if(r.push(N),T!==64){const et=d<<6&192|T;r.push(et)}}}return r},init_(){if(!this.byteToCharMap_){this.byteToCharMap_={},this.charToByteMap_={},this.byteToCharMapWebSafe_={},this.charToByteMapWebSafe_={};for(let e=0;e<this.ENCODED_VALS.length;e++)this.byteToCharMap_[e]=this.ENCODED_VALS.charAt(e),this.charToByteMap_[this.byteToCharMap_[e]]=e,this.byteToCharMapWebSafe_[e]=this.ENCODED_VALS_WEBSAFE.charAt(e),this.charToByteMapWebSafe_[this.byteToCharMapWebSafe_[e]]=e,e>=this.ENCODED_VALS_BASE.length&&(this.charToByteMap_[this.ENCODED_VALS_WEBSAFE.charAt(e)]=e,this.charToByteMapWebSafe_[this.ENCODED_VALS.charAt(e)]=e)}}};class ot extends Error{constructor(){super(...arguments),this.name="DecodeBase64StringError"}}const it=function(e){const t=Ie(e);return st.encodeByteArray(t,!0)},Te=function(e){return it(e).replace(/\./g,"")};function ct(){try{return typeof indexedDB=="object"}catch{return!1}}function ut(){return new Promise((e,t)=>{try{let n=!0;const r="validate-browser-context-for-indexeddb-analytics-module",a=self.indexedDB.open(r);a.onsuccess=()=>{a.result.close(),n||self.indexedDB.deleteDatabase(r),e(!0)},a.onupgradeneeded=()=>{n=!1},a.onerror=()=>{var s;t(((s=a.error)===null||s===void 0?void 0:s.message)||"")}}catch(n){t(n)}})}/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const dt="FirebaseError";class I extends Error{constructor(t,n,r){super(n),this.code=t,this.customData=r,this.name=dt,Object.setPrototypeOf(this,I.prototype),Error.captureStackTrace&&Error.captureStackTrace(this,B.prototype.create)}}class B{constructor(t,n,r){this.service=t,this.serviceName=n,this.errors=r}create(t,...n){const r=n[0]||{},a=`${this.service}/${t}`,s=this.errors[t],o=s?lt(s,r):"Error",i=`${this.serviceName}: ${o} (${a}).`;return new I(a,i,r)}}function lt(e,t){return e.replace(ft,(n,r)=>{const a=t[r];return a!=null?String(a):`<${r}?>`})}const ft=/\{\$([^}]+)}/g;class E{constructor(t,n,r){this.name=t,this.instanceFactory=n,this.type=r,this.multipleInstances=!1,this.serviceProps={},this.instantiationMode="LAZY",this.onInstanceCreated=null}setInstantiationMode(t){return this.instantiationMode=t,this}setMultipleInstances(t){return this.multipleInstances=t,this}setServiceProps(t){return this.serviceProps=t,this}setInstanceCreatedCallback(t){return this.onInstanceCreated=t,this}}/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */var f;(function(e){e[e.DEBUG=0]="DEBUG",e[e.VERBOSE=1]="VERBOSE",e[e.INFO=2]="INFO",e[e.WARN=3]="WARN",e[e.ERROR=4]="ERROR",e[e.SILENT=5]="SILENT"})(f||(f={}));const ht={debug:f.DEBUG,verbose:f.VERBOSE,info:f.INFO,warn:f.WARN,error:f.ERROR,silent:f.SILENT},pt=f.INFO,gt={[f.DEBUG]:"log",[f.VERBOSE]:"log",[f.INFO]:"info",[f.WARN]:"warn",[f.ERROR]:"error"},bt=(e,t,...n)=>{if(t<e.logLevel)return;const r=new Date().toISOString(),a=gt[t];if(a)console[a](`[${r}]  ${e.name}:`,...n);else throw new Error(`Attempted to log a message with an invalid logType (value: ${t})`)};class mt{constructor(t){this.name=t,this._logLevel=pt,this._logHandler=bt,this._userLogHandler=null}get logLevel(){return this._logLevel}set logLevel(t){if(!(t in f))throw new TypeError(`Invalid value "${t}" assigned to \`logLevel\``);this._logLevel=t}setLogLevel(t){this._logLevel=typeof t=="string"?ht[t]:t}get logHandler(){return this._logHandler}set logHandler(t){if(typeof t!="function")throw new TypeError("Value assigned to `logHandler` must be a function");this._logHandler=t}get userLogHandler(){return this._userLogHandler}set userLogHandler(t){this._userLogHandler=t}debug(...t){this._userLogHandler&&this._userLogHandler(this,f.DEBUG,...t),this._logHandler(this,f.DEBUG,...t)}log(...t){this._userLogHandler&&this._userLogHandler(this,f.VERBOSE,...t),this._logHandler(this,f.VERBOSE,...t)}info(...t){this._userLogHandler&&this._userLogHandler(this,f.INFO,...t),this._logHandler(this,f.INFO,...t)}warn(...t){this._userLogHandler&&this._userLogHandler(this,f.WARN,...t),this._logHandler(this,f.WARN,...t)}error(...t){this._userLogHandler&&this._userLogHandler(this,f.ERROR,...t),this._logHandler(this,f.ERROR,...t)}}const wt=(e,t)=>t.some(n=>e instanceof n);let ie,ce;function yt(){return ie||(ie=[IDBDatabase,IDBObjectStore,IDBIndex,IDBCursor,IDBTransaction])}function Et(){return ce||(ce=[IDBCursor.prototype.advance,IDBCursor.prototype.continue,IDBCursor.prototype.continuePrimaryKey])}const Ae=new WeakMap,G=new WeakMap,Ce=new WeakMap,$=new WeakMap,X=new WeakMap;function St(e){const t=new Promise((n,r)=>{const a=()=>{e.removeEventListener("success",s),e.removeEventListener("error",o)},s=()=>{n(g(e.result)),a()},o=()=>{r(e.error),a()};e.addEventListener("success",s),e.addEventListener("error",o)});return t.then(n=>{n instanceof IDBCursor&&Ae.set(n,e)}).catch(()=>{}),X.set(t,e),t}function vt(e){if(G.has(e))return;const t=new Promise((n,r)=>{const a=()=>{e.removeEventListener("complete",s),e.removeEventListener("error",o),e.removeEventListener("abort",o)},s=()=>{n(),a()},o=()=>{r(e.error||new DOMException("AbortError","AbortError")),a()};e.addEventListener("complete",s),e.addEventListener("error",o),e.addEventListener("abort",o)});G.set(e,t)}let J={get(e,t,n){if(e instanceof IDBTransaction){if(t==="done")return G.get(e);if(t==="objectStoreNames")return e.objectStoreNames||Ce.get(e);if(t==="store")return n.objectStoreNames[1]?void 0:n.objectStore(n.objectStoreNames[0])}return g(e[t])},set(e,t,n){return e[t]=n,!0},has(e,t){return e instanceof IDBTransaction&&(t==="done"||t==="store")?!0:t in e}};function _t(e){J=e(J)}function It(e){return e===IDBDatabase.prototype.transaction&&!("objectStoreNames"in IDBTransaction.prototype)?function(t,...n){const r=e.call(P(this),t,...n);return Ce.set(r,t.sort?t.sort():[t]),g(r)}:Et().includes(e)?function(...t){return e.apply(P(this),t),g(Ae.get(this))}:function(...t){return g(e.apply(P(this),t))}}function Tt(e){return typeof e=="function"?It(e):(e instanceof IDBTransaction&&vt(e),wt(e,yt())?new Proxy(e,J):e)}function g(e){if(e instanceof IDBRequest)return St(e);if($.has(e))return $.get(e);const t=Tt(e);return t!==e&&($.set(e,t),X.set(t,e)),t}const P=e=>X.get(e);function x(e,t,{blocked:n,upgrade:r,blocking:a,terminated:s}={}){const o=indexedDB.open(e,t),i=g(o);return r&&o.addEventListener("upgradeneeded",c=>{r(g(o.result),c.oldVersion,c.newVersion,g(o.transaction),c)}),n&&o.addEventListener("blocked",c=>n(c.oldVersion,c.newVersion,c)),i.then(c=>{s&&c.addEventListener("close",()=>s()),a&&c.addEventListener("versionchange",d=>a(d.oldVersion,d.newVersion,d))}).catch(()=>{}),i}function j(e,{blocked:t}={}){const n=indexedDB.deleteDatabase(e);return t&&n.addEventListener("blocked",r=>t(r.oldVersion,r)),g(n).then(()=>{})}const At=["get","getKey","getAll","getAllKeys","count"],Ct=["put","add","delete","clear"],L=new Map;function ue(e,t){if(!(e instanceof IDBDatabase&&!(t in e)&&typeof t=="string"))return;if(L.get(t))return L.get(t);const n=t.replace(/FromIndex$/,""),r=t!==n,a=Ct.includes(n);if(!(n in(r?IDBIndex:IDBObjectStore).prototype)||!(a||At.includes(n)))return;const s=async function(o,...i){const c=this.transaction(o,a?"readwrite":"readonly");let d=c.store;return r&&(d=d.index(i.shift())),(await Promise.all([d[n](...i),a&&c.done]))[0]};return L.set(t,s),s}_t(e=>({...e,get:(t,n,r)=>ue(t,n)||e.get(t,n,r),has:(t,n)=>!!ue(t,n)||e.has(t,n)}));/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class Dt{constructor(t){this.container=t}getPlatformInfoString(){return this.container.getProviders().map(n=>{if(kt(n)){const r=n.getImmediate();return`${r.library}/${r.version}`}else return null}).filter(n=>n).join(" ")}}function kt(e){const t=e.getComponent();return(t==null?void 0:t.type)==="VERSION"}const z="@firebase/app",de="0.10.13";/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const b=new mt("@firebase/app"),Nt="@firebase/app-compat",Ot="@firebase/analytics-compat",Bt="@firebase/analytics",xt="@firebase/app-check-compat",Mt="@firebase/app-check",Rt="@firebase/auth",$t="@firebase/auth-compat",Pt="@firebase/database",jt="@firebase/data-connect",Lt="@firebase/database-compat",Ht="@firebase/functions",Ft="@firebase/functions-compat",Vt="@firebase/installations",Kt="@firebase/installations-compat",Wt="@firebase/messaging",qt="@firebase/messaging-compat",Ut="@firebase/performance",Gt="@firebase/performance-compat",Jt="@firebase/remote-config",zt="@firebase/remote-config-compat",Yt="@firebase/storage",Xt="@firebase/storage-compat",Zt="@firebase/firestore",Qt="@firebase/vertexai-preview",en="@firebase/firestore-compat",tn="firebase",nn={[z]:"fire-core",[Nt]:"fire-core-compat",[Bt]:"fire-analytics",[Ot]:"fire-analytics-compat",[Mt]:"fire-app-check",[xt]:"fire-app-check-compat",[Rt]:"fire-auth",[$t]:"fire-auth-compat",[Pt]:"fire-rtdb",[jt]:"fire-data-connect",[Lt]:"fire-rtdb-compat",[Ht]:"fire-fn",[Ft]:"fire-fn-compat",[Vt]:"fire-iid",[Kt]:"fire-iid-compat",[Wt]:"fire-fcm",[qt]:"fire-fcm-compat",[Ut]:"fire-perf",[Gt]:"fire-perf-compat",[Jt]:"fire-rc",[zt]:"fire-rc-compat",[Yt]:"fire-gcs",[Xt]:"fire-gcs-compat",[Zt]:"fire-fst",[en]:"fire-fst-compat",[Qt]:"fire-vertex","fire-js":"fire-js",[tn]:"fire-js-all"};/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const rn=new Map,an=new Map,le=new Map;function fe(e,t){try{e.container.addComponent(t)}catch(n){b.debug(`Component ${t.name} failed to register with FirebaseApp ${e.name}`,n)}}function S(e){const t=e.name;if(le.has(t))return b.debug(`There were multiple attempts to register component ${t}.`),!1;le.set(t,e);for(const n of rn.values())fe(n,e);for(const n of an.values())fe(n,e);return!0}function De(e,t){const n=e.container.getProvider("heartbeat").getImmediate({optional:!0});return n&&n.triggerHeartbeat(),e.container.getProvider(t)}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const sn={"no-app":"No Firebase App '{$appName}' has been created - call initializeApp() first","bad-app-name":"Illegal App name: '{$appName}'","duplicate-app":"Firebase App named '{$appName}' already exists with different options or config","app-deleted":"Firebase App named '{$appName}' already deleted","server-app-deleted":"Firebase Server App has been deleted","no-options":"Need to provide options, when not being deployed to hosting via source.","invalid-app-argument":"firebase.{$appName}() takes either no argument or a Firebase App instance.","invalid-log-argument":"First argument to `onLog` must be null or a function.","idb-open":"Error thrown when opening IndexedDB. Original error: {$originalErrorMessage}.","idb-get":"Error thrown when reading from IndexedDB. Original error: {$originalErrorMessage}.","idb-set":"Error thrown when writing to IndexedDB. Original error: {$originalErrorMessage}.","idb-delete":"Error thrown when deleting from IndexedDB. Original error: {$originalErrorMessage}.","finalization-registry-not-supported":"FirebaseServerApp deleteOnDeref field defined but the JS runtime does not support FinalizationRegistry.","invalid-server-app-environment":"FirebaseServerApp is not for use in browser environments."},Z=new B("app","Firebase",sn);function m(e,t,n){var r;let a=(r=nn[e])!==null&&r!==void 0?r:e;n&&(a+=`-${n}`);const s=a.match(/\s|\//),o=t.match(/\s|\//);if(s||o){const i=[`Unable to register library "${a}" with version "${t}":`];s&&i.push(`library name "${a}" contains illegal characters (whitespace or "/")`),s&&o&&i.push("and"),o&&i.push(`version name "${t}" contains illegal characters (whitespace or "/")`),b.warn(i.join(" "));return}S(new E(`${a}-version`,()=>({library:a,version:t}),"VERSION"))}/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const on="firebase-heartbeat-database",cn=1,A="firebase-heartbeat-store";let H=null;function ke(){return H||(H=x(on,cn,{upgrade:(e,t)=>{switch(t){case 0:try{e.createObjectStore(A)}catch(n){console.warn(n)}}}}).catch(e=>{throw Z.create("idb-open",{originalErrorMessage:e.message})})),H}async function un(e){try{const n=(await ke()).transaction(A),r=await n.objectStore(A).get(Ne(e));return await n.done,r}catch(t){if(t instanceof I)b.warn(t.message);else{const n=Z.create("idb-get",{originalErrorMessage:t==null?void 0:t.message});b.warn(n.message)}}}async function he(e,t){try{const r=(await ke()).transaction(A,"readwrite");await r.objectStore(A).put(t,Ne(e)),await r.done}catch(n){if(n instanceof I)b.warn(n.message);else{const r=Z.create("idb-set",{originalErrorMessage:n==null?void 0:n.message});b.warn(r.message)}}}function Ne(e){return`${e.name}!${e.options.appId}`}/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const dn=1024,ln=30*24*60*60*1e3;class fn{constructor(t){this.container=t,this._heartbeatsCache=null;const n=this.container.getProvider("app").getImmediate();this._storage=new pn(n),this._heartbeatsCachePromise=this._storage.read().then(r=>(this._heartbeatsCache=r,r))}async triggerHeartbeat(){var t,n;try{const a=this.container.getProvider("platform-logger").getImmediate().getPlatformInfoString(),s=pe();return((t=this._heartbeatsCache)===null||t===void 0?void 0:t.heartbeats)==null&&(this._heartbeatsCache=await this._heartbeatsCachePromise,((n=this._heartbeatsCache)===null||n===void 0?void 0:n.heartbeats)==null)||this._heartbeatsCache.lastSentHeartbeatDate===s||this._heartbeatsCache.heartbeats.some(o=>o.date===s)?void 0:(this._heartbeatsCache.heartbeats.push({date:s,agent:a}),this._heartbeatsCache.heartbeats=this._heartbeatsCache.heartbeats.filter(o=>{const i=new Date(o.date).valueOf();return Date.now()-i<=ln}),this._storage.overwrite(this._heartbeatsCache))}catch(r){b.warn(r)}}async getHeartbeatsHeader(){var t;try{if(this._heartbeatsCache===null&&await this._heartbeatsCachePromise,((t=this._heartbeatsCache)===null||t===void 0?void 0:t.heartbeats)==null||this._heartbeatsCache.heartbeats.length===0)return"";const n=pe(),{heartbeatsToSend:r,unsentEntries:a}=hn(this._heartbeatsCache.heartbeats),s=Te(JSON.stringify({version:2,heartbeats:r}));return this._heartbeatsCache.lastSentHeartbeatDate=n,a.length>0?(this._heartbeatsCache.heartbeats=a,await this._storage.overwrite(this._heartbeatsCache)):(this._heartbeatsCache.heartbeats=[],this._storage.overwrite(this._heartbeatsCache)),s}catch(n){return b.warn(n),""}}}function pe(){return new Date().toISOString().substring(0,10)}function hn(e,t=dn){const n=[];let r=e.slice();for(const a of e){const s=n.find(o=>o.agent===a.agent);if(s){if(s.dates.push(a.date),ge(n)>t){s.dates.pop();break}}else if(n.push({agent:a.agent,dates:[a.date]}),ge(n)>t){n.pop();break}r=r.slice(1)}return{heartbeatsToSend:n,unsentEntries:r}}class pn{constructor(t){this.app=t,this._canUseIndexedDBPromise=this.runIndexedDBEnvironmentCheck()}async runIndexedDBEnvironmentCheck(){return ct()?ut().then(()=>!0).catch(()=>!1):!1}async read(){if(await this._canUseIndexedDBPromise){const n=await un(this.app);return n!=null&&n.heartbeats?n:{heartbeats:[]}}else return{heartbeats:[]}}async overwrite(t){var n;if(await this._canUseIndexedDBPromise){const a=await this.read();return he(this.app,{lastSentHeartbeatDate:(n=t.lastSentHeartbeatDate)!==null&&n!==void 0?n:a.lastSentHeartbeatDate,heartbeats:t.heartbeats})}else return}async add(t){var n;if(await this._canUseIndexedDBPromise){const a=await this.read();return he(this.app,{lastSentHeartbeatDate:(n=t.lastSentHeartbeatDate)!==null&&n!==void 0?n:a.lastSentHeartbeatDate,heartbeats:[...a.heartbeats,...t.heartbeats]})}else return}}function ge(e){return Te(JSON.stringify({version:2,heartbeats:e})).length}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function gn(e){S(new E("platform-logger",t=>new Dt(t),"PRIVATE")),S(new E("heartbeat",t=>new fn(t),"PRIVATE")),m(z,de,e),m(z,de,"esm2017"),m("fire-js","")}gn("");const Oe="@firebase/installations",Q="0.6.9";/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Be=1e4,xe=`w:${Q}`,Me="FIS_v2",bn="https://firebaseinstallations.googleapis.com/v1",mn=60*60*1e3,wn="installations",yn="Installations";/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const En={"missing-app-config-values":'Missing App configuration value: "{$valueName}"',"not-registered":"Firebase Installation is not registered.","installation-not-found":"Firebase Installation not found.","request-failed":'{$requestName} request failed with error "{$serverCode} {$serverStatus}: {$serverMessage}"',"app-offline":"Could not process request. Application offline.","delete-pending-registration":"Can't delete installation while there is a pending registration request."},v=new B(wn,yn,En);function Re(e){return e instanceof I&&e.code.includes("request-failed")}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function $e({projectId:e}){return`${bn}/projects/${e}/installations`}function Pe(e){return{token:e.token,requestStatus:2,expiresIn:vn(e.expiresIn),creationTime:Date.now()}}async function je(e,t){const r=(await t.json()).error;return v.create("request-failed",{requestName:e,serverCode:r.code,serverMessage:r.message,serverStatus:r.status})}function Le({apiKey:e}){return new Headers({"Content-Type":"application/json",Accept:"application/json","x-goog-api-key":e})}function Sn(e,{refreshToken:t}){const n=Le(e);return n.append("Authorization",_n(t)),n}async function He(e){const t=await e();return t.status>=500&&t.status<600?e():t}function vn(e){return Number(e.replace("s","000"))}function _n(e){return`${Me} ${e}`}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function In({appConfig:e,heartbeatServiceProvider:t},{fid:n}){const r=$e(e),a=Le(e),s=t.getImmediate({optional:!0});if(s){const d=await s.getHeartbeatsHeader();d&&a.append("x-firebase-client",d)}const o={fid:n,authVersion:Me,appId:e.appId,sdkVersion:xe},i={method:"POST",headers:a,body:JSON.stringify(o)},c=await He(()=>fetch(r,i));if(c.ok){const d=await c.json();return{fid:d.fid||n,registrationStatus:2,refreshToken:d.refreshToken,authToken:Pe(d.authToken)}}else throw await je("Create Installation",c)}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Fe(e){return new Promise(t=>{setTimeout(t,e)})}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Tn(e){return btoa(String.fromCharCode(...e)).replace(/\+/g,"-").replace(/\//g,"_")}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const An=/^[cdef][\w-]{21}$/,Y="";function Cn(){try{const e=new Uint8Array(17);(self.crypto||self.msCrypto).getRandomValues(e),e[0]=112+e[0]%16;const n=Dn(e);return An.test(n)?n:Y}catch{return Y}}function Dn(e){return Tn(e).substr(0,22)}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function M(e){return`${e.appName}!${e.appId}`}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Ve=new Map;function Ke(e,t){const n=M(e);We(n,t),kn(n,t)}function We(e,t){const n=Ve.get(e);if(n)for(const r of n)r(t)}function kn(e,t){const n=Nn();n&&n.postMessage({key:e,fid:t}),On()}let y=null;function Nn(){return!y&&"BroadcastChannel"in self&&(y=new BroadcastChannel("[Firebase] FID Change"),y.onmessage=e=>{We(e.data.key,e.data.fid)}),y}function On(){Ve.size===0&&y&&(y.close(),y=null)}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Bn="firebase-installations-database",xn=1,_="firebase-installations-store";let F=null;function ee(){return F||(F=x(Bn,xn,{upgrade:(e,t)=>{switch(t){case 0:e.createObjectStore(_)}}})),F}async function O(e,t){const n=M(e),a=(await ee()).transaction(_,"readwrite"),s=a.objectStore(_),o=await s.get(n);return await s.put(t,n),await a.done,(!o||o.fid!==t.fid)&&Ke(e,t.fid),t}async function qe(e){const t=M(e),r=(await ee()).transaction(_,"readwrite");await r.objectStore(_).delete(t),await r.done}async function R(e,t){const n=M(e),a=(await ee()).transaction(_,"readwrite"),s=a.objectStore(_),o=await s.get(n),i=t(o);return i===void 0?await s.delete(n):await s.put(i,n),await a.done,i&&(!o||o.fid!==i.fid)&&Ke(e,i.fid),i}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function te(e){let t;const n=await R(e.appConfig,r=>{const a=Mn(r),s=Rn(e,a);return t=s.registrationPromise,s.installationEntry});return n.fid===Y?{installationEntry:await t}:{installationEntry:n,registrationPromise:t}}function Mn(e){const t=e||{fid:Cn(),registrationStatus:0};return Ue(t)}function Rn(e,t){if(t.registrationStatus===0){if(!navigator.onLine){const a=Promise.reject(v.create("app-offline"));return{installationEntry:t,registrationPromise:a}}const n={fid:t.fid,registrationStatus:1,registrationTime:Date.now()},r=$n(e,n);return{installationEntry:n,registrationPromise:r}}else return t.registrationStatus===1?{installationEntry:t,registrationPromise:Pn(e)}:{installationEntry:t}}async function $n(e,t){try{const n=await In(e,t);return O(e.appConfig,n)}catch(n){throw Re(n)&&n.customData.serverCode===409?await qe(e.appConfig):await O(e.appConfig,{fid:t.fid,registrationStatus:0}),n}}async function Pn(e){let t=await be(e.appConfig);for(;t.registrationStatus===1;)await Fe(100),t=await be(e.appConfig);if(t.registrationStatus===0){const{installationEntry:n,registrationPromise:r}=await te(e);return r||n}return t}function be(e){return R(e,t=>{if(!t)throw v.create("installation-not-found");return Ue(t)})}function Ue(e){return jn(e)?{fid:e.fid,registrationStatus:0}:e}function jn(e){return e.registrationStatus===1&&e.registrationTime+Be<Date.now()}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function Ln({appConfig:e,heartbeatServiceProvider:t},n){const r=Hn(e,n),a=Sn(e,n),s=t.getImmediate({optional:!0});if(s){const d=await s.getHeartbeatsHeader();d&&a.append("x-firebase-client",d)}const o={installation:{sdkVersion:xe,appId:e.appId}},i={method:"POST",headers:a,body:JSON.stringify(o)},c=await He(()=>fetch(r,i));if(c.ok){const d=await c.json();return Pe(d)}else throw await je("Generate Auth Token",c)}function Hn(e,{fid:t}){return`${$e(e)}/${t}/authTokens:generate`}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function ne(e,t=!1){let n;const r=await R(e.appConfig,s=>{if(!Ge(s))throw v.create("not-registered");const o=s.authToken;if(!t&&Kn(o))return s;if(o.requestStatus===1)return n=Fn(e,t),s;{if(!navigator.onLine)throw v.create("app-offline");const i=qn(s);return n=Vn(e,i),i}});return n?await n:r.authToken}async function Fn(e,t){let n=await me(e.appConfig);for(;n.authToken.requestStatus===1;)await Fe(100),n=await me(e.appConfig);const r=n.authToken;return r.requestStatus===0?ne(e,t):r}function me(e){return R(e,t=>{if(!Ge(t))throw v.create("not-registered");const n=t.authToken;return Un(n)?Object.assign(Object.assign({},t),{authToken:{requestStatus:0}}):t})}async function Vn(e,t){try{const n=await Ln(e,t),r=Object.assign(Object.assign({},t),{authToken:n});return await O(e.appConfig,r),n}catch(n){if(Re(n)&&(n.customData.serverCode===401||n.customData.serverCode===404))await qe(e.appConfig);else{const r=Object.assign(Object.assign({},t),{authToken:{requestStatus:0}});await O(e.appConfig,r)}throw n}}function Ge(e){return e!==void 0&&e.registrationStatus===2}function Kn(e){return e.requestStatus===2&&!Wn(e)}function Wn(e){const t=Date.now();return t<e.creationTime||e.creationTime+e.expiresIn<t+mn}function qn(e){const t={requestStatus:1,requestTime:Date.now()};return Object.assign(Object.assign({},e),{authToken:t})}function Un(e){return e.requestStatus===1&&e.requestTime+Be<Date.now()}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function Gn(e){const t=e,{installationEntry:n,registrationPromise:r}=await te(t);return r?r.catch(console.error):ne(t).catch(console.error),n.fid}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function Jn(e,t=!1){const n=e;return await zn(n),(await ne(n,t)).token}async function zn(e){const{registrationPromise:t}=await te(e);t&&await t}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Yn(e){if(!e||!e.options)throw V("App Configuration");if(!e.name)throw V("App Name");const t=["projectId","apiKey","appId"];for(const n of t)if(!e.options[n])throw V(n);return{appName:e.name,projectId:e.options.projectId,apiKey:e.options.apiKey,appId:e.options.appId}}function V(e){return v.create("missing-app-config-values",{valueName:e})}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Je="installations",Xn="installations-internal",Zn=e=>{const t=e.getProvider("app").getImmediate(),n=Yn(t),r=De(t,"heartbeat");return{app:t,appConfig:n,heartbeatServiceProvider:r,_delete:()=>Promise.resolve()}},Qn=e=>{const t=e.getProvider("app").getImmediate(),n=De(t,Je).getImmediate();return{getId:()=>Gn(n),getToken:a=>Jn(n,a)}};function er(){S(new E(Je,Zn,"PUBLIC")),S(new E(Xn,Qn,"PRIVATE"))}er();m(Oe,Q);m(Oe,Q,"esm2017");/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const tr="/firebase-messaging-sw.js",nr="/firebase-cloud-messaging-push-scope",ze="BDOU99-h67HcA6JeFXHbSNMu7e2yNNu3RzoMj8TM4W88jITfq7ZmPvIM1Iv-4_l2LxQcYwhqby2xGpWwzjfAnG4",rr="https://fcmregistrations.googleapis.com/v1",Ye="google.c.a.c_id",ar="google.c.a.c_l",sr="google.c.a.ts",or="google.c.a.e";var we;(function(e){e[e.DATA_MESSAGE=1]="DATA_MESSAGE",e[e.DISPLAY_NOTIFICATION=3]="DISPLAY_NOTIFICATION"})(we||(we={}));/**
 * @license
 * Copyright 2018 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
 * in compliance with the License. You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software distributed under the License
 * is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
 * or implied. See the License for the specific language governing permissions and limitations under
 * the License.
 */var C;(function(e){e.PUSH_RECEIVED="push-received",e.NOTIFICATION_CLICKED="notification-clicked"})(C||(C={}));/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function p(e){const t=new Uint8Array(e);return btoa(String.fromCharCode(...t)).replace(/=/g,"").replace(/\+/g,"-").replace(/\//g,"_")}function ir(e){const t="=".repeat((4-e.length%4)%4),n=(e+t).replace(/\-/g,"+").replace(/_/g,"/"),r=atob(n),a=new Uint8Array(r.length);for(let s=0;s<r.length;++s)a[s]=r.charCodeAt(s);return a}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const K="fcm_token_details_db",cr=5,ye="fcm_token_object_Store";async function ur(e){if("databases"in indexedDB&&!(await indexedDB.databases()).map(s=>s.name).includes(K))return null;let t=null;return(await x(K,cr,{upgrade:async(r,a,s,o)=>{var i;if(a<2||!r.objectStoreNames.contains(ye))return;const c=o.objectStore(ye),d=await c.index("fcmSenderId").get(e);if(await c.clear(),!!d){if(a===2){const u=d;if(!u.auth||!u.p256dh||!u.endpoint)return;t={token:u.fcmToken,createTime:(i=u.createTime)!==null&&i!==void 0?i:Date.now(),subscriptionOptions:{auth:u.auth,p256dh:u.p256dh,endpoint:u.endpoint,swScope:u.swScope,vapidKey:typeof u.vapidKey=="string"?u.vapidKey:p(u.vapidKey)}}}else if(a===3){const u=d;t={token:u.fcmToken,createTime:u.createTime,subscriptionOptions:{auth:p(u.auth),p256dh:p(u.p256dh),endpoint:u.endpoint,swScope:u.swScope,vapidKey:p(u.vapidKey)}}}else if(a===4){const u=d;t={token:u.fcmToken,createTime:u.createTime,subscriptionOptions:{auth:p(u.auth),p256dh:p(u.p256dh),endpoint:u.endpoint,swScope:u.swScope,vapidKey:p(u.vapidKey)}}}}}})).close(),await j(K),await j("fcm_vapid_details_db"),await j("undefined"),dr(t)?t:null}function dr(e){if(!e||!e.subscriptionOptions)return!1;const{subscriptionOptions:t}=e;return typeof e.createTime=="number"&&e.createTime>0&&typeof e.token=="string"&&e.token.length>0&&typeof t.auth=="string"&&t.auth.length>0&&typeof t.p256dh=="string"&&t.p256dh.length>0&&typeof t.endpoint=="string"&&t.endpoint.length>0&&typeof t.swScope=="string"&&t.swScope.length>0&&typeof t.vapidKey=="string"&&t.vapidKey.length>0}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const lr="firebase-messaging-database",fr=1,D="firebase-messaging-store";let W=null;function Xe(){return W||(W=x(lr,fr,{upgrade:(e,t)=>{switch(t){case 0:e.createObjectStore(D)}}})),W}async function hr(e){const t=Ze(e),r=await(await Xe()).transaction(D).objectStore(D).get(t);if(r)return r;{const a=await ur(e.appConfig.senderId);if(a)return await re(e,a),a}}async function re(e,t){const n=Ze(e),a=(await Xe()).transaction(D,"readwrite");return await a.objectStore(D).put(t,n),await a.done,t}function Ze({appConfig:e}){return e.appId}/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const pr={"missing-app-config-values":'Missing App configuration value: "{$valueName}"',"only-available-in-window":"This method is available in a Window context.","only-available-in-sw":"This method is available in a service worker context.","permission-default":"The notification permission was not granted and dismissed instead.","permission-blocked":"The notification permission was not granted and blocked instead.","unsupported-browser":"This browser doesn't support the API's required to use the Firebase SDK.","indexed-db-unsupported":"This browser doesn't support indexedDb.open() (ex. Safari iFrame, Firefox Private Browsing, etc)","failed-service-worker-registration":"We are unable to register the default service worker. {$browserErrorMessage}","token-subscribe-failed":"A problem occurred while subscribing the user to FCM: {$errorInfo}","token-subscribe-no-token":"FCM returned no token when subscribing the user to push.","token-unsubscribe-failed":"A problem occurred while unsubscribing the user from FCM: {$errorInfo}","token-update-failed":"A problem occurred while updating the user from FCM: {$errorInfo}","token-update-no-token":"FCM returned no token when updating the user to push.","use-sw-after-get-token":"The useServiceWorker() method may only be called once and must be called before calling getToken() to ensure your service worker is used.","invalid-sw-registration":"The input to useServiceWorker() must be a ServiceWorkerRegistration.","invalid-bg-handler":"The input to setBackgroundMessageHandler() must be a function.","invalid-vapid-key":"The public VAPID key must be a string.","use-vapid-key-after-get-token":"The usePublicVapidKey() method may only be called once and must be called before calling getToken() to ensure your VAPID key is used."},h=new B("messaging","Messaging",pr);/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function gr(e,t){const n=await se(e),r=Qe(t),a={method:"POST",headers:n,body:JSON.stringify(r)};let s;try{s=await(await fetch(ae(e.appConfig),a)).json()}catch(o){throw h.create("token-subscribe-failed",{errorInfo:o==null?void 0:o.toString()})}if(s.error){const o=s.error.message;throw h.create("token-subscribe-failed",{errorInfo:o})}if(!s.token)throw h.create("token-subscribe-no-token");return s.token}async function br(e,t){const n=await se(e),r=Qe(t.subscriptionOptions),a={method:"PATCH",headers:n,body:JSON.stringify(r)};let s;try{s=await(await fetch(`${ae(e.appConfig)}/${t.token}`,a)).json()}catch(o){throw h.create("token-update-failed",{errorInfo:o==null?void 0:o.toString()})}if(s.error){const o=s.error.message;throw h.create("token-update-failed",{errorInfo:o})}if(!s.token)throw h.create("token-update-no-token");return s.token}async function mr(e,t){const r={method:"DELETE",headers:await se(e)};try{const s=await(await fetch(`${ae(e.appConfig)}/${t}`,r)).json();if(s.error){const o=s.error.message;throw h.create("token-unsubscribe-failed",{errorInfo:o})}}catch(a){throw h.create("token-unsubscribe-failed",{errorInfo:a==null?void 0:a.toString()})}}function ae({projectId:e}){return`${rr}/projects/${e}/registrations`}async function se({appConfig:e,installations:t}){const n=await t.getToken();return new Headers({"Content-Type":"application/json",Accept:"application/json","x-goog-api-key":e.apiKey,"x-goog-firebase-installations-auth":`FIS ${n}`})}function Qe({p256dh:e,auth:t,endpoint:n,vapidKey:r}){const a={web:{endpoint:n,auth:t,p256dh:e}};return r!==ze&&(a.web.applicationPubKey=r),a}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const wr=7*24*60*60*1e3;async function yr(e){const t=await Sr(e.swRegistration,e.vapidKey),n={vapidKey:e.vapidKey,swScope:e.swRegistration.scope,endpoint:t.endpoint,auth:p(t.getKey("auth")),p256dh:p(t.getKey("p256dh"))},r=await hr(e.firebaseDependencies);if(r){if(vr(r.subscriptionOptions,n))return Date.now()>=r.createTime+wr?Er(e,{token:r.token,createTime:Date.now(),subscriptionOptions:n}):r.token;try{await mr(e.firebaseDependencies,r.token)}catch(a){console.warn(a)}return Ee(e.firebaseDependencies,n)}else return Ee(e.firebaseDependencies,n)}async function Er(e,t){try{const n=await br(e.firebaseDependencies,t),r=Object.assign(Object.assign({},t),{token:n,createTime:Date.now()});return await re(e.firebaseDependencies,r),n}catch(n){throw n}}async function Ee(e,t){const r={token:await gr(e,t),createTime:Date.now(),subscriptionOptions:t};return await re(e,r),r.token}async function Sr(e,t){const n=await e.pushManager.getSubscription();return n||e.pushManager.subscribe({userVisibleOnly:!0,applicationServerKey:ir(t)})}function vr(e,t){const n=t.vapidKey===e.vapidKey,r=t.endpoint===e.endpoint,a=t.auth===e.auth,s=t.p256dh===e.p256dh;return n&&r&&a&&s}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Se(e){const t={from:e.from,collapseKey:e.collapse_key,messageId:e.fcmMessageId};return _r(t,e),Ir(t,e),Tr(t,e),t}function _r(e,t){if(!t.notification)return;e.notification={};const n=t.notification.title;n&&(e.notification.title=n);const r=t.notification.body;r&&(e.notification.body=r);const a=t.notification.image;a&&(e.notification.image=a);const s=t.notification.icon;s&&(e.notification.icon=s)}function Ir(e,t){t.data&&(e.data=t.data)}function Tr(e,t){var n,r,a,s,o;if(!t.fcmOptions&&!(!((n=t.notification)===null||n===void 0)&&n.click_action))return;e.fcmOptions={};const i=(a=(r=t.fcmOptions)===null||r===void 0?void 0:r.link)!==null&&a!==void 0?a:(s=t.notification)===null||s===void 0?void 0:s.click_action;i&&(e.fcmOptions.link=i);const c=(o=t.fcmOptions)===null||o===void 0?void 0:o.analytics_label;c&&(e.fcmOptions.analyticsLabel=c)}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Ar(e){return typeof e=="object"&&!!e&&Ye in e}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Cr(e){if(!e||!e.options)throw q("App Configuration Object");if(!e.name)throw q("App Name");const t=["projectId","apiKey","appId","messagingSenderId"],{options:n}=e;for(const r of t)if(!n[r])throw q(r);return{appName:e.name,projectId:n.projectId,apiKey:n.apiKey,appId:n.appId,senderId:n.messagingSenderId}}function q(e){return h.create("missing-app-config-values",{valueName:e})}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class Dr{constructor(t,n,r){this.deliveryMetricsExportedToBigQueryEnabled=!1,this.onBackgroundMessageHandler=null,this.onMessageHandler=null,this.logEvents=[],this.isLogServiceStarted=!1;const a=Cr(t);this.firebaseDependencies={app:t,appConfig:a,installations:n,analyticsProvider:r}}_delete(){return Promise.resolve()}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function kr(e){try{e.swRegistration=await navigator.serviceWorker.register(tr,{scope:nr}),e.swRegistration.update().catch(()=>{})}catch(t){throw h.create("failed-service-worker-registration",{browserErrorMessage:t==null?void 0:t.message})}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function Nr(e,t){if(!t&&!e.swRegistration&&await kr(e),!(!t&&e.swRegistration)){if(!(t instanceof ServiceWorkerRegistration))throw h.create("invalid-sw-registration");e.swRegistration=t}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function Or(e,t){t?e.vapidKey=t:e.vapidKey||(e.vapidKey=ze)}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function Br(e,t){if(!navigator)throw h.create("only-available-in-window");if(Notification.permission==="default"&&await Notification.requestPermission(),Notification.permission!=="granted")throw h.create("permission-blocked");return await Or(e,t==null?void 0:t.vapidKey),await Nr(e,t==null?void 0:t.serviceWorkerRegistration),yr(e)}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function xr(e,t,n){const r=Mr(t);(await e.firebaseDependencies.analyticsProvider.get()).logEvent(r,{message_id:n[Ye],message_name:n[ar],message_time:n[sr],message_device_time:Math.floor(Date.now()/1e3)})}function Mr(e){switch(e){case C.NOTIFICATION_CLICKED:return"notification_open";case C.PUSH_RECEIVED:return"notification_foreground";default:throw new Error}}/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function Rr(e,t){const n=t.data;if(!n.isFirebaseMessaging)return;e.onMessageHandler&&n.messageType===C.PUSH_RECEIVED&&(typeof e.onMessageHandler=="function"?e.onMessageHandler(Se(n)):e.onMessageHandler.next(Se(n)));const r=n.data;Ar(r)&&r[or]==="1"&&await xr(e,n.messageType,r)}const ve="@firebase/messaging",_e="0.12.12";/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const $r=e=>{const t=new Dr(e.getProvider("app").getImmediate(),e.getProvider("installations-internal").getImmediate(),e.getProvider("analytics-internal"));return navigator.serviceWorker.addEventListener("message",n=>Rr(t,n)),t},Pr=e=>{const t=e.getProvider("messaging").getImmediate();return{getToken:r=>Br(t,r)}};function jr(){S(new E("messaging",$r,"PUBLIC")),S(new E("messaging-internal",Pr,"PRIVATE")),m(ve,_e),m(ve,_e,"esm2017")}jr();var Lr="firebase",Hr="10.14.1";/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */m(Lr,Hr,"app");let Fr=null;const Vr=()=>{const[e,t]=w.useState(null),[n,r]=w.useState("default"),[a,s]=w.useState(!1);w.useEffect(()=>{const c="Notification"in window&&"serviceWorker"in navigator&&Fr!==null;s(c)},[]);const o=w.useCallback(async()=>(console.warn("FCM is not supported in this browser"),U.error("이 브라우저는 푸시 알림을 지원하지 않습니다."),!1),[a]),i=w.useCallback(async()=>!1,[e]);return w.useEffect(()=>{},[]),{token:e,permission:n,isSupported:a,requestPermission:o,unregisterToken:i}},Yr=({className:e=""})=>{const{permission:t,isSupported:n,requestPermission:r,unregisterToken:a}=Vr(),s=async()=>{await r()||U.error("알림을 활성화할 수 없습니다. 브라우저 설정을 확인해주세요.")},o=async()=>{await a()||U.error("알림을 비활성화할 수 없습니다.")};return n?l.jsxs("div",{className:`bg-white rounded-lg shadow p-4 ${e}`,children:[l.jsxs("div",{className:"flex items-center justify-between",children:[l.jsxs("div",{className:"flex items-center gap-3",children:[l.jsx("div",{className:`p-2 rounded-full ${t==="granted"?"bg-green-100":"bg-gray-100"}`,children:t==="granted"?l.jsx(tt,{className:"w-5 h-5 text-green-600"}):l.jsx(oe,{className:"w-5 h-5 text-gray-600"})}),l.jsxs("div",{children:[l.jsx("h3",{className:"font-medium text-gray-900",children:"푸시 알림"}),l.jsxs("p",{className:"text-sm text-gray-600",children:[t==="granted"&&"알림이 활성화되었습니다",t==="denied"&&"알림이 차단되었습니다",t==="default"&&"주문, 배차 등 중요한 알림을 받으세요"]})]})]}),l.jsx("div",{children:t==="granted"?l.jsxs("button",{onClick:o,className:"px-4 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors flex items-center gap-2",children:[l.jsx(nt,{className:"w-4 h-4"}),l.jsx("span",{className:"text-sm font-medium",children:"비활성화"})]}):t==="denied"?l.jsx("div",{className:"text-sm text-gray-500",children:"브라우저 설정에서 알림을 허용해주세요"}):l.jsxs("button",{onClick:s,className:"px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2",children:[l.jsx(rt,{className:"w-4 h-4"}),l.jsx("span",{className:"text-sm font-medium",children:"활성화"})]})})]}),t==="denied"&&l.jsxs("div",{className:"mt-4 p-3 bg-yellow-50 rounded-lg",children:[l.jsxs("p",{className:"text-sm text-yellow-800",children:["💡 ",l.jsx("strong",{children:"알림 허용 방법:"})]}),l.jsxs("ul",{className:"mt-2 text-sm text-yellow-700 list-disc list-inside space-y-1",children:[l.jsx("li",{children:"Chrome: 주소창 왼쪽 자물쇠 아이콘 → 사이트 설정 → 알림 허용"}),l.jsx("li",{children:"Firefox: 주소창 왼쪽 아이콘 → 권한 → 알림 허용"}),l.jsx("li",{children:"Safari: 설정 → Safari → 웹사이트 → 알림 → 허용"})]})]})]}):l.jsx("div",{className:`bg-gray-100 rounded-lg p-4 ${e}`,children:l.jsxs("div",{className:"flex items-center gap-2 text-gray-600",children:[l.jsx(oe,{className:"w-5 h-5"}),l.jsx("span",{className:"text-sm",children:"이 브라우저는 푸시 알림을 지원하지 않습니다."})]})})};export{Yr as NotificationSettings};
