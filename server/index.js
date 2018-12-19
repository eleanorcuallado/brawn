const WebSocket = require('ws');
const moment = require('moment');
const Sequelize = require('sequelize')
const wss = new WebSocket.Server({ port : 8087 });
const db = new Sequelize('DATABASE', 'USER','PASSWORD', {
  dialect: 'mysql'});


const Training = db.define('training', {
  id: { type: Sequelize.STRING(36), primaryKey: true },
  step: { type: Sequelize.INTEGER, primaryKey: true },
  value: { type: Sequelize.INTEGER }
},{ freezeTableName: true, timestamps: false });

const Parameters = db.define('parameters', {
  name: { type: Sequelize.STRING(36), primaryKey: true },
  parameter: { type: Sequelize.STRING(50), primaryKey: true},
  value: { type: Sequelize.STRING(50) }
},{ freezeTableName: true, timestamps: false });

wss.on('connection', function connection(ws){
  ws.on('message', function readData(str){
    data = JSON.parse(str);
    switch(data.type){
      case "hello":
        res = moment().format('[train]-DDMMYY-hhmmss');
        console.log('New set : ' + res)
        for (k in data.payload){
          Parameters.create({name: res, parameter: k, value: data.payload[k]});
        }
        break;
      case "training":
        console.log('New data from ' + data.name);
        Training.create({id: data.name, step: data.payload.id, value: data.payload.value });
        res = true;
        break;
      case "testing":
        console.log('New testing data from ' + data.name);
        console.log(data.payload);
        res = true;
        break;
      default:
        for ( x in data){
          console.log('key : ' + x)
        }
        console.log(data);
        res = false;
    }
  ws.send(JSON.stringify({
    'type':'answer',
    'payload': res
  }));
  });
});
