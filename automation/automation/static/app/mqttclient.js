//===================================================================
/*
 * My Web mqtt client
 *
 * Copyright (c) 2018 deunix@e-educ.fr
 *
 *  MIT License
 *
 *  Permission is hereby granted, free of charge, to any person obtaining a copy
 *  of this software and associated documentation files (the "Software"), to deal
 *  in the Software without restriction, including without limitation the rights
 *  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 *  copies of the Software, and to permit persons to whom the Software is
 *  furnished to do so, subject to the following conditions:
 *
 *  The above copyright notice and this permission notice shall be included in all
 *  copies or substantial portions of the Software.
 *
 *  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 *  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 *  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 *  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 *  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 *  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 *  SOFTWARE.
 */
//======================================================
var MQTT_RETAIN     = true;
var MQTT_NO_RETAIN  = false;
var QOS_AT_MOST_ONCE  = 0;
var QOS_AT_LEAST_ONCE = 1;
var QOS_EXACTLY_ONCE  = 2;


var MqttClientClass = function MqttClient(options, callbacks) {
    let self = this;

    this.mqtt = null;
    this.locales = options;
    this.mqttOptions = {
        userName: options.username,
        password: options.password,
        onSuccess: onConnect,
        onFailure: onFailure,
        useSSL: options.use_ssl,
        cleanSession: options.clean_session,
        keepAliveInterval: options.keepalive
    };
    var defaultCallbacks = {
        onMessageCallback: onMessageArrived,
        onConnectionLostCallback: onConnectionLost,
        onConnectionCallback: null,
        onDisconnectionCallback: null,
        onSubscribeCallback: null,
        onPublishCallback: null,
        onSynMessageCallback: null,
        onAckMessageCallback: null,
        onPongMessageCallback: null,
    };
    this.cbk = $.extend(defaultCallbacks, callbacks);
    this.reconnectTimeout = options.reconnect_timeout * 1000;
    this.clid = "domos_" + $.now();
    this.host = options.host;
    this.port = options.port;
    this.subs = options.topic_subs;

    // private methods
    function getOptions() {
        return self.locales;
    }

    function MQTTconnect() {

        console.log(self.host);
        self.mqtt = new Paho.MQTT.Client(self.host, self.port, self.clid);
        //self.mqtt.onConnectionLost = self.cbk.onConnectionLostCallback;
        //self.mqtt.onMessageArrived = self.cbk.onMessageCallback;
        self.mqtt.onConnectionLost = onConnectionLost;
        self.mqtt.onMessageArrived = onMessageArrived;
        self.mqtt.connect(self.mqttOptions);
        //console.log("Connecting to host: " + self.host + ":" + self.port +" ssl="+ self.mqttOptions.useSSL);
    }

    function MQTTsubscribe() {
        $.each(self.subs, function(i, sub) {
            self.mqtt.subscribe(sub[0], {qos: sub[1]});
            if (self.cbk.onSubscribeCallback)
                (self.cbk.onSubscribeCallback(sub[0], sub[1]));
        });
    }

    function onFailure(message) {
        console.log("Connection failed: " + message.errorMessage + ".\n Retrying...");
        setTimeout(MQTTconnect, self.reconnectTimeout);

    }

    function onConnect() {
        console.log('Connected to ' + self.host + ':' + self.port + "\nId: "+ self.clid + "\nssl: "+ self.mqttOptions.useSSL);
        if (self.cbk.onConnectionCallback)
            self.cbk.onConnectionCallback(self);
        MQTTsubscribe();
    }

    function onConnectionLost(response) {
        if (self.cbk.onDisconnectionCallback)
            self.cbk.onDisconnectionCallback(self, response);
        console.log("Connection lost: " + response.errorMessage + ".\nReconnecting...");
        setTimeout(MQTTconnect, self.reconnectTimeout);

    }

    function onMessageArrived(message) {
        if (self.cbk.onMessageCallback)
            self.cbk.onMessageCallback(self, message);
    }

    function MQTTpublish(topic, payload, qos, retained) {
        if (self.cbk.onPublishCallback)
            self.cbk.onPublishCallback(self, payload);
        self.mqtt.send(topic, payload, qos, retained);

        //console.log(topic,payload );
    }

    function MQTTdeleteRetainedMessage(topic) {
        self.mqtt.send(topic, "", 0, true);
    }

    function MQTTpublishMessage(topic, payload, retained) {
        //var msg = $.extend({time: tsNow()}, payload);
        var mqtt_retain = retained ? true: false;
        MQTTpublish(topic, JSON.stringify(payload), QOS_AT_LEAST_ONCE, mqtt_retain);
    }
    
    // public methods
    //
    this.options     = function()                               { getOptions();             };
    this.connect     = function()                               { MQTTconnect();            };
    this.disconnect  = function()                               { mqtt.disconnect();        };
    this.isConnected = function()                               { return mqtt.connected;    };
    this.suscribe    = function(filter, subscribeOptions)       { mqtt.suscribe(filter, subscribeOptions);      };
    this.unsubscribe = function(filter, unsubscribeOptions)     { mqtt.unsuscribe(filter, unsubscribeOptions);  };
    this.publish     = function(topic, payload, qos, retained)  { MQTTpublish(topic, payload, qos, retained);   };
    this.publishMessage = function(topic, payload, retained)    { MQTTpublishMessage(topic, payload, retained); };
    this.deleteRetainedMessage = function(topic)                { MQTTdeleteRetainedMessage(topic); };
};

function mqtt_init(url, onMessage, onConnection, onDisconnection) {
    ajax.Post(url).done(function(options) {
        var mqttCli = new MqttClientClass(options, {
            onMessageCallback: onMessage,
            onConnectionCallback: onConnection,
            onDisconnectionCallback: onDisconnection}
        );
        mqttCli.connect();
    });
}
let mqttc = null;
