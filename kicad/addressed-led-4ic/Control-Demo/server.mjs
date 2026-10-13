import { createServer as tcpServer } from 'node:net';
import { createServer as httpServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { Aedes } from 'aedes';
import mqtt from 'mqtt';

const HOST='127.0.0.1', MQTT_PORT=18884, HTTP_PORT=8788;
const COMMAND='codex/address-led/set', STATE='codex/address-led/state/5';
const allowedClients=new Set(['codex-demo-web','codex-demo-esp32-simulator']);
const events=[];
const add=(kind,message)=>{events.unshift({at:new Date().toISOString(),kind,message});events.splice(40);};
const broker=await Aedes.createBroker();
broker.authenticate=(client,user,password,cb)=>cb(null,allowedClients.has(client.id));
broker.authorizePublish=(client,packet,cb)=>{
 const topic=client.id==='codex-demo-web'?COMMAND:STATE;
 cb(packet.topic===topic&&packet.payload.length<256?null:new Error('Task topic denied'));
};
broker.authorizeSubscribe=(client,sub,cb)=>{
 const topic=client.id==='codex-demo-web'?STATE:COMMAND;
 cb(sub.topic===topic?null:new Error('Task subscription denied'),sub);
};
broker.on('clientReady',c=>add('CONNECT',c.id));
broker.on('clientDisconnect',c=>add('DISCONNECT',c.id));
broker.on('clientError',(c,e)=>add('ERROR',`${c?.id||'client'}: ${e.message}`));
broker.on('publish',(p,c)=>{if(c)add('MQTT',`${c.id} → ${p.topic} ${p.payload.toString()}`);});
const tcp=tcpServer(broker.handle);
await new Promise((ok,fail)=>tcp.once('error',fail).listen(MQTT_PORT,HOST,ok));
const device=mqtt.connect(`mqtt://${HOST}:${MQTT_PORT}`,{clientId:'codex-demo-esp32-simulator',protocolVersion:4,reconnectPeriod:1000});
const web=mqtt.connect(`mqtt://${HOST}:${MQTT_PORT}`,{clientId:'codex-demo-web',protocolVersion:4,reconnectPeriod:1000});
let storedMask=0, sequence=0, state={address:5,mask:0,seq:0,status:'waiting',simulated:true};
device.on('connect',()=>device.subscribe(COMMAND,{qos:1},()=>device.publish(STATE,JSON.stringify({...state,status:'ready'}),{qos:1,retain:true})));
web.on('connect',()=>web.subscribe(STATE,{qos:1}));
const valid=o=>o&&Object.keys(o).sort().join(',')==='address,mask,seq,version'&&o.version===1&&Number.isSafeInteger(o.seq)&&o.seq>0&&Number.isInteger(o.address)&&o.address>=0&&o.address<=15&&Number.isInteger(o.mask)&&o.mask>=0&&o.mask<=255;
device.on('message',(topic,payload)=>{
 try{
  const command=JSON.parse(payload.toString());if(!valid(command))return add('REJECT','Simulator rejected malformed MQTT command');
  const matched=command.address===5;
  if(matched)storedMask=command.mask;
  const ack={address:5,mask:storedMask,seq:command.seq,status:matched?'applied':'address_mismatch',received_address:command.address,simulated:true};
  device.publish(STATE,JSON.stringify(ack),{qos:1,retain:true});
 }catch{add('REJECT','Invalid MQTT JSON');}
});
web.on('message',(topic,payload)=>{try{state=JSON.parse(payload.toString());}catch{add('ERROR','State decode failed');}});
for(const client of [device,web])client.on('error',e=>add('ERROR',e.message));
const json=(res,code,data)=>{res.writeHead(code,{'Content-Type':'application/json','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});res.end(JSON.stringify(data));};
const server=httpServer(async(req,res)=>{
 if(req.headers.host!==`${HOST}:${HTTP_PORT}`&&req.headers.host!==`localhost:${HTTP_PORT}`)return json(res,403,{error:'Loopback host required'});
 if(req.method==='GET'&&req.url==='/'){
  const page=await readFile(new URL('./index.html',import.meta.url));res.writeHead(200,{'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-store','Content-Security-Policy':"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'"});return res.end(page);
 }
 if(req.method==='GET'&&req.url==='/api/state')return json(res,200,{state,events,broker:{host:HOST,port:MQTT_PORT,clients:broker.connectedClients,implementation:'Aedes 1.2.0 / MQTT 3.1.1'},connected:web.connected&&device.connected});
 if(req.method==='POST'&&req.url==='/api/command'){
  if(req.headers.origin!==`http://${HOST}:${HTTP_PORT}`&&req.headers.origin!==`http://localhost:${HTTP_PORT}`)return json(res,403,{error:'Same-origin control required'});
  if(!web.connected||!device.connected)return json(res,503,{error:'MQTT clients unavailable'});
  let body='';for await(const data of req){body+=data;if(body.length>256)return json(res,413,{error:'Command too large'});}
  let command;try{const input=JSON.parse(body);command={version:1,seq:++sequence,address:input.address,mask:input.mask};if(Object.keys(input).sort().join(',')!=='address,mask'||!valid(command))throw Error();}catch{return json(res,400,{error:'address0..15 and mask0..255 required'});}
  return web.publish(COMMAND,JSON.stringify(command),{qos:1,retain:false},error=>json(res,error?503:202,error?{error:'Publish failed'}:{queued:true,command}));
 }
 json(res,404,{error:'Not found'});
});
await new Promise((ok,fail)=>server.once('error',fail).listen(HTTP_PORT,HOST,ok));
console.log(JSON.stringify({pid:process.pid,web:`http://${HOST}:${HTTP_PORT}`,mqtt:`mqtt://${HOST}:${MQTT_PORT}`,device:'ESP32 simulation; no physical hardware',listening:'loopback only'}));
let closing=false;
async function close(){if(closing)return;closing=true;device.end(true);web.end(true);server.close();tcp.close();await new Promise(ok=>broker.close(ok));process.exit(0);}
process.on('SIGINT',close);process.on('SIGTERM',close);
