function clear(){
    //var configPanel = document.getElementById("configPanel");
    configPanel.innerHTML = "";
}

function save(id){
    // Get input fields and forms
    var general = $( "#params" ).serializeArray();
    var interfaces = document.getElementsByName("interface");
    var routingRecords = document.getElementsByName("route");

    // Create configuration object
    config = {};

    // Fill it with general configuration like name and dpid
    for(var i=0; i<general.length; i++){
        var name = general[i]['name'];
        var value = general[i]['value'];

        if( name != 'State' ){
            config[ name ] = parseFloat(value) || value;
        }
        else{
            config[ name ] = true;
        }
    }
    // Set state variable
    if(config['State'] == null && config['ID'][0] == 'S')
        config['State'] = false;

    // Change display name of a node
    changeName(config['ID'], config['Name']);
    
    // Save object coordinates
    var object = canvas.getItemByName(config['ID'])

    config['x'] = object.oCoords['tl'].x;
    config['y'] = object.oCoords['tl'].y;   
    
    // Save interfaces info
    if(interfaces.length > 0){
        config ['interfaces'] = [];
        for(var i=0; i<interfaces.length; i++){
            var intf = {};
            for(var j=0; j<interfaces[i].elements.length; j++){
                var item = interfaces[i].elements.item(j);
                intf[item.name] = item.value; 
                if(item.name === 'VLAN ID')
                    intf[item.name] = parseInt(item.value)          
            }
            config['interfaces'][i] = intf;
        }
    }
    
    // Save routing records
    if(routingRecords.length > 0){
        config ['Routing'] = [];
        for(var i=0; i<routingRecords.length; i++){
            var record = {};
            var notempty = 0;
            for(var j=0; j<routingRecords[i].elements.length; j++){
                var item = routingRecords[i].elements.item(j);
                if(item.value != ""){
                    notempty++;
                    record[item.name] = item.value;
                }       
            }
            if(notempty == 4)
                config['Routing'][i] = record;
        }
    }
    
    // Send POST with this data
    $.post("/postParams",{id: id, config: JSON.stringify(config)}).done( function(data){ 
        console.log(config);
    });
}

// Disable submit on enter for forms
window.addEventListener('keydown', function(e) {
    if (e.keyIdentifier == 'U+000A' || e.keyIdentifier == 'Enter' || e.keyCode == 13) {
        if (e.target.nodeName == 'INPUT' && e.target.type == 'text') {
            e.preventDefault();
            return false;
        }
    }
}, true);

/* Create label with specified text and append it to specified parent */
function createLabel(text, parent){
    var l = document.createElement("label");
    l.innerHTML = text;
    parent.appendChild(l);
};

function createInputField(type, name, value, pattern, parent, required, disabled){
    var i = document.createElement("input");   
    i.type = type;
    i.name = name;
    i.value = value;
    if(pattern != "")
        i.pattern = pattern;
    i.required = required;
    i.disabled = disabled;
    parent.appendChild(i);
}; 

function load(id){
    clear();
    var configPanel = document.getElementById("configPanel");
    $.get("/getParams",
    {
        id: id
    },
    function(data, status){
        var config = JSON.parse(data);
        // Create form
        var form = document.createElement("form");
        form.setAttribute('name', 'params');
        form.setAttribute('id', 'params');
        // Create element for name
        createLabel("Name:", form);
        createInputField("text", "Name", config['Name'], "[A-Za-zА-Яа-яЁё0-9 ]+", form, true, false);

        // Create hidden elements for id and coordinates
        if('DPID' in config){
            createInputField("hidden", "DPID", config['DPID'], "", form, true, false);
        }
        
        createInputField("hidden", "ID", config['ID'], "", form, false, false);    
        createInputField("hidden", "x", config['x'], "", form, false, false);    
        createInputField("hidden", "y", config['y'], "", form, false, false);   

        // Create elements for interfaces
        var formInterfaces = document.createElement("div");
        formInterfaces.setAttribute('id', 'interfaces');
        formInterfaces.setAttribute('style', 'overflow-y: scroll; height: 250px;');
        if('interfaces' in config){
            createLabel("<br>Interfaces:", formInterfaces);

            for(var intf of config['interfaces']){
                // Set interface name
                var formIntf = document.createElement("form");
                formIntf.setAttribute('name', 'interface');

                createInputField("text", "Name", intf['Name'], "", formIntf, false, true);   
                if('IP' in intf){
                    createLabel("<br>IP:", formIntf);
                    createInputField("text", "IP", intf['IP'], "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)", formIntf, true, false);   
                }
                if("Mask" in intf){
                    createLabel("<br>Mask:", formIntf);
                    createInputField("text", "Mask", intf['Mask'], "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)", formIntf, true, false);  
                }
                if("MAC" in intf){
                    createLabel("<br>MAC:", formIntf);
                    createInputField("text", "MAC", intf['MAC'], "[0-9a-f][0-9a-f]:[0-9a-f][0-9Aa-f]:[0-9a-f][0-9a-f]:[0-9a-f][0-9a-f]:[0-9a-f][0-9a-f]:[0-9a-f][0-9a-f]", formIntf, true, false); 
                }

                if("VLAN ID" in intf){
                    createLabel("<br>VLAN ID:", formIntf);
                    createInputField("text", "VLAN ID", intf['VLAN ID'], "([0-4]?[0-9]?[0-9])|(50[1-9])|(51[0-2])", formIntf, true, false);  
                }

                if("VLAN TYPE" in intf){
                    createLabel("<br>VLAN TYPE:", formIntf);

                    var i = document.createElement("select");
                    i.name = "VLAN TYPE";
                    var option1 = document.createElement("option");
                    option1.value = "access";
                    option1.text = "access";
                    var option2 = document.createElement("option");
                    option2.value = "dot1q";
                    option2.text = "dot1q";
                    if(intf['VLAN TYPE'] == "access")
                        option1.selected = true;
                    else
                        option2.selected = true;
                    i.appendChild(option1);
                    i.appendChild(option2);
                    formIntf.appendChild(i);
                }

                if('Gateway' in intf){
                    createLabel("<br>Default gateway:", formIntf);
                    createInputField("text", "Gateway", intf['Gateway'], "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)", formIntf, true, false)
                }

                formInterfaces.appendChild(formIntf);
            }
            form.appendChild(formInterfaces); 
        }
        // Create state
        if('State' in config){
            var l = document.createElement("label");
            l.setAttribute('class', 'switch');
            var i = document.createElement("input");
            i.setAttribute('type', 'checkbox');
            i.checked = config['State'];
            i.name = 'State';
            var d = document.createElement("div");
            d.setAttribute('class', 'slider round');
            l.appendChild(i);
            l.appendChild(d);
            form.appendChild(l);
        }
        // Create routing table
        if('Routing' in config){
            var formRouting = document.createElement("div");
            formRouting.setAttribute('id', 'routing');
            formRouting.setAttribute('style', 'overflow-y: scroll; height: 150px;');
            createLabel("<br>Routing table:", formRouting);
            createLabel("<br>dst mask gw intf:", formRouting);
            for(var i=0; i<config['Routing'].length+1; i++){
                if(i != config['Routing'].length)
                    var record = config['Routing'][i];
                else
                    var record = JSON.parse('{ "Destination": "", "Mask": "", "Gateway": "", "Interface": "" }')
                var formRoute = document.createElement("form");
                formRoute.setAttribute('name', 'route');
                createInputField("text", "Destination", record['Destination'], "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)", formRoute, false, false);   
                createInputField("text", "Mask", record['Mask'], "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)", formRoute, false, false);   
                createInputField("text", "Gateway", record['Gateway'], "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)", formRoute, false, false);   
                createInputField("text", "Interface", record['Interface'], "[A-Za-zА-Яа-яЁё0-9- ]+", formRoute, false, false);   
                formRouting.appendChild(formRoute);
            }
            form.appendChild(formRouting);
        }
        // Create save button
        createLabel("<br>", form);
        var s = document.createElement("input");
        s.type = "submit";
        s.value = "Save";
        s.onclick = function handler(e){ 
            e.preventDefault();
            var fields = document.getElementsByTagName('input');
            var valid = true;
            for(var i=0; i < fields.length; i++)
            { 
                valid = valid && fields[i].checkValidity();
            }
            if(valid){
                save(config['ID']); 
                /*clear();*/
            } 
        };
        configPanel.appendChild(form);
        configPanel.appendChild(s);
    });
}

