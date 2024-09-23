//
let mqttc = null;


function sendMqttMessage(uuid, msg, payload) {
    if (mqttc!=null) {
        var p = JSON.stringify({uuid: uuid, msg: msg, payload: payload});
        $.post("/mqtt/device/", p).done(function(r) {
            mqttc.publishMessage(r.basetopic + msg, payload);          
            //console.log(r.basetopic + msg, payload);
        });
    }
}

function uuidFromBtn(btn) {
    return btn.attr('id').split('-')[1];
}

function typeFromBtn(btn) {
    return btn.attr('id').split('-')[2];
}

function deviceInfos(uuid) {
    mqttc.publishMessage('zigbee2mqtt/bridge/request/device/interview', {id: uuid});
}

function setBtnOnOff(state, uuid) {
    var status = state.toLowerCase();
    $("span.state-"+uuid).text(status);
    var icon = $('i.'+uuid);
    cssClassToggle(icon, status=='on', 'fa-toggle-on', 'fa-toggle-off');
}

function setBtnPlayPause(status, uuid) {  
    if (!status) status = 'pause';
    $("span.state-" + uuid).text(status);
    var icon = $('i.' + uuid);
    cssClassToggle(icon, status=='play', 'fa-toggle-on', 'fa-toggle-off');
}

function topicToJson(topic) {
    var topics = topic.split('/');
    var opt = { org:topics[0], uuid:topics[1], evt:topics[2] };

    if (opt.org!='zigbee2mqtt') {
        if (opt.evt!==undefined) {
            if (opt.evt.endsWith('jpg')) {
                return $.extend(opt, { ts:topics[3], counter:topics[4], lat:topics[5], lon:topics[6], fps:topics[7] });
            } else if (opt.evt.endsWith('wav')) {
                return $.extend(opt, { ts:topics[3], counter:topics[4], lat:topics[5], lon:topics[6] });
            }
        }
    }
    return opt;
}

function mqtt_disconnected() {
    $.post("/mqtt/disconnect/").done(function(r) {
        //console.log(r.status);
    });
}

function onDisconnectionCBAK(mqtt, response) {
    $('span.ws-status').removeClass('w3-text-green').addClass('w3-text-red');
    mqtt_disconnected();
    mqttc = null;
}

function onConnectionCBAK(mqttclient) {
    $('span.ws-status').removeClass('w3-text-red').addClass('w3-text-green');
    mqttc = mqttclient;
}

function zigbee2mqttStatus(msg) {
    var payload = JSON.parse(msg.payloadString);
    if (payload.state == 'online')
        $('span.zigbee-status').removeClass('w3-text-red').addClass('w3-text-green');
    else if (payload.state == 'offline')
        $('span.zigbee-status').removeClass('w3-text-red').addClass('w3-text-green');
}

function onMessageCBAK(mqtt, msg)   {
    try {
        var topic = msg.destinationName;
        if (topic) {
            if (topic == "zigbee2mqtt/bridge/state")    { zigbee2mqttStatus(msg); return; }
            if (topic.startsWith("zigbee2mqtt/bridge")) { return; }
            var args = topicToJson(topic);
            if (args.evt!==undefined && (args.evt.endsWith('jpg') || args.evt.endsWith('wav')) ) {
                //console.log("onMessageCBAK-------------------", args);
                onMessageController(mqtt, args, msg.payloadBytes);
            } else {              
                onMessageController(mqtt, args, JSON.parse(msg.payloadString));
            }
        }
    } catch(e) {
        console.log(e);
    }
}

function mqttcInit(url) {
    //mqtt_init("/mqtt/init/", onMessageCBAK, onConnectionCBAK, onDisconnectionCBAK);
    mqtt_init(url, onMessageCBAK, onConnectionCBAK, onDisconnectionCBAK);
}

function videoPreview(cls)   {
    $('#videopreview').removeClass();
    $('#videopreview').addClass(cls);
    $('#videomodal').css("display", "block");
}

